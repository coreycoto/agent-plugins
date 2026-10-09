"""Packaged MCP and author validation contracts for skill-only workflow owners."""
from __future__ import annotations

import io
import json
import shutil
from pathlib import Path

import pytest
from build_codex_package import projection, write_generated
from jsonschema import Draft202012Validator, ValidationError
from server import Server
from test_skill_only_workflow import ROOT, ROUTES, task, tree
from test_skill_only_workflow import repository as repository

from author_checks.plugin_validation import validate_portable_plugin

SCHEMA = json.loads((ROOT / "schemas/agent-plugins-1.0.0.schema.json").read_text())
WORKFLOW_TOOLS = {"codex_workflow_task", "codex_workflow_evidence", "codex_workflow_route", "codex_workflow_status"}


@pytest.mark.parametrize("plugin", ["communication", "product-management", "product-development", "project-management"])
def test_all_four_packages_project_workflow_runtime_and_discover_valid_tools(tmp_path: Path, plugin: str) -> None:
    root = tmp_path / "plugin"
    write_generated(root, projection(ROOT / "plugins" / plugin, "codex"))
    for name in ("workflow.py", "workflow_hook.py", "server.py"):
        assert (root / "com.openai/codex_agents" / name).read_bytes() == (ROOT / "adapters/codex_agents" / name).read_bytes()
    server = Server(io.StringIO(), io.StringIO(), root=root)
    tools = {tool["name"]: tool for tool in server.dispatch("tools/list", {})["tools"]}
    assert WORKFLOW_TOOLS <= tools.keys()
    for name in WORKFLOW_TOOLS:
        Draft202012Validator.check_schema(tools[name]["inputSchema"])
    if plugin in {"communication", "product-management"}:
        assert set(tools) == WORKFLOW_TOOLS
        assert not (root / "com.openai/agents").exists()
        hooks = json.loads((root / "com.openai/hooks/hooks.json").read_text())["hooks"]
        assert all(handler["type"] == "command"
                   for rows in hooks.values() for row in rows for handler in row["hooks"])
        assert all("workflow_hook.py" in handler["command"]
                   for rows in hooks.values() for row in rows for handler in row["hooks"])


@pytest.mark.parametrize("plugin,condition,skill,details", ROUTES)
def test_mcp_evidence_schema_accepts_exact_details_and_rejects_malformed_or_foreign(tmp_path: Path, plugin, condition, skill, details) -> None:
    root = tmp_path / "plugin"
    write_generated(root, projection(ROOT / "plugins" / plugin, "portable"))
    server = Server(io.StringIO(), io.StringIO(), root=root)
    tool = next(tool for tool in server.dispatch("tools/list", {})["tools"] if tool["name"] == "codex_workflow_evidence")
    validator = Draft202012Validator(tool["inputSchema"])
    record = {"observation_id": "observation-1", "candidate": "a" * 64,
              "condition": condition, "reference": "evidence.json", "details": details}
    arguments = {"cwd": str(tmp_path), "session_id": "session", "evidence": record}
    validator.validate(arguments)
    for malformed in ({**record, "details": {}},
                      {key: value for key, value in record.items() if key != "details"},
                      {**record, "details": {**details, "unknown": "field"}},
                      {**record, "condition": "prose_review_requested" if plugin == "product-management" else "customer_evidence_recorded"}):
        with pytest.raises(ValidationError):
            validator.validate({**arguments, "evidence": malformed})


@pytest.mark.parametrize("plugin", ["communication", "product-management"])
def test_mcp_wire_never_prompts_or_advertises_role_installation(tmp_path: Path, repository: Path, monkeypatch, plugin: str) -> None:
    root = tmp_path / "plugin"
    write_generated(root, projection(ROOT / "plugins" / plugin, "portable"))
    home = tmp_path / "codex-home"
    monkeypatch.setenv("CODEX_HOME", str(home))
    arguments = {"cwd": str(repository), "session_id": "skill-wire"}
    requests = [
        {"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "codex-test"}, "capabilities": {"elicitation": {"form": {}}}}},
        {"id": 2, "method": "tools/list", "params": {}},
        {"id": 3, "method": "tools/call", "params": {"name": "codex_workflow_status", "arguments": arguments}},
        {"id": 4, "method": "tools/call", "params": {"name": "codex_workflow_task", "arguments": {**arguments, "task": task()}}},
        {"id": 5, "method": "tools/call", "params": {"name": "codex_agents_onboard", "arguments": arguments}},
    ]
    output = io.StringIO()
    server = Server(io.StringIO("\n".join(json.dumps(request) for request in requests) + "\n"), output, root=root)
    assert server.run() == 0
    messages = [json.loads(line) for line in output.getvalue().splitlines()]
    assert {message["id"] for message in messages} == {1, 2, 3, 4, 5}
    assert not any("method" in message for message in messages)
    responses = {message["id"]: message for message in messages}
    assert {tool["name"] for tool in responses[2]["result"]["tools"]} == WORKFLOW_TOOLS
    assert responses[3]["result"]["structuredContent"]["state"] == "absent"
    assert responses[4]["result"]["structuredContent"]["task"]["id"] == "issue-16"
    assert "error" in responses[5]
    assert not (home / "agents").exists() and not (home / "config.toml").exists()
    assert not (repository / ".codex").exists()


@pytest.mark.parametrize("plugin", ["communication", "product-management"])
def test_skill_only_author_catalog_is_valid_without_agent_catalog(tmp_path: Path, plugin: str) -> None:
    root = tmp_path / "plugin"
    shutil.copytree(ROOT / "plugins" / plugin, root)
    before = tree(root)
    assert validate_portable_plugin(root, SCHEMA) == []
    assert tree(root) == before and not (root / "com.openai/agents/catalog.json").exists()


@pytest.mark.parametrize("mutation", ["foreign_skill", "foreign_condition", "role_without_catalog", "empty_role", "duplicate", "escaping_skill"])
def test_author_validation_rejects_broken_skill_only_ownership(tmp_path: Path, mutation: str) -> None:
    root = tmp_path / "plugin"
    shutil.copytree(ROOT / "plugins/communication", root)
    path = root / "com.openai/hooks/routes.json"
    catalog = json.loads(path.read_text())
    route = catalog["routes"][0]
    if mutation == "foreign_skill":
        route["skill"] = "product-discovery"
    elif mutation == "foreign_condition":
        route["condition"] = "customer_evidence_recorded"
    elif mutation == "role_without_catalog":
        route["role"] = "pd_reviewer"
    elif mutation == "empty_role":
        route["role"] = ""
    elif mutation == "duplicate":
        catalog["routes"].append(dict(route))
    else:
        route["skill"] = "../../outside"
    path.write_text(json.dumps(catalog))
    assert any("routes.json" in error for error in validate_portable_plugin(root, SCHEMA))
