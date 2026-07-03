# Agent Memory Galaxy

Your agents remember together. Privately.

Agent Memory Galaxy is a privacy-first hub for multi-machine AI-agent work memory. It collects hand-written `agent_memory.md` logs, optional Claude memory files, and structured metadata distilled from Claude/Codex/Cursor sessions into one normalized `graph.json`, then renders the result as an interactive knowledge-galaxy viewer.

Use the public repo as the reusable framework. Keep your real memory fragments and full graph in a private fork or private deployment.

## Why It Exists

AI agents are useful, but their memory is usually scattered:

- one machine has the training run notes;
- another machine has the debugging session;
- Claude, Codex, Cursor, and humans each leave different traces;
- project relationships live in filenames, W&B runs, datasets, Notion pages, and half-remembered context.

Agent Memory Galaxy turns those traces into a durable graph so a future agent can ask, "what happened here before I arrived?"

## Quick Install as a Skill

Run these as two separate Claude Code messages:

```text
/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy
```

Then run:

```text
/plugin install agent-memory-galaxy@agent-memory-galaxy
```

After installation, use:

```text
/agent-memory-galaxy:agent-memory-galaxy
```

This points at the public framework repository. Keep real memory fragments in a private fork or private deployment.

## Quick Start Without the Skill

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
python3 collect.py --local-only --machine my-laptop --tool codex --roots "$HOME" --out fragments/my-laptop.json
python3 collect.py --merge
python3 build_artifact.py --out standalone.html --standalone
```

Open `standalone.html` locally. It contains plaintext memory data, so it is gitignored by default.

## What This Does

```text
local logs        native sessions       remote machines
agent_memory.md   Claude/Codex/Cursor   fragments/*.json
      \                 |                    /
       \                |                   /
        collect.py + distill.py + merge fragments
                         |
                    graph.json
                         |
       local standalone viewer or encrypted Pages viewer
```

Core pieces:

- `collect.py` scans local and remote sources and normalizes them into `graph.json`.
- `distill.py` fills gaps from native agent-session metadata without copying raw conversation text.
- `fragments/*.json` lets many machines contribute to one private hub.
- `presence/*.json` lights up currently active agents in the viewer.
- `viewer/index.html` is the runtime galaxy viewer.
- `docs/index.html` is the public marketing page.
- `docs/demo/` contains a fully synthetic public demo.
- `docs/galaxy/` is reserved for your optional encrypted private viewer.

## Privacy Model

Agent Memory Galaxy is privacy-first, not privacy-magic.

By default, full plaintext artifacts such as `graph.json` and `standalone.html` stay local and are gitignored. Multi-machine fragments should live only in a private repository. If you publish a web viewer, publish ciphertext only and decrypt in the browser with strong passwords.

Do not store secrets, credentials, private keys, raw confidential conversations, or unrevised sensitive code in memory files. Session distillation is intended to extract structured metadata only, but you should review configuration and generated artifacts before sharing. Client-side encryption reduces exposure, but public ciphertext can still be downloaded and attacked offline.

Public distribution rule of thumb:

- Public repo: framework code, docs, skill package, synthetic demo data.
- Private repo/fork: real `fragments/*.json`, `presence/*.json`, `graph.json`, `standalone.html`.
- Optional Pages viewer: `docs/galaxy/index.html` plus encrypted `docs/galaxy/graph.enc.json`.

This public template ignores real fragments, live presence, and encrypted graph snapshots by default. In a private hub where you intentionally want Git to sync those files, use:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

## Public Pages vs Private Galaxy

This repo intentionally separates the promotional page from the runtime memory viewer:

| Path | Purpose | Data policy |
|---|---|---|
| `docs/index.html` | Public GitHub Pages landing page | No real data, no password prompt |
| `docs/demo/index.html` | Synthetic demo viewer | Fake graph only |
| `viewer/index.html` | Source runtime viewer | Reads local `graph.json` or `graph.enc.json` |
| `docs/galaxy/index.html` | Optional encrypted deployed viewer | Should serve ciphertext only |
| `standalone.html` | Local plaintext single-file viewer | Gitignored |

## Contributor vs Aggregator

Two roles keep multi-machine sync simple:

- Contributor machine: runs `./contribute.sh <machine> <claude|codex|cursor|human> [roots]`, writes `fragments/<machine>.json`, and pushes to the private hub.
- Aggregator machine: runs `./update.sh [--pull]`, merges all fragments, injects live presence, optionally encrypts for Pages, and rebuilds the local standalone viewer.

Contributors do not need encryption passwords and should not touch `docs/galaxy/`.

## Data Model

Nodes include `project`, `entry`, `fact`, `agent`, `liveagent`, `machine`, `dataset`, `server`, `model`, `method`, `file`, `wandb`, `tech`, and `notion`.

Edges include `in`, `did`, `located`, `uses`, `touches`, `trains`, `tracks`, `syncs`, `explores`, `references`, `working_on`, `link`, and `on`.

Shared entities automatically connect projects across machines. For example, two different agents touching the same dataset, file, model, or Notion page will become connected in the graph.

## Public Demo

Build the synthetic demo with:

```bash
python3 scripts/build-public-demo.py
```

Then open:

```text
docs/demo/index.html
```

The demo graph is fully fictional. It should be safe to publish and is separate from `fragments/` so it cannot mix with real memory data.

## Requirements

- Python 3.8+ for collection, distillation, demo generation, and artifact building.
- Git for multi-machine sync.
- `cryptography` only if you enable encrypted Pages publishing with `encrypt.py`.
- No frontend build step is required. The viewer is static HTML/CSS/JS.

## License

MIT.
