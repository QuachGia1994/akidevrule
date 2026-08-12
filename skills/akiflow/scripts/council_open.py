#!/usr/bin/env python3
# akiflow — open a council session directory, and prune stale ones on the way in.
#
# Usage:  council_open.py <slug> <owner-message>        ('-' reads the message from stdin)
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


def convene(session_dir: Path) -> int:
    """Gate the spawn batch on a real decomposition. The anchor is pinned at open time (R1 needs it
    before the ledger can quote it), so the checklist cannot gate file creation — it gates convening,
    which is where 'N agents circling an uncut question' actually costs money."""
    checklist = session_dir / "checklist.md"
    if not checklist.is_file():
        print(f"council_open.py --convene: no checklist.md in {session_dir}", file=sys.stderr)
        return 1

    text = re.sub(r"<!--.*?-->", "", checklist.read_text(encoding="utf-8", errors="replace"), flags=re.DOTALL)

    # An item's three fields may sit on the ITEM line itself (pipe form) or on the lines under it
    # (block form); both are in real use, so the scope is the ITEM line up to the next ITEM/heading.
    blocks: list[str] = []
    for line in text.splitlines():
        if re.match(r"^[ \t]*ITEM[ \t]+\S", line):
            blocks.append(line)
        elif line.startswith("## "):
            blocks.append("")
        elif blocks:
            blocks[-1] += "\n" + line

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


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--convene":
        sys.exit(convene(Path(sys.argv[2])))

    root = Path(os.environ.get("AKI_COUNCIL_ROOT", Path.home() / ".aki" / "agent-council"))
    retention_days = int(os.environ.get("AKI_COUNCIL_RETENTION_DAYS", "30"))

    if len(sys.argv) < 3:
        print("usage: council_open.py <slug> <owner-message>   (use '-' to read the message from stdin)", file=sys.stderr)
        print("       the owner's message is verbatim and mandatory — a room with no anchor cannot be opened", file=sys.stderr)
        sys.exit(2)

    slug_in = sys.argv[1]
    anchor_in = sys.argv[2]

    if anchor_in == "-":
        anchor_in = sys.stdin.read()

    if not anchor_in.strip():
        print("council_open.py: the owner message is empty — nothing to anchor to", file=sys.stderr)
        sys.exit(2)

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_raw = Path(result.stdout.strip()).name
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
        checklist_md.write_bytes(
            f"""# checklist · {session}

## requirement ledger
<!-- Lead-owned, filled before decomposition. One line per distinct owner requirement, numbered REQ-1.. — compressed, never weakened.
     Each REQ carries a "quoted fragment" copied from chat.md's anchor block; that is what makes it a requirement rather than an interpretation.
     Every item below names the REQs it covers. An uncovered REQ is a decomposition bug, not a footnote. -->

## items
<!-- Lead-owned. Every item carries owner, challenger, closing criterion, the
     REQs it covers, and a <=3 line rationale written at closure. This file is
     what Phase B reads; the durable copy goes to docs/plan/ per RULE-docs.md B1. -->
""".encode("utf-8")
        )

    print(f"session: {session}")
    if pruned > 0:
        print(f"pruned: {pruned} stale session(s) older than {retention_days}d")
    print(str(session_dir))


if __name__ == "__main__":
    main()
