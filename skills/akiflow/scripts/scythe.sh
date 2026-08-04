#!/usr/bin/env bash
# scythe.sh — mechanical lint for the greppable penalty-card classes (RULE-agent-behavior.md §0).
# Detects [WRAP] (hard-wrapped code comments / markdown prose) and [YAP] (oversize comments — flagged "review", never a verdict).
# [FLUFF] (density) is content judgment and deliberately out of scope for a script.
# Usage: scythe.sh <file|dir> [...]     A dir expands to its git-tracked files; outside a repo, to find(1).
# Output: [TAG] path:line[-line] | short label      Exit: 0 clean · 1 findings · 2 usage error.
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: scythe.sh <file|dir> [...]" >&2; exit 2; }

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
MD_AWK='
function blockish(l) { return (l ~ /^[ \t]*$/ || l ~ /^#/ || l ~ /^[ \t]*\|/ || l ~ /^>/ || l ~ /^</ || l ~ /^[ \t]{4}/ || l ~ /^[ \t]*(---+|\*\*\*+|___+)[ \t]*$/) }
function listitem(l) { return (l ~ /^[ \t]*([-*+]|[0-9]+[.)]|[a-z][.)])[ \t]/) }
NR == 1 && /^---[ \t]*$/ { front = 1; next }
front { if ($0 ~ /^---[ \t]*$/) front = 0; next }
/^[ \t]*(```|~~~)/ { fence = !fence; next }
fence { next }
{
  if (prevset && !blockish(prev) && !blockish($0) && !listitem($0) && prev !~ /([.!?:;…→]|-->)[)"'"'"'\]*_`]*[ \t]*$/ && prev !~ /  $/)
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

found=0
for f in "${files[@]}"; do
  out=$(lint_file "$f")
  [ -n "$out" ] && { printf '%s\n' "$out"; found=1; }
done
exit $found
