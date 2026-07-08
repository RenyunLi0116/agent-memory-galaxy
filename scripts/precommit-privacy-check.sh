#!/usr/bin/env bash
# Privacy guard for this PUBLIC repo.
# Blocks a commit whose staged files contain any private identifier
# (real machine names, IPs, internal project names, host paths, org names).
#
# The actual patterns live in an UNTRACKED, gitignored file `.amg-privacy-denylist`
# so the denylist itself never enters the public history (that leak is exactly
# what this guard prevents). This script is token-free by design.
#
# Enable once:  ./scripts/install-privacy-hook.sh
# Bypass (only if you are certain):  git commit --no-verify
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DL="$ROOT/.amg-privacy-denylist"

if [ ! -f "$DL" ]; then
  echo "[privacy-guard] no .amg-privacy-denylist found — guard inactive." >&2
  echo "[privacy-guard] create it (see scripts/install-privacy-hook.sh) to enable." >&2
  exit 0
fi

# One extended-regex pattern per line; ignore blanks and #comments.
PAT="$(grep -vE '^[[:space:]]*(#|$)' "$DL" | paste -sd'|' -)"
[ -n "$PAT" ] || exit 0

bad=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qiE "$PAT" "$f"; then
    n="$(grep -icE "$PAT" "$f")"
    echo "[privacy-guard] BLOCKED: $f has $n private-identifier match(es)" >&2
    bad=1
  fi
done < <(git diff --cached --name-only --diff-filter=ACM)

if [ "$bad" != 0 ]; then
  echo "[privacy-guard] Remove the private identifiers from the file(s) above" >&2
  echo "[privacy-guard] before committing to this public repo." >&2
  echo "[privacy-guard] (Intentional? re-run with: git commit --no-verify)" >&2
  exit 1
fi
exit 0
