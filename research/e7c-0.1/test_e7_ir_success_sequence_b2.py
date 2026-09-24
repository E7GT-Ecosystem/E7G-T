import copy
import json
from pathlib import Path
import unittest

from e7_ir_success_sequence_b2 import (
    SequenceIRAdmissionError, compare_replay, execute, lower, parse, serialize,
)
from e7c_b1_canonical import canonical_bytes, digest
from e7c_success_sequence_b2 import evaluate_sequence
from e7c_success_sequence_checker_b2 import check_sequence
from test_e7c_success_sequence_b2 import document
from test_e7_ir_named_maps_b1 import GRAPH, B, C

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/success_sequence_ir.json"


class SequencingIR(unittest.TestCase):
    def test_pinned_full_replay_and_typed_lowering(self):
        encoded = FIXTURE.read_bytes()
        ir = json.loads(encoded)
        self.assertEqual(encoded, canonical_bytes(ir) + b"\n")
        self.assertEqual(ir, lower(document()))
        self.assertEqual(parse(serialize(ir)), ir)
        self.assertEqual(compare_replay(ir)["status"], "matched_selected_success_sequence")
        self.assertEqual(execute(ir), evaluate_sequence(ir["source_document"])["witness"]["claim"])
        self.assertEqual(check_sequence(ir["source_witness"])["status"], "accepted")
        self.assertEqual(ir["instruction"]["intermediate_type"],
                         ir["source_document"]["environment"]["maps"]["strict_normalise"]["source"])

    def test_budget_and_failure_correspondence(self):
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
                                source = document(name, binding=binding, steps=steps,
                                                  ledger=ledger, first_capability=first_capability,
                                                  next_capability=next_capability,
                                                  next_obligation=next_obligation)
                                ir = lower(source)
                                self.assertEqual(compare_replay(ir)["ir_result"],
                                                 evaluate_sequence(source)["witness"]["claim"])

    def test_rebound_type_source_and_witness_rejected(self):
        ir = json.loads(FIXTURE.read_bytes())
        for mutation in (
                lambda x: x["instruction"].update({"intermediate_type": {"tag": "config", "args": ["Sigma-B"]}}),
                lambda x: x["argument_ir"].update({"binding": B}),
                lambda x: x["source_witness"]["claim"]["terminal_outcome"].update({"value": B}),
        ):
            with self.subTest(mutation=mutation):
                altered = copy.deepcopy(ir)
                mutation(altered)
                altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
                with self.assertRaises(SequenceIRAdmissionError):
                    execute(altered)


if __name__ == "__main__":
    unittest.main()
