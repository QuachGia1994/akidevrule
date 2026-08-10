#!/usr/bin/env python3
# akiflow — read chat.md without pulling the whole room into the lead's context.
#
# The room is a live meeting, read in time order like a human would. This script
# exists so that "in time order" does not have to mean "all of it, every time".
#
# Usage:  council_read.py <chat.md> [options]
#   --index           list turn headers only (time, agent, turn no.)
#   --pinned          print the pinned header block only
#   --stats           turns per agent — the lead's drift/cost signal
#   --agent <name>    only turns by this agent
#   --from <n>        only turns numbered >= n
#   --tail <n>        only the last n matching turns
# Options combine; --index/--pinned/--stats are exclusive modes.
import sys
from pathlib import Path
from collections import Counter


def main():
    if len(sys.argv) < 2 or not Path(sys.argv[1]).is_file():
        print("usage: council_read.py <chat.md> [--index|--pinned|--stats] [--agent N] [--from N] [--tail N]", file=sys.stderr)
        sys.exit(2)

    file = Path(sys.argv[1])
    mode = "blocks"
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
        elif arg == "--agent":
            i += 1
            agent = sys.argv[i] if i < len(sys.argv) else ""
        elif arg == "--from":
            i += 1
            from_turn = int(sys.argv[i]) if i < len(sys.argv) else None
        elif arg == "--tail":
            i += 1
            tail_n = int(sys.argv[i]) if i < len(sys.argv) else None
        else:
            print(f"unknown option: {arg}", file=sys.stderr)
            sys.exit(2)
        i += 1

    lines = file.read_text().splitlines()

    if mode == "index":
        for idx, line in enumerate(lines, start=1):
            if line.startswith("### "):
                print(f"{idx}:{line}")

    elif mode == "pinned":
        for line in lines:
            if line.startswith("### "):
                break
            print(line)

    elif mode == "stats":
        agents = []
        turn_count = 0
        for line in lines:
            if line.startswith("### "):
                turn_count += 1
                parts = line.split()
                if len(parts) >= 3:
                    agents.append(parts[2])
        counts = Counter(agents)
        for name, count in counts.most_common():
            print(f"{count:>7} {name}")
        print(f"turns: {turn_count}")

    else:  # blocks mode
        blocks = []
        current = None
        for line in lines:
            if line.startswith("### "):
                parts = line.split()
                who = parts[2] if len(parts) >= 3 else ""
                turn = 0
                for p in parts:
                    if p.startswith("#") and p[1:].isdigit():
                        turn = int(p[1:])
                        break
                keep = True
                if agent and who != agent:
                    keep = False
                if from_turn is not None and turn < from_turn:
                    keep = False
                if keep:
                    if current is not None:
                        blocks.append(current)
                    current = [line]
                else:
                    if current is not None:
                        blocks.append(current)
                    current = None
            else:
                if current is not None:
                    current.append(line)
        if current is not None:
            blocks.append(current)

        if tail_n is not None and len(blocks) > tail_n:
            blocks = blocks[-tail_n:]

        for block in blocks:
            for line in block:
                print(line)


if __name__ == "__main__":
    main()
