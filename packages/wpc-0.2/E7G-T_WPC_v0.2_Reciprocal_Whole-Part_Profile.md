---
title: "E7G-T WPC/0.2 — Reciprocal Whole–Part Constitution"
profile: "WPC/0.2-proposed"
revision: "RWP1"
date: "2026-09-14"
kernel: "E7G-T v0.13-experimental-RWP1-draft"
authors: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
status: "Experimental standalone companion draft; bounded executable subset"
core_capability: "WPC-Core/0.2"
optional_capabilities:
  - "WPC-Evolution/0.1"
  - "WPC-Distributed/0.1"
legacy_profile: "WPC/0.1"
normativity: "MUST and MUST NOT apply only to implementations selecting the named profile and capability scope. This companion does not establish production readiness, external instantiation or general mathematical validity."
---

# E7G-T WPC/0.2 — Reciprocal Whole–Part Constitution

Added in revision **RWP1**, 2026-09-14. WPC/0.2 is a proposed successor to, not a silent reinterpretation of, WPC/0.1. It formalises a reciprocal system in which participating local states, relations, dependencies and admitted history constitute a semantic whole; constituents may additionally carry representations of that whole; and admitted local or relational changes may contribute to a successor whole whose representations are subsequently renewed, weakened explicitly or marked stale.

WPC/0.2 does not assert that an external system instantiates the profile, that a representation is ontologically identical to what it represents, or that a local constituent has unrestricted knowledge or authority. It supplies finite, typed, boundary-relative semantics.

### W.0 Profile structure and selection

WPC/0.2 is modular:

| Capability | Content | Selection rule |
|---|---|---|
| `WPC-Core/0.2` | Objects, coverage, constitution, representation, retention, expression, membership and reciprocal closure | Required when declaring WPC/0.2 |
| `WPC-Evolution/0.1` | Proposals, reconciliation, commitment, refresh, membership transition and causal history | Optional additional declaration |
| `WPC-Distributed/0.1` | Concurrency, partial failure, currentness, availability and deployment consistency | Optional; requires WPC-Evolution and a declared deployment model |

An implementation MUST publish a capability vector. It MUST NOT claim the evolution or distributed capability merely because it implements static reciprocal closure. Conversely, a constitutive system may be coherent without selecting all-portions SR4 or any encoding capability.

The equations below are stipulated definitions and conditional obligations. No claim of mathematical novelty, general consistency, production readiness, universal ontology or completeness beyond the declared model boundary is made.

### W.1 Reciprocal principle

Within a pinned boundary and history scope, a whole is constituted by its participating occurrences, local semantic states, relations, interfaces, shared dependencies, constraints and admitted joint history:

\[
A\xrightarrow{\mathsf{Constitute}_\rho}W.
\]

A constituent may additionally carry a representation from which a declared scope of the whole can be reconstructed:

\[
q(W)\xrightarrow{e_i}F_i\xrightarrow{d_i}q(W).
\]

When evolution is selected, admitted local, relational or whole-level proposals may jointly constitute a successor:

\[
(W,\Delta)
\xrightarrow{\mathsf{Reconcile}_\rho}\mathcal C
\xrightarrow{\mathsf{Commit}_\rho}W'
\xrightarrow{\mathsf{Refresh}_\rho}Z'.
\]

Neither direction supplies another automatically. An archive may reconstruct a whole without participating in its current constitution. A constituent may participate without carrying an encoding. A whole-bearing constituent has both roles under separate witnesses. Decoding a description does not instantiate its described system, reproduce an external event, grant authority or prove operational availability.

### W.2 Objects, boundaries and identity

#### W.2.1 Three central sorts

| Sort | Symbol | Meaning |
|---|---|---|
| Constitutive presentation | \(A\) | Indexed local states, membership, relations, interfaces, dependencies, constraints and retained history presented for constitution |
| Semantic whole | \(W\) | One canonical admitted result of constituting a complete presentation under profile \(\rho\) |
| Materialised assembly | \(Z\) | A carrier containing constituent occurrences, their current semantic state, optional whole-bearing payloads and declared materialisation metadata |

These are representation sorts inside the model. The modelled external entity remains separately identified. A blueprint, a canonical semantic whole and a running deployment have different scopes unless an explicit bridge proves otherwise.

A versioned profile declaration \(\rho\) fixes the signatures, canonical forms, admission predicates, boundary policy, composition operations, update grammar, identity rules, encoding environment, normalisation and comparison criteria. Source-specific information MUST NOT be hidden inside a supposedly fixed decoder or profile.

#### W.2.2 Constitutive presentation and semantic whole

For a finite epoch \(\varepsilon\), define:

\[
A_\varepsilon=
\langle
B_\varepsilon,M_\varepsilon,
\{(i,s_i)\}_{i\in I_\varepsilon},
R_\varepsilon,J_\varepsilon,K_\varepsilon,
D_\varepsilon,H_\varepsilon
\rangle,
\]

where \(B\) is the boundary and external interface, \(M\) the membership manifest, \(i\) an occurrence identity, \(s_i\) its local semantic state and authority bindings, \(R\) typed possibly multi-way relations, \(J\) interface contracts, \(K\) local and global constraints, \(D\) joint alternatives and shared dependencies, and \(H\) the retained finite causal history and provenance.

The semantic whole is:

\[
W_\varepsilon=
\operatorname{Can}_\rho
\langle\ell,\varepsilon,A_\varepsilon\rangle,
\]

with continuing lineage identifier \(\ell\). Lineage, epoch and exact value identity remain distinct. Every field capable of changing a protected operation, admission result or identity belongs inside semantic identity or has an explicit bridge and loss account. Diagnostic formatting and cache bytes MAY remain outside identity only by declaration.

#### W.2.3 Constituent occurrence

A materialised constituent occurrence is:

\[
C_i=\langle i,s_i,F_i,b_i,p_i\rangle,
\]

where \(F_i\) is an optional encoded payload, \(b_i\) binds its source scope, source edition and codec, and \(p_i\) carries declared provenance or transport metadata. Occurrence identity, local semantic state and payload identity are separate. Equal payload bytes do not merge occurrences. Copying a payload does not create membership, authority or an additional vote.

### W.3 Coverage, constitution and global coherence

#### W.3.1 Coverage contract

A coverage contract declares:

1. the model boundary and temporal or causal cut;
2. the expected occurrence, relation and interface inventory, or a terminating inventory-generation rule;
3. the authority and evidence supporting that inventory;
4. the mapping from expected to supplied items;
5. duplicate, alias, exclusion, unknown and external-dependency policies;
6. manifest and coverage-witness editions.

For a finite inventory, exact coverage means equality of expected and supplied occurrence sets and coverage of every required relation and interface, not equality of counts. A narrowed boundary is a new declared boundary. An inaccessible required item is `unavailable`, not absent. No unknown may be deleted merely to obtain a successful result. The default profile requires a nonempty active occurrence set; an empty-system option must be selected explicitly and cannot use vacuous all-portions reasoning as evidence of distributed whole-bearing.

#### W.3.2 Constitution operation

\(\mathsf{Constitute}_\rho(A)\) checks coverage, identity, local typing, relation and interface typing, overlap, dependency semantics, history and every declared global constraint. It returns exactly one of:

| Outcome | Meaning |
|---|---|
| `unique(W,witnesses)` | Exactly one canonical admitted whole is established |
| `ambiguous(family,witnesses)` | At least two admitted wholes remain |
| `incompatible(obstruction)` | No admitted whole exists under the declared carrier and constraints |
| `undetermined` | Available procedures did not determine the result |
| `unsupported` | A required sort, predicate, solver or operation is unavailable |
| `resource_limit` | Computation stopped before the exact result was established |
| `invalid_input` | Syntax, typing, identity or admission failed before constitution |

A deterministic relational carrier may produce one canonical assembly directly. A constraint carrier may produce a family. No candidate may be silently discarded and no arbitrary representative may be reported as the whole.

#### W.3.3 Local agreement is not global admission

Local overlap checks compare expressions through pinned common carriers, bridges and criteria. They preserve disagreement and unknowns. They do not replace multi-way relation checks or global constraints.

Pairwise agreement may establish global admission only when a sufficiency theorem or exhaustive bounded validation is supplied for the exact carrier, cover, constraint language and domain. There is no automatic sheaf, topology or categorical-gluing claim. Agreement of all payloads likewise does not prove correct inventory, global safety, empirical truth, independent evidence or authority.

### W.4 Representation, retention and local expression

#### W.4.1 Constitutive and reconstructive capabilities

For source scope \(q\), an occurrence has exact SR4 retention when:

\[
d_{i,\rho}(e_{i,\rho}(q(W)))=q(W)
\]

on its declared domain, with the inherited injectivity, capacity, codec-edition and self-containment obligations of §R.5. The strongest complete semantic-whole claim uses \(q=\operatorname{id}\) on the declared \(W\) carrier. If \(q\) omits local state, relations or history, the claim MUST name that restricted scope.

All-portions SR4 requires the equation for every active occurrence. It is optional and is not a prerequisite for constitutive coherence. Mixed SR tiers MAY be reported per occurrence. For nonempty membership, all-portions SR4 and minimal joint necessity for reconstructing the same exact scope are incompatible: any one SR4 payload is already sufficient. Collective necessity may instead concern membership, organisation, authority, availability or capability.

#### W.4.2 Contextual expression

A read-only local expression is:

\[
x_{i,\xi}=\chi_i(C_i,\xi),
\]

where \(\xi\) pins the applicable role, time, regime, access scope, composition scope and inquiry. The record retains the occurrence, source edition, derivation, preserved invariants, loss account and authority boundary.

A state-changing or generative expression MUST additionally produce an explicit proposal or event and any candidate local-state value. It MUST NOT mutate an immutable constituent by notation alone. Display-only differences need not enter \(W\); a local value that changes capabilities, constraints, history or future transitions must enter \(s_i\), a relation, a dependency or a declared external input.

### W.5 Reciprocal materialisation and reconstruction

#### W.5.1 Extraction and constitution from an assembly

A typed extraction map:

\[
\epsilon_\rho:B_Z\rightharpoonup B_A
\]

reads the semantic occurrence states, membership, relations, interfaces, dependencies, constraints and retained history from an admitted materialised assembly. It MUST declare what assembly fields it ignores and why they are outside semantic identity.

Strict semantic reconstruction first constitutes the extracted presentation:

\[
\mathsf{Constitute}_\rho(\epsilon_\rho(Z))
=\operatorname{unique}(W_Z,w_Z).
\]

If constitution is ambiguous, incompatible, undetermined, unsupported or resource-limited, reciprocal reconstruction returns the corresponding failure. It MUST NOT decode one payload and overwrite conflicting current local state.

#### W.5.2 Canonical materialisation

For admitted \(W\), canonical materialisation is:

\[
\alpha_\rho(W)=
\mathsf{Materialise}_\rho
\bigl(W,\{C_i(W)\}_{i\in I_W}\bigr)
=Z_W.
\]

The materialisation contract determines current local states, relations, component occurrences and any selected retention payloads. It MUST NOT create a literally self-containing byte definition. The semantic whole describes finite constituents and relations; the materialised carrier may then store encodings of that finite semantic value. Codec bytes, receipts and final digests are outside the same commit's encoded semantic scope by default and may enter a later edition.

#### W.5.3 Strict reconstruction and agreement

Let \(Q_Z\subseteq I_W\) be the occurrences required by the selected retention claim. The reconstruction map \(\beta_\rho\) succeeds with \(W_Z\) only when:

\[
\mathsf{Constitute}_\rho(\epsilon_\rho(Z))
=\operatorname{unique}(W_Z,w_Z)
\]

and:

\[
\forall i\in Q_Z:\qquad
d_{i,\rho}(F_i)=q(W_Z).
\]

It also checks coverage, payload bindings, source editions, codec editions and the selected representation boundary. Thus \(\beta\) is not “decode the first member”. A stale encoding remains a valid historical encoding if it still decodes on its historical domain, but it fails a currentness claim for \(W_Z\).

#### W.5.4 Reciprocal closure and normalisation

For declared domains \(D_W,D_Z\), semantic round-trip closure is:

\[
\beta_\rho(\alpha_\rho(W))=W
\qquad(W\in D_W).
\]

Raw material carriers may contain transport order, encryption randomness, timestamps or diagnostics outside semantic identity. A declared idempotent normalisation

\[
\nu_\rho:B_Z\to B_Z,
\qquad \nu_\rho\circ\nu_\rho=\nu_\rho
\]

removes or canonicalises only those fields. Assembly round-trip closure is therefore:

\[
\alpha_\rho(\beta_\rho(Z))=\nu_\rho(Z)
\qquad(Z\in D_Z).
\]

Exact raw equality is claimed only on the canonical subdomain where \(\nu_\rho(Z)=Z\). If normalisation removes material semantics, the result is a weaker projection claim, not exact reciprocal closure. Both maps must be defined on the named domains and land in their counterpart domains. Changing the semantic codec, layout or normalisation contract changes \(\rho\).

### W.6 Membership and participation

Membership changes are typed operations `join`, `leave`, `replace`, `split`, `merge` and `rebind_interface`. Each records old and new manifest editions, authority, causal cut, predecessor/successor occurrence relation, surviving and retired relations, state/history transfer, loss and new obligations. The mapping is not assumed bijective. Retired IDs cannot be reused without a new occurrence identity. Network absence does not prove withdrawal; lost payload availability does not change semantic membership.

Membership changes invalidate dependent coverage, closure, global-admission and current all-portions witnesses until rechecked.

Participation is reported independently:

| Kind | Requirement |
|---|---|
| `occurrence` | The occurrence belongs to the exact constitution |
| `relational` | Its admitted removal changes a protected relation |
| `functional` | Its admitted counterfactual removal changes a declared capability under equal resources and environment |
| `generative` | Its admitted behaviour can contribute to a successor whole |

Occurrence participation is deliberately weaker than functional necessity. Removal tests require an admitted reduced carrier or deletion operation. An inadmissible removal returns its obstruction rather than a fabricated comparison. Redundant constituents may all participate without each being necessary for one capability.

### W.7 Optional endogenous evolution — WPC-Evolution/0.1

#### W.7.1 Proposals and candidate successors

A proposal \(\delta\) records an immutable event identity, actor and authority binding, base whole edition, causal parents, affected occurrences and relations, read-set or preconditions, write-set or typed operation, membership effects, external inputs and intended invariants. Local, relational and whole-level initiation are separately typed; whole-level origin is not automatically privileged.

A joint proposal set \(\Delta\) retains event identity, shared choices, dependencies and order. Repeated references to one event do not create independent contributions. Define:

\[
\mathcal C_\rho(W,\Delta)=
\{W'\mid\mathsf{TransitionAdmitted}_\rho(W,\Delta,W')\}.
\]

The admission relation checks typing, causal completeness, authority, preconditions, membership, coverage, frame conditions for unaffected state, global constraints and history extension. Every proposal is accounted for as applied, rejected, deferred or unresolved. Reconciliation returns `unique_candidate`, `ambiguous_candidates`, `incompatible`, `pending_dependencies`, `precondition_conflict`, `unauthorised`, `unsupported`, `undetermined` or `resource_limit` with witnesses or obstruction records.

#### W.7.2 Commitment and refresh

\(\mathsf{Commit}_\rho\) publishes a candidate only under a declared selection and commitment protocol. Candidate uniqueness does not grant permission or prove physical enactment. A commit records predecessor editions, accepted, rejected and deferred events, witness bindings and the new immutable semantic whole.

After commitment, \(\mathsf{Refresh}_\rho\) produces required successor payloads:

\[
F_i'=e_{i,\rho'}(q'(W')).
\]

Refresh follows the committed semantic successor. It MUST NOT recompute \(W'\) from stale payloads and erase admitted local contributions. During refresh, semantic coherence of \(W'\), representation currentness of \(Z\), and operational availability are separate results.

#### W.7.3 Derived whole transformations

If reconciliation and selection are deterministic on a fixed admitted domain, they induce a partial transformation \(T_\Delta(W)=W'\). For sufficient shared input, an assembly transition \(\mathcal U\) satisfies:

\[
\mathcal U\circ\alpha_\rho
=\alpha_{\rho'}\circ T_\Delta,
\qquad
\beta_{\rho'}\circ\mathcal U
=T_\Delta\circ\beta_\rho.
\]

An isolated portion cannot acquire an unreceived remote event through a commutation law. Its local update must take the required messages, shared parameters or unresolved variables as explicit inputs:

\[
U_i(F_i,\Delta_{\mathrm{needed}},\xi_i)
=e_i'(T_\Delta(W)).
\]

Membership-changing transitions use predecessor/successor occurrence relations rather than a fixed-index product.

### W.8 Optional distributed operation — WPC-Distributed/0.1

An implementation distinguishes:

1. `semantic_coherent(W)`: the committed whole satisfies its constitutive contract;
2. `representation_coherent(Z,W)`: the assembly satisfies its selected closure and currentness conditions;
3. `operationally_available(Z,action)`: the deployment can currently perform a specified authorised action.

No predicate implies the next. A coherent whole may have stale replicas; an agreeing assembly may be unavailable; a stale assembly may remain valid for an explicitly historical query.

Every distributed implementation declares its consistency and commitment model, message assumptions, fault model, duplicate handling, freshness policy and recovery procedure. `coherence_pending` does not promise termination. Safety and liveness require separate assumptions and evidence.

Required event disciplines include:

- identical event ID and payload: deduplicate under the declared replay rule;
- identical event ID and different payload: equivocation conflict;
- missing causal parent: pending or rejection, not invented order;
- stale base or read-set: witnessed rebase, explicit reconciliation or rejection;
- competing writes: preserve alternatives unless an authorised policy resolves them;
- independent writes: commute only when disjointness and global admission justify it;
- failed delivery: unknown or pending delivery, not assumed rollback;
- rollback: a recorded compensating or restoring transition, not deleted history.

The retained history \(H\) is a finite event DAG or ordered history with declared semantics. Equal endpoints need not have equal history-sensitive identity. Wall-clock time alone does not settle causation. A snapshot uses a declared causally coherent cut, not universal simultaneity.

### W.9 Extension, continuity, nesting and environment

New values, relations, occurrences or capabilities already supported by the signature may form an admitted \(W'\). Growth beyond an old signature or representation scope is recorded as:

\[
\mathsf{Extends}(W,W^+,m),
\]

with the new signature, migration map, preserved obligations, introduced state, losses and authority. If an old projection discards new material semantic state, old exact closure fails. A recoverable residual requires a typed law:

\[
\mathsf{Recover}_\rho(p(W^+),r)=W^+.
\]

Without that law, retaining a residual does not prove exact recovery.

Continuing identity uses a named `Continues` criterion over lineage, preserved contracts, history and membership mapping. Exact edition identity and inquiry-relative continuity remain distinct. Splits and merges may produce multiple predecessors or successors.

A whole may participate as one component of a higher-rank whole. A boundary adapter declares what the parent sees, what the child retains, how child changes invalidate parent witnesses and whether history cuts are compatible. A child's reconstruction capability does not imply reconstruction of its parent or siblings. Shared occurrences across wholes retain one declared state binding or an explicit bridge; they are not silently duplicated into independent choices.

Environment interfaces record external inputs, outputs and dependencies. “Endogenous” means initiated within the selected model boundary, not causally closed. External observation, randomness and human choice become recorded inputs or unresolved alternatives when they affect a result.

Encoding, decoding, reading, proposing, deciding, committing and executing are separate permissions under inherited E7G-T access discipline. Whole-bearing payloads may increase disclosure and storage risk. A restricted view is not confidentiality against an actor who can read the underlying payload. External decryption keys belong to the decoding-environment declaration. Revocation does not retroactively erase copies already possessed.

### W.10 Capability and result record

WPC/0.2 does not compress independent properties into a single coherence level. A conforming claim contains at least:

```yaml
WholePartClaim:
  profile: WPC/0.2-proposed
  model_edition: required
  whole_lineage: required
  whole_edition: required
  source_scope: required
  boundary_and_cut: required
  manifest_edition: required
  capabilities:
    coverage: complete | incomplete | unknown | not_applicable
    constitution: unique | ambiguous | incompatible | undetermined | unsupported
    retention_by_occurrence: {}
    expression: checked | failed | unsupported | not_applicable
    global_admission: checked | failed | undetermined | unsupported
    reciprocal_closure: exact | normalised | relative | failed | not_claimed
    evolution: checked | pending | conflict | unsupported | not_claimed
    distributed_operation: checked | pending | conflict | unsupported | not_claimed
    availability: action_specific
  commitment_status: candidate | committed | rejected | pending | not_applicable
  witness_refs: []
  authority_refs: []
  unresolved_obligations: []
  admitted_use: []
  blocked_use: []
```

This field inventory is normative as to distinctions, but it is not yet a normative interchange schema. A future schema must define types, enumerations, references, canonicalisation and cross-field constraints. Witnesses bind all relevant input editions, profile, codec, predicate and solver versions, scope, causal cut, result and validation method. They distinguish instance tests, exhaustive finite-domain validation and universal proof.

Legacy WPC/0.1 WC0–WC4 results retain their original meanings. A WPC/0.2 claim MAY expose a legacy projection only if every obligation of the named old level passes on its pinned old scope.

### W.11 Proposed core laws

| ID | Law |
|---|---|
| WP1 | Constitution, encoding, decoding, expression, reconciliation, commitment and execution are separately typed |
| WP2 | Completeness is relative to a versioned coverage contract; omissions and unknowns remain visible |
| WP3 | Occurrence identity, local semantic state and payload identity are distinct |
| WP4 | Material local state, multi-way relations, shared dependencies and retained history participate in constitution |
| WP5 | Pairwise checks imply global admission only under a proved or exhaustively validated sufficiency result |
| WP6 | Constitution alone establishes no SR tier; SR4 retains its exact left-inverse, injectivity, capacity and scope obligations |
| WP7 | Reciprocal reconstruction proceeds through \(\epsilon:Z\to A\), unique constitution and required payload agreement |
| WP8 | Exact reciprocal closure holds only on declared domains; raw assembly closure is mediated by declared normalisation \(\nu\) |
| WP9 | A state-changing local expression produces a typed proposal or event rather than a hidden mutation |
| WP10 | Admitted local and relational proposals may generate candidates without a pre-supplied whole transformation |
| WP11 | Unique candidacy supplies neither authority, commitment, enactment nor execution evidence |
| WP12 | No proposal is silently dropped, repaired or selected during reconciliation |
| WP13 | Refreshed payloads follow the committed semantic successor; stale payloads remain historical rather than overwriting current local state |
| WP14 | Membership, rule, scope and representation changes are typed transitions and invalidate dependent witnesses until rechecked |
| WP15 | Semantic coherence, representation currentness, operational availability and liveness are independent claims |
| WP16 | Exact endpoint equality does not imply equal history, causation or audit effect |
| WP17 | Legitimate richer state is preserved under a new admitted scope rather than forced into lossy old closure |
| WP18 | Lineage, exact edition and inquiry-relative continuity are distinct |
| WP19 | Finite relation cycles do not license cyclic quotation or infinitely nested self-encoding |
| WP20 | Reconstruction grants neither execution nor access authority and does not instantiate the described system |

### W.12 Minimum conformance programme

An implementation claiming the corresponding capability MUST include positive and negative cases for:

- exact coverage and missing, extra, duplicated or unavailable occurrences;
- unique, ambiguous, incompatible, undetermined and unsupported constitution;
- equal payload values attached to distinct occurrences;
- constitutive coherence with no encoding and therefore no inferred SR tier;
- exact and relative reconstruction without tier promotion;
- local semantic state conflicting with an encoded snapshot;
- pairwise-pass/global-fail admission;
- exact semantic round trip and canonical or normalised assembly round trip;
- read-only expression and state-changing expression producing an explicit proposal;
- stale payload remaining historically valid but failing currentness;
- authorised and unauthorised membership changes;
- same endpoint with different retained histories;
- rejected cyclic self-embedding;
- explicit resource and solver stops without fabricated success.

Evolution conformance additionally covers bottom-up disjoint changes, conflicting writes, replay, equivocation, stale bases, missing dependencies, authorised commitment, refresh after commitment and membership changes. Distributed conformance additionally covers partial delivery, mixed editions, declared consistency behaviour, safety/liveness separation and action-specific availability.

### W.13 Bounded reciprocal construction

The reviewed WPC/0.2 proposal supplies a finite allocation model with occurrences A, B and C, integer local allocations 0–2, a global budget of two, explicit immutable events, fixed-authority local proposals, canonical JSON whole encodings and membership transitions.

Starting with \((0,0,0)\), A and B independently propose local values of one. Reconciliation preserves both disjoint events and admits the successor \((1,1,0)\). If C also proposes one, every pair satisfies the budget but the three-way candidate violates the global constraint. The model rejects the all-applied candidate rather than dropping an event.

Canonical materialisation stores each occurrence's current local value and one exact encoding of the semantic snapshot. Strict reconstruction constitutes the whole from actual local states, decodes every required payload and rejects a stale or conflicting encoding. Membership departure creates a new manifest and semantic edition; loss of a payload alone does not remove a member.

The proposal-extracted Python example was run under Python 3.12.14 and passed 34 named checks. It exhaustively enumerated ten initial fixed-membership allocation wholes, established distinct canonical encodings for those ten, checked both closure laws on their canonical materialisations and performed 30 exact portion round trips. The proposal-extracted code SHA-256 was `b74710ee3f8f0decec2efa350eb26df76b599ba6feb2ef18052bc8daa0d28e66`.

The versioned package adapts that example only by adding module metadata and the v0.13 profile identifier. Its reference model is `E7G-T_WPC_v0.2_Reference_Model.py`, SHA-256 `5fe2e8d5f913f92ad8fbd0575607f569cbd211b13970174d537a9af14a493ea3`. The standard-library wrapper `test_e7gt_wpc_v0_2.py`, SHA-256 `9af439dfeb6502a80a72112838a6a3476b0b008625f6c6975872c7258b5e4e43`, independently invokes the model within the same first-party package and passes four test cases. These are reproducibility aids, not independent validation.

This validates only the stated finite in-memory subset. It does not implement general ambiguous constitution, arbitrary histories, expression operations, relative reconstruction, split/merge, rule evolution, distributed commitment, general solvers or every conformance case above.

### W.14 Promotion boundary

Promotion requires:

1. review of the \(A/W/Z\) sorts, extraction map, constitution outcomes and normalised closure laws;
2. a normative interchange schema for `WholePartClaim` and the selected modules;
3. bounded implementations for every capability claimed by the release;
4. positive and negative conformance results mapped to those capabilities;
5. independent reproduction and review;
6. at least one end-to-end application demonstrating value beyond a simpler snapshot, state-machine or distributed-log baseline.

Until those conditions pass, WPC/0.2 and its optional modules remain experimental draft profiles. The central discipline is reciprocal but bounded: the whole is constituted rather than merely copied; a constituent participates rather than merely depicts; change is reconciled rather than assumed; and every reconstruction or completeness claim names its scope, edition, boundary and evidence.

