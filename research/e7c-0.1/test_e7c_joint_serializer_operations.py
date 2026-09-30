"""Finite CPython observations; these do not prove operation adequacy."""
import sys
import unittest
from fractions import Fraction
from unittest.mock import patch

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source


def observed_calls(value):
    """Observe actual pinned helper frame entries, retaining native objects.

    This is a finite helper-call observation, not an attribute/opcode trace or
    a producer of the Lean operation relation. Restore the caller's profiler.
    """
    helpers = {source._graph.__code__: ("_graph", ("g",)),
               source._row.__code__: ("_row", ("atoms", "coefficient")),
               source.rows.__code__: ("rows", ("value",))}
    events = []

    def profile(frame, event, arg):
        if event == "call" and frame.f_code in helpers:
            name, args = helpers[frame.f_code]
            events.append((name, tuple(frame.f_locals[key] for key in args)))

    previous = sys.getprofile()
    sys.setprofile(profile)
    try:
        output = source.rows(value)
    finally:
        sys.setprofile(previous)
    return output, events


class SerializerOperationTests(unittest.TestCase):
    def test_native_attribute_values_and_exact_rational_pairs(self):
        edges = ("AB", "AC", "BC")
        for mask in range(8):
            for tag in (None, "", "x", "Ω"):
                graph = Config(tuple(edge for bit, edge in enumerate(edges)
                                     if mask & (1 << bit)), tag)
                self.assertEqual(getattr(graph, "edges"), graph.edges)
                self.assertIs(getattr(graph, "tag"), tag)
                self.assertEqual(source._graph(graph), {"edges": list(graph.edges), "tag": tag})
        for coefficient in (Fraction(-7, 11), Fraction(2, 4), Fraction(0), Fraction(5, 3)):
            self.assertIs(type(coefficient.numerator), int)
            self.assertIs(type(coefficient.denominator), int)
            self.assertGreater(coefficient.denominator, 0)
            output = source._row((Config((), None), Config((), "")), coefficient)
            self.assertEqual(output["coefficient"], {"numerator": coefficient.numerator,
                                                       "denominator": coefficient.denominator})
        self.assertEqual(Fraction(2, 4).numerator, 1)  # raw-pair admission remains separate

    def test_list_copy_and_ordered_two_target_unpack(self):
        original = ("AB", "AC", "BC")
        copied = list(original)
        self.assertEqual(copied, ["AB", "AC", "BC"])
        copied.append("changed")
        self.assertEqual(original, ("AB", "AC", "BC"))
        left, right = Config((), None), Config((), "")
        atoms, coefficient = ((left, right), Fraction(-2, 3))
        self.assertIs(atoms[0], left)
        self.assertIs(atoms[1], right)
        self.assertEqual(coefficient, Fraction(-2, 3))
        for malformed in ((), (left,), (left, right, left)):
            with self.assertRaises(ValueError):
                first, second = malformed

    def test_actual_cpython_helper_visits_complete_in_joint_order(self):
        left, right = Config(("AB",), None), Config(("BC",), "")
        values = [joint([(Fraction(1, 2), (left, left)),
                         (Fraction(1, 2), (right, right))], arity=2),
                  joint([(Fraction(1, 2), (left, right)),
                         (Fraction(1, 2), (right, left))], arity=2),
                  joint([(Fraction(-2, 3), (Config((), f"{i:03}"), left))
                         for i in range(70)], arity=2)]
        for value in values:
            output, events = observed_calls(value)
            expected = [("rows", (value,))]
            for atoms, coefficient in value.terms:
                expected.extend([("_row", (atoms, coefficient)),
                                 ("_graph", (atoms[0],)), ("_graph", (atoms[1],))])
            self.assertEqual(events, expected)
            self.assertEqual(len(output), len(value.terms))
            for encoded, (atoms, coefficient) in zip(output, value.terms):
                self.assertEqual(encoded["atoms"], [source._graph(g) for g in atoms])
                self.assertEqual(encoded["coefficient"], {"numerator": coefficient.numerator,
                                                           "denominator": coefficient.denominator})

    def test_empty_native_joint_has_no_nested_calls_and_restores_profiler(self):
        previous = sys.getprofile()
        value = Joint(2, ())
        output, events = observed_calls(value)
        self.assertEqual(output, [])
        self.assertEqual(events, [("rows", (value,))])
        self.assertIs(sys.getprofile(), previous)

    def test_changed_running_helper_binding_changes_result(self):
        value = joint([(Fraction(-2, 3), (Config(("AB",), None), Config((), "")))], arity=2)
        expected = source.rows(value)
        with patch.object(source, "_graph", lambda _: {"edges": [], "tag": "forged"}):
            self.assertNotEqual(source.rows(value), expected)
        self.assertEqual(source.rows(value), expected)

    def test_interrupted_helper_does_not_produce_a_normal_output(self):
        value = joint([(Fraction(1), (Config((), None), Config((), "")))], arity=2)
        original = source._graph
        visits = []

        def interrupted(graph):
            visits.append(graph)
            if len(visits) == 2:
                raise KeyboardInterrupt("host interruption")
            return original(graph)

        with patch.object(source, "_graph", interrupted):
            with self.assertRaises(KeyboardInterrupt):
                source.rows(value)
        self.assertEqual(visits, list(value.terms[0][0]))


if __name__ == "__main__":
    unittest.main()
