#!/usr/bin/env python3
"""Build the deterministic, fully synthetic public demo graph and viewer."""
from __future__ import annotations

import json
import os
import random
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "docs", "demo")
VIEWER = os.path.join(ROOT, "viewer", "index.html")
GENERATED_AT = "2026-07-06T00:00:00Z"

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

    machines = [
        ("demo-workstation-a", "capture + local viewer", "Contributor"),
        ("demo-laptop-b", "writing + release review", "Contributor"),
        ("demo-gpu-node-c", "training + merge rehearsals", "Contributor"),
        ("demo-ci-runner-d", "nightly validation", "Aggregator"),
        ("demo-pages-host-e", "public Pages dry run", "Publisher"),
    ]
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
    ]
    models = [
        "demo-vlm-small-v0",
        "aurora-checkpoint-042",
        "harbor-reranker-v2",
        "meridian-merge-probe",
        "solstice-eval-head",
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

    for machine, primary, role in machines:
        nodes.append(node(f"machine:{machine}", "machine", machine, primary=primary, role=role, weight=24))
    for agent_name, role in agents:
        nodes.append(node(f"agent:{agent_name}", "agent", agent_name, tool=agent_name, role=role, weight=20))
    for label, machine_labels, phase, summary, visibility in projects:
        pid = f"project:{slug(label)}"
        nodes.append(node(pid, "project", label, machines=machine_labels, phase=phase, description=summary, visibility=visibility, weight=92))
        for machine in machine_labels:
            add_edge(edges, seen_edges, pid, f"machine:{machine}", "on")
    for label, role, summary in servers:
        nodes.append(node(f"server:{slug(label)}", "server", label, role=role, primary=summary, weight=34))
    for label in datasets:
        nodes.append(node(f"dataset:{slug(label)}", "dataset", label, weight=34 + rng.randint(0, 14)))
    for label in models:
        nodes.append(node(f"model:{slug(label)}", "model", label, weight=32 + rng.randint(0, 12)))
    for label in files:
        nodes.append(node(f"file:{slug(label)}", "file", label, weight=24 + rng.randint(0, 10)))
    for label, summary in artifacts:
        nodes.append(node(f"artifact:{slug(label)}", "artifact", label, primary=summary, weight=34))
    for label, summary in boundaries:
        nodes.append(node(f"boundary:{slug(label)}", "boundary", label, primary=summary, weight=40))
    for label in wandb_runs:
        nodes.append(node(f"wandb:{slug(label)}", "wandb", label, weight=22 + rng.randint(0, 8)))
    for label in methods:
        nodes.append(node(f"method:{slug(label)}", "method", label, weight=24 + rng.randint(0, 10)))
    for label in tech:
        nodes.append(node(f"tech:{slug(label)}", "tech", label, weight=24 + rng.randint(0, 12)))
    for label in notion_pages:
        nodes.append(node(f"notion:{slug(label)}", "notion", label, weight=22 + rng.randint(0, 8)))

    project_relations = [
        ("Project Meridian Sync", "Project Aurora Loom", "inherits_from"),
        ("Project Harbor Lens", "Project Meridian Sync", "depends_on"),
        ("Project Solstice Bench", "Project Harbor Lens", "inherits_from"),
        ("Project Prism Cache", "Project Meridian Sync", "depends_on"),
        ("Project Atlas Relay", "Project Prism Cache", "depends_on"),
        ("Project Atlas Relay", "Project Aurora Loom", "exports_to"),
        ("Project Harbor Lens", "Project Atlas Relay", "references"),
        ("Project Solstice Bench", "Project Meridian Sync", "references"),
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

    for pidx, (project_label, project_machines, phase, summary, visibility) in enumerate(projects):
        project_id = f"project:{slug(project_label)}"
        for eidx in range(6):
            date = f"2026-06-{10 + pidx * 2 + eidx:02d}"
            machine = project_machines[eidx % len(project_machines)]
            agent_name = agents[(pidx + eidx) % len(agents)][0]
            task = task_cycle[(pidx + eidx) % len(task_cycle)]
            status = status_cycle[(pidx * 2 + eidx) % len(status_cycle)]
            entry_id = f"entry:{slug(project_label)}:{eidx + 1:02d}"
            label = f"{verbs[(pidx + eidx) % len(verbs)]} {objects[(pidx * 2 + eidx) % len(objects)]} for {project_label.replace('Project ', '')}"
            nodes.append(node(
                entry_id,
                "entry",
                label,
                date=date,
                status=status,
                task=task,
                tool=agent_name,
                machine=machine,
                project=project_label,
                phase=phase,
                visibility=visibility,
                session=f"demo://{slug(project_label)}/session-{eidx + 1:03d}",
                excerpt="Synthetic entry: a fictional work-memory summary with fake machines, assets, and release checks only.",
                weight=58 + rng.randint(0, 42),
            ))
            add_edge(edges, seen_edges, entry_id, project_id, "in")
            add_edge(edges, seen_edges, entry_id, f"machine:{machine}", "located")
            add_edge(edges, seen_edges, f"agent:{agent_name}", entry_id, "did")
            add_edge(edges, seen_edges, entry_id, dataset_ids[(pidx + eidx) % len(dataset_ids)], "uses")
            add_edge(edges, seen_edges, entry_id, file_ids[(pidx * 2 + eidx) % len(file_ids)], "touches")
            add_edge(edges, seen_edges, entry_id, tech_ids[(pidx + eidx) % len(tech_ids)], "uses")
            add_edge(edges, seen_edges, entry_id, method_ids[(pidx + eidx) % len(method_ids)], "uses")
            if eidx % 2 == 0:
                add_edge(edges, seen_edges, entry_id, model_ids[(pidx + eidx) % len(model_ids)], "trains")
                add_edge(edges, seen_edges, entry_id, wandb_ids[(pidx + eidx) % len(wandb_ids)], "tracks")
            if eidx % 3 == 0:
                add_edge(edges, seen_edges, entry_id, notion_ids[(pidx + eidx) % len(notion_ids)], "syncs")
                add_edge(edges, seen_edges, entry_id, server_ids[(pidx + eidx) % len(server_ids)], "on")

        for fidx in range(3):
            fact_id = f"fact:{slug(project_label)}:{fidx + 1:02d}"
            machine = project_machines[(fidx + 1) % len(project_machines)]
            tool = agents[(pidx + fidx + 1) % len(agents)][0]
            nodes.append(node(
                fact_id,
                "fact",
                f"Derived synthetic fact {fidx + 1} for {project_label.replace('Project ', '')}",
                date=f"2026-06-{18 + pidx + fidx:02d}",
                status="logged",
                task="调研",
                tool=tool,
                machine=machine,
                project=project_label,
                derived=True,
                memtype="session-summary",
                excerpt="Derived from fictional session metadata. No confidential conversation, personal path, hostname, address, or real work label appears here.",
                source=f"demo://{slug(project_label)}/derived-{fidx + 1:03d}",
                weight=44 + rng.randint(0, 28),
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
            agent=agent_name,
            machine=machine,
            project=project_label,
            project_canonical=slug(project_label),
            status="working",
            current=current,
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
            "privacy_note": "All labels, sessions, machines, projects, files, datasets, models, servers, and live work states are fictional.",
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

    required_types = {"machine", "agent", "project", "entry", "fact", "liveagent", "server", "boundary", "artifact"}
    missing_types = required_types - {n["type"] for n in graph["nodes"]}
    if missing_types:
        raise ValueError(f"demo graph missing node types: {sorted(missing_types)}")

    required_edges = {"depends_on", "inherits_from", "encrypts", "redacts", "keeps_private", "shared_on", "working_on", "handoff_to", "publishes_to"}
    present_edges = {e["type"] for e in graph["edges"]}
    missing_edges = required_edges - present_edges
    if missing_edges:
        raise ValueError(f"demo graph missing edge types: {sorted(missing_edges)}")

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
