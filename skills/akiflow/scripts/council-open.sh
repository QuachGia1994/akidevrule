#!/usr/bin/env bash
# akiflow — open a council session directory, and prune stale ones on the way in.
#
# Usage:  council-open.sh <slug>
#   <slug>  short, human-readable, covers the whole session's problem.
#           The lead picks it. It is slugified here, not validated.
#
# Prints the session directory path on stdout (last line is always the path,
# so `dir=$(council-open.sh foo | tail -1)` is safe).
#
# Env overrides:
#   AKI_COUNCIL_ROOT            default ~/.aki/agent-council
#   AKI_COUNCIL_RETENTION_DAYS  default 30 — same window Claude Code uses to
#                               clean ~/.claude/projects, so the two age out together.
set -euo pipefail

ROOT="${AKI_COUNCIL_ROOT:-$HOME/.aki/agent-council}"
RETENTION_DAYS="${AKI_COUNCIL_RETENTION_DAYS:-30}"

slug_in="${1:-}"
if [ -z "$slug_in" ]; then
  echo "usage: council-open.sh <slug>" >&2
  exit 2
fi

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/[^a-z0-9]\{1,\}/-/g' -e 's/^-//' -e 's/-$//'
}

project_raw="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
project="$(slugify "$project_raw")"
slug="$(slugify "$slug_in")"
stamp="$(date +%Y.%m.%d-%H%M)"
session="$stamp-$slug"
dir="$ROOT/$project/$session"

# --- prune first ---------------------------------------------------------
# Only session directories (depth 2: <project>/<session>) are eligible, so a
# stray file at the root is never removed. Durable output lives in the repo's
# docs/ and is never touched by this script.
pruned=0
if [ -d "$ROOT" ]; then
  while IFS= read -r old; do
    [ -n "$old" ] || continue
    rm -rf "$old"
    pruned=$((pruned + 1))
  done < <(find "$ROOT" -mindepth 2 -maxdepth 2 -type d -mtime "+$RETENTION_DAYS" 2>/dev/null || true)
  find "$ROOT" -mindepth 1 -maxdepth 1 -type d -empty -delete 2>/dev/null || true
fi

# --- seed ----------------------------------------------------------------
mkdir -p "$dir"

if [ ! -f "$dir/chat.md" ]; then
  cat > "$dir/chat.md" <<EOF
# council · $session

## pinned

PROBLEM   — (lead: one paragraph, what was actually asked)
CONTEXT   — (lead: what a specialist must know that it cannot read from the repo)
GOAL      — (lead: what "done" looks like for the whole session)
ROSTER    — (lead: every agent name, what it owns, and its turn-number block)

<!-- Lead appends CHECKPOINT lines here when the room drifts or gets expensive.
     Everything below this block is the room itself, one turn per '### ' header. -->
EOF
fi

if [ ! -f "$dir/checklist.md" ]; then
  cat > "$dir/checklist.md" <<EOF
# checklist · $session

## requirement ledger
<!-- Lead-owned, filled before decomposition (Step 0). One line per distinct
     owner requirement, numbered REQ-1.. — compressed, never weakened. Every
     item below must name the REQs it covers; an uncovered REQ is a
     decomposition bug, not a footnote. -->

## items
<!-- Lead-owned. Every item carries owner, challenger, closing criterion, the
     REQs it covers, and a <=3 line rationale written at closure. This file is
     what Phase B reads; the durable copy goes to docs/plan/ per RULE-docs.md B1. -->
EOF
fi

echo "session: $session"
if [ "$pruned" -gt 0 ]; then
  echo "pruned: $pruned stale session(s) older than ${RETENTION_DAYS}d"
fi
echo "$dir"
