"""Provisional typed finite MSC coherence module for selected MSC-B1/0.1 diagrams.

Admission interprets carriers, scopes, maps and links. Source-specific optional
test, access and query declarations must be omitted; equivalent selected
operations are requested through explicit typed calls after evaluation.
This is a separate profile module, not E7C-B1 grammar or a truth oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

EDITION = "E7C-MSC-FINITE-B1/0.1-provisional"
SOURCE = "MSC-B1/0.1:msc-diagram-v1"


class AdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class Carrier:
    identity: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class Scope:
    identity: str
    edition: str
    carrier: str


@dataclass(frozen=True)
class Map:
    identity: str
    source: str
    target: str
    table: tuple[tuple[str, str], ...]

    def at(self, value: str) -> str | None:
        return dict(self.table).get(value)


@dataclass(frozen=True)
class Link:
    identity: str
    lower: str
    upper: str
    projection: str
    comparison: str


@dataclass(frozen=True)
class Diagram:
    edition: str
    identity: str
    carriers: tuple[Carrier, ...]
    scopes: tuple[Scope, ...]
    maps: tuple[Map, ...]
    links: tuple[Link, ...]
    limit: int


@dataclass(frozen=True)
class Result:
    outcome: str
    candidate_count: int
    compatible: tuple[tuple[tuple[str, str], ...], ...]
    linkwise: tuple[tuple[str, bool], ...]

    @property
    def obstruction(self) -> bool:
        return self.outcome == "incompatible" and all(ok for _, ok in self.linkwise)


def admit(document: dict) -> Diagram:
    """Check the selected exact deterministic scope/map/link language first."""
    if type(document) is not dict or document.get("schema_version") != "msc-diagram-v1":
        raise AdmissionError("unsupported_diagram_edition")
    allowed = {"schema_version", "diagram_id", "max_combinations", "carriers",
               "scopes", "maps", "links"}
    if set(document) - allowed or any(k not in document for k in
                                      ("diagram_id", "carriers", "scopes", "maps", "links")):
        raise AdmissionError("unsupported_diagram_shape")
    def indexed(key, id_key):
        items = document[key]
        if type(items) is not list or any(type(x) is not dict or
                                          type(x.get(id_key)) is not str or not x[id_key]
                                          for x in items):
            raise AdmissionError("invalid_" + key)
        ids = [x[id_key] for x in items]
        if len(ids) != len(set(ids)):
            raise AdmissionError("duplicate_" + key)
        return items

    raw_carriers = indexed("carriers", "carrier_id")
    raw_scopes = indexed("scopes", "scope_id")
    raw_maps = indexed("maps", "map_id")
    raw_links = indexed("links", "link_id")
    shapes = ((raw_carriers, {"carrier_id", "values"}),
              (raw_scopes, {"scope_id", "edition", "state_carrier"}),
              (raw_maps, {"map_id", "source_carrier", "target_carrier", "table"}),
              (raw_links, {"link_id", "lower_scope", "upper_scope",
                           "projection_map", "comparison_map", "criterion"}))
    if any(set(item) != fields for items, fields in shapes for item in items):
        raise AdmissionError("unsupported_record_shape")
    if type(document["diagram_id"]) is not str or not document["diagram_id"]:
        raise AdmissionError("invalid_diagram_id")
    if any(type(x["values"]) is not list or
           any(type(v) is not str for v in x["values"])
           for x in raw_carriers) or any(
        type(x["table"]) is not dict or
        any(type(k) is not str or type(v) is not str for k, v in x["table"].items())
        for x in raw_maps):
        raise AdmissionError("invalid_carrier_or_map")
    if any(type(x[k]) is not str for x in raw_maps
           for k in ("source_carrier", "target_carrier")):
        raise AdmissionError("invalid_map")
    if any(type(x["edition"]) is not str or type(x["state_carrier"]) is not str
           for x in raw_scopes) or any(
        type(x[k]) is not str for x in raw_links
        for k in ("lower_scope", "upper_scope", "projection_map", "comparison_map")):
        raise AdmissionError("invalid_scope_or_link")
    carriers = tuple(Carrier(x["carrier_id"], tuple(x["values"])) for x in raw_carriers)
    scopes = tuple(Scope(x["scope_id"], x["edition"], x["state_carrier"])
                   for x in raw_scopes)
    maps = tuple(Map(x["map_id"], x["source_carrier"], x["target_carrier"],
                     tuple(sorted(x["table"].items()))) for x in raw_maps)
    links = tuple(Link(x["link_id"], x["lower_scope"], x["upper_scope"],
                       x["projection_map"], x["comparison_map"]) for x in raw_links)
    cs, ss, ms = ({x.identity: x for x in items} for items in (carriers, scopes, maps))
    if not carriers or not scopes or any(not c.values or len(c.values) != len(set(c.values))
                                          or any(type(v) is not str for v in c.values)
                                          for c in carriers):
        raise AdmissionError("invalid_carrier")
    if any(not s.edition or s.carrier not in cs for s in scopes):
        raise AdmissionError("invalid_scope")
    if any(m.source not in cs or m.target not in cs or
           any(k not in cs[m.source].values or v not in cs[m.target].values
               for k, v in m.table) for m in maps):
        raise AdmissionError("invalid_map")
    if any(l.lower not in ss or l.upper not in ss or l.lower == l.upper or
           l.projection not in ms or l.comparison not in ms or
           ms[l.projection].source != ss[l.upper].carrier or
           ms[l.comparison].source != ss[l.lower].carrier or
           ms[l.projection].target != ms[l.comparison].target
           for l in links):
        raise AdmissionError("no_common_comparison_carrier_or_invalid_link")
    if any(x.get("criterion") != "exact" for x in document["links"]):
        raise AdmissionError("unsupported_criterion")
    # A scope order must be acyclic. Traverse all starts in this finite carrier.
    edges = {s.identity: set() for s in scopes}
    for link in links:
        edges[link.lower].add(link.upper)
    for start in edges:
        frontier, seen = list(edges[start]), set()
        while frontier:
            node = frontier.pop()
            if node == start:
                raise AdmissionError("scope_cycle")
            if node not in seen:
                seen.add(node)
                frontier.extend(edges[node])
    limit = document.get("max_combinations", 100000)
    if type(limit) is not int or limit < 1:
        raise AdmissionError("invalid_limit")
    return Diagram(EDITION, document["diagram_id"], carriers, scopes, maps, links, limit)


def evaluate(diagram: Diagram) -> Result:
    if type(diagram) is not Diagram or diagram.edition != EDITION:
        raise AdmissionError("wrong_diagram_sort")
    cs = {c.identity: c for c in diagram.carriers}
    ss = {s.identity: s for s in diagram.scopes}
    ms = {m.identity: m for m in diagram.maps}
    for link in diagram.links:
        for map_id in (link.projection, link.comparison):
            mapping = ms[map_id]
            if set(dict(mapping.table)) != set(cs[mapping.source].values):
                return Result("unsupported", 0, (), ())
    scopes = sorted(ss)
    domains = [cs[ss[s].carrier].values for s in scopes]
    count = 1
    for domain in domains:
        count *= len(domain)
    if count > diagram.limit:
        return Result("resource_limit", count, (), ())
    linkwise = []
    for link in diagram.links:
        lowers = cs[ss[link.lower].carrier].values
        uppers = cs[ss[link.upper].carrier].values
        linkwise.append((link.identity, any(ms[link.projection].at(u) ==
                                           ms[link.comparison].at(l)
                                           for l in lowers for u in uppers)))
    compatible = []
    for values in product(*domains):
        assignment = dict(zip(scopes, values))
        if all(ms[link.projection].at(assignment[link.upper]) ==
               ms[link.comparison].at(assignment[link.lower])
               for link in diagram.links):
            compatible.append(tuple(sorted(assignment.items())))
    outcome = "unique" if len(compatible) == 1 else (
        "ambiguous" if compatible else "incompatible")
    return Result(outcome, count, tuple(compatible), tuple(linkwise))


def scope_fibre(diagram: Diagram, result: Result, scope: str, value: str):
    """Finite candidate family; defined only after complete compatibility scan."""
    if result.outcome not in {"unique", "ambiguous", "incompatible"}:
        raise AdmissionError("incomplete_carrier")
    scopes = {s.identity: s for s in diagram.scopes}
    carriers = {c.identity: c for c in diagram.carriers}
    if scope not in scopes or value not in carriers[scopes[scope].carrier].values:
        raise AdmissionError("scope_state_sort_mismatch")
    return tuple(family for family in result.compatible if dict(family)[scope] == value)


def observation_fibre(diagram: Diagram, result: Result, scope: str,
                      observation_map: str, value: str):
    if result.outcome not in {"unique", "ambiguous", "incompatible"}:
        raise AdmissionError("incomplete_carrier")
    scopes = {s.identity: s for s in diagram.scopes}
    maps = {m.identity: m for m in diagram.maps}
    carriers = {c.identity: c for c in diagram.carriers}
    if (scope not in scopes or observation_map not in maps or
            maps[observation_map].source != scopes[scope].carrier or
            value not in carriers[maps[observation_map].target].values):
        raise AdmissionError("observation_sort_mismatch")
    return tuple(family for family in result.compatible
                 if maps[observation_map].at(dict(family)[scope]) == value)


def access_classes(diagram: Diagram, scope: str, observation_maps: tuple[str, ...]):
    """Fixed MSC-B1 co-undefined-equal policy, including empty observation lists."""
    scopes = {s.identity: s for s in diagram.scopes}
    maps = {m.identity: m for m in diagram.maps}
    carriers = {c.identity: c for c in diagram.carriers}
    if scope not in scopes or any(m not in maps or maps[m].source != scopes[scope].carrier
                                  for m in observation_maps):
        raise AdmissionError("observation_sort_mismatch")
    classes = {}
    for state in carriers[scopes[scope].carrier].values:
        key = tuple(maps[m].at(state) for m in observation_maps)
        classes.setdefault(key, []).append(state)
    return tuple(sorted((tuple(sorted(group)) for group in classes.values()),
                        key=lambda group: group[0]))
