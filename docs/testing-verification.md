# Testing and verification procedures

Product Development keeps the same sixteen skill IDs. This contribution extends
existing entrypoints with a progressively loaded testing reference library; it
does not introduce a second plugin, test runner, deployment gate, role or hook.
Start at the [decision guide](../plugins/product-development/skills/_shared/references/testing/README.md).

Use `test-behavior` for specification/regression evidence or explicitly labeled
characterization; `maintain-verification` for a bounded confidence audit or harness
instructions; `phased-refactor` for test or production restructuring;
`verify-product` for actual user-path qualification; and `review-code` for an exact
candidate's evidence. The engineering router remains optional. Tiny understood
edits do not require the entire library.

The [source map](../plugins/product-development/skills/_shared/references/testing/sources.md)
identifies all six supplied editions, relevant chapters and PDF locators, and
preserves disagreements about characterization, mocks, fixture isolation and
transaction handling. Original modern workflow/data adaptations are distinguished
from the books. The books themselves are not distributed or required at runtime.

## Author checks and effectiveness

Run the normal commands in [CONTRIBUTING](../CONTRIBUTING.md), including package
validation/build/check and tests. The new testing corpus also has a focused check:

```sh
uv run --locked pytest tests/test_testing_guidance.py
```

This checks reference/corpus integrity and that the independent test-sensitivity
oracle accepts a useful test suite and rejects specific inadequate suites. It is
not model effectiveness, native discovery or consumer deployment evidence.
See the [trial corpus](../evals/owned-workflows/test-behavior/README.md) for paired
agent evaluation and its unrun status. Existing private evaluator integration is
optional; no evaluator runtime is copied into this publisher.

## Promotion

This is an unreleased source contribution. Package versions and marketplace pins
are deliberately unchanged. Do not publish changed bytes as an existing version
or infer registry availability from the source branch. Before consumer adoption,
qualify a reviewed new release through the existing publisher workflow, update
consumer pins to that actual release, verify acquired bytes, and confirm fresh
session discovery. A separately authorized source trial can use the existing
skills-only/local-package recipe without changing production locks or hook trust.
