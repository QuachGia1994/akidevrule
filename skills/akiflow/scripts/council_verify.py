#!/usr/bin/env python3
# council_verify.py — mechanical closure gate over the room's own compliance artifacts.
#
# Usage:  council_verify.py <session-dir>
#   <session-dir>  a council workspace holding chat.md + checklist.md
#
# Checks only what a script can check — the classes real runs lost silently:
#   1. anchor        — chat.md carries a non-empty '## anchor' block
#   2. REQ quotes    — every 'REQ-<n>' line in checklist.md quotes a fragment found in that anchor
#   3. ghost seats   — every owner/challenger named in checklist.md left a trace somewhere in the session
#   4. rule receipts — every seat emitted a '[RULES]' line
#   5. evidence tags — every seat used FACT/CONSTRAINT/ASSUMPTION at least once
#   6. reminders     — every REMIND-<n> has a later ACK or OVERRULE
#   7. REQ coverage  — every REQ-<n> in the ledger is named by some item's 'covers:' line
#
# A seat's evidence is its chat.md turns plus its own <seat>.md at any depth. Nothing to check prints SKIP, never PASS.
# NOT checked, deliberately: the presence of any named seat. Roster composition is judgment; evidence is not.
# Exit 0 = no FAIL. Exit 1 = at least one FAIL.

import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def _strip_comments(text: str) -> str:
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)


def _req_ids(text: str) -> list[str]:
    """REQ ids in first-seen order, expanding the compact run form `REQ-2,3` to REQ-2 and REQ-3."""
    ids: list[str] = []
    for run in re.findall(r'REQ-[0-9]+(?:[ \t]*,[ \t]*[0-9]+)*', _strip_comments(text)):
        for num in re.findall(r'[0-9]+', run):
            if f'REQ-{num}' not in ids:
                ids.append(f'REQ-{num}')
    return ids


def read_mode(chat: str) -> str:
    """Mode from chat.md's line-2 stamp, duplicating council_open.py::read_mode() — the scripts
    are deliberately standalone. No match (pre-dispatch room, malformed file) reads as council."""
    lines = chat.splitlines()
    if len(lines) < 2:
        return "council"
    match = re.search(r"mode[ \t]+(\S+)", lines[1])
    return match.group(1).rstrip("`") if match else "council"


LANE_HEADING = re.compile(r"^#{0,6}[ \t]*LANE[ \t]+\S")


def get_lane_names(checklist: str) -> list[str]:
    """Dispatch's trace unit is the lane, not its worker — the lane is what dispatch partitions
    into, and 'worker' is roster/cost metadata that two lanes may legitimately share. A LANE
    heading's text after '·' is slugified (lowercase, spaces→dashes) so it matches both a
    <lane>.md file stem and a turn header's agent field."""
    names: set[str] = set()
    for line in _strip_comments(checklist).splitlines():
        if not LANE_HEADING.match(line):
            continue
        _, sep, short = line.partition('·')
        if not sep:
            continue
        slug = re.sub(r'[ \t]+', '-', short.strip().lower())
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        if slug:
            names.add(slug)
    return sorted(names)


def extract_anchor(chat: str) -> str:
    """Extract text between '## anchor' and the next '## ' heading, stripping HTML comments."""
    block_lines = []
    in_block = False
    for line in chat.splitlines():
        if re.match(r'^## anchor', line):
            in_block = True
            continue
        if in_block and re.match(r'^## ', line):
            break
        if in_block:
            block_lines.append(line)
    return _strip_comments('\n'.join(block_lines))


def get_posters(chat: str) -> list[str]:
    """Agents that posted at least one turn (### <time> <agent> #<n>)."""
    posters: set[str] = set()
    for line in chat.splitlines():
        if line.startswith('### '):
            parts = line.split()
            if len(parts) >= 3:
                posters.add(parts[2])
    return sorted(posters)


def get_seat_files(session_dir: Path) -> dict[str, str]:
    """Text of every non-core .md at any depth, keyed by stem — live rooms group seat files into phase subdirectories.

    A file only supplies evidence for a seat the checklist or chat already names; it never adds a seat of its own,
    or a lead's summary.md would be conscripted into a roster it was never part of."""
    seats: dict[str, str] = {}
    for path in sorted(session_dir.rglob('*.md')):
        if path.name in ('chat.md', 'checklist.md'):
            continue
        seats[path.stem] = seats.get(path.stem, '') + read_text(path)
    return seats


def get_declared(checklist: str, mode: str) -> list[str]:
    """Seat names the lead assigned in checklist.md.

    Council: owner/challenger/worker field values ARE the seat identity.
    Dispatch: the lane is the unit of dispatch, so trace by lane name instead — a lane's
    'worker' is a substrate detail, and two lanes sharing a worker type must still trace
    separately or one file/turn silently covers both."""
    if mode == "dispatch":
        return get_lane_names(checklist)
    declared: set[str] = set()
    for line in checklist.splitlines():
        # Items declare fields block-form, lanes declare them as markdown bullets — a leading dash must not hide a worker from the ghost-seat check.
        m = re.match(r'^[ \t]*(?:[-*][ \t]+)?(owner|challenger|worker):[ \t]*(\S+)', line, re.IGNORECASE)
        if m:
            name = m.group(2).split()[0]  # first token only
            if re.match(r'^[a-z0-9][a-z0-9-]*$', name):
                declared.add(name)
    return sorted(declared)


def check_anchor(anchor: str) -> tuple[bool, str]:
    if anchor.replace('\n', '').replace(' ', '').strip():
        return True, "PASS anchor: the owner's verbatim message is pinned"
    return False, "FAIL anchor: chat.md has no non-empty '## anchor' block — the room has nothing to be measured against"


def check_req_quotes(checklist: str, anchor: str) -> tuple[bool, list[str]]:
    unquoted: list[str] = []
    unfound: list[str] = []
    for line in checklist.splitlines():
        if not re.search(r'^[ \t]*[-*]?[ \t]*REQ-[0-9]+', line):
            continue
        id_match = re.search(r'REQ-[0-9]+', line)
        req_id = id_match.group() if id_match else ''
        frag_match = re.search(r'^[^"]*"([^"]+)"', line)
        if not frag_match:
            unquoted.append(req_id)
        elif frag_match.group(1) not in anchor:
            unfound.append(req_id)

    messages: list[str] = []
    ok = True
    if unquoted:
        messages.append(f"FAIL req-quotes: no \"quoted fragment\" on: {' '.join(unquoted)}")
        ok = False
    if unfound:
        messages.append(f"FAIL req-quotes: quoted text not found in the anchor block: {' '.join(unfound)}")
        ok = False
    if ok:
        messages.append("PASS req-quotes: every REQ quotes the owner's own words")
    return ok, messages


def check_ghost_seats(declared: list[str], traced: dict[str, str]) -> tuple[bool, str]:
    ghosts = [n for n in declared if n not in traced]
    if ghosts:
        return False, f"FAIL ghost-seats: declared but left no turn and no file: {' '.join(ghosts)}"
    if not declared:
        return True, "SKIP ghost-seats: checklist.md declares no owner/challenger"
    return True, "PASS ghost-seats: every declared owner/challenger left a trace"


def _agent_blocks(chat: str, agent: str) -> str:
    """Return the concatenated text of all turns posted by agent."""
    result: list[str] = []
    capturing = False
    for line in chat.splitlines():
        if line.startswith('### '):
            parts = line.split()
            capturing = len(parts) >= 3 and parts[2] == agent
        elif capturing:
            result.append(line)
    return '\n'.join(result)


def check_rule_receipts(traced: dict[str, str]) -> tuple[bool, str]:
    noreceipt = [name for name, text in sorted(traced.items()) if '[RULES]' not in text]
    if noreceipt:
        return False, f"FAIL rule-receipts: no [RULES] line anywhere from: {' '.join(noreceipt)}"
    if not traced:
        return True, "SKIP rule-receipts: no seat left a trace to check"
    return True, "PASS rule-receipts: every seat reported what it loaded"


def check_evidence_tags(traced: dict[str, str]) -> tuple[bool, str]:
    untagged = [
        name for name, text in sorted(traced.items())
        if not re.search(r'FACT|CONSTRAINT|ASSUMPTION', text)
    ]
    if untagged:
        return False, f"FAIL evidence-tags: no FACT/CONSTRAINT/ASSUMPTION anywhere from: {' '.join(untagged)}"
    if not traced:
        return True, "SKIP evidence-tags: no seat left a trace to check"
    return True, "PASS evidence-tags: every seat tagged evidence"


def check_req_coverage(checklist: str) -> tuple[bool, str]:
    """Diff the ledger against the items — the lead's omissions, found without asking the lead.

    Parsed by section rather than by line shape: both the block form (`covers:` on its own line) and
    the one-line pipe form (`ITEM 5 · … | covers REQ-1 | …`) are in real use, and a parser that only
    knows one of them fails open — the silent direction for a coverage check."""
    ledger_text, items_text = [], []
    target = None
    for line in checklist.splitlines():
        if line.startswith('## '):
            head = line[3:].strip().lower()
            # Anchored, not substring: '## REQ with no item' contains 'item' and would otherwise route an explicitly-uncovered REQ into the covered set — a silent pass.
            target = ledger_text if 'ledger' in head else (items_text if head.startswith('item') or head.startswith('lane') else None)
            continue
        if target is not None:
            target.append(line)

    ledger = _req_ids('\n'.join(ledger_text))
    covered = set(_req_ids('\n'.join(items_text)))
    if not ledger:
        return False, "FAIL req-coverage: no REQ-<n> lines in checklist.md — the ledger was never written"
    orphans = [r for r in ledger if r not in covered]
    if orphans:
        return False, f"FAIL req-coverage: no item covers: {' '.join(orphans)}"
    return True, f"PASS req-coverage: all {len(ledger)} REQs owned by an item"


def check_reminders(chat: str) -> tuple[bool, str]:
    remind_ids = set(re.findall(r'REMIND-[0-9]+', chat))
    open_reminds = []
    for rid in sorted(remind_ids):
        if not re.search(rf'(ACK|OVERRULE) {re.escape(rid)}\b', chat):
            open_reminds.append(rid)
    if open_reminds:
        return False, f"FAIL reminders: no ACK/OVERRULE for: {' '.join(open_reminds)}"
    return True, "PASS reminders: every REMIND answered (or none issued)"


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("usage: council_verify.py <session-dir>  (must contain chat.md + checklist.md)", file=sys.stderr)
        sys.exit(2)

    session_dir = Path(sys.argv[1])
    chat_path = session_dir / 'chat.md'
    checklist_path = session_dir / 'checklist.md'

    if not chat_path.is_file() or not checklist_path.is_file():
        print("usage: council_verify.py <session-dir>  (must contain chat.md + checklist.md)", file=sys.stderr)
        sys.exit(2)

    chat = read_text(chat_path)
    checklist = read_text(checklist_path)

    anchor = extract_anchor(chat)
    seat_files = get_seat_files(session_dir)
    declared = get_declared(checklist, read_mode(chat))
    roster = sorted(set(get_posters(chat)) | set(declared))
    traced = {
        name: text for name in roster
        if (text := f"{_agent_blocks(chat, name)}\n{seat_files.get(name, '')}".strip())
    }

    fail = False

    # 1. anchor
    ok, msg = check_anchor(anchor)
    print(msg)
    fail = fail or not ok

    # 2. REQ quotes
    ok, msgs = check_req_quotes(checklist, anchor)
    for msg in msgs:
        print(msg)
    fail = fail or not ok

    # 3. ghost seats
    ok, msg = check_ghost_seats(declared, traced)
    print(msg)
    fail = fail or not ok

    # 4. rule receipts
    ok, msg = check_rule_receipts(traced)
    print(msg)
    fail = fail or not ok

    # 5. evidence tags
    ok, msg = check_evidence_tags(traced)
    print(msg)
    fail = fail or not ok

    # 6. unanswered reminders
    ok, msg = check_reminders(chat)
    print(msg)
    fail = fail or not ok

    # 7. REQ coverage
    ok, msg = check_req_coverage(checklist)
    print(msg)
    fail = fail or not ok

    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
