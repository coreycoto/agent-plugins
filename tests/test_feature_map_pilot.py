"""Synthetic consumer pilot: real local CLI evidence and structural map checks."""
from __future__ import annotations

import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "evals/owned-workflows/verify-product/fixtures"
VALIDATOR = REPO / "plugins/product-development/skills/maintain-verification/scripts/check_feature_map.py"


def test_notes_cli_feature_map_pilot_retains_observation_and_preserves_consumer_data(tmp_path):
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    for name in ("notes.py", "README.md", "data/user-notes.json"):
        destination = consumer / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURES / name, destination)
    protected = {name: (consumer / name).read_bytes() for name in ("notes.py", "README.md", "data/user-notes.json")}
    source_hash = hashlib.sha256(protected["notes.py"]).hexdigest()
    harness = consumer / "verify_notes.py"
    harness.write_text(textwrap.dedent('''\
        import hashlib
        import json
        import subprocess
        import sys
        from pathlib import Path

        root = Path.cwd()
        store = root / ".artifacts/trial-notes.json"
        if store.exists():
            raise SystemExit("Disposable store already exists; preserve it instead of overwriting.")
        observations = []
        for action, extra in (("add", ["Trial note"]), ("list", [])):
            argv = [sys.executable, "-B", "notes.py", "--store", ".artifacts/trial-notes.json", action, *extra]
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=10)
            observations.append({"argv": argv, "cwd": str(root), "exit_code": result.returncode,
                                 "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode != 0:
                break
        evidence = {"kind": "synthetic-local-cli-observation", "commands": observations,
                    "source_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                      for name in ("notes.py", "README.md", "verify_notes.py")},
                    "environment": {"kind": "isolated-local-fixture", "python": sys.version}}
        receipt = root / "evidence/notes.json"
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(evidence, indent=2) + "\\n")
        if store.exists():
            store.unlink()
        raise SystemExit(0 if len(observations) == 2 and all(item["exit_code"] == 0 for item in observations) else 1)
        '''))
    feature = {
        "id": "notes-add-list",
        "behavior": {"source": "README.md", "expected": "Add and list print JSON for an isolated disposable store while existing user notes remain unchanged."},
        "entrypoint": "notes CLI add then list",
        "relevant_files": ["notes.py", "verify_notes.py"],
        "verification": {"argv": [sys.executable, "-B", "verify_notes.py"], "cwd": ".",
                         "prerequisites": ["Python is available; the owned trial store does not already exist."],
                         "evidence": ["evidence/notes.json"]},
        "qualification": {"state": "unverified", "source_revision": None, "environment": None,
                          "reason": "Planned synthetic consumer run; no CLI observed yet."},
    }
    document = {"schema_version": 1, "features": [feature]}
    map_path = consumer / "feature-map.json"
    map_path.write_text(json.dumps(document))
    inspect = runpy.run_path(str(VALIDATOR))["inspect_feature_map"]
    initial = inspect(map_path, consumer)
    assert initial["valid"]
    assert initial["features"][0]["missing_planned_evidence"] == ["evidence/notes.json"]
    assert initial["features"][0]["declared_state"] == "unverified"
    assert not initial["qualification_verified"]
    assert not (consumer / "evidence").exists()
    assert not (consumer / ".artifacts/trial-notes.json").exists()

    # The consumer harness performs the authorized commands, separately from the
    # validator. Its receipt records the commands' actual output before cleanup.
    result = subprocess.run(feature["verification"]["argv"], cwd=consumer, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt_path = consumer / "evidence/notes.json"
    evidence = json.loads(receipt_path.read_text())
    assert evidence["kind"] == "synthetic-local-cli-observation"
    assert evidence["source_sha256"]["notes.py"] == source_hash
    assert evidence["source_sha256"]["README.md"] == hashlib.sha256(protected["README.md"]).hexdigest()
    assert evidence["source_sha256"]["verify_notes.py"] == hashlib.sha256(harness.read_bytes()).hexdigest()
    expected_note = {"id": 1, "text": "Trial note"}
    for observation, action, extra, expected in zip(
        evidence["commands"], ("add", "list"), (["Trial note"], []), (expected_note, [expected_note]), strict=True,
    ):
        assert observation["argv"] == [sys.executable, "-B", "notes.py", "--store", ".artifacts/trial-notes.json", action, *extra]
        assert observation["cwd"] == str(consumer)
        assert observation["exit_code"] == 0 and observation["stderr"] == ""
        assert json.loads(observation["stdout"]) == expected
    assert evidence["environment"]["kind"] == "isolated-local-fixture"
    assert not (consumer / ".artifacts/trial-notes.json").exists()
    assert receipt_path.is_file(), "Observed evidence must survive owned cleanup"
    assert {name: (consumer / name).read_bytes() for name in protected} == protected

    feature["qualification"] = {
        "state": "passed", "source_revision": "notes.py-sha256:" + source_hash,
        "environment": "synthetic-local-python",
        "reason": "Separate add/list CLI invocations returned expected JSON; evidence retained and existing user data preserved. This qualifies only the local synthetic fixture.",
    }
    map_path.write_text(json.dumps(document))
    qualified_map = inspect(map_path, consumer)
    assert qualified_map["valid"]
    assert qualified_map["features"][0]["declared_state"] == "passed"
    assert qualified_map["features"][0]["current_qualification"] == "unverified"
    assert not qualified_map["qualification_verified"]
    assert not qualified_map["coverage_complete"]
    assert qualified_map["features"][0]["missing_planned_evidence"] == []
    stale = inspect(map_path, consumer, ["notes.py"])
    assert stale["valid"] and stale["affected_features"] == ["notes-add-list"]
    assert stale["features"][0]["stale_candidate"]
    assert stale["features"][0]["declared_state"] == "passed"
    # Existing user storage belongs to a separate consumer surface; this map's
    # isolated add/list trial neither touches it nor claims coverage of it.
    unrelated = inspect(map_path, consumer, ["data/user-notes.json"])
    assert unrelated["valid"] and unrelated["affected_features"] == []
    assert not unrelated["features"][0]["stale_candidate"]
    assert not unrelated["coverage_complete"]
