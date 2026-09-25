"""Checked first-stage control extraction and independent wire-level machine.

The whole-function AST pin guards omitted statements. The extraction below
checks the semantic control sites and produces a small instruction schedule.
The machine interprets that schedule without calling either implementation.
This is a bounded code-facing check, not a CPython soundness proof.
"""

import ast
from dataclasses import dataclass

from e7c_joint_control_flow_pin import ROOT, ENTRY_POINTS, fingerprint
from e7c_eecq_joint_restrict_b1 import EFFECTS, PREDICATE_EDITION
from e7c_b1_canonical import canonical_key


@dataclass(frozen=True)
class Program:
    path: str
    row_iterator: str
    predicate: str
    instructions: tuple[str, ...]


SCHEDULE = (
    "check_step", "charge_attempt", "check_ledger", "append_attempt",
    "check_capability", "check_obligation", "iterate_rows",
    "check_step", "charge_row", "check_ledger", "decide_row",
    "append_row", "finish_success",
)


def _statements(fn):
    """Keep nested control and helpers in their original traversal order."""
    return [node for node in ast.walk(fn) if isinstance(node, ast.stmt)]


def _require(nodes, kind, expression):
    expected = ast.dump(ast.parse(expression).body[0], include_attributes=False)
    found = [node for node in nodes if isinstance(node, kind)
             and ast.dump(node, include_attributes=False) == expected]
    if len(found) != 1:
        raise ValueError("control site missing or duplicated: " + expression)
    return found[0]


def extract(path):
    """Reject a changed full AST or a missing/altered charge and guard site."""
    code = (ROOT / path).read_text()
    if fingerprint(code, "evaluate" if path.startswith("e7c_") else "execute") != \
            ENTRY_POINTS[path, "evaluate" if path.startswith("e7c_") else "execute"]:
        raise ValueError("unreviewed first-stage implementation")
    name = "evaluate" if path.startswith("e7c_") else "execute"
    fn = next(node for node in ast.parse(code).body
              if isinstance(node, ast.FunctionDef) and node.name == name)
    source = path.startswith("e7c_")
    checks = [
        'if beta["step_bound"] == 0:\n    return finish(limit())' if source else
        'if beta["step_bound"] == 0:\n    return result(limit())',
        'if beta["ledger_bound"] == 0:\n    return finish(limit())' if source else
        'if beta["ledger_bound"] == 0:\n    return result(limit())',
        'if not interp["capability"]:\n    return finish({"tag": "unsupported", "diagnostic": "joint_restriction_unavailable"})' if source else
        'if not interp["capability"]:\n    return result({"tag": "unsupported", "diagnostic": "joint_restriction_unavailable"})',
        'if interp["obligation"] != "resolved":\n    return finish({"tag": "undetermined", "diagnostic": "joint_predicate_unresolved"})' if source else
        'if interp["obligation"] == "unresolved":\n    return result({"tag": "undetermined", "diagnostic": "joint_predicate_unresolved"})',
        'if steps >= beta["step_bound"]:\n    return finish(limit())' if source else
        'if steps >= beta["step_bound"]:\n    return result(limit())',
        'if len(ledger) >= beta["ledger_bound"]:\n    return finish(limit())' if source else
        'if len(ledger) >= beta["ledger_bound"]:\n    return result(limit())',
    ]
    stmts = _statements(fn)
    for expression in checks:
        _require(stmts, ast.stmt, expression)
    charges = [n for n in stmts if isinstance(n, ast.AugAssign)
               and ast.unparse(n) == "steps += 1"]
    if len(charges) != 2:
        raise ValueError("expected attempt and row charges")
    loops = [n for n in stmts if isinstance(n, ast.For)]
    if len(loops) != 1:
        raise ValueError("expected one first-stage row traversal")
    iterator = ast.unparse(loops[0].iter)
    expected_iterator = "enumerate(value.terms)" if source else 'enumerate(source["rows"])'
    if ast.dump(loops[0].iter) != ast.dump(ast.parse(expected_iterator, mode="eval").body):
        raise ValueError("first-stage row order changed")
    predicate = '"AB" in atoms[0].edges' if source else '"AB" in row["atoms"][0]["edges"]'
    tests = [ast.unparse(n.test) for n in ast.walk(loops[0]) if isinstance(n, ast.IfExp)]
    expected_tests = [ast.unparse(ast.parse(predicate, mode="eval").body)]
    if not source:
        expected_tests.append("decision == 'excluded'")
    if tests != expected_tests:
        raise ValueError("first-stage decision changed")
    return Program(path, iterator, predicate, SCHEDULE)


def run(program, wire_rows, step_bound, ledger_bound, capability, obligation,
        *, transitions=None):
    """Execute only the extracted first-stage schedule on exact wire rows.

    Contract: admitted rows in source order, nonnegative integer bounds,
    Boolean capability and resolved/unresolved obligation. Excludes host
    failures, Python witness construction and IR parse/size checks.
    """
    if program.instructions != SCHEDULE:
        raise ValueError("unsupported control program")
    if (type(step_bound) is not int or type(ledger_bound) is not int
            or min(step_bound, ledger_bound) < 0
            or type(capability) is not bool
            or obligation not in ("resolved", "unresolved")):
        raise ValueError("outside the admitted schedule domain")
    steps, ledger, retained, excluded = 0, [], [], []

    def emit(action, index=None):
        if transitions is not None:
            transitions.append({"action": action, "stage": "first",
                                "row_index": index, "steps": steps,
                                "ledger_entries": len(ledger),
                                "event": dict(ledger[-1]) if action == "append" else None})

    def result(tag, diagnostic=None):
        progress = {"completed_steps": steps, "completed_ledger_entries": len(ledger),
                    "ledger_prefix": list(ledger)}
        terminal = {"tag": tag}
        if tag == "resource_limit":
            terminal["progress"] = progress
        elif tag == "success":
            terminal["value"] = {"retained": retained, "excluded": excluded,
                                 "predicate_edition": PREDICATE_EDITION}
        else:
            terminal["diagnostic"] = diagnostic
        return {"terminal_outcome": terminal, "ordered_ledger": list(ledger),
                "resource_progress": progress}

    if step_bound == 0:
        return result("resource_limit")
    steps += 1
    emit("charge")
    if ledger_bound == 0:
        return result("resource_limit")
    ledger.append({"ordinal": 0, "event": "restriction_attempt",
                   "effect": EFFECTS[0], "predicate_edition": PREDICATE_EDITION})
    emit("append")
    if not capability:
        return result("unsupported", "joint_restriction_unavailable")
    if obligation == "unresolved":
        return result("undetermined", "joint_predicate_unresolved")
    for index, row in enumerate(wire_rows):
        if steps >= step_bound:
            return result("resource_limit")
        steps += 1
        emit("charge", index)
        if len(ledger) >= ledger_bound:
            return result("resource_limit")
        excluded_here = "AB" in row["atoms"][0]["edges"]
        ledger.append({"ordinal": len(ledger), "event": "joint_row_checked",
                       "effect": EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(row),
                       "decision": "excluded" if excluded_here else "retained"})
        emit("append", index)
        (excluded if excluded_here else retained).append(row)
    return result("success")
