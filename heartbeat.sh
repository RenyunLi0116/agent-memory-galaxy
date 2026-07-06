#!/usr/bin/env bash
# agent 报到/心跳：更新自己的 presence 状态 + 拉回别人的状态与记忆 + 推送自己的。
# 准实时协作（粒度 ~10min，基于 git；非秒级长连接）。
#
# 用法:
#   ./heartbeat.sh <machine> <agent> <canonical_project> "<正在做什么>"      # 报到=working（一次）
#   ./heartbeat.sh <machine> <agent> <canonical_project> "<...>" --loop     # 每 10 分钟自动上报
#   ./heartbeat.sh <machine> <agent> --idle                                 # 收工，置 idle
# 环境变量: AMG_TOOL=claude|codex|human（默认 agent）
# 依赖: python3 + git；需对仓库 push 权限。
set -uo pipefail
cd "$(dirname "$0")"
MACHINE="${1:?用法: ./heartbeat.sh <machine> <agent> <canonical_project> \"<做什么>\" [--loop]  或  ./heartbeat.sh <machine> <agent> --idle}"
AGENT="${2:?缺 agent 名}"
shift 2
STATUS="working"; LOOP=0; TOOL="${AMG_TOOL:-agent}"; POS=()
for a in "$@"; do
  case "$a" in
    --idle) STATUS="idle";;
    --loop) LOOP=1;;
    *) POS+=("$a");;
  esac
done
PROJECT="${POS[0]:-}"; CURRENT="${POS[1]:-}"
FILE="presence/${MACHINE}__${AGENT}.json"

show_others() {
  ls presence/*.json >/dev/null 2>&1 || { echo "  (还没有其他 agent 报到)"; return; }
  MINE="$FILE" python3 - <<'PY'
import glob,json,os,datetime
now=datetime.datetime.now(datetime.timezone.utc); mine=os.environ.get("MINE")
for fp in sorted(glob.glob("presence/*.json")):
    if fp==mine: continue
    try: p=json.load(open(fp,encoding="utf-8"))
    except: continue
    hb=p.get("heartbeat",""); tag=""
    try:
        dt=datetime.datetime.fromisoformat(hb.replace("Z","+00:00"))
        m=(now-dt).total_seconds()/60
        tag=f"{m:.0f}分钟前"+(" 🔴在线" if m<15 and p.get('status')=='working' else "")
    except: pass
    print(f"  - {p.get('agent')}@{p.get('machine')} [{p.get('status')}] proj={p.get('project_canonical','')} :: {str(p.get('current',''))[:48]} ({tag})")
PY
}

write_presence() {
  local hb; hb="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  AMG_A="$AGENT" AMG_M="$MACHINE" AMG_P="$PROJECT" AMG_C="$CURRENT" AMG_S="$STATUS" AMG_HB="$hb" AMG_T="$TOOL" AMG_F="$FILE" python3 - <<'PY'
import os,json
d={"agent":os.environ["AMG_A"],"machine":os.environ["AMG_M"],
   "project_canonical":os.environ["AMG_P"],"project":os.environ["AMG_P"],
   "status":os.environ["AMG_S"],"current":os.environ["AMG_C"],
   "heartbeat":os.environ["AMG_HB"],"tool":os.environ["AMG_T"]}
open(os.environ["AMG_F"],"w",encoding="utf-8").write(json.dumps(d,ensure_ascii=False,indent=1))
PY
  echo "$hb"
}

report() {
  local hb; hb="$(write_presence)"
  # 先提交自己（保证工作区干净，pull --rebase 才不会因脏树失败）
  git add "$FILE" 2>/dev/null
  if git diff --cached --quiet; then echo "[$hb] $STATUS（无变化）"; return 0; fi
  git commit -q -m "presence: ${MACHINE}/${AGENT} ${STATUS} ${hb}" 2>/dev/null
  for i in 1 2 3 4 5; do
    # 拉回别人的状态与记忆；rebase 冲突（同名文件被并发改）时 abort 兜底，绝不提交冲突标记
    if ! git pull -q --rebase 2>/dev/null; then git rebase --abort 2>/dev/null || true; sleep 3; continue; fi
    if git push -q 2>/dev/null; then echo "[$hb] ✓ 已上报 $STATUS ${PROJECT:+@$PROJECT}"; return 0; fi
    echo "  远端领先，pull --rebase 后重试 $i/5"; sleep 3
  done
  echo "  ✗ 上报失败（检查网络/push 权限；如反复冲突说明同名 agent 被并发运行）"; return 1
}

echo "== 报到前先看别的 agent 在做什么（避免撞车）=="
git pull -q --rebase 2>/dev/null || true
show_others
echo "== 上报本机状态 =="
report
if [ "$LOOP" = 1 ]; then
  echo "== --loop：每 10 分钟自动上报，Ctrl-C 停止 =="
  while true; do sleep 600; report; done
fi
