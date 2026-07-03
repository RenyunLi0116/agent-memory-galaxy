#!/usr/bin/env python3
"""Build the fully synthetic public demo graph and demo viewer."""
from __future__ import annotations

import json
import os
import random
import re
import shutil
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "docs", "demo")
VIEWER = os.path.join(ROOT, "viewer", "index.html")

FORBIDDEN_PATTERNS = [
    r"[A-Z]:\\",
    r"/Users/",
    r"\\Users\\",
    re.escape("Cyber" + "Origin2077"),
    re.escape("Cyber" + "Memory"),
    re.escape("agent-memory-" + "graph"),
    r"github_pat_",
    r"ghp_",
    r"sk-",
    r"BEGIN (RSA |OPENSSH |DSA |EC |)?PRIVATE KEY",
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


def pick(items, offset: int, count: int):
    return [items[(offset + i) % len(items)] for i in range(count)]


def add_unique_edge(edges, seen, source: str, target: str, typ: str):
    key = (source, target, typ)
    if source != target and key not in seen:
        edges.append(edge(source, target, typ))
        seen.add(key)


def build_graph():
    rng = random.Random(2077)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    nodes = []
    edges = []
    seen_edges = set()

    machines = [
        ("demo-workstation-a", "primary capture + local viewer"),
        ("demo-laptop-b", "writing + evaluation notes"),
        ("demo-gpu-node-c", "training + scheduled runs"),
        ("demo-ci-runner-d", "nightly validation"),
        ("demo-mac-studio-e", "design review + docs"),
    ]
    agents = [
        ("codex", "implementation"),
        ("claude", "research synthesis"),
        ("cursor", "editor sessions"),
        ("human", "manual notes"),
        ("automator", "scheduled jobs"),
    ]
    projects = [
        ("Project Aurora Loom", ["demo-workstation-a", "demo-gpu-node-c"], "memory graph viewer and demo data"),
        ("Project Harbor Lens", ["demo-laptop-b", "demo-mac-studio-e"], "evaluation notes and visual inspection"),
        ("Project Meridian Sync", ["demo-gpu-node-c", "demo-ci-runner-d"], "multi-machine fragment merge"),
        ("Project Atlas Relay", ["demo-workstation-a", "demo-ci-runner-d"], "encrypted publishing pipeline"),
        ("Project Solstice Bench", ["demo-gpu-node-c", "demo-laptop-b"], "toy benchmark tracking"),
        ("Project Prism Cache", ["demo-mac-studio-e", "demo-workstation-a"], "session metadata distillation"),
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
        "train_pipeline.py",
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
    wandb_runs = [
        "demo-run-aurora-001",
        "demo-run-harbor-014",
        "demo-run-meridian-009",
        "demo-run-atlas-022",
        "demo-run-solstice-031",
    ]
    methods = [
        "shared-entity linking",
        "derived gap filling",
        "client-side decrypt",
        "live presence pulse",
        "timeline filtering",
        "synthetic graph rehearsal",
        "privacy redaction pass",
    ]
    tech = [
        "Canvas 3D",
        "AES-GCM",
        "PBKDF2",
        "SQLite",
        "GitHub Pages",
        "Claude Code Plugin",
        "Codex Skill",
        "Graph JSON",
    ]
    notion_pages = [
        "Weekly Progress",
        "Release Notes",
        "Experiment Ledger",
        "Deployment Runbook",
    ]
    servers = [
        "demo-server-a",
        "demo-server-b",
        "demo-runner-c",
        "demo-vault-d",
    ]

    for machine, primary in machines:
        nodes.append(node(f"machine:{machine}", "machine", machine, primary=primary, weight=22))
    for agent_name, role in agents:
        nodes.append(node(f"agent:{agent_name}", "agent", agent_name, tool=agent_name, role=role, weight=20))
    for label, machine_labels, summary in projects:
        nodes.append(
            node(
                f"project:{slug(label)}",
                "project",
                label,
                machines=machine_labels,
                description=summary,
                weight=82 + len(machine_labels) * 4,
            )
        )
        for machine in machine_labels:
            add_unique_edge(edges, seen_edges, f"project:{slug(label)}", f"machine:{machine}", "on")

    typed_assets = [
        ("dataset", datasets, 34),
        ("model", models, 32),
        ("file", files, 24),
        ("wandb", wandb_runs, 20),
        ("method", methods, 22),
        ("tech", tech, 24),
        ("notion", notion_pages, 20),
        ("server", servers, 22),
    ]
    for typ, labels, base_weight in typed_assets:
        for label in labels:
            nodes.append(node(f"{typ}:{slug(label)}", typ, label, weight=base_weight + rng.randint(0, 14)))

    task_cycle = ["鏁版嵁", "璁粌", "璇勬祴", "閮ㄧ讲", "璋冪爺", "鍚屾", "瑙勫垝", "鍏朵粬"]
    status_cycle = ["done", "logged", "doing", "planned"]
    verbs = [
        "Linked",
        "Reviewed",
        "Distilled",
        "Validated",
        "Merged",
        "Benchmarked",
        "Published",
        "Mapped",
    ]
    objects = [
        "synthetic fragments",
        "viewer controls",
        "agent session metadata",
        "encrypted publish path",
        "multi-machine handoff",
        "demo graph labels",
        "privacy scan output",
        "timeline filters",
    ]

    for pidx, (project_label, project_machines, _) in enumerate(projects):
        project_id = f"project:{slug(project_label)}"
        project_assets = {
            "dataset": pick([f"dataset:{slug(x)}" for x in datasets], pidx, 2),
            "model": pick([f"model:{slug(x)}" for x in models], pidx, 1),
            "file": pick([f"file:{slug(x)}" for x in files], pidx * 2, 3),
            "wandb": pick([f"wandb:{slug(x)}" for x in wandb_runs], pidx, 1),
            "method": pick([f"method:{slug(x)}" for x in methods], pidx, 2),
            "tech": pick([f"tech:{slug(x)}" for x in tech], pidx, 2),
            "notion": pick([f"notion:{slug(x)}" for x in notion_pages], pidx, 1),
            "server": pick([f"server:{slug(x)}" for x in servers], pidx, 1),
        }

        for eidx in range(6):
            date = f"2026-06-{10 + pidx * 2 + eidx:02d}"
            machine = project_machines[eidx % len(project_machines)]
            agent_name = agents[(pidx + eidx) % len(agents)][0]
            task = task_cycle[(pidx + eidx) % len(task_cycle)]
            status = status_cycle[(pidx * 2 + eidx) % len(status_cycle)]
            label = f"{verbs[(pidx + eidx) % len(verbs)]} {objects[(pidx * 2 + eidx) % len(objects)]} for {project_label.replace('Project ', '')}"
            entry_id = f"entry:{slug(project_label)}:{eidx + 1:02d}"
            nodes.append(
                node(
                    entry_id,
                    "entry",
                    label,
                    date=date,
                    status=status,
                    task=task,
                    tool=agent_name,
                    machine=machine,
                    project=project_label,
                    session=f"demo://{slug(project_label)}/session-{eidx + 1:03d}",
                    excerpt=(
                        "Synthetic entry: captures a safe work-memory summary with fictional "
                        "machines, artifacts, and project names only."
                    ),
                    weight=58 + rng.randint(0, 42),
                )
            )
            add_unique_edge(edges, seen_edges, entry_id, project_id, "in")
            add_unique_edge(edges, seen_edges, entry_id, f"machine:{machine}", "located")
            add_unique_edge(edges, seen_edges, f"agent:{agent_name}", entry_id, "did")
            for target in [
                project_assets["dataset"][eidx % 2],
                project_assets["file"][eidx % 3],
                project_assets["tech"][eidx % 2],
                project_assets["method"][eidx % 2],
            ]:
                add_unique_edge(edges, seen_edges, entry_id, target, "touches" if target.startswith("file:") else "uses")
            if eidx % 2 == 0:
                add_unique_edge(edges, seen_edges, entry_id, project_assets["model"][0], "trains")
                add_unique_edge(edges, seen_edges, entry_id, project_assets["wandb"][0], "tracks")
            if eidx % 3 == 0:
                add_unique_edge(edges, seen_edges, entry_id, project_assets["notion"][0], "syncs")
                add_unique_edge(edges, seen_edges, entry_id, project_assets["server"][0], "on")

        for fidx in range(3):
            machine = project_machines[(fidx + 1) % len(project_machines)]
            tool = agents[(pidx + fidx + 1) % len(agents)][0]
            fact_id = f"fact:{slug(project_label)}:{fidx + 1:02d}"
            nodes.append(
                node(
                    fact_id,
                    "fact",
                    f"Derived memory fact {fidx + 1} for {project_label.replace('Project ', '')}",
                    date=f"2026-06-{18 + pidx + fidx:02d}",
                    status="logged",
                    task="璋冪爺",
                    tool=tool,
                    machine=machine,
                    project=project_label,
                    derived=True,
                    memtype="session-summary",
                    excerpt=(
                        "Derived from synthetic session metadata. No raw conversation, "
                        "personal path, hostname, server address, or private project appears here."
                    ),
                    source=f"demo://{slug(project_label)}/derived-{fidx + 1:03d}",
                    weight=44 + rng.randint(0, 28),
                )
            )
            add_unique_edge(edges, seen_edges, fact_id, project_id, "in")
            add_unique_edge(edges, seen_edges, fact_id, f"machine:{machine}", "located")
            add_unique_edge(edges, seen_edges, fact_id, project_assets["file"][fidx % 3], "touches")
            add_unique_edge(edges, seen_edges, fact_id, project_assets["tech"][fidx % 2], "uses")
            add_unique_edge(edges, seen_edges, fact_id, project_assets["method"][fidx % 2], "explores")

    project_ids = [f"project:{slug(p[0])}" for p in projects]
    reference_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 3), (1, 4), (2, 5)]
    for a, b in reference_pairs:
        add_unique_edge(edges, seen_edges, project_ids[a], project_ids[b], "references")

    shared_links = [
        ("model:demo-vlm-small-v0", "dataset:syntheticcity-rgbd-1k", "uses"),
        ("model:meridian-merge-probe", "dataset:toyfleet-mcap-v0", "uses"),
        ("method:client-side-decrypt", "tech:aes-gcm", "uses"),
        ("method:client-side-decrypt", "tech:pbkdf2", "uses"),
        ("tech:github-pages", "file:encrypt-publish-py", "touches"),
        ("tech:claude-code-plugin", "tech:codex-skill", "references"),
        ("tech:graph-json", "file:graph-loader-py", "touches"),
        ("notion:weekly-progress", "notion:release-notes", "references"),
    ]
    for source, target, typ in shared_links:
        add_unique_edge(edges, seen_edges, source, target, typ)

    live_agents = [
        ("codex", "demo-workstation-a", "Project Aurora Loom", "reviewing the synthetic demo graph wiring"),
        ("claude", "demo-gpu-node-c", "Project Meridian Sync", "drafting a privacy checklist for encrypted publishing"),
        ("cursor", "demo-mac-studio-e", "Project Prism Cache", "inspecting the landing-page preview modal"),
        ("automator", "demo-ci-runner-d", "Project Atlas Relay", "checking public artifact boundaries"),
    ]
    for agent_name, machine, project_label, current in live_agents:
        live_id = f"liveagent:{machine}:{agent_name}"
        nodes.append(
            node(
                live_id,
                "liveagent",
                f"{agent_name}@{machine}",
                agent=agent_name,
                machine=machine,
                project=project_label,
                project_canonical=slug(project_label),
                status="working",
                current=current,
                heartbeat=now,
                tool=agent_name,
                weight=96,
            )
        )
        add_unique_edge(edges, seen_edges, live_id, f"machine:{machine}", "located")
        add_unique_edge(edges, seen_edges, live_id, f"project:{slug(project_label)}", "working_on")
        add_unique_edge(edges, seen_edges, f"agent:{agent_name}", live_id, "did")

    for i in range(len(live_agents) - 1):
        add_unique_edge(
            edges,
            seen_edges,
            f"liveagent:{live_agents[i][1]}:{live_agents[i][0]}",
            f"liveagent:{live_agents[i + 1][1]}:{live_agents[i + 1][0]}",
            "link",
        )

    degree = {n["id"]: 0 for n in nodes}
    for e in edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1
    for n in nodes:
        n["degree"] = degree.get(n["id"], 0)

    type_counts = {}
    for n in nodes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1

    graph = {
        "meta": {
            "generated": now,
            "sanitized": True,
            "demo": True,
            "synthetic": True,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "type_counts": type_counts,
            "machines": [m[0] for m in machines],
            "projects": [p[0] for p in projects],
            "privacy_note": "All labels, sessions, machines, projects, files, datasets, models, and servers are fictional.",
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

    allowed_tasks = {"璁粌", "鏁版嵁", "璇勬祴", "閮ㄧ讲", "璋冪爺", "鍚屾", "瑙勫垝", "鍏朵粬"}
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
    print(
        f"wrote {os.path.join(DEMO, 'graph.json')} "
        f"({graph['meta']['node_count']} nodes, {graph['meta']['edge_count']} edges)"
    )


if __name__ == "__main__":
    main()
