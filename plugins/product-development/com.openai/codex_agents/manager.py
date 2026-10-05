"""Owned, consent-gated projections of packaged roles into native Codex discovery."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import tomllib
import uuid
from pathlib import Path

OWNER = "coreycoto/agent-plugins:product-development"
MARKER = ".agent-plugins.json"
RESTART = (
    "Restart Codex and resume this chat; in CLI, exit and relaunch in the repository. "
    "This MCP connection cannot reload the desktop app's active configuration. "
    "A client-supported reload is sufficient only after custom-role discovery is verified. "
    "Compaction or rerunning SessionStart is not proof of a reload. Then inspect the spawn "
    "tool's role selector and use the registered role names when delegation is appropriate."
)


class AgentError(RuntimeError):
    """An intentionally non-sensitive error safe to surface through a hook."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_048_576:
        raise AgentError("Expected a regular file of at most 1 MiB; resolve the path conflict.")
    return path.read_bytes()


def safe_path(path: Path) -> None:
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise AgentError("Symlinked installation paths require manual resolution.")


def private_dir(path: Path) -> None:
    safe_path(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.is_dir():
        raise AgentError("Installation path is not a directory.")


def private_write(path: Path, data: bytes) -> None:
    safe_path(path)
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value):
        raise AgentError("This installer requires a stable three-part package version.")
    return tuple(int(part) for part in value.split("."))


class Manager:
    def __init__(self, root: Path, codex_home: Path, cwd: Path):
        self.root = root.resolve(strict=True)
        self.home = codex_home.absolute()
        self.cwd = cwd.resolve(strict=True)
        if not self.cwd.is_dir():
            raise AgentError("The working directory must be a directory.")
        safe_path(self.home)
        manifest_path = self.root / "plugin.json"
        if not manifest_path.exists():
            manifest_path = self.root / ".codex-plugin/plugin.json"
        manifest = json.loads(read(manifest_path))
        if manifest.get("name") != "product-development":
            raise AgentError("Unexpected plugin identity.")
        self.version = manifest["version"]
        version(self.version)
        agents = self.root / "com.openai/agents"
        catalog = json.loads(read(agents / "catalog.json"))
        if catalog.get("schemaVersion") != 1 or not catalog.get("roles"):
            raise AgentError("Unsupported or empty role catalog.")
        self.files: dict[str, bytes] = {".gitignore": b"*\n"}
        self.roles = []
        for entry in catalog["roles"]:
            name, filename = entry["name"], entry["file"]
            if not re.fullmatch(r"pd_[a-z_]+", name) or filename != name + ".toml":
                raise AgentError("Invalid namespaced role identity.")
            asset = agents / filename
            asset.resolve(strict=True).relative_to(self.root)
            data = read(asset)
            role = tomllib.loads(data.decode())
            if role.get("name") != name or not role.get("description") or not role.get("developer_instructions"):
                raise AgentError("The role is missing required native fields.")
            if role.get("sandbox_mode") != "read-only":
                raise AgentError("This pilot only supports read-only roles.")
            if name in {item["name"] for item in self.roles}:
                raise AgentError("Duplicate catalog role.")
            self.files[filename] = data
            self.roles.append({
                "name": name, "model": role["model"], "effort": role["model_reasoning_effort"],
                "routing": entry["routing"],
            })
        self.asset_digest = digest(encode({
            "version": self.version, "catalog": catalog,
            "files": {name: digest(data) for name, data in self.files.items()},
        }))
        self.repo = next((parent for parent in [self.cwd, *self.cwd.parents]
                          if (parent / ".git").exists()), None)

    @classmethod
    def from_environment(cls, cwd: str) -> Manager:
        home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
        return cls(Path(__file__).resolve().parents[2], home, Path(cwd))

    def target(self, scope: str) -> Path:
        if scope == "user":
            return self.home / "agents/product-development"
        if scope == "project" and self.repo:
            return self.repo / ".codex/agents/product-development"
        raise AgentError("Project installation requires a repository working directory.")

    def snapshot(self, target: Path) -> dict:
        safe_path(target)
        if not target.exists():
            return {"state": "missing", "hashes": {}}
        if not target.is_dir():
            return {"state": "conflict", "reason": "Target is not a directory."}
        hashes = {path.name: digest(read(path)) for path in sorted(target.iterdir())}
        if MARKER not in hashes:
            return {"state": "conflict", "reason": "Target has no ownership marker.", "hashes": hashes}
        try:
            marker = json.loads(read(target / MARKER))
            if marker["owner"] != OWNER or marker["schemaVersion"] != 1:
                raise ValueError("owner")
            if set(hashes) != set(marker["files"]) | {MARKER}:
                raise ValueError("unexpected files")
            if any(hashes[name] != expected for name, expected in marker["files"].items()):
                raise ValueError("modified files")
            current = version(marker["version"])
            if not isinstance(marker["assetDigest"], str) or not isinstance(marker["installedDuringSession"], str):
                raise ValueError("invalid receipt")
        except (KeyError, TypeError, ValueError, AgentError) as error:
            return {"state": "conflict", "reason": "Owned files or marker were edited; preserve and resolve them.", "hashes": hashes, "error": type(error).__name__}
        state = "ready" if marker["assetDigest"] == self.asset_digest else "upgrade_available"
        if current > version(self.version):
            state = "downgrade_blocked"
        return {"state": state, "marker": marker, "hashes": hashes}

    def conflicts(self) -> list[dict]:
        """Check native discovery layers without returning other configuration values."""
        bases = {self.home, *(parent / ".codex" for parent in [self.cwd, *self.cwd.parents]
                              if (parent / ".codex").exists())}
        owned = set()
        for scope in ("user", "project") if self.repo else ("user",):
            target = self.target(scope)
            if self.snapshot(target)["state"] in {"ready", "upgrade_available", "downgrade_blocked"}:
                owned.add(target)
        names = {role["name"] for role in self.roles}
        conflicts = []
        for base in sorted(bases):
            config = base / "config.toml"
            if config.exists() or config.is_symlink():
                settings = tomllib.loads(read(config).decode())
                for name in names & settings.get("agents", {}).keys():
                    conflicts.append({"name": name, "path": str(config), "reason": "Explicit role registration already exists."})
            directory = base / "agents"
            if directory.is_symlink():
                raise AgentError("Symlinked agent discovery directory requires manual resolution.")
            for path in sorted(directory.rglob("*.toml")) if directory.exists() else []:
                if any(path.is_relative_to(target) for target in owned):
                    continue
                role = tomllib.loads(read(path).decode())
                if role.get("name") in names:
                    conflicts.append({"name": role["name"], "path": str(path), "reason": "An existing discovered role has this name."})
        return conflicts

    def plans(self) -> dict[str, dict]:
        conflicts = self.conflicts()
        plans = {}
        for scope in ("user", "project") if self.repo else ("user",):
            target = self.target(scope)
            snap = self.snapshot(target)
            other = self.snapshot(self.target("project" if scope == "user" else "user")) if self.repo else {"state": "missing"}
            if conflicts or other["state"] != "missing":
                snap = {**snap, "state": "conflict", "reason": "Resolve duplicate role scopes or existing registrations first."}
            plans[scope] = {
                "scope": scope, "target": str(target), "state": snap["state"],
                "version": self.version, "installedVersion": snap.get("marker", {}).get("version"),
                "reason": snap.get("reason"), "conflicts": conflicts,
                "fingerprint": digest(encode({"snapshot": snap, "conflicts": conflicts, "other": other, "desired": self.asset_digest})),
                "files": sorted([*self.files, MARKER]),
            }
        return plans

    def status(self, session_id: str = "") -> dict:
        plans = self.plans()
        observed = self.observed(session_id) if session_id and any(plan["state"] == "ready" for plan in plans.values()) else []
        return {
            "plugin": "product-development", "version": self.version,
            "roles": self.roles, "installations": plans,
            "session": {"id": session_id, "nativeRoleSelections": observed,
                        "verification": "role_selection_observed" if observed else "pending"},
            "restartGuidance": RESTART,
        }

    def state_dir(self, scope: str = "user") -> Path:
        base = self.target(scope).parents[1]
        return base / "agent-plugin-state/product-development"

    def apply(self, scope: str, fingerprint: str, session_id: str) -> dict:
        """Called only after an accepted native form; revalidate before any writes."""
        current = self.plans().get(scope)
        if not current or current["fingerprint"] != fingerprint:
            raise AgentError("The reviewed plan changed while the form was open; no role files changed.")
        if current["state"] == "ready":
            return {"result": "unchanged", "restartGuidance": RESTART}
        if current["state"] not in {"missing", "upgrade_available"}:
            raise AgentError("Resolve installation conflicts before applying this plan.")
        target, state = self.target(scope), self.state_dir(scope)
        private_dir(state)
        if not (state / ".gitignore").exists():
            private_write(state / ".gitignore", b"*\n")
        lock = state / "install.lock"
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError as error:
            raise AgentError("Another install may be running; inspect the installation lock before retrying.") from error
        stage = None
        backup = None
        committed = False
        try:
            if self.plans()[scope]["fingerprint"] != fingerprint:
                raise AgentError("The reviewed plan changed; no role files changed.")
            stage = Path(tempfile.mkdtemp(prefix="stage-", dir=state))
            for name, data in self.files.items():
                private_write(stage / name, data)
            private_write(stage / MARKER, encode({
                "schemaVersion": 1, "owner": OWNER, "version": self.version,
                "assetDigest": self.asset_digest, "installedDuringSession": session_id,
                "files": {name: digest(data) for name, data in self.files.items()},
            }))
            if self.plans()[scope]["fingerprint"] != fingerprint:
                raise AgentError("The reviewed plan changed during staging; no role files changed.")
            expected_snapshot = self.snapshot(target)
            private_dir(target.parent)
            if target.exists():
                backups = state / "backups"
                private_dir(backups)
                backup = backups / str(uuid.uuid4())
                os.rename(target, backup)
                if self.snapshot(backup) != expected_snapshot:
                    raise AgentError("Role files changed during publication; preserve and inspect the restored files.")
            if target.exists() or target.is_symlink():
                raise AgentError("The installation target changed during publication.")
            os.rename(stage, target)
            stage = None
            committed = True
            if self.snapshot(target)["state"] != "ready":
                raise AgentError("Installed files could not be verified; inspect the target and backup before retrying.")
            return {"result": "installed" if backup is None else "upgraded", "scope": scope,
                    "target": str(target), "version": self.version,
                    "backup": str(backup) if backup else None, "sessionVerification": "pending",
                    "restartRequired": True, "restartGuidance": RESTART}
        except BaseException:
            if not committed and backup is not None and not target.exists() and not target.is_symlink():
                os.rename(backup, target)
            raise
        finally:
            if stage is not None:
                shutil.rmtree(stage)
            lock.rmdir()

    def record_start(self, event: dict) -> bool:
        """A native SubagentStart receipt proves selection, not arbitrary live policy reload."""
        session, name, agent_id = event.get("session_id"), event.get("agent_type"), event.get("agent_id")
        if not all(isinstance(value, str) and 0 < len(value) <= 256 for value in (session, name, agent_id)):
            return False
        if name not in {role["name"] for role in self.roles}:
            return False
        ready = [scope for scope, plan in self.plans().items() if plan["state"] == "ready"]
        if len(ready) != 1:
            return False
        marker = self.snapshot(self.target(ready[0]))["marker"]
        if marker["installedDuringSession"] == session:
            return False  # Never claim that installation reloaded the active session.
        directory = self.state_dir() / "sessions" / digest(session.encode())
        private_dir(directory)
        path = directory / (digest(agent_id.encode()) + ".json")
        if not path.exists():
            private_write(path, encode({"session": session, "role": name, "agentId": agent_id,
                                        "assetDigest": self.asset_digest, "cwd": str(self.cwd)}))
        return True

    def observed(self, session_id: str) -> list[str]:
        directory = self.state_dir() / "sessions" / digest(session_id.encode())
        safe_path(directory)
        result = set()
        for path in directory.glob("*.json") if directory.exists() else []:
            receipt = json.loads(read(path))
            if receipt.get("session") == session_id and receipt.get("assetDigest") == self.asset_digest and receipt.get("cwd") == str(self.cwd):
                result.add(receipt["role"])
        return sorted(result)
