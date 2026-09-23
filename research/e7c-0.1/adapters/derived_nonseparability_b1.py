"""Derived finite relational-separation assessment over existing FG3 fibres.

No new E7C constructor: the only projection and reconstruction are the
already declared untagged FG3 edge-count quotient and finite candidate fibre.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from eec_q_fg3_b1 import AdmissionError, Config, State, signature
from eec_q_fg3_phase_b1 import BASIS, CRITERION, identify_phase
from eec_q_fg3_fibre_b1 import FiniteCarrier, reconstruct_fibre

MODULE_EDITION = "E7C-DERIVED-RELATIONAL-SEPARATION/0.1-provisional"
PROTECTED = ("edge_count", "has_AB")


def _singleton(config: Config) -> State:
    if type(config) is not Config or config not in BASIS:
        raise AdmissionError("only untagged fixed FG3 graphs admitted")
    return State(((config, Fraction(1)),))


def complete_carrier() -> FiniteCarrier:
    states = tuple(sorted((_singleton(graph) for graph in BASIS), key=signature))
    return FiniteCarrier("FG3-ALL-EIGHT-GRAPHS/0.1", states)


def _protected(config: Config, criterion: str) -> int | bool:
    return len(config.edges) if criterion == "edge_count" else "AB" in config.edges


@dataclass(frozen=True)
class Assessment:
    edition: str
    semantic_context: str
    inquiry: str
    protected_criterion: str
    projection_criterion: str
    source: Config
    carrier: FiniteCarrier
    component_views: tuple[tuple[str, str], ...]
    outcome: str
    compatible: tuple[Config, ...]
    material_witness: tuple[Config, Config] | None
    reason: str
    lost_relations: tuple[str, ...]


def assess(source: Config, carrier: FiniteCarrier, budget: int,
           semantic_context: str, inquiry: str,
           protected_criterion: str) -> Assessment:
    """Decide only relative to the *complete* declared eight-graph basis."""
    state = _singleton(source)
    if (type(carrier) is not FiniteCarrier or type(budget) is not int or budget < 0 or
            type(semantic_context) is not str or not semantic_context or
            type(inquiry) is not str or not inquiry or
            protected_criterion not in PROTECTED):
        raise AdmissionError("typed context inquiry carrier criterion and bound required")
    target = identify_phase(state)
    complete = complete_carrier()
    if carrier.edition != complete.edition:
        raise AdmissionError("candidate_carrier_edition_mismatch")
    fibre = reconstruct_fibre(target, carrier, budget)
    base = dict(edition=MODULE_EDITION, semantic_context=semantic_context,
                inquiry=inquiry, protected_criterion=protected_criterion,
                projection_criterion=CRITERION, source=source, carrier=carrier,
                component_views=(("A", "present"), ("B", "present"), ("C", "present")),
                lost_relations=("exact_edge_identity",))
    if fibre.tag != "success":
        return Assessment(**base, outcome="undetermined", compatible=(),
                          material_witness=None,
                          reason="resource_limit")
    if carrier.candidates != complete.candidates:
        return Assessment(**base, outcome="undetermined", compatible=(),
                          material_witness=None,
                          reason="candidate_carrier_not_complete_fixed_basis")
    graphs = tuple(candidate.terms[0][0] for candidate in fibre.candidates)
    if source not in graphs:
        return Assessment(**base, outcome="undetermined", compatible=graphs,
                          material_witness=None,
                          reason="source_not_in_declared_fibre")
    different = next((graph for graph in graphs
                      if _protected(graph, protected_criterion) !=
                      _protected(source, protected_criterion)), None)
    if different is not None:
        return Assessment(**base, outcome="non_separable", compatible=graphs,
                          material_witness=(source, different),
                          reason="hidden_relation_changes_protected_property")
    # Return the whole compatible class; selecting one graph would invent
    # an unsupported exact relation among the isolated components.
    return Assessment(**base, outcome="separable", compatible=graphs,
                      material_witness=None,
                      reason="all_complete_fibre_candidates_preserve_protected_property")
