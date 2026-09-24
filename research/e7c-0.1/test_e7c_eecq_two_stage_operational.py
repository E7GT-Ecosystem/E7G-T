"""Independent finite event-plan differential for the Lean operational rule.

This checks concrete encodings; it is not an all-input Python/Lean proof.
"""

from fractions import Fraction
import itertools
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_b1_canonical import canonical_key
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import execute, lower


P, Q, R = Config(("AB",), None), Config(("BC",), None), Config(("AC",), None)


def plan(source):
    first, second = source["first"]["interpretation"], source["second_interpretation"]
    rows = source["first"]["rows"]
    events = [("first_attempt", None, None, None)]
    first_ready = first["capability"] and first["obligation"] == "resolved"
    if not first_ready:
        return events, first_ready, False, []
    first_retained = []
    for i, row in enumerate(rows):
        excluded = "AB" in row["atoms"][0]["edges"]
        events.append(("first_row", i, row, excluded))
        if not excluded:
            first_retained.append(row)
    events.append(("second_attempt", None, None, None))
    second_ready = second["capability"] and second["obligation"] == "resolved"
    if second_ready:
        for i, row in enumerate(first_retained):
            events.append(("second_row", i, row, "BC" in row["atoms"][1]["edges"]))
    return events, first_ready, second_ready, first_retained


def projected(ledger):
    result = []
    for entry in ledger:
        event = entry["event"]
        if event == "restriction_attempt":
            result.append(("first_attempt", None, None, None))
        elif event == "second_restriction_attempt":
            result.append(("second_attempt", None, None, None))
        else:
            name = "first_row" if event == "joint_row_checked" else "second_row"
            result.append((name, entry["row_index"], entry["row_key"],
                           entry["decision"] in ("excluded", "second_excluded")))
    return result


def check(source):
    events, first_ready, second_ready, first_retained = plan(source)
    policy = source["first"]["resource_policy"]
    step_bound, ledger_bound = policy["step_bound"], policy["ledger_bound"]
    count = min(len(events), step_bound, ledger_bound)
    prefix = events[:count]
    expected_steps = (len(events) if count == len(events) else
                      step_bound if step_bound <= ledger_bound else ledger_bound + 1)
    actual = evaluate(source)
    independent = execute(lower(source))
    assert {k: v for k, v in actual.items() if k != "witness"} == independent
    assert projected(independent["ordered_ledger"]) == [
        (name, i, canonical_key(row) if row is not None else None, excluded)
        for name, i, row, excluded in prefix]
    assert independent["resource_progress"]["completed_steps"] == expected_steps
    assert independent["resource_progress"]["ledger_prefix"] == independent["ordered_ledger"]
    first_count = 1 + len(source["first"]["rows"])
    first_excluded = [row for row in source["first"]["rows"]
                      if "AB" in row["atoms"][0]["edges"]]
    expected_first = first_excluded if first_ready and count >= first_count else None
    assert independent["resource_progress"]["first_excluded"] == expected_first
    assert independent["resource_progress"]["second_excluded_prefix"] == [
        row for name, _, row, excluded in prefix if name == "second_row" and excluded]
    assert actual["witness"]["second_started"] == (first_ready and expected_steps > first_count)
    tag = ("resource_limit" if count < len(events) else
           "unsupported" if not source["first"]["interpretation"]["capability"] or
                            first_ready and not source["second_interpretation"]["capability"] else
           "undetermined" if not first_ready or not second_ready else "success")
    assert independent["terminal_outcome"]["tag"] == tag
    if tag == "success":
        value = independent["terminal_outcome"]["value"]
        assert value["first_excluded"] == first_excluded
        assert value["second_excluded"] == [r for r in first_retained
                                            if "BC" in r["atoms"][1]["edges"]]
        assert value["retained"] == [r for r in first_retained
                                      if "BC" not in r["atoms"][1]["edges"]]
    else:
        assert "value" not in independent["terminal_outcome"]


class OperationalDifferential(unittest.TestCase):
    def test_all_policy_and_budget_paths(self):
        supports = [joint([], arity=2), joint([(Fraction(-2, 3), (P, Q))], arity=2),
                    joint([(Fraction(-2, 3), (P, Q)), (Fraction(3, 5), (Q, R)),
                           (Fraction(1, 7), (R, Q))], arity=2)]
        for support, step, ledger, first_cap, first_obl, second_cap, second_obl in itertools.product(
                supports, range(8), range(8), (False, True), ("resolved", "unresolved"),
                (False, True), ("resolved", "unresolved")):
            source = document(support, step_bound=step, ledger_bound=ledger,
                              first_capability=first_cap, first_obligation=first_obl,
                              second_capability=second_cap, second_obligation=second_obl)
            with self.subTest(size=len(support.terms), step=step, ledger=ledger,
                              first=(first_cap, first_obl), second=(second_cap, second_obl)):
                check(source)


if __name__ == "__main__":
    unittest.main()
