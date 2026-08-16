#!/usr/bin/env python3
# akiflow — tally token usage per seat for a closed council session, at Step 6 close-out.
#
# Usage:  council_cost.py [<session-dir>] [--session <uuid>]
#   <session-dir>  a room under ~/.aki/agent-council/<project>/<session>/; its chat.md line 2 carries the `claude-session <uuid>` stamp council_open.py writes. Rooms opened before that stamp carry none.
#   --session      explicit session id — the only way to cost an unstamped room, and takes precedence over a parsed stamp when both are given.
#
# The harness writes each seat its own transcript, so a seat IS one ~/.claude/projects/<cwd-slug>/<session-id>/subagents/agent-*.jsonl and the lead is the plain <session-id>.jsonl beside it — no chain-walking to separate interleaved turns.
# Scope is the Claude meter, and that is the complete answer rather than a partial one — why a headless lane on another vendor's quota is left out instead of missing: docs/arch/akiflow.md § Close-out accounting.
# Dollar cost is deliberately not computed: per-model prices drift, and a hardcoded table in a distributed script rots.
import sys
import json
import re
from pathlib import Path
from collections import OrderedDict


USAGE = "usage: council_cost.py [<session-dir>] [--session <uuid>]"
STAMP_RE = re.compile(r"claude-session\s+([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})")


def fmt(n):
    return f"{n:,}"


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rows.append(json.loads(raw))
            except Exception:
                continue
    return rows


def seat_label(meta_path, seat_id):
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return f"unlabeled-{seat_id}"
    agent_type = meta.get("agentType") or "unlabeled"
    description = (meta.get("description") or "").strip()
    if description and description.lower() != agent_type.lower():
        return f"{agent_type}: {description}"
    return agent_type


def tally(rows, label, agents):
    for d in rows:
        if d.get("type") != "assistant":
            continue
        msg = d.get("message", {})
        usage = msg.get("usage") or {}
        model = msg.get("model") or "?"
        b = agents.setdefault(label, OrderedDict()).setdefault(model, {"turns": 0, "in": 0, "out": 0, "cw": 0, "cr": 0})
        b["turns"] += 1
        b["in"] += usage.get("input_tokens", 0)
        b["out"] += usage.get("output_tokens", 0)
        b["cw"] += usage.get("cache_creation_input_tokens", 0)
        b["cr"] += usage.get("cache_read_input_tokens", 0)


def main():
    args = sys.argv[1:]
    session_dir_arg = None
    session_override = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--session":
            i += 1
            session_override = args[i] if i < len(args) else None
        elif session_dir_arg is None:
            session_dir_arg = a
        else:
            print(f"council_cost.py: unexpected argument: {a}", file=sys.stderr)
            sys.exit(2)
        i += 1

    if not session_dir_arg and not session_override:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    session_id = session_override
    if not session_id:
        session_dir = Path(session_dir_arg)
        chat_path = session_dir / "chat.md"
        if not chat_path.is_file():
            print(USAGE, file=sys.stderr)
            print(f"no chat.md in {session_dir} — not a council room.", file=sys.stderr)
            sys.exit(2)
        text = chat_path.read_text(encoding="utf-8", errors="replace")
        m = STAMP_RE.search(text)
        if not m:
            print(f"session id unknown: {chat_path} carries no claude-session stamp — this room predates the stamp.", file=sys.stderr)
            print("per-seat cost cannot be attributed without a session id: rerun with --session <uuid>.", file=sys.stderr)
            sys.exit(1)
        session_id = m.group(1)

    slug = str(Path.cwd()).replace("/", "-")
    project_dir = Path.home() / ".claude" / "projects" / slug
    main_file = project_dir / f"{session_id}.jsonl"
    if not main_file.is_file():
        print(f"no transcript for session {session_id}: {main_file} does not exist.", file=sys.stderr)
        print("confirm the session id and that this runs from the project's own working directory.", file=sys.stderr)
        sys.exit(1)

    print(f"session: {session_id}")
    print(f"transcript: {main_file}")

    subagents_dir = project_dir / session_id / "subagents"
    seat_files = sorted(subagents_dir.glob("agent-*.jsonl")) if subagents_dir.is_dir() else []
    if seat_files:
        print(f"seats: {len(seat_files)} subagent transcript(s) under {subagents_dir}")
    else:
        print(f"seats: none under {subagents_dir} — LEAD-only is the whole session, not a partial table.")

    agents = OrderedDict()
    tally(read_jsonl(main_file), "LEAD", agents)
    for seat_file in seat_files:
        stem = seat_file.stem
        seat_id = stem[len("agent-"):] if stem.startswith("agent-") else stem
        label = seat_label(seat_file.with_suffix(".meta.json"), seat_id)
        tally(read_jsonl(seat_file), label, agents)

    header = f"{'agent':<32} {'model':<22} {'turns':>6} {'in':>10} {'out':>10} {'cache_w':>12} {'cache_r':>12}"
    grand = {"turns": 0, "in": 0, "out": 0, "cw": 0, "cr": 0}
    print()
    print(header)
    print("-" * len(header))
    for label, models in agents.items():
        for model, b in models.items():
            print(f"{label:<32} {model:<22} {b['turns']:>6} {fmt(b['in']):>10} {fmt(b['out']):>10} {fmt(b['cw']):>12} {fmt(b['cr']):>12}")
            for k in grand:
                grand[k] += b[k]
    print("-" * len(header))
    print(f"{'TOTAL':<32} {'':<22} {grand['turns']:>6} {fmt(grand['in']):>10} {fmt(grand['out']):>10} {fmt(grand['cw']):>12} {fmt(grand['cr']):>12}")
    print()
    print("note: cache_w = cache_creation_input_tokens, cache_r = cache_read_input_tokens.")
    print("cost = tokens x current per-model price (billed input = input + cache_creation; cache_read and output are priced separately) — prices drift, look them up, do not assume.")
    print("seat labels come from each seat's meta.json sidecar (agentType/description), never guessed from prompt text — still worth a sanity-check against the declared roster.")


if __name__ == "__main__":
    main()
