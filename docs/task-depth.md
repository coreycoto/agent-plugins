# Conditional task depth

Issue [#39](https://github.com/coreycoto/agent-plugins/issues/39) adds references
within existing skills to improve source and method selection for the same
requested outcome. It adds no discoverable skill, agent role, runtime or mandatory
stage. Direct routine work remains valid.

| Package | Existing entrypoints | Conditional reference |
| --- | --- | --- |
| Product Development | engineering-workflow | [Task depth](../plugins/product-development/skills/_shared/references/judgment/task-depth.md) |
| Product Management | product-discovery, product-requirements | [Research depth](../plugins/product-management/skills/_shared/references/research-depth.md) |
| Communication | write-prose | [Substantive depth](../plugins/communication/skills/_shared/references/substantive-depth.md) |

Each selected package is complete on its own. The references share a mechanism
but own different decisions: engineering evidence and verification, product
framing and research, or the substance of an explanation. Project Management
keeps its existing delivery and publication responsibilities.

## Source and adaptation

The source is [be-ambitious at `7dc63b7a748b8bd14bf213c15ecddd4536409407`](https://github.com/DannyMac180/skills/blob/7dc63b7a748b8bd14bf213c15ecddd4536409407/be-ambitious/SKILL.md)
by Dan McAteer, based on [Felix Rieseberg's article of October 13, 2026](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/).
The upstream skill and MIT license were inspected at that immutable Git revision.
Each affected package retains its own source-lineage entry and MIT notice.
The article is motivation and attribution, not independent effectiveness evidence.

The adaptation connects professional practice, useful primary material, concrete
methods and an observable check that can reject the answer. It preserves the
requested scope and medium. More raw data, more complex tools and more agents
are not default improvements. A method is valuable when it changes an important
choice within the actual resource and access limits.

The upstream skill always rewrites a prompt and then waits for execution consent.
Here, prompt-rewriting requests stop at the rewrite, while already-authorized
execution continues through the existing workflow. No new confirmation gate is
introduced. A broader outcome, unavailable access or uncovered external action
still requires its own decision. Stretch targets stay hypotheses rather than
invented requirements or reasons to ignore real constraints.

## Qualification limits

The [comparison plan](../evals/owned-workflows/task-depth.md) compares current
guidance, conditional references and an experimental command before considering
a new discoverable entrypoint. Synthetic read-only cases exercise method choices,
counterevidence, unavailable material, legitimate exceptions, routine work and
delivery-stage recommendations. They do not prove execution continuation.

Run the reference corpus tests and normal author checks from CONTRIBUTING.md.
Fixture-preservation checks and package qualification do not establish native
selection, body use, adherence, comprehension or useful model outcomes. Paired
model/client trials remain unrun until separately authorized and observed.

This is unreleased source. Release, acquisition, installation, trust review and
fresh-session activation remain separate endpoints.
