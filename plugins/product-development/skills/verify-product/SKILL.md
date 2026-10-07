---
name: verify-product
description: Exercise an actual user-facing product path and preserve evidence of its observable outcome, failure, or unavailable prerequisites.
---

# Verify Product

Establish the requested behavior, exact source or deployed artifact, environment
and task authority. Use the consumer's existing verification instructions or
harness where available. Read the
[verification guide](../_shared/references/product-verification.md) for launch,
interaction, evidence and cleanup details; do not invent credentials or setup.

Choose the user-visible entry point: browser flow, CLI command, desktop action,
API consumer or library contract. Drive that path using actual available tools.
Avoid internal state setters and test-only routes that bypass the behavior
being claimed. A launch, health endpoint or import establishes readiness, not
the user outcome.

Check prerequisites and instance identity before driving it. Keep shared browser
or app state serial; isolated independent environments may be used only within
task scope. A missing provider, auth state or platform feature is an unverified
prerequisite. Preparation or synthetic coverage can proceed independently,
but cannot turn that gap into a pass.

Observe both action and result. Verify relevant persistence, generated files,
consumer state or downstream effects as well as the visible response. Keep
expected behavior grounded in acceptance policy; current source is evidence
of mechanics, not permission to redefine a broken product as correct.

Retain revision, commands or interaction steps, results and redacted artifacts
for each material claim. Preserve failure evidence before cleaning owned
scratch or processes. Stop only instances created by the run; never use broad
process-name cleanup or alter unrelated user sessions. Do not replay ambiguous
provider mutations to obtain evidence.

Complete with pass, reproduced failure or unverified prerequisites for the
specified path, plus exact evidence and limitations. Repairs belong to an
authorized implementation task. Use
[maintain-verification](../maintain-verification/SKILL.md) when a consumer's
instructions or harness need creation or correction; verification alone does
not authorize deployment or publication.
