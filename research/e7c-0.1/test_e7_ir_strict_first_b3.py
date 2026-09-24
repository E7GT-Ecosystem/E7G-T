"""B3 typed IR differential across strict first success and failure."""

import copy
import json
from pathlib import Path
import unittest

from e7c_b1_canonical import canonical_bytes, digest
from e7_ir_strict_first_b3 import (
    SequenceIRAdmissionError, compare_replay, execute, lower, parse, serialize,
)
from test_e7c_strict_first_b3 import B, C, GRAPH, document

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/strict_first_ir_b3.json"


class StrictFirstIR(unittest.TestCase):
    def test_complete_fixture_and_types(self):
        package = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(package) + b"\n")
        self.assertEqual(package, lower(document()))
        self.assertEqual(parse(serialize(package)), package)
        self.assertEqual(compare_replay(package)["ir_result"], execute(package))
        self.assertNotEqual(package["instruction"]["input_type"],
                            package["instruction"]["intermediate_type"])
        self.assertEqual(package["instruction"]["intermediate_type"],
                         package["instruction"]["output_type"])

    def test_finite_differential(self):
        for binding in (GRAPH, B, C):
            for steps in range(5):
                for ledger in range(4):
                    for capability, obligation, next_capability in (
                            (True, "resolved", True), (False, "resolved", True),
                            (True, "unresolved", True), (True, "resolved", False)):
                        with self.subTest(binding=binding, steps=steps, ledger=ledger):
                            package = lower(document(
                                binding=binding, steps=steps, ledger=ledger,
                                first_capability=capability, first_obligation=obligation,
                                next_capability=next_capability))
                            self.assertEqual(compare_replay(package)["ir_result"], execute(package))
                            if binding == B and steps == 4 and ledger == 3 and capability and obligation == "resolved":
                                self.assertEqual(execute(package)["terminal_outcome"]["tag"], "domain_error")
                                self.assertEqual(len(execute(package)["ordered_ledger"]), 2)

    def test_rebinding_rejected(self):
        package = json.loads(FIXTURE.read_bytes())
        for change in (
                lambda p: p["instruction"].update({"intermediate_type": p["instruction"]["input_type"]}),
                lambda p: p["argument_ir"].update({"binding": B}),
                lambda p: p["source_witness"]["claim"]["terminal_outcome"].update({"value": {"id": "C"}}),
        ):
            altered = copy.deepcopy(package)
            change(altered)
            altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
            with self.assertRaises(SequenceIRAdmissionError):
                execute(altered)


if __name__ == "__main__":
    unittest.main()
