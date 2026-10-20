import unittest

from tools.event_forge.engine import EventForge, ValidationError, benchmark, generate_mockup_state


class EventForgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.forge = EventForge()

    def test_mockup_state_matches_documented_day_43_control(self) -> None:
        state = generate_mockup_state()
        self.assertEqual(state.day, 43)
        self.assertEqual(state.water_litres, 124)
        self.assertEqual(state.pressure_psi, 58)
        self.assertEqual(state.residents["sanna"].bond, 62)

    def test_all_ten_authored_patterns_are_registered(self) -> None:
        self.assertEqual([pattern.pattern_id for pattern in self.forge.patterns], [f"P{index:02d}" for index in range(1, 11)])

    def test_generation_is_deterministic_for_same_seed_and_state(self) -> None:
        first = self.forge.generate(generate_mockup_state(), seed=7).to_dict()
        second = self.forge.generate(generate_mockup_state(), seed=7).to_dict()
        self.assertEqual(first, second)

    def test_proposal_has_complete_contract(self) -> None:
        proposal = self.forge.generate(generate_mockup_state(), seed=7)
        for key in ("event_id", "pattern_id", "seed", "trigger_facts", "state_version", "actor_ids", "location_ids", "options", "preconditions", "proposed_effects", "expiry_day", "cooldown_key"):
            self.assertIn(key, proposal.to_dict())

    def test_corrupted_proposal_is_rejected(self) -> None:
        state = generate_mockup_state()
        proposal = self.forge.generate(state, seed=7)
        proposal.eligibility["actor_alive"] = False
        with self.assertRaises(ValidationError):
            self.forge.validate(state, proposal)

    def test_stale_proposal_is_rejected_after_actor_dies(self) -> None:
        state = generate_mockup_state()
        proposal = self.forge.generate(state, seed=7)
        state.residents[proposal.actor_ids[0]].alive = False
        state.state_version += 1
        with self.assertRaises(ValidationError):
            self.forge.validate(state, proposal)

    def test_stale_proposal_is_rejected_after_state_changes(self) -> None:
        state = generate_mockup_state()
        proposal = self.forge.generate(state, seed=7)
        state.marks += 1
        with self.assertRaises(ValidationError):
            self.forge.validate(state, proposal)

    def test_commit_is_atomic_and_records_consequence(self) -> None:
        state = generate_mockup_state()
        proposal = self.forge.generate(state, seed=7)
        before_version = state.state_version
        self.forge.commit(state, proposal, "report")
        self.assertEqual(state.state_version, before_version + 1)
        self.assertEqual(state.consequence_ledger[-1]["event_id"], proposal.event_id)
        self.assertIn(proposal.proposed_effects["evidence_token"], state.evidence_tokens)

    def test_duplicate_active_event_is_rejected(self) -> None:
        state = generate_mockup_state()
        proposal = self.forge.generate(state, seed=7)
        self.forge.commit(state, proposal)
        with self.assertRaises(ValidationError):
            self.forge.generate(state, seed=7)

    def test_invalid_snapshot_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.forge.generate(generate_mockup_state(invalid=True), seed=7)

    def test_benchmark_has_ninety_valid_and_ten_incompatible_snapshots(self) -> None:
        self.assertEqual(benchmark(), {"snapshots": 100, "valid_proposals": 90, "incompatible_rejections": 10})


if __name__ == "__main__":
    unittest.main()
