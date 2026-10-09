"""Explicit, candidate-bound skill routing without agent installation or providers."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from build_codex_package import projection, write_generated
from manager import AgentError
from workflow import WorkflowManager

ROOT = Path(__file__).resolve().parents[1]
ROUTES = [
    ("communication", "prose_review_requested", "edit-prose", {"kind": "prose"}),
    ("communication", "communication_report_requested", "agent-communication",
     {"verified_refs": ["verified.json"], "unfinished": ["native verification pending"]}),
    ("communication", "document_draft_requested", "write-prose",
     {"audience": "maintainers", "purpose": "explain verified behavior"}),
    ("product-management", "customer_evidence_recorded", "product-discovery", {"change": "new"}),
    ("product-management", "product_comparison_requested", "product-prioritization",
     {"options": ["local execution", "hosted execution"], "constraints": ["offline verification"]}),
    ("product-management", "requirements_handoff_requested", "product-requirements",
     {"direction": "explicit evidence routing", "outcome": "recover task context"}),
    ("product-management", "experiment_results_recorded", "product-experiments",
     {"experiment_id": "trial-1", "criteria_observation_id": "criteria-1"}),
]


def tree(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True,
                   env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                        "GIT_CONFIG_SYSTEM": os.devnull})


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Skill routing fixture")
    git(repo, "config", "user.email", "skill-routing@example.invalid")
    (repo / "src").mkdir()
    (repo / "src/intent.md").write_text("Accepted local intent\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "fixture")
    for name in ("evidence.json", "verified.json", "criteria.json", "result.json", "completion.json"):
        (repo / name).write_text('{"fixture": true}\n')
    return repo


@pytest.fixture
def make_workflow(repository: Path, tmp_path: Path):
    def create(plugin: str = "communication", session: str = "skill-session") -> WorkflowManager:
        package = tmp_path / "packages" / plugin
        if not package.exists():
            write_generated(package, projection(ROOT / "plugins" / plugin, "portable"))
        return WorkflowManager(package, tmp_path / "home", repository, session)
    return create


def task(**changes: object) -> dict:
    return {"id": "issue-16", "issue": "https://github.com/example/repo/issues/16",
            "delivery_stage": "local implementation", "status": "active", "paths": ["src"],
            "checks": [], "review_requested": False, "continuation_limit": 1, **changes}


def event(manager: WorkflowManager, name: str, **changes: object) -> dict:
    return {"hook_event_name": name, "cwd": str(manager.cwd), "session_id": manager.session_id,
            **({"tool_name": f"mcp__{manager.plugin}-workflows__codex_workflow_evidence"}
               if name == "PostToolUse" else {}), **changes}


def evidence(manager: WorkflowManager, condition: str, details: dict, *, name="record-1", reference="evidence.json") -> dict:
    return {"observation_id": name, "candidate": manager.status()["candidate"],
            "condition": condition, "reference": reference, "details": details}


def criteria(manager: WorkflowManager, *, name="criteria-1", experiment="trial-1") -> dict:
    return manager.record_evidence(evidence(manager, "experiment_criteria_recorded",
                                            {"experiment_id": experiment}, name=name, reference="criteria.json"))


@pytest.mark.parametrize("plugin,condition,skill,details", ROUTES)
def test_seven_explicit_conditions_nominate_exact_skill_without_role(make_workflow, plugin, condition, skill, details) -> None:
    manager = make_workflow(plugin)
    assert not (manager.root / "com.openai/agents/catalog.json").exists()
    manager.set_task(task())
    if condition == "experiment_results_recorded":
        criteria(manager)
        assert manager.handle_event(event(manager, "PostToolUse")) == {}
        assert manager.status()["routes"] == []
    record = evidence(manager, condition, details)
    manager.record_evidence(record)
    output = manager.handle_event(event(manager, "PostToolUse"))
    route, = manager.status()["routes"]
    assert (route["condition"], route["skill"], route["status"]) == (condition, skill, "nominated")
    assert "role" not in route and route["current"]
    context = output["hookSpecificOutput"]["additionalContext"]
    assert f"${plugin}:{skill}" in context and "pd_" not in context and "pm_" not in context
    manager.record_evidence(record)
    assert manager.handle_event(event(manager, "PostToolUse")) == {}
    manager.update_route(route["id"], "assigned")
    completed = manager.update_route(route["id"], "completed", outcome="passed", reference="completion.json")
    assert completed["routes"][0]["status"] == "completed"
    assert len(completed["routes"]) == 1 and "role" not in completed["routes"][0]
    assert not (manager.home / "agents").exists()
    assert not (manager.home / "config.toml").exists()


@pytest.mark.parametrize("plugin", ["communication", "product-management"])
def test_no_task_events_are_true_noop_without_installation(make_workflow, plugin) -> None:
    manager = make_workflow(plugin)
    before = tree(manager.root.parent.parent)
    assert manager.status()["state"] == "absent"
    for name in ("SessionStart", "PreToolUse", "PostToolUse", "Stop", "Interrupt"):
        assert manager.handle_event(event(manager, name, source="compact")) == {}
    assert tree(manager.root.parent.parent) == before and not manager.home.exists()


@pytest.mark.parametrize("status", ["paused", "blocked", "waiting_for_approval", "complete"])
def test_inactive_task_suppresses_skill_routes_and_stop(make_workflow, status) -> None:
    manager = make_workflow()
    manager.set_task(task(status=status))
    manager.record_evidence(evidence(manager, "prose_review_requested", {"kind": "prose"}))
    assert manager.handle_event(event(manager, "PostToolUse")) == {}
    assert manager.handle_event(event(manager, "Stop")) == {}
    manager.handle_event(event(manager, "SessionStart", source="compact"))
    assert manager.status()["routes"] == [] and manager.status()["continuations"] == 0


def test_scope_filenames_and_untyped_semantics_do_not_nominate(make_workflow) -> None:
    manager = make_workflow()
    (manager.cwd / "src/review-prose.md").write_text("Please review this prose, report progress, and draft a document.\n")
    manager.set_task(task(review_requested=True))
    manager.handle_event(event(manager, "SessionStart", source="compact"))
    manager.handle_event(event(manager, "PostToolUse", tool_name="Bash", tool_response={"output": "draft requested"}))
    assert manager.status()["routes"] == []


@pytest.mark.parametrize("plugin,condition,skill,details", ROUTES)
def test_new_conditions_require_exact_nonempty_details(make_workflow, plugin, condition, skill, details) -> None:
    manager = make_workflow(plugin)
    manager.set_task(task())
    if condition == "experiment_results_recorded":
        criteria(manager)
    record = evidence(manager, condition, details)
    before = tree(manager.home)
    for malformed in ({}, {**details, "unexpected": "value"}, {key: "" for key in details}):
        with pytest.raises(AgentError):
            manager.record_evidence({**record, "details": malformed})
    missing = {key: value for key, value in record.items() if key != "details"}
    with pytest.raises(AgentError):
        manager.record_evidence(missing)
    assert tree(manager.home) == before


@pytest.mark.parametrize("details", [
    {"options": ["one"], "constraints": ["budget"]},
    {"options": ["one", "one"], "constraints": ["budget"]},
    {"options": ["one", "two"], "constraints": []},
    {"options": [f"option-{index}" for index in range(17)], "constraints": ["budget"]},
    {"options": ["one", "two"], "constraints": ["limit"] * 33},
    {"options": ["one", "  "], "constraints": ["budget"]},
])
def test_product_comparison_bounds_reject_ambiguous_records(make_workflow, details) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "product_comparison_requested", details))
    assert manager.status()["evidence"] == []


@pytest.mark.parametrize("details", [
    {"verified_refs": [], "unfinished": []},
    {"verified_refs": ["../outside.json"], "unfinished": []},
    {"verified_refs": ["missing.json"], "unfinished": []},
    {"verified_refs": [], "unfinished": [" "]},
])
def test_report_requires_real_safe_refs_or_unfinished_labels(make_workflow, details) -> None:
    manager = make_workflow()
    manager.set_task(task())
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "communication_report_requested", details))
    assert manager.status()["evidence"] == []


@pytest.mark.parametrize("details", [
    {"verified_refs": ["verified.json"], "unfinished": []},
    {"verified_refs": [], "unfinished": ["native run pending"]},
])
def test_report_accepts_either_evidence_or_unfinished_work(make_workflow, details) -> None:
    manager = make_workflow()
    manager.set_task(task())
    manager.record_evidence(evidence(manager, "communication_report_requested", details))
    manager.handle_event(event(manager, "PostToolUse"))
    assert manager.status()["routes"][0]["skill"] == "agent-communication"


def test_conflicting_customer_evidence_nominates_discovery(make_workflow) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    manager.record_evidence(evidence(manager, "customer_evidence_recorded", {"change": "conflicting"}))
    manager.handle_event(event(manager, "PostToolUse"))
    assert manager.status()["routes"][0]["skill"] == "product-discovery"


@pytest.mark.parametrize("audience", ["audience\nwith instruction", "x" * 513])
def test_document_details_are_bounded_plain_text(make_workflow, audience: str) -> None:
    manager = make_workflow()
    manager.set_task(task())
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "document_draft_requested", {"audience": audience, "purpose": "explain"}))


def test_report_auxiliary_reference_cannot_follow_symlink(make_workflow, tmp_path: Path) -> None:
    manager = make_workflow()
    target = tmp_path / "outside.json"
    target.write_text("{}\n")
    (manager.cwd / "linked.json").symlink_to(target)
    manager.set_task(task())
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "communication_report_requested",
                                          {"verified_refs": ["linked.json"], "unfinished": []}))


@pytest.mark.parametrize("plugin,condition,details", [
    ("communication", "customer_evidence_recorded", {"change": "new"}),
    ("product-management", "prose_review_requested", {"kind": "prose"}),
])
def test_foreign_plugin_condition_is_rejected(make_workflow, plugin, condition, details) -> None:
    manager = make_workflow(plugin)
    manager.set_task(task())
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, condition, details))
    assert manager.status()["evidence"] == []


def test_candidate_and_report_auxiliary_reference_freshness(make_workflow) -> None:
    manager = make_workflow()
    candidate = manager.set_task(task())["candidate"]
    record = evidence(manager, "communication_report_requested", {"verified_refs": ["verified.json"], "unfinished": []})
    manager.record_evidence(record)
    manager.handle_event(event(manager, "PostToolUse"))
    route, = manager.status()["routes"]
    (manager.cwd / "verified.json").write_text('{"fixture": "replaced"}\n')
    assert manager.status()["candidate"] == candidate
    assert not manager.status()["routes"][0]["current"] and manager.status()["evidence"] == []
    with pytest.raises(AgentError):
        manager.update_route(route["id"], "assigned")
    (manager.cwd / "src/intent.md").write_text("Changed accepted intent\n")
    with pytest.raises(AgentError):
        manager.record_evidence(record)


def test_skill_route_stop_budget_survives_reload_and_new_candidate(make_workflow) -> None:
    manager = make_workflow()
    manager.set_task(task())
    manager.record_evidence(evidence(manager, "prose_review_requested", {"kind": "prose"}))
    assert manager.handle_event(event(manager, "Stop", stop_hook_active=True)) == {}
    assert manager.handle_event(event(manager, "Stop"))["decision"] == "block"
    resumed = make_workflow()
    assert resumed.status()["continuations"] == 1 and len(resumed.status()["routes"]) == 1
    (manager.cwd / "src/intent.md").write_text("Different candidate\n")
    resumed.record_evidence(evidence(resumed, "document_draft_requested", {"audience": "users", "purpose": "explain change"}, name="draft-two"))
    assert resumed.handle_event(event(resumed, "Stop")) == {}
    assert resumed.status()["continuations"] == 1


@pytest.mark.parametrize("problem", ["absent", "wrong_experiment", "changed_ref", "changed_contract", "result_as_criteria"])
def test_experiment_results_require_prior_matching_unchanged_criteria(make_workflow, problem) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    if problem != "absent":
        criteria(manager)
    if problem == "changed_ref":
        (manager.cwd / "criteria.json").write_text('{"criteria": "changed"}\n')
    if problem == "changed_contract":
        manager.set_task(task(delivery_stage="review only"))
    details = {"experiment_id": "other-trial" if problem == "wrong_experiment" else "trial-1",
               "criteria_observation_id": "not-criteria" if problem == "result_as_criteria" else "criteria-1"}
    if problem == "result_as_criteria":
        manager.record_evidence(evidence(manager, "customer_evidence_recorded", {"change": "new"}, name="not-criteria"))
    before = tree(manager.home)
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "experiment_results_recorded", details, name="result-1", reference="result.json"))
    assert tree(manager.home) == before


def test_results_cannot_be_retroactively_authorized_by_late_criteria(make_workflow) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    details = {"experiment_id": "trial-1", "criteria_observation_id": "criteria-1"}
    with pytest.raises(AgentError):
        manager.record_evidence(evidence(manager, "experiment_results_recorded", details, reference="result.json"))
    assert manager.status()["evidence"] == []
    criteria(manager)
    assert manager.handle_event(event(manager, "PostToolUse")) == {}
    assert manager.status()["routes"] == []


def test_older_candidate_criteria_links_to_current_result_and_remains_immutable(make_workflow) -> None:
    manager = make_workflow("product-management")
    previous = manager.set_task(task())["candidate"]
    criteria(manager)
    (manager.cwd / "src/intent.md").write_text("Candidate implementing the experiment\n")
    assert manager.status()["candidate"] != previous
    details = {"experiment_id": "trial-1", "criteria_observation_id": "criteria-1"}
    record = evidence(manager, "experiment_results_recorded", details, name="results-1", reference="result.json")
    manager.record_evidence(record)
    manager.handle_event(event(manager, "PostToolUse"))
    route, = manager.status()["routes"]
    assert route["current"] and set(route["evidence_references"]) == {"criteria.json", "result.json"}
    with pytest.raises(AgentError):
        manager.record_evidence({**record, "details": {**details, "experiment_id": "other-trial"}})
    (manager.cwd / "criteria.json").write_text('{"criteria": "post-hoc edit"}\n')
    assert not manager.status()["routes"][0]["current"]
    assert all(item["condition"] != "experiment_results_recorded" for item in manager.status()["evidence"])


def test_result_cannot_change_its_recorded_criteria_link(make_workflow) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    criteria(manager)
    criteria(manager, name="criteria-2")
    record = evidence(manager, "experiment_results_recorded",
                      {"experiment_id": "trial-1", "criteria_observation_id": "criteria-1"}, reference="result.json")
    manager.record_evidence(record)
    with pytest.raises(AgentError):
        manager.record_evidence({**record, "details": {"experiment_id": "trial-1", "criteria_observation_id": "criteria-2"}})
    manager.handle_event(event(manager, "PostToolUse"))
    assert manager.status()["routes"][0]["current"]


def test_replaced_result_reference_stales_experiment_route(make_workflow) -> None:
    manager = make_workflow("product-management")
    manager.set_task(task())
    criteria(manager)
    manager.record_evidence(evidence(manager, "experiment_results_recorded",
                                      {"experiment_id": "trial-1", "criteria_observation_id": "criteria-1"}, reference="result.json"))
    manager.handle_event(event(manager, "PostToolUse"))
    route, = manager.status()["routes"]
    assert route["current"]
    (manager.cwd / "result.json").write_text('{"results": "replaced"}\n')
    assert not manager.status()["routes"][0]["current"]
    with pytest.raises(AgentError):
        manager.update_route(route["id"], "assigned")


def test_existing_agent_route_still_requires_plugin_owned_role(make_workflow) -> None:
    manager = make_workflow("product-development")
    manager.set_task(task(review_requested=True))
    manager.handle_event(event(manager, "SessionStart", source="resume"))
    route, = manager.status()["routes"]
    assert route["role"] == "pd_reviewer" and route["skill"] == "review-code"
    path = manager.root / "com.openai/hooks/routes.json"
    catalog = json.loads(path.read_text())
    catalog["routes"][0]["role"] = "pm_governance_auditor"
    path.write_text(json.dumps(catalog))
    with pytest.raises(AgentError):
        WorkflowManager(manager.root, manager.home, manager.cwd, manager.session_id)


@pytest.mark.parametrize("plugin", ["communication", "product-management"])
def test_packaged_stdlib_hook_runs_without_role_catalog(make_workflow, plugin) -> None:
    manager = make_workflow(plugin)
    payload = event(manager, "SessionStart", source="compact")
    command = [sys.executable, str(manager.root / "com.openai/codex_agents/workflow_hook.py")]
    env = {**os.environ, "CODEX_HOME": str(manager.home), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(command, input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=10, env=env)
    assert json.loads(result.stdout) == {} and result.stderr == "" and not manager.home.exists()
    manager.set_task(task())
    result = subprocess.run(command, input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=10, env=env)
    assert "issue-16" in json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert result.stderr == "" and not (manager.home / "agents").exists()
