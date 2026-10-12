# Asynchrony, persistence and truthful recovery claims

Source basis: GOOS chs. 25-27; Meszaros Persistent Fixture Management, Erratic Test
and database patterns; Continuous Delivery chs. 8/12. See [source map](sources.md).
Crash-point matrices and restart classifications below are modern adaptations.

## Separate policy from scheduling without erasing scheduling

Test deterministic decision logic synchronously when possible, with explicit
clock/event inputs. Keep separate tests of the real scheduling, synchronization,
transport and storage semantics. Passing pure rule tests cannot establish a race
is fixed. Conversely, brute-force stress is not the only way to test a rule.
Use barriers, controlled completions and repeatable schedules to expose a known
race. Stress adds different evidence and is not an exhaustive proof.

Await the actual operation and propagate task errors. Use bounded observation
that succeeds as soon as the required condition is observed, rather than a fixed
sleep followed by a guess. Preserve the last observed state for diagnostics.
Artificial time is useful only when the relevant timers and scheduling effects
are actually under that clock's control.

## Avoid false asynchronous passes

GOOS ch. 27 distinguishes sampling from recording notifications. Sampling can
miss intermediate states that were overwritten; a correctly scoped event record
can preserve them. Choose according to what the assertion must establish.

A final value equal to the initial value can pass before processing starts.
Observe a meaningful intermediate transition or completion evidence before
asserting return to the initial state. For an action that should have no effect,
first establish that the tested work was processed. A later marker is a valid
fence only if the processing-order contract prevents it from overtaking that work.
In a parallel system, use the relevant completion/settlement boundary instead.
Do not impose ordering merely to make the test pass.

Name synchronization separately from business assertions. Removing an apparently
redundant wait can introduce a runaway test. Negative assertions need a stated
observation horizon or completed-work boundary, not a claim that an event can
never happen because it was absent for a few milliseconds.

## Make transaction boundaries observable

Use real commits for commit-time constraints, committed visibility, rollback
behavior and independent-connection reads. Flush/clear an ORM cache or reopen a
handle when needed to avoid reading the same in-memory object. A surrounding
rollback transaction can isolate some tests but cannot prove behavior on commit.
An in-memory database may be real SQL, yet lack the production engine's semantics.
State exactly which engine, adapter and configuration were exercised.

Test relevant failures immediately before and after the mutation/commit. Verify
both expected changes and forbidden partial effects. Use a fresh connection for
visibility assertions; reset only owned data. Initialize a known state at the
start and preserve diagnostic evidence before cleanup. Handle foreign-key order,
listeners and in-flight tasks explicitly.

## Name the restart boundary precisely

| Actual experiment | Supported claim |
| --- | --- |
| Rebuild a JS/Python object over the same fake | Component reinitialization only |
| Close/reopen a real database handle in one process | Persistence across handle reopen |
| Stop/start the process with durable storage retained and fresh volatile scratch | Recovery across that process boundary |
| Restart an actual isolate/container with its configured persistence | Recovery at that local native lifecycle boundary |
| Exercise deployed provider identity, bindings and lifecycle | Bounded hosted acceptance under those conditions |

A parent that retains results, ownership or fake executor state can accidentally
supply information the restarted system lost. Inventory what survives and why.
A cooperative exception is not equivalent to abrupt termination; an actual kill
without exercising the relevant commit window is not sufficient either. Exercise
the claimed failure and report its limits.

Require progress as well as safety: unknown acceptance must not duplicate an
effect, but valid recovery evidence should eventually settle the operation within
the accepted conditions. Retrying a test, increasing production deadlines or
serializing all work can hide the bug rather than repair it. Preserve product
retry/authorization rules and use [workflow verification](data-workflows.md) for
multi-system effects.
