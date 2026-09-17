import copy
from pathlib import Path
import unittest

from e7c_b1_canonical import canonical_key
from e7c_b1_evaluator import evaluate
from test_wp3_i import CLASSIFY, RECONSTRUCT, RESTRICT, STRICT, VAR, VIEW, document


HERE = Path(__file__).resolve().parent


class WP4SpecificationControlTests(unittest.TestCase):
    def test_required_metatheory_files_and_boundaries(self):
        obligations = (HERE / "E7C_0.1_PROOF_OBLIGATIONS.md").read_text(encoding="utf-8")
        catalogue = (HERE / "E7C_0.1_COUNTEREXAMPLE_CATALOGUE.md").read_text(encoding="utf-8")
        selection = (HERE / "E7C_0.1_PROOF_ASSISTANT_SELECTION.md").read_text(encoding="utf-8")
        for theorem in range(1, 18):
            heading = f"### E7C-T{theorem:03d}"
            self.assertIn(heading, obligations)
            section = obligations.split(heading, 1)[1].split("\n### E7C-T", 1)[0]
            self.assertIn("Applicable hypotheses", section)
            self.assertIn("Exact statement", section)
            self.assertIn("Status", section)
            self.assertIn("Counterexample search", section)
            self.assertIn("Mechanisation disposition", section)
        for counterexample in range(1, 28):
            self.assertIn(f"CE-{counterexample:03d}", catalogue)
        self.assertIn("selection_deferred; lean_executable_candidate_review_pending", selection)
        self.assertIn("not an acceptance verdict", selection)
        self.assertIn("does not establish", obligations)
        self.assertNotIn("Status: `mechanised`", obligations)

    def test_progress_and_replay_claims_are_explicitly_split(self):
        obligations = (HERE / "E7C_0.1_PROOF_OBLIGATIONS.md").read_text(encoding="utf-8")
        self.assertIn("Exact statement T009A", obligations)
        self.assertIn("Exact statement T009B", obligations)
        self.assertIn("`EvaluationInputError`", obligations)
        self.assertIn("Exact statement T011A", obligations)
        self.assertIn("Exact statement T011B", obligations)
        self.assertIn("ReplayMachine adequacy to WP3-S", obligations)
        self.assertIn("T011B remains blocked until", obligations)


class WP4BoundedEvidenceTests(unittest.TestCase):
    TERMS = (VAR, STRICT, VIEW, RESTRICT, RECONSTRUCT, CLASSIFY)

    def test_repeated_evaluation_is_byte_structurally_deterministic(self):
        for term in self.TERMS:
            source = document(term)
            first = evaluate(copy.deepcopy(source))
            second = evaluate(copy.deepcopy(source))
            self.assertEqual(first, second)

    def test_every_ledger_atom_is_within_the_static_effect_bound(self):
        for term in self.TERMS:
            result = evaluate(document(term))
            static_atoms = {
                canonical_key(atom)
                for atom in result["witness"]["evaluation_claim"]["static_judgement"]["effects"]
            }
            runtime_atoms = {
                canonical_key(entry["static_atom"])
                for entry in result["ordered_ledger"]
            }
            self.assertLessEqual(runtime_atoms, static_atoms)

    def test_all_small_resource_bounds_return_declared_outcomes(self):
        declared = {"success", "domain_error", "unsupported", "undetermined", "resource_limit"}
        for term in self.TERMS:
            for steps in range(4):
                for candidates in range(4):
                    for ledger in range(4):
                        result = evaluate(document(term, steps=steps, candidates=candidates, ledger=ledger))
                        self.assertIn(result["terminal_outcome"]["tag"], declared)

    def test_successful_reconstruction_is_the_exact_fixture_fibre(self):
        result = evaluate(document(RECONSTRUCT))
        self.assertEqual(result["terminal_outcome"]["tag"], "success")
        self.assertEqual(
            result["terminal_outcome"]["value"],
            [{"id": "a", "valid": True}, {"id": "c", "valid": True}],
        )
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 3)

    def test_interrupted_enumerators_never_report_success(self):
        for term, bound in ((RESTRICT, 2), (RECONSTRUCT, 2), (CLASSIFY, 1)):
            result = evaluate(document(term, candidates=bound))
            self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
            self.assertNotIn("value", result["terminal_outcome"])


if __name__ == "__main__":
    unittest.main()
