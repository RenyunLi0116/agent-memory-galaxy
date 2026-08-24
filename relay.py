#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relay.py — 实时「上下同步」中继（A 干完活 → 立刻推给此刻正在干活的 B）
=====================================================================
补的缺口：原本 A 的记忆要等汇总端 cron(15min) 或 B 自己 heartbeat(10min) 才会流到 B。
本模块让「A 上行(contribute/采集) → 主脑 → 正在工作的 B 下行」在**秒级~数十秒**完成。

传输层仍是 git（零新依赖、零服务端），靠三条不变式做到多机并发无冲突：
  1. `relay/<收件机>/by-<写入机>.jsonl` —— **只有 <写入机> 会写这个文件**（append-only）。
     注意文件名里的是「写入者」不是「记忆来源」：主脑代某台「只被远程采集、自己不跑
     contribute.sh」的机器中继时，写的是 `by-<主脑名>.jsonl`，行里的 from.machine 才是那台机器。
     这样主脑代发也不破坏单写者不变式。
  2. `relay/<收件机>/_ack.json` —— **只有 <收件机> 会写**（回执：收到到哪一条了）。
  3. 渲染产物 `SYNC_INBOX.md` 与游标 `.amg_relay/` 一律 **不入库**（本地重建，不产生提交噪声）。
条目 id 由内容派生 → 同一条被主脑与本人重复中继时，收件端天然去重。

子命令
  scan            算出某机「新增/更新」的记忆条目（不写库，供调试/管道）
  fanout          把新增条目投递给此刻在线(working)的其他机器  [--scan-all 主脑代发所有 fragment]
  apply           收件端：汇总收件箱 → 渲染 SYNC_INBOX.md（🆕未读优先、同项目置顶）+ 写回执
  read            把未读游标推进到最新（agent 处理完后调用）
  wake            对 ssh 可达的在线 peer 立刻远程 `git pull` + apply（真正的“立刻”）
  gc              清理自己写的收件箱文件中过期条目（只动 by-<自己>.jsonl）
  status          在线 peer / 各收件箱待读数 / 最近回执
  presence-sync   刷新本机 presence（auto_presence），仅在**实质变化**时才落盘（防轮询提交风暴）

依赖：python3 标准库 + git。可在任何一台参与机器上跑。
"""
import os, re, sys, json, glob, time, hashlib, argparse, datetime, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY_DIR = os.path.join(HERE, "relay")
STATE_DIR = os.path.join(HERE, ".amg_relay")
INBOX_MD = os.path.join(HERE, "SYNC_INBOX.md")
LEDGER = os.path.join(STATE_DIR, "ledger.json")       # 我已中继过什么: {origin: {key: {rev, ts}}}
READ_CUR = os.path.join(STATE_DIR, "read.json")       # 我已读到哪: {"ts": "...", "ids": [...]}
LOCK = os.path.join(STATE_DIR, "relay.lock")

SUMMARY_LEN = 600
DEFAULT_WIN = 45          # presence 新鲜窗口(分钟)：心跳在此窗口内且 working 才算“正在干活”
DEFAULT_MAX = 60          # 单次 fanout 每个来源最多投递条数（防灌爆）
DEFAULT_AGE = 14          # 只中继近 N 天的记录（无日期的 fact 不受限，由 ledger 去重兜底）
DEFAULT_REPEAT_MIN = 20   # 同一条记录被改动后，最短再次投递间隔(分钟)
DEFAULT_CATCHUP = 1440    # 补投窗口(分钟)：最近这么久内中继过的条目，对「后来才上线」的机器仍会补投

# ---------------------------------------------------------------- 基础工具

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None

def minutes_since(s):
    dt = parse_iso(s)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 60.0

def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def atomic_write(path, text):
    """写 .tmp 再 os.replace：主脑 cron 每 15min `git add -A`，半截文件会被直接提交上线。"""
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-relay-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:          # 含 KeyboardInterrupt/SystemExit：否则 .tmp-relay-* 会留在
        try:                       # 工作区，被主脑 cron 的 `git add -A` 连同明文一起提交
            os.unlink(tmp)
        except OSError:
            pass
        raise

def atomic_append_lines(path, lines):
    """追加若干行（读-合并-原子替换）。单写者不变式保证同一文件不会被别的机器并发写。"""
    if not lines:
        return
    old = ""
    if os.path.exists(path):
        try:
            old = open(path, encoding="utf-8").read()
        except Exception:
            old = ""
    if old and not old.endswith("\n"):
        old += "\n"
    atomic_write(path, old + "".join(l.rstrip("\n") + "\n" for l in lines))

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")

def safe_machine(name):
    """机器名会进路径/文件名/ssh 命令，只允许安全字符（对齐公开版 pull_remote.sh 的做法）。
    额外挡掉 "." / ".." / 前导点：`.` 与 `..` 是能通过字符类的合法目录穿越，会让收件箱写到
    仓库根（by-*.jsonl / _ack.json），绕过所有 `/relay/*/` 忽略规则把明文摘要带进公开库。"""
    n = str(name or "").strip()
    if not SAFE_NAME.match(n) or n.startswith(".") or n in (".", ".."):
        return ""
    return n

class Lock:
    """粗粒度 flock：同机上 cron update.sh / watcher / contribute 可能同时跑 relay。"""
    def __init__(self, path=LOCK, timeout=60):
        self.path, self.timeout, self.fh = path, timeout, None
    def __enter__(self):
        import fcntl
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fh = open(self.path, "w")
        deadline = time.time() + self.timeout
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.time() > deadline:
                    print("  ! relay 锁等待超时，放弃本轮（别的进程正在中继）", file=sys.stderr)
                    self.fh.close(); self.fh = None
                    raise SystemExit(0)
                time.sleep(0.5)
    def __exit__(self, *a):
        if self.fh:
            import fcntl
            try:
                fcntl.flock(self.fh, fcntl.LOCK_UN)
            finally:
                self.fh.close()

# ---------------------------------------------------------------- 项目 canonical

_canon_ready = False

def canon(raw):
    """把 presence / 节点里的项目名归一成 canonical key（复用 collect.py 的别名表）。"""
    global _canon_ready
    raw = raw or ""
    try:
        sys.path.insert(0, HERE)
        import collect
        if not _canon_ready:
            collect.load_projects()
            _canon_ready = True
        k, label = collect.resolve_canon(raw) if raw else ("", "")
        return k, (label or raw)
    except Exception:
        return re.sub(r"[\s/_.\-]+", "", raw.lower()), raw

# ---------------------------------------------------------------- presence

def read_presence(win=DEFAULT_WIN):
    """读 presence/*.json → [{machine, agent, status, project, project_label, mins, live}]"""
    out = []
    for fp in sorted(glob.glob(os.path.join(HERE, "presence", "*.json"))):
        p = load_json(fp)
        if not isinstance(p, dict):
            continue
        m = safe_machine(p.get("machine"))
        if not m:
            continue
        raw = p.get("project_canonical") or p.get("project") or ""
        ckey, clabel = canon(raw) if raw else ("", "")
        mins = minutes_since(p.get("heartbeat"))
        out.append({
            "machine": m, "agent": str(p.get("agent", "?")),
            "status": p.get("status", "idle"), "tool": p.get("tool", "agent"),
            "user": p.get("user", ""), "current": p.get("current", ""),
            "project": ckey, "project_label": clabel,
            "heartbeat": p.get("heartbeat", ""), "mins": mins,
            "live": (p.get("status") == "working" and mins is not None and mins <= win),
        })
    return out

def live_machines(win=DEFAULT_WIN, exclude=None):
    """此刻正在干活的机器 → {machine: [presence...]}（exclude 通常是发送方自己）。"""
    res = {}
    for p in read_presence(win):
        if not p["live"] or p["machine"] == exclude:
            continue
        res.setdefault(p["machine"], []).append(p)
    return res

# ---------------------------------------------------------------- 条目抽取

def _revstr(s):
    """给字符串排序做倒序键（日期新的排前面），避免多次 sort 造成的顺序纠缠。"""
    return tuple(-ord(c) for c in s)

def _item_key(origin, n):
    """稳定身份：机器|项目|标题|日期。**不能用节点 id**——collect 的 entry id 是
    `entry:<机器>:<文件hash>:<第几节>`，在文件头部插入新记录会让后面所有 idx 平移。"""
    base = "|".join([origin, str(n.get("project") or ""), str(n.get("label") or ""),
                     str(n.get("date") or "")])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]

def _item_rev(n):
    body = str(n.get("excerpt") or n.get("description") or "")
    return hashlib.sha1(body.encode("utf-8")).hexdigest()[:6]

def fragment_items(path, origin=None, include_derived=False):
    """从 fragment/graph json 里抽出可中继的记忆条目（entry / fact）。"""
    d = load_json(path)
    if not isinstance(d, dict):
        return []
    items = []
    for n in d.get("nodes", []):
        if not isinstance(n, dict) or n.get("type") not in ("entry", "fact"):
            continue
        if n.get("derived") and not include_derived:
            continue
        org = safe_machine(n.get("machine") or origin or "")
        if not org:
            continue
        body = str(n.get("excerpt") or n.get("description") or "").strip()
        items.append({
            "key": _item_key(org, n), "rev": _item_rev(n),
            "origin": org, "node_id": n.get("id"),
            "kind": n.get("type"), "title": str(n.get("label") or "")[:160],
            "date": n.get("date"), "status": n.get("status") or "",
            "project_raw": n.get("project") or "",
            "tool": n.get("tool") or "", "agent": n.get("agent") or "",
            "user": n.get("user") or "", "source": n.get("source") or "",
            "summary": body[:SUMMARY_LEN],
            "derived": bool(n.get("derived")),
            "weight": n.get("weight") or 0,
        })
    return items

def select_new(items, ledger, max_items=DEFAULT_MAX, max_age=DEFAULT_AGE,
               repeat_min=DEFAULT_REPEAT_MIN, bootstrap=False, catchup_min=DEFAULT_CATCHUP):
    """对照本地台账挑出「新增 / 有实质更新 / 仍在补投窗口内」的条目。bootstrap=True 只记账不投递。

    catchup 很关键：台账只按**来源**记账，而收件人是「投递那一刻在线的机器」。若只投一次，
    半分钟后才开工的 B 就**永远**收不到那条——它已被记成「已中继」。所以最近 catchup_min 分钟
    内中继过的条目仍进候选池，靠收件端 `existing`（该收件箱已有的 id 集合）做精确去重，
    已经收到的人不会被重复打扰。
    """
    today = datetime.date.today()
    fresh, seen_now = [], {}
    dup = set()
    for it in items:
        org = it["origin"]
        # 同一条可能同时出现在 fragments/<M>.json 与 graph.json（主脑 --scan-all --include-local）：
        # 先按 (来源, key, rev) 去重，否则一次 fanout 会把同一条写进收件箱两次。
        sig = (org, it["key"], it["rev"])
        if sig in dup:
            continue
        dup.add(sig)
        prev = (ledger.get(org) or {}).get(it["key"])
        # sent 记录「这条到底有没有真的投出去过」：bootstrap 只是建账(sent=False)，
        # 不算已投——否则 catchup 会把整段历史当成「刚投过、补投给后来上线的人」再灌一遍。
        seen_now.setdefault(org, {})[it["key"]] = {"rev": it["rev"], "ts": now_iso(),
                                                   "sent": False if bootstrap else None}
        if bootstrap:
            continue
        if it.get("date"):                       # 日期太老的历史记录不再打扰在线的人
            try:
                d = datetime.date.fromisoformat(str(it["date"])[:10])
                if (today - d).days > max_age:
                    continue
            except ValueError:
                pass
        if prev is None:
            it["update"] = False
            fresh.append(it); continue
        mins = minutes_since(prev.get("ts"))
        if prev.get("rev") == it["rev"]:
            seen_now[org][it["key"]] = prev      # 未变：保留原时间戳，别让 ts 无谓前移
            if prev.get("sent") and mins is not None and mins <= catchup_min:
                it["update"] = False
                it["catchup"] = True             # 补投给「投递之后才上线」的机器；收件端按 id 去重
                fresh.append(it)
            continue
        if mins is not None and mins < repeat_min:
            seen_now[org][it["key"]] = prev      # 同一条被频繁改写(如滚动 doing 段)：限流
            continue
        it["update"] = True
        fresh.append(it)
    # 新增/更新排在补投之前；同档内按日期倒序。超出 --max 时优先保住真正的新东西。
    fresh.sort(key=lambda x: (1 if x.get("catchup") else 0,
                              _revstr(str(x.get("date") or "")), x["title"]))
    dropped = max(0, len(fresh) - max_items)
    if dropped:
        print(f"  · 超出单轮上限 {max_items}，本轮只投递最新 {max_items} 条（其余 {dropped} 条下轮继续）",
              file=sys.stderr)
        keep = {id(x) for x in fresh[:max_items]}
        for it in fresh[max_items:]:             # 未投递的回滚台账，下一轮还会被选中
            prev = (ledger.get(it["origin"]) or {}).get(it["key"])
            if prev is None:
                seen_now.get(it["origin"], {}).pop(it["key"], None)
            else:
                seen_now[it["origin"]][it["key"]] = prev
        fresh = [x for x in fresh if id(x) in keep]
    return fresh, seen_now

def merge_ledger(ledger, seen_now):
    for org, d in seen_now.items():
        ledger.setdefault(org, {}).update(d)
    return ledger

# ---------------------------------------------------------------- 投递 / 收件

def to_wire(it, writer, agent_hint=""):
    """台账条目 → 收件箱一行。id 由内容派生：主脑与本人重复中继时收件端天然去重。"""
    ckey, clabel = canon(it.get("project_raw") or "")
    return {
        "id": f"{it['key']}.{it['rev']}",
        "ts": now_iso(),
        "writer": writer,
        "from": {"machine": it["origin"], "agent": it.get("agent") or agent_hint or "",
                 "user": it.get("user") or "", "tool": it.get("tool") or ""},
        "project": ckey, "project_label": clabel,
        "kind": it["kind"], "title": it["title"], "date": it.get("date") or "",
        "status": it.get("status") or "", "update": bool(it.get("update")),
        "derived": bool(it.get("derived")),
        "summary": it.get("summary") or "", "node_id": it.get("node_id") or "",
        "source": os.path.basename(str(it.get("source") or "")),
    }

def inbox_path(recipient, writer):
    return os.path.join(RELAY_DIR, recipient, f"by-{writer}.jsonl")

def read_inbox(recipient):
    """读 relay/<收件机>/by-*.jsonl，按 id 去重（同一条可能被本人与主脑各投一次）。
    **每行独立容错**：一条坏行只丢它自己。早先把 try 放在文件层 + 用 it["id"] 取值，
    遇到「合法 JSON 但没有 id」的行会 KeyError 逃到文件层，把该文件**剩下的条目全丢掉**。"""
    if not safe_machine(recipient):
        return []
    seen, items, bad = set(), [], 0
    for fp in sorted(glob.glob(os.path.join(RELAY_DIR, recipient, "by-*.jsonl"))):
        try:
            fh = open(fp, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    it = json.loads(line)
                except Exception:
                    bad += 1; continue            # 半截行(极端断电)只丢这一行
                if not isinstance(it, dict):
                    bad += 1; continue
                iid = it.get("id")
                if not iid or iid in seen:
                    if not iid:
                        bad += 1
                    continue
                seen.add(iid); items.append(it)
    if bad:
        print(f"  [inbox] {recipient}: 跳过 {bad} 行坏数据（其余照常）", file=sys.stderr)
    items.sort(key=lambda x: str(x.get("ts") or ""))
    return items

# ---------------------------------------------------------------- 子命令

def cmd_scan(args):
    items = []
    for fp in fragments_for(args.machine, args.fragment):
        items += fragment_items(fp, args.machine, args.include_derived)
    ledger = load_json(LEDGER, {}) or {}
    fresh, _ = select_new(items, ledger, args.max, args.max_age_days, args.repeat_min)
    json.dump(fresh, sys.stdout, ensure_ascii=False, indent=1)
    print("", file=sys.stderr)
    print(f"  [scan] {args.machine}: {len(items)} 条可中继记录，其中 {len(fresh)} 条为新增/更新",
          file=sys.stderr)
    return 0

def fragments_for(machine, explicit=None):
    """某机的 fragment 文件（主碎片 + -distilled 派生碎片）。"""
    if explicit:
        return [explicit]
    out = []
    for suffix in (".json", "-distilled.json"):
        fp = os.path.join(HERE, "fragments", f"{machine}{suffix}")
        if os.path.isfile(fp):
            out.append(fp)
    return out

def cmd_fanout(args):
    with Lock():
        ledger = load_json(LEDGER, {}) or {}
        writer = safe_machine(args.machine)
        if not writer:
            print("✗ --machine 名非法（只允许字母数字 . _ -）", file=sys.stderr); return 2
        sources = []
        if args.scan_all:
            # 主脑代发：遍历所有 fragment（含经 pull_remote 采回、自己从不跑 contribute 的 server）
            for fp in sorted(glob.glob(os.path.join(HERE, "fragments", "*.json"))):
                base = os.path.basename(fp)[:-5]
                if base.endswith("-distilled"):
                    base = base[:-len("-distilled")]
                sources.append((safe_machine(base) or writer, fp))
            if args.include_local:
                # 主脑自己的记忆从不落 fragments/（collect 直接解析进 graph.json）——本机这一路必须另取：
                # ① watcher 的秒级快扫 .amg_relay/local-scan.json（不入库）；② 上一轮 collect 的
                # graph.json（15min 粒度兜底）。两者并集，重复条目由台账去重。
                for extra in (os.path.join(STATE_DIR, "local-scan.json"),
                              os.path.join(HERE, "graph.json")):
                    if os.path.isfile(extra):
                        sources.append((writer, extra))
        else:
            for fp in fragments_for(writer, args.fragment):
                sources.append((writer, fp))
            if not sources and os.path.isfile(os.path.join(HERE, "graph.json")):
                sources.append((writer, os.path.join(HERE, "graph.json")))

        items = []
        for org, fp in sources:
            items += fragment_items(fp, org, args.include_derived)
        if not items:
            print("  [fanout] 没有可中继的记录（先跑 collect/contribute）", file=sys.stderr); return 0

        # 首次见到某来源机 → 只建账不投递，否则会把全部历史灌给在线的人
        known = set(ledger.keys())
        origins = {it["origin"] for it in items}
        first_seen = origins - known
        if first_seen and not args.no_bootstrap:
            boot = [it for it in items if it["origin"] in first_seen]
            _, seen_boot = select_new(boot, ledger, bootstrap=True)
            merge_ledger(ledger, seen_boot)
            atomic_write(LEDGER, json.dumps(ledger, ensure_ascii=False, indent=1))
            print(f"  [fanout] 首次建账(不投递): {', '.join(sorted(first_seen))}", file=sys.stderr)
            items = [it for it in items if it["origin"] not in first_seen]
            if not items:
                return 0

        fresh, seen_now = select_new(items, ledger, args.max, args.max_age_days,
                                     args.repeat_min, catchup_min=args.catchup_min)
        if not fresh:
            print("  [fanout] 无新增记录，跳过", file=sys.stderr)
            merge_ledger(ledger, seen_now)
            atomic_write(LEDGER, json.dumps(ledger, ensure_ascii=False, indent=1))
            return 0

        peers = live_machines(args.win)
        # 不给「本条记忆的来源机」再投一遍；主脑代发时逐条按 origin 判断
        recipients = sorted(peers.keys())
        if not recipients:
            print(f"  [fanout] 此刻没有别的机器在工作（{args.win}min 内 status=working）——"
                  f"{len(fresh)} 条已记账，等有人上线时由后续轮次投递", file=sys.stderr)
            # **默认不记账**：记了的话这些条目就永远算「已中继」，等有人上线时反而收不到。
            # 只把「本来就没变过」的条目回写（保持 ts 不前移），真正待投的留到下轮。
            if args.drop_pending:
                merge_ledger(ledger, seen_now)
                atomic_write(LEDGER, json.dumps(ledger, ensure_ascii=False, indent=1))
            else:
                pend = {it["key"] for it in fresh}
                for org, d in seen_now.items():
                    for k in list(d):
                        if k in pend:
                            d.pop(k)
                merge_ledger(ledger, seen_now)
                atomic_write(LEDGER, json.dumps(ledger, ensure_ascii=False, indent=1))
            return 0

        total, hit = 0, 0
        for r in recipients:
            mine = [it for it in fresh if it["origin"] != r]
            if not mine:
                continue
            existing = {x.get("id") for x in read_inbox(r)}
            lines, n = [], 0
            for it in mine:
                w = to_wire(it, writer, args.agent)
                if w["id"] in existing:
                    continue
                existing.add(w["id"])      # 同一轮里也去重：同条记录可能来自 fragment 与 graph 两份
                lines.append(json.dumps(w, ensure_ascii=False)); n += 1
            if lines:
                atomic_append_lines(inbox_path(r, writer), lines)
                who = ", ".join(f"{p['agent']}({p['project_label'] or '?'})" for p in peers[r][:3])
                print(f"  [fanout] → {r}: +{n} 条（在线: {who}）", file=sys.stderr)
                total += n; hit += 1
        for it in fresh:                     # 真投出去了才算已投，catchup 只认这些
            e = seen_now.get(it["origin"], {}).get(it["key"])
            if e is not None and e.get("sent") is None:
                e["sent"] = True
        merge_ledger(ledger, seen_now)
        atomic_write(LEDGER, json.dumps(ledger, ensure_ascii=False, indent=1))
        _gc_own(writer, args.keep_days)
        if total:
            print(f"  [fanout] 共投递 {total} 条给 {hit} 台在线机器"
                  f"（在线 {len(recipients)} 台，其余机器本身就是这些记录的来源）", file=sys.stderr)
        else:
            print(f"  [fanout] 在线 {len(recipients)} 台机器都已有这些记录，无需投递", file=sys.stderr)
        return 0

def cmd_presence_bundle(args):
    """把本机的 presence/<机>__auto-*.json 打包成单个 json（{文件名: 内容}）。
    供 pull_remote.sh 从只读 server 上一次性取回——那些机器不跑 cron、不 push，
    没有这条回传路径它们在中继里就永远不算「在线」，收不到别人刚干完的活。"""
    me = safe_machine(args.machine)
    if not me:
        print("✗ --machine 名非法", file=sys.stderr); return 2
    bundle = {}
    for fp in sorted(glob.glob(os.path.join(HERE, "presence", f"{me}__auto-*.json"))):
        d = load_json(fp)
        if isinstance(d, dict):
            bundle[os.path.basename(fp)] = d
    atomic_write(args.out, json.dumps(bundle, ensure_ascii=False, indent=1))
    print(f"  [presence-bundle] {me}: {len(bundle)} 个活跃会话 → {args.out}", file=sys.stderr)
    return 0

def cmd_local_scan(args):
    """快扫本机记忆 → .amg_relay/local-scan.json（**不入库、不参与建图**，只作 relay 的差分源）。
    主脑自己的记忆不落 fragments/，若只靠 graph.json 就得等 15min 的 update.sh；这一步让
    「在主脑上干完的活」也能秒级中继出去。实测全量本地扫描 <1s（prune 列表已剪掉重目录）。"""
    roots = args.roots
    if not roots:
        cfg = load_json(os.path.join(HERE, "sources.json"), {}) or {}
        rs = []
        for src in cfg.get("sources", []):
            if not isinstance(src, dict) or src.get("type") != "local" or not src.get("enabled"):
                continue
            if safe_machine(src.get("machine")) != safe_machine(args.machine):
                continue          # 只扫「本机」那条源；NAS 等另立机器名的慢源不进快扫
            rs += [r for r in (src.get("roots") or []) if r]
        roots = ",".join(rs)
    if not roots:
        print(f"  [local-scan] sources.json 里没有 machine={args.machine} 的本地源，跳过", file=sys.stderr)
        return 0
    out = os.path.join(STATE_DIR, "local-scan.json")
    tmp = out + ".tmp"
    cmd = [sys.executable, os.path.join(HERE, "collect.py"), "--local-only",
           "--machine", args.machine, "--roots", roots, "--out", tmp]
    if args.user:
        cmd += ["--user", args.user]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"  [local-scan] 超时 {args.timeout}s，跳过（非致命）", file=sys.stderr)
        return 0
    if r.returncode != 0 or not os.path.isfile(tmp):
        print(f"  [local-scan] 失败（非致命）: {r.stderr.strip()[-160:]}", file=sys.stderr)
        return 0
    os.replace(tmp, out)
    n = (load_json(out, {}) or {}).get("meta", {}).get("node_count", "?")
    print(f"  [local-scan] {args.machine}: {n} 节点 → {os.path.relpath(out, HERE)}", file=sys.stderr)
    return 0

def cmd_apply(args):
    me = safe_machine(args.machine)
    if not me:
        print("✗ --machine 名非法", file=sys.stderr); return 2
    items = read_inbox(me)
    cur = load_json(READ_CUR, {}) or {}
    read_ids = set(cur.get("ids") or [])
    mark = str(cur.get("watermark") or "")
    unread = [x for x in items
              if x.get("id") not in read_ids and not (mark and str(x.get("ts") or "") < mark)]
    mine_live = [p for p in read_presence(args.win) if p["machine"] == me and p["live"]]
    my_projects = {p["project"] for p in mine_live if p["project"]}

    def rel(x):
        return bool(x.get("project")) and x.get("project") in my_projects

    unread.sort(key=lambda x: (not rel(x), str(x.get("ts") or "")), reverse=False)
    unread.sort(key=lambda x: (0 if rel(x) else 1, -_ts_ord(x)))
    recent = [x for x in items if (minutes_since(x.get("ts")) or 1e9) <= args.recent_hours * 60]
    recent.sort(key=lambda x: -_ts_ord(x))

    md = render_inbox(me, mine_live, unread, recent, args.recent_hours, args.max_render)
    atomic_write(INBOX_MD, md)
    # 回执：只有收件机自己写，跨机不冲突
    ack = {"machine": me, "updated": now_iso(), "total": len(items), "unread": len(unread),
           "last_item_ts": items[-1]["ts"] if items else "",
           "by": {}}
    for fp in sorted(glob.glob(os.path.join(RELAY_DIR, me, "by-*.jsonl"))):
        wname = os.path.basename(fp)[len("by-"):-len(".jsonl")]
        ack["by"][wname] = sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))
    ackp = os.path.join(RELAY_DIR, me, "_ack.json")
    if os.path.isdir(os.path.join(RELAY_DIR, me)):
        # 只有**实质**字段变了才落盘：`updated` 每次都在变，无脑写的话 watcher 每 30s 跑一次 apply
        # 就把回执变成每 30s 一个提交的噪声源（与 presence-sync 同一套防抖思路）。
        prev = load_json(ackp, {}) or {}
        if {k: v for k, v in prev.items() if k != "updated"} != {k: v for k, v in ack.items() if k != "updated"}:
            atomic_write(ackp, json.dumps(ack, ensure_ascii=False, indent=1))
    if args.mark_read:
        _mark_read(items)
    print(f"NEW={len(unread)} TOTAL={len(items)}")      # 供 sync_watch.sh 判断是否触发钩子
    tag = f"📥 {len(unread)} 条新同步" if unread else "📥 无新同步"
    print(f"  [apply] {me}: {tag}（收件箱共 {len(items)} 条）→ {os.path.relpath(INBOX_MD, HERE)}",
          file=sys.stderr)
    if unread and args.print_new:
        for x in unread[:args.print_new]:
            mark = "★" if rel(x) else "·"
            print(f"    {mark} [{x.get('project_label') or '—'}] {x.get('title','')[:52]} "
                  f"← {x['from'].get('machine')}/{x['from'].get('agent') or x['from'].get('tool') or 'agent'}",
                  file=sys.stderr)
    return 0

def _ts_ord(x):
    dt = parse_iso(x.get("ts"))
    return dt.timestamp() if dt else 0.0

def _mark_read(items):
    """已读游标 = 水位线(watermark) + 水位线之后的 id 列表。
    早先只存「最后 4000 个 id」，收件箱一超过 4000 条，最老的那些每次都会掉出游标、
    重新变成「未读」——永远清不掉。水位线让更老的条目一律视为已读。"""
    ts = [str(x.get("ts") or "") for x in items if x.get("ts")]
    mark = max(ts) if ts else now_iso()
    ids = [x.get("id") for x in items if x.get("id") and str(x.get("ts") or "") >= mark]
    atomic_write(READ_CUR, json.dumps({"ts": now_iso(), "watermark": mark, "ids": ids[-2000:]},
                                      ensure_ascii=False, indent=1))

def cmd_read(args):
    me = safe_machine(args.machine)
    if not me or not os.path.isdir(os.path.join(RELAY_DIR, me)):
        print(f"✗ 没有名为 {args.machine!r} 的收件箱——拒绝操作（写错名字会把已读游标清空，"
              f"让所有旧消息重新变成未读）", file=sys.stderr)
        return 2
    _mark_read(read_inbox(me))
    print("  [read] 已把收件箱标记为已读", file=sys.stderr)
    return 0

def render_inbox(me, mine_live, unread, recent, recent_hours, max_render=40):
    L = []
    L.append(f"# 📥 SYNC_INBOX — {me}")
    L.append("")
    L.append(f"> 别的机器/agent 刚干完的活，已实时同步到本机。生成于 {now_iso()}。")
    L.append("> 本文件由 `relay.py apply` 本地重建、**不入库**；处理完请跑 `python3 relay.py read --machine "
             f"{me}` 标记已读。")
    L.append("")
    if mine_live:
        who = "、".join(f"`{p['agent']}`→{p['project_label'] or '?'}" for p in mine_live)
        L.append(f"**本机正在工作**：{who}")
    else:
        L.append("**本机当前无 working agent**（收到的都会先攒着）")
    L.append("")
    L.append(f"## 🆕 未读 ({len(unread)})")
    L.append("")
    if not unread:
        L.append("_（没有新消息）_")
    for x in unread[:max_render]:            # 封顶：没人跑 `relay.py read` 时未读会一直攒，
        L.append(_render_item(x, star=bool(x.get("project")) and any(   # 不封顶收件箱会无限膨胀
            p["project"] == x.get("project") for p in mine_live)))
    if len(unread) > max_render:
        L.append(f"\n_（还有 {len(unread) - max_render} 条更早的未读，见下方「最近」清单；"
                 f"处理完请跑 `python3 relay.py read --machine {me}`）_")
    L.append("")
    L.append(f"## 最近 {recent_hours}h 全部 ({len(recent)})")
    L.append("")
    if not recent:
        L.append("_（无）_")
    for x in recent:
        f = x.get("from", {})
        L.append(f"- `{str(x.get('ts',''))[5:16]}` **{x.get('title','')[:64]}** "
                 f"— {f.get('machine','?')}/{f.get('agent') or f.get('tool') or 'agent'}"
                 f" · {x.get('project_label') or '—'}")
    L.append("")
    return "\n".join(L) + "\n"

def _render_item(x, star=False):
    f = x.get("from", {})
    head = "★ **同项目**" if star else "·"
    tag = " ·（更新）" if x.get("update") else ""
    dtag = " ·derived" if x.get("derived") else ""
    body = (x.get("summary") or "").strip()
    body = "\n".join("  > " + l for l in body.splitlines()[:10]) if body else ""
    return (f"\n### {head} {x.get('title','(无标题)')}{tag}{dtag}\n"
            f"- 来源：`{f.get('machine','?')}` / `{f.get('agent') or f.get('tool') or 'agent'}`"
            f"{('（' + f.get('user') + '）') if f.get('user') else ''}"
            f" · 项目 **{x.get('project_label') or '—'}** · {x.get('date') or '无日期'}"
            f" · 状态 `{x.get('status') or '—'}`\n"
            f"- 同步于 `{x.get('ts','')}`\n"
            + (body + "\n" if body else ""))

def cmd_wake(args):
    """对 ssh 可达的在线 peer 立刻 `git pull` + apply —— 这是真正的“立刻”（~2s）。"""
    cfg = load_json(os.path.join(HERE, "sources.json"), {}) or {}
    by_machine = {}
    for s in cfg.get("sources", []):
        if isinstance(s, dict) and s.get("type") == "ssh" and s.get("host"):
            m = safe_machine(s.get("machine"))
            if m:
                by_machine[m] = s
    peers = live_machines(args.win, exclude=safe_machine(args.machine))
    targets = [m for m in peers if m in by_machine] if not args.only else \
              [m for m in [safe_machine(args.only)] if m in by_machine]
    if not targets:
        print("  [wake] 没有 ssh 可达的在线 peer（其余机器靠自己的 sync_watch.sh 拉取）",
              file=sys.stderr)
        return 0
    import shlex
    ok = 0
    for m in targets:
        s = by_machine[m]
        tgt = f"{s['user']}@{s['host']}" if s.get("user") else s["host"]
        base = ["ssh", "-o", "ConnectTimeout=6", "-o", "BatchMode=yes",
                "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=3"]
        if s.get("port"):
            base += ["-p", str(s["port"])]
        raw = str(s.get("repo") or "~/agent-memory-galaxy")
        # 不能对 `~/…` 做 shlex.quote —— 远端 `cd '~/x'` 不展开波浪号，必然 No such file。
        repo = ("\"$HOME\"/" + shlex.quote(raw[2:])) if raw.startswith("~/") else shlex.quote(raw)
        # **绝不 reset 对端**：对方可能正留着「push 失败、下次补推」的本地 commit（contribute.sh
        # 明确承诺保留），reset --hard 会把那份还没上线的记忆连同 relay 载荷一起抹掉。
        # 只做 ff-only。但 ff-only 也会因**脏树**失败，而被远程采集的机器上 auto_presence 每轮都会
        # 改写自己的 presence/ —— 那份脏是机器自己产生、hub 早已取走的，不该被当成「分叉」。
        # 所以：ff-only 失败先只丢弃 presence/ 的本地改动再试一次；还不行才是真分叉，如实报出来。
        # 无论如何 apply 照常跑（至少把已有的渲染出来）。
        cmd = (f"cd {repo} && git fetch -q origin main && "
               f"{{ git merge -q --ff-only origin/main 2>/dev/null "
               f"|| {{ git checkout -q -- presence 2>/dev/null; "
               f"git merge -q --ff-only origin/main 2>/dev/null; }} "
               f"|| echo AMG_DIVERGED; }}; "
               f"python3 relay.py apply --machine {shlex.quote(m)} 2>&1 | tail -2")
        try:
            r = None
            for _try in range(2):      # 链路时好时坏：一次不够，但也别为它拖住每分钟的轮询
                try:
                    r = subprocess.run(base + [tgt, cmd], capture_output=True, text=True,
                                       timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    r = None
                if r is not None and r.returncode == 0:
                    break
            if r is None:
                raise subprocess.TimeoutExpired(cmd, args.timeout)
            if r.returncode == 0:
                if "AMG_DIVERGED" in (r.stdout or ""):
                    print(f"  [wake] ⚠ {m} 的仓库已与 origin/main 分叉（有未推送的本地 commit？）——"
                          f"没有强制对齐，请人工到那台机 `git pull --rebase` 处理", file=sys.stderr)
                print(f"  [wake] ✓ {m} 已即时拉取 {r.stdout.strip()[:120]}", file=sys.stderr); ok += 1
            else:
                print(f"  [wake] · {m} 唤醒失败（非致命，等它自己轮询）: "
                      f"{(r.stderr or r.stdout).strip()[:120]}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"  [wake] · {m} 唤醒超时（非致命）", file=sys.stderr)
    return 0 if ok or not targets else 0

def _gc_own(writer, keep_days):
    """只清理自己写的 by-<自己>.jsonl（单写者不变式：绝不重写别人的文件）。"""
    if keep_days <= 0:
        return
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=keep_days)
    for fp in glob.glob(os.path.join(RELAY_DIR, "*", f"by-{writer}.jsonl")):
        keep, dropped = [], 0
        try:
            for line in open(fp, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    dt = parse_iso(json.loads(line).get("ts"))
                except Exception:
                    keep.append(line); continue
                if dt and dt < cutoff:
                    dropped += 1
                else:
                    keep.append(line)
        except Exception:
            continue
        if dropped:
            atomic_write(fp, "".join(l + "\n" for l in keep))
            print(f"  [gc] {os.path.relpath(fp, HERE)}: 清掉 {dropped} 条 >{keep_days} 天", file=sys.stderr)

def cmd_gc(args):
    with Lock():
        _gc_own(safe_machine(args.machine), args.keep_days)
    return 0

def cmd_status(args):
    ps = read_presence(args.win)
    print("== 在线 agent（status=working 且心跳新鲜）==")
    live = [p for p in ps if p["live"]]
    if not live:
        print("  (无)")
    for p in live:
        print(f"  🔴 {p['agent']}@{p['machine']} · {p['project_label'] or '—'} · "
              f"{(p['mins'] or 0):.0f}分钟前 :: {str(p['current'])[:44]}")
    idle = [p for p in ps if not p["live"]]
    if idle:
        print(f"  ({len(idle)} 个 idle/过期心跳未列出)")
    print("\n== 收件箱 ==")
    if not os.path.isdir(RELAY_DIR):
        print("  (还没有 relay/ 目录——没人中继过)")
        return 0
    for d in sorted(os.listdir(RELAY_DIR)):
        p = os.path.join(RELAY_DIR, d)
        if not os.path.isdir(p):
            continue
        items = read_inbox(d)
        ack = load_json(os.path.join(p, "_ack.json"), {}) or {}
        last = items[-1]["ts"] if items else "—"
        print(f"  {d}: {len(items)} 条（最新 {last}）；回执 {ack.get('updated','—')} "
              f"未读 {ack.get('unread','?')}")
    return 0

def cmd_presence_sync(args):
    """跑 auto_presence，但只在**实质变化**时才让 presence/ 落盘 —— 否则 30s 轮询
    会因心跳时间戳每次都变而产生提交风暴（沿用 update.sh 的哈希闸门思路）。"""
    me = safe_machine(args.machine)
    if not me:
        print("✗ --machine 名非法", file=sys.stderr); return 2
    before = {}
    for fp in glob.glob(os.path.join(HERE, "presence", f"{me}__*.json")):
        before[os.path.basename(fp)] = load_json(fp, {}) or {}
    r = subprocess.run([sys.executable, os.path.join(HERE, "auto_presence.py"),
                        "--machine", me, "--win", str(args.win)],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"  [presence] auto_presence 失败（非致命）: {r.stderr.strip()[:160]}", file=sys.stderr)
        return 0
    after = {}
    for fp in glob.glob(os.path.join(HERE, "presence", f"{me}__*.json")):
        after[os.path.basename(fp)] = load_json(fp, {}) or {}
    changed = set(before) ^ set(after)
    for k in set(before) & set(after):
        a, b = before[k], after[k]
        if (a.get("status") != b.get("status") or a.get("project_canonical") != b.get("project_canonical")
                or a.get("current") != b.get("current")):
            changed.add(k); continue
        m = minutes_since(a.get("heartbeat"))
        m2 = minutes_since(b.get("heartbeat"))
        if m is not None and m2 is not None and (m - m2) >= args.min_delta_min:
            changed.add(k)
    if not changed:
        for k, v in before.items():       # 还原时间戳，避免只有心跳前移的无意义 diff
            fp = os.path.join(HERE, "presence", k)
            if k in after:
                atomic_write(fp, json.dumps(v, ensure_ascii=False, indent=1))
        print("  [presence] 无实质变化（不落盘）", file=sys.stderr)
        print("UNCHANGED")
        return 0
    print(f"  [presence] {len(changed)} 个 presence 有实质变化 → 落盘", file=sys.stderr)
    print("CHANGED")
    return 0

# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description="AMG 实时上下同步中继")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, machine_help="本机唯一名"):
        p.add_argument("--machine", required=True, help=machine_help)
        p.add_argument("--win", type=int, default=DEFAULT_WIN,
                       help=f"presence 新鲜窗口(分钟)，默认 {DEFAULT_WIN}")

    p = sub.add_parser("scan", help="算出本机新增/更新的记忆条目（只读）")
    common(p); p.add_argument("--fragment", default="")
    p.add_argument("--include-derived", action="store_true")
    p.add_argument("--max", type=int, default=DEFAULT_MAX)
    p.add_argument("--max-age-days", type=int, default=DEFAULT_AGE)
    p.add_argument("--repeat-min", type=int, default=DEFAULT_REPEAT_MIN)
    p.set_defaults(fn=cmd_scan)

    p = sub.add_parser("fanout", help="把新增记忆投递给此刻在线的其他机器")
    common(p, "写入者机器名（主脑代发时是主脑自己）")
    p.add_argument("--fragment", default="")
    p.add_argument("--agent", default="", help="发送方 agent 名（仅用于展示）")
    p.add_argument("--scan-all", action="store_true", help="主脑模式：代所有 fragment 中继")
    p.add_argument("--include-local", action="store_true",
                   help="--scan-all 时把本机 graph.json 也算作来源（本机记忆不写 fragments/）")
    p.add_argument("--include-derived", action="store_true")
    p.add_argument("--no-bootstrap", action="store_true", help="首次见到的来源也立刻投递（会灌历史）")
    p.add_argument("--drop-pending", action="store_true",
                   help="没人在线时直接记账丢弃（默认相反：留到有人上线再投）")
    p.add_argument("--max", type=int, default=DEFAULT_MAX)
    p.add_argument("--max-age-days", type=int, default=DEFAULT_AGE)
    p.add_argument("--repeat-min", type=int, default=DEFAULT_REPEAT_MIN)
    p.add_argument("--catchup-min", type=int, default=DEFAULT_CATCHUP,
                   help="补投窗口(分钟)：这段时间内中继过的条目，对之后才上线的机器仍会补投")
    p.add_argument("--keep-days", type=int, default=14, help="顺手清理自己写的过期收件条目")
    p.set_defaults(fn=cmd_fanout)

    p = sub.add_parser("presence-bundle", help="打包本机 auto presence（供 pull_remote 回传）")
    common(p)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_presence_bundle)

    p = sub.add_parser("local-scan", help="快扫本机记忆 → relay 专用快照（不入库）")
    common(p)
    p.add_argument("--roots", default="", help="逗号分隔根目录，缺省取 sources.json 里同名 local 源")
    p.add_argument("--user", default="", help="推送者身份")
    p.add_argument("--timeout", type=int, default=180)
    p.set_defaults(fn=cmd_local_scan)

    p = sub.add_parser("apply", help="收件端：渲染 SYNC_INBOX.md + 写回执")
    common(p, "收件机器名")
    p.add_argument("--recent-hours", type=int, default=24)
    p.add_argument("--max-render", type=int, default=40, help="SYNC_INBOX.md 里最多详细展开多少条未读")
    p.add_argument("--mark-read", action="store_true")
    p.add_argument("--print-new", type=int, default=5, help="stderr 上打印前 N 条新消息，0=不打印")
    p.set_defaults(fn=cmd_apply)

    p = sub.add_parser("read", help="标记收件箱已读")
    common(p, "收件机器名"); p.set_defaults(fn=cmd_read)

    p = sub.add_parser("wake", help="ssh 唤醒在线 peer 立刻拉取")
    common(p, "发送方机器名（不唤醒自己）")
    p.add_argument("--only", default="", help="只唤醒指定机器")
    p.add_argument("--timeout", type=int, default=25)
    p.set_defaults(fn=cmd_wake)

    p = sub.add_parser("gc", help="清理自己写的过期收件条目")
    common(p); p.add_argument("--keep-days", type=int, default=14)
    p.set_defaults(fn=cmd_gc)

    p = sub.add_parser("status", help="在线 peer / 收件箱概览")
    p.add_argument("--machine", default="", help="（可选，仅展示用）")
    p.add_argument("--win", type=int, default=DEFAULT_WIN)
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("presence-sync", help="刷新本机 presence（仅实质变化才落盘）")
    common(p)
    p.add_argument("--min-delta-min", type=int, default=5)
    p.set_defaults(fn=cmd_presence_sync)

    args = ap.parse_args()
    os.makedirs(STATE_DIR, exist_ok=True)
    return args.fn(args) or 0

if __name__ == "__main__":
    sys.exit(main())
