# CLAUDE.md - Agent Memory Galaxy Guide

Claude agents should follow the same operating rules as `AGENTS.md`.

First choose one top-level path:

- Public demo: `python3 scripts/build-public-demo.py` and synthetic data only.
- Single-machine preview: `./scripts/build-private-preview.py --roots <project-root>` and local plaintext only.
- Multi-machine private hub: contributor or aggregator role inside a private repo/fork.

Inside a private hub, use the contributor role unless the user explicitly asks this machine to maintain the full hub. Use a narrow project root; do not scan `$HOME`, `/`, or a whole workspace on the first run.

Contributor example:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh workstation-a claude ~/projects/my-app
```

In a multi-user team hub, append the push identity (GitHub username) as an optional 4th argument or set `AMG_USER`; it defaults to `git config user.name`, then `$USER`. See the Team Work section in `README.md` and `team.json.example`. The push identity (`user`) is distinct from the agent label inside entries.

When adding reviewed memory, prefer write-time lineage capture:

```bash
python3 record_note.py --root <project-root> --tool codex --machine <machine> \
  --title "Short title" --status done --body-file /tmp/note.md
```

This appends `agent_memory.md` and writes a private `.amg_lineage/note_lineage.jsonl` sidecar. `collect.py` can then recover the agent from `agent_source=note_lineage_event` even when the note heading has no visible tool tag.

Aggregator examples:

```bash
./update.sh
./update.sh --pull
AMG_TRACK_PRIVATE=1 ./update.sh
```

Privacy reminders:

- Do not commit real `fragments/*.json`, `presence/*.json`, `graph.json`, `standalone.html`, passwords, logs, raw session files, hostnames, IPs, or private project names to a public repo.
- Keep public demo data synthetic.
- If publishing online, publish `docs/galaxy/index.html` plus encrypted `docs/galaxy/graph.enc.json`, not plaintext graph data.
- GitHub Pages is publicly reachable; privacy comes from encryption and private handling of plaintext artifacts.

Read `ONBOARDING.md` for the complete workflow and `PORTABILITY.md` for migration/publishing notes.
