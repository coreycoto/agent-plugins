---
name: prototype-decision
description: Run a bounded disposable experiment to answer a specific technical or interaction uncertainty with explicit decision criteria.
---

# Prototype Decision

Name the uncertainty, decision it blocks and evidence that would resolve it.
Distinguish a technical feasibility question from a product hypothesis; use
available `product-management:product-experiments` for the latter. Avoid building
a broad demo when one focused observation can settle the choice.

Define success and failure criteria before implementation. Identify assumptions,
representative inputs, comparison and scope limits. Use supplied constraints;
do not invent targets or claim production feasibility from a toy scenario.
If the criteria are unresolved product decisions, return them while progressing
independent setup.

Choose the cheapest faithful experiment: an isolated script, narrow interface,
small UI flow or limited integration harness. Put it in disposable scratch or
the consumer's designated prototype area, preserving working changes. Mock a
boundary only when it does not invalidate the question; label synthetic results.
Provider-backed experiments require actual task authority and available access.

Implement only what is needed to observe the uncertain behavior. Capture inputs,
revision, environment, output and failure modes. For competing approaches, keep
work and conditions comparable. Use the
[benchmarking guide](../_shared/references/benchmarking.md) for performance claims.

Assess the original criteria, including adverse evidence and untested limits.
Report supported, rejected or inconclusive rather than stretching a promising
demo into proof. Identify the smallest next experiment only if unresolved
evidence changes the decision.

Complete with the question, experiment, evidence, decision implication and
limits. Preserve useful results before removing only authorized owned scratch.
Promotion of a prototype into maintained product code needs the consumer's
accepted implementation scope; route to
[design-change](../design-change/SKILL.md) or
[implement-change](../implement-change/SKILL.md) when that is authorized.
