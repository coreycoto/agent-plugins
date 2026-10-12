"""Synthetic protocol candidate; acceptance count is receiver-durable state."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class State:
    phase: str = "ready"
    accepted: int = 0


def next_states(state: State, *, repair: bool = False):
    if state.phase == "ready" and state.accepted < 2:
        yield "dispatch", replace(state, phase="sent")
    elif state.phase == "sent":
        yield "accept_reply", State("done", state.accepted + 1)
        yield "accept_lost", State("unknown", state.accepted + 1)
    elif state.phase == "unknown":
        yield "observe", replace(state, phase="done")
        yield "wait", state
        if not repair:
            yield "expire", replace(state, phase="ready")
