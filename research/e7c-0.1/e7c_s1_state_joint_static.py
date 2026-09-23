"""Opt-in S1 static successor: nominal finite State and correlated Joint types.

This is a small type-checking fragment, not the accepted B1 grammar, evaluator,
profile semantics or a stable interchange format. Values never enter this API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from e7c_b1_static import Diagnostic, Effect, MAX_INPUT_DEPTH, MAX_INPUT_NODES, TYPE_ARITY, NESTED_TYPE_POSITIONS, DOMAIN_POLICIES

EDITION = "E7C-S1-STATE-JOINT/0.1-provisional"
STRICT_EDITION = "E7C-S1-STATE-JOINT-STRICT/0.1-provisional"
STRICT_EXTENSION = "E7C-S1-FG3-STRICT/0.1-provisional"
MAX_JOINT_ARITY = 8
REGISTERED_MODULES = {
    "E7C-EECQ-FG3-BRIDGE/0.1-provisional": frozenset({"FG3-graph"}),
}


@dataclass(frozen=True)
class S1Type:
    tag: str
    args: tuple[Any, ...]

    def render(self) -> str:
        def atom(value: Any) -> str:
            return value.render() if isinstance(value, S1Type) else json.dumps(value, ensure_ascii=False)
        return f"{self.tag.capitalize()}[{','.join(atom(a) for a in self.args)}]"


def _fail(code: str, message: str, path: str) -> None:
    raise Diagnostic("invalid_input", code, message, path)


def _name(value: Any, path: str) -> str:
    if type(value) is not str or not value:
        _fail("E7C-S1-001", "non-empty nominal name required", path)
    return value


def parse_type(value: Any, path: str = "$.type", depth: int = 0) -> S1Type:
    if depth > MAX_INPUT_DEPTH:
        _fail("E7C-S1-002", "type depth exceeded", path)
    if type(value) is not dict or set(value) != {"tag", "args"}:
        _fail("E7C-S1-001", "type requires exact tag and args", path)
    tag, args = _name(value["tag"], f"{path}.tag"), value["args"]
    if type(args) is not list:
        _fail("E7C-S1-001", "type args must be a list", f"{path}.args")
    if tag == "state":
        if len(args) != 2:
            _fail("E7C-S1-003", "State requires module edition and signature", path)
        parsed = (_name(args[0], f"{path}.args[0]"), _name(args[1], f"{path}.args[1]"))
        if parsed[1] not in REGISTERED_MODULES.get(parsed[0], ()):
            _fail("E7C-S1-004", "unregistered module/signature pair", path)
    elif tag == "joint":
        if not 2 <= len(args) <= MAX_JOINT_ARITY:
            _fail("E7C-S1-003", "Joint requires 2 to 8 State coordinates", path)
        parsed = tuple(parse_type(a, f"{path}.args[{i}]", depth + 1) for i, a in enumerate(args))
        if any(a.tag != "state" for a in parsed):
            _fail("E7C-S1-004", "Joint coordinates must be State types", path)
        if len({a.args[0] for a in parsed}) != 1:
            _fail("E7C-S1-004", "Joint coordinates must use the same module edition", path)
    elif tag in TYPE_ARITY:
        if len(args) != TYPE_ARITY[tag]:
            _fail("E7C-S1-003", "wrong B1 type arity", path)
        nested = set(NESTED_TYPE_POSITIONS.get(tag, ()))
        parsed = tuple(parse_type(a, f"{path}.args[{i}]", depth + 1) if i in nested
                       else _name(a, f"{path}.args[{i}]") for i, a in enumerate(args))
        if tag == "map" and parsed[2] not in DOMAIN_POLICIES:
            _fail("E7C-S1-004", "unknown domain policy", path)
    else:
        _fail("E7C-S1-001", "unknown type constructor", path)
    result = S1Type(tag, parsed)
    if tag == "outcome":
        if _contains_outcome(result.args[0]):
            _fail("E7C-S1-005", "nested Outcome is terminal", path)
    elif any(isinstance(a, S1Type) and _contains_outcome(a) for a in parsed):
        _fail("E7C-S1-005", "Outcome is terminal", path)
    return result


def _contains_outcome(value: S1Type) -> bool:
    return value.tag == "outcome" or any(
        isinstance(a, S1Type) and _contains_outcome(a) for a in value.args)


def check_document(document: Any) -> dict[str, Any]:
    """Check only variables, binary independent product and joint marginal.

    Product is a syntactic capability of this provisional fragment. Runtime
    admission and exact coefficient arithmetic remain a separate gate.
    """
    try:
        nodes = 0
        stack = [(document, 0)]
        while stack:
            item, depth = stack.pop()
            nodes += 1
            if nodes > MAX_INPUT_NODES or depth > MAX_INPUT_DEPTH:
                _fail("E7C-S1-002", "input budget exceeded", "$")
            if type(item) is dict:
                stack.extend((v, depth + 1) for v in item.values())
            elif type(item) is list:
                stack.extend((v, depth + 1) for v in item)
        if type(document) is not dict or set(document) != {"edition", "variables", "term"}:
            _fail("E7C-S1-001", "document requires edition, variables, term", "$")
        if document["edition"] not in (EDITION, STRICT_EDITION):
            _fail("E7C-S1-004", "wrong successor edition", "$.edition")
        variables = document["variables"]
        if type(variables) is not dict:
            _fail("E7C-S1-001", "variables must be an object", "$.variables")
        context = {_name(k, "$.variables"): parse_type(v, f"$.variables.{k}") for k, v in variables.items()}

        def infer(term: Any, path: str, depth: int) -> tuple[S1Type, frozenset[Effect]]:
            if depth > MAX_INPUT_DEPTH or type(term) is not dict or "tag" not in term:
                _fail("E7C-S1-001", "malformed term", path)
            tag = term["tag"]
            if tag == "var" and set(term) == {"tag", "name"}:
                key = _name(term["name"], f"{path}.name")
                if key not in context:
                    raise Diagnostic("type_error", "E7C-S1-T01", "unknown variable", path)
                return context[key], frozenset()
            if tag == "independent" and set(term) == {"tag", "left", "right"}:
                (left, left_effects) = infer(term["left"], f"{path}.left", depth + 1)
                (right, right_effects) = infer(term["right"], f"{path}.right", depth + 1)
                if left.tag != "state" or right.tag != "state" or left.args[0] != right.args[0]:
                    raise Diagnostic("type_error", "E7C-S1-T02", "product requires two States of one module edition", path)
                return S1Type("joint", (left, right)), left_effects | right_effects | {Effect("resources", "finite_joint_product")}
            if tag == "marginal" and set(term) == {"tag", "coordinate", "arg"}:
                source, effects = infer(term["arg"], f"{path}.arg", depth + 1)
                index = term["coordinate"]
                if source.tag != "joint" or type(index) is not int or not 0 <= index < len(source.args):
                    raise Diagnostic("type_error", "E7C-S1-T03", "in-range Joint coordinate required", path)
                return source.args[index], effects | {Effect("resources", "finite_marginal")}
            if tag == "strict_union" and set(term) == {"tag", "arg"} and document["edition"] == STRICT_EDITION:
                source, effects = infer(term["arg"], f"{path}.arg", depth + 1)
                if source.tag != "joint" or len(source.args) != 2 or source.args[0] != source.args[1]:
                    raise Diagnostic("type_error", "E7C-S1-T04", "strict FG3 union requires a binary same-signature Joint", path)
                return (S1Type("outcome", (source.args[0], STRICT_EXTENSION)),
                        effects | {Effect("resources", "finite_strict_union"),
                                   Effect("partiality", STRICT_EXTENSION)})
            _fail("E7C-S1-001", "unknown or malformed term", path)

        result, effects = infer(document["term"], "$.term", 0)
        return {"status": "ok", "type": result.render(), "effects": [
            {"dimension": e.dimension, "payload": e.payload} for e in sorted(effects)]}
    except Diagnostic as exc:
        return {"status": "diagnostic", "diagnostic": exc.as_dict()}
