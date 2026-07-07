#!/usr/bin/env python3
"""Build the deterministic, fully synthetic public demo graph and viewer."""
from __future__ import annotations

import json
import os
import random
import re
import shutil
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "docs", "demo")
VIEWER = os.path.join(ROOT, "viewer", "index.html")
GENERATED_AT = "2026-07-06T00:00:00Z"
GEN_DATE = datetime.strptime(GENERATED_AT[:10], "%Y-%m-%d")


def day_offset(days_back: int) -> str:
    """Date string N days before GENERATED_AT, so demo activity stays fresh."""
    return (GEN_DATE - timedelta(days=days_back)).strftime("%Y-%m-%d")

FORBIDDEN_PATTERNS = [
    r"[A-Z]:\\",
    r"/Users/",
    r"\\Users\\",
    r"github_pat_",
    r"ghp_",
    r"sk-",
    r"BEGIN (RSA |OPENSSH |DSA |EC |)?PRIVATE KEY",
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    r"raw conversation",
    r"private project",
]




PROJECT_ZH = {
    "Project Aurora Loom": "极光织机项目",
    "Project Meridian Sync": "经线同步项目",
    "Project Harbor Lens": "港湾透镜项目",
    "Project Solstice Bench": "至日评测项目",
    "Project Prism Cache": "棱镜缓存项目",
    "Project Atlas Relay": "阿特拉斯中继项目",
}
PROJECT_SUMMARY_ZH = {
    "Memory graph schema and Galaxy Viewer": "记忆图谱 schema 与 Galaxy Viewer",
    "Multi-machine fragment merge and shared entity linking": "多机器 fragment 合并与共享实体链接",
    "Human and agent review of graph clarity": "人类与 agent 共同审阅图谱清晰度",
    "Toy benchmark using shared datasets and models": "使用共享数据集和模型的玩具评测",
    "Safe session metadata distillation": "安全会话元数据提炼",
    "Encrypted Pages publishing and public demo split": "加密 Pages 发布与公开 demo 分离",
}
MACHINE_ZH = {
    "demo-workstation-a": "演示工作站 A",
    "demo-laptop-b": "演示笔记本 B",
    "demo-gpu-node-c": "演示 GPU 节点 C",
    "demo-ci-runner-d": "演示 CI Runner D",
    "demo-pages-host-e": "演示 Pages 主机 E",
}
# 虚构团队成员（user = 推送者身份，全部虚构短 handle，与任何真实人名无关；改名须通过 FORBIDDEN_PATTERNS 校验）
TEAM_MEMBERS = {
    "ada": {"display": "Ada", "color": "#7dd3fc"},
    "kael": {"display": "Kael", "color": "#f0abfc"},
    "mira": {"display": "Mira", "color": "#fde68a"},
}
TEAM_META = {"team": "demo-orbit", "default_user": "unassigned", "members": TEAM_MEMBERS}
MACHINE_PRIMARY_ZH = {
    "capture + local viewer": "采集 + 本地 viewer",
    "writing + release review": "写作 + 发布审阅",
    "training + merge rehearsals": "训练 + 合并演练",
    "nightly validation": "夜间验证",
    "public Pages dry run": "公开 Pages 预演",
}
ROLE_ZH = {"Contributor": "贡献机器", "Aggregator": "聚合机器", "Publisher": "发布机器"}
SERVER_ZH = {
    "demo-capture-server": "演示采集服务器",
    "demo-merge-runner": "演示合并 Runner",
    "demo-ci-validator": "演示 CI 验证器",
    "demo-vault": "演示私有保险库",
    "demo-pages-edge": "演示 Pages 边缘节点",
}
SERVER_SUMMARY_ZH = {
    "collects workstation and laptop fragments": "采集工作站与笔记本 fragment",
    "normalizes fragments into graph.json": "将 fragment 归一化为 graph.json",
    "runs privacy and demo integrity checks": "运行隐私与 demo 完整性检查",
    "keeps plaintext graph and passwords private": "保管明文图谱与密码",
    "serves the public landing and synthetic demo": "服务公开宣传页与合成 demo",
}
ARTIFACT_ZH = {
    "local plaintext graph": "本地明文图谱",
    "standalone local viewer": "本地单文件 viewer",
    "encrypted pages graph": "加密 Pages 图谱",
    "public synthetic demo graph": "公开合成 demo 图谱",
    "privacy redaction report": "隐私脱敏报告",
    "plugin marketplace package": "插件市场包",
}
ARTIFACT_SUMMARY_ZH = {
    "private artifact, gitignored": "私有产物，已 gitignore",
    "private single-file viewer, gitignored": "私有单文件 viewer，已 gitignore",
    "ciphertext artifact for optional private Pages viewer": "可选私有 Pages viewer 的密文产物",
    "publishable fictional graph": "可发布的虚构图谱",
    "CI evidence for public boundary": "公开边界的 CI 证据",
    "installable skill wrapper": "可安装的 skill 包装层",
}
BOUNDARY_ZH = {
    "Public Framework": "公开框架",
    "Private Memory Hub": "私有记忆 Hub",
    "Encrypted Viewer Zone": "加密 Viewer 区",
    "Synthetic Demo Zone": "合成 Demo 区",
}
BOUNDARY_SUMMARY_ZH = {
    "code, docs, skill package, synthetic demo": "代码、文档、skill 包与合成 demo",
    "real fragments, presence, plaintext graph": "真实 fragment、presence 与明文图谱",
    "viewer shell plus ciphertext only": "仅 viewer shell 与密文",
    "fictional graph for marketing and testing": "用于宣传和测试的虚构图谱",
}
METHOD_ZH = {
    "shared-entity linking": "共享实体链接",
    "derived gap filling": "自动提炼补全",
    "client-side decrypt": "客户端解密",
    "live presence pulse": "在线状态脉冲",
    "timeline filtering": "时间轴过滤",
    "synthetic graph rehearsal": "合成图谱演练",
    "privacy redaction pass": "隐私脱敏流程",
}
NOTION_ZH = {
    "Weekly Progress": "每周进展",
    "Release Notes": "发布说明",
    "Experiment Ledger": "实验台账",
    "Deployment Runbook": "部署 Runbook",
}
VERB_ZH = {
    "Linked": "链接", "Reviewed": "审阅", "Distilled": "提炼", "Validated": "验证",
    "Merged": "合并", "Benchmarked": "评测", "Published": "发布", "Mapped": "映射",
}
OBJECT_ZH = {
    "synthetic fragments": "合成 fragments",
    "viewer controls": "viewer 控件",
    "safe session metadata": "安全会话元数据",
    "encrypted publish path": "加密发布路径",
    "multi-server handoff": "多服务器交接",
    "demo graph labels": "demo 图谱标签",
    "privacy scan output": "隐私扫描输出",
    "timeline filters": "时间轴过滤器",
}
LIVE_CURRENT_ZH = {
    "wiring project inheritance edges into the demo graph": "正在把项目继承边接入 demo 图谱",
    "checking encrypted Pages boundary language": "正在检查加密 Pages 边界文案",
    "reviewing the public landing preview": "正在审阅公开宣传页预览",
    "running synthetic graph integrity checks": "正在运行合成图谱完整性检查",
    "approving the release story": "正在批准发布叙事",
}
AGENT_ROLE_ZH = {
    "implementation": "实现",
    "research synthesis": "研究综合",
    "editor sessions": "编辑器会话",
    "release review": "发布审阅",
    "scheduled jobs": "定时任务",
}


def bi(en: str, zh: str) -> dict:
    return {"en": en, "zh": zh}
def slug(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def node(node_id: str, typ: str, label: str, **extra):
    d = {"id": node_id, "type": typ, "label": label}
    d.update(extra)
    return d


def edge(source: str, target: str, typ: str):
    return {"source": source, "target": target, "type": typ}


def add_edge(edges, seen, source: str, target: str, typ: str):
    key = (source, target, typ)
    if source != target and key not in seen:
        edges.append(edge(source, target, typ))
        seen.add(key)


def build_graph():
    rng = random.Random(4077)
    nodes = []
    edges = []
    seen_edges = set()

    # 第 4 元素 = 机器归属的虚构 user（推送者身份）：5 台机器分属 3 人
    machines = [
        ("demo-workstation-a", "capture + local viewer", "Contributor", "ada"),
        ("demo-laptop-b", "writing + release review", "Contributor", "ada"),
        ("demo-gpu-node-c", "training + merge rehearsals", "Contributor", "kael"),
        ("demo-ci-runner-d", "nightly validation", "Aggregator", "mira"),
        ("demo-pages-host-e", "public Pages dry run", "Publisher", "mira"),
    ]
    machine_owner = {m[0]: m[3] for m in machines}
    agents = [
        ("codex", "implementation"),
        ("claude", "research synthesis"),
        ("cursor", "editor sessions"),
        ("human", "release review"),
        ("automator", "scheduled jobs"),
    ]
    servers = [
        ("demo-capture-server", "capture", "collects workstation and laptop fragments"),
        ("demo-merge-runner", "merge", "normalizes fragments into graph.json"),
        ("demo-ci-validator", "ci", "runs privacy and demo integrity checks"),
        ("demo-vault", "vault", "keeps plaintext graph and passwords private"),
        ("demo-pages-edge", "public-host", "serves the public landing and synthetic demo"),
    ]
    projects = [
        ("Project Aurora Loom", ["demo-workstation-a", "demo-gpu-node-c"], "01 schema/viewer", "Memory graph schema and Galaxy Viewer", "public-safe"),
        ("Project Meridian Sync", ["demo-gpu-node-c", "demo-ci-runner-d"], "02 merge", "Multi-machine fragment merge and shared entity linking", "private-hub"),
        ("Project Harbor Lens", ["demo-laptop-b", "demo-pages-host-e"], "03 review", "Human and agent review of graph clarity", "public-safe"),
        ("Project Solstice Bench", ["demo-gpu-node-c", "demo-laptop-b"], "04 benchmark", "Toy benchmark using shared datasets and models", "public-safe"),
        ("Project Prism Cache", ["demo-pages-host-e", "demo-workstation-a"], "05 distill", "Safe session metadata distillation", "private-hub"),
        ("Project Atlas Relay", ["demo-ci-runner-d", "demo-pages-host-e"], "06 publish", "Encrypted Pages publishing and public demo split", "public-boundary"),
    ]
    datasets = [
        "SyntheticCity-RGBD-1K",
        "ToyFleet-MCAP-v0",
        "OpenKitchen-Sim-240",
        "RiverWalk-MockLogs",
        "LabBench-Events-128",
        "MiniDepot-Trajectories",
        "HarborScan-Synth-512",
        "AtlasRelay-Frames-64",
        "PrismTrace-Tokens-2M",
        "MeridianGrid-Tiles-96",
        "AuroraLoom-Sketches-300",
        "SolsticePose-Clips-77",
    ]
    models = [
        "demo-vlm-small-v0",
        "aurora-checkpoint-042",
        "harbor-reranker-v2",
        "meridian-merge-probe",
        "solstice-eval-head",
        "prism-distill-encoder",
        "atlas-relay-router-v1",
        "loom-layout-gan-008",
        "bench-scorer-tiny",
        "cache-probe-v3",
    ]
    files = [
        "collector_config_example.json",
        "dataset_manifest.json",
        "eval_report.ipynb",
        "viewer_embed.html",
        "graph_loader.py",
        "privacy_checklist.md",
        "fragment_merge_tests.py",
        "presence_heartbeat.py",
        "demo_storyboard.md",
        "notion_export.py",
        "encrypt_publish.py",
        "session_distiller.py",
    ]
    # 扩展合成文件面：stem × kind 组合出“尘埃层”小文件（全部虚构命名）
    file_stems = [
        "collector", "merge", "viewer", "timeline", "presence", "fragment",
        "schema", "redaction", "manifest", "snapshot", "heartbeat", "publish",
        "distill", "galaxy", "legend", "palette", "orbit", "nebula", "beacon",
        "lattice", "relay", "prism", "harbor", "atlas",
    ]
    file_kinds = [
        ("config", "json"), ("report", "md"), ("notes", "md"), ("pipeline", "py"),
        ("checks", "py"), ("probe", "py"), ("layout", "html"), ("story", "md"),
        ("index", "json"), ("metrics", "csv"),
    ]
    extra_files = [f"{stem}_{kind}.{ext}" for stem in file_stems for kind, ext in file_kinds]
    files = files + extra_files[: 138 - len(files)]
    artifacts = [
        ("local plaintext graph", "private artifact, gitignored"),
        ("standalone local viewer", "private single-file viewer, gitignored"),
        ("encrypted pages graph", "ciphertext artifact for optional private Pages viewer"),
        ("public synthetic demo graph", "publishable fictional graph"),
        ("privacy redaction report", "CI evidence for public boundary"),
        ("plugin marketplace package", "installable skill wrapper"),
    ]
    boundaries = [
        ("Public Framework", "code, docs, skill package, synthetic demo"),
        ("Private Memory Hub", "real fragments, presence, plaintext graph"),
        ("Encrypted Viewer Zone", "viewer shell plus ciphertext only"),
        ("Synthetic Demo Zone", "fictional graph for marketing and testing"),
    ]
    wandb_runs = ["demo-run-aurora-001", "demo-run-harbor-014", "demo-run-meridian-009", "demo-run-atlas-022", "demo-run-solstice-031"]
    methods = ["shared-entity linking", "derived gap filling", "client-side decrypt", "live presence pulse", "timeline filtering", "synthetic graph rehearsal", "privacy redaction pass"]
    tech = ["Canvas 3D", "AES-GCM", "PBKDF2", "Git", "GitHub Pages", "Claude Code Plugin", "Codex Skill", "Graph JSON"]
    notion_pages = ["Weekly Progress", "Release Notes", "Experiment Ledger", "Deployment Runbook"]

    # 长尾 weight：对标私有图实测分布(min 1/中位 9/p90 2670/max 128956)，
    # 经 viewer radiusOf=2.4+26*sqrt(w)/wmax 归一化后形成「尘埃(entry/fact/file) → 中层实体 → 枢纽(machine/server/project)」星系层级。
    project_weights = [6000, 4600, 3800, 3100, 2600, 2100]
    for machine, primary, role, owner in machines:
        nodes.append(node(f"machine:{machine}", "machine", machine, label_i18n=bi(machine, MACHINE_ZH[machine]), primary=primary, primary_i18n=bi(primary, MACHINE_PRIMARY_ZH[primary]), role=role, role_i18n=bi(role, ROLE_ZH.get(role, role)), user=owner, weight=300 + rng.randint(0, 1200)))
    # user 节点（团队成员，推送者身份）+ owns 边；常量 weight，不消费 rng（保住 Random(4077) 确定性序列）
    for handle, info in TEAM_MEMBERS.items():
        owned = [m[0] for m in machines if m[3] == handle]
        nodes.append(node(
            f"user:{handle}", "user", handle,
            display=info["display"], color=info["color"], user=handle, machines=owned,
            role="Team member (push identity)",
            role_i18n=bi("Team member (push identity)", "团队成员（推送身份）"),
            weight=430 if len(owned) > 1 else 280,
        ))
        for owned_machine in owned:
            add_edge(edges, seen_edges, f"user:{handle}", f"machine:{owned_machine}", "owns")
    for agent_name, role in agents:
        nodes.append(node(f"agent:{agent_name}", "agent", agent_name, tool=agent_name, role=role, role_i18n=bi(role, AGENT_ROLE_ZH.get(role, role)), weight=140 + rng.randint(0, 180)))
    for pidx, (label, machine_labels, phase, summary, visibility) in enumerate(projects):
        pid = f"project:{slug(label)}"
        nodes.append(node(pid, "project", label, label_i18n=bi(label, PROJECT_ZH[label]), machines=machine_labels, phase=phase, description=summary, description_i18n=bi(summary, PROJECT_SUMMARY_ZH[summary]), visibility=visibility, weight=project_weights[pidx % len(project_weights)]))
        for machine in machine_labels:
            add_edge(edges, seen_edges, pid, f"machine:{machine}", "on")
    for label, role, summary in servers:
        nodes.append(node(f"server:{slug(label)}", "server", label, label_i18n=bi(label, SERVER_ZH[label]), role=role, primary=summary, primary_i18n=bi(summary, SERVER_SUMMARY_ZH[summary]), weight=300 + rng.randint(0, 1200)))
    for label in datasets:
        nodes.append(node(f"dataset:{slug(label)}", "dataset", label, weight=50 + rng.randint(0, 350)))
    for label in models:
        nodes.append(node(f"model:{slug(label)}", "model", label, weight=50 + rng.randint(0, 350)))
    for label in files:
        nodes.append(node(f"file:{slug(label)}", "file", label, weight=1 + min(19, int(rng.expovariate(1 / 5)))))
    for label, summary in artifacts:
        nodes.append(node(f"artifact:{slug(label)}", "artifact", label, label_i18n=bi(label, ARTIFACT_ZH[label]), primary=summary, primary_i18n=bi(summary, ARTIFACT_SUMMARY_ZH[summary]), weight=40 + rng.randint(0, 80)))
    for label, summary in boundaries:
        nodes.append(node(f"boundary:{slug(label)}", "boundary", label, label_i18n=bi(label, BOUNDARY_ZH[label]), primary=summary, primary_i18n=bi(summary, BOUNDARY_SUMMARY_ZH[summary]), weight=40 + rng.randint(0, 80)))
    for label in wandb_runs:
        nodes.append(node(f"wandb:{slug(label)}", "wandb", label, weight=20 + rng.randint(0, 40)))
    for label in methods:
        nodes.append(node(f"method:{slug(label)}", "method", label, label_i18n=bi(label, METHOD_ZH[label]), weight=5 + rng.randint(0, 75)))
    for label in tech:
        nodes.append(node(f"tech:{slug(label)}", "tech", label, weight=5 + rng.randint(0, 75)))
    for label in notion_pages:
        nodes.append(node(f"notion:{slug(label)}", "notion", label, label_i18n=bi(label, NOTION_ZH[label]), weight=20 + rng.randint(0, 40)))

    project_relations = [
        ("Project Meridian Sync", "Project Aurora Loom", "inherits_from"),
        ("Project Harbor Lens", "Project Meridian Sync", "depends_on"),
        ("Project Solstice Bench", "Project Harbor Lens", "inherits_from"),
        ("Project Prism Cache", "Project Meridian Sync", "depends_on"),
        ("Project Atlas Relay", "Project Prism Cache", "depends_on"),
        ("Project Atlas Relay", "Project Aurora Loom", "exports_to"),
        ("Project Harbor Lens", "Project Atlas Relay", "references"),
        ("Project Solstice Bench", "Project Meridian Sync", "references"),
        # 金色骨架加密：references 链/星织在高 weight 项目枢纽之间（Aurora/Meridian 为双中心）
        ("Project Harbor Lens", "Project Aurora Loom", "references"),
        ("Project Prism Cache", "Project Aurora Loom", "references"),
        ("Project Solstice Bench", "Project Aurora Loom", "references"),
        ("Project Atlas Relay", "Project Meridian Sync", "references"),
        ("Project Aurora Loom", "Project Meridian Sync", "references"),
        ("Project Atlas Relay", "Project Solstice Bench", "references"),
    ]
    for a, b, typ in project_relations:
        add_edge(edges, seen_edges, f"project:{slug(a)}", f"project:{slug(b)}", typ)

    server_chain = [
        ("demo-capture-server", "demo-merge-runner", "replicates_to"),
        ("demo-merge-runner", "demo-ci-validator", "validates"),
        ("demo-ci-validator", "demo-vault", "keeps_private"),
        ("demo-vault", "demo-pages-edge", "publishes_to"),
        ("demo-pages-edge", "project-atlas-relay", "serves"),
    ]
    for source, target, typ in server_chain:
        add_edge(edges, seen_edges, f"server:{slug(source)}", (f"server:{slug(target)}" if target.startswith("demo-") else f"project:{slug(target)}"), typ)

    boundary_links = [
        ("boundary:private-memory-hub", "artifact:local-plaintext-graph", "keeps_private"),
        ("boundary:private-memory-hub", "artifact:standalone-local-viewer", "keeps_private"),
        ("artifact:local-plaintext-graph", "method:privacy-redaction-pass", "redacts"),
        ("method:privacy-redaction-pass", "artifact:privacy-redaction-report", "exports_to"),
        ("artifact:privacy-redaction-report", "server:demo-ci-validator", "validates"),
        ("method:client-side-decrypt", "artifact:encrypted-pages-graph", "encrypts"),
        ("artifact:encrypted-pages-graph", "boundary:encrypted-viewer-zone", "publishes"),
        ("artifact:public-synthetic-demo-graph", "boundary:synthetic-demo-zone", "publishes"),
        ("boundary:public-framework", "artifact:plugin-marketplace-package", "exports_to"),
        ("boundary:public-framework", "artifact:public-synthetic-demo-graph", "exposes"),
    ]
    for source, target, typ in boundary_links:
        add_edge(edges, seen_edges, source, target, typ)

    shared_asset_links = [
        ("dataset:syntheticcity-rgbd-1k", "server:demo-capture-server", "shared_on"),
        ("dataset:toyfleet-mcap-v0", "server:demo-merge-runner", "shared_on"),
        ("model:demo-vlm-small-v0", "machine:demo-gpu-node-c", "cached_on"),
        ("model:meridian-merge-probe", "server:demo-merge-runner", "cached_on"),
        ("file:fragment-merge-tests-py", "server:demo-ci-validator", "validates"),
        ("tech:github-pages", "server:demo-pages-edge", "serves"),
        ("tech:aes-gcm", "artifact:encrypted-pages-graph", "encrypts"),
        ("tech:pbkdf2", "artifact:encrypted-pages-graph", "encrypts"),
        ("tech:claude-code-plugin", "artifact:plugin-marketplace-package", "exports_to"),
        ("tech:codex-skill", "artifact:plugin-marketplace-package", "exports_to"),
    ]
    for source, target, typ in shared_asset_links:
        add_edge(edges, seen_edges, source, target, typ)

    task_cycle = ["数据", "训练", "评测", "部署", "调研", "同步", "规划", "其他"]
    status_cycle = ["done", "logged", "doing", "planned"]
    verbs = ["Linked", "Reviewed", "Distilled", "Validated", "Merged", "Benchmarked", "Published", "Mapped"]
    objects = ["synthetic fragments", "viewer controls", "safe session metadata", "encrypted publish path", "multi-server handoff", "demo graph labels", "privacy scan output", "timeline filters"]
    dataset_ids = [f"dataset:{slug(x)}" for x in datasets]
    model_ids = [f"model:{slug(x)}" for x in models]
    file_ids = [f"file:{slug(x)}" for x in files]
    method_ids = [f"method:{slug(x)}" for x in methods]
    tech_ids = [f"tech:{slug(x)}" for x in tech]
    notion_ids = [f"notion:{slug(x)}" for x in notion_pages]
    wandb_ids = [f"wandb:{slug(x)}" for x in wandb_runs]
    server_ids = [f"server:{slug(x[0])}" for x in servers]

    ENTRIES_PER_PROJECT = 28
    RECENT_PER_PROJECT = 2   # 每项目最后 2 条 entry 落在 GENERATED_AT 前 0-2 天 → 最近 3 天各 4 条，点亮绿呼吸层
    for pidx, (project_label, project_machines, phase, summary, visibility) in enumerate(projects):
        project_id = f"project:{slug(project_label)}"
        for eidx in range(ENTRIES_PER_PROJECT):
            if eidx >= ENTRIES_PER_PROJECT - RECENT_PER_PROJECT:
                days_back = (pidx * RECENT_PER_PROJECT + (eidx - (ENTRIES_PER_PROJECT - RECENT_PER_PROJECT))) % 3
            else:
                days_back = rng.randint(3, 44)   # 其余覆盖 GENERATED_AT 前约 45 天
            date = day_offset(days_back)
            machine = project_machines[eidx % len(project_machines)]
            agent_name = agents[(pidx + eidx) % len(agents)][0]
            task = task_cycle[(pidx + eidx) % len(task_cycle)]
            status = status_cycle[(pidx * 2 + eidx) % len(status_cycle)]
            entry_id = f"entry:{slug(project_label)}:{eidx + 1:02d}"
            verb = verbs[(pidx + eidx) % len(verbs)]
            obj = objects[(pidx * 2 + eidx) % len(objects)]
            label = f"{verb} {obj} for {project_label.replace('Project ', '')}"
            zh_label = f"{PROJECT_ZH[project_label]}：{VERB_ZH[verb]}{OBJECT_ZH[obj]}"
            nodes.append(node(
                entry_id,
                "entry",
                label,
                label_i18n=bi(label, zh_label),
                date=date,
                status=status,
                task=task,
                tool=agent_name,
                machine=machine,
                user=machine_owner[machine],
                project=project_label,
                project_i18n=bi(project_label, PROJECT_ZH[project_label]),
                phase=phase,
                visibility=visibility,
                session=f"demo://{slug(project_label)}/session-{eidx + 1:03d}",
                excerpt="Synthetic entry: a fictional work-memory summary with fake machines, assets, and release checks only.",
                excerpt_i18n=bi(
                    "Synthetic entry: a fictional work-memory summary with fake machines, assets, and release checks only.",
                    "合成记录：仅包含虚构机器、资产与发布检查的工作记忆摘要。",
                ),
                weight=1 + min(39, int(rng.expovariate(1 / 8))),
            ))
            add_edge(edges, seen_edges, entry_id, project_id, "in")
            add_edge(edges, seen_edges, entry_id, f"machine:{machine}", "located")
            add_edge(edges, seen_edges, f"agent:{agent_name}", entry_id, "did")
            add_edge(edges, seen_edges, entry_id, dataset_ids[(pidx + eidx) % len(dataset_ids)], "uses")
            add_edge(edges, seen_edges, entry_id, file_ids[(pidx * ENTRIES_PER_PROJECT + eidx) % len(file_ids)], "touches")
            add_edge(edges, seen_edges, entry_id, tech_ids[(pidx + eidx) % len(tech_ids)], "uses")
            add_edge(edges, seen_edges, entry_id, method_ids[(pidx + eidx) % len(method_ids)], "uses")
            if eidx % 2 == 0:
                add_edge(edges, seen_edges, entry_id, model_ids[(pidx + eidx) % len(model_ids)], "trains")
                add_edge(edges, seen_edges, entry_id, wandb_ids[(pidx + eidx) % len(wandb_ids)], "tracks")
            else:
                add_edge(edges, seen_edges, entry_id, file_ids[(pidx * ENTRIES_PER_PROJECT + eidx * 3 + 1) % len(file_ids)], "touches")
            if eidx % 3 == 0:
                add_edge(edges, seen_edges, entry_id, notion_ids[(pidx + eidx) % len(notion_ids)], "syncs")
                add_edge(edges, seen_edges, entry_id, server_ids[(pidx + eidx) % len(server_ids)], "on")

        for fidx in range(9):
            fact_id = f"fact:{slug(project_label)}:{fidx + 1:02d}"
            machine = project_machines[(fidx + 1) % len(project_machines)]
            tool = agents[(pidx + fidx + 1) % len(agents)][0]
            nodes.append(node(
                fact_id,
                "fact",
                f"Derived synthetic fact {fidx + 1} for {project_label.replace('Project ', '')}",
                label_i18n=bi(
                    f"Derived synthetic fact {fidx + 1} for {project_label.replace('Project ', '')}",
                    f"{PROJECT_ZH[project_label]}：自动提炼事实 {fidx + 1}",
                ),
                date=day_offset(rng.randint(1, 30)),
                status="logged",
                task="调研",
                tool=tool,
                machine=machine,
                user=machine_owner[machine],
                project=project_label,
                project_i18n=bi(project_label, PROJECT_ZH[project_label]),
                derived=True,
                memtype="session-summary",
                excerpt="Derived from fictional session metadata. No confidential conversation, personal path, hostname, address, or real work label appears here.",
                excerpt_i18n=bi(
                    "Derived from fictional session metadata. No confidential conversation, personal path, hostname, address, or real work label appears here.",
                    "从虚构会话元数据提炼而来；不包含机密对话、个人路径、主机名、地址或真实工作标签。",
                ),
                source=f"demo://{slug(project_label)}/derived-{fidx + 1:03d}",
                weight=1 + min(29, int(rng.expovariate(1 / 7))),
            ))
            add_edge(edges, seen_edges, fact_id, project_id, "in")
            add_edge(edges, seen_edges, fact_id, f"machine:{machine}", "located")
            add_edge(edges, seen_edges, fact_id, file_ids[(pidx + fidx) % len(file_ids)], "touches")
            add_edge(edges, seen_edges, fact_id, tech_ids[(pidx + fidx) % len(tech_ids)], "uses")
            add_edge(edges, seen_edges, fact_id, method_ids[(pidx + fidx) % len(method_ids)], "explores")

    live_agents = [
        ("codex", "demo-workstation-a", "Project Aurora Loom", "wiring project inheritance edges into the demo graph"),
        ("claude", "demo-ci-runner-d", "Project Atlas Relay", "checking encrypted Pages boundary language"),
        ("cursor", "demo-pages-host-e", "Project Harbor Lens", "reviewing the public landing preview"),
        ("automator", "demo-ci-runner-d", "Project Meridian Sync", "running synthetic graph integrity checks"),
        ("human", "demo-laptop-b", "Project Solstice Bench", "approving the release story"),
    ]
    for agent_name, machine, project_label, current in live_agents:
        live_id = f"liveagent:{machine}:{agent_name}"
        nodes.append(node(
            live_id,
            "liveagent",
            f"{agent_name}@{machine}",
            label_i18n=bi(f"{agent_name}@{machine}", f"{agent_name}@{MACHINE_ZH[machine]}"),
            agent=agent_name,
            machine=machine,
            user=machine_owner[machine],
            project=project_label,
            project_i18n=bi(project_label, PROJECT_ZH[project_label]),
            project_canonical=slug(project_label),
            status="working",
            current=current,
            current_i18n=bi(current, LIVE_CURRENT_ZH[current]),
            heartbeat=GENERATED_AT,
            demo_live=True,
            tool=agent_name,
            weight=96,
        ))
        add_edge(edges, seen_edges, live_id, f"machine:{machine}", "located")
        add_edge(edges, seen_edges, live_id, f"project:{slug(project_label)}", "working_on")
        add_edge(edges, seen_edges, f"agent:{agent_name}", live_id, "did")
    for idx in range(len(live_agents) - 1):
        a = live_agents[idx]
        b = live_agents[idx + 1]
        add_edge(edges, seen_edges, f"liveagent:{a[1]}:{a[0]}", f"liveagent:{b[1]}:{b[0]}", "handoff_to")

    degree = {n["id"]: 0 for n in nodes}
    for e in edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1
    for n in nodes:
        n["degree"] = degree.get(n["id"], 0)

    type_counts = {}
    edge_counts = {}
    for n in nodes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    for e in edges:
        edge_counts[e["type"]] = edge_counts.get(e["type"], 0) + 1

    graph = {
        "meta": {
            "generated": GENERATED_AT,
            "sanitized": True,
            "demo": True,
            "synthetic": True,
            "story": "Public Memory Graph Release Pipeline",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "type_counts": type_counts,
            "edge_counts": edge_counts,
            "machines": [m[0] for m in machines],
            "projects": [p[0] for p in projects],
            "servers": [s[0] for s in servers],
            "users": sorted(TEAM_MEMBERS),
            "team": TEAM_META,
            "privacy_note": "All labels, sessions, machines, projects, files, datasets, models, servers, team members, and live work states are fictional.",
            "privacy_note_i18n": bi(
                "All labels, sessions, machines, projects, files, datasets, models, servers, team members, and live work states are fictional.",
                "所有标签、session、机器、项目、文件、数据集、模型、服务器、团队成员和当前工作状态都是虚构的。",
            ),
            "demo_features": [
                "multi-server collaboration",
                "currently working agents",
                "project inheritance and dependencies",
                "shared datasets, models, and files",
                "private/public/encrypted boundaries",
                "skill and GitHub Pages publication path",
            ],
        },
        "nodes": nodes,
        "edges": edges,
    }
    validate_graph(graph)
    return graph


def validate_graph(graph):
    node_ids = {n["id"] for n in graph["nodes"]}
    bad_edges = [e for e in graph["edges"] if e["source"] not in node_ids or e["target"] not in node_ids]
    if bad_edges:
        raise ValueError(f"demo graph has dangling edges: {bad_edges[:3]}")

    degree = {n["id"]: 0 for n in graph["nodes"]}
    for e in graph["edges"]:
        degree[e["source"]] += 1
        degree[e["target"]] += 1
    isolated = [n for n, d in degree.items() if d == 0]
    if isolated:
        raise ValueError(f"demo graph has isolated nodes: {isolated[:5]}")

    required_types = {"machine", "agent", "project", "entry", "fact", "liveagent", "server", "boundary", "artifact", "user"}
    missing_types = required_types - {n["type"] for n in graph["nodes"]}
    if missing_types:
        raise ValueError(f"demo graph missing node types: {sorted(missing_types)}")

    required_edges = {"depends_on", "inherits_from", "encrypts", "redacts", "keeps_private", "shared_on", "working_on", "handoff_to", "publishes_to", "owns"}
    present_edges = {e["type"] for e in graph["edges"]}
    missing_edges = required_edges - present_edges
    if missing_edges:
        raise ValueError(f"demo graph missing edge types: {sorted(missing_edges)}")

    # team work 完整性：entry/fact/machine/liveagent 全带 user、user 声明齐、机器都有归属、至少 1 个跨 user 共享项目
    meta_users = set(graph["meta"].get("users") or [])
    user_carriers = [n for n in graph["nodes"] if n["type"] in ("entry", "fact", "machine", "liveagent")]
    missing_user = [n["id"] for n in user_carriers if not n.get("user")]
    if missing_user:
        raise ValueError(f"demo graph nodes missing user attribute: {missing_user[:5]}")
    undeclared = {n["user"] for n in user_carriers} - meta_users
    if undeclared:
        raise ValueError(f"demo graph node users not declared in meta.users: {sorted(undeclared)}")
    owned_machines = {e["target"] for e in graph["edges"] if e["type"] == "owns"}
    all_machines = {n["id"] for n in graph["nodes"] if n["type"] == "machine"}
    if all_machines - owned_machines:
        raise ValueError(f"demo graph machines without an owning user: {sorted(all_machines - owned_machines)}")
    project_users = {}
    for n in graph["nodes"]:
        if n["type"] == "entry":
            project_users.setdefault(n["project"], set()).add(n["user"])
    if not any(len(us) >= 2 for us in project_users.values()):
        raise ValueError("demo graph has no cross-user shared project (need entries from >=2 users on one project)")

    allowed_tasks = {"训练", "数据", "评测", "部署", "调研", "同步", "规划", "其他"}
    bad_tasks = [n for n in graph["nodes"] if n.get("task") and n["task"] not in allowed_tasks]
    if bad_tasks:
        raise ValueError(f"demo graph has unsupported task labels: {[n['task'] for n in bad_tasks[:5]]}")

    raw = json.dumps(graph, ensure_ascii=False)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, raw, flags=re.IGNORECASE):
            raise ValueError(f"demo graph contains forbidden pattern: {pattern}")


def main():
    os.makedirs(DEMO, exist_ok=True)
    shutil.copyfile(VIEWER, os.path.join(DEMO, "index.html"))
    graph = build_graph()
    with open(os.path.join(DEMO, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"wrote {os.path.join(DEMO, 'index.html')}")
    print(f"wrote {os.path.join(DEMO, 'graph.json')} ({graph['meta']['node_count']} nodes, {graph['meta']['edge_count']} edges)")


if __name__ == "__main__":
    main()
