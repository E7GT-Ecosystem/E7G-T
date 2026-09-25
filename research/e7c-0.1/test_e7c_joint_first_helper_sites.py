"""Adversarial changes to helper contracts must invalidate the AST checker."""

import unittest

from e7c_joint_first_helper_sites import ROOT, FUNCTIONS, checked_sites


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


if __name__ == "__main__":
    unittest.main()
