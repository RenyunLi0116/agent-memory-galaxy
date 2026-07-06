#!/usr/bin/env python3
"""Build a local plaintext private preview from one explicit project root."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def abs_root(value: str) -> Path:
    return Path(os.path.abspath(os.path.expanduser(value)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Build local graph.json and standalone.html from one narrow project root.")
    ap.add_argument("--roots", required=True, help="One explicit project root. Do not use $HOME or / on first run.")
    ap.add_argument("--machine", default="local-preview", help="Neutral machine label for the preview graph.")
    ap.add_argument("--tool", default="codex", choices=["claude", "codex", "cursor", "human", "agent"], help="Tool label for entries.")
    ap.add_argument("--graph", default="graph.json", help="Output graph path, default graph.json.")
    ap.add_argument("--html", default="standalone.html", help="Output standalone viewer path, default standalone.html.")
    args = ap.parse_args()

    roots = [abs_root(x) for x in args.roots.split(",") if x.strip()]
    if not roots:
        raise SystemExit("--roots must name at least one explicit project directory")
    home = abs_root("~")
    for root in roots:
        if root in (Path("/"), home):
            raise SystemExit(f"Refusing wide scan root {root}. Pass a narrow project directory.")
        if not root.is_dir():
            raise SystemExit(f"Project root does not exist: {root}")

    roots_arg = ",".join(str(x) for x in roots)
    subprocess.run([
        "python3", "collect.py", "--local-only", "--machine", args.machine,
        "--tool", args.tool, "--roots", roots_arg, "--out", args.graph,
    ], cwd=ROOT, check=True)
    subprocess.run([
        "python3", "build_artifact.py", "--out", args.html, "--standalone",
    ], cwd=ROOT, check=True)
    print(f"wrote {ROOT / args.graph}")
    print(f"wrote {ROOT / args.html}")
    print("These files contain plaintext memory data and are gitignored by default.")


if __name__ == "__main__":
    main()
