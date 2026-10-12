"""Structural and executable grader checks, not measurements of agent usefulness."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/owned-workflows/test-behavior"
REFS = ROOT / "plugins/product-development/skills/_shared/references/testing"
SPEC = importlib.util.spec_from_file_location("testing_sensitivity", SUITE / "oracles/sensitivity.py")
assert SPEC is not None and SPEC.loader is not None
ORACLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLE)
GOOD = """
import unittest
from checkout import invoice_total

class CheckoutTests(unittest.TestCase):
    def test_accepted_examples(self):
        for subtotal, member, expected in [
            (4999, False, 5499), (5000, False, 5000),
            (5001, False, 5001), (100, True, 100), (0, False, 500)
        ]:
            with self.subTest(subtotal=subtotal, member=member):
                self.assertEqual(expected, invoice_total(subtotal, member))
"""


class TestTestingGuidance(unittest.TestCase):
    def assess(self, tests: str, *, change_source: bool = False) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ORACLE.EXPECTED_FILES:
                shutil.copyfile(SUITE / "fixtures" / name, root / name)
            (root / "test_checkout.py").write_text(tests, encoding="utf-8")
            if change_source:
                (root / "checkout.py").write_text("# unrequested rewrite\n", encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            findings = ORACLE.assess_workspace(root)
            after = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            self.assertEqual(before, after, "grader must not mutate submitted artifacts")
            return findings

    def test_independent_tests_detect_all_selected_faults(self):
        self.assertEqual([], self.assess(GOOD))

    def test_circular_oracle_is_rejected(self):
        self.assertTrue(self.assess((SUITE / "fixtures/test_checkout.py").read_text()))

    def test_empty_discovery_is_rejected(self):
        self.assertTrue(self.assess("# no executable tests\n"))

    def test_import_error_is_not_behavioral_detection(self):
        self.assertTrue(self.assess("import nonexistent_example_module\n"))

    def test_syntax_error_is_not_behavioral_detection(self):
        self.assertTrue(self.assess("def broken(:\n"))

    def test_incorrect_control_expectation_is_rejected(self):
        self.assertTrue(self.assess(GOOD.replace("5499", "9999")))

    def test_skipped_tests_are_not_qualification(self):
        self.assertTrue(self.assess(GOOD.replace(
            "class CheckoutTests", "@unittest.skip('avoid failure')\nclass CheckoutTests")))

    def test_unrequested_production_change_is_rejected(self):
        self.assertTrue(self.assess(GOOD, change_source=True))

    def test_symlinked_submission_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ORACLE.EXPECTED_FILES:
                shutil.copyfile(SUITE / "fixtures" / name, root / name)
            (root / "test_checkout.py").unlink()
            (root / "test_checkout.py").symlink_to(SUITE / "fixtures/test_checkout.py")
            self.assertTrue(ORACLE.assess_workspace(root))

    def test_read_only_oracle_checks_actual_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(SUITE / "fixtures/review-scope.md", root / "review-scope.md")
            command = [sys.executable, "-I", str(SUITE / "oracles/unchanged.py"),
                       str(root), str(root / "response.txt"), str(root / "events.json")]
            self.assertEqual(0, subprocess.run(command, capture_output=True, timeout=5).returncode)
            (root / "unexpected.txt").write_text("unrequested change")
            self.assertEqual(1, subprocess.run(command, capture_output=True, timeout=5).returncode)

    def test_corpus_paths_ids_and_grader_separation(self):
        data = json.loads((SUITE / "evals.json").read_text())
        self.assertEqual(3, data["schema_version"])
        self.assertEqual("product-development:test-behavior", data["skill_name"])
        ids = [case["id"] for case in data["evals"]]
        self.assertEqual(len(ids), len(set(ids)))
        for case in data["evals"]:
            self.assertEqual("artifact-safe", case["execution_mode"])
            self.assertTrue(case["prompt"] and case["expected_output"] and case["checks"])
            self.assertTrue(set(case["tiers"]) <= {"smoke", "deep"})
            for item in case["workspace_files"]:
                source = (SUITE / item["source"]).resolve(strict=True)
                self.assertTrue(source.is_relative_to((SUITE / "fixtures").resolve()))
                self.assertFalse(Path(item["path"]).is_absolute())
                self.assertNotIn("..", Path(item["path"]).parts)
            for check in case["checks"]:
                if check["type"] == "assertion":
                    self.assertTrue((SUITE / check["script"]).is_file())
                    self.assertNotIn(check["script"], [x["source"] for x in case["workspace_files"]])
                else:
                    self.assertEqual("rubric", check["type"])
                    self.assertTrue(check["text"])

    def test_trigger_cases_include_positive_and_near_miss(self):
        data = json.loads((SUITE / "trigger_queries.json").read_text())
        self.assertEqual(2, data["schema_version"])
        for split in ("train", "validation"):
            self.assertEqual({True, False}, {
                case["should_trigger"] for case in data["queries"] if case["split"] == split
            })

    def test_reference_links_remain_inside_the_library(self):
        for path in REFS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^\s)]+)\)", text):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve(strict=True)
                self.assertTrue(resolved.is_file())
                self.assertTrue(resolved.is_relative_to(REFS.resolve()))


if __name__ == "__main__":
    unittest.main()
