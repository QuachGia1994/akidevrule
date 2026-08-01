#!/usr/bin/env python3
"""CLI for reading/mutating an Aki-Dev-Sync `.akidevsync/notes.json` task file.

Schema (as written by the Aki-Dev-Sync app itself):
  { "about": "<url>", "schema": 1, "notes": "<free text>",
    "tasks": [ { "id", "title", "detail", "done", "pin", "wish",
                 "created_at", "updated_at" } (ms epoch ints) ],
    "updated_at": <ms epoch int> }

Every mutation preserves the on-disk key order (alphabetical per task,
declared order at root) so a diff against the app's own next write stays
quiet, and writes back with ensure_ascii=False (Vietnamese text unescaped)
and a trailing newline, matching the app's own formatting.
"""
import argparse
import json
import sys
import time
from pathlib import Path

TASK_KEY_ORDER = ["created_at", "detail", "done", "id", "pin", "title", "updated_at", "wish"]
ROOT_KEY_ORDER = ["about", "schema", "notes", "tasks", "updated_at"]


def now_ms():
    return int(time.time() * 1000)


def load(path):
    p = Path(path)
    if not p.exists():
        sys.exit(f"error: {path} does not exist (this project has no Aki-Dev-Sync task notes yet)")
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    data["updated_at"] = now_ms()
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def new_id(data):
    existing = {t["id"] for t in data["tasks"]}
    ts = now_ms()
    tid = f"task-{ts}"
    while tid in existing:
        ts += 1
        tid = f"task-{ts}"
    return tid, ts


def ordered_task(fields):
    return {k: fields[k] for k in TASK_KEY_ORDER}


def find_task(data, task_id):
    for t in data["tasks"]:
        if t["id"] == task_id:
            return t
    sys.exit(f"error: no task with id {task_id!r}")


def cmd_list(args):
    data = load(args.path)
    tasks = data["tasks"]
    if args.pin:
        tasks = [t for t in tasks if t["pin"]]
    if args.pending:
        tasks = [t for t in tasks if not t["done"]]
    if args.done:
        tasks = [t for t in tasks if t["done"]]
    if args.wish:
        tasks = [t for t in tasks if t["wish"]]
    for t in tasks:
        mark = "x" if t["done"] else " "
        pin = "📌" if t["pin"] else "  "
        print(f"[{mark}] {pin} {t['id']}  {t['title']}")
        if args.detail and t["detail"]:
            for line in t["detail"].splitlines():
                print(f"        {line}")


def cmd_add(args):
    data = load(args.path)
    tid, ts = new_id(data)
    task = ordered_task({
        "created_at": ts,
        "detail": args.detail or "",
        "done": False,
        "id": tid,
        "pin": bool(args.pin),
        "title": args.title,
        "updated_at": ts,
        "wish": bool(args.wish),
    })
    data["tasks"].append(task)
    save(args.path, data)
    print(json.dumps(task, ensure_ascii=False, indent=2))


def cmd_set(args):
    data = load(args.path)
    t = find_task(data, args.task_id)
    changed = False
    if args.done is not None:
        t["done"] = args.done
        changed = True
    if args.pin is not None:
        t["pin"] = args.pin
        changed = True
    if args.wish is not None:
        t["wish"] = args.wish
        changed = True
    if args.title is not None:
        t["title"] = args.title
        changed = True
    if args.detail is not None:
        t["detail"] = args.detail
        changed = True
    if not changed:
        sys.exit("error: set needs at least one of --done/--pin/--wish/--title/--detail")
    t["updated_at"] = now_ms()
    save(args.path, data)
    print(json.dumps(t, ensure_ascii=False, indent=2))


def cmd_delete(args):
    data = load(args.path)
    before = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != args.task_id]
    if len(data["tasks"]) == before:
        sys.exit(f"error: no task with id {args.task_id!r}")
    save(args.path, data)
    print(f"deleted {args.task_id}")


def cmd_note(args):
    data = load(args.path)
    data["notes"] = args.text
    save(args.path, data)
    print("notes field updated")


def cmd_init(args):
    p = Path(args.path)
    if p.exists():
        sys.exit(f"error: {args.path} already exists — refusing to overwrite")
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {k: v for k, v in {
        "about": "https://github.com/lacvietanh/aki-dev-sync",
        "schema": 1,
        "notes": "",
        "tasks": [],
        "updated_at": now_ms(),
    }.items()}
    data = {k: data[k] for k in ROOT_KEY_ORDER}
    save(args.path, data)
    print(f"created {args.path}")


def parse_bool(s):
    return s.lower() in ("1", "true", "yes", "on")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="path to .akidevsync/notes.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--pin", action="store_true", help="only pinned tasks")
    p_list.add_argument("--done", action="store_true", help="only done tasks")
    p_list.add_argument("--pending", action="store_true", help="only not-done tasks")
    p_list.add_argument("--wish", action="store_true", help="only wishlist tasks")
    p_list.add_argument("--detail", action="store_true", help="also print each task's detail")
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("title")
    p_add.add_argument("--detail", default="")
    p_add.add_argument("--pin", action="store_true")
    p_add.add_argument("--wish", action="store_true")
    p_add.set_defaults(func=cmd_add)

    p_set = sub.add_parser("set", help="update fields on an existing task")
    p_set.add_argument("task_id")
    p_set.add_argument("--done", type=parse_bool, default=None)
    p_set.add_argument("--pin", type=parse_bool, default=None)
    p_set.add_argument("--wish", type=parse_bool, default=None)
    p_set.add_argument("--title", default=None)
    p_set.add_argument("--detail", default=None)
    p_set.set_defaults(func=cmd_set)

    p_del = sub.add_parser("delete", help="remove a task permanently")
    p_del.add_argument("task_id")
    p_del.set_defaults(func=cmd_delete)

    p_note = sub.add_parser("note", help="replace the project-wide notes text")
    p_note.add_argument("text")
    p_note.set_defaults(func=cmd_note)

    p_init = sub.add_parser("init", help="create a new empty notes.json (only if missing)")
    p_init.set_defaults(func=cmd_init)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
