#!/usr/bin/env bash
# 在「其他电脑」上运行：把本机 agent 记忆采集成 fragment，推送到共享私有仓库。
# 汇总端下次跑 update.sh 会自动合并所有 fragment 并更新加密 Pages。
#
# 用法:  ./contribute.sh <本机唯一名> <工具> <项目根目录> [推送者user]
#   <本机唯一名>  这台机的唯一标识（如 workstation-a / laptop-b），勿与他机重名
#   <工具>        claude / codex / cursor / human，用于在图里区分产出工具
#   <项目根目录>  必须是明确、较窄的项目目录；首次运行不要扫 $HOME、/ 或整个 workspace
#   [推送者user]  可选，团队 hub 中的推送者身份（GitHub 用户名）；缺省依次取
#                 AMG_USER env / git config user.name / $USER（详见 README「Team Work」与 team.json.example）
# 例:  ./contribute.sh workstation-a codex  ~/projects/my-app
#      ./contribute.sh lab-node-b  claude ~/work/active-project
#      ./contribute.sh lab-node-b  claude ~/work/active-project ada   # 显式声明推送者身份
# 默认只生成本机 fragment，不提交；在私有 hub 中设置 AMG_PRIVATE_HUB=1 才会 git add -f/commit/push。
# AMG_RELAY=0 关闭「上下同步中继」（私有 hub 模式下默认开：干完活立刻投给此刻在线的 agent）。
# 依赖: 仅 python3(标准库) + git；私有 hub 推送需要 push 权限。
set -uo pipefail
cd "$(dirname "$0")"
NAME="${1:?用法: ./contribute.sh <本机唯一名> <工具> <项目根目录> [推送者user]}"
TOOL="${2:?用法: ./contribute.sh <本机唯一名> <工具> <项目根目录> [推送者user]}"
ROOT="${3:?用法: ./contribute.sh <本机唯一名> <工具> <项目根目录> [推送者user]}"
USER_ID="${4:-}"   # 可选推送者身份；留空时 collect.py 依次取 AMG_USER / git config user.name / $USER
case "$TOOL" in claude|codex|cursor|human|agent) ;; *) echo "工具必须是 claude / codex / cursor / human"; exit 2;; esac
ROOT_ABS="$(python3 -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$ROOT")"
HOME_ABS="$(python3 -c 'import os; print(os.path.abspath(os.path.expanduser("~")))')"
if [ "$ROOT_ABS" = "/" ] || [ "$ROOT_ABS" = "$HOME_ABS" ]; then
  echo "拒绝扫描 $ROOT_ABS。请传入较窄的项目目录；若确实要大范围扫描，先设置 AMG_ALLOW_WIDE_SCAN=1。"
  [ "${AMG_ALLOW_WIDE_SCAN:-0}" = "1" ] || exit 2
fi
if [ ! -d "$ROOT_ABS" ]; then
  echo "项目根目录不存在: $ROOT_ABS"; exit 2
fi

echo "[1/5] 采集本机记忆（root=$ROOT_ABS, tool=$TOOL${USER_ID:+, user=$USER_ID}）→ fragments/$NAME.json"
python3 collect.py --local-only --machine "$NAME" --tool "$TOOL" ${USER_ID:+--user "$USER_ID"} --roots "$ROOT_ABS" --out "fragments/$NAME.json" >/dev/null \
  || { echo "采集失败"; exit 1; }
echo "      $(python3 -c "import json;d=json.load(open('fragments/$NAME.json'));print(d['meta']['node_count'],'节点')" 2>/dev/null)"

# [2/5] 从 Claude/Codex/Cursor 原生会话「提炼」派生记忆（仅补缺口·结构化字段·derived 次级）
# 让没写 agent_memory.md 的项目也能进图。默认开；AMG_DISTILL=0 关闭。非致命：失败不阻塞主贡献。
DIST="fragments/$NAME-distilled.json"
if [ "${AMG_DISTILL:-1}" != "0" ]; then
  echo "[2/5] 提炼原生会话（Claude/Codex/Cursor，仅结构化字段）→ $DIST"
  if python3 distill.py --machine "$NAME" --out "$DIST" 2>/dev/null; then
    :
  else
    echo "      · 提炼跳过（无原生会话或出错，非致命）"
    rm -f "$DIST"
  fi
else
  echo "[2/5] 提炼已禁用（AMG_DISTILL=0）"; rm -f "$DIST"
fi

if [ "${AMG_PRIVATE_HUB:-0}" != "1" ]; then
  echo "[3/5] 跳过提交：public-safe 默认不强制提交 fragments。"
  echo "      已生成 fragments/$NAME.json$([ -f "$DIST" ] && echo " 和 $DIST")"
  echo "      在私有 hub 中确认可以保存真实记忆后，使用 AMG_PRIVATE_HUB=1 重新运行以提交并推送。"
  exit 0
fi

# 仓库级 git 写锁（与 update.sh / heartbeat.sh / sync_watch.sh 共用，防 .git/index.lock 撞车）
mkdir -p .amg_relay
exec 9>.amg_relay/repo.lock
if ! flock -w 300 9; then echo "· 仓库锁被占用超过 300s，放弃本次（稍后重试）"; exit 1; fi

# push 抗抖动：网络瞬断会让 push 挂满数分钟；失败还不重试的话，relay 载荷会躺在本地未推送的
# commit 里，而 peer 被 wake 过去只会拉到一个不存在的提交。
export GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-ssh} -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3"
git_push_retry() {
  local i
  for i in 1 2 3 4 5; do
    if ! timeout 90 git pull -q --rebase 2>/dev/null; then git rebase --abort 2>/dev/null || true; fi
    if timeout 90 git push -q 2>/dev/null; then return 0; fi
    echo "  · 推送第 $i/5 次失败/超时，pull --rebase 后重试…"; sleep 3
  done
  return 1
}
flush_pending() {
  local n; n="$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)"
  [ "${n:-0}" -gt 0 ] 2>/dev/null || return 0
  echo "· 检测到 $n 个未推送积压 commit，补推"
  git_push_retry && echo "  ✓ 积压已补推" || echo "  ✗ 积压补推仍失败，下次再试"
}

echo "[3/5] 私有 hub 模式：git pull + 强制 stage ignored fragments"
git pull -q --no-edit 2>/dev/null || true

# [4/5] 上下同步中继：把本次新增记忆立刻投进「此刻正在干活」的机器的收件箱
# （relay/<对方机>/by-$NAME.jsonl，append-only、单写者，多机并发 push 不会冲突）。AMG_RELAY=0 关闭。
if [ "${AMG_RELAY:-1}" != "0" ] && [ -f relay.py ]; then
  echo "[4/5] 中继：把本次工作投递给此刻在线的 agent"
  python3 relay.py fanout --machine "$NAME" --agent "${AMG_AGENT:-$TOOL}" 2>&1 \
    | grep -E '\[fanout\]' || true
  python3 relay.py apply --machine "$NAME" --print-new 3 >/dev/null 2>&1 || true
else
  echo "[4/5] 中继已禁用（AMG_RELAY=0）"
fi

echo "[5/5] 提交 + 推送"
git add -f "fragments/$NAME.json"
[ -f "$DIST" ] && git add -f "$DIST"
# relay/ 在公开仓默认 gitignore（明文），私有 hub 模式下才 -f 强制追踪
find relay -mindepth 2 -type f \( -name '*.jsonl' -o -name '_ack.json' \) -exec git add -f {} + 2>/dev/null || true
if git diff --cached --quiet; then echo "无改动，跳过"; flush_pending; exit 0; fi
git commit -q -m "memory: $NAME($TOOL) 记忆碎片$([ -f "$DIST" ] && echo '+派生') $(date +%F)"
if git_push_retry; then
  echo "✓ 已推送。汇总端下次 update.sh 会自动合并并更新 Pages。"
  # 立刻唤醒 ssh 可达的在线 peer（够不着的机器由它自己的 sync_watch.sh 轮询拉取，~30s）
  if [ "${AMG_RELAY:-1}" != "0" ] && [ -f relay.py ]; then
    python3 relay.py wake --machine "$NAME" 2>&1 | grep -E '\[wake\]' || true
  fi
else
  echo "✗ 推送失败（已重试5次；检查 push 权限/网络）。本地 commit 已保留，下次运行会自动补推"; exit 1
fi
