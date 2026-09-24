import copy
import json
from pathlib import Path
import unittest

from e7_ir_strict_map_b1 import (
    MapIRAdmissionError, compare_replay, execute, lower, parse, serialize,
)
from e7c_b1_canonical import canonical_bytes, digest
from e7c_b1_evaluator import evaluate

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "fixtures/wp5_ir/finite_graph_var.json"
REPLAY = ROOT / "fixtures/wp5_ir/strict_graph_map.json"
TERM = {"tag": "apply", "declaration": "strict_normalise",
        "arg": {"tag": "var", "name": "source_config"}}


def source_document(*, binding=None, steps=20, ledger=20, capability=True, obligation="resolved"):
    document = copy.deepcopy(json.loads(SEED.read_bytes())["source_document"])
    document["term"] = copy.deepcopy(TERM)
    if binding is not None:
        document["values"]["source_config"] = binding
    document["resource_policy"]["step_bound"] = steps
    document["resource_policy"]["ledger_entry_bound"] = ledger
    document["interpretation"]["maps"]["strict_normalise"]["capability"] = capability
    document["interpretation"]["maps"]["strict_normalise"]["obligation"] = obligation
    return document


def conventional_map(config):
    """Explicit control table for the selected graph and one outside-domain input."""
    table = [({"edges": ["AB"], "tag": None}, {"id": "A"}),
             ({"id": "b", "valid": False}, None)]
    for source, target in table:
        if config == source:
            return {"tag": "success", "value": target} if target else {
                "tag": "domain_error", "diagnostic": "outside-domain:strict_normalise"}
    raise ValueError("input outside conventional comparison table")


class StrictMapDifferential(unittest.TestCase):
    def test_success_fixture_replay_and_baseline(self):
        ir = json.loads(REPLAY.read_bytes())
        self.assertEqual(REPLAY.read_bytes(), canonical_bytes(ir) + b"\n")
        self.assertEqual(lower(source_document()), ir)
        self.assertEqual(parse(serialize(ir)), ir)
        matched = compare_replay(ir)
        self.assertEqual(matched["status"], "matched_selected_fragment")
        self.assertEqual(matched["ir_result"], execute(ir))
        direct = conventional_map(ir["argument_ir"]["binding"])
        self.assertEqual(direct["value"], matched["ir_result"]["terminal_outcome"]["value"])
        self.assertEqual(evaluate(ir["source_document"])["witness"], ir["source_witness"])

    def test_resource_order_domain_and_guard(self):
        cases = [
            ({"edges": ["AB"], "tag": None}, True, "resolved"),
            ({"id": "b", "valid": False}, True, "resolved"),
            ({"edges": ["AB"], "tag": None}, False, "resolved"),
            ({"edges": ["AB"], "tag": None}, True, "unresolved"),
        ]
        for binding, capability, obligation in cases:
            for steps in (0, 1, 2, 3):
                for ledger in (0, 1, 2, 3):
                    with self.subTest(binding=binding, steps=steps, ledger=ledger,
                                      capability=capability, obligation=obligation):
                        source = source_document(binding=binding, steps=steps, ledger=ledger,
                                                 capability=capability, obligation=obligation)
                        ir = lower(source)
                        self.assertEqual(compare_replay(ir)["ir_result"], execute(ir))
                        self.assertEqual(len(execute(ir)["ordered_ledger"]), min(ledger, 2)
                                         if steps >= 2 else 0)
                        if steps >= 2 and ledger >= 2 and capability and obligation == "resolved":
                            direct = conventional_map(binding)
                            actual = execute(ir)["terminal_outcome"]
                            self.assertEqual(actual["tag"], direct["tag"])
                            if actual["tag"] == "success":
                                self.assertEqual(actual["value"], direct["value"])
                            else:
                                self.assertEqual(actual["diagnostic"], direct["diagnostic"])

    def test_replay_integrity_and_identity(self):
        ir = json.loads(REPLAY.read_bytes())
        altered = copy.deepcopy(ir)
        altered["source_witness"]["runtime_inputs"]["values"]["source_config"] = {
            "id": "b", "valid": False}
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        with self.assertRaises(MapIRAdmissionError):
            execute(altered)
        altered = copy.deepcopy(ir)
        altered["argument_ir"]["binding"] = {"id": "b", "valid": False}
        altered["argument_ir"]["id"] = digest({k: v for k, v in altered["argument_ir"].items() if k != "id"})
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        with self.assertRaises(MapIRAdmissionError):
            execute(altered)
        altered = copy.deepcopy(ir)
        altered["required_capabilities"].append("future")
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        with self.assertRaises(MapIRAdmissionError):
            execute(altered)


if __name__ == "__main__":
    unittest.main()
