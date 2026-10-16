"""Offline contract experiments; no live releases, installation, trust or reload."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest
from build_codex_package import projection

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/release-safeguards"
CODEX = os.environ.get("CODEX_TEST_BINARY")
TEMPLATE = ROOT / "plugins/project-management/com.openai/release-policy/review-release.rules"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SUITE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GUARD, INSTALLER = load("guard_model"), load("installer_model")


@pytest.fixture
def operation():
    candidate = {"host": "github.example", "repository": "example/product", "repository_id": 77,
                 "release_id": 101, "tag": "v2.0.0-beta.1", "source_sha": "a" * 40,
                 "artifacts": {"product.tgz": "b" * 64}, "body_sha256": "c" * 64,
                 "isDraft": True, "isPrerelease": True}
    request = {"action": "edit_draft", "expected": copy.deepcopy(candidate),
               "result": {**candidate, "body_sha256": "d" * 64}}
    authority = copy.deepcopy(request)
    return request, [candidate], authority


def test_authorized_draft_body_edit(operation):
    request, state, authority = operation
    assert GUARD.decide(request, state, authority, True) == "eligible"


def publication(operation):
    request, state, _ = copy.deepcopy(operation)
    request.update(action="publish_draft", result={**request["expected"], "isDraft": False})
    authority = {**copy.deepcopy(request), "explicit_publication_approval": True}
    return request, state, authority


def test_explicitly_approved_exact_draft_publication(operation):
    assert GUARD.decide(*publication(operation), True) == "eligible"


@pytest.mark.parametrize("publish", [False, True])
def test_fake_operation_performs_only_reviewed_transition(operation, publish):
    request, state, authority = publication(operation) if publish else operation
    writes = []
    assert GUARD.simulate_operation(request, authority, True, lambda: state, writes.append) == "simulated_write"
    assert writes == [request["result"]]
    assert writes[0]["isDraft"] is (not publish)


@pytest.mark.parametrize("prerelease", [True, False])
@pytest.mark.parametrize("action", ["edit_draft", "publish_draft"])
def test_published_stable_and_prerelease_refused(operation, prerelease, action):
    request, state, authority = publication(operation) if action == "publish_draft" else operation
    state[0].update(isDraft=False, isPrerelease=prerelease)
    assert GUARD.decide(request, state, authority, True) == "already_published"


@pytest.mark.parametrize("value", [None, [], {}, [None], [{"isDraft": True}], "draft"])
def test_missing_or_malformed_state_refused(operation, value):
    request, _, authority = operation
    assert GUARD.decide(request, value, authority, True) != "eligible"


@pytest.mark.parametrize("value", [None, "true", 1])
def test_draft_boolean_is_required(operation, value):
    request, state, authority = operation
    state[0]["isDraft"] = value
    assert GUARD.decide(request, state, authority, True) == "invalid_state"


def test_ambiguous_release_lookup_refused(operation):
    request, state, authority = operation
    assert GUARD.decide(request, state + state, authority, True) == "missing_or_ambiguous_state"


@pytest.mark.parametrize("key,value", [
    ("host", "other.example"), ("repository", "example/other"), ("repository_id", 78),
    ("release_id", 102), ("tag", "v2"), ("source_sha", "e" * 40),
    ("artifacts", {"product.tgz": "e" * 64}), ("body_sha256", "e" * 64),
    ("isPrerelease", False),
])
def test_identity_or_payload_drift_refused(operation, key, value):
    request, state, authority = operation
    state[0][key] = value
    assert GUARD.decide(request, state, authority, True) == "changed_release_identity"


def test_edit_authority_does_not_authorize_publication(operation):
    request, state, _ = publication(operation)
    assert GUARD.decide(request, state, operation[2], True) == "unauthorized_action"


@pytest.mark.parametrize("field,value", [("source_sha", "main"), ("source_sha", 1),
    ("body_sha256", "unknown"), ("artifacts", None), ("release_id", True),
    ("repository_id", None), ("isPrerelease", "true"), ("isDraft", False)])
def test_incomplete_or_unreviewed_candidate_refused(operation, field, value):
    request, state, authority = operation
    request["expected"][field] = value
    assert GUARD.decide(request, state, authority, True) == "invalid_candidate"


def test_draft_edit_cannot_publish_incidentally(operation):
    request, state, authority = operation
    request["result"]["isDraft"] = authority["result"]["isDraft"] = False
    assert GUARD.decide(request, state, authority, True) == "wrong_transition"


def test_body_edit_cannot_change_tag_or_artifacts(operation):
    request, state, authority = operation
    request["result"]["tag"] = authority["result"]["tag"] = "new-tag"
    assert GUARD.decide(request, state, authority, True) == "changed_result_identity"


def test_unknown_payload_fields_require_a_separately_reviewed_adapter(operation):
    request, state, authority = operation
    request["result"]["make_latest"] = True
    assert GUARD.decide(request, state, authority, True) == "invalid_candidate"


@pytest.mark.parametrize("approval", [None, False, 1, "approved"])
def test_explicit_publication_approval_required(operation, approval):
    request, state, authority = publication(operation)
    authority["explicit_publication_approval"] = approval
    assert GUARD.decide(request, state, authority, True) == "publication_approval_required"


def test_approval_does_not_cover_revised_public_body(operation):
    request, state, authority = publication(operation)
    request["expected"]["body_sha256"] = state[0]["body_sha256"] = "f" * 64
    request["result"]["body_sha256"] = "f" * 64
    assert GUARD.decide(request, state, authority, True) == "unauthorized_candidate"


@pytest.mark.parametrize("permitted", [False, None, "allow", 1])
def test_executable_denial_or_unknown_cannot_be_overridden(operation, permitted):
    assert GUARD.decide(*operation, permitted) == "executable_denied_or_unknown"


@pytest.mark.parametrize("action", ["delete", "upload", "retag", "recreate"])
def test_unsupported_mutations_are_explicit(operation, action):
    request, state, authority = operation
    request["action"] = action
    assert GUARD.decide(request, state, authority, True) == "unsupported_action"


def test_second_read_detects_concurrent_publication(operation):
    request, state, authority = operation
    observations = iter([state, [{**state[0], "isDraft": False}]])
    writes = []
    result = GUARD.simulate_operation(request, authority, True, lambda: next(observations), writes.append)
    assert result == "already_published" and writes == []


def test_two_reads_do_not_prevent_publication_after_last_check(operation):
    request, state, authority = operation
    writes = []

    def race(payload):
        state[0]["isDraft"] = False  # competing publisher after final read
        writes.append((state[0]["isDraft"], payload))

    assert GUARD.simulate_operation(request, authority, True, lambda: copy.deepcopy(state), race) == "simulated_write"
    assert writes[0][0] is False  # counterexample to atomic safety, not a successful guard


def test_provider_read_error_refuses_fake_write(operation):
    def unavailable():
        raise TimeoutError("fixture")

    writes = []
    request, _, authority = operation
    assert GUARD.simulate_operation(request, authority, True, unavailable, writes.append) == "read_failed"
    assert writes == []


def test_unknown_write_outcome_is_not_automatically_retried(operation):
    request, state, authority = publication(operation)
    writes = []

    def apply_then_timeout(payload):
        writes.append(payload)
        state[0] = copy.deepcopy(payload)
        raise TimeoutError("response lost after fake publication")

    assert GUARD.simulate_operation(request, authority, True, lambda: state, apply_then_timeout) == "write_outcome_unknown"
    assert len(writes) == 1
    assert GUARD.simulate_operation(request, authority, True, lambda: state, writes.append) == "already_published"
    assert len(writes) == 1


@pytest.fixture
def installer(tmp_path):
    home, repo = tmp_path / "user/.codex", tmp_path / "repo"
    home.mkdir(parents=True)
    repo.mkdir()
    (home / "config.toml").write_text('# unrelated\nmodel = "example"\n')
    (home / "rules").mkdir()
    (home / "rules/local.rules").write_text('# unrelated deny\n')
    return INSTALLER.InstallerModel(home, repo, "0.10.4", TEMPLATE.read_bytes())


def tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("scope", ["user", "project"])
def test_rule_install_model_preserves_other_scope_and_unrelated_configuration(installer, scope):
    before = tree(installer.home.parent.parent)
    other = installer.paths("project" if scope == "user" else "user")
    plan = installer.preview(scope, project_trusted=True)
    assert not any(path.exists() for path in other)
    assert installer.apply(plan, consent=True, project_trusted=True).endswith("pending")
    for path, data in before.items():
        assert (installer.home.parent.parent / path).read_bytes() == data
    assert not any(path.exists() for path in other)
    assert installer.snapshot(scope)["state"] == "ready"


@pytest.mark.parametrize("consent", [None, False, 1, "yes"])
def test_rule_model_decline_cancel_unavailable_consent_leave_files_unchanged(installer, consent):
    before = tree(installer.home.parent.parent)
    plan = installer.preview("user")
    assert installer.apply(plan, consent=consent) == "deferred"
    assert tree(installer.home.parent.parent) == before


def test_rule_model_untrusted_project_refused(installer):
    with pytest.raises(INSTALLER.Conflict, match="trust"):
        installer.preview("project")


@pytest.mark.parametrize("kind", ["unowned", "edited", "wrong_owner", "malformed", "missing", "symlink"])
def test_rule_model_preserves_ownership_drift_conflicts(installer, kind):
    if kind != "unowned":
        installer.apply(installer.preview("user"), consent=True)
    target, marker = installer.paths("user")
    if kind in {"unowned", "edited"}:
        target.write_bytes(b"# local changes\n")
    elif kind == "wrong_owner":
        record = json.loads(marker.read_text())
        record["owner"] = "another/plugin"
        marker.write_text(json.dumps(record))
    elif kind == "malformed":
        marker.write_text("broken json")
    elif kind == "missing":
        target.unlink()
    else:
        target.unlink()
        target.symlink_to(installer.home / "rules/local.rules")
    before = tree(installer.home.parent.parent)
    with pytest.raises(INSTALLER.Conflict):
        installer.preview("user")
    assert tree(installer.home.parent.parent) == before


def test_rule_model_scoped_upgrade_backup_and_duplicate_scope_conflict(installer):
    installer.apply(installer.preview("user"), consent=True)
    target, marker = installer.paths("user")
    previous = target.read_bytes()
    newer = INSTALLER.InstallerModel(installer.home, installer.repo, "0.10.5", previous + b"# update\n")
    plan = newer.preview("user")
    assert plan["current"]["state"] == "upgrade_available"
    newer.apply(plan, consent=True)
    assert [p.read_bytes() for p in marker.parent.glob("*.backup")] == [previous]
    with pytest.raises(INSTALLER.Conflict, match="duplicate"):
        newer.preview("project", project_trusted=True)
    with pytest.raises(INSTALLER.Conflict):
        installer.preview("user")  # downgrade


def test_rule_model_rechecks_plan_and_preserves_late_edit(installer):
    plan = installer.preview("user")
    target, _ = installer.paths("user")
    target.write_bytes(b"# appeared while consent form open\n")
    before = tree(installer.home.parent.parent)
    with pytest.raises(INSTALLER.Conflict):
        installer.apply(plan, consent=True)
    assert tree(installer.home.parent.parent) == before


def test_rule_model_rechecks_project_trust_after_consent_preview(installer):
    plan = installer.preview("project", project_trusted=True)
    before = tree(installer.home.parent.parent)
    with pytest.raises(INSTALLER.Conflict, match="trust"):
        installer.apply(plan, consent=True, project_trusted=False)
    assert tree(installer.home.parent.parent) == before


def test_rule_model_rejects_changed_template_after_preview(installer):
    plan = installer.preview("user")
    installer.template += b"# changed after review\n"
    before = tree(installer.home.parent.parent)
    with pytest.raises(INSTALLER.Conflict, match="plan changed"):
        installer.apply(plan, consent=True)
    assert tree(installer.home.parent.parent) == before


def test_rule_model_rejects_changed_bytes_at_same_version(installer):
    installer.apply(installer.preview("user"), consent=True)
    revised = INSTALLER.InstallerModel(installer.home, installer.repo, installer.version, b"# different\n")
    with pytest.raises(INSTALLER.Conflict):
        revised.preview("user")


@pytest.mark.parametrize("command,expected", [
    (["gh", "release", "edit", "v2", "--draft=false"], "prompt"),
    (["gh", "release", "upload", "v2", "product.tgz"], "prompt"),
    (["gh", "release", "delete", "v2"], "prompt"),
    (["gh", "release", "create", "v2", "--draft"], "prompt"),
    (["gh", "release", "view", "v2"], None),
    (["gh", "--repo", "example/product", "release", "edit", "v2"], None),
    (["gh", "api", "--method", "PATCH", "repos/example/product/releases/101"], None),
    (["curl", "--request", "PATCH", "https://api.github.example/repos/example/product/releases/101"], None),
])
def test_real_execpolicy_prefix_coverage_and_gaps(command, expected):
    if not CODEX:
        pytest.skip("native Codex required; guard/installer tests remain offline")
    result = subprocess.run([CODEX, "execpolicy", "check", "--rules", str(TEMPLATE), "--", *command],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout).get("decision") == expected


@pytest.mark.parametrize("order", [False, True])
@pytest.mark.parametrize("action", ["edit", "delete"])
def test_real_execpolicy_existing_forbidden_wins_over_template_and_allow(tmp_path, order, action):
    if not CODEX:
        pytest.skip("native Codex required")
    deny, allow = tmp_path / "existing.rules", tmp_path / "unsafe-allow.rules"
    deny.write_text('prefix_rule(pattern=["gh", "release", ["delete", "edit"]], decision="forbidden")\n')
    allow.write_text('prefix_rule(pattern=["gh", "release", "edit"], decision="allow")\n')
    rules = [deny, TEMPLATE, allow]
    if order:
        rules.reverse()
    command = [CODEX, "execpolicy", "check"]
    for path in rules:
        command.extend(["--rules", str(path)])
    result = subprocess.run([*command, "--", "gh", "release", action, "v2"],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["decision"] == "forbidden"


def test_built_packages_include_guidance_and_inert_template_without_guard_activation():
    for format in ("portable", "codex"):
        pm = projection(ROOT / "plugins/project-management", format)
        communication = projection(ROOT / "plugins/communication", format)
        assert pm["com.openai/release-policy/review-release.rules"] == TEMPLATE.read_bytes()
        assert "skills/publish-change/references/release-lifecycle.md" in pm
        assert "skills/_shared/references/public-release-writing.md" in communication
        assert "release-policy" not in pm["com.openai/hooks/hooks.json"].decode()
        assert "release-policy" not in pm.get(".mcp.json", pm.get("mcp.json", b"")).decode()


def test_editorial_examples_retain_useful_facts_and_reject_internal_context():
    examples = json.loads((SUITE / "fixtures/public-notes.json").read_text())
    for example in examples:
        for fact in example["retain"]:
            assert fact in example["public"] and fact in example["development"]
        for internal in example["reject"]:
            assert internal in example["development"] and internal not in example["public"]
        assert example["rubric"]  # Human-reviewed examples, not a semantic model evaluation.
