# AGENTS.md - Agent Memory Galaxy operating guide

You are working inside an Agent Memory Galaxy hub. The goal is to collect AI-agent work memory from one or more machines into a private knowledge graph, then view it locally or publish an encrypted viewer.

## First Decide the Role

Use the contributor role unless the user explicitly says this machine is the aggregator.

| Role | What to run | What not to do |
|---|---|---|
| Contributor | `./contribute.sh <machine> <tool> [roots]` | Do not run `update.sh`, do not encrypt, do not touch `docs/galaxy/` |
| Aggregator | `./update.sh [--pull]` | Do not publish plaintext `graph.json` or `standalone.html` |

`<tool>` should be `claude`, `codex`, `cursor`, or `human`.

## Contributor Flow

```bash
./contribute.sh <unique-machine-name> <claude|codex|cursor|human> [scan-root]
```

Use a neutral unique machine name, especially in examples: `workstation-a`, `laptop-b`, `lab-node-c`. Avoid real hostnames in public docs.

The command writes:

- `fragments/<machine>.json`
- `fragments/<machine>-distilled.json` when distillation finds structured session metadata

Fragments are plaintext. Keep them in a private hub. The public framework ignores `fragments/*.json` by default.

## Aggregator Flow

```bash
./update.sh
```

Use `./update.sh --pull` only when `sources.json` has SSH/remote collection configured.

Aggregator outputs:

- `graph.json`: plaintext graph, local only, gitignored.
- `standalone.html`: plaintext local viewer, gitignored.
- `docs/galaxy/index.html`: optional Pages viewer shell.
- `docs/galaxy/graph.enc.json`: optional encrypted graph, publishable if passwords are strong.

## Memory Format

For future work, maintain an `agent_memory.md` file in each project:

```markdown
## 2026-07-03 - Short title (codex)
- What changed:
- Why:
- Status: doing | done
- Verification:
- Files:
```

The collector also understands limited structured metadata from native Claude/Codex/Cursor sessions through `distill.py`. It is intended to fill gaps, not replace reviewed project memory.

## Privacy Rules

- Never commit real `graph.json`, `standalone.html`, `.amg_password*`, `sources_cache/`, logs, credentials, raw session logs, or private fragments.
- Keep real `fragments/*.json` and `presence/*.json` private.
- Public demo data must be synthetic and live under `docs/demo/` or `samples/`, not under `fragments/`.
- Before making a repo public, run a leak scan for paths, usernames, hostnames, IPs, tokens, real project names, and tracked memory JSON.

## Useful Files

- `README.md`: public overview and install commands.
- `ONBOARDING.md`: setup and operating walkthrough.
- `PORTABILITY.md`: migration and publishing notes.
- `viewer/index.html`: runtime galaxy viewer source.
- `docs/index.html`: public landing page.
- `docs/demo/`: synthetic demo only.
