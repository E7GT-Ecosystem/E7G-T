"""Selected /0.5→/0.6 code sites, not a Python semantics proof.

The check records the exact child lowering and separate serialization order,
and the second attempt's charge, started bit, ledger guard, then append. It
requires the full entry-point AST fingerprint from the existing code pin.
"""

import ast
from pathlib import Path

from e7c_joint_control_flow_pin import check_repository

ROOT = Path(__file__).resolve().parent


def function(name, entry):
    source = (ROOT / name).read_text()
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name == entry]
    if len(nodes) != 1:
        raise ValueError("entry-point shape changed")
    return nodes[0]


def size_constant(name):
    module = ast.parse((ROOT / name).read_text())
    matches = [node.value.value for node in module.body
               if isinstance(node, ast.Assign)
               and [target.id for target in node.targets if isinstance(target, ast.Name)]
               == ["MAX_BYTES"] and isinstance(node.value, ast.Constant)]
    if matches != [1_000_000]:
        raise ValueError("IR package-size constant changed: " + name)
    return matches[0]


def require_order(haystack, needles):
    at = 0
    for needle in needles:
        found = haystack.find(needle, at)
        if found < 0:
            raise ValueError("selected operation missing or reordered: " + needle)
        at = found + len(needle)


def check_sites():
    check_repository()
    child_limit = size_constant("e7_ir_eecq_joint_restrict_b1.py")
    outer_limit = size_constant("e7_ir_eecq_two_stage_b1.py")
    child_lower = function("e7_ir_eecq_joint_restrict_b1.py", "lower")
    outer_lower = function("e7_ir_eecq_two_stage_b1.py", "lower")
    child_serialize = function("e7_ir_eecq_joint_restrict_b1.py", "serialize")
    outer_serialize = function("e7_ir_eecq_two_stage_b1.py", "serialize")
    executor = function("e7_ir_eecq_two_stage_b1.py", "execute")
    require_order(ast.unparse(child_lower), (
        "admit(source)", "result = evaluate(source)",
        "package['id'] = digest(package)", "return parse(serialize(package))"))
    require_order(ast.unparse(outer_lower), (
        "admit(source)", "first_ir = lower_first(source['first'])",
        "witness = evaluate(source)['witness']", "package['id'] = digest(package)",
        "return parse(serialize(package))"))
    for node in (child_serialize, outer_serialize):
        require_order(ast.unparse(node), (
            "encoded = canonical_bytes(package)", "if len(encoded) > MAX_BYTES:",
            "raise ", "return encoded"))
    require_order(ast.unparse(executor), (
        "first = execute_first(checked['first_ir']",
        "if first['terminal_outcome']['tag'] != 'success':",
        "if steps >= beta['step_bound']:", "steps += 1", "second_started = True",
        "emit('charge')", "if len(ledger) >= beta['ledger_bound']:",
        "ledger.append({'ordinal': len(ledger), 'event': 'second_restriction_attempt'",
        "emit('append')"))
    return {"child_ir_edition": "E7-IR/0.5-EECQ-JOINT-RESTRICT-provisional",
            "outer_ir_edition": "E7-IR/0.6-EECQ-JOINT-TWO-STAGE-provisional",
            "nested_byte_limit": child_limit, "outer_byte_limit": outer_limit}
