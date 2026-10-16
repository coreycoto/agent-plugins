# Engineering judgment and specialist verification

Version 0.10.0 adds three Product Development entrypoints and strengthens
existing design, diagnosis, implementation, review, refactoring and knowledge
procedures. It does not add a plugin, runtime, role, hook or mandatory workflow
chain. Registry availability and exact acquired contents require verification
before consumer adoption.

## Choose by outcome

| Task | Procedure |
| --- | --- |
| Find worthwhile structural work | understand-codebase, with its maintained assessment reference |
| Settle alternatives and caller obligations | design-change |
| Clarify identity, valid states and decision/effect boundaries | model-domain |
| Investigate measured system effects or a limiter | diagnose-problem or improve-performance |
| Explore competing executions of a protocol | check-protocol |
| Exercise the path through a schema/API/component transition | rehearse-migration |
| Assess a dataset's fitness for a declared use | assess-data-quality |

The three new skills use existing tools and carry explicit evidence boundaries.
A model result is not an implementation proof; a destination test is not a
transition rehearsal; a green pipeline is not a data-quality assessment.
A small change can still go directly to implementation and relevant checks.

## Improvements without new names

Conditional guidance covers modernization value and history confounders,
before/after caller complexity, bounded alternative-design experiments,
decision/effect separation, trustworthy runtime boundaries, accumulation/delays,
and preservation of design assumptions rather than file-change summaries.
See the [source/adaptation record](../plugins/product-development/skills/_shared/references/judgment/sources.md).
The newly discussed books were not supplied for full-text extraction. Public
primary material and relevant supplied-book sections are distinguished from
original workflow adaptations; no books or private consumer code are bundled.

Version 0.10.1 adds two conditional references adapted from pinned
Anthropic plugin mechanisms. The
[version-upgrade catalog](../plugins/product-development/skills/_shared/references/judgment/version-upgrade-catalog.md)
connects exact-version changes to actual callers, silent behavior and pilot
evidence in design-change and phased-refactor. The
[diff-scoped simplification guide](../plugins/product-development/skills/_shared/references/judgment/diff-scoped-simplification.md)
helps implement-change refine the owned patch while retaining useful boundaries
and valid no-change outcomes. Consumer standards, artifacts and authorization
continue to govern both; no new skill, role or runtime is added.

Version 0.10.2 includes [#37](https://github.com/coreycoto/agent-plugins/issues/37),
adding conditional pstack adaptations within the same procedures:

- Diagnosis and performance work can reconsider a premise shared by repeated
  failed fixes, inspecting distributions and work assignment without treating
  required asymmetry or a uniform defect as a scheduling bug.
- Benchmarking checks peak and partial-cycle resource windows against accepted
  limits; eventual balance or a sampled maximum is a different claim.
- Design and protocol work compare independent facts with a real canonical-state
  invariant before adding coordination.
- Refactoring qualifies existing mechanical tools or a small repeatable command
  when replay earns its cost, preserving direct small edits as a valid choice.
- Capture forensics preserves artifact/build identity, reduction and source
  attribution while keeping observed hot paths separate from confirmed causes.

The optional [steering index](../plugins/product-development/skills/_shared/references/engineering-principles.md)
lets a user say "Attack the Premise" or "Separate Before Coordinating" and reach
the applicable guidance. It adds no discoverable skill or mandatory reply section;
the explanation should identify the actual changed decision. Existing consumer
authority and scope remain intact. The
[comparison plan](../evals/owned-workflows/engineering-principles.md) separates
prior procedures, conditional references and references plus named steering.

## Evaluate before claiming effectiveness

The [specialist trial plan](../evals/owned-workflows/engineering-judgment/README.md)
compares the prior skills, improved general skills with references, and specialist
entrypoints. Synthetic author fixtures cover lost acknowledgment, migration
intermediate states and data-population defects, with meaningful negative cases.
Deterministic checks qualify fixtures and graders, not model adherence, native
selection or production correctness. Agent/model trials remain unrun until
observed through the existing authorized evaluation workflow.

Run normal author checks from CONTRIBUTING.md and the focused suite:

```sh
uv run --locked pytest tests/test_engineering_workflows.py
```

Do not publish changed content under an existing version. Source preparation,
release, registry acquisition, consumer pins, installation and fresh-session
discovery require separate evidence. Nothing here changes the private Agent
Development authoring runtime or any consumer repository's operations or
verification policy.

Six additional read-only reference trials cover silent rounding changes, an
unavailable analyzer, a routine patch bump, an unnecessary wrapper, a helpful
authorization boundary and already-clear code. See the
[upgrade suite](../evals/owned-workflows/version-upgrade-catalog/README.md) and
[simplification suite](../evals/owned-workflows/diff-scoped-simplification/README.md).
Their frozen assertions check fixture preservation; separate rubrics judge
recommendations. These cases do not claim execution of refinements or model
effectiveness. Qualify their staging/grader contract with:

```sh
uv run --locked pytest tests/test_upgrade_simplification_evals.py
```

The potential Data Engineering package stays a [backlog proposal](https://github.com/coreycoto/agent-plugins/issues/30).
Its go/no-go decision must justify independent selection and non-duplicating
ownership; check-protocol and rehearse-migration remain general engineering.
