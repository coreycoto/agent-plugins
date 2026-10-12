# Testing and verification decision guide

Use this guide when a testing decision is unresolved, not as a mandatory sequence.
The existing Product Development skills remain the entrypoints. Consumer policy,
current commands, permissions and release gates remain authoritative. These are
original procedures informed by the [six-book source map](sources.md); modern
adaptations are identified there rather than attributed to the older books.

| Current task | Primary skill | Read only the relevant reference |
| --- | --- | --- |
| Add behavior or lock down a regression | `test-behavior` | [Test design](test-design.md) |
| Understand and preserve an unfamiliar implementation | `test-behavior`, then `phased-refactor` | [Legacy change](legacy-refactoring.md) |
| Decide whether a suite provides useful confidence | `maintain-verification` | [Strategy and audit](strategy.md) |
| Reduce fixture, duplication or organization friction | `phased-refactor` | [Fixtures and doubles](fixtures-doubles.md), [suite refactoring](suite-refactoring.md) |
| Change callbacks, concurrency, transactions or recovery | `test-behavior` | [Asynchrony and persistence](asynchrony-persistence.md) |
| Change a data pipeline or distributed lifecycle | `test-behavior`, `phased-refactor` | [Data and workflow adaptation](data-workflows.md) |
| Qualify a built or deployed candidate | `verify-product` | [Delivery evidence](delivery.md) |
| Review test quality and evidence claims | `review-code` | Relevant reference above and [evidence template](evidence-template.md) |

A small understood change normally needs its existing focused tests, not an audit,
new fixture framework, coverage target or extra agent. For an audit, inspect a
bounded capability and report evidence before editing. For implementation, finish
one useful test/code/refactor increment and continue to the authorized endpoint.

## Distinctions to preserve

A specification test checks an accepted requirement. A characterization test
records observed behavior at a fixed baseline. An experiment answers a question.
A passing characterization does not establish desirability; a failed experiment
can still answer its question. Label the purpose before selecting an oracle.

Test purpose, system boundary and execution environment are separate dimensions.
An acceptance test is not necessarily a browser test. A component test may use a
real database. A real database test does not automatically prove process-restart
recovery. Record the relevant distinctions instead of policing names alone.

Execution coverage locates unexercised code, not unproved requirements. Additional
layers earn their cost by detecting different failures. Preserve existing gates;
changing a threshold or exception is a policy decision, not a fixture repair.

## Adoption and evaluation

Keep skill IDs, installation permissions and existing release workflow unchanged.
References ship inside Product Development and do not require access to the books
at runtime. No copyrighted source text or consumer-private fixtures belong here.
A source change is not a released or actively loaded package. Validate package
containment, build output and session discovery separately.

Evaluate on the actual intended tasks using frozen inputs and independently held
expectations. Compare baseline and candidate at the same tool/model settings,
including tasks where extra process would be wasteful. A deterministic fixture
check does not establish model adherence or effectiveness. Keep grader artifacts
outside the measured workspace; do not tune on a held-out case and still call it
held out. Retain failures, invalid runs, cost and unnecessary edit scope alongside
successful defect detection.
