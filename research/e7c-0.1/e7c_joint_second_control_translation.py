"""Selected second-stage control schedule for source and independent IR.

This checks the complete pinned entry-point AST and the stage-two control
sites. The separate interpreter consumes an already checked first-stage
observation; it does not call either second-stage implementation. Python host
semantics and package admission remain outside this bounded comparison.
"""

import ast
import copy
from dataclasses import dataclass

from e7c_b1_canonical import canonical_key
from e7c_eecq_two_stage_b1 import FIRST_PREDICATE, SECOND_EFFECTS, SECOND_PREDICATE
from e7c_joint_control_flow_pin import ENTRY_POINTS, ROOT, fingerprint


SCHEDULE = ("first_terminal", "check_step", "charge_attempt", "check_ledger",
            "append_attempt", "check_capability", "check_obligation",
            "iterate_retained", "check_step", "charge_row", "check_ledger",
            "append_row", "finish")


@dataclass(frozen=True)
class Program:
    path: str
    instructions: tuple[str, ...]


def extract(path):
    if path not in ("e7c_eecq_two_stage_b1.py", "e7_ir_eecq_two_stage_b1.py"):
        raise ValueError("unknown second-stage entry point")
    code = (ROOT / path).read_text()
    if fingerprint(code, "evaluate" if path.startswith("e7c_") else "execute") != \
            ENTRY_POINTS[path, "evaluate" if path.startswith("e7c_") else "execute"]:
        raise ValueError("unreviewed second-stage implementation")
    name = "evaluate" if path.startswith("e7c_") else "execute"
    fn = next(n for n in ast.parse(code).body
              if isinstance(n, ast.FunctionDef) and n.name == name)
    source = path.startswith("e7c_")
    body = ast.get_source_segment(code, fn)
    sites = [
        'if first["terminal_outcome"]["tag"] != "success":',
        'if steps >= beta["step_bound"]:',
        'steps += 1',
        'second_started = True',
        'emit("charge")',
        'if len(ledger) >= beta["ledger_bound"]:',
        'ledger.append({',
        'emit("append")',
        'if not policy["capability"]:',
        'if policy["obligation"]',
    ]
    positions = [body.find(site) for site in sites]
    if -1 in positions or positions != sorted(positions):
        raise ValueError("second-attempt charge, append or policy order changed")
    loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)]
    if len(loops) != 1:
        raise ValueError("expected one second-stage row traversal")
    expected = "enumerate(retained_joint.terms)" if source else "enumerate(rows)"
    if ast.dump(loops[0].iter) != ast.dump(ast.parse(expected, mode="eval").body):
        raise ValueError("second-stage row order changed")
    loop_body = ast.get_source_segment(code, loops[0])
    for site in ('if steps >= beta["step_bound"]:', 'steps += 1',
                 'emit("charge", index=index)',
                 'if len(ledger) >= beta["ledger_bound"]:',
                 'decision = ', 'ledger.append({', 'emit("append", index=index)'):
        if site not in loop_body:
            raise ValueError("missing second-row control site: " + site)
    predicate = '"BC" in atoms[1].edges' if source else \
        '"BC" in row["atoms"][1]["edges"]'
    if predicate not in loop_body:
        raise ValueError("second-row predicate changed")
    return Program(path, SCHEDULE)


def run(program, first, step_bound, ledger_bound, capability, obligation,
        *, transitions=None):
    """Execute the selected second stage from the independent child claim.

    The input is a canonical first-stage claim with ordered correlated rows.
    Admission, package sizes and the child claim's authenticity are separate
    premises. This function checks only its own budget and policy domain.
    """
    if program.instructions != SCHEDULE:
        raise ValueError("unsupported second-stage schedule")
    if (type(step_bound) is not int or type(ledger_bound) is not int
            or min(step_bound, ledger_bound) < 0 or type(capability) is not bool
            or obligation not in ("resolved", "unresolved")):
        raise ValueError("outside second-stage schedule domain")
    terminal = first["terminal_outcome"]
    ledger = copy.deepcopy(first["ordered_ledger"])
    steps = first["resource_progress"]["completed_steps"]
    first_excluded = None
    second_excluded_prefix = []
    second_started = False

    def progress():
        return {"completed_steps": steps, "completed_ledger_entries": len(ledger),
                "ledger_prefix": copy.deepcopy(ledger),
                "first_excluded": copy.deepcopy(first_excluded),
                "second_excluded_prefix": copy.deepcopy(second_excluded_prefix)}

    def emit(action, index=None):
        if transitions is not None:
            transitions.append({"action": action, "stage": "second",
                                "row_index": index, "steps": steps,
                                "ledger_entries": len(ledger),
                                "second_started": second_started,
                                "event": copy.deepcopy(ledger[-1]) if action == "append" else None})

    def finish(outcome):
        claim = {"terminal_outcome": copy.deepcopy(outcome),
                 "ordered_ledger": copy.deepcopy(ledger), "resource_progress": progress()}
        if transitions is not None:
            transitions.append({"action": "terminal",
                                "stage": "second" if first_excluded is not None else "first",
                                "row_index": None, "steps": steps,
                                "ledger_entries": len(ledger),
                                "second_started": second_started, "event": None,
                                "terminal_outcome": claim["terminal_outcome"],
                                "progress": claim["resource_progress"]})
        return claim, second_started

    def limit():
        return {"tag": "resource_limit", "progress": progress()}

    if terminal["tag"] != "success":
        return finish(limit() if terminal["tag"] == "resource_limit" else terminal)
    first_excluded = copy.deepcopy(terminal["value"]["excluded"])
    retained = terminal["value"]["retained"]
    if steps >= step_bound:
        return finish(limit())
    steps += 1
    second_started = True
    emit("charge")
    if len(ledger) >= ledger_bound:
        return finish(limit())
    ledger.append({"ordinal": len(ledger), "event": "second_restriction_attempt",
                   "effect": SECOND_EFFECTS[0], "predicate_edition": SECOND_PREDICATE})
    emit("append")
    if not capability:
        return finish({"tag": "unsupported", "diagnostic": "second_joint_restriction_unavailable"})
    if obligation == "unresolved":
        return finish({"tag": "undetermined", "diagnostic": "second_joint_predicate_unresolved"})
    kept, excluded = [], []
    for index, row in enumerate(retained):
        if steps >= step_bound:
            return finish(limit())
        steps += 1
        emit("charge", index)
        if len(ledger) >= ledger_bound:
            return finish(limit())
        decision = "second_excluded" if "BC" in row["atoms"][1]["edges"] else "retained"
        ledger.append({"ordinal": len(ledger), "event": "second_joint_row_checked",
                       "effect": SECOND_EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(row), "decision": decision})
        emit("append", index)
        (excluded if decision == "second_excluded" else kept).append(copy.deepcopy(row))
        if decision == "second_excluded":
            second_excluded_prefix.append(copy.deepcopy(row))
    return finish({"tag": "success", "value": {
        "retained": kept, "first_excluded": first_excluded,
        "second_excluded": excluded,
        "predicate_editions": [FIRST_PREDICATE, SECOND_PREDICATE]}})
