# Separate decisions from effects when it removes real coupling

Use when a calculation is entangled with time, storage, transport or orchestration.
Identify the data, decisions and effects needed for the actual behavior. Make
inputs explicit only where that creates a useful seam; do not force every helper
through a universal command interpreter or introduce a framework for purity.

For example, calculating which inputs lack a verified checkpoint may be a pure
operation over supplied observations. Acquiring the current observations,
claiming ownership, reading bytes, persisting progress and publishing results
remain effects. Returning a plan does not make its later execution atomic.
State what must be revalidated when the observed world changes before apply.

At boundaries, distinguish values and identities that have different lifetimes.
A source, attempt, observation and artifact are not interchangeable because all
use strings. Tagged states or value types can exclude invalid combinations, but
the type's claim must be earned by a constructor or validator. Untrusted wire and
stored data still require runtime checks. A cast to a trusted type is not proof
of integrity, ownership or freshness.

Keep scheduling, clocks, randomness and external events controllable without
changing the behavior under test. Extract decision logic in behavior-preserving
steps and exercise the actual callers after extraction. Test calculations cheaply;
retain independent tests for serialization, commits, conflicts, process recovery
and external handoffs. A planner test cannot replace an executor test simply
because both execute related code.

Make the extraction earn its cost: simpler callers, fewer duplicated decisions,
clear ownership or better fault localization. Preserve distinct policies rather
than add mode flags to make unrelated cases share one implementation. Shared
mechanics and domain knowledge can have different owners. When pure decisions
already have clear boundaries, leave them alone.

This reference adapts GOOS's separation of functionality from concurrency policy
and the supplied testing literature's design-for-testability concerns. It is not
a full extraction of the newly recommended functional-design books; see
[source scope](sources.md).
