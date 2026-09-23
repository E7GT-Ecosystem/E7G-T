"""Provisional typed composition of selected WP5 FG3 profile operations.

This is an executable *profile module* prototype. It does not extend the
accepted E7C-B1 syntax, evaluator or proof assistant encoding.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

from eec_q_fg3_b1 import AdmissionError, Rule, State, push
from eec_q_fg3_joint_b1 import Joint
from eec_q_fg3_assembly_b1 import AssemblyState, join_pair, join_wire_choice
from eec_q_fg3_phase_b1 import PhaseState, identify_phase
from eec_q_fg3_fibre_b1 import SourceProjection, project_view, source_return
from eec_q_fg3_quote_b1 import Quote, inside, pack

MODULE_EDITION = "E7C-EECQ-FG3-BRIDGE/0.1-provisional"
CANONICAL_BLOB = "a84da2c4de2ada23577cde4512a10c3369aba2b5"
MODEL_BLOB = "6c624fcd49b95e473a3e80160979183e8d3b58aa"


class BridgeError(ValueError):
    """Closed module typing or admission failure, before execution."""


@dataclass(frozen=True)
class Sort:
    edition: str
    tag: str

    def __post_init__(self) -> None:
        if self.edition != MODULE_EDITION or self.tag not in SORT_CARRIERS:
            raise BridgeError("unknown typed profile sort or edition")


SORT_CARRIERS = MappingProxyType({
    "graph_state": State,
    "untagged_graph_state": State,
    "graph_joint2": Joint,
    "graph_joint3": Joint,
    "assembly_state": AssemblyState,
    "phase_state": PhaseState,
    "source_view": SourceProjection,
    "whole_quote": Quote,
})


def _admits(tag: str, value: Any) -> bool:
    carrier = SORT_CARRIERS[tag]
    if type(value) is not carrier:
        return False
    if tag in ("graph_joint2", "graph_joint3"):
        return value.arity == (2 if tag == "graph_joint2" else 3)
    if tag == "untagged_graph_state":
        return all(graph.tag is None for graph, _ in value.terms)
    return True


@dataclass(frozen=True)
class TypedValue:
    sort: Sort
    payload: Any

    def __post_init__(self) -> None:
        if type(self.sort) is not Sort or not _admits(self.sort.tag, self.payload):
            raise BridgeError("payload does not inhabit declared profile sort")


def admit(tag: str, payload: Any) -> TypedValue:
    return TypedValue(Sort(MODULE_EDITION, tag), payload)


@dataclass(frozen=True, order=True)
class Effect:
    dimension: str
    payload: str


STEP = Effect("resources", "one_module_step")
STRICT = Effect("partiality", "strict_domain")
LOSS = Effect("loss", "exact_graph_identity_by_edge_count")
INQUIRY = Effect("inquiry", "FG3-UNTAGGED-EDGE-COUNT/0.1")


@dataclass(frozen=True)
class Action:
    input_tag: str
    output_tag: str
    domain: str
    effects: tuple[Effect, ...]


ACTIONS = MappingProxyType({
    "add_ab": Action("graph_state", "graph_state", "total", (STEP,)),
    "require_absent_ab": Action("graph_state", "graph_state", "strict", (STEP, STRICT)),
    "join_pair": Action("graph_joint2", "assembly_state", "total", (STEP,)),
    "join_wire_choice": Action("graph_joint3", "assembly_state", "strict", (STEP, STRICT)),
    "identify_phase": Action("untagged_graph_state", "phase_state", "total", (STEP, LOSS)),
    "project_view": Action("untagged_graph_state", "source_view", "total", (STEP, INQUIRY)),
    "source_return": Action("source_view", "untagged_graph_state", "total", (STEP,)),
    "pack": Action("graph_state", "whole_quote", "total", (STEP,)),
    "inside_add_ab": Action("whole_quote", "whole_quote", "total", (STEP,)),
    "inside_require_absent_ab": Action("whole_quote", "whole_quote", "strict", (STEP, STRICT)),
})


@dataclass(frozen=True)
class CheckedAction:
    output: Sort
    static_effects: tuple[Effect, ...]


def check(name: str, operand: Sort) -> CheckedAction:
    """Check type and static effect bound without evaluating a value."""
    if type(name) is not str or name not in ACTIONS or type(operand) is not Sort:
        raise BridgeError("unknown action or malformed profile sort")
    declaration = ACTIONS[name]
    if operand.edition != MODULE_EDITION or operand.tag != declaration.input_tag:
        raise BridgeError("action cannot consume this exact profile sort")
    return CheckedAction(Sort(MODULE_EDITION, declaration.output_tag), declaration.effects)


def _dispatch(name: str, payload: Any) -> tuple[str, Any | None]:
    operations: dict[str, Callable[[Any], Any]] = {
        "add_ab": lambda x: push(Rule("add", "AB"), x),
        "require_absent_ab": lambda x: push(Rule("require_absent", "AB"), x),
        "join_pair": join_pair,
        "join_wire_choice": join_wire_choice,
        "identify_phase": identify_phase,
        "project_view": project_view,
        "source_return": source_return,
        "pack": pack,
        "inside_add_ab": lambda x: inside(Rule("add", "AB"), x),
        "inside_require_absent_ab": lambda x: inside(Rule("require_absent", "AB"), x),
    }
    result = operations[name](payload)
    if name in {"add_ab", "require_absent_ab", "join_pair", "join_wire_choice",
                "inside_add_ab", "inside_require_absent_ab"}:
        return result.tag, result.value
    return "success", result


@dataclass(frozen=True)
class BridgeOutcome:
    action: str
    tag: str
    value: TypedValue | None
    ledger: tuple[Effect, ...]

    def __post_init__(self) -> None:
        if type(self.action) is not str or self.action not in ACTIONS or type(self.ledger) is not tuple:
            raise BridgeError("invalid module result")
        decl = ACTIONS[self.action]
        if any(type(effect) is not Effect or effect not in decl.effects for effect in self.ledger):
            raise BridgeError("incurred effect outside static bound")
        if self.tag == "success":
            if type(self.value) is not TypedValue or self.value.sort.tag != decl.output_tag:
                raise BridgeError("success has wrong result sort")
        elif self.tag == "domain_error":
            if decl.domain != "strict" or self.value is not None:
                raise BridgeError("domain failure must be strict and whole")
        else:
            raise BridgeError("undeclared module outcome")


def execute(name: str, operand: TypedValue) -> BridgeOutcome:
    """Check the whole input before dispatch and retain incurred effects."""
    if type(operand) is not TypedValue:
        raise BridgeError("admitted typed value required")
    checked = check(name, operand.sort)
    try:
        tag, result = _dispatch(name, operand.payload)
    except AdmissionError as exc:
        raise BridgeError("profile admission failed during operation") from exc
    if tag not in {"success", "domain_error"}:
        raise BridgeError("target returned undeclared outcome")
    ledger = (STEP,)
    if tag == "domain_error":
        ledger += (STRICT,)
        return BridgeOutcome(name, tag, None, ledger)
    if name == "identify_phase":
        ledger += (LOSS,)
    elif name == "project_view":
        ledger += (INQUIRY,)
    return BridgeOutcome(name, "success", TypedValue(checked.output, result), ledger)
