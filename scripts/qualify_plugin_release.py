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
REVIEWED_FAILURE_RUN_ID = 37705082572
REVIEWED_FAILURE_VERSION = "0.9.1"
REVIEWED_FAILURE_REVISION = "5be0b7b1dae318ebc0cf31eb5515226d9424c905"


def package_name(plugin: str) -> str:
    if plugin not in PLUGINS:
        raise ValueError("Select an independently released public plugin")
    return f"@coreycoto/agent-plugin-{plugin}"


def require_successful_ci(runs: list[dict], revision: str) -> dict:
    """The API selects source only; establish successful main CI from actual fields."""
    matches = [run for run in runs if (
        run.get("head_sha") == revision and run.get("head_branch") == "main"
        and run.get("status") == "completed" and run.get("conclusion") == "success"
        and run.get("event") == "push" and run.get("path") == ".github/workflows/ci.yml"
        and (run.get("repository") or {}).get("full_name") == REPOSITORY_NAME)]
    if not matches:
        raise ValueError("No successful exact-source main CI")
    return {"source_revision": revision, "ci_run_id": matches[0]["id"],
            "ci_status": "completed", "ci_conclusion": "success"}


def require_first_publication(runs: list[dict], run_id: int, run_attempt: int,
                              version: str, *, recovery_run: dict | None = None,
                              recovery_jobs: list[dict] | None = None) -> dict:
    """Allow only the explicitly reviewed qualification failure; never replay publication."""
    prior = [run for run in runs if run["id"] != run_id
             and run["display_title"] == f"Agent Plugins {version}"]
    if run_attempt != 1:
        raise ValueError("Publication already attempted; inspect prior receipts before reviewed recovery")
    if not prior and recovery_run is None and recovery_jobs is None:
        return {"publication_mode": "initial-publication"}
    if (version != REVIEWED_FAILURE_VERSION or len(prior) != 1
            or prior[0]["id"] != REVIEWED_FAILURE_RUN_ID
            or recovery_run is None or recovery_jobs is None):
        raise ValueError("Publication already attempted; only the exact reviewed qualification failure may recover")
    expected_run = {"id": REVIEWED_FAILURE_RUN_ID, "head_sha": REVIEWED_FAILURE_REVISION,
                    "display_title": f"Agent Plugins {REVIEWED_FAILURE_VERSION}",
                    "head_branch": "main", "event": "workflow_dispatch", "run_attempt": 1,
                    "path": ".github/workflows/publish-plugins.yml", "status": "completed",
                    "conclusion": "failure"}
    if (any(recovery_run.get(key) != value for key, value in expected_run.items())
            or (recovery_run.get("repository") or {}).get("full_name") != REPOSITORY_NAME
            or len(recovery_jobs) != 2 or {job.get("name") for job in recovery_jobs} != {"qualify", "publish"}
            or any(job.get("run_id") != REVIEWED_FAILURE_RUN_ID
                   or job.get("run_attempt") != 1 or job.get("head_sha") != REVIEWED_FAILURE_REVISION
                   or job.get("status") != "completed" for job in recovery_jobs)):
        raise ValueError("Reviewed recovery requires complete exact-run and attempt evidence")
    jobs = {job["name"]: job for job in recovery_jobs}
    steps = jobs["qualify"].get("steps") or []
    expected_steps = {"Require exact dispatch source and successful main CI": "failure",
                      "Hold any previous attempt for this version": "skipped",
                      "Build and qualify all four exact package candidates": "skipped"}
    if (jobs["qualify"].get("conclusion") != "failure"
            or jobs["publish"].get("conclusion") != "skipped"
            or jobs["publish"].get("steps") != []
            or any(len([step for step in steps if step.get("name") == name
                        and step.get("status") == "completed" and step.get("conclusion") == conclusion]) != 1
                   for name, conclusion in expected_steps.items())):
        raise ValueError("Reviewed recovery requires positive proof that publication never started")
    return {"publication_mode": "reviewed-qualification-recovery",
            "prior_run_id": REVIEWED_FAILURE_RUN_ID, "prior_run_attempt": 1,
            "prior_source_revision": REVIEWED_FAILURE_REVISION, "version": version,
            "publication_never_started_verified": True}


def require_unchanged_recovery_inputs(root: Path) -> None:
    """The workflow repair cannot silently replace the already reviewed package candidate."""
    result = subprocess.run(["git", "diff", "--exit-code", REVIEWED_FAILURE_REVISION, "HEAD", "--",
                             "plugins", "adapters", "LICENSE", ".agents/plugins",
                             "scripts/build_codex_package.py"], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("Reviewed recovery requires unchanged package inputs and builder")


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
