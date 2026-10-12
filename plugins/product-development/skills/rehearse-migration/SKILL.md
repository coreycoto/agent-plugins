---
name: rehearse-migration
description: Exercise a planned schema, API, persisted-state, or component migration through supported intermediate versions, interruption, and recovery in an isolated environment before rollout.
---

# Rehearse Migration

Use when persistent representations or independently changing consumers must
survive a transition. A local extraction without cross-version implications
belongs in `phased-refactor`. Resolve the accepted migration, old/new artifacts,
consumer contracts, permitted scratch environment and requested output from
source. Planning belongs in `design-change`; a rehearsal needs executable steps.

Derive the compatibility matrix from the actual rollout: producers, consumers,
schemas, queued messages and in-flight owners that can coexist. Do not assume
every theoretical combination must be supported. Explicitly identify excluded
combinations and the rollout mechanism that prevents them. Use the
[transition guide](references/transition-evidence.md) for intermediate-state and
recovery cases. Missing rollout decisions remain visible.

Create owned isolated fixtures using the real migration and relevant reader/
writer entrypoints. Include representative historical records, boundary values
and permitted post-upgrade writes. Record fixture provenance, versions and
configuration. Do not copy production data or invoke hosted operations without
that scope and access; synthetic evidence remains labeled.

Execute the intended sequence. At meaningful checkpoints, test reads and writes
from each supported version; interrupt and resume where partial work is possible.
Exercise actual commit boundaries and fresh connections/processes when the claim
requires them. Check data meaning, identities, units, constraints and retained
progress, not only row counts or command success. Keep expected outcomes
independent of the transformation being rehearsed.

Exercise the proposed recovery path as well as forward success. Distinguish
binary reversion, schema reversal, backup restore and forward repair. Determine
what happens to writes made after a backup or after the new version starts.
State an irreversible point and the required next action rather than promise
rollback that discards accepted data. A rehearsal does not authorize that action.

Complete with source/artifact identity, supported and excluded combinations,
commands, observed intermediate results, semantic comparisons, interruption and
recovery evidence, untested prerequisites and stop conditions. Retain evidence
before cleaning only owned scratch. Describe an unexecuted plan as a plan;
passing the destination alone is not a successful transition rehearsal. Keep
live deployment, migration and publication in the consumer's approved workflow.
