"""Selected WP5 WPC/0.2 allocation adapter; finite draft model only.

The E7C carrier keeps semantic wholes, occurrence-bearing portions, encoded
representations, and proposed successors separate. No commitment is modeled.
"""

from __future__ import annotations

from dataclasses import dataclass
import json

SOURCE_EDITION = "E7G-T-v0.13-draft:WPC/0.2-proposed:allocation-example/0.1"
MODULE_EDITION = "E7C-WPC-ALLOCATION-B1/0.1-provisional"
IDS = ("A", "B", "C")


class AdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class Whole:
    epoch: int
    members: tuple[str, ...]
    values: tuple[int, ...]
    events: tuple[tuple, ...] = ()
    budget: int = 2

    def __post_init__(self):
        if type(self.epoch) is not int or self.epoch < 0:
            raise AdmissionError("invalid_epoch")
        if (type(self.members) is not tuple or not self.members
                or self.members != tuple(sorted(set(self.members)))
                or not set(self.members) <= set(IDS)):
            raise AdmissionError("invalid_membership")
        if type(self.values) is not tuple or len(self.values) != len(self.members):
            raise AdmissionError("coverage_incomplete")
        if any(type(v) is not int or not 0 <= v <= 2 for v in self.values):
            raise AdmissionError("invalid_value")
        if type(self.budget) is not int or self.budget != 2:
            raise AdmissionError("unsupported_budget")
        if sum(self.values) > self.budget:
            raise AdmissionError("global_incompatibility")
        if type(self.events) is not tuple or any(type(e) is not tuple for e in self.events):
            raise AdmissionError("invalid_history")


@dataclass(frozen=True)
class Representation:
    edition: str
    payload: str


@dataclass(frozen=True)
class Portion:
    occurrence: str
    local_value: int
    representation: Representation


@dataclass(frozen=True)
class Presentation:
    epoch: int
    manifest: tuple[str, ...]
    portions: tuple[Portion, ...]
    events: tuple[tuple, ...]


def represent(whole: Whole) -> Representation:
    if type(whole) is not Whole:
        raise AdmissionError("whole_required")
    payload = json.dumps([SOURCE_EDITION, whole.epoch, whole.members,
                          whole.values, whole.events, whole.budget],
                         separators=(",", ":"), ensure_ascii=True)
    return Representation(SOURCE_EDITION, payload)


def extract(representation: Representation) -> Whole:
    if type(representation) is not Representation or representation.edition != SOURCE_EDITION:
        raise AdmissionError("unsupported_profile")
    # Only model-produced canonical representations are admitted to this bridge.
    try:
        profile, epoch, members, values, events, budget = json.loads(representation.payload)
        if profile != SOURCE_EDITION:
            raise AdmissionError("unsupported_profile")
        whole = Whole(epoch, tuple(members), tuple(values),
                      tuple(tuple(e) for e in events), budget)
    except AdmissionError:
        raise
    except (ValueError, TypeError, KeyError) as exc:
        raise AdmissionError("invalid_representation") from exc
    if represent(whole) != representation:
        raise AdmissionError("noncanonical_representation")
    return whole


def materialise(whole: Whole) -> Presentation:
    payload = represent(whole)
    return Presentation(whole.epoch, whole.members,
                        tuple(Portion(i, v, payload)
                              for i, v in zip(whole.members, whole.values)),
                        whole.events)


def constitute(presentation: Presentation) -> Whole:
    """Constitute from actual portions, then check each representation agrees."""
    if type(presentation) is not Presentation:
        raise AdmissionError("presentation_required")
    if tuple(p.occurrence for p in presentation.portions) != presentation.manifest:
        raise AdmissionError("coverage_incomplete")
    actual = Whole(presentation.epoch, presentation.manifest,
                   tuple(p.local_value for p in presentation.portions),
                   presentation.events)
    for portion in presentation.portions:
        if extract(portion.representation) != actual:
            raise AdmissionError("source_conflict")
    if materialise(actual) != presentation:
        raise AdmissionError("noncanonical_assembly")
    return actual


@dataclass(frozen=True)
class Proposal:
    event_id: str
    actor: str
    base: Representation
    target: str
    value: int


@dataclass(frozen=True)
class Candidate:
    base: Whole
    proposed: Whole
    accepted_events: tuple[str, ...]


def reconcile(base: Whole, proposals: tuple[Proposal, ...]) -> Candidate:
    if type(base) is not Whole or type(proposals) is not tuple:
        raise AdmissionError("invalid_proposal_input")
    unique = {}
    for proposal in proposals:
        if type(proposal) is not Proposal or type(proposal.event_id) is not str or not proposal.event_id:
            raise AdmissionError("invalid_event_id")
        if proposal.event_id in unique and unique[proposal.event_id] != proposal:
            raise AdmissionError("event_equivocation")
        unique[proposal.event_id] = proposal
    if not unique:
        return Candidate(base, base, ())
    writes, events = {}, []
    seen = {event[0] for event in base.events}
    for event_id, proposal in sorted(unique.items()):
        if event_id in seen:
            raise AdmissionError("already_committed_event")
        if proposal.base != represent(base):
            raise AdmissionError("precondition_conflict")
        if proposal.actor != proposal.target or proposal.target not in base.members:
            raise AdmissionError("unauthorised")
        if proposal.target in writes:
            raise AdmissionError("write_conflict")
        if type(proposal.value) is not int or not 0 <= proposal.value <= 2:
            raise AdmissionError("invalid_value")
        writes[proposal.target] = proposal.value
        events.append((event_id, proposal.actor, base.epoch, "set",
                       proposal.target, proposal.value))
    values = dict(zip(base.members, base.values))
    values.update(writes)
    successor = Whole(base.epoch + 1, base.members,
                      tuple(values[i] for i in base.members), base.events + tuple(events))
    return Candidate(base, successor, tuple(sorted(unique)))


def membership_candidate(base: Whole, actor: str, members: tuple[str, ...],
                         event_id: str) -> Candidate:
    """Admit a proposed membership successor with an explicit base lineage."""
    if type(base) is not Whole:
        raise AdmissionError("whole_required")
    if actor != "coordinator":
        raise AdmissionError("unauthorised")
    if not event_id or event_id in {event[0] for event in base.events}:
        raise AdmissionError("invalid_event_id")
    values = dict(zip(base.members, base.values))
    members = tuple(members)
    historical = set(base.members)
    for event in base.events:
        if event[3] == "membership":
            historical.update(event[4].split(","))
            historical.update(event[5].split(","))
    if (set(members) - set(base.members)) & historical:
        raise AdmissionError("occurrence_reuse")
    proposed = Whole(base.epoch + 1, members,
                     tuple(values.get(i, 0) for i in members),
                     base.events + ((event_id, actor, base.epoch, "membership",
                                     ",".join(base.members), ",".join(members)),))
    return Candidate(base, proposed, (event_id,))
