# E7C/0.1 research control surface

Status: `WP0_ACCEPTED; WP1_ACCEPTED; WP2_ACCEPTED; WP3_S_ACCEPTED; WITNESS_CONTRACT_ACCEPTED; WP3_I_MERGED_WITHOUT_INDEPENDENT_ACCEPTANCE; WP4_S_ACCEPTED; LEAN_BOUNDED_SPIKE_ACCEPTED; WP4_LEAN_CORE_REVISION_REQUIRED`

Direction: `E7-ECO-DIR-2026-09-15.1`

Baseline: `9f997801eba3ff526f7caa83b6a4a1980a713bcb`

Source-freeze cutoff: `2026-09-15T19:52:58Z`

This directory contains the WP0 source freeze, accepted WP1–WP3-S specifications,
the integrated disposable WP3-I implementation and the merged WP4-S
metatheory and bounded Lean spike, plus the draft WP4 Lean core extension. E7G-T
v0.12.1-experimental, profile `RGP/0.1`, revision `RGP2`, remains the published
experimental canonical reference.

## Reading order

1. `E7C_0.1_CURRENT_STATE.md`
2. `E7C_0.1_CHARTER.md`
3. `E7C_0.1_FORMAL_VOCABULARY.md`
4. `E7C_0.1_PROFILE_MODULE_CONTRACT.md`
5. `E7C_0.1_WP1_REVIEW_MATRIX.md`
6. `E7C_0.1_STATIC_SEMANTICS.md`
7. `E7C_0.1_DYNAMIC_DENOTATIONAL_SEMANTICS.md`
8. `E7C_0.1_WITNESS_CONTRACT.md`
9. `E7C_0.1_WP3_I_IMPLEMENTATION.md`
10. `E7C_0.1_PROOF_OBLIGATIONS.md`
11. `E7C_0.1_COUNTEREXAMPLE_CATALOGUE.md`
12. `E7C_0.1_PROOF_ASSISTANT_SELECTION.md`
13. `E7C_0.1_SOURCE_REGISTRY.yaml`
14. `E7C_0.1_POST_V0121_GAP_AND_PROPOSAL_REGISTER.md`
15. `E7C_0.1_SUCCESSOR_SOURCE_COVERAGE.yaml`
16. `E7C_0.1_COMPONENT_DISPOSITIONS.md`
17. `E7C_0.1_TERMINOLOGY_MATRIX.md`
18. `E7C_0.1_COMPATIBILITY_BOUNDARIES.md`
19. `E7C_0.1_DECISION_REGISTER.md`
20. `E7C_0.1_RISK_REGISTER.md`

WP0 was accepted with named deferrals at PR #34 merge `64c49b4676…`. WP1 was
accepted at PR #35 and merged as `1f4c7cf…`. WP2 was accepted at PR #36 and
merged as `ed2a49de…`. WP3-S was accepted at PR #37 head `bae84fb73e…` and
merged as `c13d77dc5b…`. The witness contract was accepted at PR #38 head
`eea2c88290ee…` and merged as `a6c562108450…`. WP3-I was merged from exact head
`fe7ed454fa28…` as `9f997801eba3…` by explicit owner direction, without a
recorded independent acceptance verdict; no conformance or correctness claim
follows from that integration. WP4-S states the first bounded metatheorems, proof sketches and
counterexamples. PR #40 and the bounded PR #42 Lean feasibility spike merged.
PR #43 is draft at `01f7087bbe6dfd0022033c442b922df366ad7814`;
its exact-head review found three corrections required: separate WP2 effects
from WP3 order, fix the ill-typed regression claim and pin workflow actions.
A follow-up review of a corrected head is required. Proof-assistant selection
remains deferred. Stable IR, runtime, schemas
and APIs remain out of scope.
