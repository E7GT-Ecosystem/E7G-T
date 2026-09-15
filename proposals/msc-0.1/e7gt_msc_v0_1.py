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


def _string(value: Any, message: str) -> str:
    _require(isinstance(value, str) and bool(value), message)
    return value


def _shape(value: Any, label: str, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{label} must be an object")
    optional = optional or set()
    missing = required - set(value)
    extra = set(value) - required - optional
    _require(not missing, f"{label} missing fields: {sorted(missing)}")
    _require(not extra, f"{label} has additional fields: {sorted(extra)}")
    return value


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


def validate_diagram(doc: Any) -> dict[str, Any]:
    _shape(doc, "document", {"schema_version", "diagram_id", "carriers", "scopes", "maps", "links"},
           {"max_combinations", "access_profiles", "commutation_tests", "invariant_tests", "reconstruction_queries"})
    _require(doc["schema_version"] == "msc-diagram-v1", "unsupported schema_version")
    _require(isinstance(doc["diagram_id"], str) and doc["diagram_id"], "diagram_id missing")
    carriers = _indexed(doc["carriers"], "carrier_id", "carriers")
    scopes = _indexed(doc["scopes"], "scope_id", "scopes")
    maps = _indexed(doc["maps"], "map_id", "maps")
    links = _indexed(doc["links"], "link_id", "links")
    access_profiles = _indexed(doc.get("access_profiles", []), "profile_id", "access_profiles")
    commutation_tests = _indexed(doc.get("commutation_tests", []), "test_id", "commutation_tests")
    invariant_tests = _indexed(doc.get("invariant_tests", []), "test_id", "invariant_tests")
    reconstruction_queries = _indexed(doc.get("reconstruction_queries", []), "query_id", "reconstruction_queries")
    _require(carriers and scopes, "at least one carrier and scope are required")
    _require(not (set(commutation_tests) & set(invariant_tests)), "duplicate test_id across test families")

    for carrier_id, carrier in carriers.items():
        _shape(carrier, f"carrier {carrier_id}", {"carrier_id", "values"})
        values = carrier["values"]
        _require(isinstance(values, list) and values, f"carrier {carrier_id} is empty")
        _require(all(isinstance(v, str) for v in values), f"carrier {carrier_id} has non-string value")
        _require(len(values) == len(set(values)), f"carrier {carrier_id} has duplicate values")
    for scope_id, scope in scopes.items():
        _shape(scope, f"scope {scope_id}", {"scope_id", "edition", "state_carrier"})
        state_carrier = _string(scope["state_carrier"], f"scope {scope_id} state carrier invalid")
        _require(state_carrier in carriers, f"scope {scope_id} has unknown state carrier")
        _string(scope["edition"], f"scope {scope_id} edition missing")
    for map_id, mapping in maps.items():
        _shape(mapping, f"map {map_id}", {"map_id", "source_carrier", "target_carrier", "table"})
        source = _string(mapping["source_carrier"], f"map {map_id} source carrier invalid")
        target = _string(mapping["target_carrier"], f"map {map_id} target carrier invalid")
        _require(source in carriers and target in carriers, f"map {map_id} has unknown carrier")
        table = mapping["table"]
        _require(isinstance(table, dict), f"map {map_id} table missing")
        _require(all(isinstance(k, str) and isinstance(v, str) for k, v in table.items()), f"map {map_id} table must map strings")
        _require(set(table).issubset(set(carriers[source]["values"])), f"map {map_id} has key outside source carrier")
        _require(set(table.values()).issubset(set(carriers[target]["values"])), f"map {map_id} has value outside target carrier")

    edges: dict[str, list[str]] = {scope_id: [] for scope_id in scopes}
    for link_id, link in links.items():
        _shape(link, f"link {link_id}", {"link_id", "lower_scope", "upper_scope", "projection_map", "comparison_map", "criterion"})
        lower = _string(link["lower_scope"], f"link {link_id} lower scope invalid")
        upper = _string(link["upper_scope"], f"link {link_id} upper scope invalid")
        _require(lower in scopes and upper in scopes and lower != upper, f"link {link_id} has invalid scopes")
        _require(link["criterion"] == "exact", f"link {link_id} criterion unsupported")
        projection_id = _string(link["projection_map"], f"link {link_id} projection map invalid")
        comparison_id = _string(link["comparison_map"], f"link {link_id} comparison map invalid")
        projection = maps.get(projection_id)
        comparison = maps.get(comparison_id)
        _require(projection is not None and comparison is not None, f"link {link_id} map missing")
        _require(projection["source_carrier"] == scopes[upper]["state_carrier"], f"link {link_id} projection source mismatch")
        _require(comparison["source_carrier"] == scopes[lower]["state_carrier"], f"link {link_id} comparison source mismatch")
        _require(projection["target_carrier"] == comparison["target_carrier"], f"link {link_id} has no common comparison carrier")
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

    for profile_id, profile in access_profiles.items():
        _shape(profile, f"access profile {profile_id}", {"profile_id", "scope", "context", "observation_maps"})
        scope_id = _string(profile["scope"], f"access profile {profile_id} scope invalid")
        _require(scope_id in scopes, f"access profile {profile_id} has unknown scope")
        _string(profile["context"], f"access profile {profile_id} context missing")
        observation_ids = profile["observation_maps"]
        _require(isinstance(observation_ids, list) and all(isinstance(v, str) and v for v in observation_ids), f"access profile {profile_id} observation maps invalid")
        _require(len(observation_ids) == len(set(observation_ids)), f"access profile {profile_id} observation maps duplicate")
        source = scopes[scope_id]["state_carrier"]
        for map_id in observation_ids:
            _require(map_id in maps, f"access profile {profile_id} has unknown observation map {map_id}")
            _require(maps[map_id]["source_carrier"] == source, f"access profile {profile_id} observation source mismatch")

    for test_id, test in commutation_tests.items():
        _shape(test, f"commutation test {test_id}", {"test_id", "direct_map", "path"})
        direct_id = _string(test["direct_map"], f"commutation test {test_id} direct map invalid")
        _require(direct_id in maps, f"commutation test {test_id} has unknown direct map")
        _require(isinstance(test["path"], list) and test["path"] and all(isinstance(v, str) and v for v in test["path"]), f"commutation test {test_id} path invalid")
        for map_id in test["path"]:
            _require(map_id in maps, f"commutation test {test_id} has unknown path map {map_id}")

    for test_id, test in invariant_tests.items():
        _shape(test, f"invariant test {test_id}", {"test_id", "maps_by_scope"})
        selected = test["maps_by_scope"]
        _require(isinstance(selected, dict) and len(selected) >= 2, f"invariant test {test_id} requires two scopes")
        _require(all(isinstance(scope_id, str) and scope_id and isinstance(map_id, str) and map_id for scope_id, map_id in selected.items()), f"invariant test {test_id} references invalid")
        target = None
        for scope_id, map_id in selected.items():
            _require(scope_id in scopes and map_id in maps, f"invariant test {test_id} has unknown reference")
            mapping = maps[map_id]
            _require(mapping["source_carrier"] == scopes[scope_id]["state_carrier"], f"invariant test {test_id} source mismatch")
            target = target or mapping["target_carrier"]
            _require(mapping["target_carrier"] == target, f"invariant test {test_id} target mismatch")

    for query_id, query in reconstruction_queries.items():
        _shape(query, f"reconstruction query {query_id}", {"query_id", "scope", "kind", "value"}, {"observation_map"})
        query_scope = _string(query["scope"], f"reconstruction query {query_id} scope invalid")
        _require(query_scope in scopes, f"reconstruction query {query_id} has unknown scope")
        kind = _string(query["kind"], f"reconstruction query {query_id} kind invalid")
        _require(kind in {"scope_state", "observation"}, f"reconstruction query {query_id} kind invalid")
        _require(isinstance(query["value"], str), f"reconstruction query {query_id} value invalid")
        source = scopes[query_scope]["state_carrier"]
        if kind == "scope_state":
            _require("observation_map" not in query, f"scope-state query {query_id} must not name observation map")
            _require(query["value"] in carriers[source]["values"], f"scope-state query {query_id} value outside carrier")
        else:
            map_id = _string(query.get("observation_map"), f"observation query {query_id} observation map invalid")
            _require(map_id in maps, f"observation query {query_id} has unknown map")
            mapping = maps[map_id]
            _require(mapping["source_carrier"] == source, f"observation query {query_id} source mismatch")
            _require(query["value"] in carriers[mapping["target_carrier"]]["values"], f"observation query {query_id} value outside carrier")

    max_combinations = doc.get("max_combinations", 100000)
    _require(isinstance(max_combinations, int) and not isinstance(max_combinations, bool) and max_combinations > 0, "max_combinations invalid")
    order_pairs = {(scope_id, scope_id) for scope_id in scopes}
    for lower in scopes:
        frontier = list(edges[lower])
        while frontier:
            upper = frontier.pop()
            if (lower, upper) not in order_pairs:
                order_pairs.add((lower, upper))
                frontier.extend(edges[upper])
    return {
        "carriers": carriers, "scopes": scopes, "maps": maps, "links": links,
        "access_profiles": access_profiles, "commutation_tests": commutation_tests,
        "invariant_tests": invariant_tests, "reconstruction_queries": reconstruction_queries,
        "scope_order": sorted([list(pair) for pair in order_pairs]),
        "max_combinations": max_combinations,
    }


def _map_total(mapping: dict[str, Any], carrier: dict[str, Any]) -> bool:
    return set(mapping["table"]) == set(carrier["values"])


def _access_quotients(model: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for profile_id, profile in model["access_profiles"].items():
        scope_id = profile["scope"]
        carrier_id = model["scopes"][scope_id]["state_carrier"]
        values = model["carriers"][carrier_id]["values"]
        observations = [model["maps"][map_id] for map_id in profile["observation_maps"]]
        classes: dict[tuple[str, ...], list[str]] = {}
        for value in values:
            signature = tuple(json.dumps(mapping["table"].get(value, {"undefined": True}), sort_keys=True) for mapping in observations)
            classes.setdefault(signature, []).append(value)
        results.append({
            "profile_id": profile_id, "scope": scope_id, "context": profile["context"],
            "classes": sorted((sorted(group) for group in classes.values()), key=lambda x: x[0]),
            "empty_observation_family": not observations,
            "missingness_rule": "co_undefined_equal",
        })
    return results


def _commutation(model: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for test_id, test in model["commutation_tests"].items():
        direct = model["maps"][test["direct_map"]]
        path = [model["maps"][map_id] for map_id in test["path"]]
        typed = path[0]["source_carrier"] == direct["source_carrier"] and path[-1]["target_carrier"] == direct["target_carrier"]
        typed = typed and all(path[i]["target_carrier"] == path[i + 1]["source_carrier"] for i in range(len(path) - 1))
        if not typed:
            results.append({"test_id": test_id, "outcome": "domain_mismatch"})
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
        result: dict[str, Any] = {"test_id": test_id, "outcome": outcome}
        if disagreements:
            result["disagreement_sources"] = disagreements
        results.append(result)
    return results


def _invariants(model: dict[str, Any], compatible: list[dict[str, str]]) -> list[dict[str, str]]:
    results = []
    for test_id, test in model["invariant_tests"].items():
        selected = [(scope_id, model["maps"][map_id]) for scope_id, map_id in test["maps_by_scope"].items()]
        if not compatible:
            outcome = "not_applicable_incompatible"
        else:
            undefined = any(family[scope_id] not in mapping["table"] for family in compatible for scope_id, mapping in selected)
            if undefined:
                outcome = "unsupported"
            else:
                preserved = all(len({mapping["table"][family[scope_id]] for scope_id, mapping in selected}) == 1 for family in compatible)
                outcome = "preserved" if preserved else "violated"
        results.append({"test_id": test_id, "outcome": outcome})
    return results


def _reconstruction(model: dict[str, Any], compatible: list[dict[str, str]]) -> list[dict[str, Any]]:
    results = []
    for query_id, query in model["reconstruction_queries"].items():
        if query["kind"] == "scope_state":
            families = [family for family in compatible if family[query["scope"]] == query["value"]]
        else:
            mapping = model["maps"][query["observation_map"]]
            families = [family for family in compatible if mapping["table"].get(family[query["scope"]]) == query["value"]]
        results.append({"query_id": query_id, "kind": query["kind"], "compatible_count": len(families), "compatible_families": families})
    return results


def evaluate(doc: Any) -> dict[str, Any]:
    model = validate_diagram(doc)
    carriers, scopes, maps, links = model["carriers"], model["scopes"], model["maps"], model["links"]
    for link in links.values():
        projection, comparison = maps[link["projection_map"]], maps[link["comparison_map"]]
        upper_carrier = carriers[scopes[link["upper_scope"]]["state_carrier"]]
        lower_carrier = carriers[scopes[link["lower_scope"]]["state_carrier"]]
        if not _map_total(projection, upper_carrier) or not _map_total(comparison, lower_carrier):
            return {"schema_version": "msc-result-v1", "diagram_id": doc["diagram_id"], "outcome": "unsupported", "reason": "MSC-B1 requires total-on-admitted-carrier coherence maps", "interpretation_boundary": "Finite model-relative coherence only; no external existence, infinity, causation or authority claim."}

    scope_ids = sorted(scopes)
    domains = [carriers[scopes[scope_id]["state_carrier"]]["values"] for scope_id in scope_ids]
    combination_count = 1
    for domain in domains:
        combination_count *= len(domain)
    if combination_count > model["max_combinations"]:
        return {"schema_version": "msc-result-v1", "diagram_id": doc["diagram_id"], "outcome": "resource_limit", "candidate_combinations": combination_count, "limit": model["max_combinations"], "interpretation_boundary": "Finite model-relative coherence only; no external existence, infinity, causation or authority claim."}

    linkwise = {}
    for link_id, link in links.items():
        lower_values = carriers[scopes[link["lower_scope"]]["state_carrier"]]["values"]
        upper_values = carriers[scopes[link["upper_scope"]]["state_carrier"]]["values"]
        projection, comparison = maps[link["projection_map"]], maps[link["comparison_map"]]
        linkwise[link_id] = any(projection["table"][upper] == comparison["table"][lower] for lower in lower_values for upper in upper_values)

    compatible = []
    for values in itertools.product(*domains):
        assignment = dict(zip(scope_ids, values))
        coherent = all(
            maps[link["projection_map"]]["table"][assignment[link["upper_scope"]]]
            == maps[link["comparison_map"]]["table"][assignment[link["lower_scope"]]]
            for link in links.values()
        )
        if coherent:
            compatible.append(assignment)

    outcome = "unique" if len(compatible) == 1 else ("ambiguous" if compatible else "incompatible")
    return {
        "schema_version": "msc-result-v1",
        "diagram_id": doc["diagram_id"],
        "outcome": outcome,
        "scope_order_reflexive_transitive_closure": model["scope_order"],
        "candidate_combinations": combination_count,
        "compatible_count": len(compatible),
        "compatible_families": compatible,
        "linkwise_satisfiable": linkwise,
        "all_links_individually_satisfiable": all(linkwise.values()),
        "global_obstruction_despite_linkwise_satisfiability": not compatible and all(linkwise.values()),
        "access_quotients": _access_quotients(model),
        "commutation_tests": _commutation(model),
        "invariant_tests": _invariants(model, compatible),
        "reconstruction_queries": _reconstruction(model, compatible),
        "interpretation_boundary": "Finite model-relative coherence only; no external existence, infinity, causation or authority claim.",
    }


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
