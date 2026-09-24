"""Closed data admission for the disposable E7C-B1 WP3-I package.

Evaluator and replay checker share these data-shape and carrier checks only.
No evaluation order, resource accounting or semantic control flow lives here.
"""

from __future__ import annotations

from typing import Any, Mapping

from e7c_b1_canonical import INTERPRETATION_EDITION, canonical_key


class AdmissionError(ValueError):
    def __init__(self, diagnostic: str, detail: str) -> None:
        super().__init__(detail)
        self.diagnostic = diagnostic
        self.detail = detail


ATOMIC_TAGS = {"base", "config", "entity"}
SEQUENCE_TAGS = {"family", "fibre", "partition"}


def _exact_object(value: Any, fields: set[str], path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdmissionError("runtime_input_mismatch", f"{path} must be an object")
    if set(value) != fields:
        raise AdmissionError("runtime_input_mismatch", f"{path} has non-canonical fields")
    return value


def _canonical_unique(values: Any, path: str) -> list[Any]:
    if not isinstance(values, list):
        raise AdmissionError("runtime_input_mismatch", f"{path} must be a finite list")
    keys = [canonical_key(value) for value in values]
    if len(keys) != len(set(keys)):
        raise AdmissionError("runtime_input_mismatch", f"{path} contains duplicates")
    if keys != sorted(keys):
        raise AdmissionError("runtime_input_mismatch", f"{path} is not canonically ordered")
    return values


def _type_key(type_json: Mapping[str, Any]) -> str:
    return canonical_key(type_json)


def _collect_atomic_types(type_json: Mapping[str, Any], found: dict[str, Mapping[str, Any]]) -> None:
    if type_json["tag"] in ATOMIC_TAGS:
        found[_type_key(type_json)] = type_json
    for argument in type_json["args"]:
        if isinstance(argument, Mapping):
            _collect_atomic_types(argument, found)


def _required_atomic_types(environment: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    found: dict[str, Mapping[str, Any]] = {}
    for type_json in environment["variables"].values():
        _collect_atomic_types(type_json, found)
    typed_fields = {
        "maps": ("source", "target"),
        "views": ("source", "target"),
        "restrictions": ("element",),
        "reconstructions": ("source", "view_type"),
        "criteria": ("source",),
    }
    for section, fields in typed_fields.items():
        for declaration in environment[section].values():
            for field in fields:
                _collect_atomic_types(declaration[field], found)
    return found


def _carrier(carriers: Mapping[str, Any], type_json: Mapping[str, Any], path: str) -> list[Any]:
    key = _type_key(type_json)
    if key not in carriers:
        raise AdmissionError("missing_replay_material", f"missing carrier for {path}")
    return carriers[key]


def _member(value: Any, carrier: list[Any], path: str) -> None:
    if canonical_key(value) not in {canonical_key(item) for item in carrier}:
        raise AdmissionError("runtime_input_mismatch", f"{path} is outside its declared carrier")


def _validate_terminal(value: Any, success_type: Mapping[str, Any], carriers: Mapping[str, Any], path: str) -> None:
    if not isinstance(value, Mapping) or "tag" not in value:
        raise AdmissionError("runtime_input_mismatch", f"{path} is not a terminal outcome")
    shapes = {
        "success": {"tag", "value", "optional_witness"},
        "domain_error": {"tag", "diagnostic"},
        "unsupported": {"tag", "capability"},
        "undetermined": {"tag", "obligation"},
        "resource_limit": {"tag", "bound", "progress"},
    }
    expected = shapes.get(value["tag"])
    if expected is None or set(value) != expected:
        raise AdmissionError("runtime_input_mismatch", f"{path} has an invalid outcome shape")
    if value["tag"] == "success":
        if value["optional_witness"] is not None:
            raise AdmissionError("identity_mismatch", f"{path} imports a witness binding")
        _validate_value(value["value"], success_type, carriers, f"{path}.value")


def _validate_value(value: Any, type_json: Mapping[str, Any], carriers: Mapping[str, Any], path: str) -> None:
    tag = type_json["tag"]
    args = type_json["args"]
    if tag in ATOMIC_TAGS:
        _member(value, _carrier(carriers, type_json, path), path)
        return
    if tag == "family":
        if not isinstance(value, list):
            raise AdmissionError("runtime_input_mismatch", f"{path} must be a family list")
        for index, item in enumerate(value):
            _validate_value(item, args[1], carriers, f"{path}[{index}]")
        return
    if tag == "fibre":
        if not isinstance(value, list):
            raise AdmissionError("runtime_input_mismatch", f"{path} must be a fibre list")
        for index, item in enumerate(value):
            _validate_value(item, args[0], carriers, f"{path}[{index}]")
        return
    if tag == "partition":
        if not isinstance(value, list):
            raise AdmissionError("runtime_input_mismatch", f"{path} must be a partition list")
        return
    if tag in {"view", "projection"}:
        record = _exact_object(
            value,
            {"kind", "declaration", "representation", "source_return_token"},
            path,
        )
        expected_kind = "source_preserving" if tag == "view" else "projection"
        policy_index = 3 if tag == "view" else 4
        if record["kind"] != expected_kind or record["declaration"] != args[policy_index]:
            raise AdmissionError("runtime_input_mismatch", f"{path} has the wrong nominal view policy")
        _validate_value(record["representation"], args[1], carriers, f"{path}.representation")
        if tag == "view":
            if record["source_return_token"] is None:
                raise AdmissionError("runtime_input_mismatch", f"{path} lacks a source-return token")
            _validate_value(record["source_return_token"], args[0], carriers, f"{path}.source_return_token")
        elif record["source_return_token"] is not None:
            raise AdmissionError("runtime_input_mismatch", f"{path} projection retains a source token")
        return
    if tag == "outcome":
        _validate_terminal(value, args[0], carriers, path)
        return
    raise AdmissionError("runtime_input_mismatch", f"{path} uses unsupported runtime type {tag}")


def _validate_guard(record: Mapping[str, Any], path: str) -> None:
    if not isinstance(record["capability"], bool):
        raise AdmissionError("runtime_input_mismatch", f"{path}.capability must be Boolean")
    if record["obligation"] not in {"resolved", "unresolved"}:
        raise AdmissionError("runtime_input_mismatch", f"{path}.obligation is invalid")


def _validate_cases(cases: Any, path: str) -> list[Mapping[str, Any]]:
    if not isinstance(cases, list):
        raise AdmissionError("missing_replay_material", f"{path} is missing")
    records: list[Mapping[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping) or "input" not in case:
            raise AdmissionError("runtime_input_mismatch", f"{path}[{index}] is malformed")
        records.append(case)
    keys = [canonical_key(case["input"]) for case in records]
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise AdmissionError("runtime_input_mismatch", f"{path} is not a canonical function table")
    return records


def _validate_interpretation(environment: Mapping[str, Any], interpretation: Any) -> Mapping[str, Any]:
    package = _exact_object(
        interpretation,
        {"interpretation_edition", "carriers", "maps", "views", "restrictions", "reconstructions", "criteria"},
        "interpretation",
    )
    if package["interpretation_edition"] != INTERPRETATION_EDITION:
        raise AdmissionError("edition_mismatch", "unknown interpretation edition")
    carriers = package["carriers"]
    if not isinstance(carriers, Mapping):
        raise AdmissionError("missing_replay_material", "carrier table")
    required_types = _required_atomic_types(environment)
    if set(carriers) != set(required_types):
        raise AdmissionError("missing_replay_material", "carrier table does not exactly cover declared atomic types")
    for key in sorted(carriers):
        _canonical_unique(carriers[key], f"interpretation.carriers[{key}]")

    schemas = {
        "maps": {"capability", "obligation", "cases"},
        "views": {"capability", "obligation", "cases"},
        "restrictions": {"capability", "obligation", "retained_keys"},
        "reconstructions": {
            "capability", "obligation", "carrier_finite", "equality_resolved",
            "constraint_resolved", "carrier",
        },
        "criteria": {"capability", "obligation", "cases"},
    }
    for section, fields in schemas.items():
        table = package[section]
        if not isinstance(table, Mapping) or set(table) != set(environment[section]):
            raise AdmissionError("missing_replay_material", f"interpretation.{section} coverage")
        for name, raw_record in table.items():
            record = _exact_object(raw_record, fields, f"interpretation.{section}.{name}")
            _validate_guard(record, f"interpretation.{section}.{name}")

    for name, declaration in environment["maps"].items():
        record = package["maps"][name]
        cases = _validate_cases(record["cases"], f"interpretation.maps.{name}.cases")
        source_carrier = _carrier(carriers, declaration["source"], f"map {name} source")
        target_carrier = _carrier(carriers, declaration["target"], f"map {name} target")
        if [canonical_key(case["input"]) for case in cases] != [canonical_key(value) for value in source_carrier]:
            raise AdmissionError("missing_replay_material", f"map {name} lacks source-carrier coverage")
        policy = declaration["domain_policy"]
        for index, case in enumerate(cases):
            allowed = {"input", "in_domain", "output"}
            if policy == "filtering":
                allowed |= {"retained", "excluded"}
            if not set(case) <= allowed or not isinstance(case.get("in_domain"), bool):
                raise AdmissionError("runtime_input_mismatch", f"map {name} case {index} shape")
            _validate_value(case["input"], declaration["source"], carriers, f"map {name} input")
            if policy == "total" and (not case["in_domain"] or "output" not in case):
                raise AdmissionError("missing_replay_material", f"total map {name} target")
            if case["in_domain"] and "output" not in case:
                raise AdmissionError("missing_replay_material", f"map {name} target")
            if "output" in case:
                _validate_value(case["output"], declaration["target"], carriers, f"map {name} output")
            if policy == "filtering":
                if not isinstance(case.get("retained"), list) or not isinstance(case.get("excluded"), list):
                    raise AdmissionError("missing_replay_material", f"filtering alternatives for {name}")
                for field in ("retained", "excluded"):
                    for item in case[field]:
                        _validate_value(item, declaration["source"], carriers, f"map {name} {field}")

    for name, declaration in environment["views"].items():
        record = package["views"][name]
        cases = _validate_cases(record["cases"], f"interpretation.views.{name}.cases")
        source_carrier = _carrier(carriers, declaration["source"], f"view {name} source")
        if [canonical_key(case["input"]) for case in cases] != [canonical_key(value) for value in source_carrier]:
            raise AdmissionError("missing_replay_material", f"view {name} lacks source-carrier coverage")
        for case in cases:
            if set(case) != {"input", "output"}:
                raise AdmissionError("runtime_input_mismatch", f"view {name} case shape")
            _validate_value(case["input"], declaration["source"], carriers, f"view {name} input")
            _validate_value(case["output"], declaration["target"], carriers, f"view {name} output")

    for name, declaration in environment["restrictions"].items():
        record = package["restrictions"][name]
        retained = record["retained_keys"]
        if not isinstance(retained, list) or retained != sorted(set(retained)):
            raise AdmissionError("runtime_input_mismatch", f"restriction {name} retained keys")
        allowed = {canonical_key(value) for value in _carrier(carriers, declaration["element"], f"restriction {name}")}
        if not set(retained) <= allowed:
            raise AdmissionError("runtime_input_mismatch", f"restriction {name} key outside carrier")

    for name, declaration in environment["reconstructions"].items():
        record = package["reconstructions"][name]
        for field in ("carrier_finite", "equality_resolved", "constraint_resolved"):
            if not isinstance(record[field], bool):
                raise AdmissionError("runtime_input_mismatch", f"reconstruction {name} {field}")
        carrier = _canonical_unique(record["carrier"], f"reconstruction {name} carrier")
        source_carrier = _carrier(carriers, declaration["source"], f"reconstruction {name} source")
        if [canonical_key(value) for value in carrier] != [canonical_key(value) for value in source_carrier]:
            raise AdmissionError("missing_replay_material", f"reconstruction {name} carrier coverage")

    for name, declaration in environment["criteria"].items():
        record = package["criteria"][name]
        cases = _validate_cases(record["cases"], f"interpretation.criteria.{name}.cases")
        source_type = declaration["source"]
        element_type = source_type["args"][0] if source_type["tag"] == "fibre" else source_type
        source_carrier = _carrier(carriers, element_type, f"criterion {name} source")
        if [canonical_key(case["input"]) for case in cases] != [canonical_key(value) for value in source_carrier]:
            raise AdmissionError("missing_replay_material", f"criterion {name} lacks source-carrier coverage")
        for case in cases:
            if set(case) != {"input", "output"}:
                raise AdmissionError("runtime_input_mismatch", f"criterion {name} case shape")
            _validate_value(case["input"], element_type, carriers, f"criterion {name} input")
    return package


def validate_runtime_package(
    environment: Mapping[str, Any], values: Any, interpretation: Any
) -> None:
    package = _validate_interpretation(environment, interpretation)
    if not isinstance(values, Mapping) or set(values) != set(environment["variables"]):
        raise AdmissionError("missing_replay_material", "value environment coverage")
    for name, type_json in environment["variables"].items():
        _validate_value(values[name], type_json, package["carriers"], f"values.{name}")


def validate_typed_binding(value: Any, type_json: Mapping[str, Any],
                           carriers: Any) -> None:
    """Admit one closed binding against precisely its edition-bound atomic carriers.

    Reuses the WP3-I value/terminal admission rules; no evaluation control flow.
    The caller separately pins the interpretation edition and source identity.
    """
    if type(carriers) is not dict:
        raise AdmissionError("missing_replay_material", "typed binding carriers missing")
    required: dict[str, Mapping[str, Any]] = {}
    _collect_atomic_types(type_json, required)
    if set(carriers) != set(required):
        raise AdmissionError("missing_replay_material", "typed binding carrier coverage")
    for key in sorted(required):
        _canonical_unique(carriers[key], f"binding.carriers[{key}]")
    _validate_value(value, type_json, carriers, "binding")
