# Optional consumer feature map

Use the consumer's existing convention first. This small JSON contract is useful
when maintaining selected feature-to-command mappings is the assigned task. It
is not a complete product inventory, command runner or new runtime dependency.
Keep the map and product-specific commands in the consumer repository.

A version 1 map has exactly `schema_version` and `features`. Each feature has:

```json
{
  "schema_version": 1,
  "features": [{
    "id": "notes-list",
    "behavior": {
      "source": "README.md",
      "expected": "List returns only the notes stored in the selected disposable store."
    },
    "entrypoint": "notes CLI list command",
    "relevant_files": ["notes.py", "tests/test_notes.py"],
    "verification": {
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests"],
      "cwd": ".",
      "prerequisites": ["Python and the consumer test fixture are available."],
      "evidence": ["evidence/notes-list.json"]
    },
    "qualification": {
      "state": "unverified",
      "source_revision": null,
      "environment": null,
      "reason": "Planned command; not executed against this revision."
    }
  }]
}
```

Use a stable lowercase identifier with digits and `-`, `.`, or `_` separators
(maximum 80 characters). `behavior.source` names an existing accepted-behavior
file; `expected` identifies the observable result. The map does not establish
that current code or that file is accepted policy. `entrypoint` names the user
surface. `relevant_files` is a nonempty list of existing files or directories;
include policy, product and harness dependencies needed for change selection.
Directory entries conservatively cover descendants. No match means only that
these explicit mappings did not match, not that a changed path is harmless.

`verification.argv` is a nonempty argument array, `cwd` is an existing directory,
and `prerequisites` contains descriptive requirements (possibly none). Never put
credentials or raw logs in the map. This validator stores no receipt and executes
no command. An authorized executor must separately check prerequisites, task
permissions, instance identity and the [verification guide](../../_shared/references/product-verification.md).
`evidence` is a nonempty array of consumer-relative receipt paths; planned output
parents may be absent. Qualification state is `unverified`, `passed` or `failed`,
with a nonempty reason. Unverified source/environment may be null; passed/failed
require nonempty source revision/artifact and environment plus existing evidence
files. Existing receipts and declared states do not prove behavior or freshness.

All path references are relative to the explicitly supplied consumer root, with
no absolute paths, traversal, backslashes, colons or symlink components. `.` is
allowed only for `cwd`. Referenced policy, product and harness paths must exist;
explicit changed paths may be deleted. Rename analysis should supply both old
and new paths and repair missing mappings rather than omit them.

Run the contained script using its actual installed path:

```sh
python -B /actual/skill/path/scripts/check_feature_map.py consumer-feature-map.json \
  --root /explicit/consumer/root --changed-path notes.py
```

Exit 0 means the map and references are valid, 1 means schema/reference problems,
and 2 means unusable JSON/root/changed-path input. JSON reports `declared_state`
separately from `current_qualification: "unverified"`; `qualification_verified`
and `coverage_complete` remain false. Explicit changes touching policy or
`relevant_files` mark `stale_candidate` and list affected IDs. This requests
selected revalidation; it neither invalidates accepted behavior nor executes it.

For qualification, execute the authorized command through available host tools,
retain action/result and independent acceptance evidence before owned cleanup,
and record the tested revision/environment and limitations. Refresh affected
entries using current source and accepted policy. Preserve original failures;
report missing prerequisites as unverified and observed behavior failures as
failed. A source change, stale candidate or old timestamp alone is neither a
product failure nor proof of a successful current run.
