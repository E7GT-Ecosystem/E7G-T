"""Derived outcomes from the existing exact finite FG3 reconstruction fibre."""

import unittest

from derived_nonseparability_b1 import BASIS, assess, complete_carrier
from eec_q_fg3_b1 import AdmissionError, Config
from eec_q_fg3_fibre_b1 import FiniteCarrier


class DerivedSeparationTests(unittest.TestCase):
    def setUp(self):
        self.carrier = complete_carrier()

    def check(self, graph, protected, budget=8, carrier=None):
        return assess(graph, carrier or self.carrier, budget,
                      "FG3 declared graph", "protected relation for selected use", protected)

    def test_every_fixed_graph_is_separable_for_preserved_edge_count(self):
        for graph in BASIS:
            with self.subTest(edges=graph.edges):
                assessment = self.check(graph, "edge_count")
                self.assertEqual(assessment.outcome, "separable")
                self.assertTrue(all(len(candidate.edges) == len(graph.edges)
                                    for candidate in assessment.compatible))
                self.assertEqual(assessment.component_views,
                                 (("A", "present"), ("B", "present"), ("C", "present")))
                self.assertIn("exact_edge_identity", assessment.lost_relations)
        # An equivalent class does not name the exact source relation.
        graph = Config(("AC",), None)
        self.assertGreater(len(self.check(graph, "edge_count").compatible), 1)

    def test_hidden_connection_changes_protected_adjacency(self):
        for graph in BASIS:
            assessment = self.check(graph, "has_AB")
            if len(graph.edges) in (1, 2):
                self.assertEqual(assessment.outcome, "non_separable")
                source, alternative = assessment.material_witness
                self.assertEqual(len(source.edges), len(alternative.edges))
                self.assertNotEqual("AB" in source.edges, "AB" in alternative.edges)
                self.assertIn(source, assessment.compatible)
                self.assertIn(alternative, assessment.compatible)
            else:
                self.assertEqual(assessment.outcome, "separable")
                self.assertIsNone(assessment.material_witness)

    def test_incomplete_carrier_or_resource_stop_is_undetermined(self):
        graph = Config(("AB",), None)
        limited = self.check(graph, "has_AB", budget=7)
        self.assertEqual((limited.outcome, limited.reason, limited.compatible),
                         ("undetermined", "resource_limit", ()))
        partial = FiniteCarrier(self.carrier.edition, self.carrier.candidates[:1])
        assessment = self.check(graph, "has_AB", carrier=partial)
        self.assertEqual(assessment.outcome, "undetermined")
        self.assertEqual(assessment.reason, "candidate_carrier_not_complete_fixed_basis")
        with self.assertRaisesRegex(AdmissionError, "edition_mismatch"):
            self.check(graph, "has_AB", carrier=FiniteCarrier("future", self.carrier.candidates))

    def test_no_context_free_or_tagged_claims(self):
        with self.assertRaises(AdmissionError):
            self.check(Config(("AB",), "semantic"), "has_AB")
        with self.assertRaises(AdmissionError):
            self.check(Config(("AB",), None), "quantum_entanglement")
        with self.assertRaises(AdmissionError):
            assess(Config(("AB",), None), self.carrier, 8, "", "inquiry", "has_AB")


if __name__ == "__main__":
    unittest.main()
