#!/usr/bin/env bash
# akiflow — mechanical closure gate over the room's own compliance artifacts.
#
# Usage:  council-verify.sh <session-dir>
#   <session-dir>  a council workspace holding chat.md + checklist.md
#
# Checks only what a script can check — the classes real runs lost silently:
#   1. anchor        — chat.md carries a non-empty '## anchor' block
#   2. REQ quotes    — every 'REQ-<n>' line in checklist.md quotes a fragment found in that anchor
#   3. ghost seats   — every owner/challenger named in checklist.md posted >=1 turn in chat.md
#   4. rule receipts — every posting agent emitted a '[RULES]' line, so a violation resolves to LOAD-fail or COMPLY-fail instead of a guess (agent.A5)
#   5. evidence tags — every posting agent used FACT/CONSTRAINT/ASSUMPTION at least once
#   6. reminders     — every REMIND-<n> has a later ACK or OVERRULE
#
# NOT checked, deliberately: the presence of any named seat. Roster composition is judgment; evidence is not. Reasoning: docs/research/akiflow-drift-diagnosis-aug6.md (root R2).
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

# Everything between '## anchor' and the next '## ', minus the HTML comment, so an unfilled template reads empty.
anchor="$(awk '
  /^## anchor/ { inblock = 1; next }
  /^## /       { inblock = 0 }
  inblock      { print }
' "$chat" | sed -e 's/<!--.*-->//' -e '/<!--/,/-->/d')"

# --- 1. anchor block -----------------------------------------------------
if [ -n "$(printf '%s' "$anchor" | tr -d '[:space:]')" ]; then
  say "PASS anchor: the owner's verbatim message is pinned"
else
  say "FAIL anchor: chat.md has no non-empty '## anchor' block — the room has nothing to be measured against"
  fail=1
fi

# --- 2. every REQ quotes the anchor --------------------------------------
unquoted=""
unfound=""
while IFS= read -r line; do
  [ -n "$line" ] || continue
  id="$(printf '%s' "$line" | grep -oE 'REQ-[0-9]+' | head -1)"
  frag="$(printf '%s' "$line" | sed -nE 's/^[^"]*"([^"]+)".*$/\1/p')"
  if [ -z "$frag" ]; then
    unquoted="$unquoted $id"
  elif ! printf '%s' "$anchor" | grep -qF -- "$frag"; then
    unfound="$unfound $id"
  fi
done < <(grep -E '^[[:space:]]*[-*]?[[:space:]]*REQ-[0-9]+' "$checklist" 2>/dev/null || true)
if [ -n "$unquoted" ] || [ -n "$unfound" ]; then
  [ -n "$unquoted" ] && say "FAIL req-quotes: no \"quoted fragment\" on:$unquoted"
  [ -n "$unfound" ]  && say "FAIL req-quotes: quoted text not found in the anchor block:$unfound"
  fail=1
else
  say "PASS req-quotes: every REQ quotes the owner's own words"
fi

# --- 3. ghost seats ------------------------------------------------------
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

# --- 4. rule receipts per posting agent ----------------------------------
noreceipt=""
for name in $posters; do
  n="$(awk -v who="$name" '
    /^### / { keep = ($3 == who) }
    keep && /\[RULES\]/ { n++ }
    END { print n + 0 }
  ' "$chat")"
  [ "$n" -eq 0 ] && noreceipt="$noreceipt $name"
done
if [ -n "$noreceipt" ]; then
  say "FAIL rule-receipts: no [RULES] line anywhere in turns by:$noreceipt"
  fail=1
else
  say "PASS rule-receipts: every posting agent reported what it loaded"
fi

# --- 5. evidence tags per posting agent ----------------------------------
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
