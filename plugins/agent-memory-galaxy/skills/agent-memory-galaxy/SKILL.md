---
name: agent-memory-galaxy
description: Set up, operate, or package Agent Memory Galaxy-style multi-machine AI-agent memory graphs. Use when the user wants to connect a machine's agent_memory.md, Claude/Codex/Cursor session metadata, fragments, presence heartbeats, private graph aggregation, encrypted Pages publishing, a synthetic public demo, or privacy review for an agent memory graph repo.
---

# Agent Memory Galaxy

Help users create and operate a privacy-first memory graph for AI-agent work across machines.

## Start

First determine the user's intent:

- Create a new private memory hub.
- Connect this machine as a contributor.
- Refresh/aggregate an existing hub.
- Publish an encrypted viewer.
- Build a synthetic public demo.
- Review a repo for privacy leaks before making it public.

## Privacy Rules

- Never publish real `graph.json`, `standalone.html`, `fragments/*.json`, `presence/*.json`, passwords, raw session logs, absolute personal paths, IPs, hostnames, private project names, W&B runs, Notion pages, credentials, or raw confidential conversation text.
- Public repos may include code, docs, plugin packaging, and synthetic demo graphs only.
- Real fragments belong in a private repo or private fork.
- If publishing online, serve viewer assets plus encrypted `graph.enc.json`; do not serve plaintext graph data.
- Run a leak scan before public release.

## Contributor Flow

Use this when the user wants to connect the current machine:

```bash
./contribute.sh <unique-machine-name> <claude|codex|cursor|human> [scan-root]
```

If the repo is not present, clone it first:

```bash
git clone https://github.com/your-org/agent-memory-galaxy.git
cd agent-memory-galaxy
```

Choose a unique machine name. Prefer a neutral label such as `workstation-a`, `laptop-b`, or a user-approved nickname. Avoid real hostnames in public examples.

## Aggregator Flow

Use this when the user wants to merge all memory:

```bash
./update.sh
```

Use `./update.sh --pull` only when `sources.json` is configured for SSH/remote collection.

Key outputs:

- `graph.json`: local plaintext, gitignored.
- `standalone.html`: local plaintext viewer, gitignored.
- `docs/galaxy/index.html`: optional deployed viewer shell.
- `docs/galaxy/graph.enc.json`: optional encrypted graph if passwords are configured.

## Public Demo

Use synthetic data only:

```bash
python3 scripts/build-public-demo.py
```

This writes `docs/demo/index.html` and `docs/demo/graph.json`. It must not read or copy real fragments.

## Privacy Review

Before public sharing, inspect tracked files:

```bash
git ls-files
rg -n "REAL_NAME|REAL_HOST|REAL_PROJECT|USERPROFILE|HOME_DIR|TOKEN|PASSWORD|SECRET|PRIVATE KEY|graph.enc|fragments/.*json|presence/.*json" .
```

Explain any findings and remove or replace sensitive data with synthetic examples.
