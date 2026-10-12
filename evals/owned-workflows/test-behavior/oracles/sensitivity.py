"""Frozen grader for the checkout test-design task; not an agent runtime tool."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EXPECTED_FILES = {"checkout.py", "test_checkout.py", "policy.md"}
HARNESS = """
import json, pathlib, sys, unittest
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root))
suite = unittest.defaultTestLoader.discover(str(root), pattern='test_checkout.py')
result = unittest.TextTestRunner(verbosity=0).run(suite)
(root / 'result.json').write_text(json.dumps({
    'run': result.testsRun, 'failures': len(result.failures),
    'errors': len(result.errors), 'skipped': len(result.skipped),
    'success': result.wasSuccessful()
}))
sys.exit(0 if result.wasSuccessful() else 1)
"""


def product_files(workspace: Path) -> set[str]:
    """The trial runtime independently checks its .agents skill closure."""
    return {
        path.relative_to(workspace).as_posix()
        for path in workspace.rglob("*")
        if (path.is_file() or path.is_symlink())
        and path.relative_to(workspace).parts[0] != ".agents"
        and "__pycache__" not in path.relative_to(workspace).parts
    }


def run_variant(tests: str, source: str) -> dict[str, object]:
    """Run untrusted submitted tests only on a disposable evaluation host."""
    with tempfile.TemporaryDirectory(prefix="testing-oracle-") as directory:
        root = Path(directory)
        (root / "checkout.py").write_text(source, encoding="utf-8")
        (root / "test_checkout.py").write_text(tests, encoding="utf-8")
        env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT") if key in os.environ}
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", HARNESS, str(root)],
                cwd=root, env=env, capture_output=True, text=True, timeout=8, check=False,
            )
        except subprocess.TimeoutExpired:
            return {"kind": "timeout"}
        result_file = root / "result.json"
        if not result_file.is_file():
            return {"kind": "no-result", "exit": completed.returncode}
        try:
            result = json.loads(result_file.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            return {"kind": "invalid-result"}
        if (not isinstance(result, dict)
                or any(type(result.get(key)) is not int or result[key] < 0
                       for key in ("run", "failures", "errors", "skipped"))
                or type(result.get("success")) is not bool):
            return {"kind": "invalid-result"}
        return {"kind": "completed", "exit": completed.returncode, **result}


def assess_workspace(workspace: Path) -> list[str]:
    """Return demonstrated task failures; never change the submitted workspace."""
    if product_files(workspace) != EXPECTED_FILES:
        return ["Only the assigned test file may change; unexpected or missing product files."]
    for name in EXPECTED_FILES:
        if (workspace / name).is_symlink():
            return ["Submitted product files must not be symlinks."]
    for name in ("checkout.py", "policy.md"):
        if (workspace / name).read_bytes() != (FIXTURES / name).read_bytes():
            return [f"Fixed evidence changed: {name}."]
    tests = (workspace / "test_checkout.py").read_text(encoding="utf-8")
    original = (FIXTURES / "checkout.py").read_text(encoding="utf-8")
    corrected = original.replace("subtotal_cents > 5000", "subtotal_cents >= 5000")
    variants = {
        "corrected-control": (corrected, True),
        "boundary-defect": (original, False),
        "member-defect": (corrected.replace("member or ", ""), False),
        "shipping-defect": (corrected.replace(
            "shipping_cents = 0 if member or subtotal_cents >= 5000 else 500",
            "shipping_cents = 0"), False),
        "subtotal-defect": (corrected.replace(
            "return subtotal_cents + shipping_cents",
            "return 2 * subtotal_cents + shipping_cents"), False),
    }
    failures = []
    for name, (source, should_pass) in variants.items():
        result = run_variant(tests, source)
        valid = (result.get("kind") == "completed" and result.get("run", 0) > 0
                 and result.get("errors") == 0 and result.get("skipped") == 0)
        demonstrated = (
            result.get("success") is True and result.get("failures") == 0
            and result.get("exit") == 0
        ) if should_pass else (
            result.get("success") is False and result.get("failures", 0) > 0
            and result.get("exit") == 1
        )
        if not valid or not demonstrated:
            failures.append(f"{name}: expected {'pass' if should_pass else 'assertion detection'}, got {result}.")
    return failures


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: sensitivity.py WORKSPACE RESPONSE_PATH EVENTS_PATH")
    failures = assess_workspace(Path(sys.argv[1]).resolve())
    for failure in failures:
        print(f"FAIL: {failure}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
