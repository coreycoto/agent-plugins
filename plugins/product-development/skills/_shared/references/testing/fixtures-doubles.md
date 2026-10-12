# Fixtures, test doubles and test-support design

Source basis: Meszaros chs. 8-13/18/20/22-26; GOOS chs. 8/20/22/25;
Beck Isolated Test and Test Data. See [source map](sources.md).

## Choose dimensions independently

A **Minimal Fixture** contains what the condition requires. A **Standard Fixture**
reuses a design. A **Fresh Fixture** creates an instance for one test. A **Shared
Fixture** reuses the same instance. Standard does not imply shared, and shared
setup code does not require shared mutable state.

Prefer fresh mutable state unless measured setup cost justifies a different
strategy. Share immutable expensive input or infrastructure only with explicit
ownership, reset/namespace rules and a test showing isolation. A rollback fixture
is unsuitable when commit, another connection or restart is the behavior at issue.

Use in-line setup when the few lines explain the case. Use Delegated Setup,
Creation Methods or Test Data Builders to hide irrelevant mechanics. Do not hide
the specific revision, tenant, amount or failure point that causes the assertion.
Prefer a named small builder over a universal factory with unrelated flags.
Use valid typed defaults; invalid-input cases should change one relevant field
or explicitly cross an `unknown`/wire boundary. Do not cast every valid fixture
into an incompatible production type to silence drift.

## Select a double for its job

| Double | Role | Review question |
| --- | --- | --- |
| Dummy | Required but unused argument | Would execution accidentally use it? |
| Stub | Controlled indirect inputs | Are statuses/errors/envelopes faithful? |
| Spy | Records indirect outputs | Is the observed effect part of the contract? |
| Mock | Verifies expected collaboration | Are expectations essential or incidental? |
| Fake | Lightweight working replacement | Which real semantics does it omit? |

GOOS's owned-adapter approach lets the application speak its domain while
focused integration tests check the third-party API. Use that where it reduces
coupling. Do not wrap every value type or standard library solely for a pattern.
The book allows limited external mocking for difficult failures; preserve the
real adapter tests instead of treating the exception as complete integration proof.

A fake storage service should not decide the same business rule as the SUT.
For example, an in-memory map can supply bytes; it cannot establish real transaction
isolation, conditional-write behavior or process durability. Contract-check a
reused fake against the real adapter for the semantics tests rely on. List remaining
differences rather than claiming interchangeable fidelity.

## Prevent fixture leakage

Avoid process-global permissive authorization/fetch mocks. Match only the intended
request and let unrelated cases reach their proper behavior. Restore patches,
clocks, random seeds, environment, module state and current directories after
success or failure. Scope listeners and pending tasks to the test; drain or cancel
them before disposing their resources. Unique temp paths and namespaces must not
be hardcoded to one operating system or silently share a developer's state.

A test should pass alone and in relevant alternative orders. Use reversed/randomized
order and parallel runs where that execution mode is supported and meaningful.
A fixed favorable order is not an isolation repair. Repeated success does not
prove the absence of races; retain the controlled regression scenario.

## Treat helpers as code worth testing

Test custom assertions with both matching and mismatching values. Confirm that
builders create independent nested values, not shallow copies of shared mutation.
Check cleanup after setup failure, timeout and test failure. Keep diagnostics:
expected versus actual, case identity, meaningful state and bounded error details.
Do not suppress the original failure with cleanup exceptions.

Own reusable support near the relevant capability; promote it only when multiple
real consumers need a stable contract. Avoid imports from another package's
private test tree and avoid a root helper that depends on every domain. This is
an ownership/design investigation, not an automatic ban on all cross-package
fixtures. Make the chosen dependency intentional, typed and acyclic.
