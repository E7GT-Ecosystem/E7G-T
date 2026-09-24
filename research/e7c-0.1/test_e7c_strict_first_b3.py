"""Finite, typed strict-first sequence with complete independent replay."""

import copy
import json
from pathlib import Path
import unittest

from e7c_b1_canonical import canonical_bytes, digest
from e7c_strict_first_b3 import EDITION, FIRST, SequenceAdmissionError, admit, evaluate_sequence
from e7c_strict_first_checker_b3 import check_sequence
from test_e7_ir_named_maps_b1 import GRAPH, B, C, conventional, input_document

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/strict_first_b3.json"
FAILURE_FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/strict_first_domain_error_b3.json"


def document(*, binding=None, steps=20, ledger=20, first_capability=True,
             first_obligation="resolved", next_capability=True,
             next_obligation="resolved"):
    source = input_document("strict_normalise", binding=binding, steps=steps, ledger=ledger,
                            capability=first_capability, obligation=first_obligation)
    source["edition"] = EDITION
    source["term"] = {"tag": "sequence_success", "first": copy.deepcopy(FIRST),
                      "then_map": "total_identity_b"}
    source["environment"]["maps"]["total_identity_b"] = {
        "domain_policy": "total", "failure_family": "no-domain-errors-1",
        "map_edition": "map-identity-b-1", "outcome_extension": "core-1",
        "source": {"tag": "config", "args": ["Sigma-B"]},
        "target": {"tag": "config", "args": ["Sigma-B"]},
    }
    source["interpretation"]["maps"]["total_identity_b"] = {
        "capability": next_capability, "obligation": next_obligation,
        "cases": [
            {"in_domain": True, "input": {"id": "A"}, "output": {"id": "A"}},
            {"in_domain": True, "input": {"id": "C"}, "output": {"id": "C"}},
        ],
    }
    return source


class StrictFirst(unittest.TestCase):
    def test_complete_fixture_and_control(self):
        recorded = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(recorded) + b"\n")
        self.assertEqual(recorded, evaluate_sequence(document()))
        self.assertEqual(check_sequence(recorded["witness"])["status"], "accepted")
        self.assertEqual(recorded["terminal_outcome"]["value"],
                         conventional("strict_normalise", GRAPH)["value"])
        self.assertEqual(recorded["resource_progress"]["completed_steps"], 4)
        self.assertEqual([(e["detail"]["declaration"], e["static_atom"]["dimension"])
                          for e in recorded["ordered_ledger"]],
                         [("strict_normalise", "evidence"),
                          ("strict_normalise", "partiality"),
                         ("total_identity_b", "evidence")])

    def test_complete_failure_fixture(self):
        recorded = json.loads(FAILURE_FIXTURE.read_bytes())
        self.assertEqual(FAILURE_FIXTURE.read_bytes(), canonical_bytes(recorded) + b"\n")
        self.assertEqual(recorded, evaluate_sequence(document(binding=B)))
        self.assertEqual(check_sequence(recorded["witness"])["status"], "accepted")
        self.assertEqual(recorded["terminal_outcome"]["tag"], "domain_error")
        self.assertEqual(recorded["terminal_outcome"]["diagnostic"],
                         "outside-domain:strict_normalise")
        self.assertEqual(recorded["resource_progress"]["completed_steps"], 3)
        self.assertEqual([e["detail"]["declaration"] for e in recorded["ordered_ledger"]],
                         ["strict_normalise", "strict_normalise"])

    def test_finite_tags_budget_and_failure_short_circuit(self):
        for binding in (GRAPH, B, C):
            for steps in range(5):
                for ledger in range(4):
                    for first_capability, first_obligation, next_capability in (
                            (True, "resolved", True), (False, "resolved", True),
                            (True, "unresolved", True), (True, "resolved", False)):
                        with self.subTest(binding=binding, steps=steps, ledger=ledger,
                                          first_capability=first_capability,
                                          first_obligation=first_obligation,
                                          next_capability=next_capability):
                            result = evaluate_sequence(document(
                                binding=binding, steps=steps, ledger=ledger,
                                first_capability=first_capability,
                                first_obligation=first_obligation,
                                next_capability=next_capability))
                            self.assertEqual(check_sequence(result["witness"])["status"], "accepted")
                            self.assertLessEqual(result["resource_progress"]["completed_steps"], steps)
                            self.assertLessEqual(len(result["ordered_ledger"]), ledger)
                            self.assertTrue(all(e["static_atom"] in result["witness"]["static_judgement"]["effects"]
                                                for e in result["ordered_ledger"]))
                            if steps == 4 and ledger == 3 and first_capability and first_obligation == "resolved":
                                if binding == B:
                                    self.assertEqual(result["terminal_outcome"]["tag"], "domain_error")
                                    self.assertEqual(len(result["ordered_ledger"]), 2)
                                    self.assertTrue(all(e["detail"]["declaration"] == "strict_normalise"
                                                        for e in result["ordered_ledger"]))
                                elif next_capability:
                                    self.assertEqual(result["terminal_outcome"]["value"],
                                                     conventional("strict_normalise", binding)["value"])

    def test_rebinding_and_ill_typed_continuation(self):
        recorded = json.loads(FIXTURE.read_bytes())
        for mutation in (
                lambda w: w["claim"]["terminal_outcome"].update({"value": {"id": "C"}}),
                lambda w: w["child_witness"]["runtime_inputs"]["values"].update({"source_config": B}),
                lambda w: w["static_judgement"].update({"effects": []}),
        ):
            altered = copy.deepcopy(recorded["witness"])
            mutation(altered)
            altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
            self.assertEqual(check_sequence(altered)["status"], "rejected")
        wrong = document()
        wrong["environment"]["maps"]["total_identity_b"]["source"]["args"] = ["Sigma-A"]
        with self.assertRaises(SequenceAdmissionError):
            admit(wrong)
        wrong = document()
        wrong["interpretation"]["maps"]["total_identity_b"]["cases"][0]["output"] = {"id": "C"}
        with self.assertRaises(SequenceAdmissionError):
            admit(wrong)


if __name__ == "__main__":
    unittest.main()
