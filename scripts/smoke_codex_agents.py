#!/usr/bin/env python3
"""Qualify native local MCP forms and package hooks in temporary Codex homes, without inference."""

from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from build_codex_package import marketplace_projection, write_generated
from jsonschema import validate

HOOK_SCHEMA = json.loads((Path(__file__).resolve().parents[1] /
                          "tests/fixtures/codex-session-start-output.schema.json").read_text())


class Rpc:
    def __init__(self, codex: str, home: Path, repo: Path, plugin: str, extra_env: dict | None = None):
        self.server = plugin + "-agents"
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"),
                   PYTHONDONTWRITEBYTECODE="1")
        env.update(extra_env or {})
        self.process = subprocess.Popen([codex, "app-server", "--stdio"], cwd=repo, env=env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True)
        self.messages = queue.Queue()
        self.forms = []
        self.next_id = 0
        threading.Thread(target=self.read, daemon=True).start()

    def read(self) -> None:
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except ValueError:
                continue
        self.messages.put(None)

    def send(self, message: dict) -> None:
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method: str, params: dict, answer: dict | None = None) -> dict:
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        while True:
            message = self.messages.get(timeout=30)
            if message is None:
                raise RuntimeError("Native server stopped.")
            if message.get("method") == "mcpServer/elicitation/request":
                self.forms.append(message["params"])
                self.send({"id": message["id"], "result": answer or {"action": "decline", "content": None}})
            elif message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"Native request failed: {method}: {json.dumps(message['error'])}")
                return message["result"]

    def initialize(self) -> None:
        self.call("initialize", {"clientInfo": {"name": "codex-role-qualification", "version": "1"},
                                 "capabilities": {"experimentalApi": True, "mcpServerOpenaiFormElicitation": True}})
        self.send({"method": "initialized"})

    def close(self) -> None:
        self.process.stdin.close()
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdout.close()


def tool(rpc: Rpc, thread_id: str, repo: Path, session: str, answer=None) -> dict:
    response = rpc.call("mcpServer/tool/call", {
        "threadId": thread_id, "server": rpc.server, "tool": "codex_agents_onboard",
        "arguments": {"cwd": str(repo), "session_id": session},
    }, answer)
    output = response["structuredContent"]
    validate(output, HOOK_SCHEMA)
    text_output = json.loads(response["content"][0]["text"])
    validate(text_output, HOOK_SCHEMA)
    assert text_output == output
    return output


def onboarding_context(output: dict) -> str:
    return output["hookSpecificOutput"]["additionalContext"]


def status(rpc: Rpc, thread_id: str, repo: Path) -> dict:
    return rpc.call("mcpServer/tool/call", {
        "threadId": thread_id, "server": rpc.server, "tool": "codex_agents_status",
        "arguments": {"cwd": str(repo), "session_id": thread_id},
    })["structuredContent"]


def workflow_probe(rpc: Rpc, thread_id: str, repo: Path, package: Path, env: dict) -> dict:
    """Exercise connected tools and the command envelope, without a model turn."""
    def call(name: str, **arguments) -> dict:
        response = rpc.call("mcpServer/tool/call", {
            "threadId": thread_id, "server": rpc.server, "tool": name,
            "arguments": {"cwd": str(repo), "session_id": thread_id, **arguments},
        })
        assert json.loads(response["content"][0]["text"]) == response["structuredContent"]
        return response["structuredContent"]

    assert call("codex_workflow_status")["state"] == "absent"
    source = repo / "workflow-source.txt"
    source.write_text("Isolated workflow qualification fixture.\n")
    subprocess.run(["git", "-C", str(repo), "add", source.name], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Qualification fixture", "-c",
                    "user.email=qualification@example.invalid", "commit", "-qm", "fixture"],
                   check=True, capture_output=True)
    task = {"id": "qualification", "issue": "isolated fixture", "delivery_stage": "local qualification",
            "status": "active", "paths": [source.name], "checks": [],
            "review_requested": False, "continuation_limit": 1}
    assert call("codex_workflow_task", task=task)["state"] == "ready"
    evidence_file = repo / "workflow-evidence.json"
    evidence_file.write_text('{"observation":"qualification fixture"}\n')
    plugin = json.loads((package / ".codex-plugin/plugin.json").read_text())["name"]
    if plugin == "product-development":
        task["review_requested"] = True
        call("codex_workflow_task", task=task)
    else:
        call("codex_workflow_evidence", evidence={"observation_id": "fixture", "condition": "governance_mismatch",
             "candidate": call("codex_workflow_status")["candidate"], "reference": evidence_file.name})
    command = package / "com.openai/codex_agents/workflow_hook.py"
    result = subprocess.run([sys.executable, "-S", str(command)], cwd=repo, env=env, text=True,
                            input=json.dumps({"hook_event_name": "SessionStart", "cwd": str(repo), "session_id": thread_id}),
                            capture_output=True, check=True, timeout=10)
    output = json.loads(result.stdout)
    validate(output, HOOK_SCHEMA)
    routes = call("codex_workflow_status")["routes"]
    assert len(routes) == 1 and routes[0]["current"] and routes[0]["status"] == "nominated"
    call("codex_workflow_route", route_id=routes[0]["id"], status="assigned")
    completed = call("codex_workflow_route", route_id=routes[0]["id"], status="completed",
                     outcome="passed", reference=evidence_file.name)
    assert completed["routes"][0]["status"] == "completed"
    return {"connectedTools": True, "commandEnvelope": True, "nativeEventDispatch": "unverified"}


def qualify(codex: str, work: Path, scope: str, package: Path) -> dict:
    plugin = json.loads((package / ".codex-plugin/plugin.json").read_bytes())["name"]
    home, repo, catalog = work / "user", work / "repo", work / "marketplace"
    home.mkdir(parents=True)
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True, capture_output=True)
    (home / ".codex").mkdir()
    (home / ".codex/config.toml").write_text(
        f"model = \"gpt-6.1-sol\"\n[projects.{json.dumps(str(repo))}]\ntrust_level = \"trusted\"\n")
    destination = catalog / "plugins" / plugin
    shutil.copytree(package, destination, ignore=shutil.ignore_patterns("__pycache__"))
    # Qualify catalog growth from a smaller catalog that retains every route target.
    role_catalog = destination / "com.openai/agents/catalog.json"
    expanded_catalog = role_catalog.read_bytes()
    previous_catalog = json.loads(expanded_catalog)
    route_path = destination / "com.openai/hooks/routes.json"
    route_roles = ({route["role"] for route in json.loads(route_path.read_bytes())["routes"]}
                   if route_path.is_file() else set())
    retained = ({"pd_explorer", "pd_reviewer", "pd_architecture_adviser"}
                if plugin == "product-development" else {entry["name"] for entry in previous_catalog["roles"][:2]})
    previous_catalog["roles"] = [entry for entry in previous_catalog["roles"] if entry["name"] in retained | route_roles]
    initial_count, final_count = len(previous_catalog["roles"]), len(json.loads(expanded_catalog)["roles"])
    role_catalog.write_text(json.dumps(previous_catalog))
    marketplace = catalog / ".agents/plugins/marketplace.json"
    marketplace.parent.mkdir(parents=True)
    marketplace.write_text(json.dumps({
        "name": "codex-role-qualification", "plugins": [{"name": plugin,
            "source": {"source": "local", "path": "./plugins/" + plugin},
            "policy": {"installation": "AVAILABLE"}, "category": "Developer Tools"}]}))
    env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"), PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([codex, "plugin", "marketplace", "add", str(catalog)], cwd=repo, env=env,
                   capture_output=True, check=True, timeout=30)
    rpc = Rpc(codex, home, repo, plugin)
    try:
        rpc.initialize()
        rpc.call("plugin/install", {"marketplacePath": str(marketplace), "pluginName": plugin})
        detail = rpc.call("plugin/read", {"marketplacePath": str(marketplace), "pluginName": plugin})["plugin"]
        native_manifest = json.loads((package / ".codex-plugin/plugin.json").read_bytes())
        authored_hooks = json.loads((package / native_manifest["hooks"]).read_bytes())["hooks"]
        assert len(detail["hooks"]) == sum(len(row["hooks"]) for rows in authored_hooks.values() for row in rows)
        assert detail["onboardingSkill"]["name"].endswith(":manage-codex-agents")
    finally:
        rpc.close()
    rpc = Rpc(codex, home, repo, plugin)
    target = (home / ".codex" if scope == "user" else repo / ".codex") / "agents" / plugin
    other = (repo / ".codex" if scope == "user" else home / ".codex") / "agents" / plugin
    original_config = (home / ".codex/config.toml").read_bytes()
    try:
        rpc.initialize()
        thread_id = rpc.call("thread/start", {"cwd": str(repo), "ephemeral": True, "model": "gpt-6.1-sol"})["thread"]["id"]
        statuses = rpc.call("mcpServerStatus/list", {"threadId": thread_id})["data"]
        assert any(server["name"] == plugin + "-agents" and server["runtimeStatus"] == "connected" for server in statuses)
        declined = tool(rpc, thread_id, repo, thread_id)
        assert "Onboarding result: deferred" in onboarding_context(declined) and not target.exists()
        installed = tool(rpc, thread_id, repo, "qualification-accepted", {
            "action": "accept", "content": {"scope": scope, "confirm": True}})
        assert "Onboarding result: installed" in onboarding_context(installed)
        assert "restart" in onboarding_context(installed).lower()
        assert status(rpc, thread_id, repo)["installations"][scope]["state"] == "ready"
        assert len(list(target.glob("*.toml"))) == initial_count and not other.exists()
        assert (home / ".codex/config.toml").read_bytes() == original_config
        expected_mode = rpc.forms[0]["mode"]
        assert expected_mode in {"openaiForm", "form"}
        form_method = "openai/elicitation/create" if expected_mode == "openaiForm" else "elicitation/create"
        assert len(rpc.forms) == 2 and all(form["mode"] == expected_mode for form in rpc.forms)
        form_modes = [form["mode"] for form in rpc.forms]
        workflow = (workflow_probe(rpc, thread_id, repo, destination, env)
                    if (package / "com.openai/hooks/routes.json").is_file() else {"state": "not_configured"})
    finally:
        rpc.close()
    # Simulate a native package upgrade only in this isolated local source.
    manifest = destination / ".codex-plugin/plugin.json"
    data = json.loads(manifest.read_bytes())
    parts = data["version"].split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    data["version"] = ".".join(parts)
    manifest.write_text(json.dumps(data))
    role_catalog.write_bytes(expanded_catalog)
    rpc = Rpc(codex, home, repo, plugin)
    try:
        rpc.initialize()
        rpc.call("plugin/install", {"marketplacePath": str(marketplace), "pluginName": plugin})
    finally:
        rpc.close()
    rpc = Rpc(codex, home, repo, plugin)
    try:
        rpc.initialize()
        thread_id = rpc.call("thread/start", {"cwd": str(repo), "ephemeral": True})["thread"]["id"]
        upgraded = tool(rpc, thread_id, repo, thread_id, {
            "action": "accept", "content": {"scope": scope, "confirm": True}})
        assert "Onboarding result: upgraded" in onboarding_context(upgraded)
        assert status(rpc, thread_id, repo)["version"] == data["version"]
        assert len(list(target.glob("*.toml"))) == final_count
        backups = list((target.parents[1] / "agent-plugin-state" / plugin / "backups").iterdir())
        assert len(backups) == 1 and backups[0].is_dir() and not backups[0].is_relative_to(target.parent)
        assert len(list(backups[0].glob("*.toml"))) == initial_count
        assert len(rpc.forms) == 1 and rpc.forms[0]["mode"] == expected_mode
        assert (home / ".codex/config.toml").read_bytes() == original_config
    finally:
        rpc.close()
    return {"plugin": plugin, "scope": scope, "hookEvents": [hook["eventName"] for hook in detail["hooks"]],
            "onboardingSkill": detail["onboardingSkill"]["name"], "formMethod": form_method, "formModes": form_modes,
            "declinePreservedFiles": True, "install": "installed", "upgrade": "upgraded", "hookOutputSchemaVerified": True,
            "generatedRoles": sorted(path.name for path in target.glob("*.toml")),
            "unrelatedConfigPreserved": True, "sessionSelectionVerification": "pending", "workflow": workflow}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--package", type=Path, help="Qualify one generated package; default is all public owned catalogs.")
    args = parser.parse_args()
    receipt = {"verified": False, "inferenceRequests": 0, "desktopActivation": False,
               "cloudPilot": "pending", "cases": []}
    try:
        if not args.codex:
            raise RuntimeError("A local Codex executable is required.")
        receipt["codexVersion"] = subprocess.check_output([args.codex, "--version"], text=True, stderr=subprocess.DEVNULL).strip()
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="codex-role-qualification-") as temporary:
            work = Path(temporary).resolve()
            if args.package:
                packages = [args.package]
            else:
                distribution = work / "distribution"
                write_generated(distribution, marketplace_projection(root))
                packages = [distribution / "plugins" / name for name in ("product-development", "project-management")]
            for package in packages:
                plugin = json.loads((package / ".codex-plugin/plugin.json").read_bytes())["name"]
                for scope in ("user", "project"):
                    receipt["cases"].append(qualify(args.codex, work / plugin / scope, scope, package))
        receipt["verified"] = True
    except Exception as error:
        receipt["failure"] = {"type": type(error).__name__, "message": str(error) if isinstance(error, RuntimeError) else "Native qualification failed; inspect the failing case."}
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return int(not receipt["verified"])


if __name__ == "__main__":
    raise SystemExit(main())
