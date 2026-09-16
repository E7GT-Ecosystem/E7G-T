from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent


class WP3SemanticsSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = (HERE / "E7C_0.1_DYNAMIC_DENOTATIONAL_SEMANTICS.md").read_text(
            encoding="utf-8"
        )
        cls.normalized = " ".join(cls.spec.split())

    def test_is_specification_only(self):
        self.assertIn("wp3_specification_drafted_unimplemented", self.spec)
        self.assertIn("It is a specification only", self.spec)
        self.assertIn("No row is implemented by this package", self.spec)

    def test_admission_diagnostics_remain_outside_evaluation(self):
        self.assertIn(
            "`invalid_input` and `type_error` remain checker diagnostics outside this relation",
            self.normalized,
        )

    def test_outcome_normal_amendment_has_direct_terminal_rule(self):
        self.assertIn("WP3-GAP-001", self.spec)
        self.assertIn("`E7C-S013`", self.spec)
        self.assertIn("x \\Downarrow (o,[])", self.spec)
        self.assertIn("not `success(o,none)`", self.spec)
        self.assertIn("`Family[I,Outcome[A,xi]]`", self.spec)
        self.assertIn("any value position beneath another type constructor", self.normalized)
        self.assertIn("WP3-I remains blocked", self.spec)

    def test_resource_charges_and_precedence_are_exact(self):
        for phrase in (
            "before variable lookup or argument evaluation",
            "Immediately before each required ledger append",
            "Immediately before each candidate predicate or equality check",
            "Resource checks and semantic failures are resolved by program order",
            "zero step bound makes even variable lookup return `resource_limit`",
            "ledger bound exhausted at `evidence` or `partiality` wins",
        ):
            self.assertIn(phrase, self.normalized)

    def test_every_terminal_outcome_is_named(self):
        for outcome in (
            "success(v, optional_witness)",
            "domain_error(diagnostic)",
            "unsupported(capability)",
            "undetermined(obligation)",
            "resource_limit(bound, progress)",
        ):
            self.assertIn(outcome, self.spec)

    def test_every_wp2_constructor_has_correspondence_row(self):
        for constructor in (
            "`var`",
            "`apply`",
            "`view` (source-preserving)",
            "`view` (projection)",
            "`restrict`",
            "`reconstruct`",
            "`classify`",
        ):
            self.assertIn(f"| {constructor} |", self.spec)

    def test_ledger_contract_preserves_failure_prefix(self):
        self.assertIn(r"\mathsf{atoms}(\lambda) \subseteq \varepsilon", self.spec)
        self.assertIn("retains the complete ledger prefix", self.normalized)
        self.assertIn("stable concatenation, not set union", self.normalized)

    def test_reconstruction_cannot_report_partial_success(self):
        self.assertIn("No rule returns a successful incomplete subset", self.spec)
        self.assertIn(
            "Projection values have no exact-reconstruction rule", self.normalized
        )

    def test_observation_keeps_outcomes_and_ledgers_distinct(self):
        self.assertIn(
            "Same success value with different loss, evidence, alternatives, order, failure tag or resource progress is not equivalent by default",
            self.normalized,
        )

    def test_proof_claims_remain_deferred(self):
        self.assertIn("Both directions are `statement_drafted`", self.spec)
        self.assertIn("Proof belongs to WP4", self.spec)


if __name__ == "__main__":
    unittest.main()
