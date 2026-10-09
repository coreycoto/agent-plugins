#!/usr/bin/env python3
"""Bounded JSON hook adapter; failures are advisory and never expose input."""
from __future__ import annotations

import json
import sys

from workflow import WorkflowManager

MAX_INPUT = 1024 * 1024
EVENTS = {"SessionStart", "PreToolUse", "PostToolUse", "Stop", "Interrupt"}


def main() -> int:
    event = {}
    try:
        raw = sys.stdin.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise ValueError("size")
        event = json.loads(raw)
        if not isinstance(event, dict) or event.get("hook_event_name") not in EVENTS:
            print("{}")
            return 0
        manager = WorkflowManager.from_environment(event["cwd"], event["session_id"])
        output = manager.handle_event(event)
    except Exception:
        # Stop/Interrupt have different output schemas and must never block on error.
        # Other hooks receive a warning only through stderr, not exception details.
        print("Workflow hook could not verify private task state; no workflow was started or authorized.", file=sys.stderr)
        output = {}
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
