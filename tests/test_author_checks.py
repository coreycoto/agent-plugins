from __future__ import annotations

import json
from pathlib import Path

import pytest

from author_checks.plugin_validation import validate_portable_plugin

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/agent-plugins-1.0.0.schema.json").read_text())


def manifest(root: Path, **fields: object) -> None:
    root.mkdir(exist_ok=True)
    (root / "plugin.json").write_text(json.dumps({
        "$schema": SCHEMA["$id"], "name": "example", "version": "0.7.0", **fields,
    }))


def test_catalog_packages_conform() -> None:
    for root in (ROOT / "plugins").iterdir():
        assert not validate_portable_plugin(root, SCHEMA)


@pytest.mark.parametrize("payload", [
    '{"name":"example","name":"other"}',
    '{"name":"example","extensions":{"org.example":{"value":NaN}}}',
])
def test_ambiguous_or_non_json_manifests_are_rejected(tmp_path: Path, payload: str) -> None:
    (tmp_path / "plugin.json").write_text(payload)
    assert any("invalid" in error for error in validate_portable_plugin(tmp_path, SCHEMA))


@pytest.mark.parametrize("field", ["apps", "hooks"])
def test_extension_references_require_contained_files(tmp_path: Path, field: str) -> None:
    manifest(tmp_path, extensions={"com.openai": {field: "./com.openai/data"}})
    directory = tmp_path / "com.openai/data"
    directory.mkdir(parents=True)
    assert any("invalid" in error for error in validate_portable_plugin(tmp_path, SCHEMA))
    directory.rmdir()
    directory.write_text("{}")
    assert not validate_portable_plugin(tmp_path, SCHEMA)
    directory.unlink()
    directory.symlink_to(tmp_path.parent / "outside")
    assert validate_portable_plugin(tmp_path, SCHEMA)


@pytest.mark.parametrize("header", [
    "name: wrong\ndescription: Example", "name: example\ndescription: ''",
    "name: example\ndescription: Example\nmetadata:\n  version: 1",
])
def test_skill_identity_and_metadata_are_checked(tmp_path: Path, header: str) -> None:
    manifest(tmp_path)
    skill = tmp_path / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(f"---\n{header}\n---\nInstructions.\n")
    assert validate_portable_plugin(tmp_path, SCHEMA)
