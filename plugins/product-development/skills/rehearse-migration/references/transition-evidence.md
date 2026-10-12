# Evidence through a transition

Use the rollout's real order, not a generic all-versions checklist. Begin with a
matrix of reader/writer version, stored or wire representation, stage, required
behavior and evidence. Mark a combination excluded only when a verified rollout
constraint prevents it; otherwise it remains an unresolved compatibility risk.

An expand/transition/contract sequence may help, but it is not universal. Test
what makes each intermediate stage safe: defaults, compatibility readers,
backfill rules, dual-write reconciliation or actual quiescence. A declaration
that an old version is gone is not evidence that old jobs and messages drained.

## Choose consequential cases

Include old data with values that distinguish the intended conversion from a
plausible incorrect one. Fractions catch truncation; equal row counts do not.
For backfills, consider new writes, changes to already visited rows, checkpoint
commit order and resumed batches. Repetition must be tested against the real
idempotency and transaction contract, not assumed safe because the tool has a
retry flag. Capture mismatches before any repair or canonicalization hides them.

Test both behavior and data constraints. An additive column can still break an
old writer through NOT NULL, missing defaults or changed validation. A schema
that accepts both versions may still change meaning, such as a unit, timezone,
identity or revision-precedence rule. Include real consumer parsing/serialization
when wire formats change. Gate a removal on evidence that its consumers have
moved, including retained or delayed work.

Use actual migration files and runtime versions in owned fixtures. An in-memory
SQLite rehearsal establishes only its tested SQL behavior; it does not establish
another database's locks, DDL semantics, replication, scale or hosted identity.
Do not call a reopened connection a process restart. Retain the local evidence
and identify a needed native/provider check without silently running it.

## Recovery is not one operation

| Recovery | Question the rehearsal must answer |
| --- | --- |
| Revert the executable | Can it interpret state written by the newer version? |
| Reverse the schema | Which information or relationships would be lost? |
| Restore a backup | How are post-backup accepted writes preserved/reconciled? |
| Forward repair | How is the faulty state detected and corrected safely? |

Different stages may have different recovery paths. Preserve critical new data,
not just an old application image. State backups, write fences, reconciliation,
authority and external dependencies as prerequisites, not observed facts unless
actually exercised. Recovery capacity and duration require representative
measurement; a tiny fixture cannot qualify a large-scale restore.

A concise result records matrix rows, artifacts, pre/post semantic assertions,
checkpoints, failure injection, recovery outcome and unverified combinations.
Use existing consumer evidence conventions. See [source scope](../../_shared/references/judgment/sources.md):
Continuous Delivery's Managing Data chapter is a basis for transition reasoning;
this workflow's full protocol is an original adaptation, not a book quotation.
