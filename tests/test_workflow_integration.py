"""Author ownership and exposed MCP contracts for the optional workflow adapter."""
from __future__ import annotations

import io
import json
import shutil
from pathlib import Path

import pytest
from build_codex_package import projection, write_generated
from jsonschema import Draft202012Validator
from server import Server

from author_checks.plugin_validation import validate_portable_plugin

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/agent-plugins-1.0.0.schema.json").read_text())


@pytest.mark.parametrize("plugin", ["product-development", "project-management"])
def test_workflow_tools_have_valid_schemas_and_owned_targets(tmp_path: Path, plugin: str) -> None:
    package = tmp_path / "package"
    write_generated(package, projection(ROOT / "plugins" / plugin, "codex"))
    server = Server(io.StringIO(), io.StringIO(), root=package)
    tools = {tool["name"]: tool for tool in server.dispatch("tools/list", {})["tools"]}
    names = {"codex_workflow_task", "codex_workflow_evidence", "codex_workflow_route", "codex_workflow_status"}
    assert names <= tools.keys()
    for name in names:
        Draft202012Validator.check_schema(tools[name]["inputSchema"])
        assert tools[name]["annotations"]["readOnlyHint"] == (name == "codex_workflow_status")
    routes = json.loads((package / "com.openai/hooks/routes.json").read_text())["routes"]
    roles = {role["name"] for role in json.loads((package / "com.openai/agents/catalog.json").read_text())["roles"]}
    for route in routes:
        assert (package / "skills" / route["skill"] / "SKILL.md").is_file()
        assert route["role"] in roles
    authored = json.loads((package / "com.openai/hooks/hooks.json").read_text())["hooks"]
    for event in ("SessionStart", "PreToolUse", "PostToolUse", "Stop", "Interrupt"):
        commands = [handler for row in authored[event] for handler in row["hooks"]
                    if handler["type"] == "command" and "workflow_hook.py" in handler["command"]]
        assert len(commands) == 1
        assert commands[0]["timeout"] <= (1 if event == "Interrupt" else 5)


def test_optional_adapter_does_not_advertise_unconfigured_routes(tmp_path: Path) -> None:
    package = tmp_path / "package"
    write_generated(package, projection(ROOT / "plugins/product-development", "portable"))
    (package / "com.openai/hooks/routes.json").unlink()
    server = Server(io.StringIO(), io.StringIO(), root=package)
    assert not any(tool["name"].startswith("codex_workflow_")
                   for tool in server.dispatch("tools/list", {})["tools"])


def test_workflow_wire_errors_do_not_disclose_malformed_input(tmp_path: Path) -> None:
    package = tmp_path / "package"
    write_generated(package, projection(ROOT / "plugins/product-development", "portable"))
    request = {"id": 7, "method": "tools/call", "params": {
        "name": "codex_workflow_task", "arguments": {"task": {"secret": "private fixture token"}},
    }}
    output = io.StringIO()
    assert Server(io.StringIO(json.dumps(request) + "\n"), output, root=package).run() == 0
    response = json.loads(output.getvalue())
    assert response["id"] == 7 and "error" in response
    assert "private fixture token" not in output.getvalue()
    assert not (tmp_path / "agent-plugin-state").exists()


@pytest.mark.parametrize("mutation", ["foreign_skill", "foreign_role", "duplicate", "escaping_skill", "unknown_condition"])
def test_author_validation_rejects_broken_route_ownership(tmp_path: Path, mutation: str) -> None:
    package = tmp_path / "package"
    shutil.copytree(ROOT / "plugins/product-development", package)
    path = package / "com.openai/hooks/routes.json"
    data = json.loads(path.read_text())
    route = data["routes"][0]
    if mutation == "foreign_skill":
        route["skill"] = "project-governance"
    elif mutation == "foreign_role":
        route["role"] = "pm_governance_auditor"
    elif mutation == "duplicate":
        data["routes"].append(dict(route))
    elif mutation == "escaping_skill":
        route["skill"] = "../../outside"
    else:
        route["condition"] = "agent_stopped"
    path.write_text(json.dumps(data))
    errors = validate_portable_plugin(package, SCHEMA)
    assert any("routes.json" in error for error in errors)
