"""Temporary-home experiment for flat rules ownership; NOT a callable installer.

The role installer owns whole directories. Native rules need a flat loaded file
and separate ownership state. This model tests that contract before any runtime
integration. It intentionally has no MCP/CLI/hook entrypoint.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OWNER = "coreycoto/agent-plugins:project-management:release-review"
RULE = "agent-plugins-project-management-release-review.rules"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Conflict(ValueError):
    pass


class InstallerModel:
    def __init__(self, home: Path, repo: Path, version: str, template: bytes):
        self.home, self.repo = home, repo
        self.version, self.template = version, template

    def paths(self, scope: str) -> tuple[Path, Path]:
        if scope not in {"user", "project"}:
            raise Conflict("unknown scope")
        base = self.home if scope == "user" else self.repo / ".codex"
        return (base / "rules" / RULE,
                base / "agent-plugin-state/project-management/release-policy.json")

    def snapshot(self, scope: str) -> dict:
        target, marker = self.paths(scope)
        for path in (target, marker):
            if any(parent.is_symlink() for parent in (path, *path.parents)):
                raise Conflict("symlinked path")
        if not target.exists() and not marker.exists():
            return {"state": "missing"}
        if not target.is_file() or not marker.is_file():
            raise Conflict("unowned or incomplete installation")
        try:
            record = json.loads(marker.read_bytes())
            if (record["owner"] != OWNER or record["schema"] != 1
                    or record["sha256"] != sha(target.read_bytes())):
                raise Conflict("ownership or local drift")
            installed = tuple(int(x) for x in record["version"].split("."))
            desired = tuple(int(x) for x in self.version.split("."))
            if len(installed) != 3 or installed > desired:
                raise Conflict("downgrade or invalid version")
            if installed == desired and record["sha256"] != sha(self.template):
                raise Conflict("same version has different bytes")
        except (KeyError, TypeError, ValueError) as error:
            raise Conflict("invalid ownership or drift") from error
        return {"state": "ready" if installed == desired else "upgrade_available",
                "rule": sha(target.read_bytes()), "marker": sha(marker.read_bytes())}

    def preview(self, scope: str, *, project_trusted: bool = False) -> dict:
        if scope == "project" and not project_trusted:
            raise Conflict("project trust required")
        other = "project" if scope == "user" else "user"
        if self.snapshot(other)["state"] != "missing":
            raise Conflict("duplicate scopes")
        target, marker = self.paths(scope)
        plan = {"scope": scope, "version": self.version, "template_sha256": sha(self.template),
                "target": str(target), "marker": str(marker), "current": self.snapshot(scope)}
        plan["fingerprint"] = sha(json.dumps(plan, sort_keys=True).encode())
        return plan

    def apply(self, plan: dict, *, consent: object, project_trusted: bool = False) -> str:
        if consent is not True:
            return "deferred"
        if self.preview(plan["scope"], project_trusted=project_trusted) != plan:
            raise Conflict("reviewed plan changed")
        if plan["current"]["state"] == "ready":
            return "unchanged"
        target, marker = self.paths(plan["scope"])
        # Single-process model only. Production needs a lock, staged writes,
        # recovery journal and path/race handling before this can be an installer.
        marker.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = marker.parent / ("release-policy-" + sha(target.read_bytes()) + ".backup")
            backup.write_bytes(target.read_bytes())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self.template)
        marker.write_text(json.dumps({"schema": 1, "owner": OWNER, "version": self.version,
                                      "sha256": sha(self.template)}, sort_keys=True))
        return "written_reload_and_runtime_verification_pending"
