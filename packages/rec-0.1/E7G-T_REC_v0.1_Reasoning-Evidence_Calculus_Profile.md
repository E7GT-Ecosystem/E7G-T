---
title: "E7G-T REC/0.1 — Reasoning–Evidence Calculus"
profile: "REC/0.1-proposed"
revision: "REC1"
date: "2026-09-15"
kernel: "E7G-T v0.14-experimental-REC1-draft"
authors: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
status: "Experimental standalone companion draft; bounded executable subset"
reference_model: "REC-B1/0.1"
normativity: "MUST and MUST NOT apply only to implementations selecting REC/0.1 and the declared capability scope. The profile constrains information-flow reasoning; it does not establish truth, domain authority, empirical accuracy or improved AI performance."
---

# E7G-T REC/0.1 — Reasoning–Evidence Calculus

REC/0.1 supplies a small executable reasoning contract over typed claims, evidence, rules and queries. It fills a boundary left intentionally open by earlier E7G-T profiles: the inherited kernel explains what responsible reasoning should distinguish, while REC specifies a finite class of reasoning moves that can be replayed and checked.

REC is optional. An ordinary E7G-T analysis does not become a REC computation merely because it uses the vocabulary of context, evidence, projection, whole–part constitution or operational phase.

## C.0 Purpose and boundary

REC/0.1 is designed to prevent five recurrent failures:

1. unsupported text being presented as a derived conclusion;
2. conflicting evidence being silently collapsed;
3. a conclusion exceeding the semantic, temporal or jurisdictional scope of its premises;
4. one modality, such as possibility, being silently converted into another, such as fact or obligation;
5. a reasoning explanation being accepted without a replayable witness.

The profile does not determine whether imported evidence is factually correct. It does not replace retrieval, measurement, legal interpretation, scientific method, proof assistants, SMT solvers or domain review. A conforming result means only that the declared bounded information-flow computation satisfies this profile.

## C.1 Central judgement

For admitted evidence (E), background claims and rules (K), profile edition \(\rho\), claim (c), information status \(\sigma\) and witness (w), write:

\[
E;K\vdash_{\rho}c:\sigma\triangleright w.
\]

This means that the checker can reproduce status \(\sigma\) for (c) from the admitted envelope and verify (w). It does not mean that (c) is true outside the declared source, scope, time, semantics and rules.

The control dimensions are:

\[
\rho=\langle
\Sigma_C,\Sigma_E,\Sigma_R,
\mathsf{Adm},\mathsf{Current},
\mathsf{Scope},\mathsf{Modality},
\mathsf{Fire},\mathsf{Decide},
\mathsf{Canon},L
\rangle,
\]

where the signatures type claims, evidence and rules; the predicates govern admission and currentness; the policies govern scope, modality, rule firing and decision; `Canon` fixes deterministic encoding; and (L) declares resource limits.

## C.2 Claim, evidence, rule and query sorts

A claim is:

\[
c=\langle i,\varphi,M,C,I,T,S,D,P\rangle,
\]

where:

- (i) is an immutable occurrence identity;
- \(\varphi\) is proposition content in the declared language;
- (M) is modality;
- (C) is semantic context;
- (I) is inquiry;
- (T) is temporal scope;
- (S) is the declared applicability scope;
- (D) identifies dependencies;
- (P) records provenance and edition bindings.

Equal proposition strings do not merge claim occurrences. Conversely, different strings are not automatically different propositions; any semantic identification requires an explicit rule or domain adapter.

An evidence occurrence is:

\[
e=\langle j,i,p,s,v,g,S_e,T_e,P_e\rangle,
\]

where (j) is evidence identity, (i) the target claim, (p\in\{+,-\}) support or refutation polarity, (s) the source identity, (v) the source edition, (g) a provenance-dependence group, and (S_e,T_e,P_e) its scope, validity and provenance.

Polarity states what role the evidence plays under the selected interpretation. It is not an assertion that the evidence is correct or independent.

A rule is:

\[
r=\langle k,\{(i_m,q_m)\}_{m=1}^{n},(i_o,p_o),B,A\rangle,
\]

where (q_m\) requests a supported or refuted premise status, (p_o) supplies support or refutation to the conclusion, (B) is an optional typed modality bridge, and (A) records the bridge authority.

A query identifies one claim and one decision policy. Querying does not change the claim status.

## C.3 Four information statuses

For each claim (c), retain two independent evidence bits:

\[
\operatorname{bits}(c)=\langle s(c),r(c)\rangle\in\{0,1\}^{2},
\]

where (s(c)) records admitted support and (r(c)) admitted refutation. Define:

| Bits | REC status | Meaning |
|---|---|---|
| \(\langle0,0\rangle\) | `neither` | neither support nor refutation has been derived |
| \(\langle1,0\rangle\) | `supported` | support without refutation |
| \(\langle0,1\rangle\) | `refuted` | refutation without support |
| \(\langle1,1\rangle\) | `both` | support and refutation coexist |

These are information states rather than complete truth values. `Neither` is not false. `Both` is not permission to choose a preferred side. Contradiction is local:

\[
c:\mathsf{both}\not\vdash d
\]

for unrelated (d). A rule may use a supported or refuted bit even when the claim is `both`, but the resulting witness MUST retain the conflict and the reliance policy MUST NOT silently treat `both` as supported-only.

## C.4 Admission and currentness

Before inference, an implementation MUST validate:

- kernel, profile and model editions;
- unique occurrence identities;
- required claim, evidence, rule and query fields;
- referenced identities;
- admitted modalities and polarities;
- source and source-edition bindings;
- explicit provenance-dependence groups;
- scope coverage;
- time-zone-bearing timestamps and ordered validity intervals;
- resource limits.

Evidence outside its validity interval is `stale` for the current query. It MAY remain historically valid. A stale occurrence MUST NOT set a current support or refutation bit, and its identity MUST be exposed in the witness.

Copied or repeated evidence sharing one provenance group remains one dependence group. REC/0.1 does not infer statistical independence from source count.

## C.5 Inference closure

Let (b_0(c)) contain the bits supplied by current admitted evidence. For a finite rule set, rules fire in canonical rule-identity order until a fixed point is reached:

\[
b_{n+1}=F_{\rho}(b_n),\qquad
b^{*}=F_{\rho}(b^{*}).
\]

Each rule fires at most once in REC-B1/0.1. Firing adds a bit; it does not erase an existing bit. The finite reference model therefore terminates.

Every application MUST record the rule identity, premises, required premise bits and conclusion polarity. An unstated natural-language inference is not a REC derivation.

REC-B1 does not implement quantification, negation parsing, defeasible priority, probabilistic inference, default logic, higher-order rules or arbitrary host-language predicates.

## C.6 Scope and temporal safety

Write (S_o\preceq S_i) when the output scope preserves every coordinate fixed by the input scope and may add further narrowing coordinates. A rule is scope-safe only if:

\[
\forall m,\quad S_o\preceq S_{i_m}.
\]

A conclusion MUST NOT drop a jurisdiction, document, population, role, configuration, source or other scope coordinate fixed by a premise. Generalisation requires an explicit separately validated bridge outside REC-B1.

The bounded model admits a temporal rule only when the output temporal scope equals every non-`any` input temporal scope. Temporal projection, interpolation, prediction and generalisation require separately declared rules and validation.

## C.7 Modality safety

The base modality set is:

\[
\{\mathsf{fact},\mathsf{obligation},\mathsf{permission},
\mathsf{prohibition},\mathsf{possibility},
\mathsf{prediction},\mathsf{recommendation}\}.
\]

If a conclusion modality does not occur among its premises, the rule MUST include a modality bridge identifying:

- the exact source modalities;
- the output modality;
- the authority or policy licensing the change.

An explicit bridge makes the transformation inspectable; it does not prove that the authority is legitimate or the rule is domain-correct.

## C.8 Decision and abstention

REC distinguishes status calculation from action policy. REC-B1 defines:

| Query policy | Status | Next action |
|---|---|---|
| `report` | any | `report_status` |
| `rely_if_supported_only` | `supported` | `rely_within_declared_scope` |
| `rely_if_supported_only` | `refuted` | `do_not_rely` |
| `rely_if_supported_only` | `both` | `resolve_conflict_or_abstain` |
| `rely_if_supported_only` | `neither` | `seek_evidence_or_abstain` |

No recommendation, execution, external message, authority decision or material action follows merely from status computation.

## C.9 Canonical witness

A conforming witness MUST include:

- kernel, profile, model, reasoning identity and edition;
- query time and exact envelope digest;
- every claim status;
- query status, policy and next action;
- admitted and stale evidence identities;
- evidence identities and provenance groups per claim;
- every fired rule application;
- every conflict;
- unsupported or resource-limited steps;
- query scope, temporal scope and modality;
- canonical witness digest.

The witness hash binds bytes but does not establish correctness. A checker MUST replay the admitted evidence and rule closure rather than accepting a self-consistent hash alone.

## C.10 Required operations

The conceptual REC operation registry contains:

| Operation | REC-B1 disposition |
|---|---|
| `Admit` | implemented for the bounded envelope |
| `Support` | implemented as positive evidence or derived bit |
| `Refute` | implemented as negative evidence or derived bit |
| `Derive` | implemented for finite monotone rules |
| `Project` | represented by explicit scope narrowing; general projection unsupported |
| `Compose` | fixed-point combination of admitted evidence and rules; rich semantic composition unsupported |
| `Conflict` | implemented as `both` without explosion |
| `Revise` | represented by a new envelope edition and deterministic replay; minimal-change belief revision unsupported |
| `Decide` | implemented for two bounded query policies |
| `Abstain` | implemented through explicit next actions |

## C.11 Relationship to other E7G-T profiles

- The inherited constitutional core supplies context, inquiry, projection, evidence, temporal and operational-phase distinctions. REC makes a bounded subset executable without promoting every informative pilot into the constitutional core.
- EEC-Q coefficients remain exact formal-combination coefficients. They MUST NOT be reinterpreted as confidence, belief or evidence weight.
- SF and CFS may describe families of claims or reasoning envelopes only through explicit adapters that retain their profile meanings.
- RGP may host, project or encode REC objects, but hosting is not inference and decoding is not validation.
- WPC may constitute a versioned reasoning whole from claims, evidence, rules and history. WPC-Evolution may model proposed updates and commitment. REC status computation remains distinct from WPC constitution and commitment.
- E7Q remains independently versioned. Any connection requires an explicit adapter and does not turn REC information statuses into quantum states or measurement results.

## C.12 Conformance

A REC/0.1 implementation MUST publish a capability vector and conformance matrix. Minimum positive and negative cases include:

1. all four information statuses;
2. contradiction retention without unrelated derivation;
3. deterministic fixed-point replay;
4. explicit evidence and source-edition binding;
5. stale and future evidence exclusion from current status;
6. provenance-group retention without inferred independence;
7. rule identity and application recording;
8. scope narrowing acceptance and scope expansion rejection;
9. temporal-scope change rejection;
10. modality change rejection without a bridge;
11. explicit modality-bridge admission;
12. reliance refusal for `both`, `refuted` and `neither`;
13. envelope digest verification;
14. witness digest verification;
15. rejection of re-signed forged statuses, conflicts, stale lists and rule traces;
16. deterministic failure on malformed references and duplicate identities.

Conformance to the bounded model does not establish source truth, inference-rule soundness for an external domain, completeness, independent validation or improved AI performance.

## C.13 Promotion gate

Promotion beyond experimental draft requires:

1. review of the claim, evidence, rule, scope, modality and status semantics;
2. a normative stable interchange schema;
3. an independently implemented checker;
4. positive and negative conformance suites;
5. a real domain adapter with expert-reviewed rules;
6. comparison of ordinary prompting, checklist prompting, retrieval alone and retrieval plus REC enforcement using the same underlying model and sources;
7. reported accuracy, unsupported-claim, scope-error, conflict-retention, abstention, latency and cost results;
8. independent reproduction.

Until those conditions pass, REC/0.1 is an executable reasoning-audit proposal, not evidence that E7G-T improves an AI's intelligence, knowledge or truthfulness.
