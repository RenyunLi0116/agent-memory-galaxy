---
name: agent-memory-galaxy
description: Set up, operate, validate, or package Agent Memory Galaxy-style multi-machine AI-agent memory graphs. Use when the user wants a synthetic public demo, private hub setup, contributor machine connection, safe narrow-root collection, Claude/Codex/Cursor session distillation, fragment aggregation, live presence, encrypted GitHub Pages publishing, or privacy review for an agent memory graph repo.
---

# Agent Memory Galaxy

Operate Agent Memory Galaxy as a privacy-first memory graph for AI-agent work across machines.

## First Decision

Detect the requested top-level path before running commands:

- **Public demo**: rebuild only synthetic `docs/demo/` data and the public landing. Do not scan local memory.
- **Single-machine preview**: scan one explicit narrow project root and build local plaintext `standalone.html`.
- **Multi-machine private hub**: operate as either contributor or aggregator inside a private repo/fork.

Treat privacy review as a checklist task that can apply to any path, not as a data collection mode.

A Claude Code plugin skill installation gives the agent these instructions; it does not by itself provide a checked-out repo. If the current directory is not an Agent Memory Galaxy checkout, first guide the user to clone the repo or switch to the private hub checkout.

## Privacy Rules

Treat memory artifacts as sensitive by default.

- Never publish real `graph.json`, `standalone.html`, `fragments/*.json`, `presence/*.json`, passwords, raw session logs, absolute personal paths, IPs, hostnames, private project names, credentials, or raw confidential conversation text.
- Public repos may include code, docs, skill/plugin packaging, and synthetic demo graphs only.
- Real fragments belong in a private repo/fork or local machine.
- GitHub Pages is not private access control. `/galaxy/` may be publicly reachable; publish only `docs/galaxy/index.html` plus encrypted `docs/galaxy/graph.enc.json`.
- Client-side encryption is useful but not magic: public ciphertext can be downloaded and attacked offline.

## Public Demo Flow

Use synthetic data only:

```bash
python3 scripts/build-public-demo.py
python3 scripts/build-landing-concepts.py
python3 -m http.server 8765 --directory docs
```

Open `http://127.0.0.1:8765/` for the promo page or `/demo/` for the synthetic graph. The demo must not read `fragments/` or real `agent_memory.md`.

## Single-Machine Preview

Use a narrow project root. Do not scan `$HOME`, `/`, or a whole workspace on the first run.

```bash
./scripts/build-private-preview.py --machine <machine> --tool <claude|codex|cursor|human> --roots <project-root>
```

`graph.json` and `standalone.html` are plaintext and gitignored.

## Private Hub Setup

If the user has no private hub yet:

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git <private-hub>
cd <private-hub>
git remote set-url origin git@github.com:<your-user-or-org>/<private-hub>.git
git push -u origin main
```

Use a private repository or private fork before collecting real fragments.

## Contributor Flow

Use only inside a private hub checkout after confirming the user wants to store real memory there:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh <unique-machine-name> <claude|codex|cursor|human> <project-root>
```

Manual equivalent when `contribute.sh` is unavailable:

```bash
python3 collect.py --local-only --machine <machine> --tool <tool> --roots <project-root> --out fragments/<machine>.json
python3 distill.py --machine <machine> --out fragments/<machine>-distilled.json
git add -f fragments/<machine>.json fragments/<machine>-distilled.json
git commit -m "memory: <machine>"
git push
```

Do not run `update.sh` from a contributor-only machine unless the user explicitly wants this machine to be the aggregator.

## Aggregator And Encrypted Pages

Refresh the private hub:

```bash
./update.sh
```

Use `./update.sh --pull` only when `sources.json` has SSH/remote collection configured.

If `.amg_password` and `.amg_password2` are configured, encrypted Pages output is:

```text
docs/galaxy/index.html
docs/galaxy/graph.enc.json
```

The public framework excludes private artifacts by default. In a private hub, use `AMG_TRACK_PRIVATE=1 ./update.sh` when the user intentionally wants private fragments/presence or encrypted graph blobs tracked.

## Public Repo Review Checklist

Before public release:

```bash
git status --short
git ls-files
rg -n "REAL_NAME|REAL_HOST|REAL_PROJECT|USERPROFILE|HOME_DIR|TOKEN|PASSWORD|SECRET|PRIVATE KEY|graph.enc|fragments/.*json|presence/.*json" .
git ls-files 'fragments/*.json' 'presence/*.json' graph.json standalone.html docs/galaxy/graph.json
```

Confirm no real memory artifacts are tracked. It is acceptable for docs to mention file patterns such as `fragments/*.json`; it is not acceptable to track real JSON fragments in a public repo.

## Claude Code Plugin Install

The repo should include:

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

After installation, users should invoke the skill with natural language, for example: "Use Agent Memory Galaxy to create a private hub" or "Use Agent Memory Galaxy to review this repo before public release." Do not document a slash command unless a real command is added.
