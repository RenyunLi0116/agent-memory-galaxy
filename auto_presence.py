#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_presence.py — 自动点亮「正在工作」红光（无需 agent 配合跑 heartbeat.sh）
==========================================================================
原理：Claude Code 的会话 transcript（~/.claude/projects/<slug>/*.jsonl）在 agent
工作时持续被写入。扫描**最近 AMG_AUTO_WIN 分钟**内有修改的主会话，为每个活跃会话
生成 presence/<machine>__auto-*.json 心跳（status=working, heartbeat=文件mtime），
collect 照常注入 liveagent → 查看器红色呼吸灯。

- 项目归属：复用 distill.project_root_of(会话 cwd)（容器上卷/数据目录判定），
  归不进项目的(如 NAS 数据目录、纯家目录)记到 local-env「本机环境」。
- current 字段用会话的 aiTitle（Claude 自动生成的标题，结构化、安全）。
- **幂等清理**：每次运行先删本机全部 auto-* presence，再为当前活跃会话重建——
  会话停止后下一轮(cron 15min)自动消灯。手工 heartbeat.sh 的文件(非 auto-*)不受影响。
用法：python3 auto_presence.py [--machine local] [--home ~] [--win 45]
"""
import os, re, sys, json, glob, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import collect
import distill   # 复用 project_root_of / session cwd 逻辑

def session_cwd_quick(fp, max_lines=80):
    """快速取会话 cwd：只读前 max_lines 行找第一个 "cwd" 字段。"""
    try:
        with open(fp, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                m = re.search(r'"cwd"\s*:\s*"([^"]+)"', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None

def session_title(fp):
    """取会话 aiTitle（倒序找最省，但顺扫前 200 行足够——ai-title 通常很靠前）。"""
    try:
        with open(fp, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= 200:
                    break
                if '"aiTitle"' in line:
                    m = re.search(r'"aiTitle"\s*:\s*"([^"]*)"', line)
                    if m:
                        return m.group(1)[:60]
    except Exception:
        pass
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--machine', default='local')
    ap.add_argument('--home', default='~')
    ap.add_argument('--win', type=int, default=int(os.environ.get('AMG_AUTO_WIN', '45')),
                    help='活跃窗口(分钟)：jsonl 在此窗口内有修改才算「正在工作」')
    args = ap.parse_args()
    home = os.path.expanduser(args.home)
    collect.load_projects()
    pdir = os.path.join(HERE, 'presence')
    os.makedirs(pdir, exist_ok=True)
    # 幂等：清掉本机旧 auto-* 心跳（会话停了灯就灭）
    for f in glob.glob(os.path.join(pdir, f'{args.machine}__auto-*.json')):
        os.remove(f)
    now = datetime.datetime.now().timestamp()
    best = {}   # pkey -> (mtime, plabel, title)
    for fp in glob.glob(os.path.join(home, '.claude', 'projects', '*', '*.jsonl')):
        try:
            mt = os.path.getmtime(fp)
        except OSError:
            continue
        if now - mt > args.win * 60:
            continue
        cwd = session_cwd_quick(fp)
        root = distill.project_root_of(cwd) if cwd else None
        if root:
            pkey, plabel = collect.project_for_manual(os.path.join(root, 'agent_memory.md'))
        else:
            pkey, plabel = 'localenv', '本机环境(local)'
        if pkey not in best or mt > best[pkey][0]:
            best[pkey] = (mt, plabel, session_title(fp))
    cnt = 0
    for pkey, (mt, plabel, title) in best.items():
        hb = datetime.datetime.fromtimestamp(mt, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        p = {'agent': f'auto-{pkey[:16]}', 'machine': args.machine, 'tool': 'claude',
             'project_canonical': pkey, 'project': plabel, 'status': 'working',
             'current': (title or '活跃会话(自动检测)'), 'heartbeat': hb, 'auto': True}
        fn = os.path.join(pdir, f"{args.machine}__auto-{pkey[:16]}.json")
        json.dump(p, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        cnt += 1
        print(f"  [auto-presence] 🔴 {plabel} ← {p['current'][:40]} (心跳 {hb})", file=sys.stderr)
    print(f"  [auto-presence] {args.machine}: {cnt} 个活跃会话点亮(窗口 {args.win}min)", file=sys.stderr)

if __name__ == '__main__':
    main()
