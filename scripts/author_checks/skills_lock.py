"""Read pinned GitHub entries from Vercel's native project skills-lock.json."""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

SKILLS_LOCK_FILENAME = "skills-lock.json"
_ENTRY_FIELDS = {
    "source", "sourceUrl", "ref", "sourceType", "skillPath", "computedHash",
    "subagents", "wellKnownDigest",
}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_github_skill_lock(path: Path) -> dict[str, dict[str, Any]]:
    """Apply publisher pin/path policy without adding fields to the native format."""
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or unsafe native skill lock: {path}")
    try:
        lock = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read {path}: {error}") from error
    if (
        not isinstance(lock, dict)
        or set(lock) != {"version", "skills"}
        or type(lock.get("version")) is not int
        or lock["version"] != 1
        or not isinstance(lock.get("skills"), dict)
        or not lock["skills"]
    ):
        raise ValueError(f"{path} must use native version-1 skills-lock.json with skills")

    sources: dict[str, str] = {}
    for name, entry in lock["skills"].items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"invalid locked skill name: {name!r}")
        if not isinstance(entry, dict) or set(entry) - _ENTRY_FIELDS:
            raise ValueError(f"{name}: unsupported native skill lock fields")
        source = entry.get("source")
        if (
            entry.get("sourceType") != "github"
            or not isinstance(source, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", source)
        ):
            raise ValueError(f"{name}: publisher snapshots require a GitHub owner/repo source")
        ref = entry.get("ref")
        if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
            raise ValueError(f"{name}: ref must be a full lowercase Git SHA-1")
        if source in sources and sources[source] != ref:
            raise ValueError(f"{source}: package source entries must share one exact ref")
        sources[source] = ref
        skill_path = entry.get("skillPath")
        if (
            not isinstance(skill_path, str)
            or "\\" in skill_path
            or "\x00" in skill_path
            or PurePosixPath(skill_path).is_absolute()
            or any(part in {"", ".", ".."} for part in skill_path.split("/"))
            or PurePosixPath(skill_path).name != "SKILL.md"
        ):
            raise ValueError(f"{name}: skillPath must be a safe relative SKILL.md path")
        digest = entry.get("computedHash")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"{name}: computedHash must be a lowercase SHA-256")
        for field in {"sourceUrl", "wellKnownDigest"} & entry.keys():
            if not isinstance(entry[field], str):
                raise ValueError(f"{name}: {field} must be a string")
        if "sourceUrl" in entry and entry["sourceUrl"] not in {
            f"https://github.com/{source}", f"https://github.com/{source}.git",
        }:
            raise ValueError(f"{name}: sourceUrl must match its GitHub source")
        if "subagents" in entry and (
            not isinstance(entry["subagents"], list)
            or any(not isinstance(value, str) for value in entry["subagents"])
        ):
            raise ValueError(f"{name}: subagents must be an array of strings")
    return lock["skills"]


def license_snapshot_path(source: str) -> Path:
    return Path("licenses") / f"{source.replace('/', '-')}-MIT.txt"


def native_skill_hash(files: Mapping[str, bytes]) -> str:
    """Use Vercel's path/content hash, including Node's localeCompare ordering.

    Contract: vercel-labs/skills 1.7.0, src/local-lock.ts. Node preserves the
    CLI's ordering semantics; Python's bytewise sort does not match them.
    """
    payload = [[name, base64.b64encode(content).decode("ascii")] for name, content in files.items()]
    command = (
        "const {readFileSync}=require('node:fs');"
        "const {createHash}=require('node:crypto');"
        "const files=JSON.parse(readFileSync(0,'utf8'));"
        "files.sort((a,b)=>a[0].localeCompare(b[0]));"
        "const hash=createHash('sha256');"
        "for(const [path,content] of files){hash.update(path);hash.update(Buffer.from(content,'base64'));}"
        "process.stdout.write(hash.digest('hex'));"
    )
    try:
        result = subprocess.run(
            ["node", "-e", command], input=json.dumps(payload),
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Node.js is required to verify native Vercel skill hashes") from error
    return result.stdout


def verify_installed_dependencies(
    lock_path: Path, installed_root: Path, consumer_lock_path: Path,
) -> list[str]:
    """Check restored files against the original publisher lock, not a rewritten hash."""
    try:
        expected = load_github_skill_lock(lock_path)
        consumer = json.loads(
            consumer_lock_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
        )
    except (ValueError, OSError, UnicodeDecodeError) as error:
        return [str(error)]
    if (
        not isinstance(consumer, dict)
        or type(consumer.get("version")) is not int
        or consumer["version"] != 1
        or not isinstance(consumer.get("skills"), dict)
    ):
        return [f"invalid native consumer skill lock: {consumer_lock_path}"]
    if installed_root.is_symlink() or not installed_root.is_dir():
        return [f"missing or unsafe consumer skill directory: {installed_root}"]

    errors: list[str] = []
    for name, entry in expected.items():
        actual_entry = consumer["skills"].get(name)
        if not isinstance(actual_entry, dict) or any(
            actual_entry.get(field) != entry[field]
            for field in ("source", "sourceType", "ref", "skillPath", "computedHash")
        ):
            errors.append(f"{name}: consumer lock differs from the declared dependency")
        directory = installed_root / name
        if directory.is_symlink() or not directory.is_dir():
            errors.append(f"{name}: missing or unsafe installed skill")
            continue
        files: dict[str, bytes] = {}
        unsafe = False
        for current, directories, filenames in os.walk(directory, followlinks=False):
            current_path = Path(current)
            for child in list(directories):
                path = current_path / child
                if child in {".git", "node_modules"}:
                    directories.remove(child)
                elif path.is_symlink():
                    errors.append(f"{name}: unsafe installed symlink: {path}")
                    unsafe = True
                    directories.remove(child)
            for child in filenames:
                path = current_path / child
                if path.is_symlink() or not path.is_file():
                    errors.append(f"{name}: unsafe installed file: {path}")
                    unsafe = True
                else:
                    try:
                        files[path.relative_to(directory).as_posix()] = path.read_bytes()
                    except OSError as error:
                        errors.append(f"{name}: could not read installed file: {error}")
                        unsafe = True
        if "SKILL.md" not in files:
            errors.append(f"{name}: missing installed SKILL.md")
        if not unsafe:
            try:
                if native_skill_hash(files) != entry["computedHash"]:
                    errors.append(f"{name}: installed content differs from native computedHash")
            except ValueError as error:
                errors.append(str(error))
    return errors
