# E7G-T source-repository alignment

Direction: `E7-ECO-DIR-2026-09-13.1`  
Baseline reviewed: main `fc4cdf95c6434e653efbe017587aab60b4b2a86c`  
Status: `ALIGNED_IN_DESIGN` as the source owner; independent reproduction and product adoption remain unestablished.

## Source and profiles

The canonical source for new ecosystem architecture is `E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md`, revision RGP2, pinned at commit `fc4cdf95c6434e653efbe017587aab60b4b2a86c`. Recorded v0.12 companion implementations retain their embedded v0.12 identifiers and hashes.

- EEC-Q/0.1: `adopted` by the v0.12 experimental specification.
- SF/0.1: `adopted` by the v0.12 experimental specification.
- CFS/0.1: `adopted` by the v0.12 experimental specification.
- RGP/0.1: `adopted` as an optional structural specification; bounded executable coverage remains incomplete.

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
| RGP/0.1 structural specification | retain |
| RGP-B1 bounded reference model and first-party tests | add as experimental; no general conformance claim |
| Ecosystem-facing contract/conformance adapters | adapt when two consumer requirements are known |
| Historical predecessor specifications | retain as versioned predecessor material |

No replacement or retirement is authorized by this record.

## RGP implementation boundary

`RGP-B1/0.1` demonstrates typed generation, source-linked projection, exact SR4 whole-bearing round trips, damage rejection, placement-coordinate independence and identity-preserving composition. It intentionally omits SR3, all-portions SR4, a canonical interchange schema, general recursion, authorization enforcement and distributed execution. Its first-party fixtures do not establish independent reproduction or external instantiation.

## Next bounded demonstration

Complete the remaining §R.12 negative cases, publish a canonical interchange proposal and obtain independent reproduction. Shared cross-product contracts still wait for two concrete consumer mappings from E2CI and E7Q-IR.

Falsification gate: do not promote a shared contract when the two products require incompatible meanings or when the abstraction erases their native distinctions.
