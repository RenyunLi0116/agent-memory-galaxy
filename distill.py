#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
distill.py — 从各机 Claude/Codex/Cursor 原生会话原文「提炼」派生记忆
=====================================================================
用途：当某个项目**没写** agent_memory.md（也没有 Claude memory/ 覆盖）时，
     从原生会话记录里**只抽结构化字段**（标题 / 日期 / 文件 / 工具 / 可选摘要），
     按【项目 × 天】聚合成 agent_memory 风格的 entry，打 `derived` 标记并入 fragment，
     让这些「没人手写记录」的项目也能进 Agent Memory Galaxy 知识图谱。

红线（隐私）：绝不提取对话正文 / 代码片段 / 工具输出 / 粘贴的密钥。
     只碰：标题、时间戳、文件路径、工具名/次数；以及（可选、默认关）Claude 自带的压缩摘要。

三源：
  claude : ~/.claude/projects/<slug>/*.jsonl（**只读主会话**；跳过 subagents/workflows/tool-results）
  codex  : ~/.codex/sessions/**/rollout-*.jsonl（+ history.jsonl；本机若无则优雅空跑）
  cursor : ~/.config/Cursor/User/globalStorage/state.vscdb（sqlite 只读；bubbleId/composerData）

策略（与用户确认一致）：
  - 仅补缺口：项目已有 agent_memory.md 或 Claude memory/ 覆盖 → 跳过，不与人工记录重复。
  - 项目×天聚合：同项目同天的多个 session 合成一条 entry。
  - derived 次级：节点带 derived=true，前端可区分/一键筛掉。
  - 混合：默认纯启发式（零依赖）；--llm 时可对**已抽的结构化字段**做一句话润色（不喂原文）。

产出：默认写 `fragments/<machine>-distilled.json`（独立文件，汇总端 collect --merge 的
     `fragments/*.json` glob 会自动合并，**collect.py / 加密 / 前端链路零改动**）。

复用 collect.py 的 canonical 项目归并、实体抽取、图容器，保持 schema 一致。
"""
import os, re, sys, json, glob, argparse, sqlite3, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import collect   # 复用：Graph / apply_canon / project_for_* / extract_entities / classify_task / squash ...

HOME = os.path.expanduser("~")
MAX_FILES = 12          # 每条聚合 entry 最多列几个文件
MAX_TITLES = 4          # 每条最多列几个 session 标题

# 只抽结构化字段，但仍对可能夹带的敏感串做兜底红字（即便进的是加密 blob，也纵深防御）
_SECRET = re.compile(r'(?i)(sk-[a-z0-9]{12,}|ghp_[a-z0-9]{20,}|AKIA[0-9A-Z]{12,}|xox[baprs]-[\w-]{10,}'
                     r'|-----BEGIN [A-Z ]+PRIVATE KEY-----|password\s*[:=]\s*\S+|token\s*[:=]\s*\S+)')
def redact(s: str) -> str:
    return _SECRET.sub('‹secret›', s or '')

def dedup_keep(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

def uri_to_path(u: str) -> str:
    """file:///a/b -> /a/b；vscode-remote://ssh-remote+host/a/b -> /a/b；其它原样返回。"""
    if not isinstance(u, str):
        return ""
    if u.startswith("file://"):
        return u[len("file://"):]
    m = re.match(r'vscode-remote://[^/]+(/.*)$', u)
    if m:
        return m.group(1)
    return u

# ----------------------------- 源1：Claude Code jsonl -----------------------------
def iter_claude(home):
    """遍历 ~/.claude/projects/<slug>/*.jsonl 主会话，产出结构化 session 记录。"""
    base = os.path.join(home, ".claude", "projects")
    if not os.path.isdir(base):
        return
    for slug in sorted(os.listdir(base)):
        pdir = os.path.join(base, slug)
        if not os.path.isdir(pdir):
            continue
        for fp in sorted(glob.glob(os.path.join(pdir, "*.jsonl"))):   # 只顶层：不递归 subagents/workflows/tool-results
            rec = _parse_claude_session(fp, slug)
            if rec:
                yield rec

def _parse_claude_session(fp, slug):
    cwds, dates, files, title, compact = {}, set(), [], None, None
    try:
        f = open(fp, encoding="utf-8", errors="replace")
    except Exception:
        return None
    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue                      # 坏行安全跳过
            if not isinstance(o, dict):
                continue
            cwd = o.get("cwd")
            if isinstance(cwd, str) and cwd:
                cwds[cwd] = cwds.get(cwd, 0) + 1
            ts = o.get("timestamp")
            if isinstance(ts, str) and len(ts) >= 10 and ts[4] == '-':
                dates.add(ts[:10])
            if o.get("type") == "ai-title" and o.get("aiTitle") and not title:
                title = str(o["aiTitle"]).strip()
            # 结构化：只从 assistant 的 tool_use(Edit/Write/NotebookEdit) 抽 file_path
            m = o.get("message")
            if isinstance(m, dict):
                c = m.get("content")
                if isinstance(c, list):
                    for b in c:
                        if (isinstance(b, dict) and b.get("type") == "tool_use"
                                and b.get("name") in ("Edit", "Write", "NotebookEdit")):
                            p = (b.get("input") or {}).get("file_path") or (b.get("input") or {}).get("notebook_path")
                            if isinstance(p, str) and p:
                                files.append(p)
            # Claude 自带压缩摘要（记录带 isCompactSummary:true）；默认不取，--with-summary 才用
            if o.get("isCompactSummary") and compact is None:
                mm = o.get("message")
                if isinstance(mm, dict):
                    cc = mm.get("content")
                    if isinstance(cc, str):
                        compact = cc
                    elif isinstance(cc, list):
                        txt = " ".join(b.get("text", "") for b in cc
                                       if isinstance(b, dict) and b.get("type") == "text")
                        compact = txt or None
    if not cwds and not files and not dates:
        return None
    cwd = max(cwds, key=cwds.get) if cwds else None     # 一 session 多 cwd → 取出现最多的
    return {
        "tool": "claude", "source_id": os.path.basename(fp), "slug": slug,
        "cwd": cwd, "dates": sorted(dates), "title": title, "files": files,
        "summary": (compact.strip()[:400] if compact else None),
    }

# ----------------------------- 源2：Codex rollout jsonl -----------------------------
def iter_codex(home):
    """~/.codex/sessions/**/rollout-*.jsonl。本机暂无 → 空跑；有则按 rollout 事件抽结构化字段。"""
    sess = os.path.join(home, ".codex", "sessions")
    if not os.path.isdir(sess):
        return
    for fp in sorted(glob.glob(os.path.join(sess, "**", "rollout-*.jsonl"), recursive=True)):
        rec = _parse_codex_session(fp)
        if rec:
            yield rec

def _parse_codex_session(fp):
    cwd, dates, files, title = None, set(), [], None
    # 文件名日期兜底： .../sessions/YYYY/MM/DD/rollout-...
    mdate = re.search(r'/(\d{4})/(\d{2})/(\d{2})/rollout-', fp)
    if mdate:
        dates.add("-".join(mdate.groups()))
    try:
        f = open(fp, encoding="utf-8", errors="replace")
    except Exception:
        return None
    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if not isinstance(o, dict):
                continue
            # session-meta / config 事件带 cwd
            for k in ("cwd", "workdir", "working_directory"):
                v = o.get(k) or (o.get("payload") or {}).get(k) if isinstance(o.get("payload"), dict) else o.get(k)
                if isinstance(v, str) and v and not cwd:
                    cwd = v
            ts = o.get("timestamp") or o.get("time")
            if isinstance(ts, str) and len(ts) >= 10 and ts[4] == '-':
                dates.add(ts[:10])
            typ = o.get("type") or o.get("event") or ""
            # 文件编辑：apply_patch / patch / function_call 里的 path 字段（只取路径，不取内容）
            if "patch" in str(typ).lower() or "apply" in str(typ).lower():
                for cand in (o, o.get("payload") if isinstance(o.get("payload"), dict) else {}):
                    if isinstance(cand, dict):
                        p = cand.get("path") or cand.get("file") or cand.get("filename")
                        if isinstance(p, str) and p:
                            files.append(p)
            if not title:
                # 标题只用 session id / 首个 message 的截断（避免拉正文，最多 60 字且过密钥红）
                sid = o.get("session_id") or o.get("id")
                if sid:
                    title = f"codex-{str(sid)[:12]}"
    if not cwd and not files and not dates:
        return None
    return {"tool": "codex", "source_id": os.path.basename(fp), "slug": None,
            "cwd": cwd, "dates": sorted(dates), "title": title, "files": files, "summary": None}

# ----------------------------- 源3：Cursor state.vscdb (sqlite) -----------------------------
def _cur_load(v):
    if isinstance(v, (bytes, bytearray)):
        try:
            v = v.decode("utf-8")
        except Exception:
            return None
    if not isinstance(v, str):
        return None
    try:
        return json.loads(v)
    except Exception:
        return None

def iter_cursor(home):
    """Cursor 全局库 cursorDiskKV：composerData:<cid> + bubbleId:<cid>:<b>。只抽结构化：日期/文件/(合成)标题。"""
    db = os.path.join(home, ".config", "Cursor", "User", "globalStorage", "state.vscdb")
    if not os.path.isfile(db):
        return
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except Exception:
        return
    try:
        comp = {}   # cid -> composerData dict
        try:
            for key, val in conn.execute("SELECT key,value FROM cursorDiskKV WHERE key LIKE 'composerData:%'"):
                d = _cur_load(val)
                if isinstance(d, dict):
                    comp[key.split(":", 1)[1]] = d
        except sqlite3.Error:
            pass
        bubbles = {}   # cid -> list[dict]
        try:
            for key, val in conn.execute("SELECT key,value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%'"):
                parts = key.split(":")
                if len(parts) < 3:
                    continue
                cid = parts[1]
                d = _cur_load(val)
                if isinstance(d, dict):
                    bubbles.setdefault(cid, []).append(d)
        except sqlite3.Error:
            pass
    finally:
        conn.close()

    cids = set(comp) | set(bubbles)
    for cid in sorted(cids):
        dates, files = set(), []
        for b in bubbles.get(cid, []):
            ts = b.get("createdAt")
            if isinstance(ts, str) and len(ts) >= 10 and ts[4] == '-':
                dates.add(ts[:10])
            for blk in (b.get("suggestedCodeBlocks") or []):
                fn = blk.get("fileName") if isinstance(blk, dict) else None
                if isinstance(fn, str) and fn:
                    files.append(uri_to_path(fn))
            for rf in (b.get("relevantFiles") or []):
                if isinstance(rf, str) and rf:
                    files.append(uri_to_path(rf))
        cd = comp.get(cid, {})
        if not dates:
            ms = cd.get("createdAt")
            if isinstance(ms, (int, float)) and ms > 0:
                try:
                    dates.add(datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m-%d"))
                except Exception:
                    pass
        # 标题：优先 composerData 的原生生成名（若有），否则由文件名合成；绝不用 bubble 正文
        title = None
        for k in ("name", "title", "composerTitle"):
            v = cd.get(k)
            if isinstance(v, str) and v.strip():
                title = v.strip(); break
        if not files and not dates:
            continue
        yield {"tool": "cursor", "source_id": cid[:12], "slug": None,
               "cwd": None, "dates": sorted(dates), "title": title, "files": files, "summary": None}

# ----------------------------- 项目归属 / 缺口过滤 -----------------------------
# 工作区容器目录名：其下第一层才是「一个项目」（多机通用约定：.../Project/<name>）
CONTAINER_SEGS = {"project", "projects", "repo", "repos", "code", "workspace", "work", "src"}
# 数据挂载/非工作项目：整段命中则不视为可提炼项目
DATA_SEGS = {"nas", "data", "datasets", "dataset", ".trash", "trash"}

def project_root_of(cwd):
    """把 cwd 上卷到其所属「项目根」：容器目录(Project/…)下第一层。
    返回 None 表示：数据挂载 / 容器本身 / 无法认定为项目 → 不提炼。"""
    if not cwd:
        return None
    parts = [p for p in cwd.rstrip("/").split("/") if p != ""]
    low = [p.lower() for p in parts]
    _hp = [p.lower() for p in HOME.rstrip("/").split("/") if p != ""]
    _rel = low[len(_hp):] if low[:len(_hp)] == _hp else low   # 只看 $HOME 之下的段，避免把 '/data/...' 家目录前缀误判为数据挂载
    if any(seg in DATA_SEGS for seg in _rel):     # 命中 NAS/data 等 → 数据目录，跳过
        return None
    for i, seg in enumerate(low):
        if seg in CONTAINER_SEGS:
            if i + 1 < len(parts):
                return "/" + "/".join(parts[:i + 2])   # 容器下第一层 = 项目根
            return None                                 # cwd 就是容器本身 → 非项目
    # 无容器约定：向上找最近的项目标记(.git/.amg_project/agent_memory.md)，不越过 $HOME
    home_parts = [p for p in HOME.rstrip("/").split("/") if p != ""]
    d = "/" + "/".join(parts)
    steps = 0
    while steps < 6 and len([p for p in d.strip("/").split("/") if p]) > len(home_parts):
        if any(os.path.exists(os.path.join(d, mk)) for mk in (".git", ".amg_project", "agent_memory.md")):
            return d
        d = os.path.dirname(d); steps += 1
    return cwd.rstrip("/")            # 兜底：用 cwd 自身

def session_cwd(rec):
    """取 session 的工作目录：显式 cwd 优先；否则从绝对路径文件推断最常见父目录。"""
    cwd = rec.get("cwd")
    if cwd:
        return cwd
    dirs = {}
    for f in rec.get("files", []):
        if isinstance(f, str) and f.startswith("/"):
            d = os.path.dirname(f)
            dirs[d] = dirs.get(d, 0) + 1
    return max(dirs, key=dirs.get) if dirs else None

def project_of_session(rec):
    """把 session 映射到 canonical (pkey,plabel)；先把 cwd 上卷到项目根。无法定位→None。"""
    root = project_root_of(session_cwd(rec))
    if not root:
        return None
    # 复用 collect：用 <root>/agent_memory.md 走 project_for_manual（含 .amg_project / NAS / HOME 规则）
    return collect.project_for_manual(os.path.join(root, "agent_memory.md"))

def covered_pkeys(home, candidate_cwds):
    """已被人工/自动记忆覆盖的项目 pkey 集合 → 这些项目不提炼（仅补缺口）。"""
    covered = set()
    # (a) Claude memory/ 覆盖的 slug
    for md in glob.glob(os.path.join(home, ".claude", "projects", "*", "memory", "*.md")):
        slug = md.split("/.claude/projects/", 1)[1].split("/memory/", 1)[0]
        pk, _ = collect.project_for_auto(slug)
        covered.add(pk)
    # (b) 各候选 cwd 下若有 agent_memory.md → 该项目已人工覆盖
    for cwd in candidate_cwds:
        if cwd and os.path.isfile(os.path.join(cwd, "agent_memory.md")):
            pk, _ = collect.project_for_manual(os.path.join(cwd, "agent_memory.md"))
            covered.add(pk)
    return covered

# ----------------------------- 组装 entry / 输出 -----------------------------
def build_excerpt(tool, sessions, files, with_summary):
    lines = [f"[自动提炼·derived] 来源:{tool} 原生会话 × {len(sessions)}"]
    titles = dedup_keep(redact(s["title"]) for s in sessions if s.get("title"))
    if titles:
        lines.append("标题: " + " / ".join(titles[:MAX_TITLES]))
    bases = dedup_keep(os.path.basename(f) for f in files if f)
    if bases:
        lines.append("涉及文件: " + ", ".join(bases[:MAX_FILES]))
    if with_summary:
        summ = dedup_keep(redact(s["summary"]) for s in sessions if s.get("summary"))
        if summ:
            lines.append("摘要: " + " ".join(summ)[:400])
    return "\n".join(lines)

def llm_polish(blob):
    """可选：把结构化字段交给本机 claude CLI 润成一句中文摘要（只喂结构化 blob，不喂原文）。失败则原样返回。"""
    prompt = ("下面是从某次编程会话里提取的**结构化字段**（标题/文件清单）。"
              "请用一句不超过40字的中文概括这次会话大概在做什么，只输出这句话：\n\n" + blob)
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=60)
        out = (r.stdout or "").strip().splitlines()
        if r.returncode == 0 and out:
            return out[0][:80]
    except Exception:
        pass
    return None

def distill(args):
    collect.load_projects()
    home = os.path.expanduser(args.home)
    srcs = [s.strip() for s in args.sources.split(",") if s.strip()]

    # 1) 采集三源 session
    raw = []
    if "claude" in srcs: raw += list(iter_claude(home))
    if "codex"  in srcs: raw += list(iter_codex(home))
    if "cursor" in srcs: raw += list(iter_cursor(home))

    # 2) 定位项目 + 缺口过滤（缺口判定用上卷后的「项目根」，子目录会归到父项目）
    cand_roots = {project_root_of(session_cwd(r)) for r in raw}
    covered = covered_pkeys(home, {r for r in cand_roots if r})
    if args.verbose:
        print(f"  已覆盖项目 pkey({len(covered)}): {sorted(covered)}", file=sys.stderr)

    # (pkey, date) -> {plabel, tool, sessions[], files[]}
    groups, skipped_covered, skipped_noproj = {}, 0, 0
    for r in raw:
        proj = project_of_session(r)
        if not proj:
            skipped_noproj += 1; continue
        pkey, plabel = proj
        if pkey in covered:
            skipped_covered += 1; continue
        date = (r["dates"][0] if r.get("dates") else None) or "0000-00-00"   # 归到起始日
        gk = (pkey, date, r["tool"])
        g = groups.setdefault(gk, {"plabel": plabel, "tool": r["tool"], "sessions": [], "files": []})
        g["sessions"].append(r)
        g["files"].extend(r.get("files", []))

    # 3) 组图（复用 collect.Graph）
    graph = collect.Graph()
    machine = args.machine
    mach_id = graph.node(f"machine:{machine}", "machine", machine)
    n_entries = 0
    for (pkey, date, tool), g in sorted(groups.items()):
        plabel = g["plabel"]
        proj_id = graph.node(f"project:{pkey}", "project", plabel, machines=[machine])
        graph.edge(proj_id, mach_id, "on")
        files = g["files"]
        excerpt = build_excerpt(tool, g["sessions"], files, args.with_summary)
        # 供实体抽取的 blob：标题 + 文件全路径（让 file/dataset/model 节点建起来）
        blob = "\n".join([excerpt] + dedup_keep(files))
        if args.llm:
            polished = llm_polish(excerpt)
            if polished:
                excerpt = "摘要(LLM): " + polished + "\n" + excerpt
        title = (dedup_keep(s["title"] for s in g["sessions"] if s.get("title")) or [None])[0]
        title = (redact(title)[:60] if title else None) or f"{plabel}·{tool}提炼·{date}"
        eid = f"entry:{machine}:distill:{tool}:{pkey}:{date}"
        graph.node(eid, "entry", title[:80],
                   date=(date if date != "0000-00-00" else None),
                   status="logged", tool=tool, derived=True,
                   task=collect.classify_task(blob),
                   machine=machine, project=plabel, source=f"native:{tool}",
                   n_sessions=len(g["sessions"]),
                   weight=max(len(excerpt), 1), excerpt=excerpt)
        graph.edge(eid, proj_id, "in")
        graph.edge(eid, mach_id, "located")
        collect.extract_entities(graph, eid, blob)     # 文件/数据集/模型节点 + touches/uses 边
        n_entries += 1

    # 4) 输出：合并进独立 distilled fragment（collect --merge 的 fragments/*.json glob 会自动吸收）
    nodes = list(graph.nodes.values())
    edges = list(graph.edges.values())
    stats = {"raw_sessions": len(raw), "skipped_covered": skipped_covered,
             "skipped_noproject": skipped_noproj, "derived_entries": n_entries,
             "groups": len(groups)}
    print(json.dumps({"machine": machine, "sources": srcs, **stats}, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("  [dry-run] 未写文件。", file=sys.stderr)
        if args.verbose:
            for n in nodes:
                if n["type"] == "entry":
                    print("  ---", n["label"], "\n     " + n.get("excerpt", "").replace("\n", "\n     "),
                          file=sys.stderr)
        return
    out = {"meta": {"generated": args.now or "", "machine": machine, "derived": True,
                    "sources": srcs, "stats": stats},
           "nodes": nodes, "edges": edges}
    outp = args.out or os.path.join(HERE, "fragments", f"{machine}-distilled.json")
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✓ 写出 {outp}（{len(nodes)} 节点 / {len(edges)} 边，全 derived）。", file=sys.stderr)

def main():
    ap = argparse.ArgumentParser(description="从 Claude/Codex/Cursor 原生会话提炼 derived 记忆")
    ap.add_argument("--machine", default="local", help="本机唯一名（与 contribute.sh 一致）")
    ap.add_argument("--sources", default="claude,codex,cursor", help="逗号分隔: claude,codex,cursor")
    ap.add_argument("--home", default="~", help="扫描的用户主目录（默认 $HOME）")
    ap.add_argument("--out", default="", help="输出文件（默认 fragments/<machine>-distilled.json）")
    ap.add_argument("--with-summary", action="store_true", help="额外纳入 Claude 自带压缩摘要（默认关，更保守）")
    ap.add_argument("--llm", action="store_true", help="用本机 claude CLI 对结构化字段润一句摘要（不喂原文）")
    ap.add_argument("--dry-run", action="store_true", help="只统计、不写文件（-v 可预览 entry）")
    ap.add_argument("--now", default="", help="时间戳字符串（写入 meta.generated）")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    distill(args)

if __name__ == "__main__":
    main()
