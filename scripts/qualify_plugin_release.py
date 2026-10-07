"""Qualify exact public plugin artifacts and registry reads; never publish here."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from build_codex_package import distribution_projection, package_metadata, source_files

REPOSITORY = Path(__file__).resolve().parents[1]
REGISTRY = "https://npm.pkg.github.com"
REPOSITORY_NAME = "coreycoto/agent-plugins"
PLUGINS = ("communication", "product-development", "product-management", "project-management")


def package_name(plugin: str) -> str:
    if plugin not in PLUGINS:
        raise ValueError("Select an independently released public plugin")
    return f"@coreycoto/agent-plugin-{plugin}"


def require_first_publication(runs: list[dict], run_id: int, run_attempt: int,
                              version: str) -> None:
    """A prior same-version dispatch holds the entire coordinated release."""
    if run_attempt != 1 or any(
        run["id"] != run_id and run["display_title"] == f"Agent Plugins {version}"
        for run in runs
    ):
        raise ValueError("Publication already attempted; inspect prior receipts before reviewed recovery")


def qualify_registry_metadata(metadata: dict, plugin: str) -> dict:
    """Package creation can initially be private; do not claim public delivery."""
    name = package_name(plugin).split("/")[1]
    if (metadata.get("visibility") not in {"private", "public"}
            or metadata.get("name") != name
            or metadata.get("package_type") != "npm"
            or (metadata.get("repository") or {}).get("full_name") != REPOSITORY_NAME):
        raise ValueError("Registry package identity, visibility and publisher association are unverified")
    return {"schema_version": 1, "package": package_name(plugin), "registry": REGISTRY,
            "repository": REPOSITORY_NAME, "observed_visibility": metadata["visibility"],
            "package_identity_verified": True,
            "public_visibility_verified": metadata["visibility"] == "public"}


def qualify_registry_version(metadata: dict, plugin: str, version: str, archive: Path) -> dict:
    """Bind the fresh registry version and checksum to the acquired artifact."""
    payload = archive.read_bytes()
    distribution = metadata.get("dist") or {}
    url = urlsplit(distribution.get("tarball", ""))
    checksums = {"shasum": hashlib.sha1(payload).hexdigest(),
                 "integrity": "sha512-" + base64.b64encode(
                     hashlib.sha512(payload).digest()).decode("ascii")}
    observed_checksums = [name for name in checksums if name in distribution]
    if (metadata.get("name") != package_name(plugin) or metadata.get("version") != version
            or url.scheme != "https" or url.hostname != "npm.pkg.github.com"
            or url.username is not None or url.password is not None
            or any(distribution[name] != checksums[name] for name in observed_checksums)):
        raise ValueError("Registry version, destination or artifact checksum mismatch")
    return {"package": package_name(plugin), "version": version, "registry": REGISTRY,
            "archive_sha256": hashlib.sha256(payload).hexdigest(),
            "registry_checksums_observed": observed_checksums,
            "registry_checksum_verified": bool(observed_checksums)}


def require_committed_inputs(root: Path) -> None:
    inputs = []
    for name in PLUGINS:
        plugin = Path("plugins") / name
        inputs += [plugin / name for name in source_files(root / plugin)]
    inputs += [Path("adapters/codex_agents") / name for name in ("manager.py", "server.py", "hook.py")]
    inputs += [Path("LICENSE"), Path(".agents/plugins/distribution.json"),
               Path(".agents/plugins/marketplace.json")]
    for name in ("publisher.json", "public-source.json"):
        path = Path(".agents/plugins") / name
        if (root / path).exists():
            inputs.append(path)
    for path in inputs:
        committed = subprocess.run(["git", "show", f"HEAD:{path.as_posix()}"], cwd=root,
                                   capture_output=True, check=False)
        if committed.returncode or committed.stdout != (root / path).read_bytes():
            raise ValueError(f"Build input is not the committed source: {path}")


def qualify(root: Path, revision: str, version: str, archive: Path, plugin: str) -> dict:
    package = package_name(plugin)
    if not re.fullmatch(r"[0-9a-f]{40}", revision) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Select a full source SHA and stable package version")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                    cwd=root, text=True)
    if head != revision or dirty:
        raise ValueError("Release source must be the selected clean revision")
    require_committed_inputs(root)
    for name in PLUGINS:
        metadata = package_metadata(root / "plugins" / name, root)
        if (metadata["name"] != package_name(name) or metadata["version"] != version
                or metadata["publishConfig"] != {"registry": REGISTRY, "access": "public"}
                or metadata["repository"]["url"] != f"https://github.com/{REPOSITORY_NAME}.git"):
            raise ValueError("Coordinated public package identity, version or destination mismatch")
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("Release archive must be a regular file")
    payload = archive.read_bytes()
    name = f"npm/coreycoto-agent-plugin-{plugin}-{version}.tgz"
    if payload != distribution_projection(root)[name]:
        raise ValueError("Release archive differs from the selected source build")
    return {"schema_version": 1, "source_revision": head, "package": package,
            "version": version, "registry": REGISTRY, "intended_visibility": "public",
            "archive_sha256": hashlib.sha256(payload).hexdigest(), "archive_bytes": len(payload)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--plugin", choices=PLUGINS, required=True)
    args = parser.parse_args()
    try:
        receipt = qualify(REPOSITORY, args.revision, args.version, args.archive, args.plugin)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
