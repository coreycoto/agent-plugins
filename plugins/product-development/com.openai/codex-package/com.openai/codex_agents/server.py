#!/usr/bin/env python3
"""Local MCP adapter using negotiated Codex rich forms for role consent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

from hook import context
from manager import AgentError, Manager

ARGUMENTS = {
    "type": "object",
    "properties": {
        "cwd": {"type": "string", "description": "The current session's absolute working directory."},
        "session_id": {"type": "string", "description": "The current parent Codex session id."},
        "source": {"type": "string", "description": "Optional SessionStart source."},
    },
    "required": ["cwd", "session_id"], "additionalProperties": False,
}


def form_method(capabilities: dict) -> str | None:
    extensions = capabilities.get("extensions", {})
    if isinstance(extensions, dict) and "openai/form" in extensions:
        return "openai/form"
    elicitation = capabilities.get("elicitation", {})
    if isinstance(elicitation, dict) and isinstance(elicitation.get("form"), dict):
        return "elicitation/create"
    return None


def onboard(manager: Manager, session: str, capabilities: dict,
            request_form: Callable[[str, dict], dict]) -> dict:
    plans = manager.plans()
    ready = [plan for plan in plans.values() if plan["state"] == "ready"]
    if ready:
        return {"result": "registered", **manager.status(session)}
    eligible = [scope for scope, plan in plans.items()
                if plan["state"] in {"missing", "upgrade_available"}]
    method = form_method(capabilities)
    if not eligible or method is None:
        return {"result": "conflict" if not eligible else "form_unavailable", **manager.status(session)}
    preview = "\n".join(
        f"{scope}: {plans[scope]['state']}, {plans[scope]['installedVersion'] or 'not installed'} "
        f"→ {manager.version}; {plans[scope]['target']}" for scope in eligible)
    roles = "\n".join(f"{role['name']}: {role['model']} ({role['effort']})" for role in manager.roles)
    params = {
        "message": (
            f"Install or upgrade Product Development's generated Codex roles?\n{roles}\n\n{preview}\n\n"
            "The plugin remains the authored source. This writes the listed role TOMLs, an ownership "
            "marker and a local .gitignore in the selected scope, plus private install metadata and "
            "backups under that scope's agent-plugin-state/product-development/. Native role-selection "
            "receipts are stored in the shared Codex state directory. Existing configuration, project "
            "trust and other role definitions are preserved. Project scope requires an already-trusted "
            "repository. A restart is required afterward; this form cannot restart the desktop app."
        ),
        "requestedSchema": {
            "type": "object", "properties": {
                "scope": {"type": "string", "title": "Installation scope",
                          "description": "user shares the roles across repositories; project installs only here; later makes no changes.",
                          "enum": [*eligible, "later"]},
                "confirm": {"type": "boolean", "title": "Approve the listed role installation or upgrade",
                            "description": "Check only to approve writes in the selected scope."},
            }, "required": ["scope", "confirm"], "additionalProperties": False,
        },
    }
    if method == "elicitation/create":
        params["mode"] = "form"
    response = request_form(method, params)
    answer = response.get("content")
    if response.get("action") != "accept" or not isinstance(answer, dict):
        return {"result": "deferred", "reason": "Form declined or cancelled; no role files changed."}
    if set(answer) != {"scope", "confirm"} or answer.get("confirm") is not True or answer.get("scope") not in eligible:
        return {"result": "deferred", "reason": "No valid affirmative installation choice; no role files changed."}
    scope = answer["scope"]
    return manager.apply(scope, plans[scope]["fingerprint"], session)


class Server:
    def __init__(self, input_stream=sys.stdin, output_stream=sys.stdout):
        self.input = input_stream
        self.output = output_stream
        self.capabilities = {}
        self.client_name = ""
        self.next_id = 0
        self.deferred = set()

    def send(self, payload: dict) -> None:
        self.output.write(json.dumps({"jsonrpc": "2.0", **payload}) + "\n")
        self.output.flush()

    def request_form(self, method: str, params: dict) -> dict:
        self.next_id += 1
        request_id = f"pd-form-{self.next_id}"
        self.send({"id": request_id, "method": method, "params": params})
        for line in self.input:
            message = json.loads(line)
            if message.get("id") == request_id:
                return message.get("result", {"action": "cancel"})
            if message.get("method") == "notifications/cancelled":
                return {"action": "cancel"}
            if "id" in message and "method" in message:
                if message["method"] == "ping":
                    self.send({"id": message["id"], "result": {}})
                else:
                    self.send({"id": message["id"], "error": {
                        "code": -32000, "message": "Installer is awaiting a form response."}})
        return {"action": "cancel"}

    def dispatch(self, method: str, params: dict) -> dict:
        if method == "initialize":
            self.capabilities = params.get("capabilities", {})
            self.client_name = params.get("clientInfo", {}).get("name", "")
            root = Path(__file__).resolve().parents[2]
            manifest = root / "plugin.json"
            if not manifest.exists():
                manifest = root / ".codex-plugin/plugin.json"
            return {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                    "serverInfo": {"name": "product-development-agents", "version": json.loads(
                        manifest.read_bytes())["version"]}}
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": [{
                "name": name, "description": description, "inputSchema": ARGUMENTS,
                "annotations": {"readOnlyHint": name == "codex_agents_status", "destructiveHint": False,
                                "idempotentHint": True, "openWorldHint": False},
            } for name, description in (
                ("codex_agents_status", "Read packaged-role registration, upgrade conflicts and native session-selection receipts."),
                ("codex_agents_onboard", "Preview and offer a native install/upgrade form for missing or outdated Codex roles; changes require affirmative form consent."),
            )]}
        if method != "tools/call" or params.get("name") not in {"codex_agents_status", "codex_agents_onboard"}:
            raise AgentError("Unknown MCP method or tool.")
        args = params.get("arguments", {})
        if not isinstance(args.get("cwd"), str) or not isinstance(args.get("session_id"), str) or set(args) - ARGUMENTS["properties"].keys():
            raise AgentError("Provide the current cwd and session_id.")
        manager = Manager.from_environment(args["cwd"])
        session = args["session_id"]
        key = (str(manager.cwd), session, manager.asset_digest)
        if params["name"] == "codex_agents_status":
            result = manager.status(session)
        elif "codex" not in self.client_name.lower():
            result = {"result": "client_unsupported", "reason": "This extension manages local Codex roles."}
        elif key in self.deferred:
            result = {"result": "deferred", "reason": "Already deferred in this session; no repeated startup prompt."}
        else:
            result = onboard(manager, session, self.capabilities, self.request_form)
            if result.get("result") == "deferred":
                self.deferred.add(key)
        result["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": context(manager.status(session)) + "\nOnboarding result: " +
                                 result.get("result", "status") + "\n" + result.get("restartGuidance", ""),
        }
        return {"content": [{"type": "text", "text": json.dumps(result)}], "structuredContent": result}

    def run(self) -> int:
        for line in self.input:
            request = {}
            try:
                request = json.loads(line)
                if "id" not in request:
                    continue
                result = self.dispatch(request["method"], request.get("params", {}))
                self.send({"id": request["id"], "result": result})
            except Exception as error:
                if "id" in request:
                    self.send({"id": request["id"], "error": {
                        "code": -32000,
                        "message": str(error) if isinstance(error, AgentError) else
                                   "The role operation could not complete; inspect configuration and owned files before retrying.",
                    }})
        return 0


if __name__ == "__main__":
    raise SystemExit(Server().run())
