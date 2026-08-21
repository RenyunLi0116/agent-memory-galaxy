#!/usr/bin/env bash
# sync_watch.sh — 让「A 干完活 → 正在干活的 B 立刻收到」真正发生的常驻轮询器。
#
# 每台参与的机器都可以跑一个（主脑加 --hub）。一轮做的事：
#   ① git ls-remote 比对远端 main（很轻，不变就啥也不干）→ 变了才 pull --rebase
#   ② presence-sync：刷新「本机此刻在不在干活」（只有实质变化才落盘，防提交风暴）
#   ②' --hub：local-scan —— 快扫主脑自己的记忆（主脑记忆从不落 fragments/，不扫就只能等 15min）
#   ③ --hub：fanout --scan-all —— 代所有 fragment（含 pull_remote 采回、自己从不跑 contribute 的
#      server）把新增记忆投递给此刻在线的机器
#   ④ apply：渲染本机 SYNC_INBOX.md；有新消息则跑 $AMG_ON_SYNC 钩子
#   ⑤ 只把 presence/ 与 relay/ 的改动 commit+push（**不用 git add -A**，避免把别人半截的工作提交上线）
#   ⑥ --hub：wake —— ssh 可达的在线 peer 立刻远程 pull（真正的“秒级”）
#
# 用法:
#   ./sync_watch.sh <本机唯一名> [--hub] [--agent <名>] [--interval 30] [--idle-interval 300]
#   ./sync_watch.sh <本机唯一名> --once            # 跑一轮就退出（配 cron: * * * * *）
#   nohup ./sync_watch.sh local --hub >> sync_watch.log 2>&1 &     # 常驻
#
# 环境变量:
#   AMG_ON_SYNC   有新同步时执行的命令（收到的条数在 $AMG_NEW，收件箱在 $AMG_INBOX）
#   AMG_USER      推送者身份（team work）
#   AMG_WIN       presence 新鲜窗口(分钟)，默认 45
#   AMG_RELAY_PUSH=0   只在本地同步、不 commit/push（调试用）
#   AMG_SCAN_MIN   --hub 时本机快扫的最小间隔(秒)，默认 180
#   AMG_COMMIT_MIN 仅 presence 变化时的最小提交间隔(秒)，默认 300；有中继载荷则立即提交
#   AMG_PRIVATE_HUB=1 / AMG_TRACK_PRIVATE=1  公开模板默认 gitignore presence/relay，
#                  设其一才 `git add -f` 真正推送（私有仓两目录本就受追踪，无需设置）
set -uo pipefail
cd "$(dirname "$0")"

MACHINE="${1:?用法: ./sync_watch.sh <本机唯一名> [--hub] [--once] [--interval N]}"
shift
HUB=0; ONCE=0; INTERVAL="${AMG_WATCH_INTERVAL:-30}"; IDLE_INTERVAL="${AMG_WATCH_IDLE:-300}"
AGENT=""; WIN="${AMG_WIN:-45}"; SCAN_MIN="${AMG_SCAN_MIN:-180}"; COMMIT_MIN="${AMG_COMMIT_MIN:-300}"
while [ $# -gt 0 ]; do
  case "$1" in
    --hub) HUB=1;;
    --once) ONCE=1;;
    --interval) INTERVAL="${2:?}"; shift;;
    --idle-interval) IDLE_INTERVAL="${2:?}"; shift;;
    --agent) AGENT="${2:?}"; shift;;
    --win) WIN="${2:?}"; shift;;
    *) echo "未知参数: $1"; exit 2;;
  esac
  shift
done

export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh} -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3"
mkdir -p .amg_relay
PY="${AMG_PYTHON:-python3}"

log() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

# 推送重试（抄 update.sh:git_push_retry）：只推 presence/ 与 relay/ 的提交，绝不丢本地提交。
push_retry() {
  local i
  for i in 1 2 3; do
    if ! timeout 90 git pull -q --rebase 2>/dev/null; then git rebase --abort 2>/dev/null || true; fi
    if timeout 90 git push -q origin HEAD 2>/dev/null; then return 0; fi
    sleep 3
  done
  return 1
}

remote_head() { timeout 25 git ls-remote --heads origin main 2>/dev/null | awk '{print $1}'; }
local_head()  { git rev-parse origin/main 2>/dev/null; }

# presence/ 与 relay/ 以外还有未提交改动？（有的话不敢 --autostash：pop 冲突会在别人改到一半的
# 文件里留冲突标记。这种一轮先不 pull，等它被提交/cron 收拾掉，下轮自然恢复。）
dirty_outside() {
  git status --porcelain -- . ':(exclude)presence' ':(exclude)relay' 2>/dev/null | grep -q .
}

# 一轮的实际工作，整段持**仓库级 git 写锁**：期间 update.sh / heartbeat.sh / contribute.sh
# 不会与我们撞 .git/index.lock（它们等锁，我们用 -n 不等——反正 30s 后还有下一轮）。
tick() {
  ( flock -n 8 || { log "· 仓库锁被别的同步任务占用，跳过本轮"; exit 0; }; tick_body ) 8>.amg_relay/repo.lock
  LAST_NEW="$(cat .amg_relay/last_new 2>/dev/null || echo 0)"
}

tick_body() {
  local changed_remote=0 rh lh new=0
  rh="$(remote_head)"; lh="$(local_head)"
  if [ -n "$rh" ] && [ "$rh" != "$lh" ]; then
    changed_remote=1
    if dirty_outside; then
      if ! timeout 120 git pull -q --rebase 2>/dev/null; then
        git rebase --abort 2>/dev/null || true
        log "· 工作区有未提交改动且远端领先 → 本轮跳过 pull（不用 autostash，避免 pop 冲突留标记）"
      fi
    elif ! timeout 120 git pull -q --rebase --autostash 2>/dev/null; then
      git rebase --abort 2>/dev/null || true
      log "· pull --rebase 失败，本轮跳过（下轮重试）"
    fi
  fi

  # ② 本机在不在干活（只有实质变化才落盘 → 30s 轮询也不会刷屏提交）
  "$PY" relay.py presence-sync --machine "$MACHINE" --win "$WIN" >/dev/null 2>>.amg_relay/watch.err || true

  # ②' 主脑快扫本机记忆（<1s）：主脑自己干完的活也要能秒级中继，不能只等 15min 的 update.sh
  if [ "$HUB" = 1 ]; then
    # 节流用文件 mtime 记（tick_body 跑在持锁子 shell 里，普通变量传不出去）
    local nowsec last=0; nowsec="$(date +%s)"
    [ -f .amg_relay/last_scan ] && last="$(stat -c %Y .amg_relay/last_scan 2>/dev/null || echo 0)"
    if [ $((nowsec - last)) -ge "$SCAN_MIN" ]; then
      "$PY" relay.py local-scan --machine "$MACHINE" >/dev/null 2>>.amg_relay/watch.err \
        && touch .amg_relay/last_scan
    fi
  fi

  # ③ 主脑代发：把各机（含本机快扫）的新增记忆投给此刻在线的机器
  if [ "$HUB" = 1 ]; then
    "$PY" relay.py fanout --machine "$MACHINE" --scan-all --include-local \
        ${AGENT:+--agent "$AGENT"} --win "$WIN" 2>&1 | grep -E '\[fanout\]' || true
  fi

  # ④ 收件：渲染 SYNC_INBOX.md。注意 apply 不推进「已读」游标（那是 agent 处理完才做的事），
  #    所以 NEW= 是**存量未读数**，不是本轮增量——必须自己比对 TOTAL 才知道这轮到底有没有新东西，
  #    否则钩子会每 30s 重复触发、日志每轮都喊「N 条新同步」。
  local out total prev_total=0
  out="$("$PY" relay.py apply --machine "$MACHINE" --win "$WIN" 2>/dev/null | head -1)"
  new="$(printf '%s' "$out" | sed -n 's/^NEW=\([0-9]*\).*/\1/p')"; new="${new:-0}"
  total="$(printf '%s' "$out" | sed -n 's/.*TOTAL=\([0-9]*\).*/\1/p')"; total="${total:-0}"
  [ -f .amg_relay/last_total ] && prev_total="$(cat .amg_relay/last_total 2>/dev/null || echo 0)"
  local delta=$(( total - prev_total )); [ "$delta" -lt 0 ] && delta=0
  printf '%s' "$total" > .amg_relay/last_total

  # ⑤ 只提交 presence/ 与 relay/（**不用 git add -A**，也带 pathspec 提交，绝不顺手把别人
  #    stage 在索引里的东西一起提交）。
  if [ "${AMG_RELAY_PUSH:-1}" != "0" ]; then
    # 公开模板把 presence/*.json 与 relay/*/ 设为 gitignore，不加 -f 会「add 成功但什么都没暂存」，
    # 于是 watcher 每轮静默空转。私有仓两目录本就受追踪，普通 add 即可。
    if [ "${AMG_PRIVATE_HUB:-0}" = "1" ] || [ "${AMG_TRACK_PRIVATE:-0}" = "1" ]; then
      find presence -maxdepth 1 -type f -name '*.json' -exec git add -f {} + 2>/dev/null || true
      [ -d relay ] && { find relay -mindepth 2 -type f \( -name '*.jsonl' -o -name '_ack.json' \) \
                         -exec git add -f {} + 2>/dev/null || true; }
    else
      git add presence 2>/dev/null || true         # 分开 add：relay/ 还不存在时，合并写一条
      [ -d relay ] && git add relay 2>/dev/null     # 会让整个 git add 失败、连 presence 都不暂存
    fi
    if ! git diff --cached --quiet -- presence relay 2>/dev/null; then
      # 提交限速：relay/ 有新载荷就立刻提交推送（这正是「立刻」要保的路径）；
      # 只有 presence 心跳在动时，最快 COMMIT_MIN 秒一次——否则 30s 一轮会变成每天数千个提交。
      local relay_dirty=0 last=0 nowsec
      git diff --cached --quiet -- relay 2>/dev/null || relay_dirty=1
      nowsec="$(date +%s)"
      [ -f .amg_relay/last_commit ] && last="$(stat -c %Y .amg_relay/last_commit 2>/dev/null || echo 0)"
      if [ "$relay_dirty" = 1 ] || [ $((nowsec - last)) -ge "$COMMIT_MIN" ]; then
        git commit -q -m "sync: ${MACHINE} 中继/在场状态 $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            -- presence relay 2>>.amg_relay/watch.err && touch .amg_relay/last_commit
        push_retry || log "· 推送失败（本地 commit 已保留，下轮补推）"
      fi
    elif [ "${AMG_PRIVATE_HUB:-0}" != "1" ] && [ "${AMG_TRACK_PRIVATE:-0}" != "1" ] \
         && [ ! -f .amg_relay/.warned_ignore ]; then
      log "· presence/relay 被 gitignore 且未设 AMG_PRIVATE_HUB=1 → 本机只在本地同步，不推送"
      : > .amg_relay/.warned_ignore
    fi
  fi

  # ⑥ 主脑：ssh 可达的在线 peer 立刻拉取
  if [ "$HUB" = 1 ]; then
    "$PY" relay.py wake --machine "$MACHINE" --win "$WIN" 2>&1 | grep -E '\[wake\]' || true
  fi

  if [ "$delta" -gt 0 ] 2>/dev/null; then
    log "📥 本轮新到 $delta 条（未读共 $new）→ SYNC_INBOX.md"
    if [ -n "${AMG_ON_SYNC:-}" ]; then
      # 8>&- 9>&-：钩子若把自己丢到后台，会连带继承这两个 fd 把仓库锁/实例锁钉死
      AMG_NEW="$delta" AMG_UNREAD="$new" AMG_INBOX="$PWD/SYNC_INBOX.md" \
        bash -c "$AMG_ON_SYNC" 8>&- 9>&- || true
    fi
  elif [ "$changed_remote" = 1 ]; then
    log "· 远端有更新，已同步（无新收件）"
  fi
  echo "$delta" > .amg_relay/last_new
}

# 同机防重入：cron `--once` 每分钟 + 常驻实例同时存在时不互相踩
command -v flock >/dev/null 2>&1 || {
  echo "✗ 未找到 flock（util-linux）。sync_watch 依赖它防重入与仓库锁，请先安装。"; exit 1; }
exec 9>.amg_relay/watch.lock
if ! flock -n 9; then
  echo "另一个 sync_watch 正在运行，退出"; exit 0
fi

if [ "$ONCE" = 1 ]; then
  tick; exit 0
fi

log "== sync_watch 启动: machine=$MACHINE hub=$HUB interval=${INTERVAL}s idle=${IDLE_INTERVAL}s =="
QUIET=0
while true; do
  LAST_NEW=0
  tick
  # 自适应：没人在干活（含本机）时退到 idle 间隔，省掉无谓的 ls-remote
  if [ "$LAST_NEW" -gt 0 ] 2>/dev/null; then QUIET=0; else QUIET=$((QUIET+1)); fi
  if [ "$QUIET" -ge 20 ] && ! "$PY" relay.py status --win "$WIN" 2>/dev/null | grep -q '🔴'; then
    sleep "$IDLE_INTERVAL"
  else
    sleep "$INTERVAL"
  fi
done
