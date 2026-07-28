#!/usr/bin/env bash
# akiflow — read chat.md without pulling the whole room into the lead's context.
#
# The room is a live meeting, read in time order like a human would. This script
# exists so that "in time order" does not have to mean "all of it, every time".
#
# Usage:  council-read.sh <chat.md> [options]
#   --index           list turn headers only (time, agent, turn no.)
#   --pinned          print the pinned header block only
#   --stats           turns per agent — the lead's drift/cost signal
#   --agent <name>    only turns by this agent
#   --from <n>        only turns numbered >= n
#   --tail <n>        only the last n matching turns
# Options combine; --index/--pinned/--stats are exclusive modes.
set -euo pipefail

file="${1:-}"
if [ -z "$file" ] || [ ! -f "$file" ]; then
  echo "usage: council-read.sh <chat.md> [--index|--pinned|--stats] [--agent N] [--from N] [--tail N]" >&2
  exit 2
fi
shift

mode="blocks"; agent=""; from=""; tail_n=""
while [ $# -gt 0 ]; do
  case "$1" in
    --index)  mode="index" ;;
    --pinned) mode="pinned" ;;
    --stats)  mode="stats" ;;
    --agent)  agent="${2:-}"; shift ;;
    --from)   from="${2:-}"; shift ;;
    --tail)   tail_n="${2:-}"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$mode" in
  index)
    grep -n '^### ' "$file" || true
    ;;
  pinned)
    awk '/^### /{exit} {print}' "$file"
    ;;
  stats)
    grep '^### ' "$file" 2>/dev/null | awk '{print $3}' | sort | uniq -c | sort -rn || true
    printf 'turns: %s\n' "$(grep -c '^### ' "$file" 2>/dev/null || echo 0)"
    ;;
  blocks)
    awk -v agent="$agent" -v from="$from" -v tail_n="$tail_n" '
      /^### / {
        keep = 1
        who = $3
        turn = $0; sub(/.*#/, "", turn); turn = turn + 0
        if (agent != "" && who != agent) keep = 0
        if (from  != "" && turn < from + 0) keep = 0
        if (keep) blocks[++nb] = ""
        if (keep) { blocks[nb] = blocks[nb] $0 "\n"; next }
      }
      { if (keep && nb > 0) blocks[nb] = blocks[nb] $0 "\n" }
      END {
        start = 1
        if (tail_n != "" && nb > tail_n + 0) start = nb - tail_n + 1
        for (i = start; i <= nb; i++) printf "%s", blocks[i]
      }
    ' "$file"
    ;;
esac
