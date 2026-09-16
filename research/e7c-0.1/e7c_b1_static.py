"""Bounded E7C-B1/0.1 static-semantics prototype.

This module checks a deliberately small JSON AST.  It does not evaluate terms,
stabilise a public API, or implement any source-profile adapter.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, Mapping


class Diagnostic(Exception):
    def __init__(self, category: str, code: str, message: str, path: str = "$") -> None:
        super().__init__(message)
        self.category = category
        self.code = code
        self.message = message
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True)
class Type:
    tag: str
    args: tuple[Any, ...]

    def render(self) -> str:
        rendered = ",".join(
            a.render() if isinstance(a, Type) else json.dumps(a, ensure_ascii=False)
            for a in self.args
        )
        return f"{self.tag.capitalize()}[{rendered}]"


@dataclass(frozen=True, order=True)
class Effect:
    dimension: str
    payload: str


@dataclass(frozen=True)
class StaticResult:
    type: Type
    effects: tuple[Effect, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.render(),
            "effects": [
                {"dimension": effect.dimension, "payload": effect.payload}
                for effect in self.effects
            ],
        }


TYPE_ARITY = {
    "base": 1,
    "entity": 1,
    "config": 1,
    "map": 4,
    "view": 4,
    "projection": 5,
    "family": 2,
    "fibre": 2,
    "partition": 2,
    "outcome": 2,
}

NESTED_TYPE_POSITIONS = {
    "map": (0, 1),
    "view": (0, 1),
    "projection": (0, 1),
    "family": (1,),
    "fibre": (0,),
    "partition": (0,),
    "outcome": (0,),
}

EFFECT_DIMENSIONS = {
    "partiality",
    "loss",
    "inquiry",
    "access",
    "authority",
    "alternatives",
    "evidence",
    "history",
    "resources",
    "bridge",
}

DOMAIN_POLICIES = {"total", "strict", "filtering"}
VIEW_KINDS = {"source_preserving", "projection"}
MAX_INPUT_DEPTH = 64
MAX_INPUT_NODES = 10_000


def _canonical_payload(value: Any) -> str:
    """Encode structured effect payloads without delimiter collisions."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Diagnostic("invalid_input", "E7C-S001", "expected object", path)
    return value


def _exact_keys(value: Mapping[str, Any], required: set[str], path: str) -> None:
    actual = set(value)
    if actual != required:
        missing = sorted(required - actual)
        extra = sorted(actual - required)
        raise Diagnostic(
            "invalid_input",
            "E7C-S002",
            f"field mismatch; missing={missing}, extra={extra}",
            path,
        )


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise Diagnostic("invalid_input", "E7C-S003", "expected non-empty string", path)
    return value


def parse_type(value: Any, path: str = "$.type", _depth: int = 0) -> Type:
    if _depth > MAX_INPUT_DEPTH:
        raise Diagnostic("invalid_input", "E7C-S012", "type depth limit exceeded", path)
    obj = _object(value, path)
    _exact_keys(obj, {"tag", "args"}, path)
    tag = _text(obj["tag"], f"{path}.tag")
    if tag not in TYPE_ARITY:
        raise Diagnostic("invalid_input", "E7C-S004", f"unknown type tag {tag!r}", path)
    args = obj["args"]
    if not isinstance(args, list) or len(args) != TYPE_ARITY[tag]:
        raise Diagnostic(
            "invalid_input",
            "E7C-S005",
            f"type {tag!r} requires {TYPE_ARITY[tag]} arguments",
            f"{path}.args",
        )
    nested = set(NESTED_TYPE_POSITIONS.get(tag, ()))
    parsed: list[Any] = []
    for index, arg in enumerate(args):
        arg_path = f"{path}.args[{index}]"
        parsed.append(
            parse_type(arg, arg_path, _depth + 1) if index in nested else _text(arg, arg_path)
        )
    if tag == "map" and parsed[2] not in DOMAIN_POLICIES:
        raise Diagnostic(
            "invalid_input",
            "E7C-S010",
            f"unknown domain policy {parsed[2]!r}",
            f"{path}.args[2]",
        )
    return Type(tag, tuple(parsed))


def type_json(value: Type) -> dict[str, Any]:
    return {
        "tag": value.tag,
        "args": [type_json(arg) if isinstance(arg, Type) else arg for arg in value.args],
    }


def _effects(*effects: Effect) -> tuple[Effect, ...]:
    for effect in effects:
        if effect.dimension not in EFFECT_DIMENSIONS:
            raise AssertionError(f"undeclared effect dimension: {effect.dimension}")
    return tuple(sorted(set(effects)))


class Checker:
    REQUIRED_ENV_SECTIONS = {
        "variables",
        "maps",
        "views",
        "restrictions",
        "reconstructions",
        "criteria",
    }

    def __init__(self, environment: Any) -> None:
        env = _object(environment, "$.environment")
        _exact_keys(env, self.REQUIRED_ENV_SECTIONS, "$.environment")
        self.variables = self._type_table(env["variables"], "variables")
        self.maps = self._declaration_table(env["maps"], "maps")
        self.views = self._declaration_table(env["views"], "views")
        self.restrictions = self._declaration_table(env["restrictions"], "restrictions")
        self.reconstructions = self._declaration_table(env["reconstructions"], "reconstructions")
        self.criteria = self._declaration_table(env["criteria"], "criteria")
        self._validate_environment()

    def _validate_environment(self) -> None:
        schemas = {
            "maps": (
                self.maps,
                {
                    "source",
                    "target",
                    "domain_policy",
                    "map_edition",
                    "failure_family",
                    "outcome_extension",
                },
                {"source", "target"},
                {"domain_policy", "map_edition", "failure_family", "outcome_extension"},
            ),
            "views": (
                self.views,
                {
                    "kind",
                    "source",
                    "target",
                    "inquiry",
                    "preserved_observations",
                    "excluded_observations",
                    "quotient_relation",
                    "reconstruction_obligation",
                },
                {"source", "target"},
                {"kind", "inquiry", "quotient_relation", "reconstruction_obligation"},
            ),
            "restrictions": (
                self.restrictions,
                {"input_index", "output_index", "element", "outcome_extension"},
                {"element"},
                {"input_index", "output_index", "outcome_extension"},
            ),
            "reconstructions": (
                self.reconstructions,
                {
                    "source",
                    "view_type",
                    "inquiry",
                    "view_policy",
                    "required_obligation",
                    "resource_policies",
                    "outcome_extension",
                },
                {"source", "view_type"},
                {"inquiry", "view_policy", "required_obligation", "outcome_extension"},
            ),
            "criteria": (
                self.criteria,
                {"source", "outcome_extension"},
                {"source"},
                {"outcome_extension"},
            ),
        }
        for section, (table, fields, type_fields, text_fields) in schemas.items():
            for name, declaration in table.items():
                path = f"$.environment.{section}.{name}"
                _exact_keys(declaration, fields, path)
                for field in type_fields:
                    parse_type(declaration[field], f"{path}.{field}")
                for field in text_fields:
                    _text(declaration[field], f"{path}.{field}")
        for name, declaration in self.maps.items():
            policy = declaration["domain_policy"]
            if policy not in DOMAIN_POLICIES:
                raise Diagnostic(
                    "invalid_input",
                    "E7C-S010",
                    f"unknown domain policy {policy!r}",
                    f"$.environment.maps.{name}.domain_policy",
                )
        for name, declaration in self.views.items():
            path = f"$.environment.views.{name}"
            kind = declaration["kind"]
            if kind not in VIEW_KINDS:
                raise Diagnostic("invalid_input", "E7C-S011", f"unknown view kind {kind!r}", f"{path}.kind")
            for field in ("preserved_observations", "excluded_observations"):
                values = declaration[field]
                if not isinstance(values, list) or any(
                    not isinstance(item, str) or not item for item in values
                ):
                    raise Diagnostic("invalid_input", "E7C-S008", f"{field} must be a string list", f"{path}.{field}")
            preserved = set(declaration["preserved_observations"])
            excluded = set(declaration["excluded_observations"])
            if preserved & excluded:
                raise Diagnostic("invalid_input", "E7C-S011", "preserved and excluded observations overlap", path)
            if kind == "source_preserving" and (
                excluded
                or declaration["quotient_relation"] != "identity"
                or declaration["reconstruction_obligation"] != "exact_source_return"
            ):
                raise Diagnostic("invalid_input", "E7C-S011", "invalid source-preserving view contract", path)
            if kind == "projection" and (
                not excluded
                or declaration["quotient_relation"] == "identity"
                or declaration["reconstruction_obligation"] == "exact_source_return"
            ):
                raise Diagnostic("invalid_input", "E7C-S011", "projection requires explicit loss and quotient", path)
        for name, declaration in self.reconstructions.items():
            path = f"$.environment.reconstructions.{name}"
            values = declaration["resource_policies"]
            if not isinstance(values, list) or any(
                not isinstance(item, str) or not item for item in values
            ):
                raise Diagnostic("invalid_input", "E7C-S009", "resource_policies must be a string list", f"{path}.resource_policies")
            view_name = declaration["view_policy"]
            if view_name not in self.views:
                raise Diagnostic("invalid_input", "E7C-S011", f"unknown view policy {view_name!r}", f"{path}.view_policy")
            view = self.views[view_name]
            expected_contract = (
                view["kind"] == "source_preserving"
                and view["reconstruction_obligation"] == declaration["required_obligation"]
                and parse_type(view["source"]) == parse_type(declaration["source"])
                and parse_type(view["target"]) == parse_type(declaration["view_type"])
                and view["inquiry"] == declaration["inquiry"]
            )
            if not expected_contract:
                raise Diagnostic("invalid_input", "E7C-S011", "reconstruction/view contract mismatch", path)

    @staticmethod
    def _type_table(value: Any, section: str) -> dict[str, Type]:
        obj = _object(value, f"$.environment.{section}")
        return {
            _text(name, f"$.environment.{section}.<key>"): parse_type(
                declaration, f"$.environment.{section}.{name}"
            )
            for name, declaration in obj.items()
        }

    @staticmethod
    def _declaration_table(value: Any, section: str) -> dict[str, Mapping[str, Any]]:
        obj = _object(value, f"$.environment.{section}")
        return {
            _text(name, f"$.environment.{section}.<key>"): copy.deepcopy(
                _object(declaration, f"$.environment.{section}.{name}")
            )
            for name, declaration in obj.items()
        }

    @staticmethod
    def _lookup(table: Mapping[str, Any], name: Any, kind: str, path: str) -> Any:
        key = _text(name, path)
        if key not in table:
            raise Diagnostic("type_error", "E7C-T001", f"unknown {kind} {key!r}", path)
        return table[key]

    @staticmethod
    def _expect(actual: Type, expected: Type, path: str) -> None:
        if actual != expected:
            raise Diagnostic(
                "type_error",
                "E7C-T002",
                f"expected {expected.render()}, found {actual.render()}",
                path,
            )

    @staticmethod
    def _decl_type(decl: Mapping[str, Any], field: str, path: str) -> Type:
        if field not in decl:
            raise Diagnostic("invalid_input", "E7C-S006", f"missing field {field!r}", path)
        return parse_type(decl[field], f"{path}.{field}")

    @staticmethod
    def _decl_text(decl: Mapping[str, Any], field: str, path: str) -> str:
        if field not in decl:
            raise Diagnostic("invalid_input", "E7C-S006", f"missing field {field!r}", path)
        return _text(decl[field], f"{path}.{field}")

    def check(self, term: Any, path: str = "$.term", _depth: int = 0) -> StaticResult:
        if _depth > MAX_INPUT_DEPTH:
            raise Diagnostic("invalid_input", "E7C-S012", "term depth limit exceeded", path)
        obj = _object(term, path)
        tag = _text(obj.get("tag"), f"{path}.tag")
        method = getattr(self, f"_check_{tag}", None)
        if method is None:
            raise Diagnostic("invalid_input", "E7C-S007", f"unknown term tag {tag!r}", path)
        return method(obj, path, _depth)

    def _check_var(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "name"}, path)
        value_type = self._lookup(self.variables, term["name"], "variable", f"{path}.name")
        return StaticResult(value_type, ())

    def _check_apply(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "declaration", "arg"}, path)
        name = _text(term["declaration"], f"{path}.declaration")
        decl = self._lookup(self.maps, name, "map declaration", f"{path}.declaration")
        source = self._decl_type(decl, "source", f"$.environment.maps.{name}")
        target = self._decl_type(decl, "target", f"$.environment.maps.{name}")
        policy = self._decl_text(decl, "domain_policy", f"$.environment.maps.{name}")
        edition = self._decl_text(decl, "map_edition", f"$.environment.maps.{name}")
        failure_family = self._decl_text(decl, "failure_family", f"$.environment.maps.{name}")
        extension = self._decl_text(decl, "outcome_extension", f"$.environment.maps.{name}")
        arg = self.check(term["arg"], f"{path}.arg", _depth + 1)
        self._expect(arg.type, source, f"{path}.arg")
        map_evidence = _canonical_payload(
            {
                "domain_policy": policy,
                "failure_family": failure_family,
                "map_declaration": name,
                "map_edition": edition,
                "outcome_extension": extension,
            }
        )
        added = () if policy == "total" else (
            Effect(
                "partiality",
                _canonical_payload(
                    {
                        "domain_policy": policy,
                        "failure_family": failure_family,
                        "map_declaration": name,
                        "map_edition": edition,
                    }
                ),
            ),
        )
        return StaticResult(
            Type("outcome", (target, extension)),
            _effects(*arg.effects, Effect("evidence", map_evidence), *added),
        )

    def _check_view(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "declaration", "arg"}, path)
        name = _text(term["declaration"], f"{path}.declaration")
        decl = self._lookup(self.views, name, "view policy", f"{path}.declaration")
        source = self._decl_type(decl, "source", f"$.environment.views.{name}")
        target = self._decl_type(decl, "target", f"$.environment.views.{name}")
        kind = self._decl_text(decl, "kind", f"$.environment.views.{name}")
        inquiry = self._decl_text(decl, "inquiry", f"$.environment.views.{name}")
        preserved = decl["preserved_observations"]
        excluded = decl["excluded_observations"]
        quotient = self._decl_text(decl, "quotient_relation", f"$.environment.views.{name}")
        obligation = self._decl_text(decl, "reconstruction_obligation", f"$.environment.views.{name}")
        arg = self.check(term["arg"], f"{path}.arg", _depth + 1)
        self._expect(arg.type, source, f"{path}.arg")
        added = [Effect("inquiry", inquiry)]
        if kind == "projection":
            added.append(
                Effect(
                    "loss",
                    _canonical_payload(
                        {
                            "excluded": sorted(set(excluded)),
                            "preserved": sorted(set(preserved)),
                            "quotient_relation": quotient,
                        }
                    ),
                )
            )
            result = Type("projection", (source, target, inquiry, quotient, name))
        else:
            result = Type("view", (source, target, inquiry, name))
        added.append(Effect("alternatives", obligation))
        return StaticResult(result, _effects(*arg.effects, *added))

    def _check_restrict(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "declaration", "arg"}, path)
        name = _text(term["declaration"], f"{path}.declaration")
        decl = self._lookup(self.restrictions, name, "restriction policy", f"{path}.declaration")
        input_index = self._decl_text(decl, "input_index", f"$.environment.restrictions.{name}")
        output_index = self._decl_text(decl, "output_index", f"$.environment.restrictions.{name}")
        element = self._decl_type(decl, "element", f"$.environment.restrictions.{name}")
        extension = self._decl_text(decl, "outcome_extension", f"$.environment.restrictions.{name}")
        arg = self.check(term["arg"], f"{path}.arg", _depth + 1)
        self._expect(arg.type, Type("family", (input_index, element)), f"{path}.arg")
        result = Type("family", (output_index, element))
        return StaticResult(
            Type("outcome", (result, extension)),
            _effects(*arg.effects, Effect("alternatives", name)),
        )

    def _check_reconstruct(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "declaration", "resource_policy", "arg"}, path)
        name = _text(term["declaration"], f"{path}.declaration")
        resource = _text(term["resource_policy"], f"{path}.resource_policy")
        decl = self._lookup(self.reconstructions, name, "reconstruction policy", f"{path}.declaration")
        source = self._decl_type(decl, "source", f"$.environment.reconstructions.{name}")
        view_type = self._decl_type(decl, "view_type", f"$.environment.reconstructions.{name}")
        inquiry = self._decl_text(decl, "inquiry", f"$.environment.reconstructions.{name}")
        view_policy = self._decl_text(decl, "view_policy", f"$.environment.reconstructions.{name}")
        extension = self._decl_text(decl, "outcome_extension", f"$.environment.reconstructions.{name}")
        allowed = decl.get("resource_policies")
        if not isinstance(allowed, list) or any(not isinstance(item, str) or not item for item in allowed):
            raise Diagnostic("invalid_input", "E7C-S009", "resource_policies must be a string list", f"$.environment.reconstructions.{name}.resource_policies")
        if resource not in allowed:
            raise Diagnostic("type_error", "E7C-T003", f"resource policy {resource!r} is not admitted", f"{path}.resource_policy")
        expected = Type("view", (source, view_type, inquiry, view_policy))
        arg = self.check(term["arg"], f"{path}.arg", _depth + 1)
        self._expect(arg.type, expected, f"{path}.arg")
        result = Type("fibre", (source, name))
        return StaticResult(
            Type("outcome", (result, extension)),
            _effects(*arg.effects, Effect("resources", resource), Effect("alternatives", name)),
        )

    def _check_classify(self, term: Mapping[str, Any], path: str, _depth: int) -> StaticResult:
        _exact_keys(term, {"tag", "declaration", "arg"}, path)
        name = _text(term["declaration"], f"{path}.declaration")
        decl = self._lookup(self.criteria, name, "criterion", f"{path}.declaration")
        source = self._decl_type(decl, "source", f"$.environment.criteria.{name}")
        extension = self._decl_text(decl, "outcome_extension", f"$.environment.criteria.{name}")
        arg = self.check(term["arg"], f"{path}.arg", _depth + 1)
        self._expect(arg.type, source, f"{path}.arg")
        result = Type("partition", (source, name))
        return StaticResult(
            Type("outcome", (result, extension)),
            _effects(*arg.effects, Effect("inquiry", name)),
        )


def _check_input_budget(document: Any) -> None:
    stack = [(document, 0)]
    nodes = 0
    while stack:
        value, depth = stack.pop()
        nodes += 1
        if nodes > MAX_INPUT_NODES:
            raise Diagnostic("invalid_input", "E7C-S012", "input node limit exceeded", "$")
        if depth > MAX_INPUT_DEPTH:
            raise Diagnostic("invalid_input", "E7C-S012", "input depth limit exceeded", "$")
        if isinstance(value, Mapping):
            stack.extend((child, depth + 1) for child in value.values())
        elif isinstance(value, list):
            stack.extend((child, depth + 1) for child in value)


def check_document(document: Any) -> dict[str, Any]:
    try:
        _check_input_budget(document)
        obj = _object(document, "$")
        _exact_keys(obj, {"environment", "term"}, "$")
        return {"status": "ok", "result": Checker(obj["environment"]).check(obj["term"]).as_dict()}
    except Diagnostic as diagnostic:
        return {"status": "diagnostic", "diagnostic": diagnostic.as_dict()}
