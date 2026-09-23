"""Differential checks against the pinned WPC/0.2 allocation example."""

import importlib.util
from itertools import product
from pathlib import Path
import unittest

from wpc_allocation_b1 import (AdmissionError, Candidate, Portion, Presentation,
                               Proposal, Representation, Whole, constitute, extract,
                               materialise, membership_candidate, reconcile, represent)

SOURCE = (Path(__file__).resolve().parents[3] / "packages" / "wpc-0.2"
          / "E7G-T_WPC_v0.2_Reference_Model.py")
spec = importlib.util.spec_from_file_location("wpc_source", SOURCE)
source = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = source
spec.loader.exec_module(source)


def pair(whole):
    return (Whole(whole.epoch, whole.members, whole.values, whole.events, whole.budget),
            source.Whole(whole.epoch, whole.members, whole.values, whole.events, whole.budget))


def reason(thunk):
    try:
        thunk()
    except (AdmissionError, source.Reject) as exc:
        return str(exc)
    return "accepted"


class WPCDifferential(unittest.TestCase):
    def test_all_ten_finite_wholes_and_thirty_occurrences(self):
        for values in product(range(3), repeat=3):
            if sum(values) > 2:
                continue
            adapted, original = pair(source.Whole(0, source.IDS, values))
            presentation, assembly = materialise(adapted), source.alpha(original)
            self.assertEqual(represent(adapted).payload, source.encode(original))
            self.assertEqual(tuple((p.occurrence, p.local_value, p.representation.payload)
                                   for p in presentation.portions), assembly.rows)
            self.assertEqual(constitute(presentation), adapted)
            self.assertEqual(materialise(constitute(presentation)), presentation)
            self.assertTrue(all(extract(p.representation) == adapted
                                for p in presentation.portions))

    def test_coverage_source_conflict_and_global_incompatibility(self):
        base, original = pair(source.Whole(0, source.IDS, (0, 0, 0)))
        presentation, assembly = materialise(base), source.alpha(original)
        bad = [
            (Presentation(0, source.IDS, presentation.portions[:-1], ()),
             source.Assembly(0, source.IDS, assembly.rows[:-1], ())),
            (Presentation(0, source.IDS, (presentation.portions[0],) * 2
                          + presentation.portions[2:], ()),
             source.Assembly(0, source.IDS, (assembly.rows[0],) * 2
                             + assembly.rows[2:], ())),
            (Presentation(0, source.IDS, (Portion("A", 1, represent(base)),)
                          + presentation.portions[1:], ()),
             source.Assembly(0, source.IDS, (("A", 1, source.encode(original)),)
                             + assembly.rows[1:], ())),
        ]
        for adapted, reference in bad:
            self.assertEqual(reason(lambda: constitute(adapted)),
                             reason(lambda: source.beta(reference)))
        for values in ((2, 1, 0), (1, 1, 1), (3, 0, 0)):
            self.assertEqual(reason(lambda: Whole(0, source.IDS, values)),
                             reason(lambda: source.Whole(0, source.IDS, values)))

    def test_candidate_lineage_proposals_and_history(self):
        base, original = pair(source.Whole(0, source.IDS, (0, 0, 0)))
        a = Proposal("a1", "A", represent(base), "A", 1)
        b = Proposal("b1", "B", represent(base), "B", 1)
        c = Proposal("c1", "C", represent(base), "C", 1)
        originals = [source.Proposal(p.event_id, p.actor, p.base.payload,
                                     p.target, p.value) for p in (a, b, c)]
        candidate = reconcile(base, (b, a))
        self.assertIs(type(candidate), Candidate)
        self.assertEqual(candidate.base, base)
        self.assertEqual(candidate.proposed.events[-2:],
                         (("a1", "A", 0, "set", "A", 1),
                          ("b1", "B", 0, "set", "B", 1)))
        self.assertEqual(candidate.proposed.values,
                         source.reconcile(original, tuple(originals[:2])).values)
        self.assertEqual(reconcile(base, (a, a, b)).proposed, candidate.proposed)
        self.assertEqual(constitute(materialise(candidate.proposed)), candidate.proposed)
        self.assertEqual(reason(lambda: reconcile(base, (a, b, c))),
                         reason(lambda: source.reconcile(original, tuple(originals))))
        stale = Proposal("c1", "C", represent(base), "C", 1)
        stale_source = originals[2]
        self.assertEqual(reason(lambda: reconcile(candidate.proposed, (stale,))),
                         reason(lambda: source.reconcile(
                             source.reconcile(original, tuple(originals[:2])), (stale_source,))))
        # An equal epoch or allocation is insufficient to identify this lineage.
        other = reconcile(base, (Proposal("a2", "A", represent(base), "A", 1), b))
        self.assertEqual(other.proposed.values, candidate.proposed.values)
        self.assertNotEqual(represent(other.proposed), represent(candidate.proposed))

    def test_representation_is_not_a_whole_or_a_commit(self):
        base = Whole(0, source.IDS, (0, 0, 0))
        self.assertNotEqual(type(represent(base)), type(base))
        self.assertNotEqual(type(materialise(base)), type(base))
        self.assertEqual(reason(lambda: extract(Representation("wrong", represent(base).payload))),
                         "unsupported_profile")
        with self.assertRaises(AdmissionError):
            materialise(represent(base))
        self.assertEqual(reconcile(base, ()).proposed, base)

    def test_membership_changes_refresh_portions_and_reject_reuse(self):
        adapted, original = pair(source.Whole(0, source.IDS, (1, 1, 0)))
        candidate = membership_candidate(adapted, "coordinator", ("A", "B"), "leave-c")
        reference = source.membership_candidate(original, "coordinator", ("A", "B"), "leave-c")
        self.assertEqual(candidate.proposed.members, reference.members)
        self.assertEqual(represent(candidate.proposed).payload, source.encode(reference))
        self.assertEqual(constitute(materialise(candidate.proposed)), candidate.proposed)
        self.assertEqual(reason(lambda: membership_candidate(
            candidate.proposed, "coordinator", source.IDS, "reuse-c")),
            reason(lambda: source.membership_candidate(
                reference, "coordinator", source.IDS, "reuse-c")))
        self.assertEqual(reason(lambda: membership_candidate(
            adapted, "A", ("A", "B"), "bad-leave")),
            reason(lambda: source.membership_candidate(
                original, "A", ("A", "B"), "bad-leave")))


if __name__ == "__main__":
    unittest.main()
