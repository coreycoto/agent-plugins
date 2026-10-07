"""Validate an explicitly supplied consumer feature map without executing its commands."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FEATURE_ID = re.compile(r"[a-z0-9]+(?:[-._][a-z0-9]+)*")
STATES = {"unverified", "passed", "failed"}


class MapInputError(ValueError):
    """The selected input or explicit changed paths cannot be inspected."""


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and "\0" not in value


def _root(value):
    try:
        root = Path(value).resolve(strict=True)
        if root.is_dir():
            return root
    except (OSError, RuntimeError):
        pass
    raise MapInputError("Consumer root must be an existing directory")


def _contained(root, value, *, exists=False, kind=None, allow_dot=False):
    if not _text(value) or "\\" in value or ":" in value:
        raise ValueError("Expected a portable relative path")
    parts = value.split("/")
    if value == "." and allow_dot:
        parts = []
    elif value.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Path must be contained, without absolute or traversal components")
    path = root
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink components are not permitted")
        if index < len(parts) - 1 and path.exists() and not path.is_dir():
            raise ValueError("A path parent is not a directory")
    present = path.exists()
    if exists and not present:
        raise ValueError("Referenced path does not exist")
    if present and ((kind == "file" and not path.is_file()) or
                    (kind == "directory" and not path.is_dir()) or
                    (kind is None and not (path.is_file() or path.is_dir()))):
        raise ValueError(f"Referenced path is not a {kind or 'regular file or directory'}")
    return path, present


def _keys(value, names, field, errors):
    if not isinstance(value, dict) or set(value) != set(names):
        errors.append({"field": field, "message": "Expected exactly the documented fields"})
        return False
    return True


def _strings(value, field, errors, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value) or not all(_text(item) for item in value):
        errors.append({"field": field, "message": "Expected an array of nonempty strings"})
        return False
    return True


def validate_feature_map(document, root, changed_paths=()):
    """Return schema/path checks and conservative affected IDs; never qualify behavior.

    ``document`` is decoded JSON. ``root`` is an explicit consumer directory.
    Changed paths are relative, may have been deleted, and may name directories.
    Invalid maps return ``valid=False``; unusable inputs raise ``MapInputError``.
    """
    root = _root(root)
    changed = []
    for value in changed_paths:
        try:
            _contained(root, value)
            changed.append(value)
        except (ValueError, OSError):
            raise MapInputError("Invalid changed path: use a contained path without symlink components") from None
    changed = sorted(set(changed))
    errors, features = [], []
    result = {"valid": False, "errors": errors, "features": features,
              "changed_paths": changed, "affected_features": [],
              "qualification_verified": False, "coverage_complete": False,
              "scope": "schema, referenced paths and explicit change mapping only; commands not executed"}
    if not _keys(document, {"schema_version", "features"}, "map", errors):
        return result
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        errors.append({"field": "schema_version", "message": "Expected schema version 1"})
    if not isinstance(document["features"], list) or not document["features"]:
        errors.append({"field": "features", "message": "Expected a nonempty array"})
        return result
    seen = set()
    for index, feature in enumerate(document["features"]):
        field = f"features[{index}]"
        if not _keys(feature, {"id", "behavior", "entrypoint", "relevant_files", "verification", "qualification"}, field, errors):
            continue
        identifier = feature["id"]
        if not isinstance(identifier, str) or len(identifier) > 80 or not FEATURE_ID.fullmatch(identifier):
            errors.append({"field": field + ".id", "message": "Expected a stable lowercase feature identifier"})
            continue
        if identifier in seen:
            errors.append({"field": field + ".id", "message": "Duplicate feature identifier"})
        seen.add(identifier)
        references, missing_evidence = [], []

        def text(value, suffix):
            if not _text(value):
                errors.append({"field": field + suffix, "message": "Expected a nonempty string"})

        def path(value, suffix, *, mapped=False, **options):
            try:
                if mapped:
                    # Keep safe declared references for deletion/rename selection.
                    # Existence and kind errors remain independent map problems.
                    _contained(root, value)
                    references.append(value)
                return _contained(root, value, **options)[1]
            except (ValueError, OSError) as error:
                errors.append({"field": field + suffix, "message": str(error) if isinstance(error, ValueError) else "Could not inspect referenced path"})
                return None

        if _keys(feature["behavior"], {"source", "expected"}, field + ".behavior", errors):
            behavior = feature["behavior"]
            text(behavior["expected"], ".behavior.expected")
            path(behavior["source"], ".behavior.source", mapped=True, exists=True, kind="file")
        text(feature["entrypoint"], ".entrypoint")
        if _strings(feature["relevant_files"], field + ".relevant_files", errors, nonempty=True):
            for position, value in enumerate(feature["relevant_files"]):
                path(value, f".relevant_files[{position}]", mapped=True, exists=True)
        qualification = feature["qualification"]
        state = None
        if _keys(qualification, {"state", "source_revision", "environment", "reason"}, field + ".qualification", errors):
            state = qualification["state"]
            if not isinstance(state, str) or state not in STATES:
                errors.append({"field": field + ".qualification.state", "message": "Expected unverified, passed or failed"})
                state = None
            text(qualification["reason"], ".qualification.reason")
            for key in ("source_revision", "environment"):
                if not (state == "unverified" and qualification[key] is None):
                    text(qualification[key], ".qualification." + key)
        verification = feature["verification"]
        if _keys(verification, {"argv", "cwd", "prerequisites", "evidence"}, field + ".verification", errors):
            _strings(verification["argv"], field + ".verification.argv", errors, nonempty=True)
            path(verification["cwd"], ".verification.cwd", exists=True, kind="directory", allow_dot=True)
            _strings(verification["prerequisites"], field + ".verification.prerequisites", errors)
            if _strings(verification["evidence"], field + ".verification.evidence", errors, nonempty=True):
                for position, value in enumerate(verification["evidence"]):
                    present = path(value, f".verification.evidence[{position}]", exists=state in {"passed", "failed"}, kind="file")
                    if present is False:
                        missing_evidence.append(value)
        affected = sorted({value for value in changed if any(
            value == reference or value.startswith(reference + "/") or reference.startswith(value + "/")
            for reference in references)})
        features.append({"id": identifier, "declared_state": state,
                         "current_qualification": "unverified",
                         "stale_candidate": bool(affected), "affected_by": affected,
                         "missing_planned_evidence": missing_evidence})
    result["valid"] = not errors
    result["affected_features"] = sorted({feature["id"] for feature in features if feature["stale_candidate"]})
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def inspect_feature_map(map_path, root, changed_paths=()):
    """Read one explicit JSON map and call :func:`validate_feature_map`."""
    try:
        document = json.loads(Path(map_path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError):
        raise MapInputError("Feature map must be readable UTF-8 JSON with unique fields") from None
    return validate_feature_map(document, root, changed_paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path, help="Explicit feature-map JSON file")
    parser.add_argument("--root", type=Path, required=True, help="Explicit consumer root")
    parser.add_argument("--changed-path", action="append", default=[], help="Contained changed or deleted path (repeatable)")
    args = parser.parse_args(argv)
    try:
        result = inspect_feature_map(args.map, args.root, args.changed_path)
    except MapInputError as error:
        print(json.dumps({"valid": False, "input_error": str(error), "qualification_verified": False}))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
