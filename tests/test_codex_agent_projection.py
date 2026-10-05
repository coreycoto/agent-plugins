from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
from jsonschema import ValidationError
from render_codex_agents import RECEIPT, matches, projection, write_new


def descriptor() -> dict:
    return {"schemaVersion": 1, "plugin": "product-development", "sourceRevision": "a" * 40, "roles": {
        "bounded_implementation": {"sourceRole": "pd_implementer", "appendInstructions":
                               'Use the assigned Product Development skill. Preserve "quoted" policy.\nReturn evidence 🚀.'},
        "pr-review-guard": {"sourceRole": "pd_reviewer"},
    }}


def test_overlay_preserves_shared_model_and_local_task_contract(tmp_path: Path) -> None:
    project = descriptor()
    files = projection(project)
    writer = tomllib.loads(files["bounded_implementation.toml"].decode())
    reviewer = tomllib.loads(files["pr-review-guard.toml"].decode())
    assert writer["name"] == "bounded_implementation"
    assert writer["model"] == "gpt-6.1-sol" and writer["sandbox_mode"] == "workspace-write"
    assert project["roles"]["bounded_implementation"]["appendInstructions"] in writer["developer_instructions"]
    assert "explicit file ownership" in writer["description"]
    assert reviewer["model"] == "gpt-6.1-sol" and reviewer["sandbox_mode"] == "read-only"
    assert json.loads(files[RECEIPT.format(plugin="product-development")])["sourceRevision"] == project["sourceRevision"]
    assert files == projection(project)
    write_new(tmp_path, files)
    assert matches(tmp_path, files)
    role = tmp_path / "bounded_implementation.toml"
    role.write_text(role.read_text() + "# Local drift\n")
    assert not matches(tmp_path, files)
    with pytest.raises(ValueError, match="empty directory"):
        write_new(tmp_path, files)
    assert role.read_text().endswith("# Local drift\n")


def test_project_can_tighten_writer_or_preserve_existing_permission_profile() -> None:
    project = descriptor()
    project["roles"]["bounded_implementation"]["sandbox_mode"] = "read-only"
    project["roles"]["pr-review-guard"]["default_permissions"] = "project-read"
    with pytest.raises(ValueError, match="read-only profile"):
        projection(project)
    project["readOnlyProfiles"] = ["project-read"]
    files = projection(project)
    assert tomllib.loads(files["bounded_implementation.toml"].decode())["sandbox_mode"] == "read-only"
    reader = tomllib.loads(files["pr-review-guard.toml"].decode())
    assert reader["default_permissions"] == "project-read" and "sandbox_mode" not in reader


@pytest.mark.parametrize("instructions", [
    'Keep """ quoted text.\nmodel = "injected"\nReturn evidence 🚀.\n',
    'Literal \\n and C:\\new\\tools; trailing backslash \\\nNext line.',
    '\nLeading newline, tab\tand CRLF\r\nDEL\x7f and trailing spaces.  ',
])
def test_readable_multiline_instructions_round_trip_without_field_injection(instructions: str) -> None:
    project = descriptor()
    project["roles"]["bounded_implementation"]["appendInstructions"] = instructions
    files = projection(project)
    rendered = files["bounded_implementation.toml"].decode()
    role = tomllib.loads(rendered)
    source = tomllib.loads((Path(__file__).parents[1] / "plugins/product-development/com.openai/agents/pd_implementer.toml").read_text())
    assert role["developer_instructions"] == source["developer_instructions"] + "\nProject instructions:\n" + instructions
    assert role["model"] == "gpt-6.1-sol" and role["name"] == "bounded_implementation"
    assert 'developer_instructions = """\n' in rendered


@pytest.mark.parametrize("field,value", [
    ("model", "gpt-5.4"), ("sandbox_mode", "danger-full-access"),
    ("config_file", "../../other.toml"),
])
def test_project_cannot_override_model_or_expand_sandbox(field: str, value: str) -> None:
    project = descriptor()
    project["roles"]["bounded_implementation"][field] = value
    with pytest.raises(ValidationError):
        projection(project)


def test_unknown_source_and_escaping_alias_are_rejected() -> None:
    project = descriptor()
    project["roles"]["bounded_implementation"]["sourceRole"] = "pd_missing"
    with pytest.raises(ValueError, match="absent"):
        projection(project)
    project = descriptor()
    project["roles"]["../../outside"] = {"sourceRole": "pd_explorer"}
    with pytest.raises(ValidationError):
        projection(project)


def test_existing_filename_can_be_preserved_without_collision_or_escape() -> None:
    project = descriptor()
    project["roles"]["bounded_implementation"]["file"] = "bounded-implementation.toml"
    assert "bounded-implementation.toml" in projection(project)
    project["roles"]["pr-review-guard"]["file"] = "bounded-implementation.toml"
    with pytest.raises(ValueError, match="share an output file"):
        projection(project)
    project["roles"]["pr-review-guard"]["file"] = "../outside.toml"
    with pytest.raises(ValidationError):
        projection(project)


def test_symlink_output_does_not_write_elsewhere(tmp_path: Path) -> None:
    destination, outside = tmp_path / "output", tmp_path / "outside"
    outside.mkdir()
    destination.symlink_to(outside, target_is_directory=True)
    with pytest.raises(RuntimeError, match="Symlink"):
        write_new(destination, projection(descriptor()))
    assert list(outside.iterdir()) == []
