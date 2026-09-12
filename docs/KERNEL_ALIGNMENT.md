# E7G-T source-repository alignment

Direction: `E7-ECO-DIR-2026-09-12.2`  
Baseline reviewed: main `4cc1abcfc9eec488c384eb3d84ca3f59e491cdfc`  
Status: `ALIGNED_IN_DESIGN` as the source owner; independent reproduction and product adoption remain unestablished.

## Source and profiles

The canonical source for ecosystem architecture is `E7G-T_Kernel_v0.12_Experimental_Canonical_Reference.md`, revision CFS1, pinned at commit `b7a30b2d56375a5a0646e0c1cab4f621b4de99ca`.

- EEC-Q/0.1: `adopted` by the v0.12 experimental specification.
- SF/0.1: `adopted` by the v0.12 experimental specification.
- CFS/0.1: `adopted` by the v0.12 experimental specification.

Adopted means defined as an experimental canonical profile. It does not mean full implementation, production maturity, product adoption or independent validation.

## Repository responsibility

- preserve the immutable meaning of published source editions;
- maintain exact reference models, manifests and conformance cases;
- distinguish constitutional inheritance from profile-specific executable obligations;
- prevent consumers from treating rational coefficients as probabilities, evidence weights or quantum amplitudes;
- publish migration guidance for source, profile and model changes;
- accept shared contracts only when their relationship to the specification is explicit and tested.

## Component disposition

| Component | Disposition |
|---|---|
| v0.12/CFS1 canonical source | retain |
| FG3, IC and CG3 bounded reference models | retain |
| Current conformance cases and non-claims | retain |
| Ecosystem-facing contract/conformance adapters | adapt when two consumer requirements are known |
| Historical predecessor specifications | retain as versioned predecessor material |

No replacement or retirement is authorized by this record.

## Next bounded demonstration

Publish a stable proposal for the minimal cross-product identity, outcome, dependence, projection-kind, quotation and history declarations only after E2CI and E7Q-IR alignment audits supply two concrete consumer mappings. Validate positive and negative cases through an independent implementation.

Falsification gate: do not promote a shared contract when the two products require incompatible meanings or when the abstraction erases their native distinctions.
