# E7G-T v0.15 quantum-view reuse and gap audit

**Status:** draft research note for exact-head mathematical and physics review. It proposes no canonical edit, profile registration, E7Q adoption, or physical claim.

## Scope, provenance and pins

The motivating question is whether E7G-T's whole/view/reconstruction machinery can describe context-dependent quantum observations and their limits. The remembered tetrahedron image is a prompt for mathematics, not a verified quotation, physical ontology, or claim that exact position and momentum are jointly readable.

- E7G-T source edition: `E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md`, revision MSC1, SHA-256 `5b1e9913cf24b80612f81014b8cc7efc7574d43402a2a188a17daa096c0c621a`; release manifest baseline `86653557f5b5780a984f3a2dab226213ebbe3702`. At public `main` `5b5cb5f10ddd913df66f5d9f65fbe059a2e33193`, v0.15 is the canonical experimental source for new E7G-T specifications. This source status does not establish implementation fidelity or completion of the calculus; those gates remain open.
- E7Q `main`: `86447771544e836222847ed04b0236cc27f2881b`; merged scope #78 is `docs/e7q-ir/SECOND_PRODUCT_JOINT_PILOT_SCOPE.md`. The current #79 review branch is `140608632a8fe8883b87a45e23a85259a42783e6`; it concerns formal rational Joint-to-Q-A1 mapping and is not quantum semantics.
- E7C evidence is a separate research lane. At the inspected E7G-T public main, `research/e7c-0.1/E7C_0.1_CURRENT_STATE.md` records bounded work only. None of that closes Python/IR-to-Lean adequacy or supplies quantum semantics.

## Glossary

| Term | Meaning here |
|---|---|
| Whole (operational) | A density operator `rho` on a declared Hilbert space, with preparation domain and model edition. It determines Born outcome distributions for declared POVMs. |
| Whole (additional ontology) | Optional hidden-variable or other enriched state `lambda`; a separate hypothesis with explicit preparation and response rules. It is not silently identified with `rho`. |
| Description | A record or mathematical representation of a state; multiple descriptions may denote the same state only under a declared relation. |
| Context/view | A declared measurement procedure and its outcome carrier, returning a distribution, an actual run record, or a state transition as separately typed objects. |
| Projection/view | Existing E7G-T operation retaining its source reference and declaring what is hidden; not automatically a physical measurement. |
| Outcome distribution | `p(o|rho,c) = tr(rho E[c,o])`, predicted by a state and POVM. It is not an actual outcome. |
| Actual outcome | The recorded result of one identified physical run, imported with protocol and provenance. The Born distribution does not specify which result that run produced. |
| Post-measurement state | Instrument-conditioned state after an actual measurement outcome; distinct from both distribution and record. |
| Compatibility | Here, operational joint measurability: existence of one parent POVM whose coarse-grained marginals are the declared POVMs for every admitted state. |
| Reconstruction fibre | All admitted preparations compatible with a declared view under a pinned comparison criterion. A singleton means unique within that model/domain only. |
| Evidence | Replay/provenance can establish what declared computation was performed; it does not establish physical validity or truth of the preparation/model. |

## Source map and dispositions

Labels: `reuse` means the existing general construct applies unchanged; `adapter-specific quantum semantics` means a typed quantum interpretation is required; `missing general law` means a substrate-neutral rule appears absent (none is established in this audit); `does not map` means the tempting identification is unsound.

| Source | Candidate construct | Disposition and exact boundary |
|---|---|---|
| v0.15 §§X.6.1, X.6.4; inherited UC5 §§6.6–6.8 | Source-preserving view vs identify/restrict | `reuse` for retaining source identity and explicit preservation/loss. A quantum context's Born map is `adapter-specific quantum semantics`; it is not automatically `Identify` or `Restrict`. A displayed outcome law does not replace `rho`. |
| v0.15 §§X.6.2–X.6.3; UC5 §§6.7–6.8 | Non-injective identify and explicit restriction | `reuse` for explicit maps and loss/fibres. `does not map` to physical collapse or exclusion of states: neither operation says a quantum alternative was destroyed. |
| v0.15 §§X.8–X.10; UC5 §§8–9 | Phase criteria, domain saturation, histories, operation order | `reuse` as inquiry-relative equivalence and operation-order discipline. `adapter-specific quantum semantics` for measurement-context equivalence and sequential instruments. Generic noncommutation is not a quantum incompatibility theorem. |
| v0.15 §§X.2–X.3 | EEC-Q `State`, `Joint`, signed rational coefficients | `does not map` to density operators, probability distributions, amplitudes or outcome counts. Coefficients are exact formal construction coefficients; no normalization/Born rule follows. A new adapter must compute quantum probabilities independently. |
| v0.15 §§X.16–X.17, especially C.11 | SF/CFS families, conditional realization | `reuse` only as symbolic-family and shared-parameter engineering patterns. `does not map` to preparation, state-vector superposition, channel, measurement or collapse; C.11 explicitly leaves the quantum carrier/rules to a different/additional profile. |
| v0.15 §§X.18–X.19 | RGP/WPC encoding, portions and accessible whole | `reuse` for explicit source edition, access/loss, retention and decoding contracts. `does not map` from measurement context to physical portion/subsystem or from accessible encoding to quantum-accessible information absent a quantum channel/operational rule. |
| v0.15 §X.21 MSC.1–MSC.8, MSC.12 | Finite scopes, partial maps, common codomains, compatible families, obstruction and fibres | `reuse` for finite diagram shape, declared domains, compatibility criterion, closure outcomes, and reconstruction fibres when candidate spaces and criterion are explicit. Stochastic observations need the separately declared distributional criterion required by MSC.6; raw-value equality is forbidden. MSC-B1 supports deterministic string observations only and explicitly excludes probabilistic observations (§MSC.12). A measurement context is not automatically a scope. No general-law gap is yet proved; quantum distributions require an adapter-specific comparison relation and joint-measurement criterion. |
| v0.15 §X.20 REC; UC5 §§3.9, 6, 9 | Replayable reasoning witness, evidence and observation boundaries | `reuse` for claim/evidence/provenance separation and bounded replay. `does not map` to certification of a physical observation, quantum hypothesis, calibration, or experimental truth. |
| v0.15 §X.14–X.15; C.11; E7Q #78 / #79 | Cross-version adapter and non-claims | `adapter-specific quantum semantics`; keep E7Q native identities and Q-A1/Q-A2/Q-A3/Q-A4 meanings unchanged. #79's signed rationals stay formal coefficients. |

**Smallest demonstrated delta:** a typed quantum adapter contract connecting admitted preparations and POVMs/instruments to distributions, actual-run outcomes and state transitions, plus operational joint measurability. MSC-B1 cannot represent stochastic observation comparison; MSC abstract MSC.6 anticipates a separately declared distributional criterion. The current evidence supports a narrow E7Q adapter, not a new substrate-neutral E7G-T law or an `IV/0.1` general profile.

## Typed candidate interface

For a declared finite-dimensional Hilbert space `H`, preparation domain `D` and map `prep : D -> W`, take `W = {rho : positive(rho) and tr(rho)=1}` as operational whole carrier. Let `C` be versioned contexts and `V_c = Dist(O_c)` be normalized distributions over finite outcomes. The effect family `E[c,o]` satisfies `E[c,o] >= 0` and `sum_o E[c,o] = I`.

```text
QuantumViewAdapter/v0alpha1:
  system: HilbertSpace[finite_dimension, basis_convention]
  preparation_domain: D
  prepare: D -> DensityOperator[H]
  context: ContextId[edition]
  effects: (context, outcome) -> PositiveOperator[H]
  distribution: (rho: W, c: C) -> ProbabilityDistribution[O_c]
  import_physical_record: (record: OutcomeRecord[O_c], provenance, preparation_id, run_id, c, protocol) -> ValidatedRecord | typed failure
  simulated_sampler: optional (rho, c, seed, simulator_edition) -> SimulatedOutcomeRecord[O_c]
  instrument: optional (c, o) -> CPMap[H -> H]  # only if state transition is in scope
  post_state: optional (rho, c, o) -> DensityOperator[H]
  state_fibre: (view_family, v, W) -> {rho in W | observations(rho) ≈ v}
  preparation_fibre: (view_family, v, D) -> {d in D | observations(prepare(d)) ≈ v}
  joint_device: (c1,c2) -> {success(parent_POVM, verified_marginals), incompatible(obstruction_certificate), invalid_input(diagnostic), unsupported(capability), undetermined(reason), resource_limit(bound)}
```

A physical outcome record is imported with provenance and run identity; the Born rule does not generate the result of a particular physical run. A separate simulator may sample an outcome only as simulated data and must bind its seed and implementation edition. Distributions from separate preparations/runs do not license a simultaneous pair of actual outcomes. An instrument uses `I[c,o](rho)` with outcome probability `tr(I[c,o](rho))` and normalized post-state only when that probability is nonzero. The initial bounded adapter should omit instrument/state update unless the requested workflow needs it.

A state-specific coupling `q(x,z)` with marginals equal to separate X and Z distributions is a mathematical coupling only. Physical joint-device admissibility requires one positive parent POVM `G[x,z]`, `sum_{x,z}G[x,z]=I`, `sum_z G[x,z]=E[X,x]`, `sum_x G[x,z]=E[Z,z]`. These operator marginal identities make the device valid uniformly over all admitted `rho`; a coupling for one selected `rho` does not establish them.

## Two meanings of “whole”

1. **Operational density operator (default):** all model predictions for the declared measurement set are computed from `rho`. It is not necessarily a complete description relative to measurements outside the declared model; reconstruction fibres state precisely what is identifiable.
2. **Enriched ontology (optional later hypothesis):** `lambda` may contain additional variables only with explicit preparation distribution, context/outcome response, transformation rules, relation to `rho`, and empirical departures or a proof of observational equivalence. Do not call `lambda` the same object as `rho` by default or imply it enables jointly sharp X/Z readings.

## Qubit fixture specification (plan, not yet implemented)

Use `H=C^2`, Pauli observables `X,Y,Z`, and sharp effects `E[A,s]=(I+sA)/2`, `s in {-1,+1}`. Let `rho_±=(I ± aY)/2`, `0<a<=1`. Then for sharp X and Z, both states yield `p(s|rho_±,X)=p(s|rho_±,Z)=1/2`, while `p(s|rho_±,Y)=(1±s a)/2`. Thus the X/Z view has a non-singleton state fibre `F_W(v)` containing at least these two distinct density operators; adding Y separates them. The preparation-description fibre is `F_D(v)={d in D | views(prepare(d))=v}` and contains the descriptions that prepare either state. Do not infer that `F_D(v)` has exactly two elements: `prepare` may be non-injective, so several descriptions may prepare the same density operator.

Sharp X and Z have no common parent POVM. If a parent `G[x,z]` had sharp X marginal, positivity and the projector marginal force each `G[x,z]` to be supported in the corresponding X eigenspace; sharp Z marginal similarly forces support in a Z eigenspace. Distinct Pauli eigenspaces are non-orthogonal, so a nonzero positive effect cannot satisfy both supports; all parent effects would be zero, contradicting their sum `I`. This argument applies to a device required to implement the sharp marginals for every admitted qubit state.

A comparison fixture is the unbiased unsharp pair `E_X(±)=(I±eta X)/2`, `E_Z(±)=(I±eta Z)/2`. A joint POVM is `G[x,z]=1/4(I+x eta X+z eta Z)`; positivity holds when `eta <= 1/sqrt(2)` since its eigenvalues are `(1 ± eta sqrt(2))/4`. Its marginals are the declared unsharp effects. This is a permitted comparison, not a blanket claim that all unsharp pairs are compatible.

The joint-device result must include a verified parent POVM and checked marginals for success, or a verified obstruction certificate for `incompatible`; it must also distinguish `invalid_input`, `unsupported`, `undetermined`, and `resource_limit`. Refuse to infer actual outcomes from distributions or across separate runs. Physical outcome records are imported with provenance; simulator output, if offered, is separately typed as simulated. These calculations are standard qubit POVM reasoning and should be independently checked in the next implementation increment; this audit itself is not an executable proof.

## Tempting but invalid identification

The EEC-Q row `(+1/2)e_(X=+1,Z=+1) + (+1/2)e_(X=-1,Z=-1)` is a formal signed-rational construction. It is not a quantum state or evidence of a joint sharp X/Z measurement. Conversely, `rho` does not imply a classical tuple of simultaneously pre-existing sharp outcomes. A state-specific classical coupling can always be constructed for two finite marginals, but it does not provide a parent POVM and its required operator marginals.

## Literature for next-stage review

These primary quantum sources are starting points, not yet a completed theorem-by-theorem literature survey for this audit:

- Heinosaari, Reitzner & Stano, “Notes on Joint Measurability of Quantum Observables,” arXiv:0811.0783 (joint measurability definitions and qubit observables): <https://arxiv.org/abs/0811.0783>.
- Busch & Heinosaari, “Approximate joint measurements of qubit observables,” arXiv:0706.1415 (joint measurability/approximation for qubit observables): <https://arxiv.org/abs/0706.1415>.
- Busch, Lahti & Werner, “Heisenberg's Uncertainty Principle,” arXiv:quant-ph/0609185 (operational uncertainty distinctions): <https://arxiv.org/abs/quant-ph/0609185>.

Physics review must verify theorem assumptions, including the all-states parent-device criterion, and extend the survey to POVMs/instruments, incompatible sharp observables, tomography, contextuality and preparation versus measurement uncertainty before Stage C implementation.

## Open questions and review gate

1. Which E7G-T object sorts best represent `D`, `W`, context declarations, distribution-valued outputs and actual run records without overloading `Config`, `State` or MSC `B_s`?
2. Does MSC's abstract distributional comparison slot suffice with a precise metric/equality relation, or is a separately versioned narrow comparison structure needed? Exhibit a failed typed mapping before proposing an E7G-T extension.
3. What identity/equality criterion applies to density matrices, POVM effects, distributions and finite precision output? The mathematical fixture uses exact values; a numerical adapter must declare tolerance and error.
4. Which contexts are performed on identically prepared separate runs, and which sequential transformations use one run and an instrument?
5. How do channels, instrument composition, postselection and zero-probability outcomes appear in a later contract?
6. What is the smallest E7Q adapter version and artifact schema that leaves all native Q-A1/Q-A2/Q-A3/Q-A4 meanings and IDs untouched and remains separate from #79?
7. Does an enriched ontology yield any observable departure, and what response law, regime, baseline, falsifier and feasible protocol would test it?
8. What mapping adds useful compositional tooling over direct Hilbert-space calculations without claiming novel physics?

**Requested review:** substantive mathematical review of maps/fibres and the joint-POVM argument, plus quantum-physics review of the adapter boundary and literature assumptions, against the exact draft commit. Keep this note in draft status; it licenses no new general law, profile, product adoption, canonical edit or quantum novelty claim.
