# Onboarding

Agent Memory Galaxy has three distinct paths. Pick one before running commands.

- **Public demo**: rebuilds fictional data under `docs/demo/`; does not scan local memory.
- **Single-machine private preview**: scans one explicit project root and builds local plaintext `standalone.html`.
- **Multi-machine private hub**: contributors push private fragments; one aggregator merges and optionally publishes an encrypted viewer.

Use a private repository or private fork for real memory data. Use this public repository only for framework code, docs, plugin packaging, and synthetic demo data.

## 1. Public Demo

```bash
python3 scripts/build-public-demo.py
python3 scripts/build-landing-concepts.py
python3 -m http.server 8765 --directory docs
```

Open `http://127.0.0.1:8765/` or `http://127.0.0.1:8765/demo/`. Never generate public demos from real fragments.

## 2. Single-Machine Private Preview

```bash
./scripts/build-private-preview.py --machine laptop-a --tool codex --roots ~/projects/my-app
```

Open `standalone.html` locally. `graph.json` and `standalone.html` are plaintext and gitignored. Use a narrow project root; do not start by scanning `$HOME`, `/`, or an entire workspace.

## 3. Create a Private Hub

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git my-memory-hub
cd my-memory-hub
git remote set-url origin git@github.com:<your-user-or-org>/<private-hub>.git
```

Keep the private hub private if it will store real fragments.

## 3.5 Invite Teammates (Team Work)

Skip this section for a single-person hub; nothing changes there.

1. Add each teammate as a GitHub collaborator on the private hub repository. Push permission is the membership declaration — no extra account system.
2. Optionally commit `team.json` in the hub root (copy `team.json.example`): team name, member display names/colors for the viewer, and a `default_user` backfilled onto fragments pushed before team mode.

Each member then follows section 4 on each of their servers, cloning with their own GitHub identity. The push identity (`user`) resolves as: `--user` / 4th `contribute.sh` argument > `AMG_USER` env > `git config user.name` > `$USER`.

Do not confuse `user` with `agent`: `user` is the person who pushes the memory (a GitHub username, stored only as a node attribute, never in node ids), while `agent` is the tool labeled inside an entry (`claude`, `codex`, ...) that executed the work. One user's machines usually host many agents.

## 4. Connect Contributor Machines

From the private hub checkout on each contributor machine:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh <unique-machine-name> <claude|codex|cursor|human> <project-root> [user]
```

Examples:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh laptop-a codex ~/projects/my-app
AMG_PRIVATE_HUB=1 ./contribute.sh workstation-b claude ~/work/active-project
AMG_PRIVATE_HUB=1 ./contribute.sh gpu-node-c claude ~/work/shared-eval kael      # explicit push identity
AMG_USER=mira AMG_PRIVATE_HUB=1 ./contribute.sh lab-node-d codex ~/projects/relay # identity via env
```

Contributor output goes to `fragments/`. These files are plaintext and should remain private. The `AMG_PRIVATE_HUB=1` flag is required before the script will stage ignored fragments and push them.

## 5. Refresh The Aggregated Graph

On the aggregator machine:

```bash
./update.sh
```

If `sources.json` has remote SSH collection configured:

```bash
./update.sh --pull
```

This produces local plaintext `graph.json` and `standalone.html`, both gitignored.

In a team hub, merged fragments keep each contributor's `user` attribute; nodes from pre-team fragments are backfilled with `team.json`'s `default_user`, and the aggregator emits `user` nodes with `owns` edges to their machines.

The public template intentionally does not stage real fragments, live presence, or encrypted graph snapshots during `update.sh`. In your private hub, opt in when you want Git to sync private memory artifacts:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```


## 5.5 Live Up/Down Sync (relay)

Heartbeats (`heartbeat.sh`) are *near*-realtime — roughly 10 minutes, and the other side has to come and
pull. The relay turns that into a push: the moment A's work reaches the hub, every machine whose
`presence/` says `status=working` with a fresh heartbeat gets A's new memory, in seconds to tens of
seconds.

```
A finishes ──contribute.sh / heartbeat.sh──► hub (private repo)
                                               │  1. relay.py fanout — read presence/, deliver to
                                               │     whoever is working right now
                                               ├─► relay/<B>/by-<writer>.jsonl   (over git)
                                               │  2. relay.py wake — ssh-reachable peers pull at once
                                               ▼
                                        B's sync_watch.sh / heartbeat.sh
                                               └─► relay.py apply → B's SYNC_INBOX.md
```

**Already wired in** (`AMG_RELAY=0` turns it off):

- `contribute.sh` — fans out while pushing, then `wake`s ssh-reachable peers.
- `heartbeat.sh` — every check-in (including `--idle`, i.e. "done for now") fans out and re-renders the
  local inbox.
- `update.sh` — the aggregator relays **on behalf of** every fragment, including servers that are only
  harvested over ssh and never run `contribute.sh` themselves. This is the coarse (per-run) backstop.

**For second-level latency, run the poller** (one per machine; add `--hub` on the aggregator):

```bash
nohup ./sync_watch.sh <machine> [--hub] >> sync_watch.log 2>&1 &
# or, without a daemon (built-in flock keeps runs from overlapping):
# * * * * * cd /path/to/repo && ./sync_watch.sh <machine> --once >> sync_watch.log 2>&1
```

Each pass: compare `git ls-remote` against the local `origin/main` (cheap — does nothing when unchanged)
→ `pull --rebase` only if it moved → refresh this machine's presence (**written only when something
substantive changed**, so a 30s poll does not spam commits) → render `SYNC_INBOX.md` and run
`$AMG_ON_SYNC` if there is anything new → commit **only** `presence/` and `relay/` (never `git add -A`)
→ on `--hub`, also fan out and `wake` peers. It backs off to `--idle-interval` (default 300s) when
nobody is working.

**Using it as an agent**

```bash
python3 relay.py status                     # who is online, unread per inbox
cat SYNC_INBOX.md                           # unread first; same canonical project pinned with ★
python3 relay.py read --machine <machine>   # mark handled
```

Put "read `SYNC_INBOX.md` before starting" into that machine's `CLAUDE.md`/`AGENTS.md`, or hook a
notification: `export AMG_ON_SYNC='notify-send "$AMG_NEW new syncs" "$AMG_INBOX"'`.
`$AMG_NEW` is what arrived **this pass** (not the standing unread count, so the hook does not re-fire
every 30s), `$AMG_UNREAD` is the total unread, `$AMG_INBOX` is the file. The hook runs with the lock
file descriptors closed, so backgrounding something from it cannot pin the repo lock.

**Why concurrent pushes never conflict** (invariants — understand these before changing the code)

- `relay/<recipient>/by-<writer>.jsonl` — **only the writer writes it** (append-only). `by-<X>` is the
  *writer*, not the memory's origin: when the hub relays for a harvested-only server it writes
  `by-<hub>.jsonl`, and the line's `from.machine` holds the origin. That keeps hub-proxy relaying
  single-writer too.
- `relay/<recipient>/_ack.json` — **only the recipient writes it**, and only when a substantive field
  changes (not on every render), so it never becomes a commit treadmill.
- `SYNC_INBOX.md` and `.amg_relay/` (ledger, read cursor, locks) — **never committed**; rebuilt locally.
- Item `id`s are content-derived, so the same entry relayed by both its origin and the hub de-duplicates
  at the recipient.
- Same-machine races (`update.sh` cron + poller + `contribute.sh`) serialize on one repo-wide
  `flock` at `.amg_relay/repo.lock`, taken by all four entry points in the same order.

**Delivery semantics**

- The ledger records `sent`: **bootstrap only registers, it never counts as delivered** — otherwise the
  catch-up window would replay a machine's entire history the moment anyone came online.
- **When nobody is online, nothing is recorded** — the items stay pending until someone starts working
  (`--drop-pending` restores the older discard-it behaviour).
- **Catch-up window `--catchup-min` (default 1440 min)**: already-delivered items stay in the candidate
  pool for that long, so a machine that starts working 30 seconds *after* the fan-out still receives
  them; the recipient de-duplicates by item id, so nobody is bothered twice.
- **A peer is never `reset --hard`**: `wake` does `--ff-only` only and reports `AMG_DIVERGED` for a
  human to resolve — the peer may be holding local commits it deliberately kept for a later retry
  (`contribute.sh` promises exactly that). `pull_remote.sh` force-aligns only when the remote has no
  commits of its own (`git merge-base --is-ancestor`).

**Keeping it from becoming noise**

- Item identity is `machine|project|title|date` — **not** the node id, because `collect.py`'s entry ids
  embed a section index that shifts whenever a note is inserted at the top of a file.
- Only a changed body counts as an "update", and the same item is not re-sent within 20 minutes
  (`--repeat-min`).
- Only entries from the last 14 days (`--max-age-days`), at most 60 per pass (`--max`); the rest carry
  over to the next pass.
- The **first** time a machine's fragment is seen it is only recorded, never delivered — otherwise its
  entire history would land on whoever happens to be online.
- `relay` edges in the graph carry only a count and a date (no exact timestamp), so relaying does not
  change `graph.json`'s hash on every pass.
- **Commit rate-limiting**: the poller commits and pushes immediately when `relay/` actually gained
  payload; when only heartbeats moved it commits at most once per `AMG_COMMIT_MIN` (default 300s) —
  otherwise a 30s loop turns into thousands of commits a day.
- `_ack.json` is written only when a substantive field changes, and so is `presence/`
  (`presence-sync --min-delta-min`).
- **The lock wraps the git section only.** `heartbeat.sh --loop` runs all day; holding a script-level
  lock would starve the aggregation cron (it times out on `flock -w 600` and exits 0, so cron sees
  nothing wrong). All four entry points share `.amg_relay/repo.lock` in the same order (repo lock →
  `relay.lock`), so they cannot deadlock; without `flock` installed they degrade to no lock and say so.
- On the public template `presence/` and `relay/` are gitignored, so the poller only commits them when
  `AMG_PRIVATE_HUB=1` (or `AMG_TRACK_PRIVATE=1`); it logs once when it is running in local-only mode.

**Privacy**: `relay/*/by-*.jsonl` is plaintext (600-char body summaries) — the same tier as `fragments/`.
This public template gitignores it and excludes it from `update.sh`'s `git add`; a private hub opts in
with `AMG_PRIVATE_HUB=1` / `AMG_TRACK_PRIVATE=1`. It must never reach `docs/`.

## 6. Optional Encrypted Pages Viewer

Create two strong local password files:

```bash
printf '%s' 'first-strong-passphrase' > .amg_password
printf '%s' 'second-strong-passphrase' > .amg_password2
chmod 600 .amg_password .amg_password2
```

Then run:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

The publishable output is:

```text
docs/galaxy/index.html
docs/galaxy/graph.enc.json
```

Do not publish plaintext `graph.json`. GitHub Pages is public; privacy comes from encryption and strong passwords.

## 7. Memory Notes

Add `agent_memory.md` to project roots:

```markdown
## 2026-07-06 - Short title (codex)
- What changed:
- Why:
- Status: doing | done
- Verification:
- Files:
```

Hand-written memory is the most accurate source. Native session distillation is a fallback for gaps and should extract structured metadata only.

## 8. Public Release Checklist

Before publishing:

```bash
git ls-files
rg -n "USERPROFILE|HOME_DIR|REAL_HOST|REAL_PROJECT|TOKEN|PASSWORD|SECRET|graph.enc|fragments/.*json|presence/.*json" .
git ls-files 'fragments/*.json' 'presence/*.json' graph.json standalone.html docs/galaxy/graph.json
```

Confirm no real memory artifacts are tracked.
