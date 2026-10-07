"""Standard-library contracts for the packaged read-only consumer map validator."""
from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/product-development/skills/maintain-verification/scripts/check_feature_map.py"
API = runpy.run_path(str(SCRIPT))


class FeatureMapTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "consumer"
        self.root.mkdir()
        for name in ("README.md", "POLICY.md", "src/notes.py", "src/export.py", "tests/test_notes.py"):
            self.write(name, "Consumer fixture\n")
        self.document = {"schema_version": 1, "features": [{
            "id": "notes-list",
            "behavior": {"source": "README.md", "expected": "List shows stored notes."},
            "entrypoint": "notes CLI list",
            "relevant_files": ["src/notes.py", "tests/test_notes.py"],
            "verification": {"argv": ["python", "-m", "unittest"], "cwd": ".", "prerequisites": [], "evidence": ["evidence/notes.json"]},
            "qualification": {"state": "unverified", "source_revision": None, "environment": None, "reason": "Not run."},
        }]}

    def write(self, name, body):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    @property
    def feature(self):
        return self.document["features"][0]

    def check(self, changed=()):
        return API["validate_feature_map"](self.document, self.root, changed)

    def cli(self, document=None, changed=()):
        path = self.write("feature-map.json", json.dumps(self.document if document is None else document))
        args = [sys.executable, "-I", "-B", str(SCRIPT), str(path), "--root", str(self.root)]
        for name in changed:
            args.extend(["--changed-path", name])
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return result, json.loads(result.stdout)

    def test_valid_unexecuted_map_has_missing_planned_receipt_and_no_behavior_proof(self):
        report = self.check()
        self.assertTrue(report["valid"])
        self.assertFalse(report["qualification_verified"])
        self.assertFalse(report["coverage_complete"])
        self.assertEqual(report["features"], [{"id": "notes-list", "declared_state": "unverified", "current_qualification": "unverified", "stale_candidate": False, "affected_by": [], "missing_planned_evidence": ["evidence/notes.json"]}])
        self.assertFalse((self.root / "evidence").exists())

    def test_declared_pass_and_failure_need_provenance_and_receipt_but_do_not_prove_behavior(self):
        self.write("evidence/notes.json", '{"result":"a deliberately untrusted claim"}')
        for state in ("passed", "failed"):
            with self.subTest(state=state):
                self.feature["qualification"].update(state=state, source_revision="fixture-v1", environment="local", reason="Observed result; limits retained.")
                report = self.check()
                self.assertTrue(report["valid"])
                self.assertEqual(report["features"][0]["declared_state"], state)
                self.assertEqual(report["features"][0]["current_qualification"], "unverified")
                self.assertFalse(report["qualification_verified"])

    def test_qualified_state_requires_all_receipts(self):
        self.feature["qualification"].update(state="passed", source_revision="fixture-v1", environment="local")
        report = self.check()
        self.assertFalse(report["valid"])
        self.assertEqual(report["errors"][0]["field"], "features[0].verification.evidence[0]")

    def test_qualified_state_does_not_allow_unknown_source_or_environment(self):
        self.write("evidence/notes.json", "{}")
        for state in ("passed", "failed"):
            for field in ("source_revision", "environment"):
                with self.subTest(state=state, field=field):
                    self.feature["qualification"].update(state=state, source_revision="fixture-v1", environment="local")
                    self.feature["qualification"][field] = None
                    report = self.check()
                    self.assertFalse(report["valid"])
                    self.assertEqual(report["errors"][0]["field"], "features[0].qualification." + field)

    def test_unverified_allows_known_provenance_but_reason_is_always_required(self):
        self.feature["qualification"].update(source_revision="fixture-v1", environment="local")
        self.assertTrue(self.check()["valid"])
        for state in ("passed", "failed", "unverified"):
            with self.subTest(state=state):
                self.feature["qualification"].update(state=state, reason="")
                self.assertFalse(self.check()["valid"])

    def test_invalid_shapes_are_reported_without_executing_or_throwing(self):
        replacements = [
            (lambda doc: doc.update(schema_version=True)),
            (lambda doc: doc.update(extra="unexpected")),
            (lambda doc: doc.update(features=[])),
            (lambda doc: doc["features"][0].update(id="unstable ID")),
            (lambda doc: doc["features"][0].update(behavior="README.md")),
            (lambda doc: doc["features"][0]["verification"].update(argv=[])),
            (lambda doc: doc["features"][0]["verification"].update(prerequisites="Python")),
            (lambda doc: doc["features"][0]["qualification"].update(state=["passed"])),
            (lambda doc: doc["features"].append(copy.deepcopy(doc["features"][0]))),
        ]
        for mutate in replacements:
            with self.subTest(mutate=mutate):
                document = copy.deepcopy(self.document)
                mutate(document)
                self.assertFalse(API["validate_feature_map"](document, self.root)["valid"])

    def test_missing_policy_product_and_harness_references_are_not_silently_omitted(self):
        for field, missing in (("source", "missing-policy.md"), ("relevant_files", ["src/missing.py"]), ("cwd", "missing-directory")):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                if field == "source":
                    document["features"][0]["behavior"][field] = missing
                elif field == "cwd":
                    document["features"][0]["verification"][field] = missing
                else:
                    document["features"][0][field] = missing
                report = API["validate_feature_map"](document, self.root)
                self.assertFalse(report["valid"])
                self.assertIn("does not exist", report["errors"][0]["message"])

    def test_explicit_policy_product_and_harness_changes_select_only_mapped_features(self):
        other = copy.deepcopy(self.feature)
        other.update(id="export", relevant_files=["src/export.py"])
        other["behavior"]["source"] = "POLICY.md"
        self.document["features"].append(other)
        for changed in ("README.md", "src/notes.py", "tests/test_notes.py"):
            with self.subTest(changed=changed):
                report = self.check([changed])
                self.assertEqual(report["affected_features"], ["notes-list"])
                self.assertEqual(report["features"][0]["affected_by"], [changed])
                self.assertEqual(report["features"][0]["declared_state"], "unverified")
                self.assertTrue(report["valid"])
        self.assertEqual(self.check(["unmapped-deleted.py"])["affected_features"], [])
        self.assertFalse(self.check(["unmapped-deleted.py"])["coverage_complete"])

    def test_directory_entries_and_changed_ancestors_conservatively_match(self):
        self.feature["relevant_files"] = ["src"]
        self.assertEqual(self.check(["src/deleted.py"])["affected_features"], ["notes-list"])
        self.feature["relevant_files"] = ["src/notes.py"]
        self.assertEqual(self.check(["src"])["affected_features"], ["notes-list"])
        self.assertEqual(self.check(["src-other/notes.py"])["affected_features"], [])

    def test_deleted_directly_mapped_product_file_remains_affected_and_invalid(self):
        (self.root / "src/notes.py").unlink()
        report = self.check(["src/notes.py"])
        self.assertFalse(report["valid"])
        self.assertEqual(report["errors"][0]["field"], "features[0].relevant_files[0]")
        self.assertEqual(report["affected_features"], ["notes-list"])
        self.assertTrue(report["features"][0]["stale_candidate"])
        self.assertEqual(report["features"][0]["affected_by"], ["src/notes.py"])

    def test_deleted_accepted_behavior_source_remains_affected_and_invalid(self):
        (self.root / "README.md").unlink()
        report = self.check(["README.md"])
        self.assertFalse(report["valid"])
        self.assertEqual(report["errors"][0]["field"], "features[0].behavior.source")
        self.assertEqual(report["affected_features"], ["notes-list"])
        self.assertTrue(report["features"][0]["stale_candidate"])
        self.assertEqual(report["features"][0]["affected_by"], ["README.md"])

    def test_accepted_source_rename_selects_old_path_until_mapping_is_repaired(self):
        new = self.root / "docs/accepted-policy.md"
        new.parent.mkdir()
        (self.root / "README.md").rename(new)
        changed = ["README.md", "docs/accepted-policy.md"]
        report = self.check(changed)
        self.assertFalse(report["valid"])
        self.assertEqual(report["affected_features"], ["notes-list"])
        self.assertEqual(report["features"][0]["affected_by"], ["README.md"])
        self.feature["behavior"]["source"] = "docs/accepted-policy.md"
        repaired = self.check(changed)
        self.assertTrue(repaired["valid"])
        self.assertEqual(repaired["affected_features"], ["notes-list"])
        self.assertEqual(repaired["features"][0]["affected_by"], ["docs/accepted-policy.md"])

    def test_unsafe_declared_reference_is_not_retained_for_change_matching(self):
        (self.root / "src/linked").symlink_to(self.root.parent / "outside", target_is_directory=True)
        self.feature["relevant_files"] = ["src/linked/deleted.py"]
        report = self.check(["src"])
        self.assertFalse(report["valid"])
        self.assertIn("Symlink", report["errors"][0]["message"])
        self.assertEqual(report["affected_features"], [])

    def test_affected_declared_pass_is_stale_candidate_without_behavior_failure_inference(self):
        self.write("evidence/notes.json", "{}")
        self.feature["qualification"].update(state="passed", source_revision="old-fixture", environment="local")
        report = self.check(["src/notes.py"])
        self.assertTrue(report["valid"])
        self.assertTrue(report["features"][0]["stale_candidate"])
        self.assertEqual(report["features"][0]["declared_state"], "passed")
        self.assertEqual(report["features"][0]["current_qualification"], "unverified")

    def test_absolute_traversal_and_nonportable_paths_are_invalid(self):
        for value in ("/etc/passwd", "../outside", "src/../README.md", "src//notes.py", "src/./notes.py", "C:\\secret", "src\\notes.py", "."):
            with self.subTest(value=value):
                self.feature["behavior"]["source"] = value
                self.assertFalse(self.check()["valid"])

    def test_existing_symlink_components_are_rejected_in_source_cwd_and_planned_evidence(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "policy.md").write_text("Outside scope")
        (self.root / "linked").symlink_to(outside, target_is_directory=True)
        for field, value in (("source", "linked/policy.md"), ("cwd", "linked"), ("evidence", ["linked/planned/missing.json"])):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                parent = document["features"][0]["behavior" if field == "source" else "verification"]
                parent[field] = value
                report = API["validate_feature_map"](document, self.root)
                self.assertFalse(report["valid"])
                self.assertIn("Symlink", report["errors"][0]["message"])

    def test_deleted_changed_path_under_dangling_symlink_is_unusable_input(self):
        (self.root / "linked").symlink_to(self.root.parent / "missing", target_is_directory=True)
        with self.assertRaises(API["MapInputError"]):
            self.check(["linked/deleted.py"])
        result, report = self.cli(changed=["linked/deleted.py"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("input_error", report)

    def test_planned_receipt_parent_must_be_directory(self):
        self.feature["verification"]["evidence"] = ["README.md/planned.json"]
        report = self.check()
        self.assertFalse(report["valid"])
        self.assertIn("parent", report["errors"][0]["message"])

    def test_cli_reports_valid_invalid_and_unusable_inputs_separately(self):
        result, report = self.cli()
        self.assertEqual(result.returncode, 0)
        self.assertTrue(report["valid"])
        result, report = self.cli({"schema_version": 2, "features": []})
        self.assertEqual(result.returncode, 1)
        self.assertTrue(report["errors"])
        path = self.write("feature-map.json", '{"schema_version":1,"schema_version":2,"private":"DO_NOT_ECHO_THIS"}')
        result = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), str(path), "--root", str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("DO_NOT_ECHO_THIS", result.stdout + result.stderr)

    def test_command_arrays_are_never_executed_and_consumer_files_are_unchanged(self):
        self.feature["verification"]["argv"] = [sys.executable, "-c", "from pathlib import Path; Path('UNAUTHORIZED').write_text('mutation')"]
        map_path = self.write("feature-map.json", json.dumps(self.document))
        before = {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        report = API["inspect_feature_map"](map_path, self.root, ["src/notes.py"])
        self.assertTrue(report["valid"])
        after = {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.root / "UNAUTHORIZED").exists())


if __name__ == "__main__":
    unittest.main()
