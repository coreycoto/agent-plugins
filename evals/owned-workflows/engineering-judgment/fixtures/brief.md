# Synthetic engineering decisions

These independent cases are not facts about an operational repository.

A. An ugly, stable report formatter has changed once in three years. Upcoming
work only changes its label. A generated schema file accounts for most churn.
No report correctness incident or relevant feature limitation is documented.

B. Three public clients must each call load, validate, claim and publish in the
same order. A proposed refactor creates four smaller helper modules but leaves
that coordination in every caller. Partial publication must remain observable.

C. Two source loops look similar: one consumes immutable revisions and the other
consumes replaceable snapshots. Snapshot rows absent from a new full snapshot
must be retired; absence in a revisions batch must not retire an entity.

D. A helper costs 2 ms within a 2 s request. Under load, elapsed time rises while
CPU utilization stays low, queue age increases, and client timeouts generate
additional attempts. No trace yet locates the server-side wait or proves a cause.

E. A pure planner reads free capacity and later an executor claims it. Two
callers can plan against the same observation. The accepted rule permits at
most one committed owner. There is no atomicity guarantee connecting planning
to apply; no claim about an actual race reproduction has been made.

F. Index and metrics workers independently update last_indexed and last_sampled
through read-modify-write operations on one status.json file. Readers accept the
most recent independent value for each field; there is no atomic-snapshot or
cross-field invariant. A proposed repair introduces a distributed lock service.

G. Two workers reserve units from one capacity pool. The accepted contract is
at most one active owner per unit. A proposal replaces the shared conditional
claim with separate per-worker files, each recording that worker's view of free
capacity. There is no merge-time conflict check before work starts, and no
existing mechanism makes the separate claims atomic with each other.

Assess only the named case. Do not change files or invent requirements, runtimes,
measurements, authors' motives or approvals. A no-structural-change recommendation
is valid when supported. The final response is the only requested output.
