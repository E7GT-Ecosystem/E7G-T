"""Finite candidate-relative reconstruction for the provisional FG3 quotient.

No operation here recovers a unique graph state from a lossy PhaseState.
Only a source-retaining view permits exact source return.
"""

from __future__ import annotations

from dataclasses import dataclass

from eec_q_fg3_b1 import AdmissionError, State, signature
from eec_q_fg3_phase_b1 import (CRITERION, PhaseState, PhaseView, identify_phase,
                               phase_view)

PROJECTION = "FG3-EDGE-COUNT-VIEW/0.1"
SOURCE_RETURN = "exact_retained_source_only"
HIDDEN = ("exact_edge_identity_within_phase",)
PRESERVED = ("exact_rational_coefficient_in_retained_source", "edge_count_display")


@dataclass(frozen=True)
class SourceProjection:
    edition: str
    displayed: PhaseView
    identified: PhaseState
    preserved: tuple[str, ...]
    hidden: tuple[str, ...]
    source_return_policy: str

    def __post_init__(self) -> None:
        if (self.edition != PROJECTION or type(self.displayed) is not PhaseView
                or type(self.identified) is not PhaseState or self.preserved != PRESERVED
                or self.hidden != HIDDEN or self.source_return_policy != SOURCE_RETURN
                or self.identified != identify_phase(self.displayed.source)):
            raise AdmissionError("invalid source-retaining projection declaration")


def project_view(source: State) -> SourceProjection:
    """Keep source and quotient observation together; source-return is explicit."""
    displayed = phase_view(source)
    return SourceProjection(PROJECTION, displayed, identify_phase(source),
                            PRESERVED, HIDDEN, SOURCE_RETURN)


def source_return(projection: SourceProjection) -> State:
    if type(projection) is not SourceProjection:
        raise AdmissionError("exact source return requires a retained view")
    return projection.displayed.source


@dataclass(frozen=True)
class FiniteCarrier:
    edition: str
    candidates: tuple[State, ...]

    def __post_init__(self) -> None:
        if type(self.edition) is not str or not self.edition or type(self.candidates) is not tuple:
            raise AdmissionError("finite carrier edition and tuple required")
        keys = []
        for state in self.candidates:
            if type(state) is not State:
                raise AdmissionError("candidate must be an admitted graph state")
            identify_phase(state)  # reject tags even in candidates that may not match
            keys.append(signature(state))
        if keys != sorted(set(keys)):
            raise AdmissionError("candidate carrier must be unique and canonical")


@dataclass(frozen=True)
class FibreOutcome:
    tag: str
    target: PhaseState
    carrier: FiniteCarrier
    checked: int
    candidates: tuple[State, ...] | None

    def __post_init__(self) -> None:
        if (type(self.target) is not PhaseState or type(self.carrier) is not FiniteCarrier
                or type(self.checked) is not int or self.checked < 0):
            raise AdmissionError("invalid fibre outcome scope")
        if self.tag == "resource_limit":
            if self.checked != 0 or self.candidates is not None:
                raise AdmissionError("resource limit cannot report a partial fibre")
        elif self.tag == "success":
            expected = tuple(s for s in self.carrier.candidates if identify_phase(s) == self.target)
            if self.checked != len(self.carrier.candidates) or self.candidates != expected:
                raise AdmissionError("success requires exact declared finite fibre")
        else:
            raise AdmissionError("unknown fibre outcome")


def reconstruct_fibre(target: PhaseState, carrier: FiniteCarrier, budget: int) -> FibreOutcome:
    """Exhaust exactly the declared candidates, or return no success fibre."""
    if (type(target) is not PhaseState or type(carrier) is not FiniteCarrier
            or type(budget) is not int or budget < 0):
        raise AdmissionError("typed phase, candidate carrier and nonnegative budget required")
    if target.criterion != CRITERION:
        raise AdmissionError("phase edition mismatch")
    if len(carrier.candidates) > budget:
        return FibreOutcome("resource_limit", target, carrier, 0, None)
    matches = tuple(candidate for candidate in carrier.candidates
                    if identify_phase(candidate) == target)
    return FibreOutcome("success", target, carrier,
                        len(carrier.candidates), matches)
