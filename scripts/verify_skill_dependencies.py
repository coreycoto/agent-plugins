"""Validate owned packages and optional legacy native skill dependencies."""
from __future__ import annotations

import argparse
from pathlib import Path

from author_checks.skills_lock import (
    SKILLS_LOCK_FILENAME,
    license_snapshot_path,
    load_github_skill_lock,
    verify_installed_dependencies,
)


def validate_package_dependencies(plugin: Path) -> list[str]:
    manifest = plugin / "plugin.json"
    if plugin.is_symlink() or not plugin.is_dir() or manifest.is_symlink() or not manifest.is_file():
        return [f"{plugin}: missing or unsafe plugin root (plugin.json is required)"]
    lock = plugin / SKILLS_LOCK_FILENAME
    if not lock.exists() and not lock.is_symlink():
        return []  # Owned, self-contained packages have no runtime dependency lock.
    try:
        entries = load_github_skill_lock(lock)
    except ValueError as error:
        return [str(error)]
    errors: list[str] = []
    for name in entries:
        if (plugin / "skills" / name).exists():
            errors.append(f"{name}: upstream dependencies must not be bundled as plugin skills")
    for source in {entry["source"] for entry in entries.values()}:
        notice = plugin / license_snapshot_path(source)
        if notice.is_symlink() or not notice.is_file():
            errors.append(f"{source}: missing or unsafe dependency license notice")
    return errors


def plugin_roots(repo_root: Path, plugin_root: Path | None = None) -> list[Path]:
    if plugin_root is not None:
        return [plugin_root]
    return [path.parent for path in sorted((repo_root / "plugins").glob("*/plugin.json"))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plugin-root", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--consumer-lock", type=Path)
    args = parser.parse_args()
    if bool(args.installed_root) != bool(args.consumer_lock):
        parser.error("--installed-root and --consumer-lock must be provided together")
    if args.installed_root and args.plugin_root is None:
        parser.error("consumer verification requires --plugin-root")
    plugins = plugin_roots(args.repo_root, args.plugin_root)
    if not plugins:
        parser.error("no authored plugins found")
    errors: list[str] = []
    for plugin in plugins:
        errors.extend(validate_package_dependencies(plugin))
        if args.installed_root and (plugin / SKILLS_LOCK_FILENAME).exists():
            errors.extend(verify_installed_dependencies(
                plugin / SKILLS_LOCK_FILENAME, args.installed_root, args.consumer_lock,
            ))
    for error in errors:
        print(f"error: {error}")
    if errors:
        return 1
    locked = sum((plugin / SKILLS_LOCK_FILENAME).is_file() for plugin in plugins)
    if not locked:
        print(f"Checked {len(plugins)} plugin packages: no runtime skill dependencies declared.")
    elif args.installed_root:
        print("Native skill dependencies verified: source pins, paths and installed content hashes.")
    else:
        print(f"Validated {locked} legacy dependency locks; consumer installation was not checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
