"""CARDO REI claim kernel.

The kernel is intentionally small and dependency-free.  Producers describe
what they executed; this module decides whether the resulting claim is
authorized.  A producer cannot set its own authorization bit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "cardo-claim-1.0"


class Verdict(str, Enum):
    UNIMPLEMENTED = "UNIMPLEMENTED"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"
    ERROR = "ERROR"
    FAIL = "FAIL"
    PASS_SCOPED = "PASS_SCOPED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    implementation: str | None
    implemented: bool


@dataclass(frozen=True)
class ProofObligation:
    obligation_id: str
    capability_id: str
    predicate: str
    executed: bool = False
    satisfied: bool = False
    evidence_refs: tuple[str, ...] = ()
    counterevidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Provenance:
    candidate_path: str
    candidate_sha256: str
    source_revision: str
    reproduction_command: str
    tool_versions: Mapping[str, str] = field(default_factory=dict)
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaimEnvelope:
    claim_id: str
    scope: str
    requested_verdict: Verdict
    capabilities: tuple[Capability, ...]
    obligations: tuple[ProofObligation, ...]
    provenance: Provenance
    known_exclusions: tuple[str, ...] = ()
    unexecuted_checks: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def evaluate(self) -> dict[str, Any]:
        reasons = list(validate_envelope(self))
        authorized = self.requested_verdict is Verdict.PASS_SCOPED and not reasons
        verdict = self.requested_verdict if authorized else fail_closed_verdict(self, reasons)
        record = asdict(self)
        record["requested_verdict"] = self.requested_verdict.value
        record["verdict"] = verdict.value
        record["claim_authorized"] = authorized
        record["authorization_failures"] = reasons
        return record


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_envelope(envelope: ClaimEnvelope) -> Iterable[str]:
    capability_ids = {capability.capability_id for capability in envelope.capabilities}
    implemented_ids = {
        capability.capability_id
        for capability in envelope.capabilities
        if capability.implemented and capability.implementation
    }
    if not envelope.claim_id.strip():
        yield "claim_id_missing"
    if not envelope.scope.strip():
        yield "scope_missing"
    if not envelope.obligations:
        yield "proof_obligations_missing"
    if not envelope.provenance.candidate_sha256:
        yield "candidate_hash_missing"
    if not envelope.provenance.source_revision:
        yield "source_revision_missing"
    if not envelope.provenance.reproduction_command:
        yield "reproduction_command_missing"
    for obligation in envelope.obligations:
        if obligation.capability_id not in capability_ids:
            yield f"{obligation.obligation_id}:capability_undeclared"
        elif obligation.capability_id not in implemented_ids:
            yield f"{obligation.obligation_id}:capability_unimplemented"
        if not obligation.executed:
            yield f"{obligation.obligation_id}:not_executed"
        elif not obligation.satisfied:
            yield f"{obligation.obligation_id}:not_satisfied"
        if obligation.executed and not obligation.evidence_refs:
            yield f"{obligation.obligation_id}:evidence_missing"
        if obligation.executed and not obligation.counterevidence_refs:
            yield f"{obligation.obligation_id}:counterevidence_missing"
    if envelope.unexecuted_checks:
        yield "unexecuted_checks_present"


def fail_closed_verdict(envelope: ClaimEnvelope, reasons: list[str]) -> Verdict:
    if any("capability_unimplemented" in reason for reason in reasons):
        return Verdict.UNIMPLEMENTED
    if any("not_executed" in reason for reason in reasons):
        return Verdict.NOT_RUN
    if any("not_satisfied" in reason for reason in reasons):
        return Verdict.FAIL
    if envelope.requested_verdict is Verdict.PASS_SCOPED:
        return Verdict.INVALIDATED
    return envelope.requested_verdict


def write_claim(path: Path, envelope: ClaimEnvelope) -> dict[str, Any]:
    record = envelope.evaluate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def validate_record(record: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if record.get("schema_version") != SCHEMA_VERSION:
        failures.append("schema_version_invalid")
    capabilities = record.get("capabilities")
    obligations = record.get("obligations")
    provenance = record.get("provenance")
    if not isinstance(capabilities, list):
        failures.append("capabilities_missing")
        capabilities = []
    if not isinstance(obligations, list) or not obligations:
        failures.append("proof_obligations_missing")
        obligations = []
    if not isinstance(provenance, dict):
        failures.append("provenance_missing")
        provenance = {}

    implemented = {
        item.get("capability_id")
        for item in capabilities
        if isinstance(item, dict) and item.get("implemented") is True and item.get("implementation")
    }
    proof_failures: list[str] = []
    for item in obligations:
        if not isinstance(item, dict):
            proof_failures.append("obligation_invalid")
            continue
        obligation_id = item.get("obligation_id", "UNKNOWN")
        if item.get("capability_id") not in implemented:
            proof_failures.append(f"{obligation_id}:capability_unimplemented")
        if item.get("executed") is not True:
            proof_failures.append(f"{obligation_id}:not_executed")
        elif item.get("satisfied") is not True:
            proof_failures.append(f"{obligation_id}:not_satisfied")
        if item.get("executed") is True and not item.get("evidence_refs"):
            proof_failures.append(f"{obligation_id}:evidence_missing")
        if item.get("executed") is True and not item.get("counterevidence_refs"):
            proof_failures.append(f"{obligation_id}:counterevidence_missing")
    for key in ("candidate_sha256", "source_revision", "reproduction_command"):
        if not provenance.get(key):
            proof_failures.append(f"{key}_missing")
    if record.get("unexecuted_checks"):
        proof_failures.append("unexecuted_checks_present")

    independently_authorized = (
        record.get("requested_verdict") == Verdict.PASS_SCOPED.value and not proof_failures
    )
    recorded_authorized = record.get("claim_authorized") is True
    if recorded_authorized != independently_authorized:
        failures.append("authorization_mismatch")
    if independently_authorized and record.get("verdict") != Verdict.PASS_SCOPED.value:
        failures.append("authorized_non_pass_verdict")
    if not independently_authorized and record.get("verdict") == Verdict.PASS_SCOPED.value:
        failures.append("unauthorized_pass_verdict")
    recorded_failures = record.get("authorization_failures")
    if not isinstance(recorded_failures, list):
        failures.append("authorization_failures_missing")
    elif set(recorded_failures) != set(proof_failures):
        failures.append("authorization_failures_mismatch")
    return failures
