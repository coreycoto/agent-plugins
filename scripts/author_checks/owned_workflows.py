"""Offline integrity checks for packaged workflow references and source lineage."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def _prose(text: str) -> str:
    """Remove fenced, indented and inline code before recognizing Markdown links."""
    lines: list[str] = []
    fence: str | None = None
    length = 0
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence, length = token[0], len(token)
            elif token[0] == fence and len(token) >= length and not line[marker.end():].strip():
                fence = None
            continue
        if fence is None and not line.startswith(("    ", "\t")):
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.DOTALL)


def _contained_file(root: Path, path: Path) -> bool:
    try:
        path.resolve(strict=True).relative_to(root.resolve())
        return path.is_file()
    except (OSError, ValueError):
        return False


def validate_markdown_references(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "skills").rglob("*.md")):
        if not _contained_file(root, path):
            continue  # Package containment validation reports unsafe source paths.
        try:
            prose = _prose(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as error:
            errors.append(f"{path}: could not read Markdown: {error}")
            continue
        # Match inline destinations and reference definitions, including <paths with spaces>.
        destinations = re.findall(r"\]\(\s*(<[^>]+>|(?:[^\s()]+|\([^()\s]*\))+)", prose)
        destinations += re.findall(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", prose, re.MULTILINE)
        for destination in destinations:
            target = destination.removeprefix("<").removesuffix(">")
            try:
                parsed = urlsplit(target)
            except ValueError:
                errors.append(f"{path}: invalid Markdown reference: {target}")
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            relative = Path(unquote(parsed.path))
            if relative.is_absolute() or not _contained_file(root, path.parent / relative):
                errors.append(f"{path}: missing or escaping local Markdown reference: {target}")
    return errors


def validate_source_lineage(root: Path) -> list[str]:
    path = root / "skills/_shared/references/upstream-lineage.json"
    if not path.exists() and not path.is_symlink():
        return []  # Legacy packages may still declare their provenance through dependency locks.
    if not _contained_file(root, path):
        return [f"{path}: source lineage must be a contained file"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        return [f"{path}: invalid source lineage: {error}"]
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1
            or data.get("kind") != "source-lineage" or data.get("runtime_dependencies") != []
            or not isinstance(data.get("sources"), list) or not data["sources"]):
        return [f"{path}: expected source-lineage version 1 with sources and no runtime dependencies"]
    errors: list[str] = []
    seen: set[str] = set()
    for source in data["sources"]:
        if not isinstance(source, dict):
            errors.append(f"{path}: source must be an object")
            continue
        identity = source.get("id")
        if not isinstance(identity, str) or not identity or identity in seen:
            errors.append(f"{path}: source ids must be non-empty and unique")
        else:
            seen.add(identity)
        revision = source.get("revision")
        if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
            errors.append(f"{path}: {identity}: revision must be a full lowercase Git SHA-1")
        if not isinstance(source.get("repository"), str) or not source["repository"].startswith("https://github.com/"):
            errors.append(f"{path}: {identity}: repository must identify its GitHub source")
        if source.get("license") != "MIT":
            errors.append(f"{path}: {identity}: source license must match the supported MIT attribution")
        license_file = source.get("license_file")
        if (not isinstance(license_file, str) or Path(license_file).is_absolute()
                or not _contained_file(root, root / license_file)):
            errors.append(f"{path}: {identity}: missing or escaping license file")
        adaptations = source.get("adaptations")
        if not isinstance(adaptations, list) or not adaptations:
            errors.append(f"{path}: {identity}: adaptations must document source and destination paths")
            continue
        for adaptation in adaptations:
            if not isinstance(adaptation, dict):
                errors.append(f"{path}: {identity}: adaptation must be an object")
                continue
            for field in ("source_paths", "destinations"):
                values = adaptation.get(field)
                if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value for value in values):
                    errors.append(f"{path}: {identity}: {field} must contain paths")
                elif field == "destinations":
                    for value in values:
                        if Path(value).is_absolute() or not _contained_file(root, root / value):
                            errors.append(f"{path}: {identity}: missing or escaping adaptation destination: {value}")
            for field in ("mechanism", "departures"):
                if not isinstance(adaptation.get(field), str) or not adaptation[field].strip():
                    errors.append(f"{path}: {identity}: {field} must explain the adaptation")
    return errors
