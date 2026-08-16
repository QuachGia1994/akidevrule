#!/usr/bin/env python3
# akiflow — read chat.md without pulling the whole room into the lead's context.
#
# The room is a live meeting, read in time order like a human would. This script exists so that "in time order" does not have to mean "all of it, every time".
#
# Usage:  council_read.py <chat.md> [options]
#   --index           list turn headers only (time, agent, turn no.)
#   --pinned          print the pinned header block only
#   --stats           turns and bytes per agent — the lead's drift/cost signal, read before deciding what to pull
#   --grep <pattern>  matching lines only, each tagged with the turn it came from — locate first, then read that turn
#   --turn <n[,m..]>  print exactly these turns, by number
#   --agent <name>    only turns by this agent
#   --from <n>        only turns numbered >= n
#   --tail <n>        only the last n matching turns
# Options combine; --index/--pinned/--stats/--grep are exclusive modes. --agent and --from narrow --grep too.
#
# A read is not a one-time cost: everything pulled into context is re-sent on every later turn, so a read of size S at turn t of a T-turn run is charged about S x (T - t). That is why locating with --grep and then pulling one turn beats reading the room.
import os
import re
import sys
from pathlib import Path
from collections import Counter


class Turn:
    def __init__(self, header: str, line_no: int):
        parts = header.split()
        self.header = header
        self.line_no = line_no
        self.agent = parts[2] if len(parts) >= 3 else ""
        self.number = next((int(p[1:]) for p in parts if p.startswith("#") and p[1:].isdigit()), 0)
        self.body: list[str] = []

    def text(self) -> str:
        return "\n".join([self.header] + self.body)


def parse_turns(lines: list[str]) -> list[Turn]:
    turns: list[Turn] = []
    for idx, line in enumerate(lines, start=1):
        if line.startswith("### "):
            turns.append(Turn(line, idx))
        elif turns:
            turns[-1].body.append(line)
    return turns


def main():
    if len(sys.argv) < 2 or not Path(sys.argv[1]).is_file():
        print("usage: council_read.py <chat.md> [--index|--pinned|--stats|--grep P] [--turn N,M] [--agent N] [--from N] [--tail N]", file=sys.stderr)
        sys.exit(2)

    file = Path(sys.argv[1])
    mode = "blocks"
    pattern = ""
    wanted: set[int] = set()
    agent = ""
    from_turn = None
    tail_n = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--index":
            mode = "index"
        elif arg == "--pinned":
            mode = "pinned"
        elif arg == "--stats":
            mode = "stats"
        elif arg in ("--grep", "--turn", "--agent", "--from", "--tail"):
            i += 1
            if i >= len(sys.argv):
                print(f"{arg} needs a value", file=sys.stderr)
                sys.exit(2)
            value = sys.argv[i]
            if arg == "--grep":
                mode = "grep"
                pattern = value
            elif arg == "--turn":
                wanted = {int(n) for n in re.findall(r"[0-9]+", value)}
            elif arg == "--agent":
                agent = value
            elif arg == "--from":
                from_turn = int(value)
            else:
                tail_n = int(value)
        else:
            print(f"unknown option: {arg}", file=sys.stderr)
            sys.exit(2)
        i += 1

    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    turns = parse_turns(lines)

    if mode == "pinned":
        for line in lines:
            if line.startswith("### "):
                break
            print(line)
        return

    if mode == "index":
        for turn in turns:
            print(f"{turn.line_no}:{turn.header}")
        return

    if mode == "stats":
        counts = Counter(t.agent for t in turns)
        weight = Counter()
        for turn in turns:
            weight[turn.agent] += len(turn.text().encode())
        print(f"{'turns':>7} {'bytes':>9}  agent")
        for name, count in counts.most_common():
            print(f"{count:>7} {weight[name]:>9,}  {name}")
        print(f"turns: {len(turns)}   bytes in turns: {sum(weight.values()):,}   file: {file.stat().st_size:,}")
        return

    selected = [t for t in turns if (not agent or t.agent == agent) and (from_turn is None or t.number >= from_turn) and (not wanted or t.number in wanted)]

    if mode == "grep":
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            print(f"bad --grep pattern: {exc}", file=sys.stderr)
            sys.exit(2)
        hits = 0
        for turn in selected:
            for offset, line in enumerate(turn.body, start=1):
                if regex.search(line):
                    hits += 1
                    print(f"#{turn.number} {turn.agent} L{turn.line_no + offset}: {line.strip()}")
        print(f"-- {hits} line(s) in {len(selected)} turn(s) searched; read one with --turn <n>", file=sys.stderr)
        return

    if tail_n is not None and len(selected) > tail_n:
        selected = selected[-tail_n:]

    for turn in selected:
        print(turn.text())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Piping into head/less is the intended use; without this the reader gets a traceback and goes back to reading the file whole.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
