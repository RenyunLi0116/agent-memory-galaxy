# AGENTS.md - Agent Memory Galaxy Operating Guide

You are working inside an Agent Memory Galaxy repo. First choose one top-level path.

| Path | What to run | Data boundary |
|---|---|---|
| Public demo | `python3 scripts/build-public-demo.py` | Synthetic data only |
| Single-machine preview | `./scripts/build-private-preview.py --roots <project-root>` | Local plaintext only |
| Multi-machine private hub | Contributor or aggregator commands below | Private hub only |

Inside a private hub, use the contributor role unless the user explicitly says this checkout is the aggregator.

## Contributor Flow

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh <unique-machine-name> <claude|codex|cursor|human> <project-root> [user]
```

Use a neutral unique machine name: `workstation-a`, `laptop-b`, `lab-node-c`. Avoid real hostnames in public docs. Use a narrow project root; do not scan `$HOME`, `/`, or a whole workspace on the first run.

The optional `[user]` is the push identity (GitHub username) for multi-user team hubs; it defaults to `AMG_USER`, then `git config user.name`, then `$USER`, and is distinct from the agent label inside entries (which tool did the work). See `team.json.example`.

The command writes:

- `fragments/<machine>.json`
- `fragments/<machine>-distilled.json` when distillation finds structured session metadata

Fragments are plaintext. Keep them in a private hub. The public framework ignores `fragments/*.json` by default, and `AMG_PRIVATE_HUB=1` is required before `contribute.sh` stages ignored fragments.

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

`update.sh` excludes private artifacts by default. In a private hub, use `AMG_TRACK_PRIVATE=1 ./update.sh` only when the user intentionally wants private fragments or encrypted graph blobs tracked.

## Memory Format

Maintain an `agent_memory.md` file in each project:

```markdown
## 2026-07-06 - Short title (codex)
- What changed:
- Why:
- Status: doing | done
- Verification:
- Files:
```

The collector also understands limited structured metadata from native Claude/Codex/Cursor sessions through `distill.py`. It is intended to fill gaps, not replace reviewed project memory.

For write-time provenance, prefer the recorder when adding a reviewed note:

```bash
python3 record_note.py --root <project-root> --tool codex --machine <machine> \
  --title "Short title" --status done --body-file /tmp/note.md
```

It appends `agent_memory.md` and writes a private `.amg_lineage/note_lineage.jsonl` sidecar. The collector uses that sidecar to set `agent_source=note_lineage_event`, so provenance still works when the visible heading does not contain `(codex)` or another tool tag. Use `--no-heading-tool-tag` only when intentionally testing lineage-only attribution.

## Privacy Rules

- Never commit real `graph.json`, `standalone.html`, `.amg_password*`, `sources_cache/`, logs, credentials, raw session logs, or private fragments to a public repo.
- Keep real `fragments/*.json` and `presence/*.json` private.
- Public demo data must be synthetic and live under `docs/demo/`, not under `fragments/`.
- `docs/galaxy/` is a public encrypted viewer shell if deployed to GitHub Pages; it is not private access control.
- Before making a repo public, run a leak scan for paths, usernames, hostnames, IPs, tokens, real project names, and tracked memory JSON.

## Useful Files

- `README.md`: public overview, install commands, URL policy.
- `ONBOARDING.md`: setup and operating walkthrough.
- `PORTABILITY.md`: migration and publishing notes.
- `viewer/index.html`: runtime galaxy viewer source.
- `docs/index.html`: public promo landing page.
- `docs/demo/`: synthetic demo only.
- `docs/galaxy/`: optional encrypted viewer shell.
