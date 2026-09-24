"""Selected B2 explicit sequence: charges, tags and separate replay."""

import copy
import json
from pathlib import Path
import unittest

from e7c_b1_canonical import canonical_bytes, digest
from e7c_success_sequence_b2 import (
    EDITION, FIRST, SequenceAdmissionError, admit, evaluate_sequence,
)
from e7c_success_sequence_checker_b2 import check_sequence
from test_e7_ir_named_maps_b1 import GRAPH, B, C, conventional, input_document

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/success_sequence.json"


def document(name="strict_normalise", *, binding=None, steps=20, ledger=20,
             first_capability=True, next_capability=True, next_obligation="resolved"):
    source = input_document(name, binding=binding, steps=steps, ledger=ledger,
                            capability=next_capability, obligation=next_obligation)
    source["edition"] = EDITION
    source["term"] = {"tag": "sequence_success", "first": copy.deepcopy(FIRST),
                      "then_map": name}
    source["interpretation"]["maps"]["total_identity"]["capability"] = first_capability
    return source


class SuccessSequence(unittest.TestCase):
    def test_canonical_complete_success_package(self):
        recorded = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(recorded) + b"\n")
        self.assertEqual(recorded, evaluate_sequence(document()))
        self.assertEqual(check_sequence(recorded["witness"])["status"], "accepted")
        self.assertEqual(recorded["terminal_outcome"]["value"],
                         conventional("strict_normalise", GRAPH)["value"])
        self.assertEqual(recorded["resource_progress"]["completed_steps"], 4)
        self.assertEqual([row["static_atom"]["dimension"] for row in recorded["ordered_ledger"]],
                         ["evidence", "evidence", "partiality"])
        self.assertEqual(recorded["terminal_outcome"]["optional_witness"], None)

    def test_success_failure_guard_and_budget_replay(self):
        for name in ("strict_normalise", "total_identity"):
            for binding in (GRAPH, B, C):
                for steps in range(5):
                    for ledger in range(4):
                        for first_capability, next_capability, next_obligation in (
                                (True, True, "resolved"), (False, True, "resolved"),
                                (True, False, "resolved"), (True, True, "unresolved")):
                            with self.subTest(name=name, binding=binding, steps=steps,
                                              ledger=ledger, first_capability=first_capability,
                                              next_capability=next_capability,
                                              next_obligation=next_obligation):
                                result = evaluate_sequence(document(
                                    name, binding=binding, steps=steps, ledger=ledger,
                                    first_capability=first_capability,
                                    next_capability=next_capability,
                                    next_obligation=next_obligation))
                                self.assertEqual(check_sequence(result["witness"])["status"], "accepted")
                                self.assertTrue(all(entry["static_atom"] in result["witness"]["static_judgement"]["effects"]
                                                    for entry in result["ordered_ledger"]))
                                self.assertLessEqual(result["resource_progress"]["completed_steps"], steps)
                                self.assertLessEqual(len(result["ordered_ledger"]), ledger)
                                if steps == 4 and ledger == 3 and first_capability and next_capability and next_obligation == "resolved":
                                    expected = conventional(name, binding)
                                    self.assertEqual(result["terminal_outcome"]["tag"], expected["tag"])
                                    self.assertEqual(result["terminal_outcome"].get("value", result["terminal_outcome"].get("diagnostic")),
                                                     expected.get("value", expected.get("diagnostic")))
                                if not first_capability and steps == 4 and ledger >= 1:
                                    self.assertEqual(result["terminal_outcome"]["tag"], "unsupported")
                                    self.assertEqual(len(result["ordered_ledger"]), 1)

    def test_rebound_claim_child_and_input_rejected(self):
        recorded = json.loads(FIXTURE.read_bytes())
        for mutate in (
                lambda w: w["claim"]["terminal_outcome"].update({"value": B}),
                lambda w: w["child_witness"]["runtime_inputs"]["values"].update({"source_config": B}),
                lambda w: w["source_document"]["values"].update({"source_config": B}),
                lambda w: w["static_judgement"].update({"effects": []}),
        ):
            with self.subTest(mutate=mutate):
                witness = copy.deepcopy(recorded["witness"])
                mutate(witness)
                witness["id"] = digest({k: v for k, v in witness.items() if k != "id"})
                self.assertEqual(check_sequence(witness)["status"], "rejected")
        bad = document(); bad["term"]["then_map"] = "unknown"
        with self.assertRaises(SequenceAdmissionError):
            admit(bad)
        bad = document(); bad["environment"]["maps"]["strict_normalise"]["source"] = {
            "tag": "config", "args": ["Sigma-B"]}
        with self.assertRaises(SequenceAdmissionError):
            admit(bad)

    def test_zero_step_has_no_child_and_rejects_rebound_child(self):
        result = evaluate_sequence(document(steps=0))
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["resource_progress"]["completed_steps"], 0)
        self.assertEqual(result["ordered_ledger"], [])
        self.assertIsNone(result["witness"]["child_witness"])
        self.assertEqual(check_sequence(result["witness"])["status"], "accepted")
        altered = copy.deepcopy(result["witness"])
        altered["child_witness"] = json.loads(FIXTURE.read_bytes())["witness"]["child_witness"]
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        self.assertEqual(check_sequence(altered)["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
