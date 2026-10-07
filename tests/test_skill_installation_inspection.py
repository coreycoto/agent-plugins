from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from inspect_skill_installation import InspectionError, inspect, package

ROOT = Path(__file__).resolve().parents[1]


def make_package(root: Path, *, codex: bool = False, version: str = "1.0.0") -> Path:
    manifest = root / (".codex-plugin/plugin.json" if codex else "plugin.json")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"name": "example", "version": version,
                                   "repository": "https://github.com/example/workflows"}))
    make_skill(root / "skills", "repair", "Use an independent reproducer.\n")
    reference = root / "skills/_shared/references/guide.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("Preserve accepted policy.\n")
    return root


def make_skill(root: Path, name: str, body: str) -> Path:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {name}\ndescription: Test procedure\n---\n\n{body}")
    return path


def snapshot(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*") if path.is_file()}


def test_portable_codex_same_workflows_do_not_establish_session(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    installed = make_package(tmp_path / "installed", codex=True)
    before = snapshot(tmp_path)
    result = inspect(candidate, [installed], [])
    assert result["comparisons"][0]["identity_matches"] is True
    assert result["comparisons"][0]["workflow_content_matches"] is True
    assert result["active_session"]["status"] == "unverified"
    assert result["active_session"]["reload_verified"] is False
    assert result["active_session"]["automatic_selection_verified"] is False
    assert result["mutations_performed"] is False
    assert snapshot(tmp_path) == before


def test_same_version_can_hide_changed_body_reference_and_inventory(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    installed = make_package(tmp_path / "installed")
    (installed / "skills/repair/SKILL.md").write_text(
        (installed / "skills/repair/SKILL.md").read_text().replace("independent", "incorrect"))
    (installed / "skills/_shared/references/guide.md").unlink()
    make_skill(installed / "skills", "extra", "Unrelated procedure.")
    comparison = inspect(candidate, [installed], [])["comparisons"][0]
    assert comparison["identity_matches"] is True
    assert comparison["workflow_content_matches"] is False
    assert comparison["changed_files"] == ["repair/SKILL.md"]
    assert comparison["missing_files"] == ["_shared/references/guide.md"]
    assert comparison["extra_files"] == ["extra/SKILL.md"]


def test_fingerprint_location_independent_and_metadata_separate(tmp_path: Path) -> None:
    first = make_package(tmp_path / "first")
    second = make_package(tmp_path / "second", version="2.0.0")
    a, b = package(first), package(second)
    assert a["workflow_fingerprint"] == b["workflow_fingerprint"]
    assert inspect(first, [second], [])["comparisons"][0]["identity_matches"] is False
    assert a["source"]["acquisition_origin"].startswith("not observed")


def test_duplicate_names_and_literal_bodies_have_distinct_meaning(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    installed = make_package(tmp_path / "installed")
    discovery = tmp_path / "legacy"
    make_skill(discovery, "repair", "A different procedure.")
    make_skill(discovery, "alias", "Use an independent reproducer.\n")
    result = inspect(candidate, [installed], [discovery, installed / "skills"])
    names = result["duplicates"]["names"]
    bodies = result["duplicates"]["equivalent_bodies"]
    assert len(names) == 1 and names[0]["value"] == "repair"
    assert len(names[0]["members"]) == 2  # Repeated observation of one path is not another copy.
    assert len(bodies) == 1
    assert {item["name"] for item in bodies[0]["members"]} == {"repair", "alias"}
    assert next(item for item in names[0]["members"] if item["qualified_name"])["qualified_name"] == "example:repair"


def test_supplied_observations_require_exact_session_and_file_bytes(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    skill = candidate / "skills/repair/SKILL.md"
    observations = tmp_path / "observations.json"
    data = {"kind": "active-session-skill-read", "session_id": "session-a",
            "skills": [{"qualified_name": "example:repair",
                        "file_sha256": hashlib.sha256(skill.read_bytes()).hexdigest()}]}
    observations.write_text(json.dumps(data))
    with pytest.raises(InspectionError, match="matching session ID"):
        inspect(candidate, [], [], session_observations=observations, session_id="session-b")
    result = inspect(candidate, [], [], session_observations=observations, session_id="session-a")
    assert len(result["active_session"]["matching_observations"]) == 1
    assert result["active_session"]["reload_verified"] is False
    data["skills"][0]["file_sha256"] = "0" * 64
    observations.write_text(json.dumps(data))
    result = inspect(candidate, [], [], session_observations=observations, session_id="session-a")
    assert result["active_session"]["status"] == "unverified"
    assert len(result["active_session"]["unmatched_observations"]) == 1


def test_cli_inventory_and_secret_looking_files_cannot_claim_discovery(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    (candidate / "auth.json").write_text('SECRET-AUTH-CONTENT')
    (candidate / "skills/.env").write_text('SECRET-ENV-CONTENT')
    inventory = tmp_path / "native.json"
    inventory.write_text(json.dumps({"installed": True, "enabled": True, "secret": "PRIVATE"}))
    result = inspect(candidate, [], [], native_inventory=inventory)
    output = json.dumps(result)
    assert all(secret not in output for secret in ("SECRET-AUTH", "SECRET-ENV", "PRIVATE"))
    assert result["active_session"]["status"] == "unverified"
    assert result["native_inventory"]["sha256"] == hashlib.sha256(inventory.read_bytes()).hexdigest()


def test_descendant_links_and_invalid_inputs_fail_closed(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    external = make_skill(tmp_path / "outside", "outside", "Outside content.")
    (candidate / "skills/linked").symlink_to(external.parent, target_is_directory=True)
    with pytest.raises(InspectionError, match="Descendant links"):
        package(candidate)
    (candidate / "skills/linked").unlink()
    (candidate / "skills/repair/SKILL.md").write_text("Malformed SECRET-VALUE")
    with pytest.raises(InspectionError) as error:
        package(candidate)
    assert "SECRET-VALUE" not in str(error.value)
    with pytest.raises(InspectionError):
        package(tmp_path / "missing")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(InspectionError, match="manifest"):
        package(empty)


def test_cli_reports_json_without_changing_inputs_or_installing(tmp_path: Path) -> None:
    candidate = make_package(tmp_path / "candidate")
    installed = tmp_path / "installed"
    shutil.copytree(candidate, installed)
    before = snapshot(tmp_path)
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/inspect_skill_installation.py"),
                             "--candidate", str(candidate), "--installed", str(installed)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["comparisons"][0]["workflow_content_matches"] is True
    assert snapshot(tmp_path) == before
    invalid = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/inspect_skill_installation.py"),
                              "--candidate", str(tmp_path / "missing")], capture_output=True, text=True)
    assert invalid.returncode == 2
    assert json.loads(invalid.stdout)["mutations_performed"] is False
