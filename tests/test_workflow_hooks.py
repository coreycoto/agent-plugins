"""Offline workflow contracts through public operations and command-hook envelopes."""

from __future__ import annotations

import json
import os
import selectors
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from build_codex_package import projection, write_generated
from jsonschema import ValidationError, validate
from manager import AgentError
from workflow import EVIDENCE_SCHEMA, TASK_SCHEMA, WorkflowManager, dispatch

REPOSITORY = Path(__file__).resolve().parents[1]


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments], capture_output=True, text=True, check=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull},
    )
    return result.stdout.strip()


def tree(path: Path) -> dict[str, bytes]:
    return {
        str(item.relative_to(path)): item.read_bytes()
        for item in path.rglob("*") if item.is_file() and not item.is_symlink()
    }


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "workflow-fixture@example.invalid")
    git(repo, "config", "user.name", "Workflow fixture")
    (repo / "src").mkdir()
    (repo / "src/module.py").write_text("VALUE = 1\n")
    (repo / "other.txt").write_text("Unrelated scope\n")
    (repo / ".gitignore").write_text("*.ignored\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "fixture")
    return repo


@pytest.fixture
def package(tmp_path: Path) -> Path:
    root = tmp_path / "plugin"
    write_generated(root, projection(REPOSITORY / "plugins/product-development", "portable"))
    return root


@pytest.fixture
def workflow(package: Path, repository: Path, tmp_path: Path) -> WorkflowManager:
    return WorkflowManager(package, tmp_path / "user/.codex", repository, "session-1")


def task(**changes: object) -> dict:
    return {
        "id": "issue-15", "issue": "https://github.com/example/repo/issues/15",
        "delivery_stage": "local implementation", "status": "active", "paths": ["src"],
        "checks": [{"id": "unit", "command": "python -m pytest tests/unit",
                    "checker": "pytest-8", "environment": "offline-python"}],
        "review_requested": False, "continuation_limit": 1, **changes,
    }


def event(workflow: WorkflowManager, name: str, **changes: object) -> dict:
    return {"hook_event_name": name, "cwd": str(workflow.cwd),
            "session_id": workflow.session_id,
            **({"tool_name": "mcp__product-development-agents__codex_workflow_evidence"}
               if name == "PostToolUse" else {}), **changes}


def observation(workflow: WorkflowManager, name: str, **changes: object) -> dict:
    reference = f"{name}.json"
    (workflow.cwd / reference).write_text('{"result": "fixture"}\n')
    return {"observation_id": name, "candidate": workflow.status()["candidate"],
            "condition": "check_failed", "reference": reference,
            "check_id": "unit", "signature": "assertion:expected-one", **changes}


def two_failures(workflow: WorkflowManager) -> list[dict]:
    for name in ("failure-one", "failure-two"):
        workflow.record_evidence(observation(workflow, name))
    workflow.handle_event(event(workflow, "PostToolUse"))
    return workflow.status()["routes"]


def bash_event(workflow: WorkflowManager, name: str, call: str, **changes: object) -> dict:
    return event(workflow, name, tool_name="Bash", tool_use_id=call,
                 tool_input={"command": "python -m pytest tests/unit", "cwd": str(workflow.cwd)},
                 **changes)


def observe_command(workflow: WorkflowManager, call: str, response: object) -> dict:
    workflow.handle_event(bash_event(workflow, "PreToolUse", call))
    return workflow.handle_event(bash_event(workflow, "PostToolUse", call, tool_response=response))


def capture_task(mode: str) -> dict:
    return task(checks=[{**task()["checks"][0], "capture_mode": mode}])


@pytest.mark.parametrize("name", ["SessionStart", "PreToolUse", "PostToolUse", "Stop", "Interrupt"])
def test_absent_task_is_a_true_noop(workflow: WorkflowManager, name: str) -> None:
    before = tree(workflow.root.parent)
    assert workflow.status()["state"] == "absent"
    assert workflow.handle_event(event(workflow, name, source="compact")) == {}
    assert tree(workflow.root.parent) == before
    assert not workflow.home.exists()


@pytest.mark.parametrize("status", ["paused", "blocked", "waiting_for_approval", "complete"])
def test_inactive_task_never_nominates_or_continues(workflow: WorkflowManager, status: str) -> None:
    workflow.set_task(task(status=status, review_requested=True))
    assert two_failures(workflow) == []
    assert workflow.handle_event(event(workflow, "Stop")) == {}
    workflow.handle_event(event(workflow, "SessionStart", source="compact"))
    assert workflow.status()["routes"] == []
    assert workflow.status()["continuations"] == 0


def test_two_distinct_equivalent_failures_nominate_once_with_evidence(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    first = observation(workflow, "failure-one")
    workflow.record_evidence(first)
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == []
    workflow.record_evidence(first)
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == [], "A replay is not a second failure"
    workflow.record_evidence(observation(workflow, "failure-two"))
    output = workflow.handle_event(event(workflow, "PostToolUse"))
    routes = workflow.status()["routes"]
    assert len(routes) == 1
    route = routes[0]
    assert (route["condition"], route["skill"], route["role"], route["status"]) == (
        "repeated_check_failure", "diagnose-problem", "pd_diagnostician", "nominated")
    assert route["evidence_references"] == ["failure-one.json", "failure-two.json"]
    assert "$product-development:diagnose-problem" in output["hookSpecificOutput"]["additionalContext"]
    workflow.handle_event(event(workflow, "PostToolUse"))
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    assert len(workflow.status()["routes"]) == 1


@pytest.mark.parametrize("middle", ["pass", "different_signature"])
def test_intervening_observation_breaks_failure_equivalence(workflow: WorkflowManager, middle: str) -> None:
    workflow.set_task(task())
    workflow.record_evidence(observation(workflow, "first"))
    changes = {"condition": "check_passed"} if middle == "pass" else {"signature": "environment:missing-lib"}
    workflow.record_evidence(observation(workflow, "middle", **changes))
    workflow.record_evidence(observation(workflow, "last"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == []


def test_observation_id_is_idempotent_and_conflicting_reuse_is_rejected(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    record = observation(workflow, "first")
    workflow.record_evidence(record)
    before = tree(workflow.home)
    assert len(workflow.record_evidence(record)["evidence"]) == 1
    assert tree(workflow.home) == before
    with pytest.raises(AgentError):
        workflow.record_evidence({**record, "condition": "check_passed"})
    assert tree(workflow.home) == before


def test_review_requires_explicit_request_and_assignment_is_not_completion(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    assert workflow.status()["routes"] == []
    workflow.set_task(task(review_requested=True))
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    route = workflow.status()["routes"][0]
    assert (route["skill"], route["role"]) == ("review-code", "pd_reviewer")
    assigned = workflow.update_route(route["id"], "assigned", agent_id="reviewer-1")["routes"][0]
    assert assigned["status"] == "assigned" and "outcome" not in assigned
    (workflow.cwd / "review.json").write_text('{"findings": []}\n')
    completed = workflow.update_route(route["id"], "completed", outcome="passed", reference="review.json")["routes"][0]
    assert completed["status"] == "completed" and completed["outcome"] == "passed"
    assert completed["agent_id"] == "reviewer-1" and completed["current"]
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    assert len(workflow.status()["routes"]) == 1


@pytest.mark.parametrize("change", ["unstaged", "staged", "untracked"])
def test_scoped_changes_invalidate_routes_and_evidence(workflow: WorkflowManager, change: str) -> None:
    workflow.set_task(task())
    record = observation(workflow, "before-edit")
    workflow.record_evidence(record)
    route = two_failures(workflow)[0]
    if change == "untracked":
        (workflow.cwd / "src/new.py").write_text("VALUE = 2\n")
    else:
        (workflow.cwd / "src/module.py").write_text("VALUE = 2\n")
        if change == "staged":
            git(workflow.cwd, "add", "src/module.py")
    current = workflow.status()
    assert current["candidate"] != record["candidate"]
    assert current["evidence"] == [] and not current["routes"][0]["current"]
    before = tree(workflow.home)
    with pytest.raises(AgentError):
        workflow.record_evidence(record)
    (workflow.cwd / "review.json").write_text("{}\n")
    with pytest.raises(AgentError):
        workflow.update_route(route["id"], "completed", outcome="passed", reference="review.json")
    assert tree(workflow.home) == before


def test_index_changes_are_part_of_candidate_even_when_working_bytes_match(workflow: WorkflowManager) -> None:
    original = workflow.set_task(task())["candidate"]
    source = workflow.cwd / "src/module.py"
    source.write_text("VALUE = 2\n")
    git(workflow.cwd, "add", "src/module.py")
    source.write_text("VALUE = 1\n")
    assert workflow.status()["candidate"] != original


def test_out_of_scope_and_ignored_edits_preserve_candidate(workflow: WorkflowManager) -> None:
    original = workflow.set_task(task())["candidate"]
    (workflow.cwd / "other.txt").write_text("Changed unrelated file\n")
    (workflow.cwd / "unrelated.py").write_text("UNTRACKED = True\n")
    (workflow.cwd / "src/result.ignored").write_text("ignored result\n")
    assert workflow.status()["candidate"] == original


def test_compaction_restores_constraints_and_pointers_without_transcript(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    workflow.record_evidence(observation(workflow, "receipt"))
    output = workflow.handle_event(event(workflow, "SessionStart", source="compact",
                                        transcript="PRIVATE TRANSCRIPT MUST NEVER BE RETAINED"))
    context = output["hookSpecificOutput"]["additionalContext"]
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "issue-15" in context and "local implementation" in context and "src" in context
    assert "codex_workflow_status" in context and workflow.status()["candidate"] in context
    assert "PRIVATE TRANSCRIPT" not in context
    assert all(b"PRIVATE TRANSCRIPT" not in data for data in tree(workflow.home).values())


def test_stop_continuation_is_bounded_and_active_stop_is_honored(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    assert workflow.handle_event(event(workflow, "Stop", stop_hook_active=True)) == {}
    assert workflow.status()["continuations"] == 0 and workflow.status()["routes"] == []
    output = workflow.handle_event(event(workflow, "Stop", stop_hook_active=False))
    assert output["decision"] == "block" and "pd_reviewer" in output["reason"]
    assert workflow.status()["continuations"] == 1
    (workflow.cwd / "src/module.py").write_text("VALUE = 2\n")
    workflow.set_task(task(review_requested=True))
    assert workflow.handle_event(event(workflow, "Stop")) == {}
    assert workflow.status()["continuations"] == 1


def test_zero_continuation_budget_does_not_block_stop(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True, continuation_limit=0))
    assert workflow.handle_event(event(workflow, "Stop")) == {}
    assert workflow.status()["continuations"] == 0


@pytest.mark.parametrize("path", ["../outside", "/tmp/outside", ".git/config", "src/../../outside"])
def test_invalid_scope_does_not_initialize_state(workflow: WorkflowManager, path: str) -> None:
    with pytest.raises(AgentError):
        workflow.set_task(task(paths=[path]))
    assert not workflow.home.exists()


def test_symlink_scope_and_evidence_are_rejected(workflow: WorkflowManager, tmp_path: Path) -> None:
    target = tmp_path / "outside.txt"
    target.write_text("outside\n")
    (workflow.cwd / "linked").symlink_to(target)
    with pytest.raises(AgentError):
        workflow.set_task(task(paths=["linked"]))
    workflow.set_task(task())
    with pytest.raises(AgentError):
        workflow.record_evidence(observation(workflow, "unsafe", reference="linked"))
    assert workflow.status()["evidence"] == []


@pytest.mark.parametrize("reference", ["../outside.json", ".git/config", "/tmp/outside.json", "missing.json"])
def test_unsafe_evidence_reference_is_rejected(workflow: WorkflowManager, reference: str) -> None:
    workflow.set_task(task())
    with pytest.raises(AgentError):
        workflow.record_evidence(observation(workflow, "unsafe", reference=reference))
    assert workflow.status()["evidence"] == []


def test_typed_command_pair_records_only_current_candidate(workflow: WorkflowManager) -> None:
    candidate = workflow.set_task(task())["candidate"]
    output = observe_command(workflow, "check-one", {"exit_code": 1, "output": "PRIVATE OUTPUT"})
    assert output == {}
    evidence = workflow.status()["evidence"]
    assert len(evidence) == 1 and evidence[0]["candidate"] == candidate
    assert evidence[0]["condition"] == "check_failed"
    assert evidence[0]["checker"] == "pytest-8" and evidence[0]["environment"] == "offline-python"
    output = observe_command(workflow, "check-two", {"exit_code": 1, "output": "PRIVATE OUTPUT"})
    assert "pd_diagnostician" in output["hookSpecificOutput"]["additionalContext"]
    assert len(workflow.status()["routes"]) == 1
    assert all(b"PRIVATE OUTPUT" not in data for data in tree(workflow.home).values())


@pytest.mark.parametrize("response", ["Process exited with code 0", {"exit_code": "0"}, {"exit_code": True}, {}])
def test_string_or_unsupported_results_do_not_claim_outcome(workflow: WorkflowManager, response: object) -> None:
    workflow.set_task(task())
    output = observe_command(workflow, "unknown-check", response)
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "codex_workflow_status" in context and "codex_workflow_evidence" in context
    assert "completed structured integer exit result" in context and "leave it unknown" in context
    status = workflow.status()
    assert status["evidence"] == [] and status["routes"] == []
    unknown, = status["unknown_checks"]
    assert unknown["reason"] == "missing_typed_exit_status" and unknown["check_id"] == "unit"
    assert unknown["candidate"] == status["candidate"] and unknown["after"] == -1
    assert workflow.handle_event(event(workflow, "Stop")) == {}
    assert workflow.status()["continuations"] == 0


@pytest.mark.parametrize("exit_code", [0, 1])
def test_native_output_string_requires_actual_parent_typed_evidence(workflow: WorkflowManager, exit_code: int) -> None:
    workflow.set_task(task())
    for call in ("native-one", "native-two"):
        # Native v0.160.0 sends output text, so quiet success and failure look identical.
        output = observe_command(workflow, call, "PRIVATE NATIVE OUTPUT")
        assert bool(output) == (call == "native-one"), "Identical unknown checkpoints advise once"
    assert workflow.status()["evidence"] == [] and workflow.status()["routes"] == []
    assert all(b"PRIVATE NATIVE OUTPUT" not in data for data in tree(workflow.home).values())
    for call in ("parent-one", "parent-two"):
        reference = f"{call}.json"
        (workflow.cwd / reference).write_text(json.dumps({"exit_code": exit_code, "command": task()["checks"][0]["command"]}))
        workflow.record_evidence({"observation_id": call, "candidate": workflow.status()["candidate"],
                                  "condition": "check_passed" if exit_code == 0 else "check_failed",
                                  "reference": reference, "check_id": "unit", "signature": f"exit:{exit_code}"})
    assert workflow.status()["unknown_checks"] == []
    output = workflow.handle_event(event(workflow, "PostToolUse"))
    assert len(workflow.status()["routes"]) == (1 if exit_code else 0)
    assert bool(output) == bool(exit_code)


def test_parent_capture_routes_real_interleaved_native_and_parent_failure_history(workflow: WorkflowManager) -> None:
    workflow.set_task(capture_task("parent"))
    for number in (1, 2):
        assert observe_command(workflow, f"native-{number}", "PRIVATE NATIVE OUTPUT") == {}
        workflow.record_evidence(observation(workflow, f"parent-{number}", signature="exit:1"))
        workflow.handle_event(event(workflow, "PostToolUse"))
        assert len(workflow.status()["routes"]) == (number - 1)
    route, = workflow.status()["routes"]
    assert route["condition"] == "repeated_check_failure" and route["current"]
    assert route["evidence_references"] == ["parent-1.json", "parent-2.json"]
    assert workflow.status()["unknown_checks"] == []
    assert all(b"PRIVATE NATIVE OUTPUT" not in data for data in tree(workflow.home).values())


@pytest.mark.parametrize("explicit_hook", [False, True])
def test_default_hook_capture_preserves_each_actual_unknown_barrier(workflow: WorkflowManager, explicit_hook: bool) -> None:
    contract = capture_task("hook") if explicit_hook else task()
    assert workflow.set_task(contract)["task"]["checks"] == contract["checks"]
    for number in (1, 2):
        output = observe_command(workflow, f"native-{number}", "")
        context = output["hookSpecificOutput"]["additionalContext"]
        assert "capture_mode parent" in context and "complete check history" in context
        assert workflow.status()["task"]["checks"] == contract["checks"], "Advisory must not change mode"
        workflow.record_evidence(observation(workflow, f"parent-{number}", signature="exit:1"))
        workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == []


@pytest.mark.parametrize("response", ["", {"exit_code": 0}, {"exit_code": 1}])
def test_parent_capture_ignores_paired_and_unpaired_native_results(workflow: WorkflowManager, response: object) -> None:
    workflow.set_task(capture_task("parent"))
    before = tree(workflow.home)
    assert observe_command(workflow, "native", response) == {}
    assert workflow.handle_event(bash_event(workflow, "PostToolUse", "unpaired", tool_response=response)) == {}
    assert tree(workflow.home) == before
    assert workflow.status()["evidence"] == [] and workflow.status()["unknown_checks"] == []


@pytest.mark.parametrize("wrong_workdir", [False, True])
def test_paired_hook_receipt_cannot_be_hidden_by_parent_mode_command(workflow: WorkflowManager, tmp_path: Path, wrong_workdir: bool) -> None:
    parent_check = {**task()["checks"][0], "id": "parent-unit", "command": "python -m pytest tests/parent", "capture_mode": "parent"}
    workflow.set_task(task(checks=[task()["checks"][0], parent_check]))
    observe_command(workflow, "first-hook", {"exit_code": 1})
    workflow.handle_event(bash_event(workflow, "PreToolUse", "mixed-completion"))
    completion = bash_event(workflow, "PostToolUse", "mixed-completion", tool_response="")
    completion["tool_input"] = {"command": parent_check["command"], "cwd": str(tmp_path if wrong_workdir else workflow.cwd)}
    assert workflow.handle_event(completion) == {}
    observe_command(workflow, "last-hook", {"exit_code": 1})
    assert workflow.status()["routes"] == [], "The mismatched completion must break the hook check failure streak"
    state = json.loads(workflow.state_path.read_text())
    assert state["pending"] == {}
    unknown, = state["unknown_checks"]
    assert unknown["check_id"] == "unit"
    assert unknown["reason"] == ("tool_or_workdir_mismatch" if wrong_workdir else "command_mismatch")


@pytest.mark.parametrize("mode", ["hook", "parent"])
def test_capture_mode_change_stales_existing_evidence_and_routes(workflow: WorkflowManager, mode: str) -> None:
    workflow.set_task(capture_task(mode))
    route, = two_failures(workflow)
    candidate = workflow.status()["candidate"]
    current = workflow.set_task(capture_task("parent" if mode == "hook" else "hook"))
    assert current["candidate"] == candidate and current["evidence"] == []
    assert not current["routes"][0]["current"]
    with pytest.raises(AgentError):
        workflow.update_route(route["id"], "assigned")


@pytest.mark.parametrize("delete_reference", [False, True])
def test_explicit_unknown_breaks_parent_failure_history_even_without_reference(workflow: WorkflowManager, delete_reference: bool) -> None:
    workflow.set_task(capture_task("parent"))
    workflow.record_evidence(observation(workflow, "first", signature="exit:1"))
    unknown = observation(workflow, "unknown", condition="check_unknown", signature="completion:unavailable")
    validate(unknown, EVIDENCE_SCHEMA)
    workflow.record_evidence(unknown)
    if delete_reference:
        (workflow.cwd / "unknown.json").unlink()
    summary, = workflow.status()["unknown_checks"]
    assert summary["reason"] == "parent_reported_unknown" and summary["after"] == 1
    assert workflow.handle_event(event(workflow, "PostToolUse")) == {}
    assert workflow.handle_event(event(workflow, "Stop")) == {}
    assert workflow.status()["routes"] == [] and workflow.status()["continuations"] == 0
    workflow.record_evidence(observation(workflow, "second", signature="exit:1"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == [] and workflow.status()["unknown_checks"] == []
    workflow.record_evidence(observation(workflow, "third", signature="exit:1"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    route, = workflow.status()["routes"]
    assert route["evidence_references"] == ["second.json", "third.json"]


def test_explicit_unknown_replay_does_not_reopen_later_known_parent_status(workflow: WorkflowManager) -> None:
    workflow.set_task(capture_task("parent"))
    unknown = observation(workflow, "unknown", condition="check_unknown", signature="completion:unavailable")
    workflow.record_evidence(unknown)
    workflow.record_evidence(observation(workflow, "known", condition="check_passed", signature="exit:0"))
    before = tree(workflow.home)
    assert workflow.record_evidence(unknown)["unknown_checks"] == []
    assert tree(workflow.home) == before


@pytest.mark.parametrize("mode", ["hook", "parent"])
def test_capture_mode_schema_accepts_only_explicit_valid_modes(workflow: WorkflowManager, mode: str) -> None:
    contract = capture_task(mode)
    validate(contract, TASK_SCHEMA)
    assert workflow.set_task(contract)["task"]["checks"] == contract["checks"]


@pytest.mark.parametrize("mode", [None, True, "automatic", ["hook"]])
def test_invalid_capture_modes_are_rejected_without_state_mutation(workflow: WorkflowManager, mode: object) -> None:
    contract = task(checks=[{**task()["checks"][0], "capture_mode": mode}])
    with pytest.raises(ValidationError):
        validate(contract, TASK_SCHEMA)
    with pytest.raises(AgentError):
        workflow.set_task(contract)
    assert not workflow.home.exists()


def test_unknown_advisory_replay_is_deduplicated_by_checkpoint(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    assert observe_command(workflow, "native-one", "")
    replay = bash_event(workflow, "PostToolUse", "native-one", tool_response="")
    before = tree(workflow.home)
    assert workflow.handle_event(replay) == {}
    assert tree(workflow.home) == before
    unknown, = workflow.status()["unknown_checks"]
    assert unknown["reason"] == "missing_typed_exit_status"
    assert observe_command(workflow, "native-two", "") == {}
    workflow.record_evidence(observation(workflow, "later-parent-pass", condition="check_passed"))
    assert workflow.status()["unknown_checks"] == []
    assert observe_command(workflow, "new-checkpoint", "")
    unknown, = workflow.status()["unknown_checks"]
    assert unknown["after"] == 0


@pytest.mark.parametrize("intervening_unknown", [False, True])
def test_old_unknown_completion_replay_preserves_later_parent_failure_streak(workflow: WorkflowManager, intervening_unknown: bool) -> None:
    workflow.set_task(task())
    observe_command(workflow, "old-native", "")
    if intervening_unknown:
        observe_command(workflow, "another-native", "")
    workflow.record_evidence(observation(workflow, "parent-first", signature="exit:1"))
    assert workflow.status()["unknown_checks"] == []
    assert workflow.handle_event(bash_event(workflow, "PostToolUse", "old-native", tool_response="")) == {}
    assert workflow.status()["unknown_checks"] == []
    workflow.record_evidence(observation(workflow, "parent-second", signature="exit:1"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    route, = workflow.status()["routes"]
    assert route["condition"] == "repeated_check_failure" and route["current"]


def test_unpaired_completion_replay_preserves_later_parent_pass(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    replay = bash_event(workflow, "PostToolUse", "unpaired-native", tool_response="")
    assert workflow.handle_event(replay) == {}
    workflow.record_evidence(observation(workflow, "parent-pass", condition="check_passed", signature="exit:0"))
    before = tree(workflow.home)
    assert workflow.handle_event(replay) == {}
    assert tree(workflow.home) == before
    assert workflow.status()["unknown_checks"] == []


def test_processed_unknown_call_cannot_be_rearmed(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "processed-native", "")
    workflow.record_evidence(observation(workflow, "parent-pass", condition="check_passed", signature="exit:0"))
    before = tree(workflow.home)
    assert observe_command(workflow, "processed-native", {"exit_code": 0}) == {}
    assert tree(workflow.home) == before
    assert len(workflow.status()["evidence"]) == 1 and workflow.status()["unknown_checks"] == []


def test_identityless_completions_remain_unknown_without_advisory(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    completion = bash_event(workflow, "PostToolUse", None, tool_response="")
    assert workflow.handle_event(completion) == {}
    workflow.record_evidence(observation(workflow, "parent-first", signature="exit:1"))
    assert workflow.handle_event(completion) == {}
    unknown, = workflow.status()["unknown_checks"]
    assert unknown["reason"] == "unpaired_result" and unknown["after"] == 0
    assert json.loads(workflow.state_path.read_text())["processed_unknown_calls"] == []


def test_legacy_state_without_completion_guards_can_record_new_unknown(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    state = json.loads(workflow.state_path.read_text())
    del state["processed_unknown_calls"]
    workflow.state_path.write_text(json.dumps(state))
    assert workflow.status()["unknown_checks"] == []
    assert observe_command(workflow, "new-native", "")
    assert len(json.loads(workflow.state_path.read_text())["processed_unknown_calls"]) == 1


@pytest.mark.parametrize("guards", [None, ["RAW CALL ID"], ["a" * 64, "a" * 64], [f"{index:064x}" for index in range(129)]])
def test_malformed_completion_guards_fail_closed(workflow: WorkflowManager, guards: object) -> None:
    workflow.set_task(task())
    state = json.loads(workflow.state_path.read_text())
    state["processed_unknown_calls"] = guards
    workflow.state_path.write_text(json.dumps(state))
    before = tree(workflow.home)
    with pytest.raises(AgentError):
        workflow.status()
    result = run_hook(workflow, event(workflow, "SessionStart"))
    assert json.loads(result.stdout) == {} and "RAW CALL ID" not in result.stdout + result.stderr
    assert tree(workflow.home) == before


def test_completion_guard_bound_preserves_existing_guards_without_partial_post_mutation(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    state = json.loads(workflow.state_path.read_text())
    state["processed_unknown_calls"] = [f"{index:064x}" for index in range(128)]
    workflow.state_path.write_text(json.dumps(state))
    workflow.handle_event(bash_event(workflow, "PreToolUse", "beyond-bound"))
    before = tree(workflow.home)
    with pytest.raises(AgentError, match="replay guard limit"):
        workflow.handle_event(bash_event(workflow, "PostToolUse", "beyond-bound", tool_response=""))
    assert tree(workflow.home) == before
    assert workflow.status()["evidence"] == [] and workflow.status()["unknown_checks"] == []


def test_later_typed_native_result_resolves_unknown_without_advisory(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "native-unknown", "")
    assert observe_command(workflow, "native-complete", {"exit_code": 0}) == {}
    status = workflow.status()
    assert status["unknown_checks"] == []
    evidence, = status["evidence"]
    assert evidence["condition"] == "check_passed" and evidence["signature"] == "exit:0"


def test_unknown_from_old_contract_does_not_mask_current_failure_streak(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "old-unknown", "")
    checks = [{**task()["checks"][0], "environment": "revised-offline-python"}]
    workflow.set_task(task(checks=checks))
    observe_command(workflow, "new-first", {"exit_code": 1})
    observe_command(workflow, "new-second", {"exit_code": 1})
    route, = workflow.status()["routes"]
    assert route["condition"] == "repeated_check_failure" and route["current"]
    assert workflow.status()["unknown_checks"] == []


@pytest.mark.parametrize("mismatch", ["tool", "command", "cwd", "candidate", "task"])
def test_unknown_advisory_requires_all_pair_identity_gates(workflow: WorkflowManager, tmp_path: Path, mismatch: str) -> None:
    workflow.set_task(task())
    workflow.handle_event(bash_event(workflow, "PreToolUse", "paired"))
    after = bash_event(workflow, "PostToolUse", "paired", tool_response="")
    if mismatch == "tool":
        after["tool_name"] = "exec_command"
    elif mismatch == "command":
        after["tool_input"]["command"] = "echo fake"
    elif mismatch == "cwd":
        after["tool_input"]["cwd"] = str(tmp_path)
    elif mismatch == "candidate":
        (workflow.cwd / "src/module.py").write_text("VALUE = 2\n")
    else:
        workflow.set_task(task(delivery_stage="revised local implementation"))
    assert workflow.handle_event(after) == {}
    assert workflow.status()["evidence"] == [] and workflow.status()["routes"] == []


@pytest.mark.parametrize("change", ["candidate", "contract"])
def test_unknown_status_is_bound_to_current_candidate_and_contract(workflow: WorkflowManager, change: str) -> None:
    workflow.set_task(task())
    observe_command(workflow, "unknown-before", "")
    assert len(workflow.status()["unknown_checks"]) == 1
    if change == "candidate":
        (workflow.cwd / "src/module.py").write_text("VALUE = 2\n")
    else:
        checks = [{**task()["checks"][0], "environment": "revised-offline-python"}]
        workflow.set_task(task(checks=checks))
    assert workflow.status()["unknown_checks"] == []
    observe_command(workflow, "unknown-after", "")
    assert len(workflow.status()["unknown_checks"]) == 1


def test_unpaired_check_is_unknown_without_advisory(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    assert workflow.handle_event(bash_event(workflow, "PostToolUse", "unpaired", tool_response="")) == {}
    unknown, = workflow.status()["unknown_checks"]
    assert unknown["reason"] == "unpaired_result"


def test_legacy_unknown_state_is_preserved_without_asserting_current_scope(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "unknown-before", "")
    state = json.loads(workflow.state_path.read_text())
    legacy = {key: value for key, value in state["unknown_checks"][0].items() if key in {"candidate", "check_id", "after"}}
    state["unknown_checks"] = [legacy]
    workflow.state_path.write_text(json.dumps(state))
    assert workflow.status()["unknown_checks"] == []
    checks = [{**task()["checks"][0], "environment": "revised-offline-python"}]
    workflow.set_task(task(checks=checks))
    assert workflow.status()["unknown_checks"] == []
    assert json.loads(workflow.state_path.read_text())["unknown_checks"] == [legacy]


@pytest.mark.parametrize("metadata", [
    {"reason": "PRIVATE INVALID REASON"}, {"scope": "invalid"}, {"advised": "true"},
    {"reason": None}, {"after": True}, {"after": 1000}, {"reason": ["missing_typed_exit_status"]},
])
def test_malformed_unknown_metadata_is_rejected_without_disclosure(workflow: WorkflowManager, metadata: dict) -> None:
    workflow.set_task(task())
    observe_command(workflow, "unknown", "")
    state = json.loads(workflow.state_path.read_text())
    state["unknown_checks"][0].update(metadata)
    workflow.state_path.write_text(json.dumps(state))
    before = tree(workflow.home)
    with pytest.raises(AgentError):
        workflow.status()
    result = run_hook(workflow, event(workflow, "SessionStart"))
    assert json.loads(result.stdout) == {}
    assert "PRIVATE INVALID REASON" not in result.stdout + result.stderr
    assert tree(workflow.home) == before


def test_partial_new_unknown_metadata_does_not_upgrade_legacy_state(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "unknown", "")
    state = json.loads(workflow.state_path.read_text())
    del state["unknown_checks"][0]["scope"]
    workflow.state_path.write_text(json.dumps(state))
    with pytest.raises(AgentError):
        workflow.status()


def test_unknown_check_result_breaks_repeated_failure(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "first", {"exit_code": 1})
    observe_command(workflow, "unknown", "Exit code: 1")
    observe_command(workflow, "last", {"exit_code": 1})
    assert workflow.status()["routes"] == []


def test_post_without_pre_and_changed_candidate_never_qualify(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    workflow.handle_event(bash_event(workflow, "PostToolUse", "no-pre", tool_response={"exit_code": 0}))
    workflow.handle_event(bash_event(workflow, "PreToolUse", "changed"))
    (workflow.cwd / "src/module.py").write_text("VALUE = 2\n")
    workflow.handle_event(bash_event(workflow, "PostToolUse", "changed", tool_response={"exit_code": 0}))
    assert workflow.status()["evidence"] == []


def test_wrong_command_workdir_and_tool_never_qualify(workflow: WorkflowManager, tmp_path: Path) -> None:
    workflow.set_task(task())
    for index, changes in enumerate([
        {"tool_name": "exec_command"},
        {"tool_input": {"command": "echo fake", "cwd": str(workflow.cwd)}},
        {"tool_input": {"command": "python -m pytest tests/unit", "cwd": str(tmp_path)}},
    ]):
        call = f"wrong-{index}"
        before = {**bash_event(workflow, "PreToolUse", call), **changes}
        after = {**before, "hook_event_name": "PostToolUse", "tool_response": {"exit_code": 0}}
        workflow.handle_event(before)
        workflow.handle_event(after)
    assert workflow.status()["evidence"] == []


def test_simultaneous_equivalent_events_never_duplicate_nomination(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    def attempt(_: int) -> object:
        manager = WorkflowManager(workflow.root, workflow.home, workflow.cwd, "session-1")
        try:
            return manager.handle_event(event(manager, "PostToolUse"))
        except AgentError:
            return "busy"
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(attempt, range(4)))
    assert len(workflow.status()["routes"]) == 1
    assert sum(isinstance(result, dict) and bool(result) for result in results) == 1


def test_workflow_dispatch_obeys_same_private_state_contract(workflow: WorkflowManager, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(workflow.home))
    arguments = {"cwd": str(workflow.cwd), "session_id": "session-1"}
    assert dispatch("codex_workflow_status", arguments, root=workflow.root)["state"] == "absent"
    assert not workflow.home.exists()
    result = dispatch("codex_workflow_task", {**arguments, "task": task()}, root=workflow.root)
    assert result["candidate"] == workflow.status()["candidate"]


def run_hook(workflow: WorkflowManager, payload: object) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(workflow.root / "com.openai/codex_agents/workflow_hook.py")],
        input=json.dumps(payload), text=True, capture_output=True, check=True, timeout=10,
        env={**os.environ, "CODEX_HOME": str(workflow.home), "PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_packaged_stdlib_hook_restores_task_and_is_quiet_when_absent(workflow: WorkflowManager) -> None:
    payload = event(workflow, "SessionStart", source="compact")
    before = tree(workflow.root.parent)
    absent = run_hook(workflow, payload)
    assert json.loads(absent.stdout) == {} and absent.stderr == ""
    assert tree(workflow.root.parent) == before
    workflow.set_task(task())
    active = run_hook(workflow, payload)
    output = json.loads(active.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "issue-15" in output["hookSpecificOutput"]["additionalContext"]
    assert active.stderr == ""


@pytest.mark.parametrize("name", ["SessionStart", "Stop"])
def test_corrupt_state_hook_is_safe_and_does_not_disclose_contents(workflow: WorkflowManager, name: str) -> None:
    workflow.set_task(task(review_requested=True))
    state_path, = workflow.home.rglob("state.json")
    state_path.write_text("PRIVATE CORRUPT STATE\n")
    before = tree(workflow.home)
    result = run_hook(workflow, event(workflow, name))
    assert json.loads(result.stdout) == {}
    assert "PRIVATE CORRUPT STATE" not in result.stdout + result.stderr
    assert tree(workflow.home) == before


def test_wrong_cwd_hook_cannot_restore_another_repository(workflow: WorkflowManager, tmp_path: Path) -> None:
    workflow.set_task(task(review_requested=True))
    before = tree(workflow.home)
    result = run_hook(workflow, event(workflow, "Stop", cwd=str(tmp_path)))
    assert json.loads(result.stdout) == {}
    assert tree(workflow.home) == before


def test_unsupported_post_event_does_not_route(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    assert workflow.handle_event(event(workflow, "PostToolUse", tool_name="unknown-tool")) == {}
    assert workflow.status()["routes"] == []


def test_changed_checker_identity_prevents_failure_reuse(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    workflow.record_evidence(observation(workflow, "old-environment"))
    checks = [{**task()["checks"][0], "environment": "different-offline-python"}]
    workflow.set_task(task(checks=checks))
    workflow.record_evidence(observation(workflow, "new-environment"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == []


def test_catalog_changes_invalidate_previous_route(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    original_route = workflow.status()["routes"][0]
    catalog_path = workflow.root / "com.openai/hooks/routes.json"
    catalog = json.loads(catalog_path.read_text())
    catalog["routes"][0]["description"] += " Follow the revised diagnostic contract."
    catalog_path.write_text(json.dumps(catalog))
    revised = WorkflowManager(workflow.root, workflow.home, workflow.cwd, "session-1")
    assert not revised.status()["routes"][0]["current"]
    with pytest.raises(AgentError):
        revised.update_route(original_route["id"], "assigned", agent_id="child-1")


def test_governance_route_uses_owning_project_management_skill(repository: Path, tmp_path: Path) -> None:
    root = tmp_path / "project-management"
    write_generated(root, projection(REPOSITORY / "plugins/project-management", "portable"))
    manager = WorkflowManager(root, tmp_path / "home", repository, "session-governance")
    manager.set_task(task(checks=[]))
    (repository / "audit.json").write_text("{}\n")
    manager.record_evidence({"observation_id": "audit-one", "candidate": manager.status()["candidate"],
                             "condition": "governance_mismatch", "reference": "audit.json"})
    output = manager.handle_event(event(manager, "PostToolUse",
                                        tool_name="mcp__project-management-agents__codex_workflow_evidence"))
    route, = manager.status()["routes"]
    assert (route["condition"], route["skill"], route["role"]) == (
        "governance_mismatch", "project-governance", "pm_governance_auditor")
    assert route["evidence_references"] == ["audit.json"]
    assert "$project-management:project-governance" in output["hookSpecificOutput"]["additionalContext"]


def test_symlinked_private_home_is_not_written(package: Path, repository: Path, tmp_path: Path) -> None:
    target = tmp_path / "real-home"
    target.mkdir()
    link = tmp_path / "linked-home"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(AgentError):
        WorkflowManager(package, link, repository, "session-1")
    assert tree(target) == {}


def test_changed_task_check_contract_invalidates_prior_route(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    route, = two_failures(workflow)
    candidate = workflow.status()["candidate"]
    checks = [{**task()["checks"][0], "environment": "revised-offline-python"}]
    current = workflow.set_task(task(checks=checks))
    assert current["candidate"] == candidate
    assert not current["routes"][0]["current"]
    assert current["evidence"] == []
    with pytest.raises(AgentError):
        workflow.update_route(route["id"], "assigned", agent_id="child-1")


@pytest.mark.parametrize("change", ["deleted", "replaced"])
def test_manual_evidence_reference_changes_invalidate_prior_route(workflow: WorkflowManager, change: str) -> None:
    workflow.set_task(task())
    route, = two_failures(workflow)
    candidate = workflow.status()["candidate"]
    reference = workflow.cwd / "failure-one.json"
    if change == "deleted":
        reference.unlink()
    else:
        reference.write_text('{"result": "different evidence"}\n')
    current = workflow.status()
    assert current["candidate"] == candidate, "Evidence is deliberately outside product scope"
    assert not current["routes"][0]["current"]
    assert all(item["observation_id"] != "failure-one" for item in current["evidence"])
    with pytest.raises(AgentError):
        workflow.update_route(route["id"], "assigned", agent_id="child-1")


def test_unpaired_configured_command_observation_breaks_failure_streak(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "first", {"exit_code": 1})
    workflow.handle_event(bash_event(workflow, "PostToolUse", "unpaired", tool_response={"exit_code": 0}))
    observe_command(workflow, "last", {"exit_code": 1})
    assert workflow.status()["routes"] == []


def test_changed_completed_reference_invalidates_review_receipt(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    route, = workflow.status()["routes"]
    reference = workflow.cwd / "review.json"
    reference.write_text('{"findings": []}\n')
    workflow.update_route(route["id"], "assigned", agent_id="reviewer-one")
    workflow.update_route(route["id"], "completed", outcome="passed", reference="review.json")
    reference.write_text('{"findings": ["different candidate"]}\n')
    assert not workflow.status()["routes"][0]["current"]


def test_replayed_paired_post_does_not_count_or_break_failure_streak(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    observe_command(workflow, "first", {"exit_code": 1})
    replay = bash_event(workflow, "PostToolUse", "first", tool_response={"exit_code": 1})
    assert workflow.handle_event(replay) == {}
    assert len(workflow.status()["evidence"]) == 1 and workflow.status()["routes"] == []
    observe_command(workflow, "second", {"exit_code": 1})
    assert len(workflow.status()["evidence"]) == 2 and len(workflow.status()["routes"]) == 1


def test_deleted_intervening_pass_does_not_rejoin_failure_streak(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    workflow.record_evidence(observation(workflow, "first"))
    workflow.record_evidence(observation(workflow, "intervening-pass", condition="check_passed"))
    workflow.record_evidence(observation(workflow, "last"))
    (workflow.cwd / "intervening-pass.json").unlink()
    workflow.handle_event(event(workflow, "PostToolUse"))
    assert workflow.status()["routes"] == []


def test_completion_cannot_replace_parent_recorded_agent_assignment(workflow: WorkflowManager) -> None:
    workflow.set_task(task(review_requested=True))
    workflow.handle_event(event(workflow, "SessionStart", source="resume"))
    route, = workflow.status()["routes"]
    workflow.update_route(route["id"], "assigned", agent_id="reviewer-one")
    (workflow.cwd / "review.json").write_text("{}\n")
    with pytest.raises(AgentError):
        workflow.update_route(route["id"], "completed", agent_id="reviewer-two",
                              outcome="passed", reference="review.json")
    assigned, = workflow.status()["routes"]
    assert assigned["status"] == "assigned" and assigned["agent_id"] == "reviewer-one"


def test_process_death_releases_workflow_mutation_lock(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "com.openai/codex_agents"))
from workflow import WorkflowManager
manager = WorkflowManager(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), "session-1")
with manager._mutation():
    print("locked", flush=True)
    sys.stdin.read()
"""
    child = subprocess.Popen(
        [sys.executable, "-c", script, str(workflow.root), str(workflow.home), str(workflow.cwd)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        with selectors.DefaultSelector() as readiness:
            readiness.register(child.stdout, selectors.EVENT_READ)
            assert readiness.select(timeout=10), "Lock holder did not become ready"
        assert child.stdout.readline().strip() == "locked"
        with pytest.raises(AgentError):
            workflow.set_task(task(status="paused"))
        child.kill()
        child.wait(timeout=10)
        assert workflow.set_task(task(status="paused"))["task"]["status"] == "paused"
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=10)


def test_reused_evidence_path_does_not_stale_new_valid_nomination(workflow: WorkflowManager) -> None:
    workflow.set_task(task())
    reference = workflow.cwd / "report.json"
    reference.write_text('{"result": "old failure"}\n')
    workflow.record_evidence(observation(workflow, "old", reference="report.json"))
    reference.write_text('{"result": "new failures"}\n')
    workflow.record_evidence(observation(workflow, "new-one", reference="report.json"))
    workflow.record_evidence(observation(workflow, "new-two", reference="report.json"))
    workflow.handle_event(event(workflow, "PostToolUse"))
    route, = workflow.status()["routes"]
    assert route["current"] and route["evidence_references"] == ["report.json"]
    assigned, = workflow.update_route(route["id"], "assigned", agent_id="child-1")["routes"]
    assert assigned["current"] and assigned["status"] == "assigned"
