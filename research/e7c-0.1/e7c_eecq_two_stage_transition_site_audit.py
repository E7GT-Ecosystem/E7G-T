"""Narrow AST audit of charge/append instrumentation in four selected paths.

This catches an omitted probe at an existing syntactic mutation site. It does
not establish Python interpreter semantics or prove the absence of indirect
mutations, generated code or dynamic monkey-patching.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGETS = (
    ("e7c_eecq_joint_restrict_b1.py", "evaluate", "first"),
    ("e7_ir_eecq_joint_restrict_b1.py", "execute", "first"),
    ("e7c_eecq_two_stage_b1.py", "evaluate", "second"),
    ("e7_ir_eecq_two_stage_b1.py", "execute", "second"),
)


class SiteAuditFailure(ValueError):
    pass


def _call(stmt, name, action):
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == name
            and bool(stmt.value.args) and isinstance(stmt.value.args[0], ast.Constant)
            and stmt.value.args[0].value == action)


def _second_start(stmt):
    return (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == "second_started"
            and isinstance(stmt.value, ast.Constant) and stmt.value.value is True)


def _blocks(node):
    """Visit nested statement lists, including loops and conditions."""
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                         ast.For, ast.While, ast.If, ast.With, ast.Try)):
        for attr in ("body", "orelse", "finalbody"):
            if isinstance(getattr(node, attr, None), list):
                yield getattr(node, attr)
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                yield handler.body


def _is_charge(stmt):
    return (isinstance(stmt, ast.AugAssign)
            and isinstance(stmt.target, ast.Name) and stmt.target.id == "steps")


def _ledger_mutation(stmt):
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and isinstance(stmt.value.func.value, ast.Name)
            and stmt.value.func.value.id == "ledger"
            and stmt.value.func.attr in {"append", "extend", "insert", "pop", "clear"})


def audit_code(code, function, stage):
    tree = ast.parse(code)
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef)
               and node.name == function]
    if len(matches) != 1:
        raise SiteAuditFailure("selected implementation entry point is missing")
    root = matches[0]
    emitters = [node for node in root.body if isinstance(node, ast.FunctionDef)
                and node.name == "emit"]
    if len(emitters) != 1:
        raise SiteAuditFailure("selected entry point needs one transition emitter")
    emitter = emitters[0]
    calls_sink = any(isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name)
                     and node.func.id == "_transition_sink"
                     for node in ast.walk(emitter))
    pinned_stage = any(isinstance(node, ast.Dict) and any(
        isinstance(key, ast.Constant) and key.value == "stage"
        and isinstance(value, ast.Constant) and value.value == stage
        for key, value in zip(node.keys, node.values)) for node in ast.walk(emitter))
    if not calls_sink or not pinned_stage:
        raise SiteAuditFailure("emitter lacks sink or registered stage")

    counts = {"charge": 0, "append": 0}

    def visit(node):
        for block in _blocks(node):
            for index, stmt in enumerate(block):
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue  # helper bodies cannot silently mutate outer counters
                if _is_charge(stmt):
                    if (not isinstance(stmt.op, ast.Add)
                            or not isinstance(stmt.value, ast.Constant)
                            or type(stmt.value.value) is not int or stmt.value.value != 1):
                        raise SiteAuditFailure("step mutation is not a single charge")
                    following = block[index + 1:index + 3]
                    if stage == "second" and block is root.body:
                        if not following or not _second_start(following[0]):
                            raise SiteAuditFailure("second attempt starts after its charge")
                        following = following[1:]
                    if not following or not _call(following[0], "emit", "charge"):
                        raise SiteAuditFailure("charge has no adjacent probe")
                    counts["charge"] += 1
                if _ledger_mutation(stmt):
                    if stmt.value.func.attr != "append":
                        raise SiteAuditFailure("unsupported ledger mutation")
                    following = block[index + 1:index + 2]
                    if not following or not _call(following[0], "emit", "append"):
                        raise SiteAuditFailure("append has no adjacent probe")
                    counts["append"] += 1
                if (isinstance(stmt, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "steps"
                                for target in stmt.targets)
                        and isinstance(stmt.value, ast.BinOp)):
                    raise SiteAuditFailure("step charge bypasses += and its probe")
                visit(stmt)

    visit(root)
    if (sum(_is_charge(node) for node in ast.walk(root)) != counts["charge"]
            or sum(_ledger_mutation(node) for node in ast.walk(root)) != counts["append"]):
        raise SiteAuditFailure("unvisited or hidden transition mutation")
    if any(isinstance(node, ast.Assign)
           and any(isinstance(target, ast.Name) and target.id == "steps"
                   for target in node.targets)
           and isinstance(node.value, ast.BinOp) for node in ast.walk(root)):
        raise SiteAuditFailure("hidden arithmetic step assignment")
    if counts != {"charge": 2, "append": 2}:
        raise SiteAuditFailure("unexpected number of direct transition sites")
    if stage == "second":
        helper_name = "finish" if function == "evaluate" else "result"
        terminal_helpers = [node for node in root.body
                            if isinstance(node, ast.FunctionDef) and node.name == helper_name]
        if len(terminal_helpers) != 1 or not any(
                isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_transition_sink"
                for node in ast.walk(terminal_helpers[0])) or not any(
                isinstance(node, ast.Dict) and any(
                    isinstance(key, ast.Constant) and key.value == "action"
                    and isinstance(value, ast.Constant) and value.value == "terminal"
                    for key, value in zip(node.keys, node.values))
                for node in ast.walk(terminal_helpers[0])):
            raise SiteAuditFailure("outer result lacks terminal transition probe")
        child = "evaluate_first" if function == "evaluate" else "execute_first"
        forwarded = any(isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name) and node.func.id == child
                        and any(keyword.arg == "_transition_sink"
                                and isinstance(keyword.value, ast.Name)
                                and keyword.value.id == "_transition_sink"
                                for keyword in node.keywords)
                        for node in ast.walk(root))
        if not forwarded:
            raise SiteAuditFailure("first-stage child does not receive the sink")
    return counts


def audit_repository():
    return {name: audit_code((ROOT / name).read_text(encoding="utf-8"), function, stage)
            for name, function, stage in TARGETS}
