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

## 4. Connect Contributor Machines

From the private hub checkout on each contributor machine:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh <unique-machine-name> <claude|codex|cursor|human> <project-root>
```

Examples:

```bash
AMG_PRIVATE_HUB=1 ./contribute.sh laptop-a codex ~/projects/my-app
AMG_PRIVATE_HUB=1 ./contribute.sh workstation-b claude ~/work/active-project
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

The public template intentionally does not stage real fragments, live presence, or encrypted graph snapshots during `update.sh`. In your private hub, opt in when you want Git to sync private memory artifacts:

```bash
AMG_TRACK_PRIVATE=1 ./update.sh
```

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
