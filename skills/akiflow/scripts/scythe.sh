#!/usr/bin/env bash
# scythe.sh — mechanical lint for the greppable penalty-card classes (RULE-agent-behavior.md §0).
# Detects [WRAP] (hard-wrapped code comments / markdown prose) and [YAP] (oversize comments — flagged "review", never a verdict).
# [FLUFF] (density) is content judgment and deliberately out of scope for a script.
# Usage: scythe.sh [--all] <file|dir> [...]   A dir expands to its git-tracked files; outside a repo, to find(1).
# Output: [TAG] path:line[-line] | short label      Exit: 0 clean · 1 findings · 2 usage error.
# Past 40 findings (SCYTHE_CAP) output becomes a capped list plus per-tag and per-file counts; --all prints everything.
set -euo pipefail

SHOW_ALL=0
CAP=${SCYTHE_CAP:-40}
args=()
for a in "$@"; do
  case "$a" in
    --all) SHOW_ALL=1;;
    *) args+=("$a");;
  esac
done
set -- "${args[@]}"

[ $# -ge 1 ] || { echo "usage: scythe.sh [--all] <file|dir> [...]" >&2; exit 2; }

# Comment runs are classified whole: a 2-line run whose 2nd line reads as a lowercase continuation is a wrap;
# a >=3-line run or a >200-char line is flagged for judgment. The file's leading comment block (license/header)
# and directive/tag lines (@param, eslint-, shellcheck, shebang, ...) are exempt — they are structure, not prose.
CODE_AWK='
function flush() {
  if (rs == 0) return
  if (header) { rs = 0; return }
  if (rs >= 3) printf "[YAP] %s:%d-%d | %d-line comment block (review)\n", FILENAME, rstart, rstart + rs - 1, rs
  else if (rs == 2 && cont) printf "[WRAP] %s:%d-%d | wrapped comment (rejoin)\n", FILENAME, rstart, rstart + 1
  rs = 0
}
BEGIN { header = 1; rs = 0 }
{
  if (match($0, "^[ \t]*(" MARKER ")[ \t]*")) {
    text = substr($0, RSTART + RLENGTH)
    if (text == "" || text ~ /^(@|!|#|eslint|prettier|biome|ts-|type:|noqa|pylint|ruff|shellcheck|fmt:|region|endregion|-{3,}|={3,}|\*)/) { flush(); next }
    if (rs == 0) { rstart = NR; cont = 0 }
    rs++
    if (rs > 1 && text ~ /^[a-z]/) cont = 1
    if (length($0) > 200 && !header) printf "[YAP] %s:%d | comment %d chars (review)\n", FILENAME, NR, length($0)
    next
  }
  flush()
  if ($0 !~ /^[ \t]*$/) header = 0
}
END { flush() }
'

# A prose line ending without terminal punctuation, followed by another plain prose line, is a split sentence.
# Structure is exempt: frontmatter, fences, headings, tables, blockquotes, HTML, rules, indented code, blank lines.
# A following list item is a new logical line, never a continuation.
# Two adjacent lines carrying the SAME directive marker are a machine-parsed run (@import block, link/badge list,
# metadata header) — never wrapped prose, which does not repeat a marker. Rejoining one would corrupt what parses it.
MD_AWK='
function blockish(l) { return (l ~ /^[ \t]*$/ || l ~ /^#/ || l ~ /^[ \t]*\|/ || l ~ /^>/ || l ~ /^</ || l ~ /^[ \t]{4}/ || l ~ /^[ \t]*(---+|\*\*\*+|___+)[ \t]*$/) }
function listitem(l) { return (l ~ /^[ \t]*([-*+]|[0-9]+[.)]|[a-z][.)])[ \t]/) }
function sig(l) { gsub(/^[ \t]+/, "", l); if (l ~ /^@/) return "@"; if (l ~ /^\[/) return "bracket"; if (l ~ /^\**[A-Za-z_][A-Za-z0-9_ -]*\**:([ \t]|$)/) return "keyline"; return "" }
NR == 1 && /^---[ \t]*$/ { front = 1; next }
front { if ($0 ~ /^---[ \t]*$/) front = 0; next }
/^[ \t]*(```|~~~)/ { fence = !fence; next }
fence { next }
{
  if (prevset && !blockish(prev) && !blockish($0) && !listitem($0) && prev !~ /([.!?:;…→]|-->)[)"'"'"'\]*_`]*[ \t]*$/ && prev !~ /  $/ && !(sig(prev) != "" && sig(prev) == sig($0)))
    printf "[WRAP] %s:%d-%d | wrapped prose (rejoin)\n", FILENAME, NR - 1, NR
  prev = $0; prevset = 1
}
'

SLASH_EXT='ts|tsx|js|jsx|mjs|rs|go|c|h|cc|cpp|swift|kt|scss'
HASH_EXT='sh|bash|py|rb|toml|yaml|yml'

lint_file() {
  local f=$1 ext=${1##*.}
  case "$f" in *.md|*.mdx) awk "$MD_AWK" "$f"; return;; esac
  if [[ "$ext" =~ ^($SLASH_EXT)$ ]]; then awk -v MARKER='//' "$CODE_AWK" "$f"
  elif [[ "$ext" =~ ^($HASH_EXT)$ ]]; then awk -v MARKER='#' "$CODE_AWK" "$f"
  elif [[ "$ext" == vue || "$ext" == html ]]; then awk -v MARKER='//|<!--' "$CODE_AWK" "$f"
  fi
}

files=()
for target in "$@"; do
  if [ -f "$target" ]; then files+=("$target")
  elif [ -d "$target" ]; then
    if git -C "$target" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      while IFS= read -r f; do [ -f "${target%/}/$f" ] && files+=("${target%/}/$f"); done < <(git -C "$target" ls-files)
    else
      while IFS= read -r f; do files+=("$f"); done < <(find "$target" -type f)
    fi
  else echo "scythe: no such path: $target" >&2; exit 2; fi
done

all=""
for f in "${files[@]}"; do
  out=$(lint_file "$f")
  [ -n "$out" ] && all+="$out"$'\n'
done

[ -z "$all" ] && exit 0
all=${all%$'\n'}
total=$(printf '%s\n' "$all" | wc -l)

# A whole-repo sweep can produce thousands of findings. Printing them all buries the caller and, for an
# agent caller, parks the whole dump in a context every later turn re-sends. Past the cap, lead with counts.
if [ "$SHOW_ALL" = 0 ] && [ "$total" -gt "$CAP" ]; then
  printf '%s\n' "$all" | awk -v n="$CAP" 'NR <= n'
  echo "--- $((total - CAP)) more findings suppressed ---"
  printf '%s\n' "$all" | awk '{ c[$1]++ } END { for (t in c) printf "%s %s  ", t, c[t] }'
  echo "(total $total)"
  echo "worst files:"
  printf '%s\n' "$all" | awk '{ sub(/:[0-9].*/, "", $2); c[$2]++ } END { for (f in c) printf "%6d  %s\n", c[f], f }' | sort -rn | awk 'NR <= 5'
  echo "Narrow the path, or pass --all for every finding."
else
  printf '%s\n' "$all"
fi
exit 1
exit $found
