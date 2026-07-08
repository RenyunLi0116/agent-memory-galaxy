#!/usr/bin/env bash
# Install the pre-commit privacy guard for this PUBLIC repo.
# Idempotent. Safe to re-run. Token-free (real patterns go in the gitignored
# `.amg-privacy-denylist`, which this script only *templates*, never fills).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOK="$ROOT/.git/hooks/pre-commit"
DL="$ROOT/.amg-privacy-denylist"

cat > "$HOOK" <<'SH'
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/scripts/precommit-privacy-check.sh"
SH
chmod +x "$HOOK"
echo "[privacy-guard] installed $HOOK"

if [ ! -f "$DL" ]; then
  cat > "$DL" <<'TXT'
# Private-identifier denylist for the pre-commit privacy guard.
# One grep -E pattern per line. Lines starting with # are ignored.
# This file is gitignored — the denylist must NEVER be committed to the public repo.
# Fill in your real machine names / IP prefixes / internal project names, e.g.:
#   my-internal-host
#   10\.0\.0
#   secret-project-name
TXT
  echo "[privacy-guard] created template $DL — fill in your private patterns."
else
  echo "[privacy-guard] $DL already present — left untouched."
fi
