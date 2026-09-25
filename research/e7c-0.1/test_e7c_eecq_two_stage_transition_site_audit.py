"""Audit every direct transition mutation in the four selected functions."""

import unittest

from e7c_eecq_two_stage_transition_site_audit import (
    ROOT, TARGETS, SiteAuditFailure, audit_code, audit_repository,
)


class TransitionSiteAudit(unittest.TestCase):
    def test_selected_source_and_ir_sites(self):
        self.assertEqual(audit_repository(), {
            name: {"charge": 2, "append": 2} for name, _, _ in TARGETS})

    def test_omitted_and_reordered_probes_rejected(self):
        for name, function, stage in TARGETS:
            original = (ROOT / name).read_text(encoding="utf-8")
            if stage == "first":
                charge = original.replace('steps += 1\n    emit("charge")',
                                          'steps += 1\n    pass\n    emit("charge")', 1)
            else:
                charge = original.replace('steps += 1\n    second_started = True',
                                          'steps += 1\n    pass\n    second_started = True', 1)
            self.assertNotEqual(charge, original)
            with self.subTest(name=name, site="charge"), self.assertRaises(SiteAuditFailure):
                audit_code(charge, function, stage)
            altered_append = original.replace('emit("append")', 'pass', 1)
            with self.subTest(name=name, site="append"), self.assertRaises(SiteAuditFailure):
                audit_code(altered_append, function, stage)

    def test_child_forwarding_and_second_started_order(self):
        for name, function, stage in TARGETS:
            if stage != "second":
                continue
            original = (ROOT / name).read_text(encoding="utf-8")
            removed = original.replace('_transition_sink=_transition_sink)', ')', 1)
            with self.subTest(name=name, site="child"), self.assertRaises(SiteAuditFailure):
                audit_code(removed, function, stage)
            reordered = original.replace('steps += 1\n    second_started = True\n    emit("charge")',
                                         'steps += 1\n    emit("charge")\n    second_started = True', 1)
            with self.subTest(name=name, site="start"), self.assertRaises(SiteAuditFailure):
                audit_code(reordered, function, stage)
            removed_terminal = original.replace('"action": "terminal"', '"action": "omitted"', 1)
            with self.subTest(name=name, site="terminal"), self.assertRaises(SiteAuditFailure):
                audit_code(removed_terminal, function, stage)


if __name__ == "__main__":
    unittest.main()
