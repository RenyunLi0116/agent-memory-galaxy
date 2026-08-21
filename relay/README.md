# relay/ — Live Up/Down Sync Inboxes

This is where "**A finishes work → hub → whoever is working right now gets it immediately**" actually
lands. Written and read by `relay.py`; **do not hand-edit**.

```
relay/
  <recipient-machine>/
    by-<writer-machine>.jsonl   append-only; **only <writer-machine> ever writes this file**
    _ack.json                   **only <recipient-machine> ever writes it** (delivered / unread / last item)
```

## Why the files are split this way

When many machines push through git concurrently, **rebase never conflicts as long as every file has a
single writer**. Hence:

- `by-<X>` names the **writer**, not the memory's **origin**. When the hub relays on behalf of a server
  that only gets harvested over ssh (`pull_remote.sh`) and never runs `contribute.sh` itself, the hub
  writes `by-<hub>.jsonl` and the line's `from.machine` carries the real origin.
- An item's `id = <content key>.<body rev>` is derived entirely from content, so if both the origin
  machine and the hub relay the same entry, the recipient de-duplicates it for free.

## One line looks like

```json
{"id":"f0fce1689b88.d78f10","ts":"2026-08-19T08:46:28Z","writer":"hub-a",
 "from":{"machine":"gpu-node-c","agent":"","user":"ada","tool":"claude"},
 "project":"myproj","project_label":"My Project",
 "kind":"entry","title":"stage2 converged","date":"2026-08-19","status":"done",
 "update":false,"derived":false,"summary":"…","node_id":"entry:gpu-node-c:…","source":"agent_memory.md"}
```

## Reading side

```bash
python3 relay.py apply  --machine <this-machine>   # render SYNC_INBOX.md (unread first, same-project pinned)
python3 relay.py read   --machine <this-machine>   # mark as read once handled
python3 relay.py status                            # who is online / per-inbox unread counts
```

`SYNC_INBOX.md` and `.amg_relay/` (ledger, read cursor, locks) are **never committed** — every machine
rebuilds them locally, so they cause neither commit noise nor conflicts.

## Retention

Each `relay.py fanout` also garbage-collects entries older than 14 days **from the files it wrote itself**
(`--keep-days`). It never rewrites another machine's file — that would break the single-writer invariant.

## Privacy

`relay/*/by-*.jsonl` is **plaintext** (body summaries capped at 600 chars) — the same sensitivity as
`fragments/`. In this public template the inboxes are gitignored and excluded from `update.sh`'s
`git add`; a private hub opts in with `AMG_PRIVATE_HUB=1` / `AMG_TRACK_PRIVATE=1`. Never publish them to
`docs/` — public Pages carries ciphertext only.
