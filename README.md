# Agent Memory Galaxy

[English](README.md) | [中文](README.zh-CN.md)

Your agents remember together. Privately.

Agent Memory Galaxy turns scattered AI-agent work traces across machines into one private, inspectable memory graph. It collects reviewed `agent_memory.md` notes, optional safe session metadata, machine fragments, and live presence into `graph.json`, then renders the result in a static Galaxy Viewer.

Use this public repo as the reusable framework and marketing/demo package. Keep real memory fragments and full graphs in a private fork, private hub, or local checkout.

## Quick Install as a Claude Code Plugin/Skill

Run these as two separate Claude Code messages:

```text
/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy
```

Then run:

```text
/plugin install agent-memory-galaxy@agent-memory-galaxy
```

After installation, invoke the skill with natural language. Examples: "Use Agent Memory Galaxy to create a private hub" or "Use Agent Memory Galaxy to review this repo before public release." The plugin installs guidance; you still need a repo checkout for the scripts.

## Choose One Path

### A. Public Promo And Synthetic Demo

This path does not scan your machine. It rebuilds only fictional demo data under `docs/demo/`.

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
python3 scripts/build-public-demo.py
python3 scripts/build-landing-concepts.py
python3 -m http.server 8765 --directory docs
```

Open `http://127.0.0.1:8765/` for the promo page and `http://127.0.0.1:8765/demo/?style=cosmos&lang=en` for the synthetic interactive demo. The demo graph is fictional, sanitized, and safe to publish.

### B. Single-Machine Private Preview

This path scans one explicit project directory and builds a local plaintext viewer. Do not start with `$HOME`, `/`, or a whole workspace.

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
./scripts/build-private-preview.py --machine laptop-a --tool codex --roots ~/projects/my-app
```

Open `standalone.html` locally. It contains plaintext memory data and is gitignored.

### C. Multi-Machine Private Hub

This path is for real collaboration. Use a private repository or private fork before collecting real fragments.

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git my-memory-hub
cd my-memory-hub
git remote set-url origin git@github.com:<your-user-or-org>/<private-hub>.git
```

On each contributor machine, run from the private hub checkout with a narrow project root:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh workstation-a codex ~/projects/my-app
```

On the aggregator machine:

```bash
./update.sh
```

Use `./update.sh` for a local refresh. In a private hub where you intentionally want Git to track private fragments, presence, or encrypted Pages blobs, use:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

Contributors write `fragments/<machine>.json`. The aggregator merges fragments, injects presence, optionally encrypts for Pages, and rebuilds the local `standalone.html`.

### Team Work: Multiple Users On One Private Hub

A private hub can be shared by a whole team. Two identity concepts stay separate in the graph:

- **agent** — the executor labeled inside a memory entry (`claude`, `codex`, `cursor`, `human`). It answers "which tool did the work".
- **user** — the push identity (GitHub username) of the person whose machines contribute fragments. It answers "whose machines and whose memory".

Create a team hub:

1. Create the private hub repository as in path C above.
2. Add each teammate as a GitHub collaborator on the private hub. Push permission is the membership declaration; there is no extra account system.
3. Optionally commit a `team.json` in the hub root (copy `team.json.example`): team name, member display names/colors for the viewer, and a `default_user` backfilled onto fragments pushed before team mode.

Join a team hub — each member, on each of their servers, clones with their own GitHub identity and contributes as usual:

```bash
git clone git@github.com:<org>/<private-hub>.git && cd <private-hub>
AMG_PRIVATE_HUB=1 ./contribute.sh my-workstation codex ~/projects/my-app        # identity auto-detected
AMG_PRIVATE_HUB=1 ./contribute.sh my-workstation codex ~/projects/my-app ada   # or declared explicitly
```

The push identity resolves in this priority order: `--user` (the optional 4th `contribute.sh` argument) > `AMG_USER` env > `git config user.name` > `$USER`. It is written only as a `user` attribute on entry/fact/machine/liveagent nodes and never becomes part of a node id, so graphs from different machines always merge cleanly.

The aggregator needs no new steps: `./update.sh` merges all fragments as before, backfills `default_user` on pre-team fragments, and emits `user` nodes with `owns` edges to their machines. When user data is present, the viewer gains a USER filter (with machine cascade) and per-user coloring.

## What This Does

```text
reviewed notes      safe session metadata      contributor fragments      live presence
agent_memory.md     Claude/Codex/Cursor        fragments/*.json           presence/*.json
        \                    |                         |                         /
         \                   |                         |                        /
          collect.py + distill.py + merge fragments + presence injection
                                      |
                                  graph.json
                                      |
             local standalone viewer or optional encrypted Pages viewer
```

Core pieces:

- `collect.py` scans local and remote sources and normalizes them into `graph.json`.
- `distill.py` fills gaps from native agent-session metadata without copying raw conversation text.
- `fragments/*.json` lets many machines contribute to one private hub.
- `presence/*.json` lights up currently active agents in the viewer.
- `viewer/index.html` is the runtime galaxy viewer.
- `docs/index.html` is the public promo landing page.
- `docs/demo/` contains the fully synthetic public demo.
- `docs/galaxy/` is reserved for your optional encrypted viewer shell for private data.

## GitHub Pages URL Policy

If Pages is enabled with `main` + `/docs`, the expected public URL is:

```text
https://renyunli0116.github.io/agent-memory-galaxy/
```

| URL/path | Purpose | Data policy |
|---|---|---|
| `/agent-memory-galaxy/` | Public promo landing | No real data |
| `/agent-memory-galaxy/demo/?style=cosmos&lang=en` | Synthetic interactive demo | Fake graph only |
| `/agent-memory-galaxy/concepts/` | Design exploration archive | Public, secondary |
| `/agent-memory-galaxy/galaxy/` | Optional encrypted viewer shell | Publicly reachable shell, no plaintext graph |
| `/agent-memory-galaxy/galaxy/graph.enc.json` | Optional encrypted graph blob | Ciphertext only |
| `standalone.html` | Local plaintext viewer | Local only, gitignored |
| private hub/fork | Real fragments, presence, graph | Private repo/local machine |

Enable Pages in GitHub with `Settings -> Pages -> Build and deployment -> Source -> GitHub Actions`. The repository includes `.github/workflows/pages.yml`, which publishes the static `docs/` site on every push to `main`.

GitHub Pages is not an access-control layer. Treat `/galaxy/` as a public shell and rely on strong client-side encryption plus private handling of plaintext artifacts.

## Privacy Model

Agent Memory Galaxy is privacy-first, not privacy-magic.

Public distribution rule of thumb:

- Public repo: framework code, docs, skill package, synthetic demo data.
- Private repo/fork: real `fragments/*.json`, `presence/*.json`, `graph.json`, `standalone.html`.
- Optional encrypted Pages viewer: `docs/galaxy/index.html` plus `docs/galaxy/graph.enc.json`, never plaintext `graph.json`.

Do not store secrets, credentials, private keys, raw confidential conversations, or unrevised sensitive code in memory files. Session distillation is intended to extract structured metadata only, but you should review configuration and generated artifacts before sharing. Client-side encryption reduces exposure, but public ciphertext can still be downloaded and attacked offline.

This public template ignores real fragments, live presence, and encrypted graph snapshots by default. In a private hub where you intentionally want Git to sync private memory artifacts, use:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

## Optional Encrypted Pages Viewer

Create two strong local password files in the private hub:

```bash
printf '%s' 'first-strong-passphrase' > .amg_password
printf '%s' 'second-strong-passphrase' > .amg_password2
chmod 600 .amg_password .amg_password2
AMG_TRACK_PRIVATE=1 ./update.sh
```

The publishable output is:

```text
docs/galaxy/index.html
docs/galaxy/graph.enc.json
```

Do not publish plaintext `graph.json`.

## Contributor Vs Aggregator

- Contributor machine: runs `AMG_PRIVATE_HUB=1 ./contribute.sh <machine> <claude|codex|cursor|human> <project-root> [user]`, writes a private fragment, and pushes it to the private hub.
- Aggregator machine: runs `./update.sh` or `./update.sh --pull`, merges all fragments, injects live presence, optionally encrypts for Pages, and rebuilds the local standalone viewer.

Contributors do not need encryption passwords and should not touch `docs/galaxy/`.

## Data Model

Nodes include `project`, `entry`, `fact`, `agent`, `liveagent`, `machine`, `user`, `dataset`, `server`, `model`, `method`, `file`, `wandb`, `tech`, `notion`, `boundary`, and `artifact`.

Edges include `in`, `did`, `located`, `uses`, `touches`, `trains`, `tracks`, `syncs`, `explores`, `references`, `depends_on`, `inherits_from`, `exports_to`, `working_on`, `handoff_to`, `owns`, `shared_on`, `cached_on`, `redacts`, `encrypts`, `publishes`, `keeps_private`, `validates`, `serves`, `replicates_to`, `link`, and `on`.

Shared entities automatically connect projects across machines. For example, two different agents touching the same dataset, file, model, or Notion page will become connected in the graph.

## Requirements

- Python 3.8+ for collection, distillation, demo generation, and artifact building.
- Git for multi-machine sync.
- `cryptography` only if you enable encrypted Pages publishing with `encrypt.py`.
- No frontend build step is required. The viewer is static HTML/CSS/JS.

## License

MIT.
