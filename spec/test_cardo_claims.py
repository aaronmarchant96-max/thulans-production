from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.audit_claim_records import audit
from tools.cardo_claims import (
    Capability,
    ClaimEnvelope,
    ProofObligation,
    Provenance,
    Verdict,
    write_claim,
)


def provenance() -> Provenance:
    return Provenance(
        candidate_path="candidate.blend",
        candidate_sha256="abc123",
        source_revision="deadbeef",
        reproduction_command="python verify.py",
    )


class ClaimKernelTests(unittest.TestCase):
    def test_producer_cannot_authorize_unimplemented_pass(self):
        envelope = ClaimEnvelope(
            claim_id="TEST.CLAIM",
            scope="test",
            requested_verdict=Verdict.PASS_SCOPED,
            capabilities=(Capability("simulation", None, False),),
            obligations=(ProofObligation("TEST.OBLIGATION", "simulation", "value < 1"),),
            provenance=provenance(),
        )

        record = envelope.evaluate()

        self.assertFalse(record["claim_authorized"])
        self.assertEqual(record["verdict"], "UNIMPLEMENTED")
        self.assertIn("TEST.OBLIGATION:capability_unimplemented", record["authorization_failures"])

    def test_scoped_pass_requires_execution_evidence_and_counterevidence(self):
        envelope = ClaimEnvelope(
            claim_id="TEST.CLAIM",
            scope="test",
            requested_verdict=Verdict.PASS_SCOPED,
            capabilities=(Capability("simulation", "verify.py", True),),
            obligations=(
                ProofObligation(
                    "TEST.OBLIGATION",
                    "simulation",
                    "value < 1",
                    executed=True,
                    satisfied=True,
                    evidence_refs=("evidence/measurement.json",),
                    counterevidence_refs=("evidence/negative-control.json",),
                ),
            ),
            provenance=provenance(),
        )

        record = envelope.evaluate()

        self.assertTrue(record["claim_authorized"])
        self.assertEqual(record["verdict"], "PASS_SCOPED")
        self.assertEqual(record["authorization_failures"], [])

    def test_unexecuted_checks_invalidate_an_otherwise_valid_pass(self):
        envelope = ClaimEnvelope(
            claim_id="TEST.CLAIM",
            scope="test",
            requested_verdict=Verdict.PASS_SCOPED,
            capabilities=(Capability("simulation", "verify.py", True),),
            obligations=(
                ProofObligation(
                    "TEST.OBLIGATION",
                    "simulation",
                    "value < 1",
                    executed=True,
                    satisfied=True,
                    evidence_refs=("positive.json",),
                    counterevidence_refs=("negative.json",),
                ),
            ),
            provenance=provenance(),
            unexecuted_checks=("robustness sweep",),
        )

        record = envelope.evaluate()

        self.assertFalse(record["claim_authorized"])
        self.assertEqual(record["verdict"], "INVALIDATED")

    def test_scanner_rejects_tampered_canonical_record(self):
        envelope = ClaimEnvelope(
            claim_id="TEST.CLAIM",
            scope="test",
            requested_verdict=Verdict.UNIMPLEMENTED,
            capabilities=(Capability("simulation", None, False),),
            obligations=(ProofObligation("TEST.OBLIGATION", "simulation", "value < 1"),),
            provenance=provenance(),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence" / "claim.json"
            record = write_claim(path, envelope)
            record["claim_authorized"] = True
            path.write_text(json.dumps(record), encoding="utf-8")

            failures, _ = audit(root)

        self.assertIn("evidence/claim.json: authorization_mismatch", failures)

    def test_scanner_recomputes_forged_pass_authorization(self):
        envelope = ClaimEnvelope(
            claim_id="TEST.CLAIM",
            scope="test",
            requested_verdict=Verdict.PASS_SCOPED,
            capabilities=(Capability("simulation", None, False),),
            obligations=(ProofObligation("TEST.OBLIGATION", "simulation", "value < 1"),),
            provenance=provenance(),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence" / "claim.json"
            record = write_claim(path, envelope)
            record["claim_authorized"] = True
            record["verdict"] = "PASS_SCOPED"
            record["authorization_failures"] = []
            path.write_text(json.dumps(record), encoding="utf-8")

            failures, _ = audit(root)

        self.assertIn("evidence/claim.json: authorization_mismatch", failures)
        self.assertIn("evidence/claim.json: unauthorized_pass_verdict", failures)
        self.assertIn("evidence/claim.json: authorization_failures_mismatch", failures)

    def test_scanner_does_not_inventory_agent_task_metadata_as_legacy_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evidence" / "agent-tasks" / "task.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "schema": "thulans-agent-task-1.0",
                        "task_id": "TASK-001",
                        "verdict": "PASS_SCOPED",
                    }
                ),
                encoding="utf-8",
            )

            failures, legacy = audit(root)

        self.assertEqual(failures, [])
        self.assertEqual(legacy, [])


if __name__ == "__main__":
    unittest.main()
