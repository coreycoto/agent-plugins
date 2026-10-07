#!/usr/bin/env python3
"""Compare explicitly supplied skill packages and discovery directories without client mutations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

import yaml

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SHA256 = re.compile(r"[0-9a-f]{64}")
SKIP_DIRS = {"node_modules", "__pycache__"}
SECRET_NAMES = {"auth.json", "credentials.json", "secrets.json"}


class InspectionError(ValueError):
    """An input could not be inspected safely; messages never include input contents."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise InspectionError(f"Expected a regular file: {path}")
    try:
        return path.read_bytes()
    except OSError:
        raise InspectionError(f"Could not read: {path}") from None


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def decode_json(data: bytes, path: Path) -> object:
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError):
        raise InspectionError(f"Invalid JSON: {path}") from None


def read_json(path: Path) -> object:
    return decode_json(read(path), path)


def directory(path: Path) -> Path:
    # A supplied root may itself be a link. Descendant links are never followed.
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        raise InspectionError(f"Missing directory: {path}") from None
    if not resolved.is_dir():
        raise InspectionError(f"Expected a directory: {path}")
    return resolved


def files(root: Path, *, reject_links: bool = False) -> list[Path]:
    result: list[Path] = []

    def failed(error: OSError) -> None:
        raise InspectionError(f"Could not inventory directory: {error.filename}")

    for current, directories, names in os.walk(root, followlinks=False, onerror=failed):
        base = Path(current)
        if reject_links and any((base / name).is_symlink() for name in directories + names):
            raise InspectionError(f"Descendant links prevent exact workflow inspection: {base}")
        directories[:] = sorted(name for name in directories
                                if not name.startswith(".") and name not in SKIP_DIRS
                                and not (base / name).is_symlink())
        result.extend(base / name for name in sorted(names)
                      if not name.startswith(".") and name not in SECRET_NAMES
                      and Path(name).suffix not in {".pyc", ".pem", ".key"})
    return sorted(result)


def skill(path: Path, plugin: str | None = None, data: bytes | None = None) -> dict:
    data = read(path) if data is None else data
    try:
        text = data.decode("utf-8").replace("\r\n", "\n")
        if not text.startswith("---\n"):
            raise ValueError
        header, body = text[4:].split("\n---\n", 1)
        metadata = yaml.safe_load(header)
        name = metadata.get("name") if isinstance(metadata, dict) else None
        if not isinstance(name, str) or len(name) > 64 or NAME.fullmatch(name) is None:
            raise ValueError
    except (ValueError, UnicodeError, yaml.YAMLError):
        raise InspectionError(f"Invalid skill identity/frontmatter: {path}") from None
    return {"name": name, "qualified_name": f"{plugin}:{name}" if plugin else None,
            "path": str(path), "file_sha256": digest(data),
            "body_sha256": digest(body.strip().encode()), "plugin": plugin}


def public_repository(value: object) -> str | None:
    if isinstance(value, dict):
        value = value.get("url")
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
    except ValueError:
        return None
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment:
        return None
    return value


def package(path: Path) -> dict:
    root = directory(path)
    candidates = [root / "plugin.json", root / ".codex-plugin/plugin.json"]
    manifests = [candidate for candidate in candidates if candidate.exists() or candidate.is_symlink()]
    if not manifests:
        raise InspectionError(f"No portable or Codex plugin manifest: {root}")
    identities = []
    for manifest in manifests:
        data = read_json(manifest)
        if not isinstance(data, dict):
            raise InspectionError(f"Invalid plugin identity: {manifest}")
        name, version = data.get("name"), data.get("version")
        if (not isinstance(name, str) or len(name) > 64 or NAME.fullmatch(name) is None
                or not isinstance(version, str) or re.fullmatch(r"[0-9A-Za-z.+-]{1,64}", version) is None):
            raise InspectionError(f"Invalid plugin identity: {manifest}")
        identities.append({"name": name, "version": version,
                           "repository": public_repository(data.get("repository"))})
    if any(identity != identities[0] for identity in identities):
        raise InspectionError(f"Conflicting portable/Codex plugin identities: {root}")
    identity = identities[0]
    skill_root = root / "skills"
    if skill_root.is_symlink() or not skill_root.is_dir():
        raise InspectionError(f"Missing or symlinked skills directory: {root}")
    workflow_files = files(skill_root, reject_links=True)
    snapshot = {file: read(file) for file in workflow_files}
    inventory = [skill(file, identity["name"], snapshot[file]) for file in workflow_files
                 if file.name == "SKILL.md" and len(file.relative_to(skill_root).parts) == 2]
    if not inventory:
        raise InspectionError(f"No immediate skill entrypoints: {root}")
    contents = {file.relative_to(skill_root).as_posix(): digest(data) for file, data in snapshot.items()}
    fingerprint = digest(json.dumps(contents, sort_keys=True, separators=(",", ":")).encode())
    return {"root": str(root), "identity": identity,
            "source": {"declared_repository": identity["repository"],
                       "acquisition_origin": "not observed; explicit directory input"},
            "workflow_fingerprint": fingerprint, "workflow_files": contents, "skills": inventory}


def discovery(path: Path) -> dict:
    root = directory(path)
    paths = [file for file in files(root) if file.name == "SKILL.md"]
    return {"root": str(root), "skills": [skill(file) for file in paths]}


def duplicates(entries: list[dict], field: str) -> list[dict]:
    groups: dict[str, dict[str, dict]] = defaultdict(dict)
    for entry in entries:
        groups[entry[field]].setdefault(entry["path"], entry)
    return [{"value": key, "members": [{field: entry[field] for field in
             ("name", "qualified_name", "path", "file_sha256", "body_sha256")}
             for entry in sorted(group.values(), key=lambda item: item["path"])]}
            for key, group in sorted(groups.items()) if len(group) > 1]


def comparison(candidate: dict, installed: dict) -> dict:
    expected, actual = candidate["workflow_files"], installed["workflow_files"]
    return {"root": installed["root"], "identity_matches": candidate["identity"] == installed["identity"],
            "workflow_content_matches": candidate["workflow_fingerprint"] == installed["workflow_fingerprint"],
            "missing_files": sorted(expected.keys() - actual.keys()),
            "extra_files": sorted(actual.keys() - expected.keys()),
            "changed_files": sorted(name for name in expected.keys() & actual.keys()
                                    if expected[name] != actual[name])}


def observations(path: Path | None, session_id: str | None, candidate: dict) -> dict:
    result = {"status": "unverified", "session_id": session_id,
              "matching_observations": [], "unmatched_observations": [],
              "reload_verified": False, "automatic_selection_verified": False,
              "limitation": "Disk and CLI inventory do not establish active-session discovery or reload. "
                            "Supplied session observations are reported, not independently authenticated."}
    if path is None:
        return result
    data = read_json(path)
    if (not isinstance(data, dict) or data.get("kind") != "active-session-skill-read"
            or data.get("session_id") != session_id or not isinstance(data.get("skills"), list)):
        raise InspectionError(f"Session observations require matching session ID and active-session-skill-read kind: {path}")
    expected = {item["qualified_name"]: item["file_sha256"] for item in candidate["skills"]}
    seen = set()
    for item in data["skills"]:
        if (not isinstance(item, dict) or not isinstance(item.get("qualified_name"), str)
                or re.fullmatch(r"[a-z0-9-]+:[a-z0-9-]+", item["qualified_name"]) is None
                or not isinstance(item.get("file_sha256"), str) or SHA256.fullmatch(item["file_sha256"]) is None
                or item["qualified_name"] in seen):
            raise InspectionError(f"Invalid or duplicate session skill observation: {path}")
        seen.add(item["qualified_name"])
        target = "matching_observations" if expected.get(item["qualified_name"]) == item["file_sha256"] else "unmatched_observations"
        result[target].append({"qualified_name": item["qualified_name"], "file_sha256": item["file_sha256"]})
    if result["matching_observations"]:
        result["status"] = "supplied exact-file observations; coverage limited to listed skills"
    return result


def inspect(candidate_path: Path, installed_paths: list[Path], discovery_paths: list[Path],
            native_inventory: Path | None = None, session_observations: Path | None = None,
            session_id: str | None = None) -> dict:
    candidate = package(candidate_path)
    installed = [package(path) for path in installed_paths]
    roots = [discovery(path) for path in discovery_paths]
    # Candidate is a comparison target, not another installed discovery location.
    entries = [item for found in installed + roots for item in found["skills"]]
    native = None
    if native_inventory is not None:
        data = read(native_inventory)
        decode_json(data, native_inventory)
        native = {"path": str(native_inventory), "sha256": digest(data),
                  "interpretation": "Supplied native inventory provenance only; no schema, installed-state, "
                                    "enablement or active-session claims inferred."}
    return {"schema_version": 1, "candidate": candidate, "installed_packages": installed,
            "discovery_roots": roots,
            "comparisons": [comparison(candidate, item) for item in installed],
            "duplicates": {"names": duplicates(entries, "name"),
                           "equivalent_bodies": duplicates(entries, "body_sha256")},
            "native_inventory": native,
            "active_session": observations(session_observations, session_id, candidate),
            "fingerprint_scope": "All non-hidden regular files under skills, excluding cache directories, "
                                 "credential filenames and .pyc/.pem/.key files. Descendant links are not followed. "
                                 "Plugin identity/version are compared separately; roles, hooks and runtime are not compared.",
            "body_equivalence": "Literal UTF-8 body after frontmatter, with CRLF normalized and outer whitespace stripped; "
                                "not semantic equivalence. File hashes retain exact bytes.",
            "coverage": "Only explicitly supplied locations; no automatic home/config/cache discovery.",
            "mutations_performed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True, help="Built portable/Codex package directory")
    parser.add_argument("--installed", type=Path, action="append", default=[], help="Explicit installed/cache package directory (repeatable)")
    parser.add_argument("--discovery-root", type=Path, action="append", default=[], help="Explicit directory containing skills (repeatable)")
    parser.add_argument("--native-inventory", type=Path, help="Existing codex plugin list --json result; provenance only")
    parser.add_argument("--session-observations", type=Path, help="Supplied active-session skill-read observations")
    parser.add_argument("--session-id", help="Expected session identifier for supplied observations")
    args = parser.parse_args()
    if args.session_observations is not None and not args.session_id:
        parser.error("--session-observations requires --session-id")
    try:
        report = inspect(args.candidate, args.installed, args.discovery_root, args.native_inventory,
                         args.session_observations, args.session_id)
    except InspectionError as error:
        print(json.dumps({"error": str(error), "mutations_performed": False}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
