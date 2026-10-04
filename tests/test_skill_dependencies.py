from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

import pytest

from author_checks.skills_lock import (
    load_github_skill_lock,
    native_skill_hash,
    verify_installed_dependencies,
)

SKILL = b"---\nname: example-skill\ndescription: Example dependency\n---\nInstructions.\n"


@pytest.fixture
def installation(tmp_path: Path) -> tuple[Path, Path, Path]:
    entry = {
        "source": "example/skills", "ref": "a" * 40, "sourceType": "github",
        "skillPath": "skills/example-skill/SKILL.md",
        "computedHash": hashlib.sha256(b"SKILL.md" + SKILL).hexdigest(),
    }
    publisher = tmp_path / "plugin" / "skills-lock.json"
    publisher.parent.mkdir()
    publisher.write_text(json.dumps({"version": 1, "skills": {"example-skill": entry}}))
    consumer = tmp_path / "consumer" / "skills-lock.json"
    consumer.parent.mkdir()
    consumer.write_bytes(publisher.read_bytes())
    installed = consumer.parent / ".agents" / "skills"
    skill = installed / "example-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(SKILL)
    return publisher, installed, consumer


def test_native_hash_matches_official_cli_fixture_and_detects_renames() -> None:
    # Golden produced by Skills 1.7.0's computeSkillFolderHash, not this implementation.
    files = {"SKILL.md": b"manifest\n", "agents/openai.yaml": b"metadata\n", "scripts/z.py": b"script\n"}
    assert native_skill_hash(files) == "7843e2769f9b073b5ad28256f18dffa18034c17dd01472a3334d91b245b465d9"
    moved = {**files, "scripts/a.py": files["scripts/z.py"]}
    del moved["scripts/z.py"]
    assert native_skill_hash(moved) != native_skill_hash(files)


def test_verified_installation_preserves_unrelated_consumer_entries(installation) -> None:
    publisher, installed, consumer = installation
    value = json.loads(consumer.read_text())
    value["skills"]["local-skill"] = {"source": "./local", "sourceType": "local", "computedHash": "b" * 64}
    consumer.write_text(json.dumps(value))
    before = consumer.read_bytes()
    assert verify_installed_dependencies(publisher, installed, consumer) == []
    assert consumer.read_bytes() == before


@pytest.mark.parametrize("field,value", [
    ("source", "other/skills"), ("ref", "b" * 40),
    ("skillPath", "skills/another/SKILL.md"), ("computedHash", "0" * 64),
])
def test_restored_lock_drift_is_checked_against_original_declaration(installation, field, value) -> None:
    publisher, installed, consumer = installation
    original = publisher.read_bytes()
    lock = json.loads(consumer.read_text())
    lock["skills"]["example-skill"][field] = value
    consumer.write_text(json.dumps(lock))
    errors = verify_installed_dependencies(publisher, installed, consumer)
    assert any("consumer lock differs" in error for error in errors)
    assert publisher.read_bytes() == original


def test_native_restore_rewritten_hash_does_not_hide_modified_content(installation) -> None:
    publisher, installed, consumer = installation
    changed = b"modified upstream file\n"
    (installed / "example-skill" / "SKILL.md").write_bytes(changed)
    lock = json.loads(consumer.read_text())
    lock["skills"]["example-skill"]["computedHash"] = hashlib.sha256(b"SKILL.md" + changed).hexdigest()
    consumer.write_text(json.dumps(lock))
    errors = verify_installed_dependencies(publisher, installed, consumer)
    assert any("installed content differs" in error for error in errors)
    assert any("consumer lock differs" in error for error in errors)


def test_partial_restore_and_extra_files_are_not_success(installation) -> None:
    publisher, installed, consumer = installation
    (installed / "example-skill" / "SKILL.md").unlink()
    errors = verify_installed_dependencies(publisher, installed, consumer)
    assert any("missing installed SKILL.md" in error for error in errors)
    (installed / "example-skill" / "SKILL.md").write_bytes(SKILL)
    (installed / "example-skill" / "unexpected.md").write_text("extra")
    assert any("installed content differs" in error for error in verify_installed_dependencies(publisher, installed, consumer))


def test_installed_symlinks_and_unsafe_lock_are_rejected(installation, tmp_path: Path) -> None:
    publisher, installed, consumer = installation
    (installed / "example-skill" / "alias.md").symlink_to(tmp_path / "external.md")
    assert any("unsafe installed file" in error for error in verify_installed_dependencies(publisher, installed, consumer))
    link = tmp_path / "lock-link.json"
    link.symlink_to(publisher)
    with pytest.raises(ValueError, match="unsafe native skill lock"):
        load_github_skill_lock(link)


@pytest.mark.parametrize("field,value", [
    ("ref", "main"), ("ref", "a" * 12), ("computedHash", "bad"),
    ("skillPath", "../outside/SKILL.md"), ("skillPath", "/outside/SKILL.md"),
    ("skillPath", "skills/../outside/SKILL.md"), ("source", "../skills"),
])
def test_publisher_requires_immutable_refs_hashes_and_safe_skill_paths(installation, field, value) -> None:
    publisher, _, _ = installation
    lock = json.loads(publisher.read_text())
    lock["skills"]["example-skill"][field] = value
    publisher.write_text(json.dumps(lock))
    with pytest.raises(ValueError):
        load_github_skill_lock(publisher)


def test_custom_fields_and_duplicate_json_skill_names_are_rejected(installation) -> None:
    publisher, _, _ = installation
    original = json.loads(publisher.read_text())
    original["sources"] = {}
    publisher.write_text(json.dumps(original))
    with pytest.raises(ValueError, match="native version-1"):
        load_github_skill_lock(publisher)
    publisher.write_text('{"version":1,"skills":{"same":{},"same":{}}}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_github_skill_lock(publisher)


def test_dependencies_are_declared_without_bundled_copies(installation) -> None:
    publisher, _, _ = installation
    root = Path(__file__).resolve().parents[1]
    validate = runpy.run_path(str(root / "scripts/verify_skill_dependencies.py"))["validate_package_dependencies"]
    notice = publisher.parent / "licenses/example-skills-MIT.txt"
    notice.parent.mkdir()
    notice.write_text("MIT license notice")
    assert validate(publisher.parent) == []
    bundled = publisher.parent / "skills/example-skill"
    bundled.mkdir(parents=True)
    (bundled / "SKILL.md").write_bytes(SKILL)
    assert any("must not be bundled" in error for error in validate(publisher.parent))
