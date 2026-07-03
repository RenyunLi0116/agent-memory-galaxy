---
name: agent-memory-galaxy
description: Set up, operate, or package Agent Memory Galaxy-style multi-machine AI-agent memory graphs. Use when the user wants to connect a machine's agent_memory.md, Claude/Codex/Cursor session metadata, fragments, presence heartbeats, private graph aggregation, encrypted Pages publishing, a synthetic public demo, or privacy review for an agent memory graph repo.
---

# Agent Memory Galaxy

Help users create and operate a privacy-first memory graph for AI-agent work across machines.

## Operating Modes

Detect the user's intent:

- **Create a hub**: clone or initialize the repo, keep it private, configure sources, and generate a local viewer.
- **Connect this machine**: run contributor flow to write `fragments/<machine>.json`.
- **Aggregate/publish**: merge fragments, rebuild `graph.json`, optionally encrypt into `docs/galaxy/graph.enc.json`.
- **Review privacy**: check for real data before public sharing.
- **Create public marketing/demo assets**: use only synthetic data under `docs/demo/` or `samples/`.

## Privacy Rules

Treat memory artifacts as sensitive by default.

- Never publish real `graph.json`, `standalone.html`, `fragments/*.json`, `presence/*.json`, passwords, raw session logs, absolute personal paths, IPs, hostnames, private project names, W&B runs, Notion pages, credentials, or raw confidential conversation text.
- Public repos may include code, docs, skill/plugin packaging, and synthetic demo graphs only.
- Real fragments belong in a private repo or private fork.
- If publishing a web viewer, put viewer assets under `docs/galaxy/` and publish encrypted `graph.enc.json`, not plaintext.
- Client-side encryption is useful but not magic: public ciphertext can be downloaded and attacked offline, so use strong passwords and review artifacts before sharing.

## Contributor Flow

Use when the user asks to connect the current machine:

```bash
./contribute.sh <unique-machine-name> <claude|codex|cursor|human> [scan-root]
```

If `contribute.sh` is unavailable, use the manual equivalent:

```bash
python3 collect.py --local-only --machine <unique-machine-name> --tool <tool> --roots "<scan-root>" --out fragments/<unique-machine-name>.json
python3 distill.py --machine <unique-machine-name> --out fragments/<unique-machine-name>-distilled.json
git add fragments/<unique-machine-name>.json fragments/<unique-machine-name>-distilled.json
git commit -m "memory: <unique-machine-name>"
```

Do not run `update.sh` from a contributor-only machine unless the user explicitly wants this machine to be the aggregator.

## Aggregator Flow

Use when the user asks to refresh the full graph:

```bash
./update.sh
```

Use `./update.sh --pull` only when `sources.json` is configured for SSH/remote collection.

Outputs:

- `graph.json`: local plaintext, gitignored.
- `standalone.html`: local plaintext viewer, gitignored.
- `docs/galaxy/index.html`: optional deployed viewer shell.
- `docs/galaxy/graph.enc.json`: optional ciphertext if `.amg_password` and `.amg_password2` are configured.

## Public Demo Flow

Use synthetic data only:

```bash
python3 scripts/build-public-demo.py
```

This writes `docs/demo/index.html` and `docs/demo/graph.json`. It must not read or copy real fragments.

## Public Repo Review Checklist

Before public release, run a leak scan with search terms like:

```bash
rg -n "REAL_NAME|REAL_HOST|REAL_PROJECT|USERPROFILE|HOME_DIR|TOKEN|PASSWORD|SECRET|PRIVATE KEY|graph.enc|fragments/.*json|presence/.*json" .
git status --short
git ls-files
```

Confirm no real memory artifacts are tracked. It is acceptable for docs to mention file patterns such as `fragments/*.json`; it is not acceptable to track real JSON fragments.

## Two-Line Plugin Install

For Claude Code-style plugin distribution, the repo should include:

- `.claude-plugin/marketplace.json`
- `plugins/agent-memory-galaxy/.claude-plugin/plugin.json`
- `plugins/agent-memory-galaxy/skills/agent-memory-galaxy/SKILL.md`

Install commands:

```text
/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy
```

```text
/plugin install agent-memory-galaxy@agent-memory-galaxy
```
