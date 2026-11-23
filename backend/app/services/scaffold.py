"""Scaffolding state machine.

Pure logic: standard library only, no I/O, no Ollama.
The backend decides the hint tier here; the LLM never does.
"""
from dataclasses import dataclass, replace
from typing import Optional

MAX_TIER = 3

TIER_LABELS = {
    1: "Petunjuk 1",
    2: "Petunjuk 2",
    3: "Pembetulan penuh",
}

BLOOM_LABELS = {
    1: "Remember / Understand",
    2: "Apply / Analyse",
    3: "Evaluate / Create",
}

EVENTS = ("attempt", "help")


@dataclass(frozen=True)
class ItemState:
    status: str = "new"  # new, in_progress, solved, revealed
    tier: int = 0
    solved_at_tier: Optional[int] = None


def tier_if_wrong(state):
    """The tier the next reply uses if this attempt is wrong."""
    return state.tier + 1


def advance(state, event, correct=False):
    """Return the NEW state after one learner event. The old state is not changed."""
    if state.status in ("solved", "revealed"):
        raise ValueError(f"item is already {state.status}")
    if event not in EVENTS:
        raise ValueError(f"unknown event: {event!r}")
    if event == "help" and state.status == "new":
        raise ValueError("help needs an attempt first")

    if event == "attempt" and correct:
        return replace(state, status="solved", solved_at_tier=state.tier)

    new_tier = tier_if_wrong(state)
    status = "revealed" if new_tier >= MAX_TIER else "in_progress"
    return replace(state, status=status, tier=new_tier)