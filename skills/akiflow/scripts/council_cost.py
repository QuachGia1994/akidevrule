#!/usr/bin/env python3
# akiflow — tally token usage per agent from a Claude Code session transcript.
#
# Run once at the close of a Tier 1/2 run (Step 9). It aggregates the raw usage
# numbers the harness already records so the lead can report actual token/cost
# against the roster it declared up front (Step 1) — never by pulling the raw
# transcript into the lead's context, which is exactly the flooding the council
# exists to avoid.
#
# Usage:  council_cost.py [transcript.jsonl]
#   With no argument it picks the newest *.jsonl in this project's transcript
#   directory: ~/.claude/projects/<cwd-path-with-slashes-as-dashes>/.
#
# What the harness gives us (all [obs], re-verify if a transcript format changes):
#   - Every assistant turn is one JSONL line with message.model and message.usage
#     {input_tokens, output_tokens, cache_creation_input_tokens,
#      cache_read_input_tokens}. Subagent turns are the same shape but carry
#     "isSidechain": true.
#   - Each subagent (Task spawn) is a chain of isSidechain lines. akiflow's
#     thinking floor makes every specialist prompt begin "You are <NAME>, ..." —
#     this script reads that NAME to label the chain. Chains without that marker
#     fall back to "sidechain-<n>". The main thread (the lead) is "LEAD".
#
# Attribution is therefore exact per model and per chain; the chain→name label is
# best-effort and the lead should sanity-check it against the roster. Dollar cost
# is intentionally NOT computed here: per-model prices drift, and a hardcoded
# table in a distributed script rots. The script prints tokens; the lead (or the
# haiku running it) multiplies by the current per-model price to get cost.
import sys
import json
import re
from pathlib import Path
from collections import OrderedDict


NAME_RE = re.compile(r"You are ([A-Za-z0-9][A-Za-z0-9._-]*)")


def chain_root(d, by_uuid):
    """Walk parentUuid up while staying inside the same sidechain; return root uuid."""
    seen = set()
    cur = d
    while True:
        p = cur.get("parentUuid")
        if not p or p in seen or p not in by_uuid:
            return cur.get("uuid")
        parent = by_uuid[p]
        if not parent.get("isSidechain"):
            return cur.get("uuid")
        seen.add(p)
        cur = parent


def text_of(d):
    msg = d.get("message", {})
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for part in c:
            if isinstance(part, dict) and part.get("type") == "text":
                out.append(part.get("text", ""))
            elif isinstance(part, str):
                out.append(part)
        return "\n".join(out)
    return ""


def fmt(n):
    return f"{n:,}"


def main():
    transcript = sys.argv[1] if len(sys.argv) > 1 else ""

    if not transcript:
        slug = str(Path.cwd()).replace("/", "-")
        dir_path = Path.home() / ".claude" / "projects" / slug
        if not dir_path.is_dir():
            print(f"no transcript directory: {dir_path}", file=sys.stderr)
            print("pass the transcript .jsonl path explicitly.", file=sys.stderr)
            sys.exit(1)
        jsonl_files = sorted(dir_path.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not jsonl_files:
            print(f"no *.jsonl in {dir_path}", file=sys.stderr)
            sys.exit(1)
        transcript = str(jsonl_files[0])

    transcript_path = Path(transcript)
    if not transcript_path.is_file():
        print(f"transcript not found: {transcript}", file=sys.stderr)
        sys.exit(1)

    print(f"transcript: {transcript}")

    lines = []
    by_uuid = {}
    with transcript_path.open(encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                d = json.loads(raw)
            except Exception:
                continue
            lines.append(d)
            u = d.get("uuid")
            if u:
                by_uuid[u] = d

    root_label = {}
    for d in lines:
        if not d.get("isSidechain"):
            continue
        if d.get("type") != "user":
            continue
        r = chain_root(d, by_uuid)
        if r in root_label:
            continue
        m = NAME_RE.search(text_of(d))
        if m:
            root_label[r] = m.group(1)

    agents = OrderedDict()

    def bucket(label, model):
        a = agents.setdefault(label, OrderedDict())
        return a.setdefault(model or "?", {"turns": 0, "in": 0, "out": 0, "cw": 0, "cr": 0})

    fallback_n = 0
    fallback_map = {}
    for d in lines:
        if d.get("type") != "assistant":
            continue
        msg = d.get("message", {})
        usage = msg.get("usage") or {}
        model = msg.get("model", "?")
        if d.get("isSidechain"):
            r = chain_root(d, by_uuid)
            label = root_label.get(r)
            if not label:
                if r not in fallback_map:
                    fallback_n += 1
                    fallback_map[r] = f"sidechain-{fallback_n}"
                label = fallback_map[r]
        else:
            label = "LEAD"
        b = bucket(label, model)
        b["turns"] += 1
        b["in"] += usage.get("input_tokens", 0)
        b["out"] += usage.get("output_tokens", 0)
        b["cw"] += usage.get("cache_creation_input_tokens", 0)
        b["cr"] += usage.get("cache_read_input_tokens", 0)

    grand = {"turns": 0, "in": 0, "out": 0, "cw": 0, "cr": 0}
    print()
    print(f"{'agent':<20} {'model':<22} {'turns':>6} {'in':>10} {'out':>10} {'cache_w':>12} {'cache_r':>12}")
    print("-" * 96)
    for label, models in agents.items():
        for model, b in models.items():
            print(f"{label:<20} {model:<22} {b['turns']:>6} {fmt(b['in']):>10} {fmt(b['out']):>10} {fmt(b['cw']):>12} {fmt(b['cr']):>12}")
            for k in grand:
                grand[k] += b[k]
    print("-" * 96)
    print(f"{'TOTAL':<20} {'':<22} {grand['turns']:>6} {fmt(grand['in']):>10} {fmt(grand['out']):>10} {fmt(grand['cw']):>12} {fmt(grand['cr']):>12}")
    print()
    print("note: cache_w = cache_creation_input_tokens, cache_r = cache_read_input_tokens.")
    print("cost = tokens x current per-model price (billed input = input + cache_creation;")
    print("cache_read and output are priced separately). Prices drift — look them up; do not")
    print("assume. Chain->agent labels are best-effort; check against the declared roster.")


if __name__ == "__main__":
    main()
