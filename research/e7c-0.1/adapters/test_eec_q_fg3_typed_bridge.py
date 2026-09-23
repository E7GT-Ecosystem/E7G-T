"""Selected E7C-profile typed composition across the FG3 adapter modules."""

from __future__ import annotations

import unittest
from fractions import Fraction

from eec_q_fg3_b1 import Config, collect
from eec_q_fg3_joint_b1 import joint
from eec_q_fg3_typed_bridge import (ACTIONS, CANONICAL_BLOB, MODEL_BLOB, LOSS,
                                     MODULE_EDITION, STEP, STRICT, BridgeError,
                                     BridgeOutcome, Sort, admit, check, execute)


class TypedBridgeTests(unittest.TestCase):
    def test_exact_sort_check_precedes_join_execution(self):
        p, q = Config(("AB",), None), Config(("BC",), None)
        pair = admit("graph_joint2", joint([(Fraction(2), (p, q))]))
        wiring = admit("graph_joint3", joint([(Fraction(1), (p, q, Config((), "uses")))]))
        self.assertEqual(check("join_pair", pair.sort).output.tag, "assembly_state")
        self.assertEqual(check("join_wire_choice", wiring.sort).static_effects, (STEP, STRICT))
        with self.assertRaises(BridgeError):
            check("join_pair", wiring.sort)
        with self.assertRaises(BridgeError):
            check("join_wire_choice", pair.sort)
        with self.assertRaises(BridgeError):
            admit("graph_joint2", wiring.payload)
        self.assertEqual(execute("join_pair", pair).value.payload.terms[0][1], Fraction(2))

    def test_lossy_identification_cannot_return_source(self):
        p, q = Config(("AB", "BC"), None), Config(("AC", "BC"), None)
        source = collect([(p, Fraction(1)), (q, Fraction(-1))])
        typed = admit("untagged_graph_state", source)
        viewed = execute("project_view", typed)
        returned = execute("source_return", viewed.value)
        self.assertEqual(returned.value.payload, source)
        self.assertEqual(viewed.ledger, (STEP, ACTIONS["project_view"].effects[1]))
        phase = execute("identify_phase", typed)
        self.assertEqual(phase.value.payload.terms, ())
        self.assertEqual(phase.ledger, (STEP, LOSS))
        with self.assertRaises(BridgeError):
            check("source_return", phase.value.sort)
        with self.assertRaises(BridgeError):
            execute("source_return", phase.value)
        self.assertNotEqual(source.terms, ())

    def test_tagged_graph_not_admitted_to_phase_only_sort(self):
        tagged = collect([(Config(("AB",), "semantic"), Fraction(1))])
        graph = admit("graph_state", tagged)
        with self.assertRaises(BridgeError):
            admit("untagged_graph_state", tagged)
        with self.assertRaises(BridgeError):
            check("identify_phase", graph.sort)
        with self.assertRaises(BridgeError):
            execute("project_view", graph)

    def test_whole_strict_failure_preserves_incurred_effect(self):
        p, q = Config(("AB",), None), Config(("BC",), None)
        state = admit("graph_state", collect([(p, Fraction(1)), (q, Fraction(1))]))
        failure = execute("require_absent_ab", state)
        self.assertEqual((failure.tag, failure.value, failure.ledger),
                         ("domain_error", None, (STEP, STRICT)))
        with self.assertRaises(BridgeError):
            BridgeOutcome("add_ab", "domain_error", None, (STEP, STRICT))
        valid, bad = Config((), "uses"), Config(("AB",), "contains")
        rows = joint([(Fraction(1), (p, q, valid)), (Fraction(1), (p, q, bad))])
        failure = execute("join_wire_choice", admit("graph_joint3", rows))
        self.assertEqual((failure.tag, failure.value, failure.ledger),
                         ("domain_error", None, (STEP, STRICT)))

    def test_whole_quote_requires_explicit_inside(self):
        p = Config(("BC",), None)
        graph = admit("graph_state", collect([(p, Fraction(2))]))
        boxed = execute("pack", graph)
        self.assertEqual(boxed.value.sort.tag, "whole_quote")
        with self.assertRaises(BridgeError):
            check("add_ab", boxed.value.sort)
        transformed = execute("inside_add_ab", boxed.value)
        self.assertEqual(transformed.tag, "success")
        self.assertEqual(transformed.value.payload.payload.terms[0][0].edges, ("AB", "BC"))
        failure = execute("inside_require_absent_ab", transformed.value)
        self.assertEqual((failure.tag, failure.value, failure.ledger),
                         ("domain_error", None, (STEP, STRICT)))

    def test_edition_and_closed_module_surface(self):
        self.assertEqual(len(CANONICAL_BLOB), 40)
        self.assertEqual(len(MODEL_BLOB), 40)
        self.assertEqual(MODULE_EDITION, "E7C-EECQ-FG3-BRIDGE/0.1-provisional")
        with self.assertRaises(BridgeError):
            Sort("future", "graph_state")
        with self.assertRaises(BridgeError):
            check("unknown", Sort(MODULE_EDITION, "graph_state"))
        with self.assertRaises(BridgeError):
            admit("graph_state", 0)


if __name__ == "__main__":
    unittest.main()
