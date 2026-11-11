#!/usr/bin/env python3
"""Bounded GCD-B1 conformance, counterexamples, and finite-domain enumeration.

Scope is exactly the declared finite carrier; passing is not general-kernel conformance.
"""
import copy
from itertools import combinations
import json
import unittest
import gcd02 as g


COUNTS = {}


def tally(name, number):
    COUNTS[name] = number


def all_subfamilies(signature, include_empty=False):
    basis = g.configs(signature)
    for n in range(0 if include_empty else 1, len(basis) + 1):
        for subset in combinations(basis, n):
            yield g.family(signature, f"exh-{n}", subset, "shared-exhaustive")


class GCDTests(unittest.TestCase):
    def setUp(self):
        self.u = g.make_config(g.SIG0)
        self.a = g.make_config(g.SIG1, ("A",))
        self.r = g.make_config(g.SIG1, ("R",))
        self.ar = g.make_config(g.SIG1, ("A", "R"))
        self.e = g.make_config(g.SIG2, ("A", "E"))
        self.h0 = g.family(g.SIG0, "base-v1", (self.u,), "source-X")
        self.h1 = g.family(g.SIG1, "variants-v1", (self.a, self.r), "source-X")

    def test_exact_finite_carrier_and_enumeration(self):
        expected = {g.SIG0: 1, g.SIG1: 4, g.SIG2: 6}
        evaluated = 0
        for signature, count in expected.items():
            values = g.configs(signature)
            self.assertEqual(len(values), count)
            self.assertEqual(len(set(values)), count)
            for c in values:
                self.assertEqual(g.read_config(g.config_record(c)), c)
                evaluated += 1
        tally("admitted_configurations_checked", evaluated)
        # Every subset of the fixed three optional stage IDs is admitted or rejected.
        for sig in expected:
            admitted = 0
            for n in range(4):
                for subset in combinations(g.ORDER, n):
                    try:
                        g.make_config(sig, subset)
                        admitted += 1
                    except g.InvalidInput:
                        pass
            self.assertEqual(admitted, expected[sig])
        tally("finite_subsets_checked_for_admission", 24)

    def test_invalid_structure_missing_required_relation(self):
        c = g.config_record(self.e)
        c["relations"] = c["relations"][:-1]
        self.assertEqual(g.execute({"op": "generate_signature", "family": g.family_record(self.h1),
                                    "candidate": c})["status"], "invalid_input")

    def test_unregistered_structural_kind_rejected(self):
        with self.assertRaises(g.InvalidInput):
            g.make_config(g.SIG1, ("E",))
        with self.assertRaises(g.InvalidInput):
            g.make_config(g.SIG2, ("E",))

    def test_strict_constitutive_refinement(self):
        result = g.differentiate(self.h0, self.h1)
        self.assertEqual(result["status"], "constitutive_refinement")
        self.assertEqual(result["ordered_pairs_checked"], 4)
        self.assertEqual(result["strict_ordered_pairs"], 2)
        self.assertEqual(g.ground(self.a, g.SIG0), g.ground(self.r, g.SIG0))
        self.assertNotEqual(self.a, self.r)

    def test_access_refinement_is_not_constitution(self):
        self.assertEqual(g.differentiate(self.h1, self.h1)["status"], "access_refinement_only")
        # On unchanged Sigma1 the coarse view is constant while semantic-kind view splits.
        self.assertEqual(g.key(self.a, "root_only"), g.key(self.r, "root_only"))
        self.assertNotEqual(g.key(self.a, "kind_set"), g.key(self.r, "kind_set"))

    def test_non_split_not_established(self):
        h = g.family(g.SIG1, "single", (self.a,))
        self.assertEqual(g.differentiate(self.h0, h)["status"], "not_established")

    def test_incompatible_ground_rejected(self):
        h = g.family(g.SIG1, "different", (self.a, self.r))
        src = g.family(g.SIG0, "empty", ())
        self.assertEqual(g.differentiate(src, h)["status"], "not_established")

    def test_exhaustive_refinement_properties(self):
        # On each full finite carrier: identity refines grounding; distinguish fibres exhaustively.
        checked = 0
        strict = 0
        for old, new in ((g.SIG0, g.SIG1), (g.SIG1, g.SIG2), (g.SIG0, g.SIG2)):
            xs = g.configs(new)
            for x in xs:
                for y in xs:
                    fine = x == y
                    coarse = g.ground(x, old) == g.ground(y, old)
                    self.assertFalse(fine and not coarse)
                    strict += int(coarse and not fine)
                    checked += 1
        self.assertEqual(checked, 4*4 + 6*6 + 6*6)
        self.assertGreater(strict, 0)
        tally("ordered_pair_refinement_law_checks", checked)
        tally("strict_split_pair_witnesses_found", strict)

    def test_grounding_embedding_left_inverse_exhaustive(self):
        cases = 0
        for old, new in ((g.SIG0, g.SIG1), (g.SIG1, g.SIG2), (g.SIG0, g.SIG2)):
            for c in g.configs(old):
                self.assertEqual(g.ground(g.embed(c, new), old), c)
                cases += 1
        tally("ground_embed_left_inverse_checks", cases)
        self.assertNotEqual(g.embed(g.ground(self.e, g.SIG1), g.SIG2), self.e)

    def test_same_signature_generation(self):
        result = g.generation_within(self.h1, self.ar)
        self.assertEqual(result["status"], "expansive_within_signature")
        self.assertEqual(result["preserved"], 2)
        h_new = g.read_family(result["target"])
        self.assertEqual(len(h_new.members), 3)
        self.assertEqual(h_new.dependency_id, self.h1.dependency_id)
        self.assertTrue(set(self.h1.members).issubset(h_new.members))

    def test_criterion_relative_novelty_fails_for_coarse_criterion(self):
        result = g.generation_within(self.h1, self.ar, "root_only")
        self.assertEqual(result["status"], "non_expansive")

    def test_renaming_does_not_generate_novelty(self):
        self.assertFalse(g.witness_novelty(self.h1.members, self.a, "kind_set"))
        self.assertEqual(g.generation_within(self.h1, self.a)["status"], "domain_error")

    def test_bad_generator_domain(self):
        only_a = g.family(g.SIG1, "only-approve", (self.a,))
        self.assertEqual(g.generation_within(only_a, self.ar)["status"], "domain_error")

    def test_signature_generation_new_kind_and_relation(self):
        result = g.generation_signature(self.h1, self.e)
        self.assertEqual(result["status"], "expansive_signature_generation")
        self.assertEqual(result["signature_extension"]["added_kinds"], ["evidence_gate"])
        self.assertEqual(result["signature_extension"]["added_relations"], ["requires"])
        self.assertEqual(result["embedding_roundtrips"], 2)
        after = g.read_family(result["target"])
        self.assertIn(self.e, after.members)
        self.assertIn(g.embed(self.r, g.SIG2), after.members)
        self.assertEqual(g.ground(self.e, g.SIG1), self.a)

    def test_signature_generation_negative_cases(self):
        self.assertEqual(g.generation_signature(self.h1, g.embed(self.a, g.SIG2))["status"], "domain_error")
        self.assertEqual(g.generation_signature(self.h1, self.e, "root_only")["status"], "non_expansive")
        self.assertEqual(g.generation_signature(self.h0, self.e)["status"], "unsupported")
        only_r = g.family(g.SIG1, "only-reject", (self.r,))
        self.assertEqual(g.generation_signature(only_r, self.e)["status"], "domain_error")

    def test_exhaustive_generation_classification(self):
        within_count, sig_count = 0, 0
        for h in all_subfamilies(g.SIG1):
            res = g.generation_within(h, self.ar)
            expected = ("expansive_within_signature" if self.a in h.members and self.r in h.members
                        and self.ar not in h.members else
                        "non_expansive" if self.a in h.members and self.r in h.members else "domain_error")
            self.assertEqual(res["status"], expected)
            within_count += 1
            sig_result = g.generation_signature(h, self.e)
            self.assertEqual(sig_result["status"], "expansive_signature_generation"
                             if self.a in h.members else "domain_error")
            sig_count += 1
        tally("all_nonempty_s1_families_within_generation", within_count)
        tally("all_nonempty_s1_families_signature_generation", sig_count)
        self.assertEqual((within_count, sig_count), (15, 15))

    def test_exhaustive_all_registered_generator_candidates(self):
        within_cases = 0
        signature_cases = 0
        for h in all_subfamilies(g.SIG1):
            for candidate in g.configs(g.SIG1):
                result = g.generation_within(h, candidate)
                if candidate == self.ar and self.a in h.members and self.r in h.members:
                    expected = "non_expansive" if self.ar in h.members else "expansive_within_signature"
                else:
                    expected = "domain_error"
                self.assertEqual(result["status"], expected)
                within_cases += 1
            for candidate in g.configs(g.SIG2):
                result = g.generation_signature(h, candidate)
                expected = "expansive_signature_generation" if candidate == self.e and self.a in h.members else "domain_error"
                self.assertEqual(result["status"], expected)
                signature_cases += 1
        self.assertEqual((within_cases, signature_cases), (60, 90))
        tally("all_registered_within_rule_candidate_cases", within_cases)
        tally("all_registered_signature_rule_candidate_cases", signature_cases)

    def test_exhaustive_differentiation_family_subsets(self):
        base = g.family(g.SIG0, "base", (self.u,))
        source_s1 = g.family(g.SIG1, "full", g.configs(g.SIG1))
        s1_count, s2_count = 0, 0
        for h in all_subfamilies(g.SIG1, include_empty=True):
            expected = "constitutive_refinement" if len(h.members) >= 2 else "not_established"
            self.assertEqual(g.differentiate(base, h)["status"], expected)
            s1_count += 1
        for h in all_subfamilies(g.SIG2, include_empty=True):
            ground_ids = [g.ground(x, g.SIG1) for x in h.members]
            has_split = len(set(ground_ids)) < len(ground_ids)
            expected = "constitutive_refinement" if has_split else "not_established"
            self.assertEqual(g.differentiate(source_s1, h)["status"], expected)
            s2_count += 1
        self.assertEqual((s1_count, s2_count), (16, 64))
        tally("exhaustive_s0_to_s1_family_refinement", s1_count)
        tally("exhaustive_s1_to_s2_family_refinement", s2_count)

    def test_selective_choice_and_preserved_families(self):
        res = g.choose(self.h1, self.a, "idA", "reviewer:bob")
        self.assertEqual(res["status"], "selected")
        self.assertTrue(res["source_family_preserved"])
        self.assertEqual(res["unchosen_member_count"], 1)
        self.assertEqual(res["choice_act"]["authority_status"], "unverified_no_commit_authority")
        self.assertFalse(res["external_enactment"])

    def test_selection_nonmember_unavailable_and_policy(self):
        self.assertEqual(g.choose(self.h1, self.ar, "x", "alice")["status"], "rejected_nonmember")
        self.assertEqual(g.choose(self.h1, None, "x", "alice")["status"], "unresolved")
        self.assertEqual(g.choose(self.h1, None, "x", "alice", "registered_policy", "wrong")["status"], "unsupported")
        valid = g.choose(self.h1, None, "x", "alice", "registered_policy", "first_canonical/v1")
        self.assertEqual(valid["status"], "selected")
        self.assertEqual(valid["choice_act"]["mechanism"], "registered_policy")

    def test_all_finite_family_choice_membership_pairs(self):
        evaluated, accepted, rejected = 0, 0, 0
        basis = g.configs(g.SIG2)
        for h in all_subfamilies(g.SIG2):
            for i, cfg in enumerate(basis):
                result = g.choose(h, cfg, f"test-{i}", "test-fixture")
                self.assertEqual(result["status"], "selected" if cfg in h.members else "rejected_nonmember")
                evaluated += 1
                accepted += int(cfg in h.members)
                rejected += int(cfg not in h.members)
        tally("exhaustive_selection_membership_pairs", evaluated)
        tally("exhaustive_selection_positive", accepted)
        tally("exhaustive_selection_negative", rejected)
        self.assertEqual((evaluated, accepted, rejected), (378, 192, 186))

    def test_empty_family_distinct_from_failure(self):
        empty = g.family(g.SIG1, "empty", ())
        self.assertEqual(g.choose(empty, None, "empty-choice", "reviewer")['status'], "unresolved")
        self.assertNotEqual(g.choose(empty, None, "empty-choice", "reviewer")['status'], "invalid_input")

    def test_different_history_identity_same_outcome(self):
        x = g.choose(self.h1, self.a, "event-1", "reviewer")
        y = g.choose(self.h1, self.a, "event-2", "reviewer")
        self.assertEqual(x["choice_act"]["selected_config"], y["choice_act"]["selected_config"])
        self.assertNotEqual(x["choice_act"], y["choice_act"])

    def test_replay_same_and_forged_receipts(self):
        request = {"op": "choose", "family": g.family_record(self.h1),
                   "candidate": g.config_record(self.a), "choice_id": "e1", "actor_ref": "reviewer"}
        item = g.receipt(request)
        self.assertTrue(g.verify_receipt(item))
        self.assertEqual(item, g.receipt(request))
        forged = copy.deepcopy(item)
        forged["outcome"]["external_enactment"] = True
        self.assertFalse(g.verify_receipt(forged))
        forged["digest_sha256"] = g.digest({k: forged[k] for k in
                                             ("kernel_base", "profile", "model", "request", "outcome")})
        self.assertFalse(g.verify_receipt(forged))  # digest match != replay match
        forged2 = copy.deepcopy(item)
        forged2["request"]["family"]["members"] = []
        self.assertFalse(g.verify_receipt(forged2))

    def test_selection_to_family_requires_explicit_adapter(self):
        receipt = g.receipt({"op": "choose", "family": g.family_record(self.h1),
                             "candidate": g.config_record(self.a), "choice_id": "actZ", "actor_ref": "x"})
        seeded = g.seed_family_from_choice(self.h1, receipt, "selected-only")
        self.assertEqual(seeded["status"], "seeded_singleton_family")
        self.assertEqual(len(seeded["excluded"]), 1)
        self.assertEqual(seeded["excluded"][0], g.config_record(self.r))
        self.assertEqual(g.read_family(seeded["target"]).dependency_id, self.h1.dependency_id)

    def test_noncommutation_typed_paths(self):
        # Choose -> typed seed adapter -> generation loses R from seeded family.
        choice = g.receipt({"op": "choose", "family": g.family_record(self.h1),
                            "candidate": g.config_record(self.a), "choice_id": "typed1", "actor_ref": "x"})
        seeded = g.read_family(g.seed_family_from_choice(self.h1, choice, "seed")["target"])
        first = g.read_family(g.generation_signature(seeded, self.e)["target"])
        # Generate -> choose keeps the unchosen R alternative in source family.
        second = g.read_family(g.generation_signature(self.h1, self.e)["target"])
        self.assertNotEqual(first.members, second.members)
        self.assertNotIn(g.embed(self.r, g.SIG2), first.members)
        self.assertIn(g.embed(self.r, g.SIG2), second.members)
        self.assertIn(g.embed(self.r, g.SIG2), g.read_family(g.family_record(second)).members)

    def test_model_only_commit_requires_independent_fixture_grant(self):
        receipt = g.receipt({"op": "choose", "family": g.family_record(self.h1),
                             "candidate": g.config_record(self.a), "choice_id": "model", "actor_ref": "reviewer:alice"})
        denied = g.commit_model(self.h1, receipt, "reviewer:alice", "wrong-grant", 0, "evt")
        self.assertEqual(denied["status"], "unauthorised")
        good = g.commit_model(self.h1, receipt, "reviewer:alice", "fixture-grant-alice", 0, "evt")
        self.assertEqual(good["status"], "model_committed")
        self.assertFalse(good["physical_or_external_effect"])
        self.assertEqual(good["event"]["new_epoch"], 1)

    def test_stale_family_cannot_commit(self):
        receipt = g.receipt({"op": "choose", "family": g.family_record(self.h1),
                             "candidate": g.config_record(self.a), "choice_id": "model", "actor_ref": "reviewer:alice"})
        altered = g.family(g.SIG1, "variants-v2", self.h1.members, self.h1.dependency_id)
        self.assertEqual(g.commit_model(altered, receipt, "reviewer:alice", "fixture-grant-alice", 0, "evt")["status"], "rejected")

    def test_commit_rejects_forged_receipt(self):
        receipt = g.receipt({"op": "choose", "family": g.family_record(self.h1),
                             "candidate": g.config_record(self.a), "choice_id": "c1", "actor_ref": "reviewer:alice"})
        receipt["outcome"]["external_enactment"] = True
        self.assertEqual(g.commit_model(self.h1, receipt, "reviewer:alice", "fixture-grant-alice", 0, "evt")["status"], "rejected")

    def test_shared_dependency_is_not_independent_choice(self):
        after_within = g.read_family(g.generation_within(self.h1, self.ar)["target"])
        after_sig = g.read_family(g.generation_signature(after_within, self.e)["target"])
        self.assertEqual({self.h1.dependency_id, after_within.dependency_id,
                          after_sig.dependency_id}, {"source-X"})
        self.assertNotEqual(len(after_sig.members), len(after_within.members) * 2)

    def test_finite_recursive_rule_and_limit(self):
        for n in range(9):
            item = g.lift("source", n)
            self.assertEqual(item["status"], "finite_chain")
            self.assertEqual(len(item["chain"]), n+1)
            for i in range(1, len(item["chain"])):
                self.assertEqual(item["chain"][i]["parent_digest"], item["chain"][i-1]["digest"])
            self.assertFalse(item["infinity_claim"])
        tally("bounded_recursive_ranks_checked", 9)
        self.assertEqual(g.lift("source", 9)["status"], "resource_limit")

    def test_full_example_and_complete_replay(self):
        example = g.complete_example()
        statuses = [v["outcome"]["status"] for v in example["stages"].values()]
        self.assertEqual(statuses, ["constitutive_refinement", "expansive_within_signature",
                                    "expansive_signature_generation", "selected", "model_committed"])
        for item in example["stages"].values():
            self.assertTrue(g.verify_receipt(item))
        self.assertFalse(example["external_effects"])

    def test_unsupported_or_bad_dispatch_is_distinct(self):
        self.assertEqual(g.execute({"op": "unregistered"})["status"], "unsupported")
        self.assertEqual(g.execute({"foo": "bar"})["status"], "invalid_input")
        self.assertNotEqual(g.execute({"op": "unregistered"})["status"], "non_expansive")

    def test_typed_receipt_from_operations(self):
        r = g.receipt({"op": "differentiate", "source": g.family_record(self.h0),
                       "target": g.family_record(self.h1)})
        self.assertEqual(r["profile"], g.PROFILE)
        self.assertEqual(r["kernel_base"], g.BASE)
        self.assertTrue(g.verify_receipt(r))

    def test_concrete_grounding_not_identity_and_noninvertible(self):
        a2 = g.embed(self.a, g.SIG2)
        self.assertNotEqual(self.e, a2)
        self.assertEqual(g.ground(a2, g.SIG1), g.ground(self.e, g.SIG1))
        self.assertEqual(g.ground(self.e, g.SIG0), self.u)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-report", help="output compact conformance summary")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GCDTests)
    run = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {"model": g.MODEL, "kernel_base": g.BASE, "named_tests": run.testsRun,
               "failures": len(run.failures), "errors": len(run.errors),
               "passed": run.wasSuccessful(), "finite_counts": COUNTS,
               "scope": "Exhaustive on specifically enumerated finite domains only",
               "non_claims": ["full v0.15 conformance", "external verification", "external act attribution",
                              "production authorisation"]}
    if args.json_report:
        with open(args.json_report, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, sort_keys=True)
            fh.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if run.wasSuccessful() else 1)
