"""Qualify synthetic artifacts and frozen graders, not model effectiveness."""
from __future__ import annotations

import ast
import json
import shlex
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals/owned-workflows"
SPECIALISTS = ("check-protocol", "rehearse-migration", "assess-data-quality")

# Grader-only controls. These scripts are not staged in an agent's measured task.
CONTROLS = {
    "check-protocol": '''from collections import deque
import json
from pathlib import Path
from protocol import State, next_states

def explore(repair):
    start = State()
    seen = {start}
    queue = deque([(start, [])])
    violation = None
    completion = None
    while queue:
        state, path = queue.popleft()
        if state.accepted > 1 and violation is None:
            violation = path
        if state.phase == "done" and completion is None:
            completion = path
        for action, target in next_states(state, repair=repair):
            if target not in seen:
                seen.add(target)
                queue.append((target, path + [action]))
    return violation, completion, len(seen)

bad, _, count = explore(False)
control, completed, control_count = explore(True)
result = {"unsafe_trace": bad, "completion_trace": completed,
          "control_has_violation": control is not None, "progress_checked": False,
          "unsafe_state_count": count, "control_state_count": control_count,
          "assumptions": "One operation, acceptance cap two, no receiver deduplication or fairness.",
          "implementation_limits": "Finite synthetic state model, not production implementation proof."}
text = json.dumps(result)
Path("evidence.json").write_text(text)
print(text)
''',
    "rehearse-migration": '''from decimal import Decimal
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile

out = Path("artifacts")
out.mkdir()
def snapshot(db, name):
    target = sqlite3.connect(out / (name + ".sqlite3"))
    try:
        db.backup(target)
    finally:
        target.close()

with tempfile.TemporaryDirectory() as scratch:
    path = Path(scratch) / "work.sqlite3"
    db = sqlite3.connect(path)
    db.executescript(Path("schema.sql").read_text())
    snapshot(db, "before")
    db.executescript(Path("expand.sql").read_text())
    db.executescript(Path("backfill.sql").read_text())
    db.execute("INSERT INTO invoices (id, amount_text) VALUES (?, ?)", ("c", "2.50"))
    db.commit()
    db.close()
    db = sqlite3.connect(path)
    snapshot(db, "after")
    missing = [row[0] for row in db.execute("SELECT id FROM invoices WHERE amount_cents IS NULL ORDER BY id")]
    db.executescript(Path("backfill.sql").read_text())
    snapshot(db, "resumed")
    mismatches = [key for key, text, cents in db.execute("SELECT id, amount_text, amount_cents FROM invoices ORDER BY id") if int(Decimal(text) * 100) != cents]
    accepted = {row[0] for row in db.execute("SELECT id FROM invoices")}
    db.close()
shutil.copyfile(out / "before.sqlite3", out / "restored.sqlite3")
restored = sqlite3.connect(out / "restored.sqlite3")
retained = {row[0] for row in restored.execute("SELECT id FROM invoices")}
restored.close()
result = {"conversion_mismatches": mismatches, "missing_new_values": missing,
          "restore_loses_ids": sorted(accepted - retained), "fresh_process_tested": False,
          "new_writer_tested": False, "rollout_limits": "SQLite connection reopen and local restore only; old writers remain incompatible with the new-reader field."}
text = json.dumps(result)
Path("evidence.json").write_text(text)
print(text)
''',
    "assess-data-quality": '''from collections import Counter
import csv
from decimal import Decimal
import json
from pathlib import Path

with Path("data.csv").open(newline="") as stream:
    rows = list(csv.DictReader(stream))
population = json.loads(Path("population.json").read_text())
def key(row):
    return ":".join(row[field] for field in ("source", "id", "revision"))
counts = Counter(map(key, rows))
result = {"dataset_id": population["dataset_id"],
          "missing_sources": sorted(set(population["expected_sources"]) - {row["source"] for row in rows}),
          "duplicate_keys": sorted(k for k, count in counts.items() if count > 1),
          "invalid_unit_keys": sorted({key(row) for row in rows if row["unit"] not in {"sqft", "sqm"}}),
          "invalid_area_keys": sorted({key(row) for row in rows if (not row["area"] and row["status"] != "not-reported") or (row["area"] and Decimal(row["area"]) < 0)}),
          "rows_examined": len(rows), "expected_source_count": len(population["expected_sources"]),
          "freshness_verified": False, "external_accuracy_verified": False}
text = json.dumps(result)
Path("evidence.json").write_text(text)
print(text)
''',
}
SCRIPTS = {"check-protocol": "analysis.py", "rehearse-migration": "rehearsal.py", "assess-data-quality": "assessment.py"}


def stage(tmp_path, skill):
    suite = EVALS / skill
    case = json.loads((suite / "evals.json").read_text())["evals"][0]
    target = tmp_path / "consumer"
    target.mkdir()
    for entry in case["workspace_files"]:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / entry["source"], destination)
    response = tmp_path / "response.txt"
    response.write_text("Result for independent artifact and semantic review.\n")
    events = tmp_path / "events.json"
    events.write_text("[]")
    return target, response, events


def complete(target, events, skill):
    script = SCRIPTS[skill]
    (target / script).write_text(CONTROLS[skill])
    command = [sys.executable, "-B", script]
    run = subprocess.run(command, cwd=target, text=True, capture_output=True, timeout=10, check=True)
    events.write_text(json.dumps([{"type": "item.completed", "item": {
        "type": "command_execution", "status": "completed", "exit_code": run.returncode,
        "command": shlex.join(command), "aggregated_output": run.stdout,
    }}]))


def inventory(target):
    return {str(path.relative_to(target)): path.read_bytes() for path in target.rglob("*") if path.is_file()}


def check(skill, target, response, events, *, passes=True, execution=False, suite=None):
    suite = suite or EVALS / skill
    name = "scope.py" if skill == "engineering-judgment" else ("execution.py" if execution else "check.py")
    before = inventory(target)
    run = subprocess.run([sys.executable, "-I", "-B", str(suite / "oracles" / name), str(target), str(response), str(events)], capture_output=True, text=True, timeout=10)
    assert run.returncode == (0 if passes else 1), run.stdout + run.stderr
    assert run.stdout.startswith("PASS:" if passes else "FAIL:")
    assert inventory(target) == before, "Grader changed submitted workspace"


def alter_evidence(target, **changes):
    path = target / "evidence.json"
    result = json.loads(path.read_text())
    result.update(changes)
    path.write_text(json.dumps(result))


@pytest.mark.parametrize("skill", SPECIALISTS)
def test_controls_produce_independently_valid_artifacts_and_commands(tmp_path, skill):
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    check(skill, target, response, events)
    check(skill, target, response, events, execution=True)
    if skill == "check-protocol":
        result = json.loads((target / "evidence.json").read_text())
        assert result["unsafe_state_count"] == 9
        assert result["control_state_count"] == 4


@pytest.mark.parametrize("skill", (*SPECIALISTS, "engineering-judgment"))
def test_frozen_evaluator_runs_without_publisher_or_submitted_imports(tmp_path, skill):
    target, response, events = stage(tmp_path, skill)
    if skill in SPECIALISTS:
        complete(target, events, skill)
    frozen_parent = tmp_path / "frozen"
    frozen_parent.mkdir()
    shutil.copyfile(EVALS / "_engineering_oracle.py", frozen_parent / "_engineering_oracle.py")
    suite = frozen_parent / skill
    shutil.copytree(EVALS / skill / "oracles", suite / "oracles")
    shutil.copytree(EVALS / skill / "fixtures", suite / "fixtures")
    check(skill, target, response, events, suite=suite)
    if skill in SPECIALISTS:
        # The artifact grader reads evidence; it never executes this submitted code.
        (target / SCRIPTS[skill]).write_text("raise RuntimeError('Do not run me during grading')\n")
        check(skill, target, response, events, suite=suite)


@pytest.mark.parametrize("skill", SPECIALISTS)
def test_original_input_is_not_a_completed_result(tmp_path, skill):
    target, response, events = stage(tmp_path, skill)
    check(skill, target, response, events, passes=False)


@pytest.mark.parametrize("change", [
    {"unsafe_trace": []}, {"unsafe_trace": ["accept_lost", "dispatch"]},
    {"unsafe_trace": ["dispatch", "accept_reply"]},
    {"completion_trace": ["dispatch", "accept_lost", "wait"]},
    {"control_has_violation": True}, {"progress_checked": True}, {"progress_checked": 0},
    {"implementation_limits": ""},
])
def test_protocol_rejects_invalid_or_overclaimed_evidence(tmp_path, change):
    skill = "check-protocol"
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    alter_evidence(target, **change)
    check(skill, target, response, events, passes=False)


@pytest.mark.parametrize("change", [
    {"conversion_mismatches": []}, {"conversion_mismatches": ["a", "b", "c"]},
    {"missing_new_values": []}, {"restore_loses_ids": []},
    {"fresh_process_tested": True}, {"new_writer_tested": True}, {"rollout_limits": ""},
])
def test_migration_rejects_omissions_and_false_runtime_claims(tmp_path, change):
    skill = "rehearse-migration"
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    alter_evidence(target, **change)
    check(skill, target, response, events, passes=False)


@pytest.mark.parametrize(("name", "sql"), [
    ("before", "DELETE FROM invoices WHERE id='b'"),
    ("after", "UPDATE invoices SET amount_cents=250 WHERE id='c'"),
    ("resumed", "UPDATE invoices SET amount_cents=125 WHERE id='a'"),
    ("restored", "INSERT INTO invoices VALUES ('c', '2.50')"),
])
def test_migration_report_cannot_substitute_for_actual_snapshot_values(tmp_path, name, sql):
    skill = "rehearse-migration"
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    db = sqlite3.connect(target / "artifacts" / f"{name}.sqlite3")
    db.execute(sql)
    db.commit()
    db.close()
    check(skill, target, response, events, passes=False)


@pytest.mark.parametrize("change", [
    {"missing_sources": []}, {"expected_source_count": 2}, {"rows_examined": 5},
    {"duplicate_keys": ["north:n1:1", "south:s1:1"]},
    {"invalid_area_keys": ["north:n2:1", "south:s1:1"]},
    {"invalid_unit_keys": []}, {"freshness_verified": True},
    {"external_accuracy_verified": True}, {"dataset_id": "different-snapshot"},
])
def test_data_quality_keeps_independent_population_and_legitimate_exceptions(tmp_path, change):
    skill = "assess-data-quality"
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    alter_evidence(target, **change)
    check(skill, target, response, events, passes=False)


@pytest.mark.parametrize("skill", SPECIALISTS)
@pytest.mark.parametrize("mutation", ["missing", "started", "nonzero", "bool-exit", "echo", "other-script", "wrong-output"])
def test_execution_requires_an_actual_successful_task_command(tmp_path, skill, mutation):
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    captured = json.loads(events.read_text())
    item = captured[0]["item"]
    if mutation == "missing":
        captured = []
    elif mutation == "started":
        captured[0]["type"] = "item.started"
    elif mutation == "nonzero":
        item["exit_code"] = 1
    elif mutation == "bool-exit":
        item["exit_code"] = False
    elif mutation == "echo":
        item["command"] = "echo " + shlex.quote(item["aggregated_output"])
    elif mutation == "other-script":
        item["command"] = "python another.py"
    elif mutation == "wrong-output":
        item["aggregated_output"] = "{}"
    events.write_text(json.dumps(captured))
    check(skill, target, response, events, passes=False, execution=True)


@pytest.mark.parametrize("skill", SPECIALISTS)
def test_native_shell_wrapping_is_supported_but_compound_commands_are_not(tmp_path, skill):
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    captured = json.loads(events.read_text())
    command = captured[0]["item"]["command"]
    captured[0]["item"]["command"] = shlex.join(["/bin/bash", "-lc", command])
    events.write_text(json.dumps(captured))
    check(skill, target, response, events, execution=True)
    captured[0]["item"]["command"] = command + " && echo completed"
    events.write_text(json.dumps(captured))
    check(skill, target, response, events, passes=False, execution=True)


@pytest.mark.parametrize("skill", (*SPECIALISTS, "engineering-judgment"))
@pytest.mark.parametrize("mutation", [None, "edit", "add", "delete", "symlink"])
def test_source_scope_and_harness_owned_closure_are_distinct(tmp_path, skill, mutation):
    target, response, events = stage(tmp_path, skill)
    if skill in SPECIALISTS:
        complete(target, events, skill)
    closure = target / ".agents/skills/example/SKILL.md"
    closure.parent.mkdir(parents=True)
    closure.write_text("Separately frozen and checked by evaluation runtime.\n")
    source = target / next((EVALS / skill / "fixtures").iterdir()).name
    if mutation == "edit":
        source.write_text("Changed accepted contract\n")
    elif mutation == "add":
        (target / "extra.py").write_text("Unexpected work\n")
    elif mutation == "delete":
        source.unlink()
    elif mutation == "symlink":
        original = tmp_path / "unowned-input"
        source.rename(original)
        source.symlink_to(original)
    check(skill, target, response, events, passes=mutation is None)


@pytest.mark.parametrize("payload", ['{"progress_checked": false, "progress_checked": true}', '{"value": NaN}', '[]'])
def test_malformed_or_ambiguous_evidence_is_not_accepted(tmp_path, payload):
    skill = "check-protocol"
    target, response, events = stage(tmp_path, skill)
    complete(target, events, skill)
    (target / "evidence.json").write_text(payload)
    check(skill, target, response, events, passes=False)


def test_corpus_contract_and_grader_separation():
    for skill in (*SPECIALISTS, "engineering-judgment"):
        suite = EVALS / skill
        data = json.loads((suite / "evals.json").read_text())
        assert data["schema_version"] == 3
        expected_name = "design-change" if skill == "engineering-judgment" else skill
        assert data["skill_name"] == f"product-development:{expected_name}"
        assert data["grader_support"] == ["_engineering_oracle.py"]
        for case in data["evals"]:
            assert case["execution_mode"] == "artifact-safe"
            assert case["expected_output"] not in case["prompt"]
            assert "$product-development" not in case["prompt"]
            for entry in case["workspace_files"]:
                assert Path(entry["path"]).name == entry["path"]
                source = (suite / entry["source"]).resolve()
                assert source.is_relative_to(suite / "fixtures") and source.is_file()
            for item in case["checks"]:
                if item["type"] == "assertion":
                    assert (suite / item["script"]).is_file()
        if skill in SPECIALISTS:
            triggers = json.loads((suite / "trigger_queries.json").read_text())
            assert triggers["schema_version"] == 2 and triggers["skill_name"] == data["skill_name"]
            for split in ("train", "validation"):
                assert {q["should_trigger"] for q in triggers["queries"] if q["split"] == split} == {True, False}


def test_new_skill_bodies_and_references_are_packaged():
    root = ROOT / "plugins/product-development"
    for name in SPECIALISTS:
        entry = root / "skills" / name / "SKILL.md"
        content = entry.read_text()
        header = yaml.safe_load(content.split("---", 2)[1])
        assert header["name"] == name and len(header["description"]) <= 1024
        assert content.count("\n") < 80
        assert list((entry.parent / "references").glob("*.md"))
    assert len(list((root / "skills").glob("*/SKILL.md"))) == 19
    for path in (EVALS / "_engineering_oracle.py", Path(__file__)):
        ast.parse(path.read_text())
