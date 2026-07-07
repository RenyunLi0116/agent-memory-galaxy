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

echo "[1/4] 采集本机记忆（root=$ROOT_ABS, tool=$TOOL${USER_ID:+, user=$USER_ID}）→ fragments/$NAME.json"
python3 collect.py --local-only --machine "$NAME" --tool "$TOOL" ${USER_ID:+--user "$USER_ID"} --roots "$ROOT_ABS" --out "fragments/$NAME.json" >/dev/null \
  || { echo "采集失败"; exit 1; }
echo "      $(python3 -c "import json;d=json.load(open('fragments/$NAME.json'));print(d['meta']['node_count'],'节点')" 2>/dev/null)"

# [2/4] 从 Claude/Codex/Cursor 原生会话「提炼」派生记忆（仅补缺口·结构化字段·derived 次级）
# 让没写 agent_memory.md 的项目也能进图。默认开；AMG_DISTILL=0 关闭。非致命：失败不阻塞主贡献。
DIST="fragments/$NAME-distilled.json"
if [ "${AMG_DISTILL:-1}" != "0" ]; then
  echo "[2/4] 提炼原生会话（Claude/Codex/Cursor，仅结构化字段）→ $DIST"
  if python3 distill.py --machine "$NAME" --out "$DIST" 2>/dev/null; then
    :
  else
    echo "      · 提炼跳过（无原生会话或出错，非致命）"
    rm -f "$DIST"
  fi
else
  echo "[2/4] 提炼已禁用（AMG_DISTILL=0）"; rm -f "$DIST"
fi

if [ "${AMG_PRIVATE_HUB:-0}" != "1" ]; then
  echo "[3/4] 跳过提交：public-safe 默认不强制提交 fragments。"
  echo "      已生成 fragments/$NAME.json$([ -f "$DIST" ] && echo " 和 $DIST")"
  echo "      在私有 hub 中确认可以保存真实记忆后，使用 AMG_PRIVATE_HUB=1 重新运行以提交并推送。"
  exit 0
fi

echo "[3/4] 私有 hub 模式：git pull + 强制 stage ignored fragments"
git pull -q --no-edit 2>/dev/null || true
git add -f "fragments/$NAME.json"
[ -f "$DIST" ] && git add -f "$DIST"
if git diff --cached --quiet; then echo "无改动，跳过"; exit 0; fi
git commit -q -m "memory: $NAME($TOOL) 记忆碎片$([ -f "$DIST" ] && echo '+派生') $(date +%F)"

echo "[4/4] 推送"
git push -q && echo "✓ 已推送。汇总端下次 update.sh 会自动合并并更新 Pages。" || { echo "✗ 推送失败（检查 push 权限）"; exit 1; }
