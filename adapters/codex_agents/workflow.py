"""Private, candidate-bound workflow receipts and advisory hook routing.

Only fixed, read-only Git commands run here. Skills and agents are nominated;
loading, delegation, authorization and interpretation remain with the parent.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

from manager import AgentError, digest, encode, plugin_manifest, read, safe_path

HANDLER_VERSION = 1
MAX_RECORDS = 128
MAX_FILES = 4096
MAX_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 1024 * 1024
TASK_STATUSES = {"active", "paused", "blocked", "waiting_for_approval", "complete"}
CONDITIONS = {"repeated_check_failure", "review_needed", "governance_mismatch"}
EVIDENCE_CONDITIONS = {"check_failed", "check_passed", "governance_mismatch"}


def bounded(value: object, label: str, limit: int = 1024) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= limit or any(ord(c) < 32 for c in value):
        raise AgentError(f"Provide a bounded {label} without control characters.")
    return value


def identity(value: object, label: str) -> str:
    value = bounded(value, label, 128)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value):
        raise AgentError(f"Provide a safe {label}.")
    return value


def exact_keys(value: object, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise AgentError("The workflow record has missing or unsupported fields.")
    return value


class WorkflowManager:
    def __init__(self, root: Path, codex_home: Path, cwd: Path, session_id: str):
        safe_path(Path(root).absolute())
        self.root = Path(root).resolve(strict=True)
        safe_path(Path(cwd).absolute())
        self.cwd = Path(cwd).resolve(strict=True)
        if not self.cwd.is_dir():
            raise AgentError("The workflow working directory must be a directory.")
        self.session_id = bounded(session_id, "session id", 256)
        self.home = Path(codex_home).absolute()
        safe_path(self.home)
        self.repo = next((p for p in [self.cwd, *self.cwd.parents] if (p / ".git").exists()), None)
        if self.repo is None:
            raise AgentError("Workflow records require a Git repository.")
        manifest = plugin_manifest(self.root)
        self.plugin = manifest["name"]
        self.routes, self.asset_digest = self._route_assets()
        key = digest(encode({"session": self.session_id, "repo": str(self.repo)}))
        self.directory = self.home / "agent-plugin-state" / self.plugin / "workflows" / key
        self.state_path = self.directory / "state.json"
        safe_path(self.directory)

    @classmethod
    def from_environment(cls, cwd: str, session_id: str, root: Path | None = None) -> WorkflowManager:
        home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
        return cls(root or Path(__file__).resolve().parents[2], home, Path(cwd), session_id)

    def _route_assets(self) -> tuple[list[dict], str]:
        path = self.root / "com.openai/hooks/routes.json"
        safe_path(path)
        data = read(path)
        asset = json.loads(data)
        exact_keys(asset, {"schemaVersion", "routes"})
        if type(asset["schemaVersion"]) is not int or asset["schemaVersion"] != 1 or not isinstance(asset["routes"], list) or len(asset["routes"]) > 32:
            raise AgentError("Unsupported workflow route catalog.")
        catalog_path = self.root / "com.openai/agents/catalog.json"
        safe_path(catalog_path)
        catalog_data = read(catalog_path)
        catalog = json.loads(catalog_data)
        if catalog.get("schemaVersion") != 1 or not isinstance(catalog.get("roles"), list):
            raise AgentError("Unsupported role catalog.")
        names = {entry["name"] for entry in catalog["roles"]}
        namespace = bounded(catalog.get("namespace"), "role namespace", 16)
        if any(not re.fullmatch(re.escape(namespace) + r"_[a-z_]+", name) for name in names):
            raise AgentError("The role catalog contains a role outside this plugin's namespace.")
        routes, seen = [], set()
        for item in asset["routes"]:
            exact_keys(item, {"condition", "skill", "role", "description"})
            if item["condition"] not in CONDITIONS or item["condition"] in seen:
                raise AgentError("Unsupported or duplicate workflow route condition.")
            skill = bounded(item["skill"], "skill name", 128)
            if not re.fullmatch(r"[a-z][a-z0-9-]*", skill):
                raise AgentError("Workflow skills must belong to the owning plugin.")
            skill_path = self.root / "skills" / skill / "SKILL.md"
            safe_path(skill_path)
            if not skill_path.is_file() or not skill_path.resolve(strict=True).is_relative_to(self.root / "skills"):
                raise AgentError("The workflow target skill is not packaged by this plugin.")
            if item["role"] not in names:
                raise AgentError("The workflow role is not owned by this plugin.")
            bounded(item["description"], "route description", 1024)
            seen.add(item["condition"])
            routes.append(dict(item))
        return routes, digest(data + catalog_data)

    def _path(self, value: object, *, file: bool = False) -> str:
        value = bounded(value, "repository-relative path", 1024)
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or ".git" in path.parts or value.startswith("~") or "\\" in value:
            raise AgentError("Workflow paths must stay in the repository and exclude Git metadata.")
        normalized = path.as_posix()
        target = self.repo / normalized
        safe_path(target)
        if not target.resolve().is_relative_to(self.repo):
            raise AgentError("Workflow paths must stay in the repository.")
        if file and (not target.is_file() or target.stat().st_size > MAX_FILE_BYTES):
            raise AgentError("Evidence references must identify an existing bounded regular file.")
        return normalized

    def _task(self, task: object) -> dict:
        task = exact_keys(task, {"id", "issue", "delivery_stage", "status", "paths", "checks", "review_requested", "continuation_limit"})
        identity(task["id"], "task id")
        bounded(task["issue"], "issue reference")
        bounded(task["delivery_stage"], "delivery stage", 256)
        if not isinstance(task["status"], str) or task["status"] not in TASK_STATUSES or type(task["review_requested"]) is not bool or type(task["continuation_limit"]) is not int or task["continuation_limit"] not in (0, 1):
            raise AgentError("Invalid task status, review request or continuation limit.")
        if not isinstance(task["paths"], list) or not 0 < len(task["paths"]) <= 64:
            raise AgentError("Provide a nonempty bounded repository scope.")
        paths = sorted({self._path(path) for path in task["paths"]})
        if not isinstance(task["checks"], list) or len(task["checks"]) > 32:
            raise AgentError("Provide a bounded check list.")
        checks, ids, commands = [], set(), set()
        for check in task["checks"]:
            exact_keys(check, {"id", "command", "checker", "environment"})
            identity(check["id"], "check id")
            bounded(check["command"], "exact check command", 4096)
            bounded(check["checker"], "checker identity", 256)
            bounded(check["environment"], "environment identity", 256)
            if check["id"] in ids or check["command"] in commands:
                raise AgentError("Check ids and exact command identities must be unique.")
            ids.add(check["id"])
            commands.add(check["command"])
            checks.append(dict(check))
        return {**task, "paths": paths, "checks": checks}

    def _git(self, *args: str) -> bytes:
        # The command vocabulary is private and fixed; task commands are never run.
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update({"GIT_OPTIONAL_LOCKS": "0", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        try:
            with tempfile.TemporaryFile() as output:
                result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false", "-C", str(self.repo), *args], stdout=output,
                                        stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, timeout=5, check=False, env=env)
                output.seek(0)
                data = output.read(MAX_FILE_BYTES + 1)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise AgentError("The candidate could not be read from Git.") from error
        if result.returncode or len(data) > MAX_FILE_BYTES:
            raise AgentError("The candidate Git metadata is unavailable or too large.")
        return data

    def _fingerprint_once(self, task: dict) -> str:
        scope = [":(literal)" + path for path in task["paths"]]
        head = self._git("rev-parse", "--verify", "HEAD")
        index = self._git("ls-files", "--stage", "-z", "--", *scope)
        untracked = self._git("ls-files", "--others", "--exclude-standard", "-z", "--", *scope)
        paths = {entry.split(b"\t", 1)[1] for entry in index.split(b"\0") if entry}
        paths.update(entry for entry in untracked.split(b"\0") if entry)
        if len(paths) > MAX_FILES:
            raise AgentError("The candidate scope contains too many files.")
        hasher = hashlib.sha256(encode({"head": head.decode("ascii").strip(), "scope": task["paths"]}) + index + untracked)
        total = 0
        for raw in sorted(paths):
            relative = raw.decode("utf-8")
            self._path(relative)
            path = self.repo / relative
            hasher.update(encode({"path": relative}))
            if not path.exists():
                hasher.update(b"deleted\0")
                continue
            before = path.stat()
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
                raise AgentError("The candidate contains an unsupported or oversized file.")
            total += before.st_size
            if total > MAX_BYTES:
                raise AgentError("The candidate scope is too large.")
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise AgentError("The candidate file grew beyond its size bound.")
            after = path.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_ino, before.st_mode) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_ino, after.st_mode):
                raise AgentError("The candidate changed while it was being read.")
            hasher.update(encode({"mode": stat.S_IMODE(before.st_mode), "digest": digest(data)}))
        if head != self._git("rev-parse", "--verify", "HEAD") or index != self._git("ls-files", "--stage", "-z", "--", *scope) or untracked != self._git("ls-files", "--others", "--exclude-standard", "-z", "--", *scope):
            raise AgentError("The candidate changed while it was being read.")
        return hasher.hexdigest()

    def _candidate(self, task: dict) -> str | None:
        try:
            first = self._fingerprint_once(task)
            return first if first == self._fingerprint_once(task) else None
        except (AgentError, OSError, ValueError, UnicodeError, IndexError):
            return None

    def _load(self) -> dict | None:
        safe_path(self.state_path)
        if not self.state_path.exists():
            return None
        state = json.loads(read(self.state_path))
        if state.get("schemaVersion") != 1 or state.get("plugin") != self.plugin or state.get("repo") != str(self.repo) or state.get("session") != self.session_id:
            raise AgentError("The private workflow state has an unsupported identity.")
        state["task"] = self._task(state["task"])
        for field in ("evidence", "routes"):
            if not isinstance(state.get(field), list) or len(state[field]) > MAX_RECORDS:
                raise AgentError("The private workflow state exceeds its record bound.")
        if not isinstance(state.get("pending"), dict) or len(state["pending"]) > 32 or type(state.get("continuations")) is not int or state["continuations"] not in (0, 1):
            raise AgentError("Invalid private workflow state.")
        if not isinstance(state.get("unknown_checks", []), list) or len(state.get("unknown_checks", [])) > MAX_RECORDS:
            raise AgentError("The private unknown-check record exceeds its bound.")
        return state

    def _private_reference(self, reference: str) -> None:
        filename = reference.removeprefix("private-check-receipt:")
        if not re.fullmatch(r"check-[0-9a-f]{64}\.json", filename):
            raise AgentError("Invalid private check receipt reference.")
        path = self.directory / filename
        safe_path(path)
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            raise AgentError("A private check receipt is missing or oversized.")

    @contextlib.contextmanager
    def _mutation(self, *, create: bool = False):
        safe_path(self.directory)
        if not self.state_path.exists() and not create:
            raise AgentError("Initialize an explicit task before recording workflow state.")
        if create:
            for directory in reversed([self.directory, *self.directory.parents]):
                if not directory.exists():
                    directory.mkdir(mode=0o700)
        lock = self.directory / ".lock"
        safe_path(lock)
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        except OSError as error:
            raise AgentError("The workflow lock could not be opened safely.") from error
        try:
            if os.name == "nt":
                import msvcrt
                if os.fstat(descriptor).st_size == 0:
                    os.write(descriptor, b"0")
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            os.close(descriptor)
            raise AgentError("The workflow state is busy; no mutation was performed.") from error
        try:
            yield self._load()
        finally:
            os.close(descriptor)

    def _save(self, state: dict) -> None:
        data = encode(state)
        if len(data) > MAX_FILE_BYTES:
            raise AgentError("The workflow state exceeds its size bound.")
        safe_path(self.state_path)
        descriptor, name = tempfile.mkstemp(prefix=".state-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            safe_path(self.state_path)
            os.replace(name, self.state_path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _scope(self, task: dict) -> str:
        return digest(encode({key: value for key, value in task.items()
                              if key not in {"status", "continuation_limit"}}))

    def _reference_stat(self, reference: str) -> dict:
        if isinstance(reference, str) and reference.startswith("private-check-receipt:"):
            self._private_reference(reference)
            path = self.directory / reference.removeprefix("private-check-receipt:")
        else:
            path = self.repo / self._path(reference, file=True)
        info = path.stat()
        return {"size": info.st_size, "mtime_ns": info.st_mtime_ns, "ctime_ns": info.st_ctime_ns,
                "inode": info.st_ino, "mode": info.st_mode}

    def _reference_valid(self, reference: str, receipt: dict | None = None) -> bool:
        try:
            current = self._reference_stat(reference)
            return receipt is None or current == receipt
        except (AgentError, OSError, ValueError):
            return False

    def _route_current(self, route: dict, task: dict, candidate: str | None) -> bool:
        return bool(candidate and route["candidate"] == candidate and route.get("scope") == self._scope(task)
                    and route.get("asset_digest") == self.asset_digest
                    and all(self._reference_valid(item["reference"], item["stat"]) for item in route.get("evidence_receipts", []))
                    and (route.get("status") != "completed" or self._reference_valid(route.get("reference"), route.get("reference_stat"))))

    def _view(self, state: dict | None) -> dict:
        if state is None:
            return {"state": "absent", "plugin": self.plugin, "candidate": None, "task": None,
                    "evidence": [], "routes": [], "continuations": 0}
        candidate = self._candidate(state["task"])
        scope = self._scope(state["task"])
        return {"state": "ready" if candidate else "candidate_unknown", "plugin": self.plugin,
                "candidate": candidate, "task": state["task"], "continuations": state["continuations"],
                "evidence": [item for item in state["evidence"] if candidate and item["candidate"] == candidate and item.get("scope") == scope and self._reference_valid(item["reference"], item["reference_stat"])],
                "routes": [{**item, "current": self._route_current(item, state["task"], candidate)} for item in state["routes"]]}

    def status(self) -> dict:
        return self._view(self._load())

    def set_task(self, task: dict) -> dict:
        task = self._task(task)
        with self._mutation(create=True) as state:
            if state is None or state["task"]["id"] != task["id"]:
                state = {"schemaVersion": 1, "plugin": self.plugin, "repo": str(self.repo),
                         "session": self.session_id, "task": task, "evidence": [], "routes": [],
                         "pending": {}, "continuations": 0, "unknown_checks": []}
            else:
                if task != state["task"]:
                    state["pending"] = {}
                state["task"] = task
            self._save(state)
            return self._view(state)

    def _evidence(self, evidence: object, task: dict) -> dict:
        evidence = exact_keys(evidence, {"observation_id", "candidate", "condition", "reference"}, {"check_id", "signature"})
        identity(evidence["observation_id"], "observation id")
        if not isinstance(evidence["candidate"], str) or not re.fullmatch(r"[0-9a-f]{64}", evidence["candidate"]):
            raise AgentError("Evidence requires a known candidate fingerprint.")
        if not isinstance(evidence["condition"], str) or evidence["condition"] not in EVIDENCE_CONDITIONS:
            raise AgentError("Unsupported typed evidence condition.")
        reference = self._path(evidence["reference"], file=True)
        if evidence["condition"].startswith("check_"):
            identity(evidence.get("check_id"), "check id")
            bounded(evidence.get("signature"), "failure equivalence signature", 256)
            if not any(check["id"] == evidence["check_id"] for check in task["checks"]):
                raise AgentError("The evidence check is not part of the explicit task.")
        elif "check_id" in evidence or "signature" in evidence:
            raise AgentError("Governance evidence must not claim a check result.")
        return {**evidence, "reference": reference}

    def _append_evidence(self, state: dict, evidence: dict) -> None:
        existing = next((item for item in state["evidence"] if item["observation_id"] == evidence["observation_id"]), None)
        payload = dict(evidence)
        if existing:
            if existing["payload_digest"] != digest(encode(payload)):
                raise AgentError("An observation id was reused with different evidence.")
            return
        if len(state["evidence"]) >= MAX_RECORDS:
            raise AgentError("The workflow evidence record limit has been reached.")
        check = next((check for check in state["task"]["checks"] if check["id"] == evidence.get("check_id")), None)
        state["evidence"].append({**payload, "scope": self._scope(state["task"]),
                                  "reference_stat": self._reference_stat(payload["reference"]),
                                  "payload_digest": digest(encode(payload)),
                                  **({"checker": check["checker"], "environment": check["environment"], "command": check["command"]} if check else {})})

    def record_evidence(self, evidence: dict) -> dict:
        with self._mutation() as state:
            evidence = self._evidence(evidence, state["task"])
            if evidence["candidate"] != self._candidate(state["task"]):
                raise AgentError("Evidence does not describe the current known candidate.")
            self._append_evidence(state, evidence)
            self._save(state)
            return self._view(state)

    def update_route(self, route_id: str, status: str, agent_id: str | None = None,
                     outcome: str | None = None, reference: str | None = None) -> dict:
        identity(route_id, "route id")
        if not isinstance(status, str) or status not in {"assigned", "completed"}:
            raise AgentError("Record a parent assignment or completed outcome.")
        with self._mutation() as state:
            candidate = self._candidate(state["task"])
            route = next((item for item in state["routes"] if item["id"] == route_id), None)
            if route is None or not self._route_current(route, state["task"], candidate):
                raise AgentError("The route is missing or belongs to a stale candidate.")
            if agent_id is not None:
                identity(agent_id, "agent id")
            if status == "assigned":
                if outcome is not None or reference is not None or route["status"] == "completed":
                    raise AgentError("Assignments cannot overwrite a completed outcome.")
                if route["status"] == "assigned" and route.get("agent_id") != agent_id:
                    raise AgentError("An existing route assignment cannot be replaced.")
                route.update({"status": status, "agent_id": agent_id})
            else:
                if route["status"] not in {"assigned", "completed"}:
                    raise AgentError("Record the parent assignment before completing a route.")
                if outcome not in {"passed", "findings", "unknown"}:
                    raise AgentError("Completion requires passed, findings or unknown outcome.")
                reference = self._path(reference, file=True)
                if agent_id is not None and agent_id != route.get("agent_id"):
                    raise AgentError("Completion cannot replace the parent's assigned agent.")
                completed = {"status": status, "agent_id": agent_id or route.get("agent_id"), "outcome": outcome, "reference": reference,
                             "reference_stat": self._reference_stat(reference)}
                if route["status"] == "completed" and any(route.get(key) != value for key, value in completed.items()):
                    raise AgentError("A completed route cannot be overwritten.")
                route.update(completed)
            self._save(state)
            return self._view(state)

    def _conditions(self, state: dict, candidate: str) -> dict[str, list[str]]:
        task = state["task"]
        scope = self._scope(task)
        evidence = [item for item in state["evidence"] if item["candidate"] == candidate and item["scope"] == scope]
        conditions = {"review_needed": []} if task["review_requested"] else {}
        mismatches = [item["reference"] for item in evidence if item["condition"] == "governance_mismatch" and self._reference_valid(item["reference"], item["reference_stat"])]
        if mismatches:
            conditions["governance_mismatch"] = mismatches
        for check in task["checks"]:
            streak, signature = [], None
            unknown_after = max((item["after"] for item in state.get("unknown_checks", [])
                                 if item["candidate"] == candidate and item["check_id"] == check["id"]), default=-1)
            for index, item in enumerate(state["evidence"]):
                if index <= unknown_after or item not in evidence:
                    continue
                if item.get("check_id") != check["id"] or item.get("checker") != check["checker"] or item.get("environment") != check["environment"] or item.get("command") != check["command"]:
                    continue
                if not self._reference_valid(item["reference"], item["reference_stat"]):
                    streak, signature = [], None
                    continue
                if item["condition"] == "check_passed":
                    streak, signature = [], None
                elif item["condition"] == "check_failed":
                    if item["signature"] != signature:
                        streak, signature = [], item["signature"]
                    streak.append(item["reference"])
            refs = streak if len(streak) >= 2 else []
            if refs:
                conditions.setdefault("repeated_check_failure", []).extend(refs)
        return conditions

    def _nominate(self, state: dict) -> list[dict]:
        if state["task"]["status"] != "active":
            return []
        candidate = self._candidate(state["task"])
        if candidate is None:
            return []
        conditions = self._conditions(state, candidate)
        scope = self._scope(state["task"])
        new = []
        for route in self.routes:
            if route["condition"] not in conditions:
                continue
            key = digest(encode({"task": state["task"]["id"], "scope": scope, "condition": route["condition"],
                                 "candidate": candidate, "handler": HANDLER_VERSION, "assets": self.asset_digest}))
            if any(item["id"] == key for item in state["routes"]):
                continue
            if len(state["routes"]) >= MAX_RECORDS:
                raise AgentError("The workflow route record limit has been reached.")
            item = {"id": key, **route, "candidate": candidate, "scope": scope, "asset_digest": self.asset_digest,
                    "status": "nominated", "evidence_references": sorted(set(conditions[route["condition"]])),
                    "evidence_receipts": [{"reference": item["reference"], "stat": item["reference_stat"]}
                        for item in state["evidence"] if item["candidate"] == candidate and item["scope"] == scope
                        and item["reference"] in conditions[route["condition"]]
                        and self._reference_valid(item["reference"], item["reference_stat"])]}
            state["routes"].append(item)
            new.append(item)
        return new

    def _instructions(self, routes: list[dict]) -> str:
        return "\n".join(
            f"Workflow nomination {route['id']} for candidate {route['candidate']}: {route['description']} "
            f"Use ${self.plugin}:{route['skill']}; delegate to {route['role']} only if the registered role is currently available and useful. "
            "The parent must assign bounded work and preserve current scope, instructions and delivery authority. "
            "This nomination grants no authority and does not load a skill or spawn an agent. "
            f"Evidence references: {', '.join(route['evidence_references']) or 'explicit task review request'}. "
            "Record assignment and completion through the workflow tools."
            for route in routes)

    def _event_workdir(self, event: dict) -> bool:
        tool_input = event.get("tool_input")
        if not isinstance(tool_input, dict):
            return False
        for field in ("cwd", "workdir", "working_directory"):
            if field in tool_input:
                value = tool_input[field]
                if not isinstance(value, str) or not Path(value).is_absolute():
                    return False
                path = Path(value)
                try:
                    safe_path(path)
                    if path.resolve(strict=True) != self.cwd:
                        return False
                except (AgentError, OSError):
                    return False
        return True

    def _before(self, state: dict, event: dict) -> None:
        if event.get("tool_name") != "Bash" or not self._event_workdir(event):
            return
        tool_input = event["tool_input"]
        if set(tool_input) - {"command", "cwd", "workdir", "working_directory", "timeout", "description"}:
            return
        check = next((check for check in state["task"]["checks"] if check["command"] == tool_input.get("command")), None)
        if check is None:
            return
        call = identity(event.get("tool_use_id"), "tool use id")
        candidate = self._candidate(state["task"])
        if candidate is None or call in state["pending"]:
            return
        if len(state["pending"]) >= 32:
            raise AgentError("The pending check receipt limit has been reached.")
        state["pending"][call] = {"candidate": candidate, "check": check, "scope": self._scope(state["task"])}

    def _unknown(self, state: dict, candidate: str, check_id: str) -> None:
        unknown = {"candidate": candidate, "check_id": check_id, "after": len(state["evidence"]) - 1}
        state.setdefault("unknown_checks", [])[:] = [item for item in state.get("unknown_checks", [])
            if (item["candidate"], item["check_id"]) != (candidate, check_id)] + [unknown]
        if len(state["unknown_checks"]) > MAX_RECORDS:
            raise AgentError("The unknown-check receipt limit has been reached.")

    def _after(self, state: dict, event: dict) -> bool:
        call = event.get("tool_use_id")
        if not isinstance(call, str) or call not in state["pending"]:
            if isinstance(call, str):
                existing = next((item for item in state["evidence"] if item["observation_id"] == "hook-" + digest(call.encode())), None)
                if existing:
                    response = event.get("tool_response")
                    code = response.get("exit_code") if isinstance(response, dict) else None
                    if type(code) is not int or existing.get("signature") != "exit:" + str(code):
                        raise AgentError("A hook observation id was reused with a different result.")
                    return False
            tool_input = event.get("tool_input")
            if event.get("tool_name") == "Bash" and isinstance(tool_input, dict):
                check = next((check for check in state["task"]["checks"] if check["command"] == tool_input.get("command")), None)
                candidate = self._candidate(state["task"])
                if check is not None and candidate is not None:
                    self._unknown(state, candidate, check["id"])
            return False
        pending = state["pending"].pop(call)
        if event.get("tool_name") != "Bash" or not self._event_workdir(event):
            self._unknown(state, pending["candidate"], pending["check"]["id"])
            return False
        if event["tool_input"].get("command") != pending["check"]["command"]:
            self._unknown(state, pending["candidate"], pending["check"]["id"])
            return False
        response = event.get("tool_response")
        exit_code = response.get("exit_code") if isinstance(response, dict) else None
        candidate = self._candidate(state["task"])
        if type(exit_code) is not int or candidate is None or candidate != pending["candidate"] or pending["scope"] != self._scope(state["task"]):
            self._unknown(state, pending["candidate"], pending["check"]["id"])
            return False
        # Keep only typed status and stable identity; tool output is never retained.
        receipt_name = "check-" + digest(call.encode()) + ".json"
        receipt_path = self.directory / receipt_name
        receipt = {"tool_use_id": call, "candidate": candidate, "check_id": pending["check"]["id"], "exit_code": exit_code}
        safe_path(receipt_path)
        if receipt_path.exists():
            if read(receipt_path) != encode(receipt):
                raise AgentError("A check receipt identity was reused with different evidence.")
        else:
            with receipt_path.open("xb") as stream:
                os.chmod(receipt_path, 0o600)
                stream.write(encode(receipt))
        evidence = {"observation_id": "hook-" + digest(call.encode()), "candidate": candidate,
                    "condition": "check_passed" if exit_code == 0 else "check_failed",
                    "check_id": pending["check"]["id"], "signature": "exit:" + str(exit_code),
                    "reference": "private-check-receipt:" + receipt_name}
        self._append_evidence(state, evidence)
        return True

    def handle_event(self, event: dict) -> dict:
        if not isinstance(event, dict) or event.get("hook_event_name") not in {"SessionStart", "PreToolUse", "PostToolUse", "Stop", "Interrupt"}:
            return {}
        if "session_id" in event and event["session_id"] != self.session_id:
            return {}
        if "cwd" in event:
            if not isinstance(event["cwd"], str):
                return {}
            try:
                safe_path(Path(event["cwd"]).absolute())
                if Path(event["cwd"]).resolve(strict=True) != self.cwd:
                    return {}
            except (AgentError, OSError):
                return {}
        safe_path(self.state_path)
        if not self.state_path.exists():
            return {}
        name = event["hook_event_name"]
        with self._mutation() as state:
            if state is None:
                return {}
            output = {}
            original = encode(state)
            if name == "Interrupt":
                state["checkpoint"] = {"task_id": state["task"]["id"], "candidate": None,
                                       "status": state["task"]["status"], "candidate_verified": False}
            elif name == "SessionStart":
                view = self._view(state)
                task = state["task"]
                text = (f"Restore explicit workflow task {task['id']} ({task['issue']}); status {task['status']}; "
                        f"delivery stage {task['delivery_stage']}; scope {', '.join(task['paths'])}; candidate {view['candidate'] or 'unknown'}. "
                        "Historical task instructions are subordinate to the current user and current session instructions. "
                        "The delivery stage is a record, never authorization. Read codex_workflow_status for current evidence and routes.")
                new = self._nominate(state)
                if new:
                    text += "\n" + self._instructions(new)
                output = {"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}}
            elif state["task"]["status"] == "active":
                if name == "PreToolUse":
                    self._before(state, event)
                elif name == "PostToolUse":
                    recorded = self._after(state, event)
                    workflow_call = isinstance(event.get("tool_name"), str) and bool(re.fullmatch(r"mcp__.+__codex_workflow_(task|evidence|route)", event["tool_name"]))
                    new = self._nominate(state) if recorded or workflow_call else []
                    if new:
                        output = {"hookSpecificOutput": {"hookEventName": name, "additionalContext": self._instructions(new)}}
                elif name == "Stop" and event.get("stop_hook_active") is not True and state["continuations"] < state["task"]["continuation_limit"]:
                    new = self._nominate(state)
                    if new:
                        state["continuations"] += 1
                        output = {"decision": "block", "reason": self._instructions(new)}
            if encode(state) != original:
                self._save(state)
            return output


_STRING = {"type": "string", "minLength": 1, "maxLength": 1024}
_CHECK_SCHEMA = {"type": "object", "properties": {
    "id": {**_STRING, "maxLength": 128}, "command": {**_STRING, "maxLength": 4096},
    "checker": {**_STRING, "maxLength": 256}, "environment": {**_STRING, "maxLength": 256}},
    "required": ["id", "command", "checker", "environment"], "additionalProperties": False}
TASK_SCHEMA = {"type": "object", "properties": {
    "id": {**_STRING, "maxLength": 128}, "issue": _STRING,
    "delivery_stage": {**_STRING, "maxLength": 256, "description": "Recorded delivery stage; never an authority grant."},
    "status": {"type": "string", "enum": sorted(TASK_STATUSES)},
    "paths": {"type": "array", "items": _STRING, "minItems": 1, "maxItems": 64},
    "checks": {"type": "array", "items": _CHECK_SCHEMA, "maxItems": 32},
    "review_requested": {"type": "boolean"}, "continuation_limit": {"type": "integer", "minimum": 0, "maximum": 1}},
    "required": ["id", "issue", "delivery_stage", "status", "paths", "checks", "review_requested", "continuation_limit"], "additionalProperties": False}
EVIDENCE_SCHEMA = {"type": "object", "properties": {
    "observation_id": {**_STRING, "maxLength": 128}, "candidate": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "condition": {"type": "string", "enum": sorted(EVIDENCE_CONDITIONS)}, "reference": _STRING,
    "check_id": {**_STRING, "maxLength": 128}, "signature": {**_STRING, "maxLength": 256}},
    "required": ["observation_id", "candidate", "condition", "reference"], "additionalProperties": False}


def _definition(name: str, description: str, extra: dict, required: list[str], *, readonly: bool = False) -> dict:
    properties = {"cwd": {**_STRING, "description": "Current absolute session working directory."},
                  "session_id": {**_STRING, "maxLength": 256}, **extra}
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties, "required": ["cwd", "session_id", *required], "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}


TOOL_DEFINITIONS = [
    _definition("codex_workflow_task", "Initialize or update an explicit bounded task; this records scope and delivery stage without granting authority.", {"task": TASK_SCHEMA}, ["task"]),
    _definition("codex_workflow_evidence", "Record typed current-candidate evidence references, without reading evidence contents or transcripts.", {"evidence": EVIDENCE_SCHEMA}, ["evidence"]),
    _definition("codex_workflow_route", "Record the parent's workflow assignment or candidate-bound completed result; no skill or agent is invoked.", {
        "route_id": {**_STRING, "maxLength": 128}, "status": {"type": "string", "enum": ["assigned", "completed"]},
        "agent_id": {**_STRING, "maxLength": 128}, "outcome": {"type": "string", "enum": ["passed", "findings", "unknown"]}, "reference": _STRING}, ["route_id", "status"]),
    _definition("codex_workflow_status", "Read private task, current candidate, evidence references and route freshness; does not create state.", {}, [], readonly=True),
]


def dispatch(name: str, args: dict, root: Path | None = None) -> dict:
    definition = next((item for item in TOOL_DEFINITIONS if item["name"] == name), None)
    if definition is None:
        raise AgentError("Unknown workflow tool.")
    schema = definition["inputSchema"]
    exact_keys(args, set(schema["required"]), set(schema["properties"]) - set(schema["required"]))
    if not isinstance(args["cwd"], str) or not Path(args["cwd"]).is_absolute():
        raise AgentError("Provide the current absolute working directory.")
    manager = WorkflowManager.from_environment(args["cwd"], args["session_id"], root)
    if name == "codex_workflow_task":
        return manager.set_task(args["task"])
    if name == "codex_workflow_evidence":
        return manager.record_evidence(args["evidence"])
    if name == "codex_workflow_route":
        return manager.update_route(args["route_id"], args["status"], args.get("agent_id"), args.get("outcome"), args.get("reference"))
    return manager.status()
