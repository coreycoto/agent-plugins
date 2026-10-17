"""Offline decision model. No provider, hook registration, shell execution or credentials.

Inputs stand for independently authenticated observations/authority; accepting
model-supplied booleans in a deployed tool would not establish that trust.
"""
from __future__ import annotations

import re
from collections.abc import Callable

IDENTITY = ("host", "repository", "repository_id", "release_id", "tag", "source_sha",
            "artifacts", "isPrerelease", "body_sha256")


def valid_candidate(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if set(value) != {*IDENTITY, "isDraft"}:
        return False  # This body-only model has no adapter for additional fields.
    if any(not isinstance(value.get(key), str) or not value[key]
           for key in ("host", "repository", "tag")):
        return False
    if any(type(value.get(key)) is not int or value[key] <= 0
           for key in ("repository_id", "release_id")):
        return False
    for key, size in (("source_sha", 40), ("body_sha256", 64)):
        if not isinstance(value.get(key), str) or not re.fullmatch(r"[0-9a-f]{" + str(size) + "}", value[key]):
            return False
    if type(value.get("isPrerelease")) is not bool:
        return False
    artifacts = value.get("artifacts")
    return isinstance(artifacts, dict) and all(
        isinstance(name, str) and name and isinstance(sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", sha)
        for name, sha in artifacts.items())


def decide(request: dict, observations: object, authority: object,
           executable_permitted: object) -> str:
    """Return eligibility, never executable permission or a concurrent-write guarantee."""
    if executable_permitted is not True:
        return "executable_denied_or_unknown"
    action = request.get("action")
    if action not in {"edit_draft", "publish_draft"}:
        return "unsupported_action"
    expected = request.get("expected")
    result = request.get("result")
    if (not valid_candidate(expected) or not valid_candidate(result)
            or expected.get("isDraft") is not True):
        return "invalid_candidate"
    # This bounded model edits the body only; artifact/tag mutations need their
    # own reviewed operation. Publication covers the exact reviewed draft body.
    fixed = IDENTITY if action == "publish_draft" else IDENTITY[:-1]
    if any(expected[key] != result[key] for key in fixed):
        return "changed_result_identity"
    if not isinstance(observations, list) or len(observations) != 1:
        return "missing_or_ambiguous_state"
    current = observations[0]
    if not valid_candidate(current) or type(current.get("isDraft")) is not bool:
        return "invalid_state"
    if current["isDraft"] is False:
        return "already_published"
    if any(current[key] != expected[key] for key in IDENTITY):
        return "changed_release_identity"
    # Authority is supplied by a hypothetical trusted boundary, not request args.
    if not isinstance(authority, dict) or authority.get("action") != action:
        return "unauthorized_action"
    if authority.get("expected") != expected or authority.get("result") != result:
        return "unauthorized_candidate"
    if action == "publish_draft" and authority.get("explicit_publication_approval") is not True:
        return "publication_approval_required"
    if result.get("isDraft") is not (action == "edit_draft"):
        return "wrong_transition"
    return "eligible"


def simulate_operation(request: dict, authority: dict, executable_permitted: object,
                       read: Callable[[], object], write: Callable[[dict], None]) -> str:
    """Two reads then a fake write; demonstrates, rather than solves, the race."""
    for _ in range(2):
        try:
            observations = read()
        except Exception:
            return "read_failed"
        decision = decide(request, observations, authority, executable_permitted)
        if decision != "eligible":
            return decision
    try:
        write(request["result"])
    except Exception:
        return "write_outcome_unknown"  # inspect state; never automatically retry
    return "simulated_write"
