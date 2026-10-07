from __future__ import annotations

import json
from pathlib import Path

import pytest

from author_checks.owned_workflows import validate_source_lineage
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


def test_portable_mcp_requires_transport_type(tmp_path: Path) -> None:
    manifest(tmp_path)
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps({"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
                               "mcpServers": {"example": {"command": "python3"}}}))
    assert validate_portable_plugin(tmp_path, SCHEMA)
    data = json.loads(path.read_text())
    data["mcpServers"]["example"]["type"] = "stdio"
    path.write_text(json.dumps(data))
    assert not validate_portable_plugin(tmp_path, SCHEMA)


def test_onboarding_requires_contained_packaged_skill(tmp_path: Path) -> None:
    manifest(tmp_path, extensions={"com.openai": {"onboardingSkill": "./skills/onboard/SKILL.md"}})
    assert validate_portable_plugin(tmp_path, SCHEMA)
    path = tmp_path / "skills/onboard/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nname: onboard\ndescription: Onboard this plugin\n---\nInstructions.\n")
    assert not validate_portable_plugin(tmp_path, SCHEMA)


def test_removed_skill_body_is_not_silently_omitted(tmp_path: Path) -> None:
    manifest(tmp_path)
    directory = tmp_path / "skills/example/references"
    directory.mkdir(parents=True)
    (directory / "guide.md").write_text("Still packaged support content.")
    assert any("must contain SKILL.md" in error for error in validate_portable_plugin(tmp_path, SCHEMA))


def test_packaged_markdown_links_require_contained_files(tmp_path: Path) -> None:
    manifest(tmp_path)
    skill = tmp_path / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    body = "---\nname: example\ndescription: Example\n---\n[guide](references/guide.md#section)\n"
    skill.write_text(body)
    assert any("missing or escaping local Markdown reference" in error
               for error in validate_portable_plugin(tmp_path, SCHEMA))
    reference = skill.parent / "references/guide.md"
    reference.parent.mkdir()
    reference.write_text("[other][target]\n[target]: <other guide.md>\n")
    assert validate_portable_plugin(tmp_path, SCHEMA)
    (reference.parent / "other guide.md").write_text("Guidance.")
    (reference.parent / "guide (detail).md").write_text("Detail.")
    reference.write_text(reference.read_text() + "[detail](guide%20(detail).md)\n")
    assert not validate_portable_plugin(tmp_path, SCHEMA)
    reference.write_text("[outside](../../../../outside.md)\n")
    (tmp_path.parent / "outside.md").write_text("Exists outside the package.")
    assert any("escaping" in error for error in validate_portable_plugin(tmp_path, SCHEMA))


def test_external_links_and_code_examples_are_not_packaged_references(tmp_path: Path) -> None:
    manifest(tmp_path)
    skill = tmp_path / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("""---
name: example
description: Example
---
[web](https://example.com/missing.md) [anchor](#section) [mail](mailto:example@example.com)
`[inline](missing.md)`
~~~markdown
[example](missing.md)
~~~
    [indented example](missing.md)
""")
    assert not validate_portable_plugin(tmp_path, SCHEMA)


def test_source_lineage_requires_pinned_attributed_existing_destinations(tmp_path: Path) -> None:
    path = tmp_path / "skills/_shared/references/upstream-lineage.json"
    path.parent.mkdir(parents=True)
    license_file = tmp_path / "licenses/example-MIT.txt"
    license_file.parent.mkdir()
    license_file.write_text("MIT license notice")
    destination = tmp_path / "skills/example/SKILL.md"
    destination.parent.mkdir()
    destination.write_text("Workflow.")
    source = {"id": "example", "repository": "https://github.com/example/skills",
              "revision": "a" * 40, "license": "MIT", "license_file": "licenses/example-MIT.txt",
              "adaptations": [{"source_paths": ["skills/original/SKILL.md"],
                               "destinations": ["skills/example/SKILL.md"],
                               "mechanism": "Adapted diagnostic procedure.",
                               "departures": "Uses consumer commands."}]}
    data = {"schema_version": 1, "kind": "source-lineage", "runtime_dependencies": [], "sources": [source]}
    path.write_text(json.dumps(data))
    assert not validate_source_lineage(tmp_path)
    source["revision"] = "main"
    path.write_text(json.dumps(data))
    assert any("full lowercase Git SHA-1" in error for error in validate_source_lineage(tmp_path))
    source["revision"] = "a" * 40
    destination.unlink()
    license_file.unlink()
    path.write_text(json.dumps(data))
    errors = validate_source_lineage(tmp_path)
    assert any("license file" in error for error in errors)
    assert any("adaptation destination" in error for error in errors)
    data["runtime_dependencies"] = ["example/skills"]
    path.write_text(json.dumps(data))
    assert any("no runtime dependencies" in error for error in validate_source_lineage(tmp_path))
