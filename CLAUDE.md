# CLAUDE.md - Agent Memory Galaxy guide

Claude agents should follow the same operating rules as `AGENTS.md`.

Default to contributor mode:

```bash
./contribute.sh <unique-machine-name> claude [scan-root]
```

Run aggregator commands only when the user explicitly asks this machine to maintain the full hub:

```bash
./update.sh
./update.sh --pull
```

Privacy reminders:

- Do not commit real `fragments/*.json`, `presence/*.json`, `graph.json`, `standalone.html`, passwords, logs, raw session files, hostnames, IPs, or private project names to a public repo.
- Keep public demo data synthetic.
- If publishing online, publish `docs/galaxy/index.html` plus encrypted `docs/galaxy/graph.enc.json`, not plaintext graph data.

Read `ONBOARDING.md` for the complete workflow and `PORTABILITY.md` for migration/publishing notes.
