#!/usr/bin/env python3
# akiflow — open a council session directory, and prune stale ones on the way in.
#
# Usage:  council_open.py <slug> <owner-message>        ('-' reads the message from stdin)
#         council_open.py --dispatch <slug> <owner-message>   same args, checklist seeded lane-shaped not item-shaped
#         council_open.py --convene <session-dir>       exit 1 unless the checklist is actually cut
#   <slug>           short, human-readable, covers the whole session. Slugified here, not validated.
#   <owner-message>  the owner's request VERBATIM — pinned as chat.md's first block; every REQ must quote a fragment of it. Why it is an argument and not a discipline: docs/research/akiflow-drift-diagnosis-aug6.md (root R1).
#
# Prints the session directory path on stdout (last line is always the path,
# so `dir=$(council_open.py foo | tail -1)` is safe).
#
# Env overrides:
#   AKI_COUNCIL_ROOT            default ~/.aki/agent-council
#   AKI_COUNCIL_RETENTION_DAYS  default 30 — same window Claude Code uses to
#                               clean ~/.claude/projects, so the two age out together.
import sys
import os
import re
import subprocess
import time
import shutil
from pathlib import Path
from datetime import datetime


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def rule_stamp() -> str:
    """Which akidevrule the room ran under, from the installed copy: version per CHANGELOG (release.A3 SSoT), commit per .version."""
    root = Path(os.environ.get("AKI_RULE_ROOT", Path.home() / ".aki" / "akidevrule"))
    version = "?"
    try:
        for line in (root / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"^## \[(\d[^\]]*)\]", line)
            if match:
                version = match.group(1)
                break
    except OSError:
        pass
    commit = ""
    try:
        for line in (root / ".version").read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("commit="):
                commit = "@" + line.split("=", 1)[1].strip()
                break
    except OSError:
        pass
    return f"akidevrule {version}{commit}"


def read_mode(session_dir: Path) -> str:
    """Mode is read from chat.md's stamp line, written once at open; no match — pre-dispatch room or malformed file — reads as council, never a crash."""
    try:
        lines = (session_dir / "chat.md").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "council"
    if len(lines) < 2:
        return "council"
    match = re.search(r"mode[ \t]+(\S+)", lines[1])
    return match.group(1).rstrip("`") if match else "council"


ITEM_TRIGGER = re.compile(r"^[ \t]*ITEM[ \t]+\S")
# LANE's heading may carry the seeded markdown '#'s or not — either opens a new block.
LANE_TRIGGER = re.compile(r"^[ \t]*(#{1,6}[ \t]+)?LANE[ \t]+\S")


def _scan_blocks(text: str, trigger: re.Pattern) -> list[str]:
    """Group lines into blocks starting at each `trigger` match, closed by the next trigger or the next '## ' heading — the one tolerance the ITEM and LANE gates share, only the trigger regex differs."""
    blocks: list[str] = []
    for line in text.splitlines():
        if trigger.match(line):
            blocks.append(line)
        elif line.startswith("## "):
            blocks.append("")
        elif blocks:
            blocks[-1] += "\n" + line
    return blocks


def _convene_council(text: str) -> int:
    blocks = _scan_blocks(text, ITEM_TRIGGER)

    complete = sum(
        1 for b in blocks
        if all(re.search(rf"{f}[ \t]*:?[ \t]*\S", b, re.IGNORECASE) for f in ("owner", "challenger", "closes"))
    )

    if complete == 0:
        print("FAIL convene: checklist.md has no ITEM carrying all of owner / challenger / closes when.", file=sys.stderr)
        print("       Decomposition is a precondition for the room, never a product of it — cut the items, then convene.", file=sys.stderr)
        return 1
    print(f"PASS convene: {complete} item(s) fully specified — roster may be spawned")
    return 0


def _lane_name(block: str) -> str:
    """The LANE heading line with leading '#'/whitespace stripped — the identifier a writes: collision message names."""
    return re.sub(r"^[ \t]*#*[ \t]*", "", block.splitlines()[0]).strip() if block else ""


def _field_paths(block: str, field: str) -> list[str]:
    """Comma-separated tokens after a `field:` label — the same list shape checklist.md already
    uses for REQ runs. Anchored to the seed's own line shape (start of line, optional bullet,
    mandatory colon) so prose mentioning the field name (e.g. 'rewrites' containing 'writes')
    is never mistaken for a declaration."""
    match = re.search(rf"(?m)^[ \t]*(?:[-*][ \t]+)?{field}[ \t]*:[ \t]*(\S.*)", block, re.IGNORECASE)
    return [p.strip() for p in match.group(1).split(",") if p.strip()] if match else []


def _normalize_write_token(token: str) -> tuple[str, bool]:
    """Strip a trailing /** or /* into a directory prefix; a plain token is its own literal.
    Single-* basename globs (scripts/*.py) are deliberately kept as literal tokens — full glob
    matching is out of scope, and the one false PASS this leaves is mixing such a pattern with
    a literal path in the same directory."""
    for suffix in ("/**", "/*"):
        if token.endswith(suffix):
            return token[: -len(suffix)], True
    return token, False


def _path_has_prefix(prefix: str, path: str) -> bool:
    """path == prefix, or prefix is a '/'-boundary-respecting ancestor of path — so 'docs'
    does not swallow 'docs-old'."""
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


def _writes_collide(a: str, b: str) -> bool:
    """Two writes: tokens collide when literally equal, or when either side's /** or /*
    prefix contains the other token (or the other's own prefix) — cheap prefix-aware overlap,
    no glob engine."""
    val_a, is_prefix_a = _normalize_write_token(a)
    val_b, is_prefix_b = _normalize_write_token(b)
    if val_a == val_b:
        return True
    if is_prefix_a and _path_has_prefix(val_a, val_b):
        return True
    if is_prefix_b and _path_has_prefix(val_b, val_a):
        return True
    return False


def _convene_dispatch(text: str) -> int:
    blocks = _scan_blocks(text, LANE_TRIGGER)

    claims: list[tuple[str, str]] = []  # (writes: token, lane name)
    for block in blocks:
        name = _lane_name(block)
        for path in _field_paths(block, "writes"):
            for other_path, other_name in claims:
                if other_name != name and _writes_collide(path, other_path):
                    print(f"FAIL convene: writes: '{other_path}' ({other_name}) overlaps '{path}' ({name}) — must be exclusive to one lane.", file=sys.stderr)
                    print("       Two lanes writing overlapping paths is the exact hazard dispatch exists to prevent — repartition writes: before convening.", file=sys.stderr)
                    return 1
            claims.append((path, name))

    complete = sum(
        1 for b in blocks
        if all(re.search(rf"(?m)^[ \t]*(?:[-*][ \t]+)?{f}[ \t]*:[ \t]*\S", b, re.IGNORECASE) for f in ("covers", "worker", "writes", "returns"))
    )

    if complete == 0:
        print("FAIL convene: checklist.md has no LANE carrying all of covers / worker / writes / returns.", file=sys.stderr)
        print("       Decomposition is a precondition for the room, never a product of it — cut the lanes, then convene.", file=sys.stderr)
        return 1
    print(f"PASS convene: {complete} lane(s) fully specified, no writes: overlap — roster may be spawned")
    return 0


def convene(session_dir: Path) -> int:
    """Gate the spawn batch on a real decomposition. The anchor is pinned at open time (R1 needs it
    before the ledger can quote it), so the checklist cannot gate file creation — it gates convening,
    which is where 'N agents circling an uncut question' actually costs money."""
    checklist = session_dir / "checklist.md"
    if not checklist.is_file():
        print(f"council_open.py --convene: no checklist.md in {session_dir}", file=sys.stderr)
        return 1

    text = re.sub(r"<!--.*?-->", "", checklist.read_text(encoding="utf-8", errors="replace"), flags=re.DOTALL)

    if read_mode(session_dir) == "dispatch":
        return _convene_dispatch(text)
    return _convene_council(text)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--convene":
        sys.exit(convene(Path(sys.argv[2])))

    root = Path(os.environ.get("AKI_COUNCIL_ROOT", Path.home() / ".aki" / "agent-council"))
    retention_days = int(os.environ.get("AKI_COUNCIL_RETENTION_DAYS", "30"))

    args = sys.argv[1:]
    mode = "council"
    if args and args[0] == "--dispatch":
        mode = "dispatch"
        args = args[1:]

    if len(args) < 2:
        print("usage: council_open.py [--dispatch] <slug> <owner-message>   (use '-' to read the message from stdin)", file=sys.stderr)
        print("       the owner's message is verbatim and mandatory — a room with no anchor cannot be opened", file=sys.stderr)
        sys.exit(2)

    slug_in = args[0]
    anchor_in = args[1]

    if anchor_in == "-":
        anchor_in = sys.stdin.read()

    if not anchor_in.strip():
        print("council_open.py: the owner message is empty — nothing to anchor to", file=sys.stderr)
        sys.exit(2)

    head = ""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_raw = Path(result.stdout.strip()).name
        head = "@" + subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        project_raw = Path.cwd().name

    project = slugify(project_raw)
    slug = slugify(slug_in)
    stamp = datetime.now().strftime("%Y.%m.%d-%H%M")
    session = f"{stamp}-{slug}"
    session_dir = root / project / session

    # --- prune first ---------------------------------------------------------
    pruned = 0
    if root.exists():
        cutoff_time = time.time() - (retention_days * 86400)
        for proj_dir in root.iterdir():
            if not proj_dir.is_dir():
                continue
            for old in proj_dir.iterdir():
                if not old.is_dir():
                    continue
                if old.stat().st_mtime < cutoff_time:
                    shutil.rmtree(old)
                    pruned += 1
            if proj_dir.is_dir() and not any(proj_dir.iterdir()):
                proj_dir.rmdir()

    # --- seed ----------------------------------------------------------------
    session_dir.mkdir(parents=True, exist_ok=True)

    chat_md = session_dir / "chat.md"
    if not chat_md.exists():
        chat_md.write_bytes(
            f"""# council · {session}
`{rule_stamp()} · {project}{head} · claude-session {os.environ.get("CLAUDE_CODE_SESSION_ID") or "n/a"} · mode {mode}`
<!-- Written once at open, never updated: what this room ran under, not what is current. The session id is the harness transcript's filename, so close-out accounting reads one known file instead of guessing. -->

## anchor
<!-- The owner's message, verbatim. IMMUTABLE: never edited, never paraphrased, never replaced by the lead's restatement. Every REQ in checklist.md quotes a fragment of the text below. -->

{anchor_in}

## pinned

PROBLEM   — (lead: one paragraph, what was actually asked. This is a working restatement and it is NOT the anchor; where the two disagree, the anchor above wins and the restatement is the thing that is wrong)
CONTEXT   — (lead: what a specialist must know that it cannot read from the repo)
GOAL      — (lead: what "done" looks like for the whole session)
ROSTER    — (lead: every agent name, what it owns, and its turn-number block)

<!-- Lead appends CHECKPOINT lines here when the room drifts or gets expensive.
     Everything below this block is the room itself, one turn per '### ' header. -->
""".encode("utf-8")
        )

    checklist_md = session_dir / "checklist.md"
    if not checklist_md.exists():
        ledger = """## requirement ledger
<!-- Lead-owned, filled before decomposition. One line per distinct owner requirement, numbered REQ-1.. — compressed, never weakened.
     Each REQ carries a "quoted fragment" copied from chat.md's anchor block; that is what makes it a requirement rather than an interpretation.
     Every item below names the REQs it covers. An uncovered REQ is a decomposition bug, not a footnote. -->
"""
        if mode == "dispatch":
            work = """## lanes
<!-- Lead-owned. `writes:` is exclusive to its lane — a path named in two lanes' writes: is a gate failure, not a style nit.
     Every REQ above must be covered by some lane.
     `returns:` exists because the lead merges the lanes at the end and cannot merge a shape no lane ever specified.

### LANE 1 · <short name>
- covers: REQ-1, REQ-2
- worker: <agent-type> (<tier>)
- writes: <exact file paths this lane may write — exclusive to it>
- reads: <paths and rule files named in its brief>
- returns: <the exact shape the lead will merge>
-->
"""
        else:
            work = """## items
<!-- Lead-owned. Every item carries owner, challenger, closing criterion, the
     REQs it covers, and a <=3 line rationale written at closure. This file is
     what Phase B reads; the durable copy goes to docs/plan/ per RULE-docs.md B1. -->
"""
        checklist_md.write_bytes(f"# checklist · {session}\n\n{ledger}\n{work}".encode("utf-8"))

    print(f"session: {session}")
    if pruned > 0:
        print(f"pruned: {pruned} stale session(s) older than {retention_days}d")
    print(str(session_dir))


if __name__ == "__main__":
    main()
