# Decide whether actors need shared mutable state

Use when a proposed design coordinates concurrent writes. Identify the actual
invariant and write target before choosing a lock, queue or coordinator.

Ask whether actors publish independent facts or must update one canonical object.
Independent diagnostic results or worker checkpoints may use separately owned
files, keys or branches, combined at a read/reporting boundary. Two fields in one
read-modify-written JSON file still share a write target. Splitting the files is
useful only when the reader can tolerate their independent versions.

Preserve real cross-actor obligations. A capacity claim, unique owner, ordered
ledger or all-or-nothing snapshot may require shared serialization or an atomic
publication boundary. Separate files alone do not establish uniqueness,
consistency or atomic visibility. Compare a transaction, conditional write,
single owner or existing lock with partitioning; use actual storage semantics.

For either choice, name ownership, reader consistency, identity, interruption,
reconciliation and the merge/publication boundary. Apply
[check-protocol](../../../check-protocol/SKILL.md) when the competing executions
need exploration, including the real atomic boundary. Eliminating an unnecessary
shared target can remove a race; it is not proof that all coordination disappears.

Use consumer-supported isolation and available tools. A recommendation to split
state does not authorize changing storage, creating worktrees, migrating data or
editing another actor's files. Keep the chosen design and its evidence in the
existing task artifact. See the [source/adaptation record](sources.md).
