# Source map and interpretation boundaries

These references identify the supplied editions used for this procedural
synthesis. They are attribution and verification locators, not bundled content
or runtime dependencies. The prose, examples and evaluation fixtures in this
contribution are original. Do not upload the books, their page images, raw text
extractions or private consumer examples into this public repository.

PDF locators below are one-based pages in the supplied files. Some files are
reflowed and do not match print pagination. Chapter titles are the stable lookup.
The study surveyed the six books' organization and catalogs and reread the
relevant sections in detail; it is not a claim of line-by-line rereading of every
page or execution of the books' sample programs.

| Source | Relevant organization and locators | Applied here |
| --- | --- | --- |
| Steve Freeman and Nat Pryce, *Growing Object-Oriented Software, Guided by Tests*, first printing 2009 | Parts I-II, chs. 1-8 (PDF 28-96); Auction Sniper worked example in Part III; chs. 20-24 (PDF 254-310), chs. 25-27 (PDF 314-352) | Nested feedback, walking skeleton, behavior rather than methods, owned adapters, listening to test difficulty, builders, diagnostics, information rather than representation, real transaction boundaries and asynchronous observation |
| Gerard Meszaros, *xUnit Test Patterns: Refactoring Test Code*, 2007 | Narratives chs. 3-6 (PDF 82-136), 8-13 (PDF 148-236); smells chs. 15-17 (PDF 248-336); patterns chs. 18-27 (PDF 340-797). Particularly ch. 12, Organizing Our Tests (PDF 216-228), Minimal Fixture (PDF 365-367), Standard Fixture (PDF 368 onward) | Four-Phase Test, fixture strategy, State/Behavior Verification, test doubles, smell diagnosis, alternative organization patterns, controllability/observability and Humble Object |
| Michael Feathers, *Working Effectively with Legacy Code*, first printing 2004 | Part I chs. 1-5 (PDF 26-77); chs. 6-7 (PDF 80-108), 11-13 (PDF 174-218), 16-18 (PDF 232-252), 20-23 (PDF 268-340); Part III, ch. 25 (PDF 348-437) | Sensing/separation, seams and enabling points, effect reasoning, interception/pinch points, characterization, small dependency-breaking changes, incremental structural recovery |
| Kent Beck, *Test-Driven Development: By Example*, first printing 2002 | Money example, chs. 1-17 (PDF 17-96); xUnit example, chs. 18-24 (PDF 98-123); patterns chs. 25-32 (PDF 126-237), especially Test List/Assert First/Test Data/Evident Data (PDF 130-136) | Red/green/refactor, adjustable step size, isolated tests, choosing the next example, Fake It/Obvious Implementation/Triangulation, testing the test harness itself |
| Martin Fowler et al., *Refactoring: Improving the Design of Existing Code*, 1999 edition | Ch. 1 worked example (PDF 13-45); chs. 2-4 (PDF 46-84); catalog chs. 5-12 (PDF 85-310); chs. 13-15 (PDF 311-335) | Two hats, behavior-preserving mechanics, self-checking tests, risk-focused cases, extraction/movement/interface changes and compiler feedback |
| Jez Humble and David Farley, *Continuous Delivery*, first printing 2010 | Foundations chs. 1-4 (PDF 37-136); pipeline chs. 5-10 (PDF 139-308); ch. 12 Managing Data (PDF 359-377); ch. 13 dependencies/incremental change (PDF 379-413); ch. 15 risk and continuous improvement (PDF 451-476) | Commit/acceptance/later stages, same artifact promotion, application drivers, environment parity, nonfunctional requirements, database evolution and whole-delivery feedback |

## Differences are decisions, not errors to erase

**Characterization versus specification.** Feathers ch. 13 deliberately captures
current output, even suspicious behavior, to detect accidental change. Beck's
next behavior and the existing `test-behavior` correctness mode instead need an
accepted expectation. The procedures retain both modes and require explicit
labels; they do not rewrite a requirement merely because current code disagrees.

**State versus interaction verification.** Meszaros chs. 4-5/10-11 discuss
alternatives and favor the front door when choices are equally effective. GOOS
uses role collaboration and mock expectations as design feedback. Neither yields
a universal ban on mocks or a command to mock every collaborator. GOOS ch. 8
also permits limited third-party mocking for otherwise difficult error cases.

**One condition versus one assertion.** Meszaros ch. 5 explicitly rejects
unhelpful dogmatism about assertion count. A workflow recovery test may need
several observations of one temporal condition. Separate unrelated conditions;
do not remove synchronization merely because it resembles a repeated assertion.

**Fixture cleanup and transactions.** GOOS ch. 25 favors initialization at test
start, retained failure data and explicit commits; it warns that rollback-only
tests can miss commit behavior. Continuous Delivery ch. 12 and Meszaros's
Transaction Rollback Teardown discuss rollback as an isolation technique.
Choose according to what is being tested: rollback can isolate a rule test but
cannot substitute for committed visibility, constraint or restart evidence.
Retain diagnostics before cleaning resources owned by the run.

**Coverage and completeness.** Continuous Delivery discusses configured quality
thresholds; Fowler ch. 4 emphasizes risk and diminishing returns. We preserve
consumer gates and exceptions without treating percentages as correctness or
inventing a universal test ratio, speed budget or mutation threshold.

**Design and distribution.** Fowler's supplied edition explicitly excludes
concurrent/distributed refactoring concerns (PDF 10). Beck's preface notes limits
of TDD for concurrency and security (PDF 9). The books do not establish the
semantics of a particular cloud provider or a distributed commit protocol.

## Explicit modern adaptations

The evidence record, exact-source/session distinctions, controlled defect probes,
property/metamorphic examples, failure matrices, owner fencing, crash-point tests,
artifact provenance and AI-output evaluation are engineering adaptations in this
contribution. The books motivate feedback, isolation, contracts and preservation;
they do not supply or prove all these mechanisms. Read current consumer contracts
and official runtime documentation for their actual semantics. Do not imply that
Fowler's catalog proves a distributed refactor safe, that deterministic tests
exhaust schedules, or that an agent-generated oracle is independent merely
because a second agent wrote it.

No source-specific numeric rule is silently promoted into repository policy.
Examples are reasoning aids; limits and correctness conditions must be justified
for the consumer and the tested operation.
