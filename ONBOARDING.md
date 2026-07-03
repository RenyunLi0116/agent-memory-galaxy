# Onboarding

Agent Memory Galaxy has two roles:

- **Contributor**: a machine that collects its local agent memory and pushes a fragment to a private hub.
- **Aggregator**: the machine/repo that merges all fragments into one graph and optionally publishes an encrypted viewer.

Use a private repository or private fork for real memory data. Use this public repository only for framework code, docs, plugin packaging, and synthetic demo data.

## 1. Create a Private Hub

```bash
git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git my-memory-hub
cd my-memory-hub
git remote set-url origin git@github.com:RenyunLi0116/<private-hub>.git
```

Keep the private hub private if it will store real fragments.

## 2. Connect a Contributor Machine

From the private hub checkout:

```bash
./contribute.sh <unique-machine-name> <claude|codex|cursor|human> [scan-root]
```

Examples:

```bash
./contribute.sh laptop-a codex ~/projects
./contribute.sh workstation-b claude ~/work
```

Contributor output goes to `fragments/`. These files are plaintext and should remain private.

## 3. Refresh the Aggregated Graph

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

## 4. Optional Encrypted Pages Viewer

Create two strong local password files:

```bash
printf '%s' 'first-strong-passphrase' > .amg_password
printf '%s' 'second-strong-passphrase' > .amg_password2
chmod 600 .amg_password .amg_password2
```

Then run:

```bash
./update.sh
```

The publishable output is:

```text
docs/galaxy/index.html
docs/galaxy/graph.enc.json
```

Do not publish plaintext `graph.json`.

## 5. Public Demo

The public demo is fully synthetic:

```bash
python3 scripts/build-public-demo.py
```

Open:

```text
docs/demo/index.html
```

Never generate public demos from real fragments.

## 6. Memory Notes

Add `agent_memory.md` to project roots:

```markdown
## 2026-07-03 - Short title (codex)
- What changed:
- Why:
- Status: doing | done
- Verification:
- Files:
```

Hand-written memory is the most accurate source. Native session distillation is a fallback for gaps and should extract structured metadata only.

## 7. Public Release Checklist

Before publishing:

```bash
git ls-files
rg -n "USERPROFILE|HOME_DIR|REAL_HOST|REAL_PROJECT|TOKEN|PASSWORD|SECRET|graph.enc|fragments/.*json|presence/.*json" .
```

Confirm no real memory artifacts are tracked.
