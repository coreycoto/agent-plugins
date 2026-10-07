from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

import manager as manager_module
import pytest
from build_codex_package import check, projection, write_generated
from jsonschema import ValidationError, validate
from manager import MARKER, AgentError, Manager
from server import Server, onboard

PLUGIN = Path(__file__).resolve().parents[1] / "plugins/product-development"
HOOK_SCHEMA = json.loads((Path(__file__).parent / "fixtures/codex-session-start-output.schema.json").read_text())


def hook_context(response: dict) -> str:
    payload = response["structuredContent"]
    validate(payload, HOOK_SCHEMA)
    text_payload = json.loads(response["content"][0]["text"])
    validate(text_payload, HOOK_SCHEMA)
    assert text_payload == payload
    return payload["hookSpecificOutput"]["additionalContext"]


@pytest.fixture
def manager(tmp_path: Path) -> Manager:
    package = tmp_path / "plugin"
    write_generated(package, projection(PLUGIN, "portable"))
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    return Manager(package, tmp_path / "user/.codex", repo)


def choose(scope: str, confirm: object = True):
    return lambda *_: {"action": "accept", "content": {"scope": scope, "confirm": confirm}}


def install(manager: Manager, scope="user", session="install-session") -> dict:
    return onboard(manager, session, {"elicitation": {"form": {}}}, choose(scope))


def trust_project(manager: Manager) -> None:
    manager.home.mkdir(parents=True, exist_ok=True)
    (manager.home / "config.toml").write_text(
        f"[projects.{json.dumps(str(manager.repo))}]\ntrust_level = \"trusted\"\n")


def upgrade_source(manager: Manager, number=None) -> Manager:
    if number is None:
        major, minor, patch = (int(part) for part in manager.version.split("."))
        number = f"{major}.{minor}.{patch + 1}"
    path = manager.root / "plugin.json"
    data = json.loads(path.read_bytes())
    data["version"] = number
    path.write_text(json.dumps(data))
    role = manager.root / "com.openai/agents/pd_reviewer.toml"
    role.write_text(role.read_text() + '\n# Revised reviewed asset.\n')
    return Manager(manager.root, manager.home, manager.cwd)


def tree(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_shared_install_preserves_unrelated_config_and_roles(manager: Manager) -> None:
    directory = manager.home / "agents"
    directory.mkdir(parents=True)
    directory.chmod(0o755)
    unrelated = directory / "other.toml"
    unrelated.write_text('name = "other"\n')
    config = manager.home / "config.toml"
    original = b'# preserve comments\nmodel = "gpt-6.1-sol"\n[agents]\nmax_threads = 4\n'
    config.write_bytes(original)
    result = install(manager)
    assert result["result"] == "installed" and result["restartRequired"]
    assert config.read_bytes() == original
    assert unrelated.read_text() == 'name = "other"\n'
    assert directory.stat().st_mode & 0o777 == 0o755
    assert len(list(manager.target("user").glob("*.toml"))) == 6
    assert not manager.target("project").exists()
    assert manager.status("install-session")["session"]["verification"] == "pending"


def test_project_scope_does_not_write_user_configuration(manager: Manager) -> None:
    trust_project(manager)
    original = tree(manager.cwd)
    original_user = tree(manager.home)
    result = install(manager, "project")
    assert result["result"] == "installed"
    assert tree(manager.home) == original_user
    assert not (manager.cwd / ".codex/config.toml").exists()
    assert len(list((manager.cwd / ".codex/agents").rglob("*.toml"))) == 6
    assert all(manager.cwd.joinpath(path).read_bytes() == data for path, data in original.items())
    assert manager.plans()["project"]["state"] == "ready"


@pytest.mark.parametrize("response", [
    {"action": "decline"}, {"action": "cancel"},
    {"action": "accept", "content": {"scope": "later", "confirm": False}},
    {"action": "accept", "content": {"scope": "user", "confirm": 1}},
    {"action": "accept", "content": {"scope": "user", "confirm": False}},
    {"action": "accept", "content": {"scope": "elsewhere", "confirm": True}},
    {"action": "accept", "content": {"scope": "user", "confirm": True, "extra": True}},
])
def test_no_valid_form_consent_means_no_writes(manager: Manager, response: dict) -> None:
    before = tree(manager.root.parent)
    result = onboard(manager, "session", {"elicitation": {"form": {}}}, lambda *_: response)
    assert result["result"] == "deferred"
    assert tree(manager.root.parent) == before
    assert not manager.home.exists()


@pytest.mark.parametrize("capabilities", [{}, {"extensions": {"openai/form": {}}}])
def test_missing_supported_form_capability_defers_without_side_effects(manager: Manager, capabilities) -> None:
    before = tree(manager.root.parent)
    result = onboard(manager, "session", capabilities, lambda *_: pytest.fail("no supported form capability"))
    assert result["result"] == "form_unavailable"
    assert tree(manager.root.parent) == before
    assert not manager.home.exists()


@pytest.mark.parametrize("capabilities,method", [
    ({"extensions": {"openai/elicitation": {"form": {}}}}, "openai/elicitation/create"),
    ({"extensions": {"openai/form": {}, "openai/elicitation": {"form": {}}}}, "openai/elicitation/create"),
    ({"extensions": {"openai/form": {}}, "elicitation": {"form": {}}}, "elicitation/create"),
    ({"elicitation": {"form": {}}}, "elicitation/create"),
])
def test_negotiated_form_method_and_reviewable_scope_preview(manager: Manager, capabilities, method) -> None:
    trust_project(manager)
    def check(actual_method, params):
        assert actual_method == method
        assert str(manager.target("user")) in params["message"]
        assert str(manager.target("project")) in params["message"]
        assert all(role["model"] in params["message"] for role in manager.roles)
        assert [option["const"] for option in params["requestedSchema"]["properties"]["scope"]["oneOf"]] == ["user", "project", "later"]
        assert all(option["title"] for option in params["requestedSchema"]["properties"]["scope"]["oneOf"])
        assert params["mode"] == "form"
        return {"action": "decline"}
    assert onboard(manager, "session", capabilities, check)["result"] == "deferred"


@pytest.mark.parametrize("invalid", [
    {"scope": "user"},
    {"scope": "user", "confirm": 1},
    {"scope": "user", "confirm": True, "extra": True},
])
def test_documented_form_schema_does_not_coerce_or_default_consent(manager: Manager, invalid: dict) -> None:
    before = tree(manager.root.parent)
    def inspect_schema(method, params):
        assert method == "openai/elicitation/create"
        schema = params["requestedSchema"]
        assert schema["properties"]["confirm"]["default"] is False
        validate({"scope": "user", "confirm": True}, schema)
        validate({"scope": "later", "confirm": False}, schema)
        if "extra" in invalid:
            # MCP's form-schema subset has no additionalProperties constraint.
            # The installer independently rejects unknown submitted fields.
            validate(invalid, schema)
        else:
            with pytest.raises(ValidationError):
                validate(invalid, schema)
        with pytest.raises(ValidationError):
            validate({"scope": "project", "confirm": True}, schema)
        return {"action": "accept", "content": invalid}
    result = onboard(manager, "session", {"extensions": {"openai/elicitation": {"form": {}}}}, inspect_schema)
    assert result["result"] == "deferred"
    assert result["formMethod"] == "openai/elicitation/create"
    assert tree(manager.root.parent) == before


@pytest.mark.parametrize("trust", [None, "untrusted"])
def test_project_requires_shared_trust_before_offer_or_install(manager: Manager, trust) -> None:
    if trust is not None:
        trust_project(manager)
        config = manager.home / "config.toml"
        config.write_text(config.read_text().replace('"trusted"', '"untrusted"'))
    before = tree(manager.root.parent)
    def reject_project_choice(_method, params):
        assert [option["const"] for option in params["requestedSchema"]["properties"]["scope"]["oneOf"]] == ["user", "later"]
        return choose("project")()
    result = onboard(manager, "session", {"elicitation": {"form": {}}}, reject_project_choice)
    assert result["result"] == "deferred"
    assert manager.plans()["project"]["state"] == "conflict"
    assert tree(manager.root.parent) == before


def test_project_local_configuration_cannot_grant_its_own_trust(manager: Manager) -> None:
    config = manager.cwd / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(f"[projects.{json.dumps(str(manager.repo))}]\ntrust_level = \"trusted\"\n")
    assert manager.plans()["project"]["state"] == "conflict"
    assert not manager.project_trusted()


def test_project_trust_revoked_during_form_invalidates_plan(manager: Manager) -> None:
    trust_project(manager)
    def revoke(*_):
        config = manager.home / "config.toml"
        config.write_text(config.read_text().replace('"trusted"', '"untrusted"'))
        return choose("project")()
    with pytest.raises(AgentError, match="plan changed"):
        onboard(manager, "session", {"elicitation": {"form": {}}}, revoke)
    assert not manager.target("project").exists()
    assert not manager.state_dir("project").exists()


def test_trusted_repository_root_covers_nested_working_directory(manager: Manager) -> None:
    trust_project(manager)
    nested = manager.cwd / "nested"
    nested.mkdir()
    scoped = Manager(manager.root, manager.home, nested)
    assert scoped.repo == manager.repo and scoped.project_trusted()
    assert install(scoped, "project")["result"] == "installed"


def test_upgrade_backs_up_owned_files_outside_discovery_tree(manager: Manager) -> None:
    install(manager)
    before = tree(manager.target("user"))
    newer = upgrade_source(manager)
    result = install(newer, session="upgrade-session")
    assert result["result"] == "upgraded"
    assert tree(Path(result["backup"])) == before
    assert not Path(result["backup"]).is_relative_to(manager.home / "agents")
    assert len(list((manager.home / "agents").rglob("*.toml"))) == 6
    assert newer.plans()["user"]["state"] == "ready"
    repeated = onboard(newer, "session", {}, lambda *_: pytest.fail("already registered"))
    assert repeated["result"] == "registered"


def test_locally_edited_owned_role_blocks_upgrade_without_overwrite(manager: Manager) -> None:
    install(manager)
    role = manager.target("user") / "pd_reviewer.toml"
    role.write_text(role.read_text() + '\n# Personal edit to retain.\n')
    before = tree(manager.home)
    newer = upgrade_source(manager)
    assert install(newer)["result"] == "conflict"
    assert tree(manager.home) == before


def test_catalog_growth_upgrades_three_owned_roles_with_fresh_consent(manager: Manager) -> None:
    catalog = manager.root / "com.openai/agents/catalog.json"
    expanded = catalog.read_bytes()
    original = json.loads(expanded)
    original["roles"] = [entry for entry in original["roles"] if entry["name"] in {
        "pd_explorer", "pd_reviewer", "pd_architecture_adviser"}]
    catalog.write_text(json.dumps(original))
    previous = Manager(manager.root, manager.home, manager.cwd)
    previous.home.mkdir(parents=True)
    config = previous.home / "config.toml"
    config.write_text('# Preserve user settings.\n[agents]\nmax_threads = 4\n')
    unrelated = previous.home / "agents/unrelated.toml"
    unrelated.parent.mkdir()
    unrelated.write_text('name = "unrelated"\n')
    assert install(previous)["result"] == "installed"
    assert previous.record_start({"session_id": "install-session", "agent_type": "pd_explorer", "agent_id": "old-child"})
    before = tree(previous.home)
    owned_before = tree(previous.target("user"))
    catalog.write_bytes(expanded)

    assert manager.version == previous.version
    assert manager.plans()["user"]["state"] == "upgrade_available"
    assert onboard(manager, "declined-upgrade", {"elicitation": {"form": {}}},
                   lambda *_: {"action": "decline"})["result"] == "deferred"
    assert tree(manager.home) == before

    def approve(_method, params):
        assert "can edit assigned files" in params["message"]
        assert "diagnosis can write temporary output" in params["message"]
        assert "inherit the current chat's permissions" in params["message"]
        assert "For read-only work." not in params["message"]
        return choose("user")()

    result = onboard(manager, "install-session", {"elicitation": {"form": {}}}, approve)
    assert result["result"] == "upgraded" and result["restartRequired"]
    assert tree(Path(result["backup"])) == owned_before
    assert len(list(manager.target("user").glob("*.toml"))) == 6
    assert config.read_bytes() == before["config.toml"]
    assert unrelated.read_bytes() == before["agents/unrelated.toml"]
    assert manager.status("install-session")["session"]["verification"] == "pending"


@pytest.mark.parametrize("sandbox", ["danger-full-access", "external-sandbox", "unknown"])
def test_packaged_role_cannot_expand_to_an_unrestricted_sandbox(manager: Manager, sandbox: str) -> None:
    role = manager.root / "com.openai/agents/pd_implementer.toml"
    role.write_text(role.read_text().replace('sandbox_mode = "workspace-write"', f'sandbox_mode = "{sandbox}"'))
    with pytest.raises(AgentError, match="sandbox default"):
        Manager(manager.root, manager.home, manager.cwd)
    assert not manager.home.exists()


def test_purpose_specific_routing_has_expected_models_and_defaults(manager: Manager) -> None:
    assert {role["name"]: (role["model"], role["effort"], role["sandboxMode"])
            for role in manager.roles} == {
        "pd_explorer": ("gpt-6-luna", "high", "read-only"),
        "pd_reviewer": ("gpt-6.1-sol", "high", "read-only"),
        "pd_implementer": ("gpt-6.1-sol", "high", "workspace-write"),
        "pd_diagnostician": ("gpt-6.1-sol", "high", "workspace-write"),
        "pd_transformer": ("gpt-6-luna", "high", "workspace-write"),
        "pd_architecture_adviser": ("gpt-6-astra", "medium", "read-only"),
    }


@pytest.mark.parametrize("explicit", [True, False])
def test_existing_role_name_blocks_install(manager: Manager, explicit: bool) -> None:
    manager.home.mkdir(parents=True)
    if explicit:
        path = manager.home / "config.toml"
        path.write_text('[agents.pd_reviewer]\nconfig_file = "personal.toml"\n')
    else:
        path = manager.home / "agents/personal.toml"
        path.parent.mkdir()
        path.write_text('name = "pd_reviewer"\n')
    before = tree(manager.home)
    assert install(manager)["result"] == "conflict"
    assert tree(manager.home) == before


def test_downgrade_is_not_offered(manager: Manager) -> None:
    install(manager)
    older = upgrade_source(manager, "0.7.0")
    before = tree(manager.home)
    assert install(older)["result"] == "conflict"
    assert older.plans()["user"]["state"] == "downgrade_blocked"
    assert tree(manager.home) == before


def test_form_time_drift_invalidates_plan_before_any_role_write(manager: Manager) -> None:
    def race(*_):
        target = manager.target("user")
        target.mkdir(parents=True)
        (target / "keep.txt").write_text("Unowned file created during review.")
        return choose("user")()
    with pytest.raises(AgentError, match="plan changed"):
        onboard(manager, "session", {"elicitation": {"form": {}}}, race)
    assert tree(manager.target("user")) == {"keep.txt": b"Unowned file created during review."}
    assert not manager.state_dir().exists()


def test_upgrade_publication_failure_restores_previous_install(manager: Manager, monkeypatch) -> None:
    install(manager)
    before = tree(manager.target("user"))
    newer = upgrade_source(manager)
    rename = os.rename
    def fail_stage(source, destination):
        if Path(source).name.startswith("stage-"):
            raise OSError("Simulated filesystem failure")
        return rename(source, destination)
    monkeypatch.setattr(os, "rename", fail_stage)
    with pytest.raises(OSError, match="Simulated"):
        install(newer)
    assert tree(manager.target("user")) == before
    assert not (manager.state_dir() / "install.lock").exists()


def test_staging_time_conflict_preserves_new_unowned_target(manager: Manager, monkeypatch) -> None:
    original_write = manager_module.private_write
    def race(path, data):
        original_write(path, data)
        if path.name == MARKER:
            target = manager.target("user")
            target.mkdir(parents=True)
            (target / "keep.txt").write_text("Keep the file created during staging.")
    monkeypatch.setattr(manager_module, "private_write", race)
    with pytest.raises(AgentError, match="changed during staging"):
        install(manager)
    assert tree(manager.target("user")) == {"keep.txt": b"Keep the file created during staging."}


def test_install_lock_prevents_overlapping_write(manager: Manager) -> None:
    state = manager.state_dir()
    state.mkdir(parents=True)
    (state / "install.lock").mkdir()
    with pytest.raises(AgentError, match="Another install"):
        install(manager)
    assert not manager.target("user").exists()
    assert (state / "install.lock").exists()


def test_symlink_target_and_escaping_source_are_rejected(manager: Manager, tmp_path: Path) -> None:
    target = manager.target("user")
    target.parent.mkdir(parents=True)
    target.symlink_to(tmp_path / "outside", target_is_directory=True)
    with pytest.raises(AgentError, match="Symlink"):
        install(manager)
    target.unlink()
    asset = manager.root / "com.openai/agents/pd_explorer.toml"
    outside = tmp_path / "outside.toml"
    asset.rename(outside)
    asset.symlink_to(outside)
    with pytest.raises(ValueError):
        Manager(manager.root, manager.home, manager.cwd)


@pytest.mark.parametrize("session", ["install-session", "fresh-session"])
def test_native_selection_receipt_tracks_same_or_new_chat_and_current_assets(manager: Manager, session) -> None:
    install(manager)
    resumed = Manager(manager.root, manager.home, manager.cwd)
    assert resumed.status(session)["session"]["verification"] == "pending"
    event = {"session_id": session, "agent_type": "pd_explorer", "agent_id": "child-1"}
    assert resumed.record_start(event)
    status = resumed.status(session)
    assert status["session"]["nativeRoleSelections"] == ["pd_explorer"]
    assert status["session"]["verification"] == "role_selection_observed"
    assert resumed.status("other-session")["session"]["verification"] == "pending"
    newer = upgrade_source(manager)
    assert newer.status(session)["session"]["verification"] == "pending"


def test_hook_handles_missing_server_and_does_not_leak_config(manager: Manager) -> None:
    manager.home.mkdir(parents=True)
    (manager.home / "config.toml").write_text('private_value = "fixture-private-value"\n')
    event = {"hook_event_name": "SessionStart", "cwd": str(manager.cwd), "session_id": "session"}
    result = subprocess.run([sys.executable, str(manager.root / "com.openai/codex_agents/hook.py")],
                            input=json.dumps(event), text=True, capture_output=True, check=True,
                            env={**os.environ, "CODEX_HOME": str(manager.home), "PYTHONDONTWRITEBYTECODE": "1"})
    output = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "pd_explorer" in output and "unverified" in output
    assert "fixture-private-value" not in output
    assert not manager.target("user").exists()


@pytest.mark.parametrize("capabilities,method", [
    ({"extensions": {"openai/elicitation": {"form": {}}}}, "openai/elicitation/create"),
    ({"elicitation": {"form": {}}}, "elicitation/create"),
])
def test_mcp_wire_form_and_decline_are_not_reprompted(manager: Manager, monkeypatch, capabilities, method) -> None:
    monkeypatch.setattr(Manager, "from_environment", lambda _: manager)
    call = {"method": "tools/call", "params": {"name": "codex_agents_onboard", "arguments": {
        "cwd": str(manager.cwd), "session_id": "session"}}}
    input_stream = io.StringIO("\n".join(json.dumps(message) for message in [
        {"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "codex-test"}, "capabilities": capabilities}},
        {"id": 2, **call}, {"id": "pd-form-1", "result": {"action": "decline"}},
        {"id": 3, **call},
    ]) + "\n")
    output = io.StringIO()
    assert Server(input_stream, output, root=manager.root).run() == 0
    messages = [json.loads(line) for line in output.getvalue().splitlines()]
    forms = [message for message in messages if message.get("method") == method]
    assert len(forms) == 1 and forms[0]["params"]["mode"] == "form"
    assert "Onboarding result: deferred" in hook_context(messages[-1]["result"])
    assert not manager.home.exists()


def test_non_codex_client_cannot_prompt_or_install(manager: Manager, monkeypatch) -> None:
    monkeypatch.setattr(Manager, "from_environment", lambda _: manager)
    server = Server(io.StringIO(), io.StringIO(), root=manager.root)
    server.dispatch("initialize", {"clientInfo": {"name": "other-client"}, "capabilities": {"elicitation": {"form": {}}}})
    result = server.dispatch("tools/call", {"name": "codex_agents_onboard", "arguments": {
        "cwd": str(manager.cwd), "session_id": "session"}})
    assert "Onboarding result: client_unsupported" in hook_context(result)
    assert not manager.home.exists()


@pytest.mark.parametrize("request_id", [2, "pd-form-1", "unrelated-request"])
def test_mcp_form_cancellation_only_matches_its_active_requests(manager: Manager, monkeypatch, request_id) -> None:
    monkeypatch.setattr(Manager, "from_environment", lambda _: manager)
    requests = [
        {"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "codex-test"}, "capabilities": {"elicitation": {"form": {}}}}},
        {"id": 2, "method": "tools/call", "params": {"name": "codex_agents_onboard", "arguments": {
            "cwd": str(manager.cwd), "session_id": "session"}}},
        {"method": "notifications/cancelled", "params": {"requestId": request_id}},
    ]
    if request_id == "unrelated-request":
        requests.append({"id": "pd-form-1", "result": choose("user")()})
    output = io.StringIO()
    input_stream = io.StringIO("\n".join(json.dumps(r) for r in requests) + "\n")
    assert Server(input_stream, output, root=manager.root).run() == 0
    messages = [json.loads(line) for line in output.getvalue().splitlines()]
    result = next(m["result"] for m in messages if m.get("id") == 2)
    if request_id == "unrelated-request":
        assert "Onboarding result: installed" in hook_context(result)
        assert manager.plans()["user"]["state"] == "ready"
    else:
        assert "Onboarding result: deferred" in hook_context(result)
        assert not manager.home.exists()


@pytest.mark.parametrize("outcome", ["installed", "registered", "upgraded", "deferred",
                                     "form_unavailable", "conflict", "client_unsupported"])
def test_onboarding_obeys_native_hook_schema_and_status_stays_detailed(manager: Manager, monkeypatch, outcome) -> None:
    if outcome in {"registered", "upgraded"}:
        install(manager)
        if outcome == "upgraded":
            manager = upgrade_source(manager)
    elif outcome == "conflict":
        manager.home.mkdir(parents=True)
        (manager.home / "config.toml").write_text('[agents.pd_explorer]\nconfig_file = "existing.toml"\n')
    monkeypatch.setattr(Manager, "from_environment", lambda _: manager)
    server = Server(io.StringIO(), io.StringIO(), root=manager.root)
    server.dispatch("initialize", {"clientInfo": {
        "name": "other-client" if outcome == "client_unsupported" else "codex-test"},
        "capabilities": {} if outcome == "form_unavailable" else {"elicitation": {"form": {}}}})
    server.request_form = lambda *_: {"action": "decline"} if outcome == "deferred" else choose("user")()
    args = {"cwd": str(manager.cwd), "session_id": "schema-session"}
    response = server.dispatch("tools/call", {"name": "codex_agents_onboard", "arguments": args})
    assert "Onboarding result: " + outcome in hook_context(response)
    status = server.dispatch("tools/call", {"name": "codex_agents_status", "arguments": args})
    assert status["structuredContent"]["roles"] == manager.roles
    assert status["structuredContent"]["installations"] == manager.plans()


def test_catalog_and_hooks_are_bundled_and_onboarding_is_discoverable() -> None:
    manifest = json.loads((PLUGIN / "plugin.json").read_bytes())
    extension = manifest["extensions"]["com.openai"]
    assert (PLUGIN / extension["onboardingSkill"]).is_file()
    hooks = json.loads((PLUGIN / extension["hooks"]).read_bytes())["hooks"]
    assert any(hook["type"] == "command" for row in hooks["SessionStart"] for hook in row["hooks"])
    assert any(hook["type"] == "mcp_tool" for row in hooks["SessionStart"] for hook in row["hooks"])
    assert "SubagentStart" in hooks
    assert MARKER not in {path.name for path in PLUGIN.rglob("*")}


def test_codex_compatibility_package_matches_authored_source(tmp_path: Path) -> None:
    package = tmp_path / "package"
    write_generated(package, projection(PLUGIN))
    assert check(PLUGIN, package)
    assert not (package / "plugin.json").exists()  # 0.160 must select its legacy hook loader.
    manifest = json.loads((package / ".codex-plugin/plugin.json").read_bytes())
    assert manifest["name"] == "product-development"
    assert (package / manifest["hooks"]).is_file()
    mcp = json.loads((package / ".mcp.json").read_bytes())["mcpServers"]["product-development-agents"]
    assert mcp["cwd"] == "." and "${PLUGIN_ROOT}" not in " ".join(mcp["args"])
