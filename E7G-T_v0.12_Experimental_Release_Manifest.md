# E7G-T v0.12 Experimental Release Manifest

**Release:** `v0.12-experimental`
**Revision:** `CFS1`
**Date:** 2026-09-08
**Status:** Experimental canonical reference
**Authors:** Alexander Gregory Wingate and Oleksandr Razinkov

## Canonical source

- `E7G-T_Kernel_v0.12_Experimental_Canonical_Reference.md`
- SHA-256: `dcb667ffa7f47fadaf326bcdbe3d199319c51215c95ccd4b246ab05ae4f83068`

Canonical means the current authoritative v0.12 experimental reference. It does not assert stable adoption, production readiness, maturity-gate completion, independent validation or general mathematical proof.

## Companion artefacts

| Artefact | Role | SHA-256 |
|---|---|---|
| `E7G-T_v0.12_Executable_Examples.py` | EEC-Q/FG3 bounded reference model | `0b4b2b24de73059e47d3f3ab7865bcdf616eaf00b493063da9d6faba16f32f94` |
| `E7G-T_Symbolic_Family_Realisation_Profile_v0.1.md` | SF/0.1 mathematical profile | `3eaed99a842b7e99774b9f0caa6b9ab904de5fb0345d593ce42c9be7b7c978b4` |
| `E7G-T_Symbolic_Families_v0.1.py` | SF/IC bounded reference model | `0a827d55cc95c4840ba5427e8585378b23ee6a3b00296856f192176cb4a2dca8` |
| `E7G-T_Symbolic_Families_Validation_v0.1.json` | Recorded SF/IC internal validation | `96a76d4859376676891f966457ba3f577725463c0602ae32e7630cc8d0e82dc7` |
| `E7G-T_Combined_Family-State_Profile_v0.1.md` | CFS/0.1 mathematical profile | `a3e5b9096c7243066ab3367df214e3724a3de2063044f2806e49d0ec7bfe42d5` |
| `E7G-T_Combined_Family_State_v0.1.py` | CFS/CG3 bounded reference model | `ed6ba76f6638c859e65d9908ecd4ef2539cd1348df8249471ca706a51b94d542` |
| `E7G-T_Combined_Family-State_Validation_v0.1.json` | Recorded CFS/CG3 internal validation | `84686137b3fc6c084eb28feb81288c915165363d06d244b800b14b11aa63da71` |

## Reproduction

The Python companions require Python 3.10 or later and use the standard library only. Keep the three Python files in the same directory because the combined model imports the EEC and SF companions.

```bash
python3 E7G-T_v0.12_Executable_Examples.py
python3 E7G-T_Symbolic_Families_v0.1.py
python3 E7G-T_Combined_Family_State_v0.1.py
```

The release run under Python 3.12.13 completed 39 FG3, 48 IC and 40 CG3 named internal checks: 127 in total. These checks overlap in purpose and are not an independent reproduction, coverage claim, performance benchmark or proof of the general profiles.

## Compatibility and migration

`E7G-T_Kernel_v0.11_UC5_Unified_Public_Reference_Specification.md` remains the constitutional predecessor. Existing consumers pinned to UC5 retain their prior semantics. EEC-Q, SF and CFS are opt-in profiles; a consumer adopts one only by declaring its profile, concrete model, supported capabilities, limits and source digest.

## Licence

Except where otherwise noted, the release is licensed under CC BY-SA 4.0. See `LICENSE` for the repository terms.
