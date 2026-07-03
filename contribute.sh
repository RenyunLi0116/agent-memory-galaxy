#!/usr/bin/env bash
# 在「其他电脑」上运行：把本机 agent 记忆采集成 fragment，推送到共享私有仓库。
# 汇总端下次跑 update.sh 会自动合并所有 fragment 并更新加密 Pages。
#
# 用法:  ./contribute.sh <本机唯一名> [工具] [扫描根目录]
#   <本机唯一名>  这台机的唯一标识（如 mac-home / work-pc），勿与他机重名
#   [工具]        claude / codex / human（默认 agent），用于在图里区分产出工具
#   [扫描根目录]  默认 $HOME；家目录太大就指定具体项目目录
# 例:  ./contribute.sh mac-codex codex
#      ./contribute.sh lab-pc   claude
#      ./contribute.sh work-pc  codex  /home/me/projects
# 依赖: 仅 python3(标准库) + git；需对本仓库有 push 权限。
set -uo pipefail
cd "$(dirname "$0")"
NAME="${1:?用法: ./contribute.sh <本机唯一名> [工具] [扫描根目录]}"
TOOL="${2:-agent}"
ROOT="${3:-$HOME}"

echo "[1/4] 采集本机记忆（root=$ROOT, tool=$TOOL）→ fragments/$NAME.json"
python3 collect.py --local-only --machine "$NAME" --tool "$TOOL" --roots "$ROOT" --out "fragments/$NAME.json" >/dev/null \
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

echo "[3/4] git pull + 提交"
git pull -q --no-edit 2>/dev/null || true
git add "fragments/$NAME.json"
[ -f "$DIST" ] && git add "$DIST"
if git diff --cached --quiet; then echo "无改动，跳过"; exit 0; fi
git commit -q -m "memory: $NAME($TOOL) 记忆碎片$([ -f "$DIST" ] && echo '+派生') $(date +%F)"

echo "[4/4] 推送"
git push -q && echo "✓ 已推送。汇总端下次 update.sh 会自动合并并更新 Pages。" || { echo "✗ 推送失败（检查 push 权限）"; exit 1; }
