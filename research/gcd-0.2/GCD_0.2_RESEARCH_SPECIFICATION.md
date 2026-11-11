---
title: E7G-T Generative Choice and Differentiation — GCD/0.2
edition: GCD/0.2-research
model: GCD-B1/0.2
status: Isolated mathematical research specification; not canonical or merged
pinned_base: E7G-T v0.15-experimental-MSC1 (2026-09-25)
predecessor: GCD/0.1 research amendment proposal
language: British English
---

# GCD/0.2 — Generative Choice and Differentiation

## 0. Constitutional, mathematical and use boundary

GCD/0.2 is a **separately versioned, optional research profile** examining (i) constituted semantic distinctions, (ii) expansive generation of admitted alternatives, (iii) explicit selection within an admitted possibility family, and (iv) authorised successor commitment as a distinct capability. Selecting GCD/0.2 imposes no obligation on ordinary E7G-T v0.15 users or existing EEC-Q, SF, CFS, RGP, WPC, REC, MSC or UC5 implementations. **Nothing here amends E7G-T v0.15, changes existing product pins or constitutes a conformance claim to the complete v0.15 kernel.**

The formal claims below are conditional on declared carriers, signatures, admission predicates, equivalence criteria, maps, editions and implementation limits. A formally constituted distinction is a distinction in a *model's semantic identity*, not proof of an external ontological creation. A witnessed choice occurrence is a checked model record, not proof of a human mental event, authenticated actor, spontaneous freedom or a physically executed transition.

The motivating interpretation of the *Law of One* is isolated in `PHILOSOPHICAL_PROVENANCE.md`, outside all definitions and axioms. The interpretation is not assumed to be a correct reading of the source, and no source-text verification is claimed.

## 1. Typed vocabulary and exact boundaries

The abstract proposal uses the following separately typed values:

| Sort | Contract | Must not be confused with |
|---|---|---|
| `Signature[Σ]` | Versioned structural kinds, relations, identity, admission and bridge contracts | Observation policy, display vocabulary |
| `Config[Σ]` | One admitted, canonically identifiable semantic configuration | Source object, view or enacted world state |
| `Family[Σ]` | Versioned finite *description* of admitted possibilities and common dependency identities | EEC-Q formal sum, realised member |
| `ComparisonCarrier[Σ]` | Pinned subset and comparison predicates on which a refinement/novelty claim is checked | Unbounded universe |
| `GroundBridge[Τ→Σ]` | Typed information-forgetting map with declared domain and losses | Reversible identification |
| `EmbedBridge[Σ→Τ]` | Typed preservation embedding, with required left-inverse law where claimed | General inverse to grounding |
| `SemanticDiffWitness[Σ,Τ]` | Material semantic extension, strict refinement and source-relationship witness | Better access to an unchanged structure |
| `AccessDiffWitness[Σ]` | New discrimination from observation or display policy at unchanged semantic signature | Constitution |
| `GenRule[Σ→Τ]` | Registered finite generator, typed domain, parameters and version | Unrestricted string evaluation |
| `GenResult[Τ]` | New family edition, preserved/lost/new alternatives, criterion-relative witness | Unrecorded overwrite |
| `ChosenDescription[Σ]` | Selected admitted configuration tied to a family edition and a choice act | SF `realise`, commitment or physical enactment |
| `ChoiceAct[Σ]` | Immutable *logical* occurrence, basis, provenance, claimed actor/authority and membership witness | Authentication or subjective freedom |
| `SeedAdapter[Σ]` | Explicit conversion of selected configuration into a new singleton family | Implicit type coercion |
| `RealisationEvent[Σ]` | Modelled transition record under a separately declared commit protocol | External effect without an execution bridge |
| `GenerationLayer[r]` | Finite-rank layer with typed parent binding | D-role, temporal role, infinite actual structure |

The executable `GCD-B1/0.2` uses finite enumerated families, immutable Python `dataclass` envelopes and canonical JSON records. Serialised JSON dictionaries remain mutable in memory: replay detects edits of an existing witness and invalid results, but **content hashes alone do not authenticate the claimed actor or prevent re-authoring**.

### 1.1 Outcome discipline

All operations return a distinct typed outcome. The bounded evaluator uses `constitutive_refinement`, `access_refinement_only`, `expansive_within_signature`, `expansive_signature_generation`, `non_expansive`, `selected`, `seeded_singleton_family`, `model_committed`, `unresolved`, `not_established`, `rejected`, `rejected_nonmember`, `domain_error`, `unauthorised`, `unsupported`, `invalid_input` and `resource_limit`, where appropriate. A non-expansive generation is neither a malformed input nor evidence that the source family is empty. The actual enum is operation-specific. No outcome is EEC-Q zero or physical realisation.

## 2. Constitutive semantic differentiation versus access refinement (review findings A, B)

Let `g: B_Τ ⇀ B_Σ` be a declared grounding map. For a **finite, explicitly identified comparison carrier** `X ⊆ B_Τ`, define:

\[
 x \approx_0 y \iff g(x)=g(y), \qquad
 x \approx_1 y \iff x =_{Τ} y.
\]

A **strict refinement witness** requires both:

\[
 \forall x,y\in X:\ (x\approx_1 y\Rightarrow x\approx_0 y),
\quad \exists x,y\in X:\ x\approx_0 y\land x\not\approx_1 y.
\]

The first statement preserves prior distinguishability; the second exhibits a grounded fibre split. These conditions alone are insufficient to certify constitution. A **constitutive semantic differentiation claim** additionally requires:

1. distinct pinned semantic signature editions `Σ` and `Τ` with a registered compatible extension (or a registered identity-bearing semantic amendment), not merely a changed observer;
2. one *material* target semantic property, entity kind or relation whose differing values enter the `Config[Τ]` identity and admission contract;
3. the extension's domain, newly introduced kinds and rules, grounding/embedding bindings and losses;
4. an admitted `X`, exact pair witness, full pair-law check in the bounded model, and proof that a target semantic distinction **does not factor through** `g` on the witnessing pair;
5. provenance of the source and target family editions and no claim that the semantic change occurred outside the model.

**Non-factorisation test.** A new target property `p` cannot be recovered solely from the previous coarse structure if `g(x)=g(y)` but `p(x)≠p(y)`. Then no function `q` on the coarse image satisfies `p=q∘g` on both `x` and `y`. This formalises *relative* semantic novelty; it does not establish ontological origin.

`DifferentiateFamily : Family[Σ] × Family[Τ] × ComparisonCarrier[Τ] → DiffResult` is the primary operation. Every comparison target must ground into the supplied source family's admitted set. A proposed single-config `DifferentiateConfig` can return a constructed config, but must reference a sufficient comparison family and does **not** by itself certify strict refinement. The reference evaluator intentionally implements only the family-level version.

An **access refinement** changes the observation functions or privileges over a fixed signature and semantic configuration. Its induced equivalence can become finer, but its correct type remains `AccessDiffWitness[Σ]`; it does not satisfy constitutive differentiation even if its partition changes identically.

## 3. Two kinds of expansive generation (findings C and additional signature requirement)

### 3.1 Common criterion-relative law

Let `H` be a source family, `H'` an output family, `ι` an explicitly registered embedding into the output signature, and `≈_Q` a pinned target-side equivalence criterion. A claim of **expansive generation at criterion Q** requires:

\[
 \iota(\llbracket H\rrbracket)\subseteq\llbracket H'\rrbracket
\]

and

\[
 \exists z\in\llbracket H'\rrbracket:\ 
 \forall h\in\llbracket H\rrbracket,\ z\not\approx_Q\iota(h).
\]

The generator must also register its domain, semantics, rule and parameter editions, shared dependence, exact identities and a replayable preservation/novelty witness. Renaming, cosmetic changes, dropping previous options and adding a target exactly equivalent at `Q` cannot satisfy this expansive class. A generating rule that replaces or contracts a family can be reported separately as **non-expansive**, but must not be relabelled expansive.

The finite evaluator supports `Q=exact`, `Q=kind_set`, and `Q=root_only`. `kind_set` is an equivalence relation based on the set of admitted non-root semantic node kinds; `root_only` deliberately collapses every configuration in the carrier and serves as a counterexample. The comparison is target-signature-relative; exact identity and criterion equivalence are different claims.

### 3.2 Generation *within* an existing signature

`GenerateWithin_γ : Family[Σ] × Config[Σ] × Criterion[Σ] → GenResult[Σ]` uses the identity embedding. Its registered rule can construct additional configurations from existing semantic kinds and relations. The initial family is unchanged; the result is a new versioned family. In the reference model, `combine_approve_reject/v1` requires existing approval and rejection branches and creates a new `approve+reject` composite under the same signature `Σ1`. Novelty is criterion-relative, not just text-label difference.

### 3.3 Signature-generative extension

`GenerateSignature_γ : Family[Σ] × Extension[Σ→Τ] × Config[Τ] × Criterion[Τ] → GenResult[Τ]` requires a versioned registered extension of the structural vocabulary. It may introduce genuinely new **node or relation kinds**, not simply additional data values inside the old signature. The extension must state:

- the old and new semantic signatures and new kinds/relations;
- admission and identity procedures for the new sort;
- an embedding `ι : B_Σ → B_Τ` preserving all source alternatives and a grounding map `g : B_Τ → B_Σ` on the declared relevant domain;
- a checked `g∘ι=id` law on the source carrier, with non-invertibility of `g` allowed and recorded;
- a new admitted configuration that *exercises* a newly introduced structural kind/relation and is novel at `Q`;
- an admitted grounded predecessor for the new alternative, or an explicitly different provenance rule for a future model.

The reference model's `Σ1→Σ2` extension introduces the **new node kind** `evidence_gate` and **new relation kind** `requires`. It constructs `approve+evidence_gate` with `requires(A,E)`, which grounds to the earlier `approve` configuration. The grounded predecessor relationship is retained, while target exact identity distinguishes the two.

A new signature label alone, an unsupported kind, a missing required edge, or an extension that produces only old embedded configurations fails the stronger signature-generative claim.

## 4. Selective choice and act provenance (finding E)

`Choose_χ : Family[Σ] × (Candidate[Σ] | Policy[Σ]) × ChoiceContext × ChoiceOccurrence → ChoiceResult[Σ]`.

A successful selection requires exact membership `w∈⟦H⟧` under the versioned membership checker. The logical `ChoiceAct` records: occurrence ID, selected configuration, family content digest and edition, source dependency, context, supplied actor reference, mechanism (`supplied_input` or registered deterministic policy), policy edition, membership index and identity digest, and **separate** actor-authentication and authority statuses. Different act IDs remain different retained histories even when selected values coincide.

An immutable *semantic edition* of the source family is preserved. A choice neither deletes unchosen possibilities nor alters the modelled world. Unknown member, unprovided candidate, unsupported policy, absent authorisation and resource exhaustion are distinct statuses. The bounded model has exact finite membership, so no probabilistic, approximate or unknown-membership solver is claimed.

`Choose` is **not** SF/0.1 criterion-driven `realise` with its objective ordering and residual-family semantics. Selecting a generator rule itself is meaningful in the abstract profile but is not implemented in GCD-B1 (the finite evaluator uses two fixed registered generators). Subjective freedom cannot be inferred from either supplied or deterministic choice mechanisms.

**Provenance limitation:** a user-supplied `actor_ref` is an *assertion*, not independently authenticated identity. A replayable hash validates recomputation, not the historical fact that a particular person selected the value.

## 5. Explicit type adapters and operation order (finding D)

`ChosenDescription[Σ]` is **not** a `Family[Σ]` or a `Config[Σ]` committed into an external state. To generate from a selected value, invoke the registered, typed `SeedChosenFamily` adapter, whose output is a **new singleton family** with an explicit list of alternatives excluded *from the seeded family only*. The original family survives. The adapter also binds the source selection receipt, family edition and shared dependency identifier. There is no coercion from a view, phase, selected description, quotation or external instantiation.

Consequently, the meaningful order comparison is:

- `GenerateSignature(H) → Choose(H',w)`: the generated family still contains all previously admitted alternatives;
- `Choose(H,a) → SeedChosenFamily(a) → GenerateSignature(H_a)`: the seeded output contains the selected branch and generated descendants but explicitly lacks other original alternatives.

Both paths are well-typed, but their output **families** differ in the finite counterexample. A bare `Generate∘Choose` expression is ill-typed until an adapter is supplied. Evaluation compares source family, target family, selected output and history separately; no general commutation law is asserted.

Differentiation versus grounding is similarly non-invertible: `g(approve)=g(reject)=workflow` while the semantic descendants remain distinct. A display/view or coarse projection cannot silently recover the distinction. A future general proof of commuting projections requires registered diagrams, common domains and matched criteria.

## 6. Grounded recursion and finite extensibility

A generated configuration can retain its declared source through `GroundBridge[Τ→Σ]` and immutable provenance, without equating the differentiated target with its predecessor. In `GCD-B1`, the `Σ2` configuration with an evidence gate is distinct from its `Σ1` grounded approval path. An embedding of the old path into `Σ2` remains distinct from the evidence-gated target, while `ground(embed(x))=x` holds for every admitted old configuration.

A separate finite recursive construction rule has the schematic type:

\[
 L_0:\mathrm{GenerationLayer}[0],\qquad
 \mathsf{Lift}:\mathrm{GenerationLayer}[n]\longrightarrow\mathrm{GenerationLayer}[n+1].
\]

For every finite natural number `n`, the mathematical rule allows another typed successor when its domain is satisfied. It supplies **no fixed mathematical maximum rank** and no completed infinite hierarchy. The executable evaluator constructs a chain of rank and parent-digest bindings with a caller-declared finite `MAX_RANK=8` resource bound. These are *SR0-like lineage references only*, **not** self-contained SR4 quotations, complete parent payloads, higher-level agency or a general RGP runtime.

## 7. Bounded reference carrier — GCD-B1/0.2 (finding F)

### 7.1 Canonical node and relation grammar

The carrier fixes one root node `W:workflow` and optional distinct stage occurrences `A:approve`, `R:reject`, `E:evidence_gate`. An admitted stage has a mandatory `contains(W,stage)` edge; `E` is admitted only together with `A`, and then `requires(A,E)` is mandatory. There are no additional stage IDs, dangling edges, undeclared relations, arbitrary host-language expressions or alias-based identities. Sorted nodes and relations define exact canonical identity; the signature edition is part of configuration identity.

| Signature | Node kinds | Relation kinds | Entire admitted configuration carrier |
|---|---|---|---|
| `Σ0` / `gcd.workflow.s0` | `workflow` | none | `{W}` (1) |
| `Σ1` / `gcd.workflow.s1` | `workflow`, `approve`, `reject` | `contains` | `{W}`, `{W,A}`, `{W,R}`, `{W,A,R}` (4) |
| `Σ2` / `gcd.workflow.s2` | `workflow`, `approve`, `reject`, `evidence_gate` | `contains`, `requires` | four embedded `Σ1` configurations, plus `{W,A,E}` and `{W,A,R,E}` (6) |

The table abbreviates each configuration's mandatory relations. These are *all* admitted configurations for this named finite carrier. It does not define arbitrary workflow diagrams or general graph rewriting.

### 7.2 Exact refinement and grounding

`ground:Σ1→Σ0` removes optional stage kinds; `ground:Σ2→Σ1` removes `E` and its incident relations; composition gives `ground:Σ2→Σ0`. `embed` includes old nodes and relations unchanged into an explicitly newer signature. The exact finite carrier satisfies `ground(embed(c))=c` on every registered source configuration, but `embed(ground(c))=c` fails for a newly differentiated target.

For the first split, `x={W,A}` and `y={W,R}` ground to the same `{W}` but have different exact identity. The new property "semantic stage kind" cannot factor through grounding. The same-signature comparison where a display reveals or hides stage kinds is classified as **access refinement only**.

For the second split, `{W,A}` (embedded into `Σ2`) and `{W,A,E}` ground to the same source `{W,A}`; the new property "requires evidence" cannot factor through grounding. The new `E` kind and `requires` relation are semantically registered. The model does not assert that a real document review has acquired the gate.

### 7.3 Exact expansive generation

Within `Σ1`, start with `H={ {W,A}, {W,R} }` and generate `{W,A,R}`. Both earlier alternatives remain, and the new kind-set differs from either. For signature generation, embed this three-member family into `Σ2`, then add `{W,A,E}`. The output family has **four** alternatives; the new one grounds to an old approval alternative. All carry the same source dependency identifier and do not become statistically or logically independent by being printed in separate rows.

### 7.4 Exact choice and model-only transition

Choose `{W,A,E}` by a supplied candidate against the *four-member `Σ2` family*. Record the unchanged family edition, a membership witness and a separate act ID. As a distinct operation, `CommitModel` can perform a *simulated* transition in a controlled in-memory fixture if its replay-valid selection has a matching hard-coded model grant. Its record says `physical_or_external_effect=false`. The grant is not secret, signed or suitable for production security. Genuine WPC-Evolution commitment requires a separately implemented and authorised contract.

### 7.5 Closed finite-domain validation

The included test program exhaustively exercises all **11** admitted configurations across the three editions, the **24** combinations of stage presence against the three signatures, **88** ordered refinement-law pairs, **6** grounding-embedding source cases, all **16** subsets of the `Σ1` carrier and **64** subsets of the `Σ2` carrier for differentiation, **60** within-signature generator candidate pairs, **90** signature-generator candidate pairs, and **378** finite family/candidate membership pairs in `Σ2` (192 members, 186 non-members). Independent finite-run counts are recorded by the executable report rather than asserted as proof about unbounded models.

## 8. Deterministic receipts and replay

Each recorded operation has: fixed base/profile/model editions, the exact serialised request, its typed outcome, and a SHA-256 digest over canonical JSON of those fields. `verify_receipt` checks the digest **and independently re-executes the operation through registered constructors**, comparing the complete resulting record. A forged status with a recomputed digest fails because it does not match actual execution. Nested `CommitModel` receipts replay their selected-choice receipt before evaluating the model-only transition.

Replay is deterministic for fixed versioned code and finite inputs; it does not prove the input's source truth, actor identity, authenticity, external observation, domain appropriateness, independent implementation fidelity, or actual execution. Re-authoring a coherent input and recomputing its receipt is possible. A future security-sensitive deployment would need authenticated event origins, durable logging, anti-replay constraints and a real authorisation engine.

## 9. Conformance counterexamples

| Counterexample | Required classification |
|---|---|
| Change observation from root-only to kind visibility without changing semantic signature | `access_refinement_only` |
| Source/target have no strict pair under the grounding equivalence | `not_established` |
| Alternative is already present or equivalent under `Q` | `non_expansive`, not expansive |
| Add a renamed description of the same alternative | Not a novel semantic configuration |
| Attempt to use `evidence_gate` in `Σ1`, or `E` without `A` | `invalid_input` |
| Candidate fails generator's typed rule or source preconditions | `domain_error` |
| Attempt unregistered source/target signature operation | `unsupported` or `invalid_input` depending on boundary |
| Candidate absent from exact family | `rejected_nonmember` |
| No supplied candidate | `unresolved` |
| Choice act with no independent model grant | `unauthorised` upon attempted model commit |
| Reuse choice receipt against a different family edition | `rejected` |
| Change result in a receipt and recompute the digest | Replay rejection |
| Compare generate-then-choose with choose-then-seed-then-generate | Different family membership, explicit adapter loss |
| Exceed rank 8 in bounded evaluator | `resource_limit`, not mathematical impossibility |
| Infer external enactment from model-only commitment | Rejected claim; `physical_or_external_effect=false` |

## 10. Selected v0.15 alignment

The compatibility account is a separate file `COMPATIBILITY_MATRIX.md`. The relevant native provisions are SF/0.1 (§X.16) for finite descriptions of families, membership and distinct realisation; CFS/0.1 (§X.17) for shared parameter dependence; RGP/0.2 (§X.18) for registered generation, lineage and projection; WPC/0.2 (§X.19) for distinction between constitution, reconciliation and commitment; REC/0.1 (§X.20) for information-flow witnesses without truth certification; MSC/0.1 (§X.21) for scope and access/authority distinctions. UC5 supplies source/view, phase, provenance and bridge disciplines. GCD-B1 is a **separate hand-written adapter demonstration**, not a full adapter to any existing executable companion.

## 11. General laws, status and promotion obligations

The mathematical equations above are direct definitions or bounded propositions. Their significance is the enforced typed and witnessed separation, **not** a claim that strict refinement, embeddings, state-machine choices, operational semantics or event receipts are new mathematics. A complete profile will require a general carrier-independent operational definition of constitutive novelty, proof or stronger semantic modelling of signature extensions, general finite-family and symbolic-family identity, typed support for heterogeneous generators, cross-signature equivalence conditions, independent replay implementation, and an end-to-end consumer evaluated against a suitable simpler baseline.

**Current status: PROPOSED and INTERNALLY TESTED only for GCD-B1/0.2.** A passing bounded run is not independent formal review, universal proof, complete kernel alignment, demonstrated marketplace value or promotion. The unchanged canonical kernel remains `v0.15-experimental-MSC1`. Promotion requires independent mathematical review, external reproduction, stable interchange/schema review, more substantial application evidence, a migration record, and an explicit decision by the governing project.
