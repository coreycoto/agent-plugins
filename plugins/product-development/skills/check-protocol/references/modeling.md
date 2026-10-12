# Model the protocol, not the hoped-for execution

Start with one disputed obligation and a small number of actors or identities.
Use representative values only when the abstraction preserves the property.
Retain the assumptions connecting the model to the actual protocol. A model
can simplify payload bytes without collapsing distinct attempts into one owner.

## State and events

Separate a worker's local belief from what a receiver has durably accepted.
A lost reply can leave those states different. Crashes erase only the volatile
state of the actors actually restarted; model recovery from persisted evidence.
If checking a claim-and-write race, separate the read, claim and effect unless
one actual transaction or operation makes them indivisible. A sequential model
that makes the disputed race atomic cannot establish its absence.

Keep safety predicates independent of next-state logic where feasible. Useful
questions include whether two owners can commit the same protected effect,
whether an old attempt can terminalize a new one, and whether publication can
precede complete verified inputs. These are examples, not automatic contracts.

## What a completed check means

Record constants, initial states, transitions, enabled properties, reductions,
constraints and resource limits. Inspect the checker's actual completion and
output, not just a zero exit or a file containing an invariant definition.
A timeout or state limit is an incomplete search. A depth-limited search proves
only the stated bounded claim. Random simulation is not exhaustive exploration.
Finite reachability can establish safety for that model; a path to completion
establishes possibility, not eventual progress on every allowed execution.

Deadlock, stuttering and livelock are different. Terminal states may legitimately
have no outgoing work. Explain any disabled deadlock check. For liveness, retain
fairness and recovery/delivery assumptions and actually enable temporal checking.
Do not add fairness that assumes the property being investigated. For TLC,
inspect the selected specification and INVARIANT/PROPERTY entries; declaring a
formula alone does not enable it. See the [TLC configuration reference](https://learning.tlapl.us/intro/tlc-config/).

## Sensitivity and implementation correspondence

Check reachability of the risky state before trusting a pass. Loosen a meaningful
guard in an isolated model and confirm a behavioral counterexample, keeping the
oracle unchanged. Also retain a legitimate recovery path so a model that blocks
all useful work cannot look correct merely by avoiding bad states.

Map each modeled action to an implementation operation, commit boundary or
external contract. A trace might be: dispatch, receiver accepts but reply is
lost, deadline expires, second dispatch, second acceptance. Whether that violates
a rule depends on actual idempotency and ownership semantics. Do not infer a
production bug solely from an intentionally simplified model.

Use the consumer's existing evidence location. A short result can name the
model, configuration, bounds, properties, reached states, traces, sensitivity,
real-code mapping and remaining gaps. No new registry or formal-methods platform
is necessary. These are original procedural adaptations; [source scope](../../_shared/references/judgment/sources.md)
distinguishes them from the older books.
