#!/usr/bin/env bash
# 基站模式(2026-07-02)：local 作为主基站，主动访问各 server——
#   ssh 远程跑 collect(--local-only)+distill 生成 fragment → 轮询完成 → scp 取回 fragments/。
# server 侧只需有本仓库副本(供 collect.py/distill.py)，**无需 git push 权限、无需自己的 cron**。
# 配置：sources.json 里 type=ssh 且 "remote_collect": true 的源（enabled 仍设 false，
#       collect.py 的旧 md-拉取路径不启用，避免与 fragment 重复）。
# 用法：./pull_remote.sh              # 处理所有 remote_collect 源
#       ./pull_remote.sh server-1    # 只处理指定机器
# 链路容错：每条 ssh 4 次重试；远程任务 nohup 脱离会话；完成标记轮询(最长 ~5min)。
set -uo pipefail
cd "$(dirname "$0")"
ONLY="${1:-}"
python3 - "$ONLY" <<'PY'
import json, subprocess, sys, time, os, re, shlex
ONLY = sys.argv[1]
cfg = json.load(open('sources.json'))
fail = 0
for src in cfg['sources']:
    if src.get('type') != 'ssh' or not src.get('remote_collect'):
        continue
    m = src['machine']
    if not re.match(r'^[\w.-]+$', m):   # 机器名用于 /tmp 路径与本地文件名——只允许安全字符
        print(f'  ✗ 跳过非法机器名(仅允许字母数字/._-): {m!r}', file=sys.stderr); fail += 1; continue
    if ONLY and m != ONLY:
        continue
    host, user, port = src['host'], src.get('user', ''), src.get('port')
    tgt = f"{user}@{host}" if user else host
    repo = src.get('repo', '~/CyberMemory')
    roots = ','.join(src.get('roots') or ['~'])
    tool = src.get('tool', 'claude')
    sshb = ['ssh', '-o', 'ConnectTimeout=12', '-o', 'ServerAliveInterval=10', '-o', 'BatchMode=yes']
    scpb = ['scp', '-o', 'ConnectTimeout=12', '-o', 'BatchMode=yes']
    if port:
        sshb += ['-p', str(port)]; scpb += ['-P', str(port)]
    def run(cmd, to=45, tries=4):
        for a in range(tries):
            try:
                r = subprocess.run(sshb + [tgt, cmd], capture_output=True, text=True, timeout=to)
                if r.returncode == 0:
                    return r.stdout
            except subprocess.TimeoutExpired:
                pass
            if a < tries - 1:
                print(f'  · {m} ssh 重试 {a+2}/{tries}', file=sys.stderr); time.sleep(8)
        return None
    def fetch(remote, local, tries=3):
        for a in range(tries):
            try:
                r = subprocess.run(scpb + [f'{tgt}:{remote}', local],
                                   capture_output=True, text=True, timeout=120)
                if r.returncode == 0 and os.path.getsize(local) > 0:
                    return True
            except Exception:
                pass
            time.sleep(8)
        return False

    print(f'[remote] {m}: 远程采集+提炼（更新远端代码 → nohup 后台跑）', file=sys.stderr)
    # 1) 远程后台任务：先 git pull 保证远端用最新解析逻辑；collect+distill 写 /tmp；done 标记收尾
    qrepo, qroots, qtool = shlex.quote(repo), shlex.quote(roots), shlex.quote(tool)   # 防路径含空格/元字符
    rc = (f'cd {qrepo} && git pull -q --ff-only 2>/dev/null; rm -f /tmp/amg_{m}.done; '
          f'nohup bash -c "python3 collect.py --local-only --machine {m} --tool {qtool} '
          f'--roots {qroots} --out /tmp/amg_{m}.json > /tmp/amg_{m}.log 2>&1; '
          f'python3 distill.py --machine {m} --out /tmp/amg_{m}-distilled.json >> /tmp/amg_{m}.log 2>&1 '
          f'|| rm -f /tmp/amg_{m}-distilled.json; touch /tmp/amg_{m}.done" >/dev/null 2>&1 &')
    if run(rc) is None:
        print(f'  ✗ {m}: 无法启动远程采集（ssh 不通）', file=sys.stderr); fail += 1; continue
    # 2) 轮询完成标记（10s×30 ≈ 5min 上限）
    done = False
    for a in range(30):
        time.sleep(10)
        out = run(f'test -f /tmp/amg_{m}.done && echo DONE', to=25, tries=2)
        if out and 'DONE' in out:
            done = True; break
    if not done:
        print(f'  ✗ {m}: 远程采集超时（看远端 /tmp/amg_{m}.log）', file=sys.stderr); fail += 1; continue
    # 3) 取回 fragment（主碎片必须成功；distilled 可选）
    if fetch(f'/tmp/amg_{m}.json', f'fragments/{m}.json'):
        n = json.load(open(f'fragments/{m}.json'))['meta']['node_count']
        print(f'  ✓ {m}: fragments/{m}.json（{n} 节点）', file=sys.stderr)
    else:
        print(f'  ✗ {m}: 取回主碎片失败', file=sys.stderr); fail += 1; continue
    if run(f'test -f /tmp/amg_{m}-distilled.json && echo Y', to=25, tries=2) and \
       fetch(f'/tmp/amg_{m}-distilled.json', f'fragments/{m}-distilled.json'):
        print(f'  ✓ {m}: fragments/{m}-distilled.json（派生）', file=sys.stderr)
sys.exit(1 if fail else 0)
PY
