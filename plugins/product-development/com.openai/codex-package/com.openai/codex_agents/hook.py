#!/usr/bin/env python3
"""Announce routing and record actual native role selection without blocking work."""

from __future__ import annotations

import json
import sys

from manager import Manager


def context(status: dict) -> str:
    lines = [f"Product Development {status['version']} Codex roles:"]
    lines.extend(f"- {role['name']} ({role['model']}, {role['effort']}, default {role['sandboxMode']}): {role['routing']}"
                 for role in status["roles"])
    lines.append("Installation: " + "; ".join(
        f"{scope}={plan['state']}" for scope, plan in status["installations"].items()))
    observed = status["session"]["nativeRoleSelections"]
    lines.append("Native role selection observed in this session: " +
                 (", ".join(observed) if observed else "none; session usability is unverified."))
    lines.append(
        "Inspect the current spawn tool's schema for a custom role/type selector before claiming "
        "that these roles are usable. Use the registered role name when delegation is appropriate "
        "and authorized; select Astra only for difficult architecture questions. If roles are missing "
        "or outdated, use $manage-codex-agents and codex_agents_onboard after the MCP server connects. "
        "The installer requests native form consent before changes. If files are ready but roles "
        "are not selectable, follow the restart guidance; installation alone does not reload this chat. "
        "Assign file ownership before implementation or transformation; diagnosis does not edit product source. "
        "Role defaults do not grant authority or override the parent's live permissions. "
        "Native SubagentStart receipts confirm actual role selection, not a model-policy reload. "
        "Cloud discovery remains pending."
    )
    return "\n".join(lines)


def main() -> int:
    event = {}
    try:
        event = json.load(sys.stdin)
        manager = Manager.from_environment(event["cwd"])
        if event.get("hook_event_name") == "SubagentStart":
            manager.record_start(event)
            return 0
        output = context(manager.status(event.get("session_id", "")))
    except Exception:
        output = (
            "Product Development's Codex role check could not complete. Session usability is "
            "unverified. Use $manage-codex-agents after the bundled MCP server connects; "
            "resolve installation conflicts without overwriting existing roles or configuration."
        )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": event.get("hook_event_name", "SessionStart"),
        "additionalContext": output,
    }}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
