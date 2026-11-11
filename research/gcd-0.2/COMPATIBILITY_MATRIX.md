# GCD/0.2 — E7G-T v0.15 compatibility and migration matrix

**Research-only alignment report.** Base pinned to `E7G-T v0.15-experimental-MSC1`; GCD has its own `GCD/0.2-research` and `GCD-B1/0.2` identifiers. Existing source, product, profile and operating-kernel pins are unchanged. The supplied E7G-T Ecosystem Operating Kernel v0.2 remains edition-pinned to the earlier v0.12 source in its own front matter; this report does not silently rewrite it to v0.15.

| Existing v0.15 source/profile | Contract held by that source | GCD/0.2 relationship | Disposition / limitation |
|---|---|---|---|
| Constitutional UC5, Part II | Entity versus description, view versus transformation, structural changes, history, bridge, authority and permissible use | Strict separation of semantic constitution from access/view; different source and target editions with explicit provenance | **Compatible by design** on bounded carrier; UC5 is not redefined |
| EEC-Q/0.1, §X.2–X.7 | Exact finite signed rational formal combinations; distinct basis identity, projection, restriction, quote, cancellation | Config identity is exact; GCD finite families have **set membership**, not EEC coefficients | **Not adopted** in evaluator; no coefficient bridge; no probability, physical amplitude or zero conflation |
| SF/0.1, §X.16 | Finite family description, admission, membership, criteria-based lexicographic `realise`, residual family | GCD uses explicit versioned finite set families with membership; `Choose` records supplied/policy selection, not objective `realise` | **Partial conceptual adapter only**; no live IC/0.1 solver or SF interchange adapter |
| CFS/0.1, §X.17 | SF outside/EEC inside; pointwise dependence, no invented independence | `dependency_id` preserved through generation and selection; no CFS combination is executed | **Deferred** for implementation; basic shared-source identity checked, not general joint-state algebra |
| RGP/0.2, §X.18 | Registered generation, typed layers, source retention, lineage, projection/encoding distinctions, finite ranks | Versioned generation and `ground/embed`; finite rank/parent links; result carries generator edition | **Partial research mapping**; rank chain is SR0-like pointer lineage, not SR4 quotation, RGP conformance or arbitrary layer engine |
| WPC/0.2, §X.19 | Constitution/representation distinct from authorised reconciliation, commitment, refresh and external enactment | `Choose` changes no material state; separate `CommitModel` tests a hard-coded in-memory fixture | **No WPC capability claimed**; no WPC constitution/coverage, authority service, refresh or real execution |
| WPC-Evolution/0.1, §W.7 | Typed proposals, causal parents, preconditions, authority and commitment | Model-only transition has distinct event and epoch from choice | **Not implemented**; no permitted WPC-Evolution commit adapter |
| REC/0.1, §X.20 | Versioned claim, evidence, information status, provenance groups, scoped replay and reliance | SHA-256 receipts plus deterministic evaluator recomputation; no source-truth or actor authentication | **Independent local receipt format**, not REC-B1 evidence calculus or REC conformance |
| MSC/0.1, §X.21 | Carrier-relative compatible scopes, access quotient, reconstruction fibres, no inherited decision authority | Access refinement not constitution; grounding fibres retain ambiguity; higher scope is not higher authority | **Compatible distinctions**, no MSC-B1 closure or general multi-scope adapter |
| E7Q / E7Q-IR | Independently versioned quantum evidence and IR work | No physical quantum claims or use of coefficients as amplitudes | **Deferred**; no changes or dependency |
| E7 Boundary | Product-local access and authority enforcement | Act record separates claimed identity from model fixture grant | **Conceptual reuse possibility**, not an integrated security mechanism |
| E7DB / E7FS / E2CI | Evidence storage, provenance, assurance | Research-use records could be stored or audited through future adapters | **Not implemented**; no product conformance or performance claim |

## Explicit boundaries preserved

1. `GCD Family` is not `EEC State`. No signed cancellation, generic probability or amplitude interpretation occurs.
2. `GCD Choose` is not `SF realise`; a successful member selection does not resolve an optimisation objective or residual family.
3. `Ground` is not a source-preserving `View`, an SR4 decoder, or a general invertible projection. The `Σ2→Σ1` bridge has non-singleton fibres.
4. New signature kinds are not merely RGP hosted items; generation is a versioned, typed operation with an admitted source and target.
5. Witness receipts are computed and replayed locally; they are not domain truth, cryptographic authentication, external actor evidence or independent verification.
6. A model-only commitment is not WPC-Evolution acceptance, production authorisation or an externally performed transition.
7. `GenerationLayer` rank is not a D0–D7 dimension, temporal role, completed infinity or ontological hierarchy.

## Migration classification

| Existing implementation surface | Retain/adapt/replace/retire | Decision |
|---|---|---|
| E7G-T v0.15 canonical document | **RETAIN, unchanged** | No canonical amendment |
| E7G-T ecosystem operating kernels | **RETAIN, unchanged** | Existing version pins remain as authored |
| All existing E7 product code and schemas | **RETAIN, unchanged** | No transitive profile obligations |
| GCD/0.1 proposal | **RETAIN as historical research input** | GCD/0.2 is a separate successor research artifact |
| GCD-B1/0.2 evaluator | **NEW isolated module** | No import of, or integration into, pinned companion executables |
| SF/CFS/RGP/WPC/MSC production adapters | **DEFER** | Require a separately reviewed, edition-pinned interface |

**Review trigger:** an independent mathematical objection, failed replay, new material counterexample, a consumer needing an unsupported signature/sort, or a request for canonical promotion.
