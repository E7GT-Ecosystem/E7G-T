#!/usr/bin/env python3
"""Bounded finite reference model for E7G-T MSC-B1/0.1."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any


class MSCError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MSCError(message)


def _indexed(items: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    _require(isinstance(items, list), f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        _require(isinstance(item, dict), f"{label}[{index}] must be an object")
        identity = item.get(key)
        _require(isinstance(identity, str) and identity, f"{label}[{index}].{key} missing")
        _require(identity not in result, f"duplicate {label} identifier {identity}")
        result[identity] = item
    return result


def validate_diagram(doc: dict[str, Any]) -> dict[str, Any]:
    _require(doc.get("schema_version") == "msc-diagram-v1", "unsupported schema_version")
    _require(isinstance(doc.get("diagram_id"), str) and doc["diagram_id"], "diagram_id missing")
    carriers = _indexed(doc.get("carriers"), "carrier_id", "carriers")
    scopes = _indexed(doc.get("scopes"), "scope_id", "scopes")
    maps = _indexed(doc.get("maps", []), "map_id", "maps")
    links = _indexed(doc.get("links", []), "link_id", "links")
    _require(carriers and scopes, "at least one carrier and scope are required")

    for carrier_id, carrier in carriers.items():
        values = carrier.get("values")
        _require(isinstance(values, list) and values, f"carrier {carrier_id} is empty")
        _require(all(isinstance(v, str) for v in values), f"carrier {carrier_id} has non-string value")
        _require(len(values) == len(set(values)), f"carrier {carrier_id} has duplicate values")
    for scope_id, scope in scopes.items():
        _require(scope.get("state_carrier") in carriers, f"scope {scope_id} has unknown state carrier")
        _require(isinstance(scope.get("edition"), str) and scope["edition"], f"scope {scope_id} edition missing")
    for map_id, mapping in maps.items():
        source = mapping.get("source_carrier")
        target = mapping.get("target_carrier")
        _require(source in carriers and target in carriers, f"map {map_id} has unknown carrier")
        table = mapping.get("table")
        _require(isinstance(table, dict), f"map {map_id} table missing")
        _require(set(table).issubset(set(carriers[source]["values"])), f"map {map_id} has key outside source carrier")
        _require(set(table.values()).issubset(set(carriers[target]["values"])), f"map {map_id} has value outside target carrier")

    edges: dict[str, list[str]] = {scope_id: [] for scope_id in scopes}
    for link_id, link in links.items():
        lower, upper = link.get("lower_scope"), link.get("upper_scope")
        _require(lower in scopes and upper in scopes and lower != upper, f"link {link_id} has invalid scopes")
        _require(link.get("criterion") == "exact", f"link {link_id} criterion unsupported")
        projection = maps.get(link.get("projection_map"))
        bridge = maps.get(link.get("bridge_map"))
        _require(projection is not None and bridge is not None, f"link {link_id} map missing")
        _require(projection["source_carrier"] == scopes[upper]["state_carrier"], f"link {link_id} projection source mismatch")
        _require(bridge["source_carrier"] == scopes[lower]["state_carrier"], f"link {link_id} bridge source mismatch")
        _require(projection["target_carrier"] == bridge["target_carrier"], f"link {link_id} has no common comparison carrier")
        edges[lower].append(upper)

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        _require(node not in visiting, "scope extension graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for child in edges[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)
    for node in scopes:
        visit(node)

    max_combinations = doc.get("max_combinations", 100000)
    _require(isinstance(max_combinations, int) and not isinstance(max_combinations, bool) and max_combinations > 0, "max_combinations invalid")
    return {"carriers": carriers, "scopes": scopes, "maps": maps, "links": links, "max_combinations": max_combinations}


def _map_total(mapping: dict[str, Any], carrier: dict[str, Any]) -> bool:
    return set(mapping["table"]) == set(carrier["values"])


def _access_quotients(doc: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for profile in doc.get("access_profiles", []):
        scope_id = profile.get("scope")
        _require(scope_id in model["scopes"], f"access profile has unknown scope {scope_id}")
        carrier_id = model["scopes"][scope_id]["state_carrier"]
        values = model["carriers"][carrier_id]["values"]
        observation_ids = profile.get("observation_maps")
        _require(isinstance(observation_ids, list), "observation_maps must be an array")
        observations = []
        for map_id in observation_ids:
            mapping = model["maps"].get(map_id)
            _require(mapping is not None and mapping["source_carrier"] == carrier_id, f"invalid observation map {map_id}")
            observations.append(mapping)
        classes: dict[tuple[Any, ...], list[str]] = {}
        for value in values:
            signature = tuple(mapping["table"].get(value, {"undefined": True}) for mapping in observations)
            classes.setdefault(tuple(json.dumps(v, sort_keys=True) for v in signature), []).append(value)
        results.append({
            "profile_id": profile.get("profile_id"),
            "scope": scope_id,
            "context": profile.get("context"),
            "classes": sorted((sorted(group) for group in classes.values()), key=lambda x: x[0]),
        })
    return results


def _commutation(doc: dict[str, Any], model: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for test in doc.get("commutation_tests", []):
        direct = model["maps"].get(test.get("direct_map"))
        path = [model["maps"].get(map_id) for map_id in test.get("path", [])]
        if direct is None or not path or any(mapping is None for mapping in path):
            results.append({"test_id": test.get("test_id"), "outcome": "unsupported"})
            continue
        typed = path[0]["source_carrier"] == direct["source_carrier"] and path[-1]["target_carrier"] == direct["target_carrier"]
        typed = typed and all(path[i]["target_carrier"] == path[i + 1]["source_carrier"] for i in range(len(path) - 1))
        if not typed:
            results.append({"test_id": test.get("test_id"), "outcome": "domain_mismatch"})
            continue
        disagreements = []
        unsupported = False
        for source in model["carriers"][direct["source_carrier"]]["values"]:
            if source not in direct["table"]:
                unsupported = True
                break
            staged = source
            for mapping in path:
                if staged not in mapping["table"]:
                    unsupported = True
                    break
                staged = mapping["table"][staged]
            if unsupported:
                break
            if direct["table"][source] != staged:
                disagreements.append(source)
        outcome = "unsupported" if unsupported else ("commuting" if not disagreements else "non_commuting")
        result = {"test_id": test.get("test_id"), "outcome": outcome}
        if disagreements:
            result["disagreement_sources"] = disagreements
        results.append(result)
    return results


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    model = validate_diagram(doc)
    carriers, scopes, maps, links = model["carriers"], model["scopes"], model["maps"], model["links"]
    for link in links.values():
        projection, bridge = maps[link["projection_map"]], maps[link["bridge_map"]]
        upper_carrier = carriers[scopes[link["upper_scope"]]["state_carrier"]]
        lower_carrier = carriers[scopes[link["lower_scope"]]["state_carrier"]]
        if not _map_total(projection, upper_carrier) or not _map_total(bridge, lower_carrier):
            return {"schema_version": "msc-result-v1", "diagram_id": doc["diagram_id"], "outcome": "unsupported", "reason": "required coherence map is partial"}

    scope_ids = sorted(scopes)
    domains = [carriers[scopes[scope_id]["state_carrier"]]["values"] for scope_id in scope_ids]
    combination_count = 1
    for domain in domains:
        combination_count *= len(domain)
    if combination_count > model["max_combinations"]:
        return {"schema_version": "msc-result-v1", "diagram_id": doc["diagram_id"], "outcome": "resource_limit", "candidate_combinations": combination_count, "limit": model["max_combinations"]}

    pairwise = {}
    for link_id, link in links.items():
        lower_values = carriers[scopes[link["lower_scope"]]["state_carrier"]]["values"]
        upper_values = carriers[scopes[link["upper_scope"]]["state_carrier"]]["values"]
        projection, bridge = maps[link["projection_map"]], maps[link["bridge_map"]]
        pairwise[link_id] = any(projection["table"][upper] == bridge["table"][lower] for lower in lower_values for upper in upper_values)

    compatible = []
    for values in itertools.product(*domains):
        assignment = dict(zip(scope_ids, values))
        if all(maps[link["projection_map"]]["table"][assignment[link["upper_scope"]]] == maps[link["bridge_map"]]["table"][assignment[link["lower_scope"]]] for link in links.values()):
            compatible.append(assignment)

    if len(compatible) == 1:
        outcome = "unique"
    elif compatible:
        outcome = "ambiguous"
    else:
        outcome = "incompatible"

    result: dict[str, Any] = {
        "schema_version": "msc-result-v1",
        "diagram_id": doc["diagram_id"],
        "outcome": outcome,
        "candidate_combinations": combination_count,
        "compatible_count": len(compatible),
        "compatible_families": compatible,
        "pairwise_link_satisfiable": pairwise,
        "pairwise_all_satisfiable": all(pairwise.values()),
        "global_obstruction_despite_pairwise_compatibility": not compatible and all(pairwise.values()),
        "access_quotients": _access_quotients(doc, model),
        "commutation_tests": _commutation(doc, model),
        "interpretation_boundary": "Finite model-relative coherence only; no external existence, infinity, causation or authority claim.",
    }

    invariant_results = []
    for test in doc.get("invariant_tests", []):
        mappings_by_scope = test.get("maps_by_scope")
        _require(isinstance(mappings_by_scope, dict) and len(mappings_by_scope) >= 2, "invariant test requires two scopes")
        selected = []
        target = None
        for scope_id, map_id in mappings_by_scope.items():
            mapping = maps.get(map_id)
            _require(scope_id in scopes and mapping is not None, f"invalid invariant map {map_id}")
            _require(mapping["source_carrier"] == scopes[scope_id]["state_carrier"], f"invariant source mismatch {map_id}")
            target = target or mapping["target_carrier"]
            _require(mapping["target_carrier"] == target, "invariant maps have different target carriers")
            selected.append((scope_id, mapping))
        if not compatible:
            inv_outcome = "vacuous"
        elif any(not _map_total(mapping, carriers[mapping["source_carrier"]]) for _, mapping in selected):
            inv_outcome = "unsupported"
        else:
            inv_outcome = "preserved" if all(len({mapping["table"][family[scope_id]] for scope_id, mapping in selected}) == 1 for family in compatible) else "violated"
        invariant_results.append({"test_id": test.get("test_id"), "outcome": inv_outcome})
    result["invariant_tests"] = invariant_results
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagram", type=Path)
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.diagram.read_text(encoding="utf-8"))
        print(json.dumps(evaluate(document), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, MSCError) as exc:
        print(f"MSC validation error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

