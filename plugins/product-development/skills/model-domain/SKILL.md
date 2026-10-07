---
name: model-domain
description: Clarify domain vocabulary, identity, state, invariants, and boundary contracts when ambiguous concepts or repeated rules complicate software design.
---

# Model Domain

Bound the problem and inspect existing domain language, accepted rules and
representative scenarios. Identify whose concepts the model represents and
where another subsystem uses different meanings. Preserve consumer terminology;
do not impose a universal glossary or model the entire business for a local
change.

Describe identity separately from attributes: what makes two values the same,
which identifiers persist, and who owns their lifecycle. Trace states,
transitions, commands and observations. State invariants and invalid combinations,
including time, ordering, concurrency and failure when they matter.

Locate boundaries where representation changes: input parsing, serialization,
storage, external APIs and ownership transfers. Distinguish a domain rule from
a transport constraint or a current implementation accident. Source contradicting
accepted policy is a decision or potential bug, not an automatic new rule.
Use the [impact guide](../_shared/references/change-impact.md) for affected
consumers or persisted representations.

Choose a structure that concentrates actual knowledge: a value object, explicit
state machine, tagged state, registry, graph or ordinary local code. Prefer
boring code when it already makes the rules clear. An abstraction should remove
invalid states, duplicated assumptions or caller burden; indirection alone is
not improvement. Keep runtime validation where external data can violate static
types.

Walk concrete valid and invalid examples through the proposed model. Identify
what it makes impossible, what still requires validation and how migration
preserves existing identities and data. Capture unresolved semantic choices for
the product or domain owner rather than guessing them.

Complete with a focused vocabulary, identity and state rules, invariants,
boundary contracts, example outcomes and remaining decisions. A model document
is not an implementation or data-migration commitment. Use
[design-change](../design-change/SKILL.md) when translating an accepted model
into technical interfaces and rollout steps.
