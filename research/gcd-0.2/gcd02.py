#!/usr/bin/env python3
"""GCD/0.2-B1 research evaluator. Standard library only.

Finite, frozen carrier. Receipts are replayable, NOT cryptographically authenticated.
No canonical-kernel code is imported or changed; no external effects occur.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from itertools import combinations
import json

PROFILE = "GCD/0.2-research"
MODEL = "GCD-B1/0.2"
BASE = "v0.15-experimental-MSC1"
SIG0, SIG1, SIG2 = "gcd.workflow.s0", "gcd.workflow.s1", "gcd.workflow.s2"
MAX_RANK = 8  # implementation limit, NOT a mathematical rank ceiling


class InvalidInput(ValueError):
    pass


@dataclass(frozen=True)
class Signature:
    edition: str
    parent: str | None
    node_kinds: tuple[str, ...]
    relation_kinds: tuple[str, ...]
    added_kinds: tuple[str, ...] = ()
    added_relations: tuple[str, ...] = ()


SIGNATURES = {
    SIG0: Signature(SIG0, None, ("workflow",), ()),
    SIG1: Signature(SIG1, SIG0, ("workflow", "approve", "reject"), ("contains",),
                    ("approve", "reject"), ("contains",)),
    SIG2: Signature(SIG2, SIG1, ("workflow", "approve", "reject", "evidence_gate"),
                    ("contains", "requires"), ("evidence_gate",), ("requires",)),
}
NODE = {"W": "workflow", "A": "approve", "R": "reject", "E": "evidence_gate"}
ORDER = ("A", "R", "E")


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(obj):
    return sha256(canonical(obj).encode("utf-8")).hexdigest()


def require(condition, description):
    if not condition:
        raise InvalidInput(description)


@dataclass(frozen=True)
class Config:
    signature: str
    nodes: tuple[tuple[str, str], ...]
    relations: tuple[tuple[str, str, str], ...]

    def __post_init__(self):
        require(self.signature in SIGNATURES, "unregistered signature")
        require(type(self.nodes) is tuple and type(self.relations) is tuple,
                "canonical tuple representations required")
        require(all(type(n) is tuple and len(n) == 2 for n in self.nodes), "invalid node")
        require(all(type(r) is tuple and len(r) == 3 for r in self.relations), "invalid relation")
        require(self.nodes == tuple(sorted(self.nodes)), "nodes not canonical")
        require(self.relations == tuple(sorted(self.relations)), "relations not canonical")
        ids = tuple(n for n, _ in self.nodes)
        require(len(set(ids)) == len(ids), "duplicate node identity")
        require(("W", "workflow") in self.nodes, "workflow root is required")
        require(all(n in NODE and NODE[n] == k for n, k in self.nodes), "wrong node identity/kind")
        sig = SIGNATURES[self.signature]
        require(all(k in sig.node_kinds for _, k in self.nodes), "node kind outside signature")
        require(all(kind in sig.relation_kinds and a in ids and b in ids
                    for kind, a, b in self.relations), "invalid relation")
        expected = [("contains", "W", n) for n in ids if n != "W"]
        if "E" in ids:
            require("A" in ids, "evidence gate requires an approval node")
            expected.append(("requires", "A", "E"))
        require(self.relations == tuple(sorted(expected)), "missing or extraneous relation")


def make_config(signature: str, present=()) -> Config:
    require(signature in SIGNATURES, "unsupported signature")
    require(type(present) in (tuple, list, set, frozenset), "present must be finite sequence/set")
    require(all(type(x) is str and x in ORDER for x in present), "unknown stage identity")
    require(len(present) == len(set(present)), "duplicate stage")
    nodes = tuple(sorted((("W", "workflow"),) + tuple((n, NODE[n]) for n in present)))
    relations = [("contains", "W", n) for n in present]
    if "E" in present:
        relations.append(("requires", "A", "E"))
    return Config(signature, nodes, tuple(sorted(relations)))


def configs(signature):
    require(signature in SIGNATURES, "unknown signature")
    result = []
    for k in range(len(ORDER) + 1):
        for values in combinations(ORDER, k):
            try:
                result.append(make_config(signature, values))
            except InvalidInput:
                pass
    return tuple(sorted(result, key=lambda x: canonical(config_record(x))))


def config_record(c):
    return {"signature": c.signature, "nodes": [list(n) for n in c.nodes],
            "relations": [list(r) for r in c.relations]}


def read_config(record):
    require(type(record) is dict and set(record) == {"signature", "nodes", "relations"},
            "malformed configuration record")
    require(type(record["nodes"]) is list and type(record["relations"]) is list,
            "nodes and relations must be lists")
    c = Config(record["signature"], tuple(tuple(n) for n in record["nodes"]),
               tuple(tuple(r) for r in record["relations"]))
    require(config_record(c) == record, "noncanonical config record")
    return c


def ancestor(older, newer):
    require(older in SIGNATURES and newer in SIGNATURES, "unknown signature")
    cursor = newer
    while cursor is not None:
        if cursor == older:
            return True
        cursor = SIGNATURES[cursor].parent
    return False


def ground(c: Config, older: str) -> Config:
    require(ancestor(older, c.signature), "missing grounding bridge")
    kinds = set(SIGNATURES[older].node_kinds)
    retained = [n for n, kind in c.nodes if n != "W" and kind in kinds]
    return make_config(older, retained)


def embed(c: Config, newer: str) -> Config:
    require(ancestor(c.signature, newer), "missing embedding bridge")
    return make_config(newer, [n for n, _ in c.nodes if n != "W"])


@dataclass(frozen=True)
class Family:
    signature: str
    edition: str
    members: tuple[Config, ...]
    dependency_id: str

    def __post_init__(self):
        require(self.signature in SIGNATURES, "family signature unregistered")
        require(all(type(v) is str and 0 < len(v) <= 128 for v in (self.edition, self.dependency_id)),
                "invalid edition or shared dependency identifier")
        require(type(self.members) is tuple and all(type(c) is Config and c.signature == self.signature
                                                 for c in self.members), "wrong family elements")
        expected = tuple(sorted(self.members, key=lambda c: canonical(config_record(c))))
        require(self.members == expected and len(set(self.members)) == len(self.members),
                "family membership must be unique and canonical")


def family(signature, edition, members, dependency_id="release-0"):
    # Explicit set conversion is a convenience for locally constructed families only.
    require(all(type(c) is Config for c in members), "invalid family member")
    return Family(signature, edition,
                  tuple(sorted(set(members), key=lambda c: canonical(config_record(c)))), dependency_id)


def family_record(h):
    return {"signature": h.signature, "edition": h.edition,
            "dependency_id": h.dependency_id,
            "members": [config_record(c) for c in h.members]}


def read_family(record):
    require(type(record) is dict and set(record) ==
            {"signature", "edition", "dependency_id", "members"}, "malformed family record")
    require(type(record["members"]) is list, "member array required")
    h = Family(record["signature"], record["edition"],
               tuple(read_config(c) for c in record["members"]), record["dependency_id"])
    require(family_record(h) == record, "noncanonical family record")
    return h


def key(c: Config, criterion):
    if criterion == "exact":
        return canonical(config_record(c))
    if criterion == "kind_set":
        return canonical(sorted(k for _, k in c.nodes if k != "workflow"))
    if criterion == "root_only":
        return "workflow:W"
    raise InvalidInput("unregistered novelty criterion")


def outcome(status, **fields):
    return {"status": status, **fields}


def differentiate(source: Family, target: Family):
    if source.signature == target.signature:
        return outcome("access_refinement_only", reason="same semantic signature: new observations do not constitute structure")
    if not ancestor(source.signature, target.signature):
        return outcome("unsupported", reason="no registered grounding chain")
    if not source.members or len(target.members) < 2:
        return outcome("not_established", reason="comparison carrier requires at least two target configurations")
    if not all(ground(c, source.signature) in source.members for c in target.members):
        return outcome("rejected", reason="target not grounded within the exact source family")
    # Exhaustive ordered-pair law check over the declared finite comparison carrier.
    law_cases = 0
    strict_pairs = []
    for x in target.members:
        for y in target.members:
            law_cases += 1
            fine = x == y  # exact target semantic identity
            coarse = ground(x, source.signature) == ground(y, source.signature)
            if fine and not coarse:
                return outcome("rejected", reason="refinement implication failed")
            if coarse and not fine:
                strict_pairs.append((x, y))
    if not strict_pairs:
        return outcome("not_established", reason="no strict semantic split")
    added = set(SIGNATURES[target.signature].node_kinds) - set(SIGNATURES[source.signature].node_kinds)
    seen = {kind for c in target.members for _, kind in c.nodes}
    if not added.intersection(seen):
        return outcome("not_established", reason="no newly admitted semantic kind used")
    material_pairs = [(x, y) for x, y in strict_pairs if key(x, "kind_set") != key(y, "kind_set")]
    if not material_pairs:
        return outcome("not_established", reason="split does not distinguish semantic node kinds")
    first_x, first_y = material_pairs[0]
    new_roles = sorted(added.intersection(seen))
    return outcome("constitutive_refinement", source_digest=digest(family_record(source)),
                   target_digest=digest(family_record(target)),
                   carrier_count=len(target.members), ordered_pairs_checked=law_cases,
                   strict_ordered_pairs=len(strict_pairs), semantic_kinds_added=new_roles,
                   nonfactorisation_witness={"property": "kind_set",
                                             "left_value": key(first_x, "kind_set"),
                                             "right_value": key(first_y, "kind_set"),
                                             "same_ground": True},
                   comparison={"coarse": "grounded exact identity", "fine": "target exact identity"},
                   split_witness={"left": config_record(first_x), "right": config_record(first_y),
                                  "grounded_left": config_record(ground(first_x, source.signature)),
                                  "grounded_right": config_record(ground(first_y, source.signature))},
                   grounding_bridge=f"{target.signature}->{source.signature}",
                   interpretation_limit="relative constitution within admitted semantic signatures only")


def witness_novelty(old: tuple[Config, ...], candidate: Config, criterion: str):
    target_value = key(candidate, criterion)
    prior_keys = {key(x, criterion) for x in old}
    return target_value not in prior_keys


def generation_within(h: Family, candidate: Config, criterion="kind_set"):
    if h.signature != SIG1 or candidate.signature != SIG1:
        return outcome("unsupported", reason="only registered s1 combine rule is supported")
    a = make_config(SIG1, ("A",))
    r = make_config(SIG1, ("R",))
    expected = make_config(SIG1, ("A", "R"))
    if a not in h.members or r not in h.members:
        return outcome("domain_error", reason="combine rule requires both source alternatives")
    if candidate != expected:
        return outcome("domain_error", reason="candidate is not the rule-produced combination")
    if not witness_novelty(h.members, candidate, criterion):
        return outcome("non_expansive", reason="candidate is not new at pinned criterion")
    after = family(SIG1, h.edition + "+within", h.members + (candidate,), h.dependency_id)
    return outcome("expansive_within_signature", rule="combine_approve_reject/v1",
                   source_digest=digest(family_record(h)), target=family_record(after),
                   preserved=len(h.members), novelty_witness=config_record(candidate),
                   criterion=criterion, shared_dependency=h.dependency_id,
                   loss=[], comparison_bridge="identity:s1")


def generation_signature(h: Family, candidate: Config, criterion="kind_set"):
    if h.signature != SIG1 or candidate.signature != SIG2:
        return outcome("unsupported", reason="only registered s1->s2 signature extension supported")
    extended = tuple(embed(c, SIG2) for c in h.members)
    if candidate != make_config(SIG2, ("A", "E")):
        return outcome("domain_error", reason="new structural-kind rule requires approval with evidence gate")
    if make_config(SIG1, ("A",)) not in h.members:
        return outcome("domain_error", reason="source approval path missing")
    if ground(candidate, SIG1) not in h.members:
        return outcome("domain_error", reason="candidate has no admitted grounded predecessor")
    added_kind = set(k for _, k in candidate.nodes) & set(SIGNATURES[SIG2].added_kinds)
    added_relation = set(r for r, _, _ in candidate.relations) & set(SIGNATURES[SIG2].added_relations)
    if not added_kind or not added_relation:
        return outcome("non_expansive", reason="new structural kind and relation not witnessed")
    if not witness_novelty(extended, candidate, criterion):
        return outcome("non_expansive", reason="no novel target criterion class")
    after = family(SIG2, h.edition + "+signature", extended + (candidate,), h.dependency_id)
    return outcome("expansive_signature_generation", rule="add_evidence_gate/v1",
                   source_digest=digest(family_record(h)), target=family_record(after),
                   signature_extension={"from": SIG1, "to": SIG2,
                                        "added_kinds": sorted(added_kind),
                                        "added_relations": sorted(added_relation)},
                   preserved=len(h.members), new=config_record(candidate),
                   grounded_new=config_record(ground(candidate, SIG1)),
                   embedding_roundtrips=sum(ground(embed(c, SIG2), SIG1) == c for c in h.members),
                   comparison_bridge="embed:s1->s2/ground:s2->s1",
                   criterion=criterion, shared_dependency=h.dependency_id, loss=[])


@dataclass(frozen=True)
class ChoiceAct:
    choice_id: str
    actor_ref: str
    actor_binding_status: str
    authority_status: str
    mechanism: str
    policy_edition: str | None
    context: str
    source_family_edition: str
    source_family_digest: str
    dependency_id: str
    selected_config: dict
    selection_history_identity: str
    membership_witness: dict
    effect: str

    # Frozen record fields; nested JSON payloads are validated by receipt replay,
    # and are NOT trusted as immutable host-language objects.


def choose(h: Family, candidate: Config | None, choice_id, actor_ref,
           mechanism="supplied_input", policy=None, context="research-fixture"):
    require(type(choice_id) is str and choice_id and type(actor_ref) is str and actor_ref,
            "choice id and actor ref required")
    require(mechanism in ("supplied_input", "registered_policy"), "unknown selection basis")
    if mechanism == "registered_policy":
        if policy != "first_canonical/v1":
            return outcome("unsupported", reason="policy not registered")
        if not h.members:
            return outcome("unresolved", reason="empty source family")
        candidate = h.members[0]
    else:
        if candidate is None:
            return outcome("unresolved", reason="no supplied alternative")
    if candidate is None or candidate.signature != h.signature or candidate not in h.members:
        return outcome("rejected_nonmember", reason="selection is not an admitted family member")
    act = ChoiceAct(
        choice_id=choice_id, actor_ref=actor_ref,
        actor_binding_status="claimed_not_authenticated",
        authority_status="unverified_no_commit_authority",
        mechanism=mechanism,
        policy_edition=policy if mechanism == "registered_policy" else None,
        context=context, source_family_edition=h.edition,
        source_family_digest=digest(family_record(h)),
        dependency_id=h.dependency_id,
        selected_config=config_record(candidate),
        selection_history_identity=choice_id,
        membership_witness={"member_index": h.members.index(candidate),
                            "exact_config_digest": digest(config_record(candidate))},
        effect="description_selected_only")
    return outcome("selected", choice_act=asdict(act), source_family_preserved=True,
                   unchosen_member_count=len(h.members)-1, external_enactment=False)


def seed_family_from_choice(source: Family, choice_receipt: dict, new_edition: str):
    """Explicit, deliberately lossy adapter: chosen configuration -> singleton family.

    It does NOT mutate the original possibility family, and is NOT implicit coercion.
    """
    if not verify_receipt(choice_receipt):
        return outcome("rejected", reason="choice receipt is not replay-valid")
    result = choice_receipt["outcome"]
    if result["status"] != "selected":
        return outcome("rejected", reason="no selection to seed")
    act = result["choice_act"]
    if act["source_family_digest"] != digest(family_record(source)):
        return outcome("rejected", reason="source family edition mismatch")
    selected = read_config(act["selected_config"])
    if selected not in source.members:
        return outcome("rejected", reason="selected config not admitted")
    target = family(source.signature, new_edition, (selected,), source.dependency_id)
    excluded = tuple(c for c in source.members if c != selected)
    return outcome("seeded_singleton_family", target=family_record(target),
                   excluded=[config_record(c) for c in excluded],
                   source_family_preserved=True,
                   adapter="chosen_config_to_family/v1",
                   loss="other alternatives absent from new seeded family, retained in source")


FIXTURE_AUTHORITIES = {"reviewer:alice": "fixture-grant-alice"}


def commit_model(h: Family, choice_receipt: dict, actor_ref: str, grant: str,
                 base_epoch: int, event_id: str):
    # Intentionally model-local and unauthenticated. Not a real authorisation service.
    if not verify_receipt(choice_receipt):
        return outcome("rejected", reason="choice receipt failed deterministic replay")
    result = choice_receipt["outcome"]
    if result["status"] != "selected":
        return outcome("rejected", reason="no selected member")
    act = result["choice_act"]
    if act["source_family_digest"] != digest(family_record(h)):
        return outcome("rejected", reason="choice was made against another family edition")
    if act["actor_ref"] != actor_ref or FIXTURE_AUTHORITIES.get(actor_ref) != grant:
        return outcome("unauthorised", reason="no matching MODEL FIXTURE grant")
    require(type(base_epoch) is int and base_epoch >= 0 and type(event_id) is str and event_id,
            "bad model commitment arguments")
    selected = read_config(act["selected_config"])
    if selected not in h.members:
        return outcome("rejected", reason="chosen configuration not in exact family")
    return outcome("model_committed", event={"event_id": event_id, "base_epoch": base_epoch,
                                            "new_epoch": base_epoch+1,
                                            "choice_id": act["choice_id"],
                                            "selected_config": config_record(selected),
                                            "authorisation": "model_fixture_only",
                                            "world_executed": False},
                   semantic_description_changed=True, physical_or_external_effect=False)


def lift(source_id: str, steps: int, implementation_limit=MAX_RANK):
    require(type(source_id) is str and source_id and type(steps) is int and steps >= 0,
            "finite source and steps required")
    require(type(implementation_limit) is int and implementation_limit >= 0,
            "invalid resource bound")
    if steps > implementation_limit:
        return outcome("resource_limit", maximum_rank=implementation_limit,
                       requested_rank=steps)
    chain = []
    previous = digest({"root": source_id, "rank": 0})
    chain.append({"rank": 0, "parent_digest": None, "digest": previous})
    for rank in range(1, steps + 1):
        next_digest = digest({"parent_digest": previous, "rank": rank, "rule": "finite_lift/v1"})
        chain.append({"rank": rank, "parent_digest": previous, "digest": next_digest})
        previous = next_digest
    return outcome("finite_chain", rank=steps, chain=chain,
                   infinity_claim=False, mathematical_rule="n -> n+1 for any finite n")


def execute(request: dict):
    """Strict, finite, deterministic dispatch. Returns a typed record, no exception on domain failures."""
    try:
        require(type(request) is dict and type(request.get("op")) is str, "bad request")
        op = request["op"]
        schemas = {
            "differentiate": {"op", "source", "target"},
            "generate_within": {"op", "family", "candidate", "criterion"},
            "generate_signature": {"op", "family", "candidate", "criterion"},
            "choose": {"op", "family", "candidate", "choice_id", "actor_ref", "mechanism", "policy", "context"},
            "seed_from_choice": {"op", "family", "choice_receipt", "new_edition"},
            "lift": {"op", "source_id", "steps", "limit"},
            "commit_model": {"op", "family", "choice_receipt", "actor_ref", "grant", "base_epoch", "event_id"},
        }
        if op in schemas:
            require(set(request).issubset(schemas[op]), "unknown request field")
        if op == "differentiate":
            return differentiate(read_family(request["source"]), read_family(request["target"]))
        if op == "generate_within":
            return generation_within(read_family(request["family"]),
                                     read_config(request["candidate"]), request.get("criterion", "kind_set"))
        if op == "generate_signature":
            return generation_signature(read_family(request["family"]),
                                        read_config(request["candidate"]), request.get("criterion", "kind_set"))
        if op == "choose":
            candidate = read_config(request["candidate"]) if request.get("candidate") is not None else None
            return choose(read_family(request["family"]), candidate, request["choice_id"],
                          request["actor_ref"], request.get("mechanism", "supplied_input"),
                          request.get("policy"), request.get("context", "research-fixture"))
        if op == "seed_from_choice":
            return seed_family_from_choice(read_family(request["family"]),
                                           request["choice_receipt"], request["new_edition"])
        if op == "lift":
            return lift(request["source_id"], request["steps"], request.get("limit", MAX_RANK))
        if op == "commit_model":
            return commit_model(read_family(request["family"]), request["choice_receipt"],
                                request["actor_ref"], request["grant"], request["base_epoch"],
                                request["event_id"])
        return outcome("unsupported", reason="unknown operation")
    except (InvalidInput, KeyError, TypeError, ValueError) as exc:
        return outcome("invalid_input", reason=str(exc))


def receipt(request):
    require(type(request) is dict, "request must be an object")
    result = execute(request)
    body = {"kernel_base": BASE, "profile": PROFILE, "model": MODEL,
            "request": request, "outcome": result}
    return {**body, "digest_sha256": digest(body)}


def verify_receipt(item):
    if not isinstance(item, dict) or set(item) != {
            "kernel_base", "profile", "model", "request", "outcome", "digest_sha256"}:
        return False
    if (item["kernel_base"], item["profile"], item["model"]) != (BASE, PROFILE, MODEL):
        return False
    body = {key: item[key] for key in ("kernel_base", "profile", "model", "request", "outcome")}
    if digest(body) != item["digest_sha256"]:
        return False
    # Important: independently recompute using typed constructors and registered operators.
    return execute(item["request"]) == item["outcome"]


def complete_example():
    base = family(SIG0, "source-1", (make_config(SIG0),), "case-42")
    a, r = make_config(SIG1, ("A",)), make_config(SIG1, ("R",))
    differentiated = family(SIG1, "alternatives-1", (a, r), "case-42")
    diff_receipt = receipt({"op": "differentiate", "source": family_record(base),
                            "target": family_record(differentiated)})
    comb_receipt = receipt({"op": "generate_within", "family": family_record(differentiated),
                            "candidate": config_record(make_config(SIG1, ("A", "R")))})
    expanded = read_family(comb_receipt["outcome"]["target"])
    sig_receipt = receipt({"op": "generate_signature", "family": family_record(expanded),
                           "candidate": config_record(make_config(SIG2, ("A", "E")))})
    expanded_sig = read_family(sig_receipt["outcome"]["target"])
    chosen_receipt = receipt({"op": "choose", "family": family_record(expanded_sig),
                              "candidate": config_record(make_config(SIG2, ("A", "E"))),
                              "choice_id": "choice-001", "actor_ref": "reviewer:alice",
                              "context": "document-review-workflow"})
    before_commit = chosen_receipt["outcome"]["external_enactment"]
    commit_receipt = receipt({"op": "commit_model", "family": family_record(expanded_sig),
                              "choice_receipt": chosen_receipt, "actor_ref": "reviewer:alice",
                              "grant": "fixture-grant-alice", "base_epoch": 0,
                              "event_id": "model-transition-001"})
    stages = {"differentiation": diff_receipt, "within_signature_generation": comb_receipt,
              "signature_generation": sig_receipt, "selection": chosen_receipt,
              "model_only_commit": commit_receipt}
    assert before_commit is False
    assert all(verify_receipt(item) for item in stages.values())
    return {"case": "AI-assisted document release with evidence-gated branch",
            "description": "Model-relative novelty, dependency preservation, authority boundary; not a deployed workflow",
            "baseline_limitation": "A bare branch label or version-control diff does not by itself certify signature-criterion novelty, grounding, exact family membership or act/commit separation",
            "stages": stages, "external_effects": False,
            "claims": ["bounded structural conformance", "deterministic recomputation"],
            "non_claims": ["real-world authorisation", "external enactment", "market superiority",
                           "externally authenticated actor", "externally observed transition"]}


if __name__ == "__main__":
    print(json.dumps(complete_example(), indent=2, sort_keys=True))
