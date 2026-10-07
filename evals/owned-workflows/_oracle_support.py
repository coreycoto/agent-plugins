"""Independent, standard-library graders kept outside measured consumer workspaces.

Each assertion accepts workspace, response and parsed Codex JSON events paths.
No grader trusts a narrated claim or edits the submitted workspace.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text())


def run(command, workspace):
    return subprocess.run(
        command, cwd=workspace, capture_output=True, text=True, timeout=10,
        env={"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def frozen(workspace, fixtures, names):
    for name in names:
        assert (workspace / name).read_bytes() == (fixtures / name).read_bytes(), f"Changed protected file: {name}"


def inventory(workspace, allowed):
    actual = set()
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        # The runtime stages the procedure closure here and independently checks
        # its exact byte inventory after execution. Product scope excludes it.
        if relative.parts[0] == ".agents":
            continue
        assert not path.is_symlink(), f"Unexpected symlink: {relative}"
        if path.is_file() and "__pycache__" not in path.parts:
            actual.add(relative.as_posix())
    assert actual <= set(allowed), f"Unexpected files: {sorted(actual - set(allowed))}"


def interval_contract(workspace, fixtures, response, events):
    # Enumerate 20 intervals x 20 intervals. Set intersection is independent of
    # the comparison expression likely used by the submitted implementation.
    probe = '''import json, runpy
conflicts = runpy.run_path("scheduler.py")["conflicts"]
intervals = [(a, b) for a in range(-2, 3) for b in range(a, 4)]
bookings = [(i, a, b) for i, (a, b) in enumerate(intervals)]
for a, b in intervals:
    expected = [i for i, c, d in bookings if set(range(a, b)) & set(range(c, d))]
    actual = conflicts(bookings, a, b)
    assert actual == expected, (a, b, actual, expected)
assert conflicts([(0, 1, 2), (9, 2, 3)], 0, 1) == []
assert conflicts([(0, 1, 3), (9, 2, 4)], 2, 3) == [0, 9]
print(json.dumps({"interval_pairs": len(intervals) ** 2}))
'''
    result = run([sys.executable, "-I", "-B", "-c", probe], workspace)
    assert result.returncode == 0, f"Interval contract failed: {result.stderr}"
    assert read_json_string(result.stdout) == {"interval_pairs": 400}


def read_json_string(value):
    return json.loads(value)


def regression_sensitivity(workspace, fixtures, response, events):
    assert (workspace / "test_scheduler.py").is_file(), "Missing regression tests"
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        shutil.copyfile(workspace / "test_scheduler.py", scratch / "test_scheduler.py")
        shutil.copyfile(workspace / "scheduler.py", scratch / "scheduler.py")
        command = [sys.executable, "-I", "-B", "-m", "unittest", "discover", "-s", str(scratch), "-p", "test_scheduler.py"]
        corrected = run(command, scratch)
        assert corrected.returncode == 0, f"Submitted regression failed: {corrected.stderr}"
        assert "Ran 0 tests" not in corrected.stderr, "No regression tests executed"
        shutil.copyfile(fixtures / "scheduler.py", scratch / "scheduler.py")
        broken = run(command, scratch)
        assert broken.returncode != 0 and "FAIL:" in broken.stderr, "Regression does not detect the original behavior failure"
        assert "ERROR:" not in broken.stderr, "Original-source run failed through setup/import errors"


def diagnosis_and_scope(workspace, fixtures, response, events):
    text = (workspace / "diagnosis.md").read_text().lower()
    assert "half-open" in text and any(word in text for word in ("boundary", "adjacen", "touch")), "Diagnosis must identify the supported interval boundary cause"
    assert any(word in text for word in ("test", "regression", "unittest")), "Missing verification account"
    frozen(workspace, fixtures, ["README.md", "AGENTS.md"])
    inventory(workspace, ["scheduler.py", "README.md", "AGENTS.md", "test_scheduler.py", "diagnosis.md"])


class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tokens = []
        self.export_text = []
        self.export_depth = 0

    def handle_decl(self, decl):
        self.tokens.append(("decl", decl.lower()))

    def handle_starttag(self, tag, attrs):
        self.tokens.append(("start", tag, tuple(sorted(attrs))))
        if self.export_depth:
            self.export_depth += 1
        elif tag == "button" and dict(attrs).get("id") == "export-button":
            self.export_depth = 1

    def handle_endtag(self, tag):
        self.tokens.append(("end", tag))
        if self.export_depth:
            self.export_depth -= 1

    def handle_data(self, data):
        if data.strip():
            self.tokens.append(("text", data.strip()))
            if self.export_depth:
                self.export_text.append(data.strip())

    def handle_comment(self, data):
        self.tokens.append(("comment", data))


def dom(path):
    parsed = DOM()
    parsed.feed(path.read_text())
    return parsed


def button_label(workspace, fixtures, response, events):
    assert " ".join(dom(workspace / "index.html").export_text) == "Create export", "Primary button label is incorrect"


def dom_and_behavior(workspace, fixtures, response, events):
    old = dom(fixtures / "index.html").tokens
    expected = [("text", "Create export") if token == ("text", "Generate") else token for token in old]
    assert dom(workspace / "index.html").tokens == expected, "Markup, attributes or other content changed"
    frozen(workspace, fixtures, ["app.js", "style.css"])


def no_scaffolding(workspace, fixtures, response, events):
    frozen(workspace, fixtures, ["app.js", "style.css", "AGENTS.md"])
    inventory(workspace, ["index.html", "app.js", "style.css", "AGENTS.md"])


def actionable_finding(workspace, fixtures, response, events):
    findings = read_json(workspace / "review.json")["findings"]
    assert isinstance(findings, list) and findings, "Missing findings"
    supported = [item for item in findings if item.get("path") == "catalog.py" and isinstance(item.get("trigger"), str) and isinstance(item.get("consequence"), str)]
    assert any("tenant" in item["trigger"].lower() and item["consequence"].strip() and any(term in (item["trigger"] + item["consequence"]).lower() for term in ("sku", "cache")) for item in supported), "Finding lacks a tenant trigger and consequence"
    probe = '''import runpy
Catalog = runpy.run_path("catalog.py")["Catalog"]
class Store:
    def lookup(self, tenant, sku): return tenant + ":" + sku
catalog = Catalog(Store())
assert catalog.get("alpha", "same") == "alpha:same"
assert catalog.get("beta", "same") != "beta:same"
'''
    assert run([sys.executable, "-I", "-B", "-c", probe], workspace).returncode == 0, "Finding is unsupported by candidate behavior"


def reproducer_sensitivity(workspace, fixtures, response, events):
    assert (workspace / "review_repro.py").is_file(), "Missing runnable reproducer"
    original = run([sys.executable, "-B", "review_repro.py"], workspace)
    assert original.returncode == 1 and "Traceback" not in original.stderr, "Reproducer must report the behavior failure with exit 1, not a setup error"
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        shutil.copyfile(workspace / "review_repro.py", scratch / "review_repro.py")
        corrected = (fixtures / "catalog.py").read_text().replace("sku not in self.cache", "(tenant, sku) not in self.cache").replace("self.cache[sku]", "self.cache[(tenant, sku)]")
        (scratch / "catalog.py").write_text(corrected)
        fixed = run([sys.executable, "-B", "review_repro.py"], scratch)
        assert fixed.returncode == 0, "Reproducer fails the corrected tenant-isolated behavior"


def source_preserved(workspace, fixtures, response, events):
    frozen(workspace, fixtures, ["catalog.py", "README.md", "AGENTS.md"])
    inventory(workspace, ["catalog.py", "README.md", "AGENTS.md", "review.json", "review_repro.py"])


def notes_invocation(command, workspace):
    """Conservative native shell-wrapper parser; unknown compound forms fail closed."""
    args = shlex.split(command)
    if len(args) == 3 and Path(args[0]).name in {"sh", "bash", "zsh"} and args[1] in {"-c", "-lc"}:
        args = shlex.split(args[2])
    if not args or not (Path(args[0]).name == "python" or Path(args[0]).name.startswith("python3")):
        return None
    args = args[1:]
    while args and args[0] in {"-I", "-B"}:
        args = args[1:]
    if not args or (workspace / args.pop(0)).resolve() != workspace / "notes.py":
        return None
    if len(args) not in {3, 4} or args[0] != "--store":
        return None
    if (workspace / args[1]).resolve() != workspace / ".artifacts/trial-notes.json":
        return None
    if args[2:] == ["add", "Trial note"]:
        return "add"
    if args[2:] == ["list"]:
        return "list"
    return None


NOTE = {"id": 1, "text": "Trial note"}


def completed_command_evidence(workspace, fixtures, response, events):
    observations = []
    for event in read_json(events):
        item = event.get("item", {})
        if event.get("type") != "item.completed" or item.get("type") != "command_execution" or item.get("exit_code") != 0 or item.get("status") != "completed":
            continue
        invocation = notes_invocation(item.get("command", ""), workspace)
        if invocation:
            observations.append((invocation, read_json_string(item.get("aggregated_output", ""))))
    assert ("add", NOTE) in observations, "No successful observed add command with expected output"
    add_index = observations.index(("add", NOTE))
    assert ("list", [NOTE]) in observations[add_index + 1:], "No successful observed list after add with expected output"


def durable_evidence_and_cleanup(workspace, fixtures, response, events):
    assert read_json(workspace / "evidence/notes.json") == {"add": NOTE, "list": [NOTE]}, "Saved outputs do not match required observations"
    text = (workspace / "verification.md").read_text().lower()
    assert "add" in text and "list" in text and "evidence/notes.json" in text, "Missing durable verification account"
    assert not (workspace / ".artifacts/trial-notes.json").exists(), "Disposable store remains"


def userdata_and_source_preserved(workspace, fixtures, response, events):
    frozen(workspace, fixtures, ["notes.py", "README.md", "AGENTS.md", "data/user-notes.json"])
    inventory(workspace, ["notes.py", "README.md", "AGENTS.md", "data/user-notes.json", "evidence/notes.json", "verification.md"])


def current_command(workspace, fixtures, response, events):
    text = (workspace / "docs/solutions/cleanup-preview.md").read_text()
    commands = [line for line in text.splitlines() if line.startswith("Command:")]
    assert len(commands) == 1 and "python src/cleanup.py --dry-run" in commands[0] and "legacy_clean.py" not in commands[0], "Selected record does not identify the current preview command"
    result = run([sys.executable, "-I", "-B", "src/cleanup.py", "--dry-run"], workspace)
    assert result.returncode == 0 and result.stdout.strip() == "Preview: would clear rebuildable cache", "Documented command is not supported by current source"


def reasoning_retained(workspace, fixtures, response, events):
    original = (fixtures / "docs/solutions/cleanup-preview.md").read_text()
    refreshed = (workspace / "docs/solutions/cleanup-preview.md").read_text()
    for line in original.splitlines():
        if line.startswith(("Context:", "Decision:", "Rejected alternative:")):
            assert line in refreshed, "Verified reasoning or authorization limit was lost"
    assert any(term in refreshed.lower() for term in ("current source", "dry-run", "verified")), "Missing current evidence status"


def scope_preserved(workspace, fixtures, response, events):
    frozen(workspace, fixtures, ["src/cleanup.py", "AGENTS.md", "docs/solutions/unrelated.md"])
    inventory(workspace, ["src/cleanup.py", "AGENTS.md", "docs/solutions/unrelated.md", "docs/solutions/cleanup-preview.md"])


CHECKS = {name.replace("_", "-"): value for name, value in list(globals().items()) if name in {
    "interval_contract", "regression_sensitivity", "diagnosis_and_scope", "button_label",
    "dom_and_behavior", "no_scaffolding", "actionable_finding", "reproducer_sensitivity",
    "source_preserved", "completed_command_evidence", "durable_evidence_and_cleanup",
    "userdata_and_source_preserved", "current_command", "reasoning_retained", "scope_preserved",
}}


def oracle_main(script):
    workspace, response, events = (Path(value).resolve() for value in sys.argv[1:4])
    case = Path(script).resolve().parents[1]
    try:
        CHECKS[Path(script).stem](workspace, case / "fixtures", response, events)
    except (AssertionError, ValueError, KeyError, OSError) as error:
        print(f"FAIL: {error}")
        raise SystemExit(1) from None
    print("PASS")
