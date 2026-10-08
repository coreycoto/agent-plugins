"""Offline portable package author checks, independent of client/runtime adapters."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from author_checks.owned_workflows import validate_markdown_references, validate_source_lineage


def _openai_settings(manifest: dict[str, object]) -> dict[str, object]:
    extensions = manifest.get("extensions", {})
    value = extensions.get("com.openai") if isinstance(extensions, dict) else None
    return value if isinstance(value, dict) else {}


def _read_manifest_file(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"Plugin manifest must be a regular file: {path}.")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (OSError, ValueError) as error:
        raise RuntimeError(f"Plugin manifest is invalid: {path}.") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"Plugin manifest must be an object: {path}.")
    return payload


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON value: {value}")


def _validate_skill(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise ValueError("YAML frontmatter is required")
        metadata = yaml.safe_load(text.split("\n---\n", 1)[0][4:])
        if not isinstance(metadata, dict):
            raise ValueError("frontmatter must be a mapping")
        name = metadata.get("name")
        if not isinstance(name, str) or not 1 <= len(name) <= 64 or re.fullmatch(r"(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", name) is None or name != path.parent.name:
            raise ValueError("skill name must be valid and match its directory")
        for field, maximum in (("description", 1024), ("compatibility", 500)):
            value = metadata.get(field)
            if field == "compatibility" and value is None:
                continue
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise ValueError(f"{field} must be a non-empty string of at most {maximum} characters")
        if set(metadata) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}:
            raise ValueError("unsupported skill frontmatter fields")
        for field in ("license", "allowed-tools"):
            if field in metadata and not isinstance(metadata[field], str):
                raise ValueError(f"{field} must be a string")
        extra = metadata.get("metadata", {})
        if not isinstance(extra, dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in extra.items()):
            raise ValueError("metadata must map strings to strings")
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"{path}: {error}"]
    return []


def _validate_workflow_routes(root: Path) -> list[str]:
    """Check optional owned routing assets without executing a runtime adapter."""
    path = root / "com.openai/hooks/routes.json"
    if not path.exists() and not path.is_symlink():
        return []
    try:
        data = _read_manifest_file(path)
        catalog = _read_manifest_file(root / "com.openai/agents/catalog.json")
        namespace = catalog.get("namespace")
        if not isinstance(namespace, str) or not re.fullmatch(r"[a-z][a-z0-9]{1,15}", namespace):
            raise ValueError("invalid owned role namespace")
        roles = catalog.get("roles")
        if catalog.get("schemaVersion") != 1 or not isinstance(roles, list):
            raise ValueError("invalid owned role catalog")
        names = {role["name"] for role in roles}
        if any(not re.fullmatch(re.escape(namespace) + r"_[a-z_]+", name) for name in names):
            raise ValueError("roles must belong to the owning plugin namespace")
        routes = data.get("routes")
        if (set(data) != {"schemaVersion", "routes"} or type(data["schemaVersion"]) is not int
                or data["schemaVersion"] != 1 or not isinstance(routes, list) or len(routes) > 32):
            raise ValueError("invalid workflow route catalog")
        seen = set()
        for route in routes:
            if not isinstance(route, dict) or set(route) != {"condition", "skill", "role", "description"}:
                raise ValueError("unsupported workflow route fields")
            condition, skill = route["condition"], route["skill"]
            if condition not in {"repeated_check_failure", "review_needed", "governance_mismatch"} or condition in seen:
                raise ValueError("unsupported or duplicate workflow route condition")
            if not isinstance(skill, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", skill):
                raise ValueError("workflow skills must belong to the owning plugin")
            target = root / "skills" / skill / "SKILL.md"
            target.resolve(strict=True).relative_to((root / "skills").resolve())
            if target.is_symlink() or not target.is_file() or route["role"] not in names:
                raise ValueError("workflow target skill and role must be packaged by the owning plugin")
            description = route["description"]
            if not isinstance(description, str) or not 0 < len(description) <= 1024 or any(ord(c) < 32 for c in description):
                raise ValueError("workflow route description must be concise plain text")
            seen.add(condition)
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as error:
        return [f"{path}: {error}"]
    return []


def validate_portable_plugin(root: Path, schema: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if root.is_symlink() or not root.is_dir():
        return [f"{root}: plugin root must be a regular directory"]
    try:
        manifest = _read_manifest_file((root / "plugin.json"))
    except RuntimeError as error:
        return [str(error)]
    errors.extend(f"{root}: {error.message}" for error in Draft202012Validator(schema).iter_errors(manifest))
    # Publisher conformance is strict even though clients may ignore unknown fields.
    for path in root.rglob("*"):
        if path.is_symlink():
            try:
                path.resolve(strict=True).relative_to(root.resolve())
            except (OSError, ValueError):
                errors.append(f"{path}: package path escapes root or is dangling")
    skills = root / "skills"
    if skills.exists() and not skills.is_dir():
        errors.append(f"{skills}: skills component must be a directory")
    elif skills.is_dir():
        for child in skills.iterdir():
            path = child / "SKILL.md"
            if child.is_dir() and child.name != "_shared" and not path.is_file():
                errors.append(f"{child}: skill directory must contain SKILL.md")
            if child.is_dir() and path.is_file():
                try:
                    path.resolve(strict=True).relative_to(root.resolve())
                except (OSError, ValueError):
                    continue  # The package containment error above already rejects it.
                errors.extend(_validate_skill(path))
        errors.extend(validate_markdown_references(root))
        errors.extend(validate_source_lineage(root))
    settings = _openai_settings(manifest)
    errors.extend(_validate_workflow_routes(root))
    mcp = root / "mcp.json"
    if mcp.exists() or mcp.is_symlink():
        try:
            payload = _read_manifest_file(mcp)
            mcp_schema = json.loads((Path(__file__).resolve().parents[2] / "schemas/agent-plugins-1.0.0.mcp.schema.json").read_text())
            errors.extend(f"{mcp}: {error.message}" for error in Draft202012Validator(mcp_schema).iter_errors(payload))
        except RuntimeError as error:
            errors.append(str(error))
    onboarding = settings.get("onboardingSkill")
    if onboarding is not None:
        try:
            if not isinstance(onboarding, str) or not onboarding.startswith("./skills/"):
                raise ValueError("onboardingSkill must reference a packaged skill")
            path = root / onboarding
            path.resolve(strict=True).relative_to(root.resolve())
            if path.name != "SKILL.md" or not path.is_file():
                raise ValueError("onboardingSkill must reference SKILL.md")
        except (OSError, ValueError):
            errors.append(f"{root}: invalid onboardingSkill reference")
    for field in ("apps", "hooks"):
        value = settings.get(field)
        if value is None:
            continue
        values = value if isinstance(value, list) else [value]
        for value in values:
            if isinstance(value, dict) and field == "hooks":
                continue
            if not isinstance(value, str) or not value.startswith("./com.openai/"):
                errors.append(f"{root}: {field} must reference a com.openai extension file")
                continue
            path = root / value
            try:
                path.resolve(strict=True).relative_to(root.resolve())
                if not path.is_file():
                    raise ValueError("extension must reference a file")
            except (OSError, ValueError):
                errors.append(f"{root}: invalid {field} path {value}")
    return errors
