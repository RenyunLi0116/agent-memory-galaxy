# presence/ - Agent Live Status

Each currently working agent can maintain one `<machine>__<agent>.json` heartbeat file through `heartbeat.sh`:

```json
{
  "agent": "codex-1",
  "machine": "workstation-a",
  "project_canonical": "myproj",
  "project": "myproj",
  "status": "working",
  "current": "reviewing graph merge output",
  "heartbeat": "2026-07-06T10:32:00Z",
  "tool": "codex"
}
```

The aggregator reads these files through `collect.py` / `update.sh`. Fresh `status=working` heartbeats become `liveagent` nodes in the Galaxy Viewer and connect to `project_canonical` with `working_on` edges.

One agent owns one file, so multi-machine pushes usually do not conflict. Real `presence/*.json` files are plaintext private artifacts and are ignored by the public template. Track them only inside a private hub, intentionally, with `AMG_TRACK_PRIVATE=1 ./update.sh` or explicit `git add -f`.

See `ONBOARDING.md` sections "Connect Contributor Machines", "Refresh The Aggregated Graph", and "Optional Encrypted Pages Viewer" for the private hub workflow.
