---
title: "E7G-T v0.14 Experimental Release Manifest"
version: "0.14-experimental-REC1-draft"
date: "2026-09-15"
status: "Release candidate for review"
baseline_commit: "8504d3124ef1e64f008087c46e09ca8acf6d7479"
branch: "codex/v014-rec-01"
---

# E7G-T v0.14 experimental release manifest

This manifest binds the standalone v0.14 kernel draft to the REC/0.1 companion package. Published predecessor editions remain immutable. No consumer is automatically migrated, and no improvement in AI performance is claimed by this release candidate.

## Release artifacts

| Repository path | Role | SHA-256 |
|---|---|---|
| `E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md` | Self-contained successor kernel draft | `a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a` |
| `packages/rec-0.1/E7G-T_REC_v0.1_Reasoning-Evidence_Calculus_Profile.md` | Standalone proposed normative profile | `52b88f24e8fbbd2aef7dc221978be844790ae1c476ea7133ceedef9fde0ebbc3` |
| `packages/rec-0.1/reasoning-envelope-v1.schema.json` | Bounded Draft 2020-12 interchange schema | `7857ec7573f31b1304ae81ca905a100aab06af84d1a41d9caf5278c346edfd50` |
| `packages/rec-0.1/e7gt_rec_v0_1.py` | Dependency-free bounded evaluator | `8902086db749567b0360bbb7ec4e71127f272791bf27b14d5f89b7049c197c55` |
| `packages/rec-0.1/run_reasoning.py` | Command-line evaluator | `bd4c7abeaa5b8ae3911199dd0ecab3279d892eeaf175d4b0e432ffde0f316146` |
| `packages/rec-0.1/check_trace.py` | Separately implemented trace checker | `ff145ff10f60ab440602f2de87d94dc51d865ef29478ad486d191ee291cac304` |
| `packages/rec-0.1/test_e7gt_rec_v0_1.py` | Standard-library external tests | `277ac773213d30b57d5f119bb8b2ce13689f556e1300a271790438033013f9db` |
| `packages/rec-0.1/fixtures/translation_clause_envelope.json` | Typed example input | `66d672ecb0acc7842601829f58cd9ce5b0be76273bd8dafb9f18726291ac6b58` |
| `packages/rec-0.1/fixtures/translation_clause_witness.json` | Canonical checked output | `df2d26ded5c0fee3d643d34644fc79444f8d2ee04011eab73896244b69257d72` |
| `packages/rec-0.1/E7G-T_REC_v0.1_Conformance_Matrix.md` | Obligation-to-implementation map | `0019101f8105ecb466b59d536b526d702a4670c2afd4f51c3f4bee6c295e45c5` |
| `packages/rec-0.1/E7G-T_REC_v0.1_Validation.json` | First-party validation record | `e10dea27260d89c1bc38408bf8b902ad125f5a742e9569af22e6c68193246aac` |
| `packages/rec-0.1/README.md` | Reproduction and boundary guide | `29e431b7664286c0419933311c541150d8b17192f5945fae881dac273896a79b` |

## Profile dispositions

| Profile or component | v0.14 disposition |
|---|---|
| EEC-Q, SF, CFS, RGP and WPC families | Retained without semantic replacement |
| REC/0.1 | Added as an optional proposed reasoning-audit profile |
| REC-B1/0.1 | Added as a partial bounded implementation |
| Existing reference models, APIs and predecessor files | Retained unchanged |
| Preserved UC5 body | Byte-for-byte content retained from the v0.13 predecessor between preservation markers |

## Reproduction record

Run from the repository root with Python 3.12 or a compatible Python 3 interpreter:

```bash
python3 packages/rec-0.1/e7gt_rec_v0_1.py
python3 -m unittest discover -s packages/rec-0.1 -p 'test_*.py' -v
python3 packages/rec-0.1/check_trace.py \
  packages/rec-0.1/fixtures/translation_clause_envelope.json \
  packages/rec-0.1/fixtures/translation_clause_witness.json
python3 -m json.tool packages/rec-0.1/reasoning-envelope-v1.schema.json
python3 -m json.tool packages/rec-0.1/E7G-T_REC_v0.1_Validation.json
```

The first-party release run under Python 3.12.14 produced:

- 34 of 34 named internal checks passed;
- 24 of 24 external `unittest` cases passed;
- the canonical fixture passed the separately implemented trace checker;
- schema and validation JSON parsed successfully;
- the embedded §X.20 profile body matched the standalone profile body;
- the preserved UC5 body matched the v0.13 predecessor.

## Claim boundary

REC-B1 checks a finite declared information-flow computation over opaque proposition text. It does not validate source truth, natural-language extraction, domain-rule soundness, authority legitimacy, general logical completeness, calibrated uncertainty or improved AI performance. The checker is separately implemented within the same first-party package; this is not independent reproduction.

Promotion requires semantic and schema review, an external implementation, expert-reviewed domain rules and controlled baseline comparisons measuring accuracy, unsupported claims, scope errors, conflict retention, abstention, latency and cost.
