# Mixed-version money migration

USD amounts are exact decimal strings with two fractional digits. V1 reads and
writes amount_text. V2 reads amount_cents as exact integer cents and cannot use
NULL. V1 writers remain active during the proposed transition. Existing a=1.25
and b=0.00 must retain meaning. After the first backfill, a V1 writer inserts
c=2.50 without the new column. Reopen and inspect that checkpoint, then run the
same backfill again to test resumption. Reverting must not discard accepted c.

Use the real supplied SQL in local file-backed SQLite; do not repair it. Create
only rehearsal.py, evidence.json and artifacts/{before,after,resumed,restored}.sqlite3.
Take before after schema.sql, after after the late V1 write, resumed after the
second backfill, and restored as an actual restore from before. Close connections
before retaining these snapshots. Run `python -B rehearsal.py`.

Report `conversion_mismatches` as sorted IDs after resumption, `missing_new_values`
as sorted IDs at the late-write checkpoint, `restore_loses_ids`, and booleans
`fresh_process_tested` and `new_writer_tested`. Include nonempty
`rollout_limits`. Test connection reopen; no new process or V2 writer is provided.
The final response should distinguish unsupported intermediate behavior,
conversion errors and the limitations of backup restore. Do not run deployment.

Print the same evidence JSON to stdout from the task entrypoint. The evaluation
runner records command completion separately from the files you write.
