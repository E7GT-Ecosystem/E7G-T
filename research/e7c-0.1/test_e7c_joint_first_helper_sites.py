"""Adversarial changes to helper contracts must invalidate the AST checker."""

import unittest
from fractions import Fraction
from unittest.mock import patch

from e7c_joint_first_helper_sites import ROOT, FUNCTIONS, checked_sites
import e7c_eecq_joint_restrict_b1 as first
from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint


class HelperSites(unittest.TestCase):
    def test_exact_helper_closure(self):
        self.assertEqual(set(checked_sites()),
                         {"admission", "partition", "serialization", "ir"})

    def test_guard_partition_and_serialization_mutations(self):
        originals = {name: (ROOT / name).read_text() for name, _ in FUNCTIONS}
        cases = (
            ("e7c_eecq_joint_restrict_b1.py",
             'rows(value) != source["rows"]', 'rows(value) == source["rows"]'),
            ("adapters/eec_q_fg3_joint_b1.py",
             'if edge not in atoms[coordinate].edges)',
             'if edge in atoms[coordinate].edges)'),
            ("e7c_eecq_joint_restrict_b1.py",
             'witness["id"] = digest(witness)',
             'witness["id"] = "unbound"'),
            ("e7_ir_eecq_joint_restrict_b1.py",
             'checked = parse(serialize(package))', 'checked = package'),
        )
        for name, before, after in cases:
            with self.subTest(name=name, mutation=before):
                mutated = dict(originals)
                self.assertIn(before, mutated[name])
                mutated[name] = mutated[name].replace(before, after, 1)
                with self.assertRaises(ValueError):
                    checked_sites(mutated)

    def test_normal_return_guard_rejects_changed_normalizer_output(self):
        left = Config(("AB",), None)
        right = Config(("BC",), "")
        value = joint([(Fraction(-2, 3), (left, right)),
                       (Fraction(1, 4), (right, left))], arity=2)
        source = first.document(value)
        real_joint = first.joint

        def altered(parsed, *, arity):
            original = real_joint(parsed, arity=arity)
            if mutation == "coefficient":
                atoms, coefficient = original.terms[0]
                return Joint(original.arity,
                             ((atoms, coefficient + Fraction(1, 7)),) + original.terms[1:])
            # The constructor normally rejects this order. Deliberately
            # corrupt a constructed object to challenge the admission guard.
            object.__setattr__(original, "terms", original.terms[::-1])
            return original

        for mutation in ("coefficient", "order"):
            with self.subTest(mutation=mutation):
                with patch.object(first, "joint", side_effect=altered):
                    with self.assertRaises(first.JointRestrictionAdmission):
                        first.admit(source)
        self.assertEqual(first.rows(first.admit(source)), source["rows"])


if __name__ == "__main__":
    unittest.main()
