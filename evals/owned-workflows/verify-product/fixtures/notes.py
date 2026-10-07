import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("text")
    commands.add_parser("list")
    args = parser.parse_args()
    existing = json.loads(args.store.read_text()) if args.store.exists() else []
    if args.command == "add":
        note = {"id": max((item["id"] for item in existing), default=0) + 1, "text": args.text}
        args.store.parent.mkdir(parents=True, exist_ok=True)
        args.store.write_text(json.dumps(existing + [note]) + "\n")
        print(json.dumps(note))
    else:
        print(json.dumps(existing))


if __name__ == "__main__":
    main()
