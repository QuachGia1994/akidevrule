#!/usr/bin/env bash
# akiflow — mechanical closure gate over the room's own compliance artifacts.
#
# Usage:  council-verify.sh <session-dir>
#   <session-dir>  a council workspace holding chat.md + checklist.md
#
# Checks only what a script can check — the classes real runs lost silently:
#   1. ghost seats   — every owner/challenger named in checklist.md posted >=1 turn
#                      in chat.md (a run once closed items citing a Red Team that
#                      never posted a single turn)
#   2. enforcer seat — akirule-enforcer posted >=1 turn (standing seat, Tier 1/2)
#   3. evidence tags — every posting agent used FACT/CONSTRAINT/ASSUMPTION at least
#                      once (the floor clause whose silent omission let two
#                      contradictory inventories both close)
#   4. reminders     — every REMIND-<n> id has a later ACK REMIND-<n> or
#                      OVERRULE REMIND-<n> line
#
# Judgment stays with the lead: this gate proves presence, never quality.
# Exit 0 = all PASS. Exit 1 = at least one FAIL. The lead pastes the output into
# chat.md before closing items (SKILL.md Step 6) and again before the Step 9 tally.
set -euo pipefail

dir="${1:-}"
chat="$dir/chat.md"
checklist="$dir/checklist.md"
if [ -z "$dir" ] || [ ! -f "$chat" ] || [ ! -f "$checklist" ]; then
  echo "usage: council-verify.sh <session-dir>  (must contain chat.md + checklist.md)" >&2
  exit 2
fi

fail=0
say() { printf '%s\n' "$1"; }

# Agents that actually posted a turn ('### <time> <agent> #<n>' → field 3).
posters="$(grep '^### ' "$chat" 2>/dev/null | awk '{print $3}' | sort -u)"

# --- 1. ghost seats ------------------------------------------------------
declared="$(grep -Ei '^[[:space:]]*(owner|challenger):' "$checklist" 2>/dev/null \
  | sed -E 's/^[[:space:]]*(owner|challenger):[[:space:]]*//I; s/[[:space:]].*$//' \
  | grep -E '^[a-z0-9][a-z0-9-]*$' | sort -u || true)"
ghosts=""
for name in $declared; do
  printf '%s\n' "$posters" | grep -qx "$name" || ghosts="$ghosts $name"
done
if [ -n "$ghosts" ]; then
  say "FAIL ghost-seats: declared but never posted a turn:$ghosts"
  fail=1
else
  say "PASS ghost-seats: every declared owner/challenger posted"
fi

# --- 2. enforcer seat ----------------------------------------------------
if printf '%s\n' "$posters" | grep -qx "akirule-enforcer"; then
  say "PASS enforcer: akirule-enforcer posted"
else
  say "FAIL enforcer: akirule-enforcer has no turn in the room"
  fail=1
fi

# --- 3. evidence tags per posting agent ----------------------------------
untagged=""
for name in $posters; do
  tags="$(awk -v who="$name" '
    /^### / { keep = ($3 == who) }
    keep && /FACT|CONSTRAINT|ASSUMPTION/ { n++ }
    END { print n + 0 }
  ' "$chat")"
  [ "$tags" -eq 0 ] && untagged="$untagged $name"
done
if [ -n "$untagged" ]; then
  say "FAIL evidence-tags: no FACT/CONSTRAINT/ASSUMPTION in any turn by:$untagged"
  fail=1
else
  say "PASS evidence-tags: every posting agent tagged evidence"
fi

# --- 4. unanswered reminders ---------------------------------------------
open_reminds=""
for id in $(grep -oE 'REMIND-[0-9]+' "$chat" 2>/dev/null | sort -u); do
  grep -qE "(ACK|OVERRULE) $id\b" "$chat" || open_reminds="$open_reminds $id"
done
if [ -n "$open_reminds" ]; then
  say "FAIL reminders: no ACK/OVERRULE for:$open_reminds"
  fail=1
else
  say "PASS reminders: every REMIND answered (or none issued)"
fi

exit "$fail"
