# Dataset fitness contract

Assess survey-snapshot-1 for a region-complete area inventory. population.json
is the independently accepted source population; discovered.json is only the
pipeline's own discovery/processing receipt. Check the entire six-row snapshot.
A source/id/revision triple is unique. Successive revisions for an entity are
valid, not duplicates. Areas must be nonnegative with unit sqft or sqm. Zero is
valid. A blank area is permitted only for status not-reported. Do not convert
unknown units, deduplicate or rewrite records.

There is no freshness threshold and no independent reference for external accuracy.
Report these as unverified. Create only assessment.py and evidence.json, leaving
all input files unchanged. Run `python -B assessment.py`. Evidence must include
`dataset_id`, `missing_sources`, `duplicate_keys` (colon-delimited triples),
`invalid_unit_keys`, `invalid_area_keys`, `rows_examined`, `expected_source_count`,
`freshness_verified` (bool) and `external_accuracy_verified` (bool).
Final conclusions must distinguish legitimate revisions, null exceptions and zero
from defects, and processing completeness from geographic/source completeness.

Print the same evidence JSON to stdout from the task entrypoint. The evaluation
runner records command completion separately from the files you write.
