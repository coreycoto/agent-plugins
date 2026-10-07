"""Qualify public workflow fixtures independently of clients, models and private runners."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "evals/owned-workflows"
SKILLS = ("diagnose-problem", "implement-change", "review-code", "verify-product", "refresh-solutions")


def load_case(skill):
    suite = ROOT / skill
    return suite, json.loads((suite / "evals.json").read_text())["evals"][0]


def workspace(tmp_path, skill):
    suite, case = load_case(skill)
    target = tmp_path / "consumer"
    target.mkdir()
    for entry in case["workspace_files"]:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / entry["source"], destination)
    response = tmp_path / "response.txt"
    response.write_text("Result submitted for independent assessment.\n")
    events = tmp_path / "events.json"
    events.write_text("[]\n")
    return target, response, events


def assert_check(skill, check_id, target, response, events, passes=True):
    suite, case = load_case(skill)
    check = next(check for check in case["checks"] if check["id"] == check_id)
    before = {str(path.relative_to(target)): path.read_bytes() for path in target.rglob("*") if path.is_file()}
    result = subprocess.run([sys.executable, "-I", "-B", str(suite / check["script"]), str(target), str(response), str(events)], capture_output=True, text=True, timeout=30)
    assert result.returncode == (0 if passes else 1), result.stdout + result.stderr
    after = {str(path.relative_to(target)): path.read_bytes() for path in target.rglob("*") if path.is_file()}
    assert after == before, "Oracle mutated the submitted workspace"
    return result


def write(target, name, body):
    destination = target / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body)


def complete(skill, target, events):
    if skill == "diagnose-problem":
        write(target, "scheduler.py", '''def conflicts(bookings, start, end):
    query = set(range(start, end))
    return [identifier for identifier, begin, stop in bookings if query & set(range(begin, stop))]
''')
        write(target, "test_scheduler.py", '''import unittest
from scheduler import conflicts

class BoundaryTests(unittest.TestCase):
    def test_adjacent_and_empty(self):
        self.assertEqual(conflicts([(0, 1, 2)], 2, 3), [])
        self.assertEqual(conflicts([(0, 1, 2)], 1, 1), [])
        self.assertEqual(conflicts([(0, 1, 1)], 0, 2), [])
    def test_ids_and_order(self):
        self.assertEqual(conflicts([(9, 1, 3), (0, 1, 3)], 2, 3), [9, 0])
''')
        write(target, "diagnosis.md", "The inclusive comparison breaks half-open adjacency and empty interval boundaries. The unittest regressions pass on the fix and fail on the original.\n")
    elif skill == "implement-change":
        path = target / "index.html"
        path.write_text(path.read_text().replace(">Generate</button>", ">Create export</button>"))
    elif skill == "review-code":
        write(target, "review.json", json.dumps({"findings": [{"path": "catalog.py", "trigger": "Two tenants request the same SKU; the cache key omits tenant identity", "consequence": "The second tenant receives the first tenant's product"}]}))
        write(target, "review_repro.py", '''import sys
from catalog import Catalog

class Store:
    def lookup(self, tenant, sku): return tenant + ":" + sku
catalog = Catalog(Store())
first = catalog.get("alpha", "shared")
second = catalog.get("beta", "shared")
sys.exit(0 if first == "alpha:shared" and second == "beta:shared" else 1)
''')
    elif skill == "verify-product":
        observed = []
        outputs = {}
        for action, extra in (("add", ["Trial note"]), ("list", [])):
            arguments = [sys.executable, "-B", "notes.py", "--store", ".artifacts/trial-notes.json", action, *extra]
            result = subprocess.run(arguments, cwd=target, text=True, capture_output=True, check=True)
            import shlex
            observed.append({"type": "item.completed", "item": {"id": action, "type": "command_execution", "command": shlex.join(arguments), "aggregated_output": result.stdout, "exit_code": result.returncode, "status": "completed"}})
            outputs[action] = json.loads(result.stdout)
        events.write_text(json.dumps(observed))
        write(target, "evidence/notes.json", json.dumps(outputs))
        write(target, "verification.md", "Executed separate add and list commands. Observed JSON is retained in evidence/notes.json; owned scratch store removed.\n")
        (target / ".artifacts/trial-notes.json").unlink()
    elif skill == "refresh-solutions":
        path = target / "docs/solutions/cleanup-preview.md"
        path.write_text(path.read_text().replace("Command: python legacy_clean.py --preview", "Command: python src/cleanup.py --dry-run").replace("Evidence: historical investigation only; current command has not been verified.", "Evidence: current source exposes --dry-run; preview prints the affected cache without mutation. Historical investigation reasoning retained."))


@pytest.mark.parametrize("skill", SKILLS)
def test_suite_and_trigger_contract(skill):
    suite, case = load_case(skill)
    data = json.loads((suite / "evals.json").read_text())
    assert data["schema_version"] == 3 and data["skill_name"] == f"product-development:{skill}"
    assert data["grader_support"] == ["_oracle_support.py"]
    for support in data["grader_support"]:
        assert Path(support).name == support and (suite.parent / support).is_file()
    assert len(data["evals"]) == 1 and case["execution_mode"] == "artifact-safe"
    assert case["tiers"] == ["smoke", "deep"] and len(case["checks"]) >= 3
    assert data["skill_name"] not in case["prompt"] and "$" not in case["prompt"]
    assert case["expected_output"] not in case["prompt"]
    assert len({check["id"] for check in case["checks"]}) == len(case["checks"])
    for check in case["checks"]:
        assert check["type"] == "assertion"
        assert (suite / check["script"]).resolve().is_relative_to(suite)
        assert (suite / check["script"]).is_file()
    queries = json.loads((suite / "trigger_queries.json").read_text())
    assert queries["schema_version"] == 2 and queries["skill_name"] == data["skill_name"]
    assert len(queries["queries"]) >= 4
    assert len({query["id"] for query in queries["queries"]}) == len(queries["queries"])
    for split in ("train", "validation"):
        assert {query["should_trigger"] for query in queries["queries"] if query["split"] == split} == {True, False}
    for item in [case, *queries["queries"]]:
        for entry in item["workspace_files"]:
            assert not Path(entry["path"]).is_absolute() and ".." not in Path(entry["path"]).parts
            assert (suite / entry["source"]).resolve().is_relative_to(suite / "fixtures")
            assert (suite / entry["source"]).is_file()


@pytest.mark.parametrize("skill", SKILLS)
def test_corrected_artifacts_pass_all_independent_checks(tmp_path, skill):
    target, response, events = workspace(tmp_path, skill)
    complete(skill, target, events)
    _, case = load_case(skill)
    for check in case["checks"]:
        assert_check(skill, check["id"], target, response, events)


@pytest.mark.parametrize("skill", [*SKILLS, "understand-codebase", "product-discovery"])
def test_declared_frozen_evaluator_snapshot_runs_standalone(tmp_path, skill):
    target, response, events = workspace(tmp_path, skill)
    complete(skill, target, events)
    suite, case = load_case(skill)
    data = json.loads((suite / "evals.json").read_text())
    snapshot_parent = tmp_path / "frozen-evaluator"
    snapshot = snapshot_parent / skill
    snapshot.mkdir(parents=True)
    for support in data["grader_support"]:
        shutil.copyfile(suite.parent / support, snapshot_parent / support)
    for entry in case["workspace_files"]:
        destination = snapshot / entry["source"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / entry["source"], destination)
    for check in case["checks"]:
        if check["type"] != "assertion":
            continue
        destination = snapshot / check["script"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / check["script"], destination)
        result = subprocess.run([sys.executable, "-I", "-B", str(destination), str(target), str(response), str(events)], capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(("skill", "check"), [
    ("diagnose-problem", "diagnosis-and-scope"),
    ("implement-change", "no-scaffolding"),
    ("review-code", "source-preserved"),
    ("verify-product", "userdata-and-source-preserved"),
    ("refresh-solutions", "scope-preserved"),
])
def test_product_inventory_excludes_runtime_closure_but_rejects_new_product_files(tmp_path, skill, check):
    target, response, events = workspace(tmp_path, skill)
    complete(skill, target, events)
    write(target, ".agents/skills/example/SKILL.md", "Harness procedure bytes checked by runtime.\n")
    write(target, ".agents/skills/example/references/contract.md", "Harness supporting reference.\n")
    assert_check(skill, check, target, response, events)
    write(target, "unexpected-product-file.txt", "An unauthorized product artifact\n")
    assert_check(skill, check, target, response, events, passes=False)


@pytest.mark.parametrize(("skill", "check"), [
    ("diagnose-problem", "interval-contract"),
    ("implement-change", "button-label"),
    ("review-code", "actionable-finding"),
    ("verify-product", "completed-command-evidence"),
    ("refresh-solutions", "current-command"),
])
def test_original_fixture_is_not_a_completed_result(tmp_path, skill, check):
    target, response, events = workspace(tmp_path, skill)
    assert_check(skill, check, target, response, events, passes=False)


@pytest.mark.parametrize(("skill", "check", "file", "replacement"), [
    ("diagnose-problem", "regression-sensitivity", "test_scheduler.py", "import unittest\nclass Tests(unittest.TestCase):\n def test_constant(self): self.assertTrue(True)\n"),
    ("diagnose-problem", "diagnosis-and-scope", "README.md", "New invented contract"),
    ("implement-change", "dom-and-behavior", "app.js", "console.log('changed behavior');"),
    ("implement-change", "no-scaffolding", "package.json", "{}"),
    ("review-code", "reproducer-sensitivity", "review_repro.py", "raise SystemExit(1)\n"),
    ("review-code", "source-preserved", "catalog.py", "# repaired source during a read-only review\n"),
    ("verify-product", "durable-evidence-and-cleanup", ".artifacts/trial-notes.json", "[]"),
    ("verify-product", "userdata-and-source-preserved", "data/user-notes.json", "[]"),
    ("refresh-solutions", "reasoning-retained", "docs/solutions/cleanup-preview.md", "Command: python src/cleanup.py --dry-run\n"),
    ("refresh-solutions", "scope-preserved", "docs/solutions/unrelated.md", "removed historical reasoning"),
])
def test_independent_assertion_detects_targeted_failure(tmp_path, skill, check, file, replacement):
    target, response, events = workspace(tmp_path, skill)
    complete(skill, target, events)
    write(target, file, replacement)
    assert_check(skill, check, target, response, events, passes=False)


@pytest.mark.parametrize("change", ["started", "exit", "narrated", "wrong-output", "reversed", "compound"])
def test_verification_requires_successful_separate_observed_commands(tmp_path, change):
    target, response, events = workspace(tmp_path, "verify-product")
    complete("verify-product", target, events)
    data = json.loads(events.read_text())
    if change == "started":
        data[0]["type"] = "item.started"
    elif change == "exit":
        data[0]["item"]["exit_code"] = 1
    elif change == "narrated":
        data[0]["item"]["type"] = "agent_message"
    elif change == "wrong-output":
        data[0]["item"]["aggregated_output"] = '{"id": 7, "text": "Existing user note"}'
    elif change == "reversed":
        data.reverse()
    elif change == "compound":
        data[0]["item"]["command"] += " && echo done"
    events.write_text(json.dumps(data))
    assert_check("verify-product", "completed-command-evidence", target, response, events, passes=False)


def test_verification_accepts_native_shell_wrapper(tmp_path):
    import shlex
    target, response, events = workspace(tmp_path, "verify-product")
    complete("verify-product", target, events)
    data = json.loads(events.read_text())
    for event in data:
        event["item"]["command"] = shlex.join(["/bin/zsh", "-lc", event["item"]["command"]])
    events.write_text(json.dumps(data))
    assert_check("verify-product", "completed-command-evidence", target, response, events)


@pytest.mark.parametrize("skill", ["understand-codebase", "product-discovery"])
@pytest.mark.parametrize("mutation", [None, "edit", "delete", "add", "symlink"])
def test_assessment_preserves_sources_and_rejects_scope_changes(tmp_path, skill, mutation):
    target, response, events = workspace(tmp_path, skill)
    write(target, ".agents/skills/example/SKILL.md", "Runtime-controlled procedure\n")
    _, case = load_case(skill)
    source = target / case["workspace_files"][0]["path"]
    if mutation == "edit":
        source.write_text("Invented consumer policy or evidence\n")
    elif mutation == "delete":
        source.unlink()
    elif mutation == "add":
        write(target, "implementation.py", "print('unexpected implementation')\n")
    elif mutation == "symlink":
        original = tmp_path / "original"
        source.rename(original)
        source.symlink_to(original)
    assert_check(skill, "scope", target, response, events, passes=mutation is None)
