"""Offline deterministic narrative-event engine for Deephearth.

The engine never calls a model and never mutates a colony during proposal
generation. A proposal is revalidated against the exact state version before a
transaction commits its physical and consequence-ledger effects.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
import random
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a proposal or state violates the event contract."""


@dataclass
class Resident:
    resident_id: str
    name: str
    alive: bool = True
    location_id: str = "deephearth"
    knowledge: set[str] = field(default_factory=set)
    bond: int = 0


@dataclass
class ColonyState:
    day: int = 43
    water_litres: int = 124
    water_capacity_litres: int = 200
    pressure_psi: int = 58
    marks: int = 100
    residents: dict[str, Resident] = field(default_factory=dict)
    locations: set[str] = field(default_factory=lambda: {"deephearth", "north_aquifer"})
    evidence_tokens: list[str] = field(default_factory=list)
    consequence_ledger: list[dict[str, Any]] = field(default_factory=list)
    active_event_keys: set[str] = field(default_factory=set)
    state_version: int = 1

    def snapshot(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "water_litres": self.water_litres,
            "water_capacity_litres": self.water_capacity_litres,
            "pressure_psi": self.pressure_psi,
            "marks": self.marks,
            "residents": {
                rid: {
                    "name": r.name,
                    "alive": r.alive,
                    "location_id": r.location_id,
                    "knowledge": sorted(r.knowledge),
                    "bond": r.bond,
                }
                for rid, r in sorted(self.residents.items())
            },
            "locations": sorted(self.locations),
            "evidence_tokens": sorted(self.evidence_tokens),
            "consequence_ledger": deepcopy(self.consequence_ledger),
            "active_event_keys": sorted(self.active_event_keys),
            "state_version": self.state_version,
        }

    def fingerprint(self) -> str:
        payload = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EventPattern:
    pattern_id: str
    title: str
    trigger: str
    actor_role: str
    location_id: str
    consequence_token: str
    water_delta: int = 0
    marks_delta: int = 0


@dataclass
class EventProposal:
    event_id: str
    pattern_id: str
    pattern_version: str
    seed: int
    source_pattern: str
    trigger_facts: dict[str, Any]
    state_version: int
    state_fingerprint: str
    actor_ids: list[str]
    location_ids: list[str]
    eligibility: dict[str, bool]
    knowledge_predicates: dict[str, list[str]]
    options: list[dict[str, Any]]
    preconditions: dict[str, Any]
    proposed_effects: dict[str, Any]
    expiry_day: int
    cooldown_key: str
    lifecycle: str = "PROPOSED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "pattern_id": self.pattern_id,
            "pattern_version": self.pattern_version,
            "seed": self.seed,
            "source_pattern": self.source_pattern,
            "trigger_facts": self.trigger_facts,
            "state_version": self.state_version,
            "state_fingerprint": self.state_fingerprint,
            "actor_ids": self.actor_ids,
            "location_ids": self.location_ids,
            "eligibility": self.eligibility,
            "knowledge_predicates": self.knowledge_predicates,
            "options": self.options,
            "preconditions": self.preconditions,
            "proposed_effects": self.proposed_effects,
            "expiry_day": self.expiry_day,
            "cooldown_key": self.cooldown_key,
            "lifecycle": self.lifecycle,
        }


PATTERNS: tuple[EventPattern, ...] = (
    EventPattern("P01", "Survival Through Concealment", "water_low", "debtor", "north_aquifer", "concealed_water", water_delta=-8, marks_delta=4),
    EventPattern("P02", "The Diverted Shipment", "marks_low", "steward", "deephearth", "diverted_shipment", water_delta=4, marks_delta=-12),
    EventPattern("P03", "Names Beneath the Stone", "pressure_low", "surveyor", "deephearth", "buried_names", marks_delta=-3),
    EventPattern("P04", "The Unsealed Flue", "pressure_high", "flue_keeper", "deephearth", "unsealed_flue", water_delta=-3),
    EventPattern("P05", "The Cold Tithe", "water_low", "steward", "north_aquifer", "cold_tithe", water_delta=6, marks_delta=-5),
    EventPattern("P06", "The Broken Gauge", "pressure_low", "surveyor", "deephearth", "broken_gauge", marks_delta=-2),
    EventPattern("P07", "The Surface Rumor", "day_even", "scout", "deephearth", "surface_rumor", marks_delta=1),
    EventPattern("P08", "The Stolen Filter-Salt", "marks_low", "debtor", "north_aquifer", "stolen_filter_salt", water_delta=2, marks_delta=-8),
    EventPattern("P09", "The Silent Sump", "water_low", "flue_keeper", "deephearth", "silent_sump", water_delta=-4),
    EventPattern("P10", "The Returning Bell", "day_even", "scout", "north_aquifer", "returning_bell", marks_delta=2),
)


def generate_mockup_state(*, invalid: bool = False) -> ColonyState:
    """Return the documented Day 43 control state.

    ``invalid=True`` deliberately removes Bram's actor eligibility for negative
    validation and benchmark controls; it is not a gameplay state claim.
    """

    residents = {
        "bram": Resident("bram", "Bram", location_id="north_aquifer", bond=0),
        "sanna": Resident("sanna", "Sanna", location_id="deephearth", bond=62),
        "mira": Resident("mira", "Mira", location_id="deephearth", bond=12),
    }
    state = ColonyState(
        water_litres=124,
        water_capacity_litres=200,
        pressure_psi=58,
        marks=100,
        residents=residents,
        evidence_tokens=["day_43", "water_62_percent", "pressure_58_psi", "bram_debt_45_marks"],
    )
    if invalid:
        for resident in state.residents.values():
            resident.alive = False
    return state


class EventForge:
    """Generate, validate, and atomically commit deterministic proposals."""

    pattern_version = "deephearth-patterns-v1"

    def __init__(self, patterns: tuple[EventPattern, ...] = PATTERNS) -> None:
        self.patterns = patterns

    def _eligible_patterns(self, state: ColonyState) -> list[EventPattern]:
        water_ratio = state.water_litres / state.water_capacity_litres
        eligible: list[EventPattern] = []
        for pattern in self.patterns:
            trigger = (
                (pattern.trigger == "water_low" and water_ratio < 0.70)
                or (pattern.trigger == "marks_low" and state.marks < 50)
                or (pattern.trigger == "pressure_low" and state.pressure_psi < 50)
                or (pattern.trigger == "pressure_high" and state.pressure_psi > 70)
                or (pattern.trigger == "day_even" and state.day % 2 == 0)
            )
            if trigger:
                eligible.append(pattern)
        return eligible

    def generate(self, state: ColonyState, *, seed: int) -> EventProposal:
        candidates = self._eligible_patterns(state)
        if not candidates:
            raise ValidationError("no authored pattern is eligible for the current state")
        rng = random.Random(seed)
        pattern = candidates[rng.randrange(len(candidates))]
        actors = [r for r in state.residents.values() if r.alive and r.location_id == pattern.location_id]
        if pattern.actor_role == "debtor":
            actors = [r for r in actors if r.name == "Bram"] or actors
        if not actors:
            raise ValidationError(f"no eligible actor for {pattern.pattern_id}")
        actor = sorted(actors, key=lambda resident: resident.resident_id)[0]
        event_id = f"{pattern.pattern_id}-D{state.day}-S{seed}"
        cooldown_key = f"{pattern.pattern_id}:{actor.resident_id}:{pattern.location_id}"
        if cooldown_key in state.active_event_keys:
            raise ValidationError("duplicate active event")
        proposal = EventProposal(
            event_id=event_id,
            pattern_id=pattern.pattern_id,
            pattern_version=self.pattern_version,
            seed=seed,
            source_pattern=f"authored:{pattern.pattern_id}",
            trigger_facts={"day": state.day, "water_litres": state.water_litres, "pressure_psi": state.pressure_psi, "marks": state.marks},
            state_version=state.state_version,
            state_fingerprint=state.fingerprint(),
            actor_ids=[actor.resident_id],
            location_ids=[pattern.location_id],
            eligibility={"actor_alive": actor.alive, "location_exists": pattern.location_id in state.locations},
            knowledge_predicates={actor.resident_id: sorted(actor.knowledge)},
            options=[
                {"option_id": "conceal", "label": "Conceal the shortage", "effects": {"marks_delta": pattern.marks_delta}},
                {"option_id": "report", "label": "Report it to the Council", "effects": {"water_delta": pattern.water_delta}},
            ],
            preconditions={"state_version": state.state_version, "actor_alive": True, "location_exists": True, "day_at_most": state.day + 1},
            proposed_effects={"water_delta": pattern.water_delta, "marks_delta": pattern.marks_delta, "evidence_token": pattern.consequence_token},
            expiry_day=state.day + 1,
            cooldown_key=cooldown_key,
        )
        self.validate(state, proposal)
        proposal.lifecycle = "VALIDATED"
        return proposal

    def validate(self, state: ColonyState, proposal: EventProposal) -> None:
        if proposal.lifecycle in {"COMMITTED", "REJECTED", "EXPIRED"}:
            raise ValidationError("proposal is no longer actionable")
        if proposal.state_version != state.state_version:
            raise ValidationError("stale proposal: state version changed")
        if proposal.state_fingerprint != state.fingerprint():
            raise ValidationError("stale proposal: state fingerprint changed")
        if state.day > proposal.expiry_day:
            raise ValidationError("proposal expired")
        if not proposal.actor_ids or not proposal.location_ids:
            raise ValidationError("proposal must name an actor and location")
        actor = state.residents.get(proposal.actor_ids[0])
        if actor is None or not actor.alive:
            raise ValidationError("actor is unavailable")
        if proposal.location_ids[0] not in state.locations:
            raise ValidationError("location is unavailable")
        if proposal.cooldown_key in state.active_event_keys:
            raise ValidationError("duplicate active event")
        if not proposal.eligibility.get("actor_alive") or not proposal.eligibility.get("location_exists"):
            raise ValidationError("proposal eligibility is false")

    def commit(self, state: ColonyState, proposal: EventProposal, option_id: str = "report") -> ColonyState:
        self.validate(state, proposal)
        option = next((item for item in proposal.options if item["option_id"] == option_id), None)
        if option is None:
            raise ValidationError(f"unknown option: {option_id}")
        before = state.snapshot()
        try:
            pattern = next(item for item in self.patterns if item.pattern_id == proposal.pattern_id)
            state.water_litres = max(0, state.water_litres + int(option.get("effects", {}).get("water_delta", pattern.water_delta)))
            state.marks = max(0, state.marks + int(option.get("effects", {}).get("marks_delta", pattern.marks_delta)))
            state.evidence_tokens.append(pattern.consequence_token)
            state.active_event_keys.add(proposal.cooldown_key)
            state.consequence_ledger.append({"event_id": proposal.event_id, "pattern_id": proposal.pattern_id, "option_id": option_id, "day": state.day})
            state.state_version += 1
            proposal.lifecycle = "COMMITTED"
            return state
        except Exception:
            state.day = before["day"]
            state.water_litres = before["water_litres"]
            state.water_capacity_litres = before["water_capacity_litres"]
            state.pressure_psi = before["pressure_psi"]
            state.marks = before["marks"]
            state.evidence_tokens = list(before["evidence_tokens"])
            state.consequence_ledger = deepcopy(before["consequence_ledger"])
            state.active_event_keys = set(before["active_event_keys"])
            state.state_version = before["state_version"]
            proposal.lifecycle = "REJECTED"
            raise


def benchmark(*, count: int = 100, seed: int = 17) -> dict[str, Any]:
    forge = EventForge()
    valid = 0
    rejected = 0
    for index in range(count):
        state = generate_mockup_state(invalid=index % 10 == 0)
        try:
            forge.generate(state, seed=seed + index)
            valid += 1
        except ValidationError:
            rejected += 1
    return {"snapshots": count, "valid_proposals": valid, "incompatible_rejections": rejected}
