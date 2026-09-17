from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent


class WitnessContractSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = (HERE / "E7C_0.1_WITNESS_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        cls.normalized = " ".join(cls.spec.split())

    def test_contract_is_specification_only(self):
        self.assertIn("witness_contract_accepted_for_bounded_wp3_i", self.spec)
        self.assertIn("It is a specification only", self.spec)
        self.assertIn("contains no evaluator", self.normalized)

    def test_witness_binds_all_replay_inputs(self):
        for field_group in (
            "rule pins",
            "evaluation claim",
            "static inputs",
            "runtime inputs",
            "resource input",
            "derivation record",
            "external assumptions",
            "integrity",
        ):
            self.assertIn(f"| {field_group} |", self.spec)

    def test_hash_only_or_redacted_material_is_not_replayable(self):
        self.assertIn("A digest alone proves neither availability nor meaning", self.spec)
        self.assertIn("`missing_replay_material`", self.spec)
        self.assertIn("audit commitment, not a replayable B1 witness", self.normalized)

    def test_integrity_identity_is_not_self_referential(self):
        self.assertIn("digest payload omits `witness_identifier`", self.spec)
        self.assertIn("`omega:root_digest`", self.spec)

    def test_root_digest_omits_nested_optional_witness_reference(self):
        self.assertIn(
            "`terminal_outcome.success.optional_witness`", self.spec
        )
        self.assertIn(
            "Only after the root digest is fixed, bind that identifier",
            self.normalized,
        )
        self.assertIn(
            "nested field is omitted from the evaluation-claim digest payload",
            self.normalized,
        )

    def test_node_digest_omits_its_own_identifier(self):
        self.assertIn("digest payload omits its own `node_id`", self.spec)
        self.assertIn("Derive node identifiers bottom-up", self.spec)
        self.assertIn("explicitly excludes its own `node_id`", self.spec)

    def test_checker_is_independent_and_recomputes(self):
        self.assertIn("must not import evaluator code", self.spec)
        self.assertIn("rerun WP2 admission", self.spec)
        self.assertIn("independently implemented WP3-S rule engine", self.spec)
        self.assertIn("return `accepted` only on exact equality", self.spec)

    def test_source_truth_and_authority_are_excluded(self):
        self.assertIn("source bytes are authentic, complete, current or true | not established", self.spec)
        self.assertIn("source/provider has legitimate domain authority | not established", self.spec)
        self.assertIn(
            "They are never converted into `authority_verified`", self.normalized
        )

    def test_replay_claim_is_bounded_and_edition_pinned(self):
        self.assertIn("one replayed derivation", self.spec)
        self.assertIn(
            "Replaying under a different edition is a new claim", self.normalized
        )
        self.assertIn("only for the pinned finite carrier", self.spec)

    def test_required_adversarial_cases_are_named(self):
        for diagnostic in (
            "digest_mismatch",
            "edition_mismatch",
            "derivation_order_mismatch",
            "resource_accounting_mismatch",
            "ledger_mismatch",
            "outcome_mismatch",
            "authority_claim_escalation",
        ):
            self.assertIn(diagnostic, self.spec)

    def test_claim_class_and_host_execution_cannot_escalate_trust(self):
        self.assertIn("fixed claim class `bounded_derivation_replay`", self.spec)
        self.assertIn("No interpretation field contains executable host-language code", self.spec)
        self.assertIn("replay trusted base is limited", self.normalized)

    def test_wp3_i_is_blocked_with_required_first_tests(self):
        self.assertIn("WP3-I was blocked until review accepted this contract", self.spec)
        for requirement in (
            "outcome propagation",
            "resource/failure precedence",
            "ordered ledgers",
            "fibre reconstruction",
            "separately implemented checker",
        ):
            self.assertIn(requirement, self.spec)


if __name__ == "__main__":
    unittest.main()
