#!/usr/bin/env python3
"""Build the fully synthetic public demo graph and demo viewer."""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(ROOT, "docs", "demo")
VIEWER = os.path.join(ROOT, "viewer", "index.html")


def node(node_id, typ, label, **extra):
    d = {"id": node_id, "type": typ, "label": label}
    d.update(extra)
    return d


def edge(source, target, typ):
    return {"source": source, "target": target, "type": typ}


def build_graph():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    nodes = [
        node("machine:demo-workstation-a", "machine", "demo-workstation-a", primary="Project Aurora Loom", weight=12),
        node("machine:demo-laptop-b", "machine", "demo-laptop-b", primary="Project Harbor Lens", weight=10),
        node("machine:demo-gpu-node-c", "machine", "demo-gpu-node-c", primary="Project Meridian Sync", weight=11),
        node("agent:codex", "agent", "codex", tool="codex", weight=14),
        node("agent:claude", "agent", "claude", tool="claude", weight=14),
        node("agent:human", "agent", "human", tool="human", weight=9),
        node("project:aurora-loom", "project", "Project Aurora Loom", machines=["demo-workstation-a", "demo-gpu-node-c"], weight=72),
        node("project:harbor-lens", "project", "Project Harbor Lens", machines=["demo-laptop-b"], weight=58),
        node("project:meridian-sync", "project", "Project Meridian Sync", machines=["demo-gpu-node-c"], weight=66),
        node("dataset:synthetic-city-rgbd-1k", "dataset", "SyntheticCity-RGBD-1K", weight=44),
        node("dataset:toyfleet-mcap-v0", "dataset", "ToyFleet-MCAP-v0", weight=34),
        node("model:demo-vlm-small-v0", "model", "demo-vlm-small-v0", weight=36),
        node("model:aurora-checkpoint-042", "model", "aurora-checkpoint-042", weight=40),
        node("file:train-pipeline", "file", "train_pipeline.py", weight=28),
        node("file:dataset-manifest", "file", "dataset_manifest.json", weight=24),
        node("file:eval-report", "file", "eval_report.ipynb", weight=25),
        node("wandb:demo-run-aurora-001", "wandb", "demo-run-aurora-001", weight=21),
        node("method:idea-1", "method", "Idea 1", weight=18),
        node("method:idea-2", "method", "Idea 2", weight=18),
        node("tech:webgpu", "tech", "WebGPU", weight=22),
        node("tech:sqlite", "tech", "SQLite", weight=19),
        node("tech:canvas-3d", "tech", "Canvas 3D", weight=24),
        node("notion:weekly-progress", "notion", "Weekly Progress", weight=18),
        node("server:demo-server-a", "server", "demo-server-a", weight=20),
        node("server:demo-server-b", "server", "demo-server-b", weight=20),
        node(
            "entry:demo-workstation-a:aurora:2026-01-14",
            "entry",
            "Wired synthetic dataset manifest into Aurora Loom",
            date="2026-01-14",
            status="done",
            task="data",
            tool="codex",
            machine="demo-workstation-a",
            project="Project Aurora Loom",
            excerpt="Created a clean manifest schema for a synthetic RGB-D dataset and linked it to evaluation notes.",
            weight=84,
        ),
        node(
            "entry:demo-laptop-b:harbor:2026-01-15",
            "entry",
            "Compared Harbor Lens outputs against Aurora references",
            date="2026-01-15",
            status="logged",
            task="evaluation",
            tool="claude",
            machine="demo-laptop-b",
            project="Project Harbor Lens",
            excerpt="Summarized evaluation differences using only fictional benchmark labels and toy artifacts.",
            weight=76,
        ),
        node(
            "entry:demo-gpu-node-c:meridian:2026-01-16",
            "entry",
            "Scheduled demo checkpoint training",
            date="2026-01-16",
            status="doing",
            task="training",
            tool="human",
            machine="demo-gpu-node-c",
            project="Project Meridian Sync",
            excerpt="Prepared a toy GPU job that writes progress into the shared memory graph.",
            weight=88,
        ),
        node(
            "fact:demo:derived:aurora:2026-01-16",
            "fact",
            "Derived session metadata linked Canvas 3D viewer work to Aurora Loom",
            date="2026-01-16",
            status="logged",
            task="derived",
            tool="cursor",
            machine="demo-workstation-a",
            project="Project Aurora Loom",
            derived=True,
            memtype="session-summary",
            excerpt="Derived from synthetic session metadata only; no raw conversation text is present.",
            weight=60,
        ),
        node(
            "liveagent:demo-workstation-a:codex",
            "liveagent",
            "codex@demo-workstation-a",
            agent="codex",
            machine="demo-workstation-a",
            project="Project Aurora Loom",
            project_canonical="aurora-loom",
            status="working",
            current="reviewing the synthetic demo graph wiring",
            heartbeat=now,
            tool="codex",
            weight=92,
        ),
        node(
            "liveagent:demo-gpu-node-c:claude",
            "liveagent",
            "claude@demo-gpu-node-c",
            agent="claude",
            machine="demo-gpu-node-c",
            project="Project Meridian Sync",
            project_canonical="meridian-sync",
            status="working",
            current="drafting a privacy checklist for encrypted publishing",
            heartbeat=now,
            tool="claude",
            weight=86,
        ),
    ]
    edges = [
        edge("project:aurora-loom", "machine:demo-workstation-a", "on"),
        edge("project:aurora-loom", "machine:demo-gpu-node-c", "on"),
        edge("project:harbor-lens", "machine:demo-laptop-b", "on"),
        edge("project:meridian-sync", "machine:demo-gpu-node-c", "on"),
        edge("entry:demo-workstation-a:aurora:2026-01-14", "project:aurora-loom", "in"),
        edge("entry:demo-workstation-a:aurora:2026-01-14", "machine:demo-workstation-a", "located"),
        edge("agent:codex", "entry:demo-workstation-a:aurora:2026-01-14", "did"),
        edge("entry:demo-workstation-a:aurora:2026-01-14", "dataset:synthetic-city-rgbd-1k", "uses"),
        edge("entry:demo-workstation-a:aurora:2026-01-14", "file:dataset-manifest", "touches"),
        edge("entry:demo-workstation-a:aurora:2026-01-14", "tech:sqlite", "uses"),
        edge("entry:demo-laptop-b:harbor:2026-01-15", "project:harbor-lens", "in"),
        edge("entry:demo-laptop-b:harbor:2026-01-15", "machine:demo-laptop-b", "located"),
        edge("agent:claude", "entry:demo-laptop-b:harbor:2026-01-15", "did"),
        edge("entry:demo-laptop-b:harbor:2026-01-15", "file:eval-report", "touches"),
        edge("entry:demo-laptop-b:harbor:2026-01-15", "dataset:synthetic-city-rgbd-1k", "uses"),
        edge("entry:demo-laptop-b:harbor:2026-01-15", "notion:weekly-progress", "syncs"),
        edge("entry:demo-gpu-node-c:meridian:2026-01-16", "project:meridian-sync", "in"),
        edge("entry:demo-gpu-node-c:meridian:2026-01-16", "machine:demo-gpu-node-c", "located"),
        edge("agent:human", "entry:demo-gpu-node-c:meridian:2026-01-16", "did"),
        edge("entry:demo-gpu-node-c:meridian:2026-01-16", "model:aurora-checkpoint-042", "trains"),
        edge("entry:demo-gpu-node-c:meridian:2026-01-16", "wandb:demo-run-aurora-001", "tracks"),
        edge("entry:demo-gpu-node-c:meridian:2026-01-16", "server:demo-server-a", "on"),
        edge("fact:demo:derived:aurora:2026-01-16", "project:aurora-loom", "in"),
        edge("fact:demo:derived:aurora:2026-01-16", "machine:demo-workstation-a", "located"),
        edge("fact:demo:derived:aurora:2026-01-16", "tech:canvas-3d", "uses"),
        edge("fact:demo:derived:aurora:2026-01-16", "method:idea-1", "explores"),
        edge("fact:demo:derived:aurora:2026-01-16", "file:train-pipeline", "touches"),
        edge("project:aurora-loom", "project:harbor-lens", "references"),
        edge("project:harbor-lens", "project:meridian-sync", "references"),
        edge("model:demo-vlm-small-v0", "dataset:toyfleet-mcap-v0", "uses"),
        edge("liveagent:demo-workstation-a:codex", "project:aurora-loom", "working_on"),
        edge("liveagent:demo-workstation-a:codex", "machine:demo-workstation-a", "located"),
        edge("liveagent:demo-gpu-node-c:claude", "project:meridian-sync", "working_on"),
        edge("liveagent:demo-gpu-node-c:claude", "machine:demo-gpu-node-c", "located"),
        edge("liveagent:demo-gpu-node-c:claude", "liveagent:demo-workstation-a:codex", "link"),
    ]
    degree = {n["id"]: 0 for n in nodes}
    for e in edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1
    for n in nodes:
        n["degree"] = degree.get(n["id"], 0)
    type_counts = {}
    for n in nodes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
    return {
        "meta": {
            "generated": now,
            "sanitized": True,
            "demo": True,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "type_counts": type_counts,
            "machines": ["demo-workstation-a", "demo-laptop-b", "demo-gpu-node-c"],
            "projects": ["Project Aurora Loom", "Project Harbor Lens", "Project Meridian Sync"],
        },
        "nodes": nodes,
        "edges": edges,
    }


def main():
    os.makedirs(DEMO, exist_ok=True)
    shutil.copyfile(VIEWER, os.path.join(DEMO, "index.html"))
    with open(os.path.join(DEMO, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(build_graph(), f, ensure_ascii=False, indent=2)
    print(f"wrote {os.path.join(DEMO, 'index.html')}")
    print(f"wrote {os.path.join(DEMO, 'graph.json')}")


if __name__ == "__main__":
    main()
