# E7C/0.1 research control surface

Status: `WP0_ACCEPTED; WP1_ACCEPTED; WP2_ACCEPTED; WP3_S_ACCEPTED; WITNESS_CONTRACT_ACCEPTED; WP3_I_IN_REVIEW`

Direction: `E7-ECO-DIR-2026-09-15.1`

Baseline: `a6c562108450679e33566b8e395c4d045f042823`

Source-freeze cutoff: `2026-09-15T19:52:58Z`

This directory contains the WP0 source freeze, accepted WP1–WP3-S specifications
and the disposable WP3-I implementation candidate. E7G-T
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
10. `E7C_0.1_SOURCE_REGISTRY.yaml`
11. `E7C_0.1_POST_V0121_GAP_AND_PROPOSAL_REGISTER.md`
12. `E7C_0.1_SUCCESSOR_SOURCE_COVERAGE.yaml`
13. `E7C_0.1_COMPONENT_DISPOSITIONS.md`
14. `E7C_0.1_TERMINOLOGY_MATRIX.md`
15. `E7C_0.1_COMPATIBILITY_BOUNDARIES.md`
16. `E7C_0.1_DECISION_REGISTER.md`
17. `E7C_0.1_RISK_REGISTER.md`

WP0 was accepted with named deferrals at PR #34 merge `64c49b4676…`. WP1 was
accepted at PR #35 and merged as `1f4c7cf…`. WP2 was accepted at PR #36 and
merged as `ed2a49de…`. WP3-S was accepted at PR #37 head `bae84fb73e…` and
merged as `c13d77dc5b…`. The witness contract was accepted at PR #38 head
`eea2c88290ee…` and merged as `a6c562108450…`. WP3-I now contains a separately
scoped disposable evaluator and independent replay checker candidate. Its exact
head requires review before any conformance or correctness claim. Stable IR,
runtime, schemas and APIs remain out of scope.
