#!/usr/bin/env bash
# 一键刷新：采集(可选 ssh 拉远程) → 加密 → 重建本地单文件 → 提交并推送(触发 Pages 重建)
# 用法：  ./update.sh           只采集本地+NAS
#         ./update.sh --pull    同时 ssh 拉取已配置的远程 server
# 加密（可选，默认全私有则跳过）：配好双密码文件 .amg_password + .amg_password2（chmod 600、已 gitignore）后才加密；
# AMG_ENCRYPT=0 强制跳过加密（纯私有：只在本地重建 standalone.html）。
set -euo pipefail
cd "$(dirname "$0")"
PULL="${1:-}"

echo "[0/5] git pull（取回各电脑推上来的 fragments/）"
git pull -q --no-edit 2>/dev/null || true

# [0.3] 基站模式：--pull 时主动远程采集 remote_collect 源（ssh 跑 collect+distill 并取回 fragment，见 pull_remote.sh）
if [ -n "$PULL" ] && [ -x ./pull_remote.sh ]; then
  echo "[0.3] 基站远程采集（pull_remote：server 无需自己的 cron/git 权限）"
  ./pull_remote.sh || echo "      · 部分远程源失败（非致命，沿用旧 fragment）"
fi

# [0.4] 自动点亮「正在工作」红光：扫描本机活跃 Claude 会话(近45min有写入) → presence 心跳（无需 agent 配合）
echo "[0.4] auto-presence（自动检测本机正在工作的 agent）"
python3 auto_presence.py --machine "${AMG_LOCAL_NAME:-local}" 2>&1 | tail -1 || echo "      · 跳过（非致命）"

# [0.5] 提炼本机 Claude/Codex/Cursor 原生会话里「没写 agent_memory.md」的缺口项目（仅结构化字段·derived 次级）
# 写 fragments/<local>-distilled.json，下一步 collect --merge 的 fragments/*.json glob 自动吸收。AMG_DISTILL=0 关闭。
LOCALN="${AMG_LOCAL_NAME:-local}"
if [ "${AMG_DISTILL:-1}" != "0" ]; then
  echo "[0.5] 提炼本机原生会话缺口 → fragments/$LOCALN-distilled.json"
  python3 distill.py --machine "$LOCALN" --out "fragments/$LOCALN-distilled.json" >/dev/null 2>&1 \
    && echo "      $(python3 -c "import json;d=json.load(open('fragments/$LOCALN-distilled.json'));print(d['meta']['stats']['derived_entries'],'条派生记忆')" 2>/dev/null)" \
    || echo "      · 无派生或跳过（非致命）"
fi

echo "[1/5] 采集 ${PULL:-(仅本地)} + 合并其他电脑的 fragments/"
python3 collect.py $PULL --merge || { echo "采集失败"; exit 1; }

# 内容哈希（忽略 meta.generated 时间戳）：图无实质变化时可跳过重新加密，
# 但不要跳过静态文件/代码提交；viewer 或 docs 可能已经更新。
NEWHASH=$(python3 -c "import json,hashlib;d=json.load(open('graph.json'));d.get('meta',{}).pop('generated',None);print(hashlib.md5(json.dumps(d,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest())" 2>/dev/null)
HASH_UNCHANGED=0
if [ -n "$NEWHASH" ] && [ -f .last_graph_hash ] && [ "$(cat .last_graph_hash)" = "$NEWHASH" ] && [ "${AMG_REKEY:-0}" != "1" ]; then
  HASH_UNCHANGED=1
fi

# [2/5] 加密（可选）：AMG_ENCRYPT=0 跳过，auto 有双密码才加密，1 要求加密否则失败。
if [ "${AMG_ENCRYPT:-auto}" = "0" ]; then
  echo "[2/5] 跳过加密（AMG_ENCRYPT=0，私有模式）"
elif [ "$HASH_UNCHANGED" = "1" ] && [ -f docs/galaxy/graph.enc.json ]; then
  echo "[2/5] 图无实质变化，沿用现有 docs/galaxy/graph.enc.json（AMG_REKEY=1 可强制重加密）"
elif [ -f .amg_password ] && [ -f .amg_password2 ]; then
  echo "[2/5] 准备 GitHub Pages galaxy viewer → docs/galaxy/"
  mkdir -p docs/galaxy
  cp viewer/index.html docs/galaxy/index.html
  echo "      加密 → docs/galaxy/graph.enc.json"
  python3 encrypt.py || { echo "加密失败（缺 cryptography？见 PORTABILITY.md）"; exit 1; }
elif [ "${AMG_ENCRYPT:-auto}" = "1" ]; then
  echo "[2/5] AMG_ENCRYPT=1 但缺少 .amg_password/.amg_password2"; exit 1
else
  echo "[2/5] 跳过加密（未配置 .amg_password/.amg_password2 → 私有模式；如需加密在线共享见 PORTABILITY.md）"
fi
mkdir -p docs/galaxy
cp viewer/index.html docs/galaxy/index.html

echo "[3/5] 重建本地完整单文件 standalone.html（含明文，仅本地私有查看）"
python3 build_artifact.py --out standalone.html --standalone

echo "[4/5] 提交（只提交代码/碎片/可选密文；明文 graph.json/standalone.html 已 gitignore）"
if [ "${AMG_TRACK_PRIVATE:-0}" = "1" ]; then
  git add -A 2>/dev/null
else
  git add -A -- ':!fragments/*.json' ':!presence/*.json' ':!docs/galaxy/graph.enc.json' 2>/dev/null
fi
if git diff --cached --quiet; then echo "无改动，跳过推送"; exit 0; fi
git commit -q -m "refresh: $(date +%F) 采集+加密快照"

echo "[5/5] 推送 → 触发 GitHub Pages 重建"
if git push -q origin main; then
  [ -n "$NEWHASH" ] && echo "$NEWHASH" > .last_graph_hash
  echo "✓ 已推送，Pages 将自动重建"
else
  echo "✗ 推送失败"; exit 1
fi
