# E7G-T v0.12 Experimental Release Manifest

**Release:** `v0.12-experimental`
**Revision:** `CFS1`
**Date:** 2026-09-08
**Status:** Experimental canonical reference
**Author:** Oleksandr Razinkov

## Canonical source

- `E7G-T_Kernel_v0.12_Experimental_Canonical_Reference.md`
- SHA-256: `dcb667ffa7f47fadaf326bcdbe3d199319c51215c95ccd4b246ab05ae4f83068`

Canonical means the current authoritative v0.12 experimental reference. It does not assert stable adoption, production readiness, maturity-gate completion, independent validation or general mathematical proof.

## Companion artefacts

| Artefact | Role | SHA-256 |
|---|---|---|
| `E7G-T_v0.12_Executable_Examples.py` | EEC-Q/FG3 bounded reference model | `53f64492f296d03e9574d9c1f2e511b950c32a80bb3480350e91493ff8c530c6` |
| `E7G-T_Symbolic_Family_Realisation_Profile_v0.1.md` | SF/0.1 mathematical profile | `241be2a4924303a50ddac1087378ee8161a5917fdff5e56b8353250c0dd380f3` |
| `E7G-T_Symbolic_Families_v0.1.py` | SF/IC bounded reference model | `a138ca772076aab8fad7ce929cac13cd19397f5fb30a255902bc1c508425a718` |
| `E7G-T_Symbolic_Families_Validation_v0.1.json` | Recorded SF/IC internal validation | `96a76d4859376676891f966457ba3f577725463c0602ae32e7630cc8d0e82dc7` |
| `E7G-T_Combined_Family-State_Profile_v0.1.md` | CFS/0.1 mathematical profile | `89555981e0b6d4f40e993b9b5e48c9a11d1bf6b3e6796f9a12ec34eb8dc7bca9` |
| `E7G-T_Combined_Family_State_v0.1.py` | CFS/CG3 bounded reference model | `617e72fadee2ff824fac030fd4d3c722b711743c846c321f6cc0e87b0f10809c` |
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

## Authorship correction on 10 October 2026

Current-tree author credits name Oleksandr Razinkov alone. The table above identifies the corrected current bytes. Historical commits and validation records retain their original byte identities; the correction does not change profile semantics or establish new validation evidence. See [the authorship record](docs/AUTHORSHIP.md).
