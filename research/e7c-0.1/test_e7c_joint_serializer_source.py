"""Pinned source translation and independent selected serializer execution."""
import unittest
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_source import ROOT, check, generated_text, interpret_helper


class SerializerSourceTests(unittest.TestCase):
    def test_generated_source_tree_matches_complete_pinned_helpers(self):
        check()

    def test_all_fg3_graphs_tags_and_signed_fraction_helpers(self):
        edges = ["AB", "AC", "BC"]
        graphs = [Config(tuple(edge for bit, edge in enumerate(edges) if mask & (1 << bit)), tag)
                  for mask in range(8) for tag in (None, "", "x", "Ω")]
        for graph in graphs:
            self.assertEqual(interpret_helper("_graph", graph), source._graph(graph))
            for coefficient in (Fraction(-7, 11), Fraction(1, 2), Fraction(5, 3)):
                atoms = (graph, graphs[-1])
                self.assertEqual(interpret_helper("_row", atoms, coefficient),
                                 source._row(atoms, coefficient))

    def test_correlated_tables_keep_order_coordinates_and_coefficients(self):
        left, right = Config(("AB",), None), Config(("BC",), "")
        diagonal = joint([(Fraction(1, 2), (left, left)),
                          (Fraction(1, 2), (right, right))], arity=2)
        crossed = joint([(Fraction(1, 2), (left, right)),
                         (Fraction(1, 2), (right, left))], arity=2)
        for value in (diagonal, crossed):
            self.assertEqual(interpret_helper("rows", value), source.rows(value))
        self.assertNotEqual(interpret_helper("rows", diagonal), interpret_helper("rows", crossed))

    def test_empty_and_serializer_lists_beyond_admission_cap(self):
        empty = Joint(2, ())
        self.assertEqual(interpret_helper("rows", empty), [])
        value = joint([(Fraction(-2, 3), (Config((), f"{i:03}"), Config((), None)))
                       for i in range(70)], arity=2)
        self.assertEqual(len(interpret_helper("rows", value)), 70)
        self.assertEqual(interpret_helper("rows", value), source.rows(value))

    def test_exact_native_type_and_binary_guard(self):
        class SubJoint(Joint):
            pass
        for value in (object(), Joint(1, ()), SubJoint(2, ())):
            with self.assertRaises(source.JointRestrictionAdmission):
                interpret_helper("rows", value)
            with self.assertRaises(source.JointRestrictionAdmission):
                source.rows(value)

    def test_forged_attribute_observation_breaks_correspondence(self):
        graph = Config((), None)
        read = lambda obj, attr: "" if attr == "tag" else getattr(obj, attr)
        self.assertNotEqual(interpret_helper("_graph", graph, read_attribute=read),
                            source._graph(graph))

    def test_forged_helper_binding_breaks_correspondence(self):
        atoms = (Config(("AB",), None), Config(("BC",), ""))
        altered = interpret_helper("_row", atoms, Fraction(-2, 3),
                                   bindings={"_graph": lambda _: {"edges": [], "tag": None}})
        self.assertNotEqual(altered, source._row(atoms, Fraction(-2, 3)))

    def test_translation_rejects_guard_bypass_and_extra_statement(self):
        code = (ROOT / "e7c_eecq_joint_restrict_b1.py").read_text()
        for old, new in [('value.arity != 2', 'value.arity != 1'),
                         ('return {"edges": list(g.edges), "tag": g.tag}',
                          'ignored = g.tag\n    return {"edges": list(g.edges), "tag": g.tag}')]:
            with self.assertRaises(ValueError):
                generated_text(code.replace(old, new))

    def test_translation_rejects_duplicate_dictionary_literal_keys(self):
        code = (ROOT / "e7c_eecq_joint_restrict_b1.py").read_text()
        code = code.replace('"tag": g.tag}', '"tag": g.tag, "tag": g.edges}')
        with self.assertRaises(ValueError):
            generated_text(code)


if __name__ == "__main__":
    unittest.main()
