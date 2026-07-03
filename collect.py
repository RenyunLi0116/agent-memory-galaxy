#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CyberMemory 采集器
=========================
把分散在多台机器、两套格式里的 agent 工作记录解析成一张规范的知识图谱 graph.json。

两套格式：
  1) 手工 agent_memory.md（CLAUDE.md 约定）：`## 日期/Session` 分节，含 (agent)、[doing]/[done]。
  2) Claude 自动记忆 .claude/projects/<slug>/memory/*.md：YAML frontmatter + [[双链]] + MEMORY.md 索引。

输出 graph.json：{ meta, nodes:[{id,type,label,...}], edges:[{source,target,type}] }。
零外部依赖（仅标准库），任何机器都能跑。
"""
import os, re, sys, json, html, hashlib, subprocess, datetime, argparse, collections, shlex

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------- 工具 -----------------------------
def squash(s: str) -> str:
    """归一化 key：去掉分隔符与大小写差异，保留 CJK。用于跨格式合并同一项目/实体。"""
    return re.sub(r'[\s/_.\-﻿]+', '', (s or '').lower())   # ﻿: 剥 Windows Notepad 的 UTF-8 BOM

def short_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()[:8]

# ----------------------------- 实体抽取规则 -----------------------------
# (实体类型, 正则, 边类型)。group(1) 若存在则取之，否则取整个匹配。
# 这里只放【通用】实体规则；团队/项目专有的数据集、模型名等，请在 projects.json 的
# "entity_patterns": [{"type":..,"regex":..,"edge":..}] 里补充（load_projects 会追加）。
ENTITY_PATTERNS = [
    ("server",  re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b'),        "on"),
    ("model",   re.compile(r'(?i)\bvit[-_]?[glbs]\b'),             "uses"),
    ("wandb",   re.compile(r'(?i)wandb[ _]?id[:\s]+([\w./-]+)'),   "tracks"),
    ("method",  re.compile(r'思路\s*\d+'),                          "explores"),
]
# Notion 页面名：命中即建对应 notion 节点。可在 projects.json 的 "notion_pages":[...] 里自定义。
NOTION_PAGES = ["Weekly Progress", "Paper Reading", "Daily Paper"]
FILE_RE = re.compile(
    r'(?:/(?:home|data|root|mnt|opt)/[\w./~+\-]+'          # 绝对路径
    r'|[\w./\-]+\.(?:py|sh|ya?ml|h5|pt|ckpt|json|csv|mcap|mp4|ipynb))'  # 带扩展名的文件
)
AGENT_RE  = re.compile(r'(?i)\(\s*(claude|codex|cursor|gpt[\w\-]*|gemini|team[\s\-]?leader|human)\s*\)')
DATE_RE   = re.compile(r'(20\d{2}-\d{2}-\d{2})')
SESSION_RE= re.compile(r'(?i)session\s*(\d+)')
LINK_RE   = re.compile(r'\[\[([^\]]+)\]\]')

MAX_FILES_PER_ENTRY = 6      # 每条记录最多抽几个文件，防爆炸
EXCERPT_LEN = 600

# 任务类型分型：按关键词命中数打分，最高者胜（理解"每条记录是哪类工作"）
TASK_KW = [
    ("训练", re.compile(r"(?i)训练|首训|重训|\btrain|epoch|checkpoint|ckpt|收敛|\bloss\b|wandb")),
    ("数据", re.compile(r"(?i)转码|提取|提特征|mcap|\.mp4|rsync|上传|下载|\.h5|内参|intrinsic|undist|去畸变|数据集|dataset")),
    ("评测", re.compile(r"(?i)评测|\beval|指标|rollout|planning|对照|holdout|留出|metric")),
    ("部署", re.compile(r"(?i)部署|环境|\bssh\b|crontab|mihomo|代理|\bgpu\b|磁盘|安装|配置|端口|tmux|conda|\bpip\b|proxy")),
    ("调研", re.compile(r"(?i)论文|\bpaper|阅读|调研|思路|方案|设计|reading|baseline|方法论")),
    ("同步", re.compile(r"(?i)notion|周报|同步|入库|progress|汇报")),
    ("规划", re.compile(r"(?i)\[doing\]|计划|待办|\btodo\b|目标|规划|接手|分工")),
]

def classify_task(text):
    best, score = "其他", 0
    for name, pat in TASK_KW:
        c = len(pat.findall(text))
        if c > score:
            best, score = name, c
    return best

# ----------------------------- 项目归属 -----------------------------
_HOME = os.path.expanduser("~")
HOME_ROOT_FILES = {os.path.join(_HOME, "agent_memory.md"),
                   os.path.join(_HOME, ".ssh", "agent_memory.md")}

# ---- canonical project 归一化（跨机把"同一个项目"的不同目录名合并成一个节点）----
ALIAS = {}    # squash(原目录名) -> canonical id(raw)
LABELS = {}   # squash(canonical id) -> 友好显示名
PROJ_TEXT = {}  # project key -> 该项目全部记忆文本(小写)，用于检测跨项目引用/派生
STOP_KEYS = {"localenv", "nas", "cybermemory"}  # 非研究伪项目：不作为引用/派生关系端点；可由 projects.json 的 "stop_keys" 扩展

def load_projects():
    fp = os.path.join(HERE, "projects.json")
    if not os.path.isfile(fp):
        return
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception as e:
        print(f"  ! projects.json 解析失败: {e}", file=sys.stderr); return
    for orig, canon in (d.get("aliases") or {}).items():
        ALIAS[squash(orig)] = canon
    for cid, nice in (d.get("labels") or {}).items():
        LABELS[squash(cid)] = nice
    for ep in (d.get("entity_patterns") or []):     # 团队自定义实体规则
        try:
            ENTITY_PATTERNS.append((ep["type"], re.compile(ep["regex"]), ep.get("edge", "uses")))
        except Exception as e:
            print(f"  ! projects.json entity_patterns 跳过一条: {e}", file=sys.stderr)
    for pg in (d.get("notion_pages") or []):
        if pg not in NOTION_PAGES:
            NOTION_PAGES.append(pg)
    for k in (d.get("stop_keys") or []):
        STOP_KEYS.add(squash(k))

def canon_of(cid_raw):
    return (squash(cid_raw), LABELS.get(squash(cid_raw), cid_raw))

def apply_canon(key, label, path=None):
    if path and "/sources_cache/" not in path:      # 项目目录内 .amg_project（远程扁平缓存读不到，跳过）
        ap = os.path.join(os.path.dirname(path), ".amg_project")
        if os.path.isfile(ap):
            try:
                cid = ""
                for ln in open(ap, encoding="utf-8").read().splitlines():
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):   # 跳过空行/注释，取第一条有效行
                        cid = ln; break
            except Exception:
                cid = ""
            if cid:
                return canon_of(cid)
    for probe in (squash(label), key):              # projects.json aliases
        if probe in ALIAS:
            return canon_of(ALIAS[probe])
    return (key, label)

def resolve_canon(raw):
    s = squash(raw)
    if s in ALIAS:
        return canon_of(ALIAS[s])
    return canon_of(raw)

def project_for_manual(path: str):
    if path in HOME_ROOT_FILES:
        return apply_canon("localenv", "本机环境(local)", path)
    if "/sources_cache/" in path:      # 远程缓存扁平化：a__b__Project__<真实项目>__agent_memory.md
        parts = os.path.basename(path).split("__")
        rk = rl = None
        for i, p in enumerate(parts):
            if p.lower() == "project" and i + 1 < len(parts):
                rk, rl = squash(parts[i + 1]), parts[i + 1]; break
        if rk is None and len(parts) >= 2:
            rk, rl = squash(parts[-2]), parts[-2]
        if rk is None:
            rk, rl = "unknown", "unknown"
        return apply_canon(rk, rl, path)
    d = os.path.dirname(path)
    base = os.path.basename(d)
    if '/NAS/' in path:
        return apply_canon(squash('nas-' + base), 'NAS:' + base, path)
    return apply_canon(squash(base), base, path)

AUTO_ENV_RE = re.compile(r'^(home|data(-users)?|users)(-[\w.]+){1,2}(-(projects?|repos?|code|workspace|work|src))?$'
                         r'|^(projects?|repos?|code|workspace|work|src|desktop|documents)$')   # 裸容器词(如 label='Project')也算环境级

def project_for_auto(slug: str):
    s = slug.lower()
    m = re.search(r'project-(.+)$', s)
    if m:
        name = m.group(1)
    else:
        name = s.strip('-')
        # 直接位于家目录下的项目(如 /home/alice/research → slug home-alice-research)：剥掉家目录前缀
        # home-<user>- / data-users-<user>- / users-<user>-，留下真正的项目段，与 project_for_manual 的
        # basename 归并到同一节点(否则该项目自动记忆会被 AUTO_ENV_RE 误判成 local-env 而与手工记忆分裂)。
        mp = re.match(r'^(?:home|users|data-users)-[\w.]+-(.+)$', name)
        if mp:
            name = mp.group(1)
        # 剥完仍是裸家目录/容器词(home-alice / data-users-bob / project 等) → 归入本机环境伪项目
        if AUTO_ENV_RE.match(name):
            name = 'local-env'
    # 与手工项目对齐：同样走 canonical 归并（否则同一项目的自动记忆会裂成独立节点）
    return apply_canon(squash(name), name)

# ----------------------------- 图容器 -----------------------------
class Graph:
    def __init__(self):
        self.nodes = {}            # id -> dict
        self.edges = {}            # (s,t,type) -> dict

    def node(self, nid, ntype, label, **attrs):
        if nid not in self.nodes:
            self.nodes[nid] = {"id": nid, "type": ntype, "label": label}
        n = self.nodes[nid]
        for k, v in attrs.items():
            if v is None:
                continue
            # 列表型属性累加去重；标量型不覆盖已有
            if isinstance(v, list):
                cur = n.setdefault(k, [])
                for x in v:
                    if x not in cur:
                        cur.append(x)
            else:
                n.setdefault(k, v)
        return nid

    def edge(self, s, t, etype):
        if s == t or s is None or t is None:
            return
        key = (s, t, etype)
        if key not in self.edges:
            self.edges[key] = {"source": s, "target": t, "type": etype}

# ----------------------------- 实体抽取 -----------------------------
def extract_entities(g: Graph, owner_id: str, text: str):
    """从一段文字里抽出实体节点，并连边 owner -> entity。"""
    for etype, pat, edge in ENTITY_PATTERNS:
        for m in pat.finditer(text):
            raw = (m.group(1) if m.groups() else m.group(0)).strip(" .,:：；;()（）")
            if not raw or len(raw) > 60:
                continue
            key = squash(raw)
            if not key:
                continue
            nid = f"{etype}:{key}"
            g.node(nid, etype, raw)
            g.edge(owner_id, nid, edge)
    # Notion
    if re.search(r'(?i)notion', text):
        g.node("notion:notion", "notion", "Notion")
        g.edge(owner_id, "notion:notion", "syncs")
        for pg in NOTION_PAGES:
            if pg.lower() in text.lower():
                pid = f"notion:{squash(pg)}"
                g.node(pid, "notion", pg)
                g.edge(owner_id, pid, "syncs")
                g.edge(pid, "notion:notion", "in")
    # 文件（限量）
    seen = 0
    for m in FILE_RE.finditer(text):
        p = m.group(0).strip(" .,:：;)）")
        base = os.path.basename(p)
        if not base or '.' not in base or len(base) > 50:
            continue
        nid = f"file:{squash(base)}"
        g.node(nid, "file", base, paths=[p])
        g.edge(owner_id, nid, "touches")
        seen += 1
        if seen >= MAX_FILES_PER_ENTRY:
            break

# ----------------------------- 解析：手工 agent_memory.md -----------------------------
def parse_manual(g: Graph, path: str, machine: str, tool: str = "claude"):
    try:
        txt = open(path, encoding='utf-8', errors='replace').read()
    except Exception as e:
        print(f"  ! 读不了 {path}: {e}", file=sys.stderr)
        return 0
    pkey, plabel = project_for_manual(path)
    PROJ_TEXT[pkey] = PROJ_TEXT.get(pkey, "") + txt.lower()[:200000]   # 累积文本供跨项目引用检测
    proj_id = g.node(f"project:{pkey}", "project", plabel, machines=[machine])
    mach_id = g.node(f"machine:{machine}", "machine", machine)
    g.edge(proj_id, mach_id, "on")

    # 按 ## 分节（# 一级标题作为文件简介，忽略其内容做节点）
    lines = txt.splitlines()
    sections = []            # (heading, body_lines)
    cur_head, cur_body = None, []
    for ln in lines:
        if re.match(r'^##\s+\S', ln):
            if cur_head is not None:
                sections.append((cur_head, cur_body))
            cur_head, cur_body = ln[2:].strip(), []
        else:
            if cur_head is not None:
                cur_body.append(ln)
    if cur_head is not None:
        sections.append((cur_head, cur_body))

    count = 0
    for idx, (head, body_lines) in enumerate(sections):
        body = "\n".join(body_lines).strip()
        blob = head + "\n" + body
        date = (DATE_RE.search(head) or DATE_RE.search(body))
        date = date.group(1) if date else None
        am = AGENT_RE.search(head) or AGENT_RE.search(body[:300])
        # 只对显式标注的 agent 建节点/连边，避免未标注记录全堆给 claude 形成巨型枢纽
        agent = re.sub(r'[\s\-]', '', am.group(1)).lower() if am else None
        sess = SESSION_RE.search(head)
        session = sess.group(1) if sess else None
        scope = head + body[:250]
        if re.search(r'\[done\]|✅|已完成|完成\）|完成）', scope):
            status = "done"
        elif re.search(r'\[doing\]|进行中|运行中|▶|正在', scope):
            status = "doing"
        elif re.search(r'\[todo\]|待办|计划|后续|TODO', head):
            status = "planned"
        else:
            status = "logged"
        title = re.sub(r'\[(?:doing|done|todo)\]', '', head)
        title = re.sub(r'\(\s*(?:claude|codex|cursor|team[\s\-]?leader|human)\s*\)', '', title, flags=re.I)
        title = title.strip(" -—:：") or (date or f"entry {idx}")

        eid = f"entry:{machine}:{short_hash(path)}:{idx}"
        g.node(eid, "entry", title[:80],
               date=date, agent=agent, status=status, session=session, tool=tool,
               task=classify_task(blob),         # 任务类型：训练/数据/评测/部署/调研/同步/规划/其他
               machine=machine, project=plabel, source=path,
               weight=len(body),                 # job 体量 = 记录正文长度
               excerpt=body[:EXCERPT_LEN])
        g.edge(eid, proj_id, "in")
        g.edge(eid, mach_id, "located")
        if agent:
            aid = g.node(f"agent:{agent}", "agent", agent)
            g.edge(aid, eid, "did")
        extract_entities(g, eid, blob)
        count += 1
    return count

# ----------------------------- 解析：自动记忆 -----------------------------
def parse_frontmatter(txt: str):
    """极简 YAML frontmatter 解析（无需 PyYAML）。返回 (meta dict, body)。"""
    if not txt.startswith('---'):
        return {}, txt
    end = txt.find('\n---', 3)
    if end == -1:
        return {}, txt
    fm = txt[3:end].strip("\n")
    body = txt[end + 4:]
    root = {}
    stack = [(-1, root)]              # (该层父键的缩进, dict)
    for raw in fm.splitlines():
        if not raw.strip() or raw.strip().startswith('#'):
            continue
        indent = len(raw) - len(raw.lstrip())
        m = re.match(r'^\s*([\w.\-]+)\s*:\s*(.*)$', raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"\'')
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            child = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = val
    return root, body

def parse_auto(g: Graph, path: str, slug: str, machine: str):
    try:
        txt = open(path, encoding='utf-8', errors='replace').read()
    except Exception as e:
        print(f"  ! 读不了 {path}: {e}", file=sys.stderr)
        return 0
    name = os.path.splitext(os.path.basename(path))[0]
    if name == "MEMORY":
        return 0  # 索引文件单独处理
    meta, body = parse_frontmatter(txt)
    md = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
    ftype = md.get("type", "project")
    desc = meta.get("description", "")
    origin = md.get("originSessionId")

    pkey, plabel = project_for_auto(slug)
    PROJ_TEXT[pkey] = PROJ_TEXT.get(pkey, "") + (body or "").lower()[:200000]
    proj_id = g.node(f"project:{pkey}", "project", plabel, machines=[machine])
    mach_id = g.node(f"machine:{machine}", "machine", machine)
    g.edge(proj_id, mach_id, "on")

    fid = f"fact:{squash(name)}"
    g.node(fid, "fact", meta.get("name", name),
           memtype=ftype, description=desc, origin=origin, tool="claude",
           machine=machine, project=plabel, source=path,
           weight=len(body.strip()),
           excerpt=body.strip()[:EXCERPT_LEN])
    g.edge(fid, proj_id, "in")
    # [[双链]]
    for m in LINK_RE.finditer(body):
        tgt = m.group(1).strip()
        g.edge(fid, f"fact:{squash(tgt)}", "link")
    extract_entities(g, fid, body)
    return 1

def parse_memindex(g: Graph, path: str, slug: str):
    """MEMORY.md 索引：确认事实节点存在并标注它属于该项目（节点可能尚未建）。"""
    pkey, plabel = project_for_auto(slug)
    g.node(f"project:{pkey}", "project", plabel)
    try:
        txt = open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return
    for m in re.finditer(r'\]\(([\w.\-]+\.md)\)', txt):
        fname = os.path.splitext(m.group(1))[0]
        fid = f"fact:{squash(fname)}"
        # 不强建节点（解析事实文件时会建）；只确保项目内有连边
        if fid in g.nodes:
            g.edge(fid, f"project:{pkey}", "in")

# ----------------------------- 文件发现 -----------------------------
def is_manual_memory(fname: str) -> bool:
    return (fname == "agent_memory.md"
            or fname.endswith("_agent_memory.md")
            or (fname.startswith("server_") and "agent" in fname and fname.endswith(".md")))

def discover_local(root: str, cfg: dict, max_depth=None):
    """返回 [(path, kind, slug)]，kind in {manual, auto, memindex}。
    max_depth：相对 root 的最大下钻深度（NAS 等慢挂载用，避免遍历海量数据子树）。"""
    excl = cfg["exclude_substrings"]
    prune = set(cfg["prune_dir_names"])
    root_depth = root.rstrip('/').count('/')
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 剪枝
        dirnames[:] = [d for d in dirnames if d not in prune]
        if any(x in dirpath + "/" for x in excl):
            dirnames[:] = []
            continue
        if max_depth is not None and dirpath.rstrip('/').count('/') - root_depth >= max_depth:
            dirnames[:] = []   # 处理本层文件，但不再深入
        # 自动记忆目录： .../.claude/projects/<slug>/memory
        am = re.search(r'/\.claude/projects/([^/]+)/memory$', dirpath)
        if am:
            slug = am.group(1)
            for f in filenames:
                if f.endswith(".md"):
                    p = os.path.join(dirpath, f)
                    out.append((p, "memindex" if f == "MEMORY.md" else "auto", slug))
            continue
        for f in filenames:
            if is_manual_memory(f):
                out.append((os.path.join(dirpath, f), "manual", None))
    return out

# ----------------------------- ssh 拉取（Task#4 启用） -----------------------------
def pull_ssh(src: dict, cache_root: str):
    """把远程匹配文件 rsync 到本地 cache，带重试+超时（链路不稳）。返回本地 cache 目录。"""
    host, user = src["host"], src.get("user", "")
    port = src.get("port")
    target = f"{user}@{host}" if user else host
    cache = os.path.join(cache_root, src["machine"])
    os.makedirs(cache, exist_ok=True)
    ssh_opt = ["-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=15", "-o", "BatchMode=yes"]
    if port:
        ssh_opt += ["-p", str(port)]
    # 1) 远程找文件
    find_cmd = (
        "find " + " ".join(shlex.quote(r) for r in src["roots"]) +
        r' -maxdepth 6 -type f \( -name agent_memory.md -o -name "*_agent_memory.md" '
        r'-o -name "server_*agent*.md" \) 2>/dev/null'
    )
    files = []
    for attempt in range(4):
        try:
            r = subprocess.run(["ssh", *ssh_opt, target, find_cmd],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                files = [x for x in r.stdout.splitlines() if x.strip()]
                break
        except subprocess.TimeoutExpired:
            pass
        print(f"  · {src['machine']} find 重试 {attempt+1}/4", file=sys.stderr)
    rp = ["-e", "ssh " + " ".join(ssh_opt)]  # rsync over ssh with opts
    pulled = []
    for rf in files:
        flat = rf.lstrip("/").replace("/", "__")
        dst = os.path.join(cache, flat)
        ok = False
        for attempt in range(2):
            try:
                r = subprocess.run(
                    ["rsync", "-az", "--timeout=45", *rp, f"{target}:{rf}", dst],
                    capture_output=True, text=True, timeout=90)
                if r.returncode == 0:
                    ok = True
                    break
            except subprocess.TimeoutExpired:
                pass
            print(f"  · rsync {os.path.basename(rf)} 重试 {attempt+1}/2", file=sys.stderr)
        if not ok:   # rsync 失败 → ssh cat 兜底（更通用，不依赖远端 rsync）
            try:
                r = subprocess.run(["ssh", *ssh_opt, target, f"cat {shlex.quote(rf)}"],
                                   capture_output=True, text=True, timeout=90)
                if r.returncode == 0 and r.stdout:
                    open(dst, "w", encoding="utf-8").write(r.stdout)
                    ok = True
                    print(f"  · {os.path.basename(rf)} 用 ssh cat 兜底成功", file=sys.stderr)
            except subprocess.TimeoutExpired:
                pass
        if ok:
            pulled.append((dst, rf))
    print(f"  ✓ {src['machine']}: 拉到 {len(pulled)}/{len(files)} 个文件", file=sys.stderr)
    return pulled

# ----------------------------- 主流程 -----------------------------
def finalize(g: Graph):
    # 悬空 fact 链接目标（[[..]] 指向不存在文件）-> 标记为 dangling 节点而非静默
    for e in list(g.edges.values()):
        if e["type"] == "link" and e["target"] not in g.nodes:
            g.node(e["target"], "fact", e["target"].split(":", 1)[-1], dangling=True)
    # 度数 + 邻接
    deg = {nid: 0 for nid in g.nodes}
    adj = {nid: [] for nid in g.nodes}
    for e in g.edges.values():
        for a, b in ((e["source"], e["target"]), (e["target"], e["source"])):
            if a in deg:
                deg[a] += 1; adj[a].append(b)
    # weight（节点视觉大小 = job 体量）：
    #   entry/fact 已带正文长度；project = 旗下记录体量之和；其余 = 度数
    for nid, n in g.nodes.items():
        n["degree"] = deg.get(nid, 0)
        if n["type"] in ("entry", "fact"):
            n["weight"] = max(n.get("weight", 1), 1)
        elif n["type"] == "project":
            s = sum(g.nodes[o].get("weight", 0) for o in adj.get(nid, [])
                    if g.nodes.get(o, {}).get("type") in ("entry", "fact"))
            n["weight"] = max(s, 1)
        elif n["type"] == "liveagent":
            n["weight"] = 7           # 中等；红光靠渲染突出，不靠体量
        else:
            n["weight"] = max(deg.get(nid, 0), 1)
            # 实体（数据集/模型/技术…）的主要关联项目 = 引用它最多的项目
            projs = [g.nodes[o].get("project") for o in adj.get(nid, [])
                     if g.nodes.get(o, {}).get("type") == "entry" and g.nodes[o].get("project")]
            if projs:
                n["primary"] = collections.Counter(projs).most_common(1)[0][0]
    return g

def merge_fragment(g, path):
    """把另一台机器提交的 fragment（graph json）合并进 g：节点按 id 去重合并、边去重。"""
    try:
        frag = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"  ! 读不了 fragment {path}: {e}", file=sys.stderr); return 0
    if not isinstance(frag, dict):     # 合法 JSON 但非对象(数组/字符串等) → 跳过，别让 .get 崩掉整个合并
        print(f"  ! fragment 非对象，跳过: {path}", file=sys.stderr); return 0
    for n in frag.get("nodes", []):
        attrs = {k: v for k, v in n.items() if k not in ("id", "type", "label", "degree")}
        g.node(n["id"], n["type"], n.get("label", ""), **attrs)
    for e in frag.get("edges", []):
        if e.get("type") == "references":   # 引用边以汇总端 link_projects 重算为准(带 STOP/遮蔽/derived 过滤)——碎片内嵌版本可能来自旧代码/伪项目，忽略
            continue
        g.edge(e.get("source"), e.get("target"), e.get("type"))
    for pk, txt in (frag.get("proj_text") or {}).items():   # 吸收碎片携带的项目原始文本 → 供 link_projects 检测「跨机」项目引用/派生
        if isinstance(txt, str) and txt:
            PROJ_TEXT[pk] = PROJ_TEXT.get(pk, "") + txt
    return len(frag.get("nodes", []))

def load_presence(g):
    """读 presence/*.json（各 agent 报到状态）→ 注入 liveagent 节点 + working_on 边。
    新鲜度(15min)由查看器用 heartbeat 时间戳自行判定，这里只如实注入 heartbeat/status。"""
    import glob
    pdir = os.path.join(HERE, "presence")
    cnt = 0
    for fp in sorted(glob.glob(os.path.join(pdir, "*.json"))):
        try:
            p = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(p, dict):     # 合法 JSON 但非对象(如数组) → 跳过，别让 .get 崩掉整个 collect
            continue
        agent = str(p.get("agent", "?")); machine = str(p.get("machine", "?"))
        raw = p.get("project_canonical") or p.get("project") or ""
        ckey, clabel = resolve_canon(raw) if raw else ("", "")
        lid = f"liveagent:{machine}__{agent}"
        g.node(lid, "liveagent", f"{agent}@{machine}",
               heartbeat=p.get("heartbeat"), status=p.get("status", "idle"),
               current=p.get("current", ""), project=clabel, machine=machine,
               tool=p.get("tool", "agent"))
        mid = f"machine:{machine}"; g.node(mid, "machine", machine); g.edge(lid, mid, "located")
        if ckey:
            pid = f"project:{ckey}"; g.node(pid, "project", clabel); g.edge(lid, pid, "working_on")
        cnt += 1
    if cnt:
        print(f"  [presence] 注入 {cnt} 个 agent 报到状态", file=sys.stderr)
    return cnt

SANITIZE_DROP = ("excerpt", "source", "paths", "description", "origin", "current")
_IP = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')

def _scrub(s):
    if not isinstance(s, str):
        return s
    s = _IP.sub('‹ip›', s)
    s = re.sub(r'/(?:home|data|root|mnt|opt)/[\w./~+\-]+', '‹path›', s)
    return s

def sanitize_public(out):
    """公开版：去正文/路径/来源，匿名化 server 节点与残留 IP/路径串；保留结构、名称、日期、连线。"""
    srv = [n["id"] for n in out["nodes"] if n["type"] == "server"]
    idmap = {sid: f"server:{chr(65 + i)}" for i, sid in enumerate(srv)}
    mid = lambda x: idmap.get(x, x)
    nodes = []
    for n in out["nodes"]:
        m = {k: v for k, v in n.items() if k not in SANITIZE_DROP}
        m["id"] = mid(n["id"])
        if n["type"] == "server":
            m["label"] = "server-" + idmap[n["id"]].split(":")[1]
        else:
            m["label"] = _scrub(m.get("label", ""))
        nodes.append(m)
    edges = [{"source": mid(e["source"]), "target": mid(e["target"]), "type": e["type"]}
             for e in out["edges"]]
    return {"meta": {**out["meta"], "sanitized": True}, "nodes": nodes, "edges": edges}

def _link_shadowed(ta, i, bsq, pool):
    """最长匹配遮蔽：ta 中位置 i 命中了名字 bsq；若该命中向前/向后各看一个字符就能延续拼进
    另一个【更长的项目名】片段(如 'proj' 后跟 '2' → 'proj2…' 属 proj2 项目/模型)，
    则该命中归属长名(或其提及)，不算 bsq 的引用。防止短名(proj)劫持长名(proj2)的所有提及。"""
    j = i + len(bsq)
    for L in pool:
        if len(L) <= len(bsq) or bsq not in L:
            continue
        k = -1
        while True:
            k = L.find(bsq, k + 1)
            if k == -1:
                break
            need_pre, need_post = k > 0, k + len(bsq) < len(L)
            ok_pre = (not need_pre) or (i > 0 and ta[i - 1] == L[k - 1])
            ok_post = (not need_post) or (j < len(ta) and ta[j] == L[k + len(bsq)])
            if ok_pre and ok_post and (need_pre or need_post):
                return True
    return False

def link_projects(g):
    """检测项目间引用/派生：若项目 A 的记忆文本里出现项目 B 的(distinctive)名字 → 加 A→B 'references' 边。
    用 squash 归一化匹配(消除 -/_ 差异)；只在有原始文本的本次解析范围内检测(贡献端解析原始文件时嵌入 fragment)。
    防误伤：①纯 derived(自动提炼、无人工记忆)项目不作为被引用目标——目录名常是通用词(如 model=某模型名)；
    ②最长匹配遮蔽——命中若能延续成另一个更长项目名片段(proj+2→proj2…)则判归长名，见 _link_shadowed。"""
    # 排除 meta/环境/顶层项目(非研究项目,不参与"派生/引用"关系)——按 project key 排除
    # STOP_KEYS 为模块级(见文件上方；可由 projects.json 的 "stop_keys" 扩展)
    projs = {nid: n["label"] for nid, n in g.nodes.items() if n["type"] == "project"}
    def pkey_of(nid): return nid.split(":", 1)[1]
    # 家目录/容器级伪项目(如 data-users-<user>、home-<user>-Project)按 label 模式排除
    def is_env(nid): return bool(AUTO_ENV_RE.match((projs.get(nid) or '').lower()))
    # ① 只有拥有人工(非 derived)entry/fact 成员的项目才可作为被引用目标
    manual_target = set()
    for e in g.edges.values():
        if e["type"] == "in" and str(e["target"]).startswith("project:"):
            s = g.nodes.get(e["source"])
            if s and s["type"] in ("entry", "fact") and not s.get("derived"):
                manual_target.add(e["target"])
    names = {}   # nid -> distinctive squash 名(作为被引用目标)
    for nid, lab in projs.items():
        sq = squash(lab)
        if len(sq) >= 6 and pkey_of(nid) not in STOP_KEYS and nid in manual_target and not is_env(nid):
            names[nid] = sq
    # 遮蔽池：所有 ≥6 字符的项目名(含 STOP/derived)——判定"命中是否其实属于某个更长的名字"
    shadow_pool = [squash(lab) for lab in projs.values() if len(squash(lab)) >= 6]
    sqtext = {}  # nid -> squash(该项目全文)(作为引用来源)
    for nid in projs:
        if pkey_of(nid) in STOP_KEYS or is_env(nid):
            continue
        t = PROJ_TEXT.get(pkey_of(nid), "")
        if t:
            sqtext[nid] = squash(t)
    def hit(ta, bsq):   # 存在至少一次"未被长名遮蔽"的命中才算引用
        i = ta.find(bsq)
        while i != -1:
            if not _link_shadowed(ta, i, bsq, shadow_pool):
                return True
            i = ta.find(bsq, i + 1)
        return False
    cnt = 0
    for a, ta in sqtext.items():
        for b, bsq in names.items():
            if a != b and bsq in ta and hit(ta, bsq):
                g.edge(a, b, "references"); cnt += 1
    if cnt:
        print(f"  [link] 检测到 {cnt} 条项目间引用", file=sys.stderr)
    return cnt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "sources.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "graph.json"))
    ap.add_argument("--pull", action="store_true", help="同时 ssh 拉取远程源")
    ap.add_argument("--local-only", action="store_true", help="只扫本地源、跳过 ssh（贡献端用）")
    ap.add_argument("--merge", action="store_true", help="合并 fragments/*.json（汇总端用）")
    ap.add_argument("--roots", default="", help="逗号分隔的本地根目录，覆盖 sources.json（贡献端用）")
    ap.add_argument("--machine", default="local", help="本机标识名（配合 --roots）")
    ap.add_argument("--tool", default="claude", help="产出工具标记: claude/codex/human（配合 --roots）")
    args = ap.parse_args()

    load_projects()
    cfg = json.load(open(args.config, encoding="utf-8"))
    g = Graph()
    stats = {"manual_files": 0, "auto_files": 0, "entries": 0, "facts": 0}

    if args.roots:        # 贡献端：用命令行根目录，忽略 sources.json 的源
        sources = [{"machine": args.machine, "type": "local", "tool": args.tool,
                    "roots": [r for r in args.roots.split(",") if r], "enabled": True}]
    else:
        sources = cfg["sources"]
    for src in sources:
        if args.local_only and src["type"] == "ssh":
            continue
        if not src.get("enabled"):     # disabled=总是跳过（含 --pull；改推送模型的 server 在此关闭 ssh 拉取避免与其 fragment 重复）
            continue
        machine = src["machine"]
        tool = src.get("tool") or args.tool
        print(f"[源] {machine} ({src['type']}) tool={tool}", file=sys.stderr)
        if src["type"] == "local":
            for root in src["roots"]:
                root = os.path.expanduser(root)
                if not os.path.isdir(root):
                    print(f"  ! 根目录不存在: {root}", file=sys.stderr); continue
                for path, kind, slug in discover_local(root, cfg, src.get("max_depth")):
                    if kind == "manual":
                        n = parse_manual(g, path, machine, tool)
                        stats["manual_files"] += 1; stats["entries"] += n
                    elif kind == "auto":
                        n = parse_auto(g, path, slug, machine)
                        stats["auto_files"] += 1; stats["facts"] += n
                    # kind == "memindex"：事实节点在 parse_auto 已连到项目，无需再处理
        elif src["type"] == "ssh":
            cache_dir = os.path.join(HERE, "sources_cache", machine)
            dsts = []
            if args.pull:
                dsts = [dst for dst, _ in pull_ssh(src, os.path.join(HERE, "sources_cache"))]
            elif os.path.isdir(cache_dir):
                dsts = [os.path.join(cache_dir, f) for f in sorted(os.listdir(cache_dir)) if f.endswith(".md")]
                print(f"  · {machine}: 用缓存 {len(dsts)} 个文件（未 --pull）", file=sys.stderr)
            for dst in dsts:
                # 远程按手工格式解析（server 上都是 agent_memory.md）
                n = parse_manual(g, dst, machine, tool)
                stats["manual_files"] += 1; stats["entries"] += n

    if args.merge:           # 汇总端：合并其他电脑提交的 fragments/*.json
        import glob
        for fp in sorted(glob.glob(os.path.join(HERE, "fragments", "*.json"))):
            print(f"  [merge] {os.path.basename(fp)}: +{merge_fragment(g, fp)} 节点", file=sys.stderr)

    if not args.roots:       # 汇总端读 presence/（贡献端 --roots 模式不注入，避免碎片里带 liveagent）
        load_presence(g)

    link_projects(g)         # 项目间引用/派生边（每次都跑；贡献端会把边嵌入 fragment）
    finalize(g)
    type_counts = {}
    for n in g.nodes.values():
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    out = {
        "meta": {
            "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats,
            "node_count": len(g.nodes),
            "edge_count": len(g.edges),
            "type_counts": type_counts,
            "machines": sorted({n["label"] for n in g.nodes.values() if n["type"] == "machine"}),
            "projects": sorted({n["label"] for n in g.nodes.values() if n["type"] == "project"}),
        },
        "nodes": list(g.nodes.values()),
        "edges": list(g.edges.values()),
    }
    if args.roots:   # 仅贡献端：把本机项目原始文本随 fragment 一并写出，供汇总端检测「跨机」项目引用（汇总端不写，graph.json/密文不含全文、保持精简）
        out["proj_text"] = {k: v[:200000] for k, v in PROJ_TEXT.items() if v}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out["meta"], ensure_ascii=False, indent=2))
    print(f"\n✓ 写出 {args.out}(完整, 仅本地)。公开 Pages 请跑 encrypt.py 生成 docs/graph.enc.json(加密)。",
          file=sys.stderr)
    # 注：sanitize_public() 仍保留，供"不加密、改用脱敏公开"的备选方案；当前默认走加密。

if __name__ == "__main__":
    main()
