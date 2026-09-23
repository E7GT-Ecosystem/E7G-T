"""Specification-derived checks for the finite temporal history candidate."""

import unittest

from temporal_history_b1 import (AdmissionError, EDITION, Fibre, History,
                                 HistoryCarrier, ProjectedFinal, State, Transition,
                                 compare_order, extend, phase, phase_boundary,
                                 phase_candidates, project_final, reconstruct,
                                 representative_status, view_final)


class TemporalHistoryTests(unittest.TestCase):
    def setUp(self):
        self.initial = State(False, False)
        self.start = History("plain", self.initial, ())
        reviewed = extend(self.start, "review")
        self.plain = extend(reviewed, "approve")
        self.revised = History("revised", self.initial, ())
        for operation in ("review", "withdraw_review", "review", "approve"):
            self.revised = extend(self.revised, operation)
        self.carrier = HistoryCarrier(EDITION, (self.plain, self.revised))

    def test_retained_view_and_lossy_final_projection_are_distinct(self):
        self.assertEqual(self.plain.final, self.revised.final)
        self.assertNotEqual(self.plain.transitions, self.revised.transitions)
        self.assertEqual(project_final(self.plain), project_final(self.revised))
        self.assertEqual(view_final(self.plain).source, self.plain)
        self.assertNotEqual(view_final(self.plain), view_final(self.revised))
        self.assertIn("step_order", project_final(self.plain).loses)
        with self.assertRaises(AdmissionError):
            view_final(project_final(self.plain))
        with self.assertRaises(AdmissionError):
            ProjectedFinal("future", self.plain.final)

    def test_fibre_is_relative_to_declared_complete_carrier(self):
        projection = project_final(self.plain)
        fibre = reconstruct(self.carrier, projection, 2)
        self.assertEqual(fibre.status, "success")
        self.assertEqual(fibre.candidates, (self.plain, self.revised))
        self.assertEqual(len(phase_candidates(fibre)), 2)
        self.assertEqual(len(reconstruct(HistoryCarrier(EDITION, (self.plain,)),
                                         projection, 1).candidates), 1)
        # A conceivable third history is not invented from independent slices.
        third = History("unlisted", self.initial, ())
        for operation in ("review", "review", "approve"):
            third = extend(third, operation)
        self.assertEqual(third.final, projection.state)
        self.assertNotIn(third, fibre.candidates)
        # No result with a partial scan may masquerade as a complete fibre.
        limited = reconstruct(self.carrier, projection, 1)
        self.assertEqual((limited.status, limited.candidates), ("resource_limit", ()))
        with self.assertRaisesRegex(AdmissionError, "complete_candidate"):
            phase_candidates(limited)
        with self.assertRaisesRegex(AdmissionError, "incomplete_or_wrong"):
            Fibre(self.carrier, projection, "success", (self.plain,), 2)

    def test_actual_transition_crosses_a_pinned_temporal_phase(self):
        reviewed = extend(self.start, "review")
        approved = extend(reviewed, "approve")
        self.assertFalse(phase_boundary(self.start, reviewed))
        self.assertTrue(phase_boundary(reviewed, approved))
        self.assertTrue(phase_boundary(reviewed, extend(reviewed, "withdraw_review")))
        self.assertNotEqual(phase(self.plain), phase(self.revised))
        with self.assertRaisesRegex(AdmissionError, "admitted_transition"):
            phase_boundary(self.plain, self.revised)

    def test_typed_history_chain_cannot_forge_a_transition(self):
        with self.assertRaisesRegex(AdmissionError, "unadmitted_transition"):
            History("forged", self.initial,
                    (Transition("approve", self.initial, State(False, True)),))
        with self.assertRaisesRegex(AdmissionError, "broken_transition_chain"):
            History("forged", self.initial,
                    (Transition("review", State(True, False), State(True, False)),))
        with self.assertRaisesRegex(AdmissionError, "invalid_declared_history_carrier"):
            HistoryCarrier(EDITION, (self.plain, self.plain))

    def test_order_and_representative_dependence(self):
        asymmetric = compare_order(self.start, "review", "approve")
        self.assertIsNotNone(asymmetric.left_then_right)
        self.assertIsNone(asymmetric.right_then_left)
        self.assertIsNone(asymmetric.same_final)
        reviewed = extend(self.start, "review")
        both = compare_order(reviewed, "review", "withdraw_review")
        self.assertIsNotNone(both.left_then_right)
        self.assertIsNotNone(both.right_then_left)
        self.assertFalse(both.same_final)
        # These histories share a phase while 'approve' has different domains.
        family = HistoryCarrier(EDITION, (self.start, History("reviewed", self.initial,
                                                               reviewed.transitions)))
        self.assertEqual(phase(family.histories[0]), phase(family.histories[1]))
        status = representative_status(family, "approve")
        self.assertFalse(status.domain_saturated)
        self.assertEqual(status.domain_witness, ("plain", "reviewed"))
        self.assertTrue(status.result_congruent)  # Vacuous success check does not fix domain.


if __name__ == "__main__":
    unittest.main()
