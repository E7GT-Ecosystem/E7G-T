import copy
import json
from pathlib import Path
import unittest

from e7c_b1_canonical import (
    INTERPRETATION_EDITION,
    bind_envelope,
    canonical_key,
    digest,
    node_digest_payload,
)
from e7c_b1_evaluator import EvaluationInputError, Evaluator, evaluate
from e7c_b1_replay_checker import check_witness


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "wp2"


def document(term, *, steps=20, candidates=20, ledger=20):
    environment = json.loads((FIXTURES / "positive.json").read_text(encoding="utf-8"))["environment"]
    config_a = {"id": "a", "valid": True}
    config_b = {"id": "b", "valid": False}
    config_c = {"id": "c", "valid": True}
    config_a_type = environment["variables"]["source_config"]
    config_b_type = environment["maps"]["strict_normalise"]["target"]
    summary_type = environment["views"]["source_preserving_inventory"]["target"]
    return {
        "environment": environment,
        "term": copy.deepcopy(term),
        "values": {
            "source_config": config_a,
            "source_family": [config_a, config_b, config_c],
            "source_view": {
                "kind": "source_preserving",
                "declaration": "source_preserving_inventory",
                "representation": {"bucket": "one"},
                "source_return_token": config_a,
            },
            "source_projection": {
                "kind": "projection",
                "declaration": "lossy_projection",
                "representation": {"count": 3},
                "source_return_token": None,
            },
            "terminal_result": {"tag": "domain_error", "diagnostic": "bound-domain-error"},
            "source_fibre": [config_a, config_c],
        },
        "interpretation": {
            "interpretation_edition": INTERPRETATION_EDITION,
            "carriers": {
                canonical_key(config_a_type): [config_a, config_b, config_c],
                canonical_key(config_b_type): [{"id": "A"}, {"id": "C"}],
                canonical_key(summary_type): [
                    {"bucket": "one"}, {"bucket": "two"},
                    {"count": 1}, {"count": 2}, {"count": 3},
                ],
            },
            "maps": {
                "strict_normalise": {
                    "capability": True,
                    "obligation": "resolved",
                    "cases": [
                        {"input": config_a, "in_domain": True, "output": {"id": "A"}},
                        {"input": config_b, "in_domain": False},
                        {"input": config_c, "in_domain": True, "output": {"id": "C"}},
                    ],
                },
                "total_identity": {
                    "capability": True,
                    "obligation": "resolved",
                    "cases": [
                        {"input": config_a, "in_domain": True, "output": config_a},
                        {"input": config_b, "in_domain": True, "output": config_b},
                        {"input": config_c, "in_domain": True, "output": config_c},
                    ],
                },
            },
            "views": {
                "source_preserving_inventory": {
                    "capability": True,
                    "obligation": "resolved",
                    "cases": [
                        {"input": config_a, "output": {"bucket": "one"}},
                        {"input": config_b, "output": {"bucket": "two"}},
                        {"input": config_c, "output": {"bucket": "one"}},
                    ],
                },
                "lossy_projection": {
                    "capability": True,
                    "obligation": "resolved",
                    "cases": [
                        {"input": config_a, "output": {"count": 1}},
                        {"input": config_b, "output": {"count": 2}},
                        {"input": config_c, "output": {"count": 3}},
                    ],
                },
            },
            "restrictions": {
                "select_J": {
                    "capability": True,
                    "obligation": "resolved",
                    "retained_keys": [canonical_key(config_a), canonical_key(config_c)],
                }
            },
            "reconstructions": {
                "exact_reconstruction": {
                    "capability": True,
                    "obligation": "resolved",
                    "carrier_finite": True,
                    "equality_resolved": True,
                    "constraint_resolved": True,
                    "carrier": [config_a, config_b, config_c],
                }
            },
            "criteria": {
                "phase_by_shape": {
                    "capability": True,
                    "obligation": "resolved",
                    "cases": [
                        {"input": config_a, "output": "stable"},
                        {"input": config_b, "output": "unstable"},
                        {"input": config_c, "output": "stable"},
                    ],
                }
            },
        },
        "resource_policy": {
            "step_bound": steps,
            "candidate_bound": candidates,
            "ledger_entry_bound": ledger,
            "policy_edition": "bounded-test-1",
        },
        "pins": {"outcome_extension_edition": "core-1"},
        "external_assumptions": {
            "source_references": [],
            "authority_asserted": False,
            "scope": "unit-test-fixture",
            "time": "2026-09-16T00:00:00Z",
            "modality": "asserted-fixture",
            "model_edition": "finite-table-1",
            "policy_labels": ["non-authoritative"],
        },
    }


VAR = {"tag": "var", "name": "source_config"}
STRICT = {"tag": "apply", "declaration": "strict_normalise", "arg": VAR}
VIEW = {"tag": "view", "declaration": "source_preserving_inventory", "arg": VAR}
RECONSTRUCT = {
    "tag": "reconstruct",
    "declaration": "exact_reconstruction",
    "resource_policy": "bounded-100",
    "arg": VIEW,
}
RECONSTRUCT_BOUND_VIEW = {
    "tag": "reconstruct",
    "declaration": "exact_reconstruction",
    "resource_policy": "bounded-100",
    "arg": {"tag": "var", "name": "source_view"},
}
RESTRICT = {
    "tag": "restrict",
    "declaration": "select_J",
    "arg": {"tag": "var", "name": "source_family"},
}
CLASSIFY = {
    "tag": "classify",
    "declaration": "phase_by_shape",
    "arg": {"tag": "var", "name": "source_fibre"},
}


def rebind_derivation_and_envelope(witness):
    remapped = {}
    nodes = witness["derivation_record"]["nodes_bottom_up"]
    for node in nodes:
        old_id = node["node_id"]
        node["child_node_ids"] = [remapped.get(child, child) for child in node["child_node_ids"]]
        node["node_id"] = digest(node_digest_payload(node))
        remapped[old_id] = node["node_id"]
    witness["derivation_record"]["root_node_id"] = nodes[-1]["node_id"]
    return bind_envelope({key: value for key, value in witness.items() if key != "integrity"})


def replace_claimed_terminal(witness, terminal):
    witness["evaluation_claim"]["terminal_outcome"] = copy.deepcopy(terminal)
    witness["derivation_record"]["nodes_bottom_up"][-1]["terminal_outcome"] = copy.deepcopy(terminal)
    return rebind_derivation_and_envelope(witness)


class WP3IDisposableEvaluatorTests(unittest.TestCase):
    def test_outcome_typed_variable_propagates_without_double_wrapping(self):
        result = evaluate(document({"tag": "var", "name": "terminal_result"}))
        self.assertEqual(result["terminal_outcome"]["tag"], "domain_error")
        self.assertNotIn("value", result["terminal_outcome"])

    def test_nested_non_success_propagates_with_ledger_prefix(self):
        source = document(RECONSTRUCT)
        source["interpretation"]["views"]["source_preserving_inventory"]["capability"] = False
        result = evaluate(source)
        self.assertEqual(result["terminal_outcome"]["tag"], "unsupported")
        self.assertEqual(
            [entry["static_atom"]["dimension"] for entry in result["ordered_ledger"]],
            ["inquiry", "alternatives"],
        )

    def test_zero_step_bound_precedes_variable_lookup(self):
        result = evaluate(document(VAR, steps=0))
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["resource_progress"]["completed_steps"], 0)

    def test_ledger_exhaustion_precedes_domain_failure(self):
        source = document(STRICT, ledger=0)
        source["values"]["source_config"] = {"id": "b", "valid": False}
        result = evaluate(source)
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["ordered_ledger"], [])

    def test_strict_domain_failure_retains_ordered_map_ledger(self):
        source = document(STRICT)
        source["values"]["source_config"] = {"id": "b", "valid": False}
        result = evaluate(source)
        self.assertEqual(result["terminal_outcome"]["tag"], "domain_error")
        self.assertEqual(
            [entry["static_atom"]["dimension"] for entry in result["ordered_ledger"]],
            ["evidence", "partiality"],
        )

    def test_filtering_records_retained_and_excluded_alternatives(self):
        term = {"tag": "apply", "declaration": "total_identity", "arg": VAR}
        source = document(term)
        source["environment"]["maps"]["total_identity"]["domain_policy"] = "filtering"
        for case in source["interpretation"]["maps"]["total_identity"]["cases"]:
            case["retained"] = [copy.deepcopy(case["input"])]
            case["excluded"] = []
        result = evaluate(source)
        partiality = result["ordered_ledger"][1]
        self.assertEqual(partiality["static_atom"]["dimension"], "partiality")
        self.assertEqual(partiality["detail"]["retained"], [{"id": "a", "valid": True}])
        self.assertEqual(partiality["detail"]["excluded"], [])

    def test_restriction_uses_canonical_family_order(self):
        source = document(RESTRICT)
        source["values"]["source_family"].reverse()
        result = evaluate(source)
        self.assertEqual([item["id"] for item in result["terminal_outcome"]["value"]], ["a", "c"])
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 3)

    def test_restriction_candidate_exhaustion_prevents_partial_success(self):
        result = evaluate(document(RESTRICT, candidates=2))
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 2)
        self.assertEqual(result["resource_progress"]["last_candidate_key"], canonical_key({"id": "b", "valid": False}))

    def test_classification_charges_each_candidate(self):
        result = evaluate(document(CLASSIFY, candidates=2))
        self.assertEqual(result["terminal_outcome"]["tag"], "success")
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 2)

    def test_classification_candidate_exhaustion_prevents_partial_success(self):
        result = evaluate(document(CLASSIFY, candidates=1))
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertNotIn("value", result["terminal_outcome"])
        self.assertEqual(result["resource_progress"]["last_candidate_key"], canonical_key({"id": "a", "valid": True}))

    def test_complete_fibre_is_canonical_and_exhaustive(self):
        result = evaluate(document(RECONSTRUCT))
        self.assertEqual(result["terminal_outcome"]["tag"], "success")
        self.assertEqual(
            [item["id"] for item in result["terminal_outcome"]["value"]],
            ["a", "c"],
        )
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 3)

    def test_candidate_exhaustion_never_returns_partial_success(self):
        result = evaluate(document(RECONSTRUCT, candidates=2))
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertNotIn("value", result["terminal_outcome"])
        self.assertEqual(
            [entry["static_atom"]["dimension"] for entry in result["ordered_ledger"][-2:]],
            ["resources", "alternatives"],
        )

    def test_missing_reconstruction_capability_precedes_other_failures(self):
        source = document(RECONSTRUCT, candidates=0)
        record = source["interpretation"]["reconstructions"]["exact_reconstruction"]
        record["capability"] = False
        record["obligation"] = "unresolved"
        record["equality_resolved"] = False
        result = evaluate(source)
        self.assertEqual(result["terminal_outcome"]["tag"], "unsupported")
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 0)

    def test_unresolved_equality_precedes_candidate_exhaustion(self):
        source = document(RECONSTRUCT, candidates=0)
        source["interpretation"]["reconstructions"]["exact_reconstruction"]["equality_resolved"] = False
        result = evaluate(source)
        self.assertEqual(result["terminal_outcome"]["tag"], "undetermined")
        self.assertEqual(result["resource_progress"]["completed_candidate_checks"], 0)

    def test_projection_cannot_bind_a_source_preserving_view_variable(self):
        source = document(RECONSTRUCT_BOUND_VIEW)
        source["values"]["source_view"] = {
            "kind": "projection",
            "declaration": "source_preserving_inventory",
            "representation": {"bucket": "one"},
            "source_return_token": None,
        }
        with self.assertRaisesRegex(EvaluationInputError, "nominal view policy"):
            evaluate(source)

    def test_missing_candidate_comparison_prevents_fibre_success(self):
        source = document(RECONSTRUCT_BOUND_VIEW)
        cases = source["interpretation"]["views"]["source_preserving_inventory"]["cases"]
        source["interpretation"]["views"]["source_preserving_inventory"]["cases"] = [
            case for case in cases if case["input"]["id"] != "c"
        ]
        with self.assertRaisesRegex(EvaluationInputError, "lacks source-carrier coverage"):
            evaluate(source)

    def test_total_map_requires_a_target_case_for_its_input(self):
        term = {"tag": "apply", "declaration": "total_identity", "arg": VAR}
        source = document(term)
        source["interpretation"]["maps"]["total_identity"]["cases"] = []
        with self.assertRaisesRegex(EvaluationInputError, "lacks source-carrier coverage"):
            evaluate(source)

    def test_plain_runtime_value_must_belong_to_declared_carrier(self):
        source = document(VAR)
        source["values"]["source_config"] = {"id": "outside", "valid": True}
        with self.assertRaisesRegex(EvaluationInputError, "outside its declared carrier"):
            evaluate(source)

    def test_interpretation_requires_explicit_obligation(self):
        source = document(VAR)
        del source["interpretation"]["maps"]["total_identity"]["obligation"]
        with self.assertRaisesRegex(EvaluationInputError, "non-canonical fields"):
            evaluate(source)

    def test_failed_candidate_does_not_advance_last_completed_key(self):
        evaluator = Evaluator(document(RECONSTRUCT_BOUND_VIEW))
        evaluator.interpretation["views"]["source_preserving_inventory"]["cases"].pop()
        with self.assertRaisesRegex(EvaluationInputError, "reconstruction comparison"):
            evaluator.run()
        progress = evaluator.state.progress()
        self.assertEqual(progress["completed_candidate_checks"], 3)
        self.assertEqual(progress["last_candidate_key"], canonical_key({"id": "b", "valid": False}))


class WP3IIndependentReplayTests(unittest.TestCase):
    def witness(self):
        return evaluate(document(RECONSTRUCT))["witness"]

    def test_independent_checker_accepts_exact_replay(self):
        result = check_witness(self.witness())
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["claim"], "bounded_derivation_replay")

    def test_unbound_tamper_is_rejected_by_digest(self):
        witness = self.witness()
        witness["runtime_inputs"]["values"]["source_config"]["id"] = "tampered"
        self.assertEqual(check_witness(witness)["diagnostic"], "digest_mismatch")

    def test_missing_inline_material_is_rejected(self):
        witness = self.witness()
        del witness["runtime_inputs"]["interpretation"]
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "missing_replay_material")

    def test_rule_edition_substitution_is_rejected(self):
        witness = self.witness()
        witness["rule_pins"]["dynamic_rules_identity"] = "newer-is-not-equivalent"
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "edition_mismatch")

    def test_authority_claim_escalation_is_rejected(self):
        witness = self.witness()
        witness["identity"]["claim_class"] = "source_truth"
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "authority_claim_escalation")

    def test_nested_optional_witness_binding_is_verified(self):
        witness = self.witness()
        witness["evaluation_claim"]["terminal_outcome"]["optional_witness"] = "forged"
        self.assertEqual(check_witness(witness)["diagnostic"], "identity_mismatch")

    def test_node_identifier_binding_is_verified(self):
        witness = self.witness()
        witness["derivation_record"]["nodes_bottom_up"][0]["node_id"] = "forged"
        self.assertEqual(check_witness(witness)["diagnostic"], "digest_mismatch")

    def test_rebound_false_ledger_is_rejected_by_replay(self):
        witness = self.witness()
        witness["evaluation_claim"]["ordered_ledger"].reverse()
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "ledger_mismatch")

    def test_unknown_mandatory_field_is_not_ignored(self):
        witness = self.witness()
        witness["runtime_inputs"]["mandatory_future_rule"] = True
        self.assertEqual(check_witness(witness)["diagnostic"], "malformed_witness")

    def test_rebound_projection_as_exact_view_is_rejected_before_replay(self):
        witness = evaluate(document(RECONSTRUCT_BOUND_VIEW))["witness"]
        forged_view = {
            "kind": "projection",
            "declaration": "source_preserving_inventory",
            "representation": {"bucket": "one"},
            "source_return_token": None,
        }
        witness["runtime_inputs"]["values"]["source_view"] = copy.deepcopy(forged_view)
        witness["derivation_record"]["nodes_bottom_up"][0]["terminal_outcome"] = {
            "tag": "success",
            "value": copy.deepcopy(forged_view),
            "optional_witness": None,
        }
        witness = rebind_derivation_and_envelope(witness)
        result = check_witness(witness)
        self.assertEqual(result["diagnostic"], "runtime_input_mismatch")

    def test_rebound_false_complete_fibre_is_rejected_for_missing_comparison(self):
        witness = evaluate(document(RECONSTRUCT_BOUND_VIEW))["witness"]
        cases = witness["runtime_inputs"]["interpretation"]["views"]["source_preserving_inventory"]["cases"]
        witness["runtime_inputs"]["interpretation"]["views"]["source_preserving_inventory"]["cases"] = [
            case for case in cases if case["input"]["id"] != "c"
        ]
        false_success = {
            "tag": "success",
            "value": [{"id": "a", "valid": True}],
            "optional_witness": None,
        }
        witness = replace_claimed_terminal(witness, false_success)
        result = check_witness(witness)
        self.assertEqual(result["diagnostic"], "missing_replay_material")

    def test_rebound_total_map_domain_error_is_rejected_for_missing_case(self):
        term = {"tag": "apply", "declaration": "total_identity", "arg": VAR}
        witness = evaluate(document(term))["witness"]
        witness["runtime_inputs"]["interpretation"]["maps"]["total_identity"]["cases"] = []
        false_domain_error = {
            "tag": "domain_error",
            "diagnostic": "outside-domain:total_identity",
        }
        witness = replace_claimed_terminal(witness, false_domain_error)
        result = check_witness(witness)
        self.assertEqual(result["diagnostic"], "missing_replay_material")

    def test_rebound_runtime_value_outside_carrier_is_rejected(self):
        witness = self.witness()
        witness["runtime_inputs"]["values"]["source_config"] = {"id": "outside", "valid": True}
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "runtime_input_mismatch")

    def test_rebound_missing_obligation_is_rejected_at_admission(self):
        witness = self.witness()
        del witness["runtime_inputs"]["interpretation"]["maps"]["total_identity"]["obligation"]
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "runtime_input_mismatch")

    def test_rebound_missing_carrier_is_rejected_at_admission(self):
        witness = self.witness()
        carriers = witness["runtime_inputs"]["interpretation"]["carriers"]
        del carriers[next(iter(carriers))]
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "missing_replay_material")

    def test_duplicate_derivation_node_identifier_is_rejected(self):
        witness = self.witness()
        nodes = witness["derivation_record"]["nodes_bottom_up"]
        nodes[1]["node_id"] = nodes[0]["node_id"]
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "malformed_witness")

    def test_derivation_cycle_is_rejected(self):
        witness = self.witness()
        nodes = witness["derivation_record"]["nodes_bottom_up"]
        nodes[0]["child_node_ids"] = [nodes[-1]["node_id"]]
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "derivation_order_mismatch")

    def test_orphan_derivation_node_is_rejected(self):
        witness = self.witness()
        orphan = copy.deepcopy(witness["derivation_record"]["nodes_bottom_up"][0])
        orphan["term"] = {"tag": "var", "name": "source_family"}
        orphan["node_id"] = digest(node_digest_payload(orphan))
        witness["derivation_record"]["nodes_bottom_up"].insert(-1, orphan)
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "malformed_witness")

    def test_dangling_derivation_child_is_rejected(self):
        witness = self.witness()
        witness["derivation_record"]["nodes_bottom_up"][-1]["child_node_ids"].append("missing-node")
        witness = bind_envelope({key: value for key, value in witness.items() if key != "integrity"})
        self.assertEqual(check_witness(witness)["diagnostic"], "missing_replay_material")


if __name__ == "__main__":
    unittest.main()
