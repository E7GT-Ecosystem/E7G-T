"""Finite, spec-derived WP5 history and temporal-phase adapter.

The carrier is an illustrative review/approval state machine. Its rules are
declared here, not attributed to the E7G-T reference or a physical process.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

EDITION = "E7C-TEMPORAL-HISTORY-B1/0.1-provisional"
PHASE_CRITERION = "AUDIT-APPROVAL-AND-WITHDRAWAL/0.1"
OPERATIONS = ("review", "withdraw_review", "approve")


class AdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class State:
    reviewed: bool
    approved: bool

    def __post_init__(self):
        if type(self.reviewed) is not bool or type(self.approved) is not bool:
            raise AdmissionError("state_requires_two_boolean_coordinates")


def step(state: State, operation: str) -> State | None:
    if type(state) is not State or operation not in OPERATIONS:
        raise AdmissionError("unknown_state_or_operation")
    if operation == "review":
        return State(True, state.approved)
    if operation == "withdraw_review":
        return State(False, state.approved)
    if not state.reviewed:
        return None  # Strict domain: this declared model requires review first.
    return State(state.reviewed, True)


@dataclass(frozen=True)
class Transition:
    operation: str
    source: State
    target: State


@dataclass(frozen=True)
class History:
    identity: str
    initial: State
    transitions: tuple[Transition, ...]

    def __post_init__(self):
        if (type(self.identity) is not str or not self.identity or
                type(self.initial) is not State or type(self.transitions) is not tuple):
            raise AdmissionError("invalid_history")
        current = self.initial
        for transition in self.transitions:
            if type(transition) is not Transition or transition.source != current:
                raise AdmissionError("broken_transition_chain")
            expected = step(current, transition.operation)
            if expected is None or transition.target != expected:
                raise AdmissionError("unadmitted_transition")
            current = transition.target

    @property
    def final(self) -> State:
        return self.transitions[-1].target if self.transitions else self.initial


def extend(history: History, operation: str) -> History | None:
    if type(history) is not History:
        raise AdmissionError("typed_history_required")
    next_state = step(history.final, operation)
    if next_state is None:
        return None
    return History(history.identity, history.initial,
                   history.transitions + (Transition(operation, history.final, next_state),))


@dataclass(frozen=True)
class RetainedFinalView:
    source: History
    displayed: State

    def __post_init__(self):
        if type(self.source) is not History or self.displayed != self.source.final:
            raise AdmissionError("view_must_retain_exact_source")


def view_final(history: History) -> RetainedFinalView:
    if type(history) is not History:
        raise AdmissionError("typed_history_required")
    return RetainedFinalView(history, history.final)


@dataclass(frozen=True)
class ProjectedFinal:
    edition: str
    state: State
    preserves: tuple[str, ...] = ("final_reviewed", "final_approved")
    loses: tuple[str, ...] = ("step_order", "intermediate_states", "withdrawal_record")

    def __post_init__(self):
        if (self.edition != EDITION or type(self.state) is not State or
                self.preserves != ("final_reviewed", "final_approved") or
                self.loses != ("step_order", "intermediate_states", "withdrawal_record")):
            raise AdmissionError("invalid_temporal_projection")


def project_final(history: History) -> ProjectedFinal:
    if type(history) is not History:
        raise AdmissionError("typed_history_required")
    return ProjectedFinal(EDITION, history.final)


@dataclass(frozen=True)
class HistoryCarrier:
    edition: str
    histories: tuple[History, ...]

    def __post_init__(self):
        if (self.edition != EDITION or type(self.histories) is not tuple or
                any(type(h) is not History for h in self.histories) or
                len({h.identity for h in self.histories}) != len(self.histories)):
            raise AdmissionError("invalid_declared_history_carrier")


@dataclass(frozen=True)
class Fibre:
    carrier: HistoryCarrier
    projection: ProjectedFinal
    status: str
    candidates: tuple[History, ...]
    bound: int

    def __post_init__(self):
        if (type(self.carrier) is not HistoryCarrier or
                type(self.projection) is not ProjectedFinal or
                type(self.bound) is not int or self.bound < 0):
            raise AdmissionError("invalid_fibre")
        if self.status == "success":
            if (self.bound < len(self.carrier.histories) or
                    self.candidates != tuple(h for h in self.carrier.histories
                                             if h.final == self.projection.state)):
                raise AdmissionError("incomplete_or_wrong_fibre")
        elif self.status == "resource_limit":
            if self.bound >= len(self.carrier.histories) or self.candidates:
                raise AdmissionError("resource_limit_cannot_return_candidates")
        else:
            raise AdmissionError("unknown_fibre_status")


def reconstruct(carrier: HistoryCarrier, projection: ProjectedFinal,
                scan_bound: int) -> Fibre:
    if (type(carrier) is not HistoryCarrier or type(projection) is not ProjectedFinal
            or type(scan_bound) is not int or scan_bound < 0):
        raise AdmissionError("typed_carrier_projection_and_bound_required")
    if scan_bound < len(carrier.histories):
        return Fibre(carrier, projection, "resource_limit", (), scan_bound)
    return Fibre(carrier, projection, "success", tuple(
        h for h in carrier.histories if h.final == projection.state), scan_bound)


@dataclass(frozen=True)
class TemporalPhase:
    criterion: str
    approved: bool
    withdrawal_seen: bool


def phase(history: History) -> TemporalPhase:
    if type(history) is not History:
        raise AdmissionError("typed_history_required")
    return TemporalPhase(PHASE_CRITERION, history.final.approved,
                         any(t.operation == "withdraw_review" for t in history.transitions))


def phase_candidates(fibre: Fibre) -> tuple[TemporalPhase, ...]:
    if type(fibre) is not Fibre or fibre.status != "success":
        raise AdmissionError("complete_candidate_fibre_required")
    return tuple(sorted({phase(h) for h in fibre.candidates},
                        key=lambda p: (p.approved, p.withdrawal_seen)))


def phase_boundary(source: History, target: History) -> bool:
    """Require exactly one admitted extension, not just differing phases."""
    if (type(source) is not History or type(target) is not History or
            source.identity != target.identity or target.initial != source.initial or
            len(target.transitions) != len(source.transitions) + 1 or
            target.transitions[:-1] != source.transitions):
        raise AdmissionError("phase_boundary_requires_admitted_transition")
    return phase(source) != phase(target)


@dataclass(frozen=True)
class RepresentativeStatus:
    domain_saturated: bool
    result_congruent: bool
    domain_witness: tuple[str, str] | None
    result_witness: tuple[str, str] | None


def representative_status(carrier: HistoryCarrier, operation: str) -> RepresentativeStatus:
    if type(carrier) is not HistoryCarrier or operation not in OPERATIONS:
        raise AdmissionError("typed_carrier_and_operation_required")
    domain, result = None, None
    for left, right in combinations(carrier.histories, 2):
        if phase(left) != phase(right):
            continue
        a, b = extend(left, operation), extend(right, operation)
        if domain is None and ((a is None) != (b is None)):
            domain = (left.identity, right.identity)
        if result is None and a is not None and b is not None and phase(a) != phase(b):
            result = (left.identity, right.identity)
    return RepresentativeStatus(domain is None, result is None, domain, result)


@dataclass(frozen=True)
class OrderComparison:
    left_then_right: History | None
    right_then_left: History | None
    same_final: bool | None


def compare_order(source: History, left: str, right: str) -> OrderComparison:
    if type(source) is not History or left not in OPERATIONS or right not in OPERATIONS:
        raise AdmissionError("typed_order_comparison_required")
    a = extend(source, left)
    b = extend(source, right)
    lr = extend(a, right) if a is not None else None
    rl = extend(b, left) if b is not None else None
    return OrderComparison(lr, rl, lr.final == rl.final if lr and rl else None)
