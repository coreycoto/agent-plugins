from __future__ import annotations

import io
import json
import re
import tomllib
from pathlib import Path

import pytest
from build_codex_package import check, write_generated
from build_codex_package import projection as package_projection
from jsonschema import ValidationError
from manager import MARKER, AgentError, Manager, role_assets
from render_codex_agents import RECEIPT, matches, projection, write_new
from server import Server, onboard

ROOT = Path(__file__).resolve().parents[1]


def make_manager(tmp_path: Path, plugin: str) -> Manager:
    source = tmp_path / plugin
    write_generated(source, package_projection(ROOT / "plugins" / plugin, "portable"))
    repo = tmp_path / "repo"
    repo.mkdir(exist_ok=True)
    (repo / ".git").mkdir(exist_ok=True)
    return Manager(source, tmp_path / "user/.codex", repo)


def consent(scope="user"):
    return lambda *_: {"action": "accept", "content": {"scope": scope, "confirm": True}}


def test_plugins_install_and_upgrade_independent_owned_roles(tmp_path: Path) -> None:
    pd = make_manager(tmp_path, "product-development")
    pm = make_manager(tmp_path, "project-management")
    assert onboard(pd, "session", {"elicitation": {"form": {}}}, consent())["result"] == "installed"
    before = {path.name: path.read_bytes() for path in pd.target("user").iterdir()}
    assert onboard(pm, "session", {"elicitation": {"form": {}}}, consent())["result"] == "installed"
    assert pd.plans()["user"]["state"] == pm.plans()["user"]["state"] == "ready"
    assert pd.target("user") != pm.target("user") and pd.state_dir() != pm.state_dir()
    assert {role["name"] for role in pd.roles}.isdisjoint({role["name"] for role in pm.roles})
    catalog = pm.root / "com.openai/agents/catalog.json"
    data = json.loads(catalog.read_bytes())
    data["guidance"] += " Revised routing."
    catalog.write_text(json.dumps(data))
    revised = Manager(pm.root, pm.home, pm.cwd)
    assert revised.plans()["user"]["state"] == "upgrade_available"
    assert onboard(revised, "upgrade", {"elicitation": {"form": {}}}, consent())["result"] == "upgraded"
    assert {path.name: path.read_bytes() for path in pd.target("user").iterdir()} == before
    # A marker for another plugin cannot acquire this plugin's files.
    marker = pm.target("user") / MARKER
    data = json.loads(marker.read_bytes())
    data["owner"] = pd.owner
    marker.write_text(json.dumps(data))
    assert revised.plans()["user"]["state"] == "conflict"


def test_pm_form_is_owned_and_decline_preserves_everything(tmp_path: Path) -> None:
    pm = make_manager(tmp_path, "project-management")
    def decline(method, params):
        assert method == "openai/elicitation/create"
        assert "Set up Project Management agents" in params["message"]
        assert "Product Development" not in params["message"]
        assert pm.install_summary in params["message"]
        return {"action": "decline"}
    assert onboard(pm, "session", {"extensions": {"openai/elicitation": {"form": {}}}}, decline)["result"] == "deferred"
    assert not pm.home.exists()
    server = Server(io.StringIO(), io.StringIO(), root=pm.root)
    result = server.dispatch("initialize", {"capabilities": {}})
    assert result["serverInfo"] == {"name": "project-management-agents", "version": "0.9.0"}


@pytest.mark.parametrize("plugin,prefix", [("product-development", "pd"), ("project-management", "pm")])
def test_every_owned_role_matches_native_receipt_hook_and_generated_package(tmp_path: Path, plugin: str, prefix: str) -> None:
    source = ROOT / "plugins" / plugin
    catalog, _, roles = role_assets(source)
    assert catalog["namespace"] == prefix
    hooks = json.loads((source / "com.openai/hooks/hooks.json").read_bytes())["hooks"]
    matchers = [row["matcher"] for row in hooks["SubagentStart"]]
    for role in roles:
        assert role["name"].startswith(prefix + "_")
        assert any(re.search(matcher, role["name"]) for matcher in matchers)
    assert not any(re.search(matcher, "unrelated_role") for matcher in matchers)
    package = tmp_path / plugin
    write_generated(package, package_projection(source))
    assert check(source, package)


def test_pm_owned_model_and_write_contracts() -> None:
    source = ROOT / "plugins/project-management/com.openai/agents"
    expected = {
        "pm_dependency_maintainer": ("gpt-6.1-sol", "workspace-write"),
        "pm_documentation_steward": ("gpt-6-luna", "workspace-write"),
        "pm_governance_auditor": ("gpt-6.1-sol", "read-only"),
        "pm_merge_reviewer": ("gpt-6.1-sol", "read-only"),
        "pm_release_preparer": ("gpt-6.1-sol", "workspace-write"),
    }
    for name, (model, sandbox) in expected.items():
        role = tomllib.loads((source / (name + ".toml")).read_text())
        assert (role["model"], role["model_reasoning_effort"], role["sandbox_mode"]) == (model, "high", sandbox)
        assert "$project-management:" in role["developer_instructions"]
        assert "pd_" not in role["developer_instructions"]
        assert "parent's live permissions" in role["developer_instructions"]


def test_projection_selects_owning_plugin_without_borrowing_roles() -> None:
    project = {"schemaVersion": 1, "plugin": "project-management", "sourceRevision": "a" * 40,
               "roles": {"dependency_patcher": {"sourceRole": "pm_dependency_maintainer", "file": "dependency-patcher.toml"}}}
    files = projection(project)
    assert "dependency-patcher.toml" in files
    assert json.loads(files[RECEIPT.format(plugin="project-management")])["source"] == "coreycoto/agent-plugins:project-management"
    project["roles"]["dependency_patcher"]["sourceRole"] = "pd_implementer"
    with pytest.raises(ValueError, match="absent"):
        projection(project)
    project["plugin"] = "../product-development"
    with pytest.raises(ValidationError):
        projection(project)


def test_namespace_mismatch_is_rejected(tmp_path: Path) -> None:
    pm = make_manager(tmp_path, "project-management")
    path = pm.root / "com.openai/agents/catalog.json"
    data = json.loads(path.read_bytes())
    data["namespace"] = "pd"
    path.write_text(json.dumps(data))
    with pytest.raises(AgentError, match="namespaced"):
        Manager(pm.root, pm.home, pm.cwd)


def test_multiple_plugin_projections_coexist_in_one_consumer_directory(tmp_path: Path) -> None:
    pd = projection({"schemaVersion": 1, "plugin": "product-development", "sourceRevision": "a" * 40,
                     "roles": {"code_reviewer": {"sourceRole": "pd_reviewer"}}})
    pm = projection({"schemaVersion": 1, "plugin": "project-management", "sourceRevision": "a" * 40,
                     "roles": {"merge_reviewer": {"sourceRole": "pm_merge_reviewer"}}})
    assert pd.keys().isdisjoint(pm.keys())
    write_new(tmp_path, {**pd, **pm})
    assert matches(tmp_path, pd) and matches(tmp_path, pm)
