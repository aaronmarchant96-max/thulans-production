"""Deterministic Deephearth Event Forge clean-room rebuild.

This package is intentionally independent of the missing historical prototype.
It implements the contract documented in ``docs/DEEPHEARTH_EVENT_FORGE_PLAN.md``
so a later recovered source can be compared against a stable oracle.
"""

from .engine import (
    ColonyState,
    EventForge,
    EventPattern,
    EventProposal,
    Resident,
    ValidationError,
    generate_mockup_state,
)

__all__ = [
    "ColonyState",
    "EventForge",
    "EventPattern",
    "EventProposal",
    "Resident",
    "ValidationError",
    "generate_mockup_state",
]
