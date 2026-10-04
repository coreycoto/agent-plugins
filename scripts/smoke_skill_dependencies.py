"""Replay plugin dependency locks with the native Vercel CLI in isolated consumer projects."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from author_checks.skills_lock import (
    SKILLS_LOCK_FILENAME,
    load_github_skill_lock,
    verify_installed_dependencies,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skills-cli", type=Path, help="Optional installed skills 1.7.0 executable")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    locks = sorted((root / "plugins").glob(f"*/{SKILLS_LOCK_FILENAME}"))
    if not locks:
        parser.error("no native plugin dependency locks found")
    scratch = Path(tempfile.mkdtemp(prefix="native-skill-dependency-smoke-"))
    environment = os.environ.copy()
    environment.update({
        "HOME": str(scratch / "home"),
        "CODEX_HOME": str(scratch / "codex"),
        "XDG_CONFIG_HOME": str(scratch / "config"),
        "XDG_STATE_HOME": str(scratch / "state"),
        "XDG_DATA_HOME": str(scratch / "data"),
        "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1", "GIT_TERMINAL_PROMPT": "0",
    })
    cli = [str(args.skills_cli.resolve())] if args.skills_cli else ["npx", "--yes", "skills@1.7.0"]
    version = subprocess.run(
        [*cli, "--version"], cwd=scratch, env=environment,
        check=True, capture_output=True, text=True, timeout=180,
    ).stdout.strip()
    if version != "1.7.0":
        raise ValueError(f"expected Skills CLI 1.7.0, found {version!r}")
    receipts: list[dict[str, object]] = []
    for lock in locks:
        entries = load_github_skill_lock(lock)
        consumer = scratch / lock.parent.name
        consumer.mkdir()
        shutil.copyfile(lock, consumer / SKILLS_LOCK_FILENAME)
        completed = subprocess.run(
            [*cli, "experimental_install"], cwd=consumer, env=environment,
            capture_output=True, text=True, timeout=300,
        )
        (consumer / "restore.log").write_text(completed.stdout + completed.stderr)
        errors = verify_installed_dependencies(
            lock, consumer / ".agents/skills", consumer / SKILLS_LOCK_FILENAME,
        )
        if completed.returncode or errors:
            raise ValueError(
                f"native restore failed for {lock.parent.name}; see {consumer / 'restore.log'}; "
                + "; ".join(errors)
            )
        receipts.append({"plugin": lock.parent.name, "skills": len(entries),
                         "consumer": str(consumer), "source_pins_and_content_hashes_verified": True})
    result = {"cli_version": version, "source_revision": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "scratch": str(scratch), "packages": receipts, "global_install": False}
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
