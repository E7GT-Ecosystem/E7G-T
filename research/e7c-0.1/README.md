# E7C/0.1 research control surface

Status: `WP0_ACCEPTED; WP1_ACCEPTED; WP2_ACCEPTED; WP3_S_ACCEPTED; WITNESS_CONTRACT_ACCEPTED; WP3_I_MERGED_WITHOUT_INDEPENDENT_ACCEPTANCE; WP4_S_ACCEPTED; LEAN_BOUNDED_SPIKE_ACCEPTED; WP4_LEAN_CORE_ACCEPTED_AND_MERGED; WP5_EECQ_BOUNDED_ADAPTERS_INTEGRATED`

Direction: `E7-ECO-DIR-2026-09-15.1`

Baseline: `9f997801eba3ff526f7caa83b6a4a1980a713bcb`

Source-freeze cutoff: `2026-09-15T19:52:58Z`

This directory contains the WP0 source freeze, accepted WP1–WP3-S specifications,
the integrated disposable WP3-I implementation and the merged WP4-S
metatheory and bounded Lean core, plus five integrated provisional WP5 slices
covering EEC-Q graph states, joint/restriction, finite phase/view, rank-one
whole-state quotation and candidate-relative phase fibres. Subsequent WP5
FG3 assembly and typed bridge modules are integrated, followed by a separate
versioned S1 State/Joint static and finite execution/replay candidate. The
strict union successor is separately editioned. E7G-T
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
Review of PR #43 at `01f7087bbe6dfd0022033c442b922df366ad7814`
found three corrections required: separate WP2 effects from WP3 order, fix the
ill-typed regression claim and pin workflow actions. Those corrections were
accepted for integration at PR #45 head `9b2c636288150c33a55d2d76348cad5352eb99ca`
and merged into PR #43 as `35ecbc1bfc54376aa48de5b160ab4533c5c7aba4`.
PR #43 passed bounded internal exact-head review at
`4dab1a8a12c64f23cf91dfff6b56c566d9dd301f` and merged as
`64758c6cd9b177b196f2cf786ee88253626b7dca`. WP5 PR #47 merged as
`30d94c24abb8559fb5ef9e4c9ecb7ffad2723b97` and PR #48 as
`0b3ff687bb30a5d9ba5ad1c6b0f8efd4ff4c83e9`. PR #50 merged as
`d2a4d139f40a211d8a6fa9005a72477e8b078182` and PR #51 as
`fcb7eb6cc14f2f720790379db343e8fae16b01a5`. PR #53 merged as
`482abdd2b050d621df24ff7afbfcf885d1e6e68d`. Their bounded source
fragments are recorded in the four `E7C_0.1_WP5_EECQ_*.md` notes and
`E7C_0.1_WP5_FINITE_FIBRE.md`; WP5
remains open and general E7C adequacy is not claimed.
PR #55 added bounded assembly joins, PR #56 a typed FG3 bridge, PR #57
introduced the S1 State/Joint static candidate and PR #58 added finite FG3
execution and separately implemented replay. The S1 strict joint successor
adds a terminal whole-failure rule under its own opt-in edition; see
`E7C_0.1_S1_STRICT_JOINT.md`. These do not complete WP5, replace accepted
B1, establish proof, or migrate any product.
Lean selection remains deferred. Stable IR, runtime, schemas
and APIs remain out of scope.
