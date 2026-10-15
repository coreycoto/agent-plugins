# Source scope and adaptation record

This iteration implements agreed engineering workflows, not a claim to have
reread all newly recommended books. Skills are original operational instructions;
source ideas inform them but do not prove that they improve any particular model.
No book text, diagrams, consumer-private examples or copyrighted PDFs are shipped.

## Supplied editions consulted

- Freeman and Pryce, Growing Object-Oriented Software, Guided by Tests (2009):
  chapter 1, internal/external quality and listening to test difficulty; chapter
  26, separating functionality and concurrency policy. Use the supplied edition's
  terminology, not a claim that its unit tests prove distributed correctness.
- Feathers, Working Effectively with Legacy Code (2004): chapters 16-17,
  understanding code and telling the system's story; chapters 4 and 13 remain
  the basis for seams and characterization in the [testing library](../testing/sources.md).
- Humble and Farley, Continuous Delivery (2010): chapter 12, especially printed
  pp. 327-334 (supplied PDF pp. 361-368), incremental change, data preservation
  and decoupled application/database transitions. The book's relational examples
  are not blanket guarantees about another database or a cloud runtime.
- Beck, Test-Driven Development: By Example (2002): the preface explicitly limits
  TDD's mechanical demonstration of security and concurrency (supplied PDF p. 9).
- Fowler et al., Refactoring (1999): the introduction excludes concurrent and
  distributed programming from its scope (supplied PDF p. 10).
- Meszaros, xUnit Test Patterns (2007): independent fixtures, verification and
  testability remain grounded in the existing [source map](../testing/sources.md),
  rather than reinterpreted as a data-quality or formal-verification standard.

## Public primary material consulted

- [TLC configuration](https://learning.tlapl.us/intro/tlc-config/): explicitly
  enabled invariant/temporal checks and fairness/configuration limits. The
  finite Python example in the author corpus is our own; it does not run TLC.
- [Donella Meadows, Leverage Points](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/):
  stocks, flows, delays and feedback; the essay warns against general recipes.
  The retry/backlog diagnostic procedure is an original software adaptation.
- [John Ousterhout's book page](https://web.stanford.edu/~ouster/cgi-bin/aposd.php):
  identifies second-edition changes and disagreements about method length and
  comments. This is limited author material, not a full-text book study.

The broader reading list (Kill It with Fire, Software Design Decoded, Thinking
in Systems, A Philosophy of Software Design, Your Code as a Crime Scene,
Grokking Simplicity, Domain Modeling Made Functional, DDIA, Enterprise Integration
Patterns and Release It!) remains candidate input for later source-specific
extraction. Those full texts were not supplied in this iteration. Do not invent
chapter locators or attribute these whole workflows to those books.

For a later source extraction, preserve claim, locator, applicable situation,
proposed agent behavior, counterexample and evaluation case separately. Keep
disagreements visible. Existing private authoring/evaluation workflows own that
work; this library introduces no second authoring runtime or automatic learning.

## Pinned plugin mechanisms

The version-upgrade catalog and diff-scoped simplification references adapt
[Anthropic's Claude Code plugins at `641d925db5a662e72f8650cb1b7670a59dab1abc`](https://github.com/anthropics/claude-plugins-official/tree/641d925db5a662e72f8650cb1b7670a59dab1abc).
Consulted paths are `plugins/code-modernization/agents/version-delta-analyst.md`,
`plugins/code-modernization/commands/modernize-uplift.md` and
`plugins/code-simplifier/agents/code-simplifier.md`. Exact source/destination
paths and departures are recorded in [source lineage](../upstream-lineage.json);
the [Apache 2.0 license](../../../../licenses/anthropic-claude-plugins-Apache-2.0.txt)
is retained with [third-party attribution](../../../../THIRD_PARTY_NOTICES.md).

These are original references within existing skills. They use consumer standards,
available tools and existing authority/evidence conventions. They omit upstream
style defaults, automatic cleanup, mandatory approval sequences, fixed artifact
names, agent fan-out, telemetry and client-specific hooks. Synthetic trials
qualify a bounded adoption decision; source inspection alone establishes no
model-effectiveness improvement.

## Pstack engineering judgment and steering

The premise-reset, shared-state, repeatable-work and trace-forensics references,
plus the optional engineering-principles index, adapt
[pstack at `6ce45c59b9301a638c1fe1a7b8dc2a82b650898f`](https://github.com/cursor/plugins/tree/6ce45c59b9301a638c1fe1a7b8dc2a82b650898f/pstack).
Consulted mechanisms are Attack the Premise, Explain the Number, Separate Before
Serializing Shared State, Build the Lever, the poteto-mode principle index and
the captured-trace forensics playbook. The
[lineage record](../upstream-lineage.json) retains earlier pins alongside this
revision, exact paths and departures. Lauren Tan's
[MIT notice](../../../../licenses/pstack-MIT.txt) remains bundled.

These are conditional original procedures within existing skills. They preserve
uniform-defect and required-affinity exceptions, canonical ownership and reader
consistency, useful direct edits, and the difference between observation and
causal confirmation. A balanced census does not clear a premise, and a paired
capture alone does not prove a cause. They require no new script for every task,
principle footer, automatic delegation, transcript mining, live hot-patching or
provider operation. Peak/partial-window resource examples and evaluation cases
are original synthetic adaptations; the supplied discussion is motivation, not
independently reproduced benchmark evidence or a universal scheduling recipe.

Names help steer an existing procedure. A name-drop is not proof of body use,
adherence or a useful outcome. Source, package and author-test qualification stay
distinct from the paired model/client trials needed to establish effectiveness.
