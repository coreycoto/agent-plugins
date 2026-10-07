#!/usr/bin/env python3
"""Build self-contained portable/Codex plugins and npm archives outside authored source."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import tarfile
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
REGISTRY = "https://npm.pkg.github.com"


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode()


def regular(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Build input must be a regular file: {path}.")
    return path.read_bytes()


def runtime_projection(repository: Path = REPOSITORY) -> dict[str, bytes]:
    return {name: regular(repository / "adapters/codex_agents" / name)
            for name in ("manager.py", "server.py", "hook.py")}


def source_files(source: Path) -> dict[str, bytes]:
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Authored plugin roots must be directories without symlinks.")
    files = {}
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Build input must not be a symlink: {path}.")
        if relative.parts[:2] in {("com.openai", "codex-package"), ("com.openai", "codex_agents")}:
            if path.is_file():
                raise ValueError("Remove generated distributions and runtime copies from plugin source.")
            continue
        if path.is_file():
            files[relative.as_posix()] = regular(path)
    return files


def distribution_settings(repository: Path) -> dict:
    settings = json.loads(regular(repository / ".agents/plugins/distribution.json"))
    if (settings.get("schemaVersion") != 1
            or settings.get("visibility") not in {"public", "private"}
            or settings.get("access") != ("public" if settings["visibility"] == "public" else "restricted")
            or settings.get("registry") != REGISTRY):
        raise ValueError("Use GitHub Packages and matching public/private package access.")
    return settings


def package_metadata(source: Path, repository: Path = REPOSITORY) -> dict:
    manifest = json.loads(regular(source / "plugin.json"))
    catalog = json.loads(regular(repository / ".agents/plugins/marketplace.json"))
    entries = [entry for entry in catalog["plugins"] if entry["name"] == source.name]
    if len(entries) != 1 or manifest["name"] != source.name:
        raise ValueError("Each authored plugin requires exactly one matching marketplace entry.")
    settings = distribution_settings(repository)
    entry = entries[0]["source"]
    owner = manifest["repository"].removeprefix("https://github.com/").split("/")[0]
    expected = {"source": "npm", "package": f"@{owner}/agent-plugin-{source.name}",
                "version": manifest["version"], "registry": settings["registry"]}
    if entry != expected or re.fullmatch(r"[a-z0-9-]+", owner) is None:
        raise ValueError("Marketplace sources must declare their own exact npm package and version.")
    return {
        "name": entry["package"], "version": manifest["version"],
        "description": manifest["description"], "license": manifest["license"],
        "repository": {"type": "git", "url": manifest["repository"] + ".git"},
        "publishConfig": {"registry": settings["registry"], "access": settings["access"]},
        "files": ["plugin.json", "mcp.json", ".codex-plugin", ".mcp.json", "skills",
                  "com.openai", "assets", "licenses", "skills-lock.json",
                  "THIRD_PARTY_NOTICES.md", "README.md", "LICENSE", "GENERATED.md"],
    }


def projection(source: Path, format: str = "codex", repository: Path = REPOSITORY) -> dict[str, bytes]:
    if format not in {"codex", "portable"}:
        raise ValueError("Use the portable or codex package format.")
    files = source_files(source)
    manifest = json.loads(files["plugin.json"])
    extension = manifest.get("extensions", {}).get("com.openai", {})
    if (source / "com.openai/agents/catalog.json").is_file():
        files.update({"com.openai/codex_agents/" + name: data
                      for name, data in runtime_projection(repository).items()})
    if format == "codex":
        compatibility = {key: manifest[key] for key in (
            "name", "version", "description", "author", "homepage", "repository", "license", "keywords")
            if key in manifest}
        compatibility.update(skills="./skills", extensions={"com.openai": {
            key: extension[key] for key in ("onboardingSkill",) if key in extension}})
        compatibility.update({key: extension[key] for key in ("hooks", "interface") if key in extension})
        if "mcp.json" in files:
            portable_mcp = json.loads(files.pop("mcp.json"))
            mcp = {"mcpServers": {name: {
                **{key: value for key, value in server.items() if key not in {"type", "args"}},
                "args": [arg.replace("${PLUGIN_ROOT}/", "./") for arg in server.get("args", [])],
                "cwd": ".", "env_vars": ["CODEX_HOME"],
            } for name, server in portable_mcp["mcpServers"].items()}}
            files[".mcp.json"] = encoded(mcp)
            compatibility["mcpServers"] = "./.mcp.json"
        files.pop("plugin.json")  # 0.160 must select its compatibility hook loader.
        files[".codex-plugin/plugin.json"] = encoded(compatibility)
    files["package.json"] = encoded(package_metadata(source, repository))
    files["LICENSE"] = regular(repository / "LICENSE")
    files["GENERATED.md"] = (
        f"Built from plugins/{manifest['name']} and the pinned shared adapter source.\n"
        "Edit authored source, never this generated distribution.\n"
        "Codex CLI 0.160 compatibility is confined to the built Codex artifact.\n"
    ).encode()
    return files


def check(source: Path, destination: Path, format: str = "codex", repository: Path = REPOSITORY) -> bool:
    return tree_matches(destination, projection(source, format, repository))


def tree_matches(destination: Path, desired: dict[str, bytes]) -> bool:
    if destination.is_symlink() or not destination.is_dir():
        return False
    paths = list(destination.rglob("*"))
    if any(path.is_symlink() for path in paths):
        return False
    actual = {path.relative_to(destination).as_posix(): path.read_bytes()
              for path in paths if path.is_file() and "__pycache__" not in path.parts}
    return actual == desired


def write_generated(destination: Path, desired: dict[str, bytes]) -> None:
    if destination.is_symlink():
        raise ValueError("Refusing a symlinked output directory.")
    for parent in destination.parents:
        if parent.is_symlink():
            raise ValueError("Refusing a symlinked output ancestor.")
    for path in destination.rglob("*") if destination.exists() else []:
        if path.is_symlink():
            raise ValueError("Refusing symlinked generated output.")
        if path.is_file() and "__pycache__" not in path.parts and path.relative_to(destination).as_posix() not in desired:
            raise ValueError("Unexpected generated file; use a fresh output directory.")
    for name, data in desired.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def archive(files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo("package/" + name)
                member.size, member.mode, member.mtime = len(data), 0o644, 0
                tar.addfile(member, io.BytesIO(data))
    return output.getvalue()


def marketplace_projection(repository: Path, format: str = "codex", plugin: str | None = None) -> dict[str, bytes]:
    catalog = json.loads(regular(repository / ".agents/plugins/marketplace.json"))
    entries = catalog["plugins"]
    names = {path.parent.name for path in (repository / "plugins").glob("*/plugin.json")}
    if {entry["name"] for entry in entries} != names or len(entries) != len(names):
        raise ValueError("Authored plugins and independently selectable catalog entries must match.")
    if plugin is not None:
        if plugin not in names:
            raise ValueError("Unknown authored plugin.")
        entries = [entry for entry in entries if entry["name"] == plugin]
    files = {}
    local_entries = []
    for entry in entries:
        name = entry["name"]
        package = projection(repository / "plugins" / name, format, repository)
        files.update({f"plugins/{name}/{path}": data for path, data in package.items()})
        local_entries.append({**entry, "source": {"source": "local", "path": f"./plugins/{name}"}})
    files[".agents/plugins/marketplace.json"] = encoded({**catalog, "plugins": local_entries})
    for name in ("publisher.json", "public-source.json"):
        path = repository / ".agents/plugins" / name
        if path.exists():
            files[f".agents/plugins/{name}"] = regular(path)
    return files


def distribution_projection(repository: Path = REPOSITORY, plugin: str | None = None) -> dict[str, bytes]:
    files = {}
    for format in ("portable", "codex"):
        files.update({format + "/" + name: data
                      for name, data in marketplace_projection(repository, format, plugin).items()})
    catalog = json.loads(files["codex/.agents/plugins/marketplace.json"])
    for entry in catalog["plugins"]:
        name = entry["name"]
        package = projection(repository / "plugins" / name, repository=repository)
        metadata = json.loads(package["package.json"])
        archive_name = metadata["name"].removeprefix("@").replace("/", "-") + "-" + metadata["version"] + ".tgz"
        files["npm/" + archive_name] = archive(package)
    files["SHA256SUMS"] = "".join(
        hashlib.sha256(data).hexdigest() + "  " + name + "\n"
        for name, data in sorted(files.items()) if name.startswith("npm/")).encode()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plugin", help="Build or check one independently selectable plugin.")
    parser.add_argument("--output", type=Path, default=REPOSITORY / "dist/plugin-packages")
    args = parser.parse_args()
    try:
        destination = Path(os.path.abspath(args.output))
        # The only permitted in-checkout output is inside the ignored dist tree.
        if destination.is_relative_to(REPOSITORY) and not destination.is_relative_to(REPOSITORY / "dist"):
            raise ValueError("Build into the ignored dist directory or an external temporary directory.")
        desired = distribution_projection(plugin=args.plugin)
        if args.check:
            if not tree_matches(destination, desired):
                raise ValueError("Built distributions differ from authored inputs; rebuild in a fresh directory.")
        else:
            write_generated(destination, desired)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Plugin distribution failed: {error}\n")
    print(f"{'Verified' if args.check else 'Built'} portable/Codex packages and npm archives: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
