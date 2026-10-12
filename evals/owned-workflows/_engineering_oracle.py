"""Read-only, frozen evidence checks for synthetic engineering tasks, not agent efficacy."""
from __future__ import annotations

import json
import re
import shlex
import sqlite3
import sys
from pathlib import Path

SCRIPTS = {
    "check-protocol": "analysis.py",
    "rehearse-migration": "rehearsal.py",
    "assess-data-quality": "assessment.py",
}
DATABASES = {f"artifacts/{name}.sqlite3" for name in ("before", "after", "resumed", "restored")}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def regular(path: Path) -> bytes:
    require(not path.is_symlink() and path.is_file(), f"Missing regular file: {path.name}")
    require(path.stat().st_size <= 1_000_000, f"Oversized fixture artifact: {path.name}")
    return path.read_bytes()


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise AssertionError(f"Non-JSON constant: {value}")


def decode(text):
    return json.loads(text, object_pairs_hook=pairs, parse_constant=reject_constant)


def evidence(workspace: Path) -> dict:
    result = decode(regular(workspace / "evidence.json"))
    require(isinstance(result, dict), "Evidence must be an object")
    return result


def source_scope(suite: Path, workspace: Path) -> None:
    expected = {path.name: regular(path) for path in (suite / "fixtures").iterdir()}
    for name, data in expected.items():
        require(regular(workspace / name) == data, f"Changed input: {name}")
    allowed = set(expected)
    if suite.name in SCRIPTS:
        allowed |= {SCRIPTS[suite.name], "evidence.json"}
    if suite.name == "rehearse-migration":
        allowed |= DATABASES
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        if relative.parts[0] == ".agents":
            continue  # The runner independently freezes and verifies its skill closure.
        require(not path.is_symlink(), f"Symlinked artifact: {relative}")
        if path.is_file():
            require(relative.as_posix() in allowed, f"Unexpected artifact: {relative}")


def replay(trace, *, repair=False):
    """Independent interpreter of the tiny contract; do not import submitted code."""
    require(isinstance(trace, list) and 0 < len(trace) <= 20, "Expected a bounded nonempty trace")
    phase, accepted = "ready", 0
    for action in trace:
        require(isinstance(action, str), "Trace actions must be strings")
        if phase == "ready" and accepted < 2 and action == "dispatch":
            phase = "sent"
        elif phase == "sent" and action in {"accept_reply", "accept_lost"}:
            accepted += 1
            phase = "done" if action == "accept_reply" else "unknown"
        elif phase == "unknown" and action == "observe":
            phase = "done"
        elif phase == "unknown" and action == "wait":
            pass
        elif phase == "unknown" and action == "expire" and not repair:
            phase = "ready"
        else:
            raise AssertionError(f"Invalid {action} from {phase}")
    return phase, accepted


def protocol(workspace: Path, result: dict) -> None:
    regular(workspace / "analysis.py")
    _, accepted = replay(result.get("unsafe_trace"))
    require(accepted > 1, "Trace does not violate the accepted-effect invariant")
    phase, count = replay(result.get("completion_trace"), repair=True)
    require(phase == "done" and count == 1, "Control needs a legitimate completion path")
    require(result.get("control_has_violation") is False, "Incorrect control conclusion")
    require(result.get("progress_checked") is False, "Finite safety evidence is not a liveness check")
    for key in ("assumptions", "implementation_limits"):
        require(isinstance(result.get(key), str) and bool(result[key].strip()), f"Missing {key}")


def rows(workspace: Path, name: str, *, expanded: bool):
    path = workspace / "artifacts" / f"{name}.sqlite3"
    regular(path)
    connection = sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        fields = "id, amount_text, amount_cents" if expanded else "id, amount_text"
        return connection.execute(f"SELECT {fields} FROM invoices ORDER BY id").fetchall()
    finally:
        connection.close()


def migration(workspace: Path, result: dict) -> None:
    regular(workspace / "rehearsal.py")
    require(rows(workspace, "before", expanded=False) == [("a", "1.25"), ("b", "0.00")], "Wrong baseline")
    require(rows(workspace, "after", expanded=True) == [("a", "1.25", 100), ("b", "0.00", 0), ("c", "2.50", None)], "Missing actual intermediate defects")
    require(rows(workspace, "resumed", expanded=True) == [("a", "1.25", 100), ("b", "0.00", 0), ("c", "2.50", 200)], "Wrong resumed snapshot")
    require(rows(workspace, "restored", expanded=False) == [("a", "1.25"), ("b", "0.00")], "Wrong restored snapshot")
    require(result.get("conversion_mismatches") == ["a", "c"], "Fractional conversion defect not identified")
    require(result.get("missing_new_values") == ["c"], "Late old-writer gap not identified")
    require(result.get("restore_loses_ids") == ["c"], "Restore would lose an accepted write")
    for key in ("fresh_process_tested", "new_writer_tested"):
        require(result.get(key) is False, f"Unsupported claim: {key}")
    require(isinstance(result.get("rollout_limits"), str) and bool(result["rollout_limits"].strip()), "Missing rollout limits")


def data_quality(workspace: Path, result: dict) -> None:
    regular(workspace / "assessment.py")
    expected = {
        "dataset_id": "survey-snapshot-1", "missing_sources": ["east"],
        "duplicate_keys": ["south:s1:1"], "invalid_unit_keys": ["south:s2:1"],
        "invalid_area_keys": [], "rows_examined": 6, "expected_source_count": 3,
    }
    for key, value in expected.items():
        require(type(result.get(key)) is type(value) and result[key] == value, f"Wrong {key}")
    require(result.get("freshness_verified") is False, "No freshness requirement was supplied")
    require(result.get("external_accuracy_verified") is False, "No independent accuracy reference was supplied")


def command_matches(command: str, script: str, workspace: Path) -> bool:
    args = shlex.split(command)
    if args and Path(args[0]).name in {"sh", "bash", "zsh"}:
        if len(args) != 3 or args[1] not in {"-c", "-lc"}:
            return False
        args = shlex.split(args[2])
    return bool(
        len(args) >= 2 and re.fullmatch(r"python(?:3(?:\.\d+)?)?", Path(args[0]).name)
        and all(arg in {"-B", "-I"} for arg in args[1:-1])
        and args[-1] in {script, f"./{script}", str(workspace / script)}
    )


def execution(suite: Path, workspace: Path, events_path: Path) -> None:
    events = decode(regular(events_path))
    require(isinstance(events, list), "Events must be a runner-captured list")
    result = evidence(workspace)
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        if item.get("status") != "completed" or type(item.get("exit_code")) is not int or item["exit_code"] != 0:
            continue
        command = item.get("command")
        if not isinstance(command, str) or not command_matches(command, SCRIPTS[suite.name], workspace):
            continue
        try:
            output = decode(item.get("aggregated_output", ""))
        except (ValueError, TypeError, AssertionError):
            continue
        if output == result:
            return
    raise AssertionError("No successful completed task entrypoint emitting the retained evidence")


def main(suite: Path, mode: str) -> int:
    if len(sys.argv) != 4:
        raise RuntimeError("Expected WORKSPACE RESPONSE_PATH EVENTS_PATH")
    workspace = Path(sys.argv[1])
    require(not workspace.is_symlink(), "Workspace must not be a symlink")
    workspace = workspace.resolve()
    try:
        source_scope(suite, workspace)
        if mode == "execution":
            execution(suite, workspace, Path(sys.argv[3]))
        elif suite.name != "engineering-judgment":
            checks = {"check-protocol": protocol, "rehearse-migration": migration, "assess-data-quality": data_quality}
            checks[suite.name](workspace, evidence(workspace))
    except (AssertionError, OSError, ValueError, sqlite3.DatabaseError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: bounded artifact evidence")
    return 0
