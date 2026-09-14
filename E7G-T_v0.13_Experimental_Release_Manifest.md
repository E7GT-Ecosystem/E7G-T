---
title: "E7G-T v0.13 Experimental Release Manifest"
version: "0.13-experimental-RWP1-draft"
date: "2026-09-14"
status: "Release candidate for review"
baseline_commit: "8e3d8d97c59c6fafd6d621779a45f15bb1dc0555"
branch: "codex/v013-rwp1-package"
---

# E7G-T v0.13 experimental release manifest

This manifest binds the standalone v0.13 kernel draft to its WPC/0.2 companion package. Version 0.12.1 remains the repository's published experimental canonical version until this candidate is reviewed and deliberately promoted.

## Release artifacts

| Repository path | Role | SHA-256 |
|---|---|---|
| `E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md` | Self-contained successor kernel draft | `ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe` |
| `packages/wpc-0.2/E7G-T_WPC_v0.2_Reciprocal_Whole-Part_Profile.md` | Standalone proposed normative profile | `e1ebd7d3b1945f816fa21aee5d1c4802486d0b7cc2e097a99c96ec1c60d1cd3c` |
| `packages/wpc-0.2/E7G-T_WPC_v0.2_Reference_Model.py` | Dependency-free bounded reference model | `5fe2e8d5f913f92ad8fbd0575607f569cbd211b13970174d537a9af14a493ea3` |
| `packages/wpc-0.2/test_e7gt_wpc_v0_2.py` | Standard-library external test wrapper | `9af439dfeb6502a80a72112838a6a3476b0b008625f6c6975872c7258b5e4e43` |
| `packages/wpc-0.2/E7G-T_WPC_v0.2_Validation.json` | First-party validation record | `230fc58a03f06a025f6ddf2017e40851205e4e953a4d27b262b31b81bd8e1b0f` |
| `packages/wpc-0.2/E7G-T_WPC_v0.2_Conformance_Matrix.md` | Obligation-to-implementation map | `ca4384f5534ce4966ca5d5b5d45c99dfae1e3056ee3dd50c962696ba695bccea` |
| `packages/wpc-0.2/README.md` | Reproduction and package boundary guide | `f0d32c0b302003d54f1069fabb8582bd45f29c446be58292cd9f4bdb90241ab7` |

## Profile dispositions

| Profile or component | v0.13 disposition |
|---|---|
| EEC-Q, SF and CFS | Retained |
| RGP/0.2 | Adapted to the v0.13 reciprocal whole–part vocabulary without replacing its profile identity |
| WPC/0.1 | Retained as legacy compatibility material |
| WPC-Core/0.2 | Proposed; bounded implementation is partial |
| WPC-Evolution/0.1 | Optional and proposed; bounded implementation is partial |
| WPC-Distributed/0.1 | Optional and proposed; no implementation claim |
| Preserved UC5 body | Unchanged from the v0.12.2 predecessor |

## Reproduction record

Run from the repository root with Python 3.12 or a compatible Python 3 interpreter:

```bash
python3 packages/wpc-0.2/E7G-T_WPC_v0.2_Reference_Model.py
python3 -m unittest discover -s packages/wpc-0.2 -p 'test_*.py' -v
python3 -m json.tool packages/wpc-0.2/E7G-T_WPC_v0.2_Validation.json
```

The first-party release run under Python 3.12.14 produced:

- 34 of 34 named internal checks passed;
- four of four external `unittest` cases passed;
- ten finite initial wholes enumerated;
- 30 exact portion round trips completed;
- validation JSON parsed successfully.

## Claim boundary

The results validate the stated finite allocation model only. They do not establish full WPC-Core/0.2 or WPC-Evolution/0.1 conformance, any WPC-Distributed/0.1 capability, independent reproduction, production readiness, physical instantiation, universal ontology, or superiority over simpler state-machine or event-log baselines.

Promotion requires review of the formal sorts and closure laws, a normative interchange schema, implementation of each claimed capability, positive and negative conformance evidence, independent reproduction, and at least one end-to-end application comparison.
