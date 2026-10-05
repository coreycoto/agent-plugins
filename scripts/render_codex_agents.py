#!/usr/bin/env python3
"""Render pinned project role overlays for reviewed, committed CI/cloud configuration."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from pathlib import Path

from jsonschema import ValidationError, validate

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "adapters/codex_agents"))

from manager import digest, encode, plugin_manifest, read, role_assets, safe_path  # noqa: E402

RECEIPT = ".agent-plugin-projection.json"


def projection(project: dict) -> dict[str, bytes]:
    schema = json.loads((REPOSITORY / "schemas/codex-agent-projection.schema.json").read_bytes())
    validate(project, schema)
    plugin = REPOSITORY / "plugins" / project["plugin"]
    manifest = plugin_manifest(plugin)
    owner = manifest["repository"].removeprefix("https://github.com/") + ":" + manifest["name"]
    _, assets, _ = role_assets(plugin)
    files = {}
    for name, overlay in sorted(project["roles"].items()):
        source_name = overlay["sourceRole"]
        source = assets.get(source_name + ".toml")
        if source is None:
            raise ValueError("The overlay references a role absent from the pinned catalog.")
        role = tomllib.loads(source.decode())
        role["name"] = name
        if "description" in overlay:
            role["description"] = overlay["description"]
        if "default_permissions" in overlay:
            if role["sandbox_mode"] == "read-only" and overlay["default_permissions"] not in project.get("readOnlyProfiles", []):
                raise ValueError("Declare the consumer's read-only profile before assigning it to a read-only role.")
            role.pop("sandbox_mode")
            role["default_permissions"] = overlay["default_permissions"]
        elif "sandbox_mode" in overlay:
            role["sandbox_mode"] = overlay["sandbox_mode"]
        if "appendInstructions" in overlay:
            role["developer_instructions"] += "\nProject instructions:\n" + overlay["appendInstructions"]
        header = (
            f"# Generated from {owner}; do not edit.\n"
            f"# Source revision: {project['sourceRevision']}; source role: {source_name}.\n"
        )
        # TOML basic strings support these JSON string escapes, including newlines.
        # Encoding strings avoids delimiter injection from project instructions.
        filename = overlay.get("file", name + ".toml")
        if filename in files:
            raise ValueError("Two role aliases cannot share an output file.")
        files[filename] = (header + "".join(
            f"{key} = {json.dumps(value, ensure_ascii=False)}\n" for key, value in role.items()
        )).encode()
    files[RECEIPT] = encode({
        "schemaVersion": 1, "source": owner,
        "sourceRevision": project["sourceRevision"], "overlayDigest": digest(encode(project)),
        "files": {name: digest(data) for name, data in files.items()},
    })
    return files


def source_revision(project: dict) -> None:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPOSITORY,
                          capture_output=True, text=True, check=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain"], cwd=REPOSITORY,
                            capture_output=True, text=True, check=True).stdout
    if status or head != project["sourceRevision"]:
        raise ValueError("Render from the clean publisher checkout at the overlay's exact sourceRevision.")


def matches(destination: Path, files: dict[str, bytes]) -> bool:
    safe_path(destination)
    return all((destination / name).is_file() and read(destination / name) == data
               for name, data in files.items())


def write_new(destination: Path, files: dict[str, bytes]) -> None:
    safe_path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Render into an empty directory, then review the diff before replacing committed projections.")
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        with (destination / name).open("xb") as stream:
            stream.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        project = json.loads(read(args.project))
        files = projection(project)
        source_revision(project)
        if args.check:
            valid = matches(args.output, files)
            print("Pinned role projections match." if valid else "Role projections differ; review regeneration.")
            return int(not valid)
        write_new(args.output, files)
        print(f"Rendered {len(project['roles'])} roles from {project['sourceRevision']}.")
        return 0
    except ValidationError:
        print("The project overlay does not match the declared schema.", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
