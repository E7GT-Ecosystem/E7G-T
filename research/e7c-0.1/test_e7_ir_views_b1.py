"""Finite view/IR differential preserves the source-token versus loss boundary."""

import copy
import json
from pathlib import Path
import unittest

from e7_ir_views_b1 import ViewIRAdmissionError, compare_replay, execute, lower, parse, serialize
from e7c_b1_canonical import canonical_bytes, digest
from e7c_b1_evaluator import EvaluationInputError, evaluate
from test_e7_ir_named_maps_b1 import input_document, GRAPH, B, C

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures/wp5_ir"
VIEWS = ("source_preserving_inventory", "lossy_projection")


def source_document(name, *, binding=None, steps=20, ledger=20,
                    capability=True, obligation="resolved"):
    source = input_document(binding=binding, steps=steps, ledger=ledger)
    source["term"] = {"tag": "view", "declaration": name,
                      "arg": {"tag": "var", "name": "source_config"}}
    source["interpretation"]["views"][name]["capability"] = capability
    source["interpretation"]["views"][name]["obligation"] = obligation
    return source


def conventional(name, binding):
    """Plain finite lookup with an explicit retained source token policy."""
    entries = [(GRAPH, "one", 1), (B, "two", 2), (C, "one", 3)]
    for config, bucket, count in entries:
        if binding == config:
            return ({"kind": "source_preserving", "declaration": name,
                     "representation": {"bucket": bucket}, "source_return_token": config}
                    if name == "source_preserving_inventory" else
                    {"kind": "projection", "declaration": name,
                     "representation": {"count": count}, "source_return_token": None})
    raise ValueError("outside selected finite carrier")


class ViewsDifferential(unittest.TestCase):
    def test_complete_replay_fixtures_and_token_boundary(self):
        for name, filename in ((VIEWS[0], "source_graph_view.json"),
                               (VIEWS[1], "lossy_graph_projection.json")):
            with self.subTest(name=name):
                path = FIXTURES / filename
                ir = json.loads(path.read_bytes())
                self.assertEqual(path.read_bytes(), canonical_bytes(ir) + b"\n")
                self.assertEqual(ir, lower(source_document(name)))
                self.assertEqual(parse(serialize(ir)), ir)
                actual = compare_replay(ir)["ir_result"]["terminal_outcome"]["value"]
                self.assertEqual(actual, conventional(name, GRAPH))
                self.assertEqual(actual["source_return_token"], GRAPH if name == VIEWS[0] else None)
                dimensions = [row["static_atom"]["dimension"] for row in execute(ir)["ordered_ledger"]]
                self.assertEqual(dimensions, (["inquiry", "alternatives"] if name == VIEWS[0]
                                             else ["inquiry", "loss", "alternatives"]))

    def test_budgets_guards_and_finite_baseline(self):
        for name in VIEWS:
            for binding in (GRAPH, B, C):
                for steps in (0, 1, 2):
                    for ledger in (0, 1, 2, 3):
                        for capability, obligation in ((True, "resolved"), (False, "resolved"),
                                                       (True, "unresolved")):
                            with self.subTest(name=name, binding=binding, steps=steps,
                                              ledger=ledger, capability=capability, obligation=obligation):
                                ir = lower(source_document(name, binding=binding, steps=steps,
                                                           ledger=ledger, capability=capability,
                                                           obligation=obligation))
                                result = compare_replay(ir)["ir_result"]
                                threshold = 2 if name == VIEWS[0] else 3
                                if steps >= 2 and ledger >= threshold and capability and obligation == "resolved":
                                    self.assertEqual(result["terminal_outcome"]["value"],
                                                     conventional(name, binding))

    def test_rebinding_or_loss_invention_rejected(self):
        view = json.loads((FIXTURES / "source_graph_view.json").read_bytes())
        altered = copy.deepcopy(view)
        altered["instruction"]["kind"] = "projection"
        altered["instruction"]["id"] = digest({k: v for k, v in altered["instruction"].items() if k != "id"})
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        with self.assertRaises(ViewIRAdmissionError):
            execute(altered)
        projection = json.loads((FIXTURES / "lossy_graph_projection.json").read_bytes())
        altered = copy.deepcopy(projection)
        altered["source_witness"]["evaluation_claim"]["terminal_outcome"]["value"]["source_return_token"] = GRAPH
        altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
        with self.assertRaises(ViewIRAdmissionError):
            execute(altered)
        bad = source_document(VIEWS[0]); bad["term"]["arg"] = {
            "tag": "view", "declaration": VIEWS[0], "arg": {"tag": "var", "name": "source_config"}}
        with self.assertRaises((ViewIRAdmissionError, ValueError)):
            lower(bad)

    def test_nested_map_requires_an_explicit_outcome_eliminator(self):
        source = input_document()
        source["term"] = {"tag": "apply", "declaration": "strict_normalise",
                          "arg": {"tag": "apply", "declaration": "total_identity",
                                  "arg": {"tag": "var", "name": "source_config"}}}
        with self.assertRaisesRegex(EvaluationInputError, 'expected Config.*found Outcome'):
            evaluate(source)


if __name__ == "__main__":
    unittest.main()
