from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

import pytest
from build_codex_package import (
    REPOSITORY,
    distribution_projection,
    distribution_settings,
    projection,
    source_files,
    tree_matches,
    write_generated,
)


def test_builds_are_reproducible_without_changing_authored_plugins(tmp_path: Path) -> None:
    before = {root.name: source_files(root) for root in (REPOSITORY / "plugins").iterdir()}
    first, second = tmp_path / "first", tmp_path / "second"
    files = distribution_projection()
    write_generated(first, files)
    write_generated(second, distribution_projection())
    assert tree_matches(first, files) and tree_matches(second, files)
    assert before == {root.name: source_files(root) for root in (REPOSITORY / "plugins").iterdir()}
    assert not any("codex-package/" in name for name in files)
    catalog = json.loads(files["codex/.agents/plugins/marketplace.json"])
    assert {entry["name"] for entry in catalog["plugins"]} == set(before)
    assert all(entry["source"] == {"source": "local", "path": "./plugins/" + entry["name"]}
               for entry in catalog["plugins"])
    # A changed or extra archive cannot pass candidate verification.
    archive = next(first.glob("npm/*.tgz"))
    archive.write_bytes(archive.read_bytes() + b"tampered")
    assert not tree_matches(first, files)


def test_archive_contains_complete_native_package_and_independent_owned_roles() -> None:
    files = distribution_projection()
    for name in ("product-development", "project-management"):
        payload = files[f"npm/coreycoto-agent-plugin-{name}-0.8.1.tgz"]
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            members = archive.getmembers()
            assert all(member.isfile() and member.name.startswith("package/") for member in members)
            assert not any(member.name == "package/plugin.json" for member in members)
            assert "package/.codex-plugin/plugin.json" in archive.getnames()
            assert "package/.mcp.json" in archive.getnames()
            catalog = json.load(archive.extractfile("package/com.openai/agents/catalog.json"))
            names = {role["file"] for role in catalog["roles"]}
            bundled = {member.name.removeprefix("package/com.openai/agents/") for member in members
                       if member.name.startswith("package/com.openai/agents/") and member.name.endswith(".toml")}
            assert names == bundled
            for role in catalog["roles"]:
                assert archive.extractfile("package/com.openai/agents/" + role["file"]).read() == (
                    REPOSITORY / "plugins" / name / "com.openai/agents" / role["file"]).read_bytes()
            for module in ("manager.py", "hook.py", "server.py"):
                assert archive.extractfile("package/com.openai/codex_agents/" + module).read() == (
                    REPOSITORY / "adapters/codex_agents" / module).read_bytes()


@pytest.mark.parametrize("plugin", ["communication", "product-development", "product-management", "project-management"])
def test_real_npm_pack_preserves_hidden_manifests_and_all_bundle_files(tmp_path: Path, plugin: str) -> None:
    package = tmp_path / "plugin"
    files = projection(REPOSITORY / "plugins" / plugin)
    write_generated(package, files)
    output = tmp_path / "packed"
    output.mkdir()
    result = subprocess.run(["npm", "pack", "--ignore-scripts", "--json", "--pack-destination", str(output), str(package)],
                            env={**os.environ, "npm_config_cache": str(tmp_path / "npm-cache")},
                            capture_output=True, text=True, check=True)
    metadata = json.loads(result.stdout)[0]
    assert metadata["name"] == f"@coreycoto/agent-plugin-{plugin}"
    with tarfile.open(output / metadata["filename"], "r:gz") as archive:
        assert set(archive.getnames()) == {"package/" + name for name in files}
        for name, expected in files.items():
            assert archive.extractfile("package/" + name).read() == expected


def test_generated_output_rejects_symlinks_and_unrelated_files(tmp_path: Path) -> None:
    target = tmp_path / "unrelated"
    target.mkdir()
    unrelated = target / "keep.txt"
    unrelated.write_text("preserve")
    with pytest.raises(ValueError, match="Unexpected generated file"):
        write_generated(target, {"package.json": b"{}"})
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinked"):
        write_generated(link, {"package.json": b"{}"})
    assert unrelated.read_text() == "preserve"
    assert not (target / "package.json").exists()


def test_source_symlinks_and_returned_generated_files_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    root_link = tmp_path / "root-link"
    root_link.symlink_to(source, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        source_files(root_link)
    outside = tmp_path / "outside"
    outside.write_text("not a build input")
    (source / "link").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        source_files(source)
    (source / "link").unlink()
    runtime = source / "com.openai/codex_agents"
    runtime.mkdir(parents=True)
    (runtime / "manager.py").write_text("duplicate")
    with pytest.raises(ValueError, match="Remove generated"):
        source_files(source)


def test_private_distribution_cannot_target_public_registry(tmp_path: Path) -> None:
    config = tmp_path / ".agents/plugins/distribution.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"schemaVersion": 1, "visibility": "private",
                                  "access": "restricted", "registry": "https://registry.npmjs.org"}))
    with pytest.raises(ValueError, match="Private plugins"):
        distribution_settings(tmp_path)


@pytest.mark.parametrize("output", ["plugins/product-development", "dist/../plugins/product-development"])
def test_cli_cannot_write_distributions_into_authored_source(output: str) -> None:
    result = subprocess.run(["python3", str(REPOSITORY / "scripts/build_codex_package.py"),
                             "--output", str(REPOSITORY / output)],
                            capture_output=True, text=True)
    assert result.returncode == 1 and "ignored dist directory" in result.stderr
