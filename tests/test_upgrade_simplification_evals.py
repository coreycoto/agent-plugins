"""Qualify reference-trial inputs and frozen scope graders, not model judgment."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parents[1] / "evals/owned-workflows"
SUITES = {
    "version-upgrade-catalog": "product-development:design-change",
    "diff-scoped-simplification": "product-development:implement-change",
    "premise-reset": "product-development:diagnose-problem",
    "resource-bounds": "product-development:improve-performance",
    "repeatable-work": "product-development:phased-refactor",
    "principle-steering": "product-development:engineering-workflow",
    "task-depth-development": "product-development:engineering-workflow",
    "task-depth-product": "product-management:product-discovery",
    "task-depth-writing": "communication:write-prose",
}
CASES = [
    (name, index)
    for name in SUITES
    for index, _ in enumerate(json.loads((EVALS / name / "evals.json").read_text())["evals"])
]


def stage(tmp_path, suite_name, case_index=0):
    suite = EVALS / suite_name
    data = json.loads((suite / "evals.json").read_text())
    case = data["evals"][case_index]
    target = tmp_path / "consumer"
    target.mkdir()
    for entry in case["workspace_files"]:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / entry["source"], destination)
    response = tmp_path / "response.txt"
    response.write_text("Recommendation requires separate semantic grading.\n")
    events = tmp_path / "events.json"
    events.write_text("[]\n")
    return suite, target, response, events


def grade(suite, target, response, events, *, passes=True):
    before = {str(path.relative_to(target)): path.read_bytes()
              for path in target.rglob("*") if path.is_file()}
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(suite / "oracles/source-preserved.py"),
         str(target), str(response), str(events)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == (0 if passes else 1), result.stdout + result.stderr
    assert result.stdout.startswith("PASS" if passes else "FAIL"), result.stdout
    after = {str(path.relative_to(target)): path.read_bytes()
             for path in target.rglob("*") if path.is_file()}
    assert before == after, "Grader changed the measured workspace"


@pytest.mark.parametrize("suite_name", SUITES)
def test_reference_trials_use_existing_skills_and_separate_semantic_grading(suite_name):
    suite = EVALS / suite_name
    data = json.loads((suite / "evals.json").read_text())
    assert data["schema_version"] == 3
    assert data["skill_name"] == SUITES[suite_name]
    assert data["grader_support"] == ["_readonly_oracle.py"]
    assert len({case["id"] for case in data["evals"]}) == len(data["evals"])
    for case in data["evals"]:
        assert case["execution_mode"] == "artifact-safe"
        assert case["tiers"] == ["smoke", "deep"]
        assert case["expected_output"] not in case["prompt"]
        assert data["skill_name"] not in case["prompt"]
        files = set()
        for entry in case["workspace_files"]:
            source = (suite / entry["source"]).resolve()
            assert source.is_relative_to(suite / "fixtures") and source.is_file()
            assert Path(entry["path"]).name == entry["path"]
            files.add(entry["path"])
            assert case["expected_output"] not in source.read_text()
        assert files == {path.name for path in (suite / "fixtures").iterdir()}
        assert {check["type"] for check in case["checks"]} == {"assertion", "rubric"}
        for check in case["checks"]:
            if check["type"] == "assertion":
                assert (suite / check["script"]).is_file()
            else:
                assert check["text"] == case["expected_output"]


@pytest.mark.parametrize(("suite_name", "case_index"), CASES)
def test_every_case_accepts_unchanged_inputs_without_importing_the_fixture(tmp_path, suite_name, case_index):
    suite, target, response, events = stage(tmp_path, suite_name, case_index)
    grade(suite, target, response, events)


@pytest.mark.parametrize("suite_name", SUITES)
@pytest.mark.parametrize("mutation", ["edit", "add", "delete", "symlink"])
def test_scope_grader_rejects_changes_and_unrequested_artifacts(tmp_path, suite_name, mutation):
    suite, target, response, events = stage(tmp_path, suite_name)
    source = target / "brief.md"
    if mutation == "edit":
        source.write_text(source.read_text() + "\nUnrequested change.\n")
    elif mutation == "add":
        (target / "plan.md").write_text("Output was requested only in the response.\n")
    elif mutation == "delete":
        source.unlink()
    else:
        source.unlink()
        source.symlink_to(suite / "fixtures/brief.md")
    grade(suite, target, response, events, passes=False)


@pytest.mark.parametrize("suite_name", SUITES)
def test_frozen_grader_and_harness_instruction_namespace_are_independent(tmp_path, suite_name):
    suite, target, response, events = stage(tmp_path, suite_name)
    parent = tmp_path / "frozen"
    parent.mkdir()
    shutil.copyfile(EVALS / "_readonly_oracle.py", parent / "_readonly_oracle.py")
    frozen = parent / suite_name
    shutil.copytree(suite / "oracles", frozen / "oracles")
    shutil.copytree(suite / "fixtures", frozen / "fixtures")
    closure = target / ".agents/skills/example/SKILL.md"
    closure.parent.mkdir(parents=True)
    closure.write_text("The runner separately freezes this instruction closure.\n")
    grade(frozen, target, response, events)
    # Scope preservation is not semantic correctness or an instruction-integrity check.
    response.write_text("An unsupported recommendation still needs the rubric to reject it.\n")
    grade(frozen, target, response, events)
