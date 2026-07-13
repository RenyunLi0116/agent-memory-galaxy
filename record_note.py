#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append reviewed agent_memory.md notes and capture private note lineage.

This is the write-time companion to collect.py's optional .amg_lineage sidecar.
It stores only hashes and safe tool/session metadata, never note text or paths.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

SCHEMA_VERSION = "note_lineage_event.v0.5"
LINEAGE_DIR = ".amg_lineage"
LINEAGE_FILE = "note_lineage.jsonl"
TOOLS = {"claude", "codex", "cursor", "human", "agent"}
SESSION_ENV = ("AMG_AGENT_SESSION_ID", "CODEX_SESSION_ID", "CLAUDE_SESSION_ID", "CURSOR_SESSION_ID")


def stable_hash(value: str, n: int = 24) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:n]


def note_anchor_hash(head: str, body: str) -> str:
    norm = "\n".join((head or "").strip().split()) + "\n" + "\n".join((body or "").strip().split())
    return stable_hash(norm, 24)


def count_sections(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if re.match(r"^##\s+\S", line):
                count += 1
    return count


def read_body(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if args.body:
        return args.body
    raise SystemExit("Provide --body or --body-file.")


def env_session_id() -> str:
    for key in SESSION_ENV:
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return ""


def append_note(memory_path: Path, heading: str, body: str) -> None:
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    needs_blank = memory_path.exists() and memory_path.stat().st_size > 0
    with memory_path.open("a", encoding="utf-8") as f:
        if needs_blank:
            f.write("\n\n")
        f.write(f"## {heading}\n")
        f.write(body.strip() + "\n")


def write_lineage(root: Path, event: dict) -> Path:
    sidecar = root / LINEAGE_DIR / LINEAGE_FILE
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    with sidecar.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return sidecar


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root containing agent_memory.md")
    parser.add_argument("--tool", required=True, choices=sorted(TOOLS))
    parser.add_argument("--machine", default=os.environ.get("AMG_LOCAL_NAME", "local"))
    parser.add_argument("--title", required=True)
    parser.add_argument("--status", choices=["doing", "done", "todo", "logged"], default="done")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--body", default="")
    parser.add_argument("--body-file", default="")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--no-heading-tool-tag", action="store_true", help="Rely on lineage sidecar instead of a visible heading tag")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    memory_path = root / "agent_memory.md"
    body = read_body(args)
    tag = "" if args.no_heading_tool_tag else f" ({args.tool})"
    status = "" if args.status == "logged" else f" [{args.status}]"
    heading = f"{args.date} - {args.title}{tag}{status}"
    section_index = count_sections(memory_path)
    anchor = note_anchor_hash(heading, body)
    session_id = args.session_id or env_session_id()
    created_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    event = {
        "schema_version": SCHEMA_VERSION,
        "record_kind": "lineage_event",
        "event_id_hash": stable_hash(f"{root}|{section_index}|{anchor}|{args.tool}", 32),
        "created_at": created_at,
        "section_index": section_index,
        "note_id_hash": stable_hash(f"{root}|{section_index}", 24),
        "note_anchor_hash": anchor,
        "agent_tool": args.tool,
        "agent_session_id_hash": stable_hash(session_id, 24) if session_id else "missing",
        "machine_hash": stable_hash(args.machine, 24),
        "project_hash": stable_hash(str(root), 24),
        "source_event_kind": "note_lineage_event",
        "evidence_pointer_ids": [f"amg-note:{stable_hash(anchor, 16)}"],
        "capture_status": "captured",
        "privacy_boundary": "safe_hashes_only",
    }
    append_note(memory_path, heading, body)
    sidecar = write_lineage(root, event)
    print(json.dumps({
        "memory": str(memory_path),
        "lineage_sidecar": str(sidecar),
        "section_index": section_index,
        "note_anchor_hash": anchor,
        "agent_tool": args.tool,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
