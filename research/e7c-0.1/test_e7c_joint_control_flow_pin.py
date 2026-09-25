import unittest

from e7c_joint_control_flow_pin import ROOT, ENTRY_POINTS, check_repository, fingerprint


class JointControlFlowPin(unittest.TestCase):
    def test_all_four_entry_points_are_exact(self):
        check_repository()

    def test_changes_to_branches_order_child_and_event_break_pin(self):
        mutations = {
            "e7c_eecq_joint_restrict_b1.py": (
                ('beta["step_bound"] == 0', 'beta["step_bound"] < 0'),
                ('enumerate(value.terms)', 'enumerate(reversed(value.terms))'),
            ),
            "e7_ir_eecq_joint_restrict_b1.py": (
                ('checked = parse(serialize(package))', 'checked = package'),
                ('if len(ledger) >= beta["ledger_bound"]:', 'if len(ledger) > beta["ledger_bound"]:'),
            ),
            "e7c_eecq_two_stage_b1.py": (
                ('second_started = True', 'second_started = False'),
                ('evaluate_first(source["first"]', 'evaluate_first(source["second_interpretation"]'),
            ),
            "e7_ir_eecq_two_stage_b1.py": (
                ('execute_first(checked["first_ir"]', 'execute_first(checked["source_document"]'),
                ('"BC" in row["atoms"][1]["edges"]', '"AB" in row["atoms"][1]["edges"]'),
            ),
        }
        for (name, entry), expected in ENTRY_POINTS.items():
            original = (ROOT / name).read_text()
            for before, after in mutations[name]:
                changed = original.replace(before, after, 1)
                self.assertNotEqual(changed, original)
                with self.subTest(name=name, mutation=before):
                    self.assertNotEqual(fingerprint(changed, entry), expected)


if __name__ == "__main__":
    unittest.main()
