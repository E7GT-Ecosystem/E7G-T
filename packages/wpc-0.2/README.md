# E7G-T WPC/0.2 package

This directory packages the proposed reciprocal whole–part profile introduced by the standalone E7G-T v0.13 experimental draft.

## Contents

| File | Role |
|---|---|
| `E7G-T_WPC_v0.2_Reciprocal_Whole-Part_Profile.md` | Standalone normative profile draft |
| `E7G-T_WPC_v0.2_Reference_Model.py` | Dependency-free bounded allocation reference model |
| `test_e7gt_wpc_v0_2.py` | Standard-library external test wrapper |
| `E7G-T_WPC_v0.2_Validation.json` | Recorded first-party run, hashes, scope and omissions |
| `E7G-T_WPC_v0.2_Conformance_Matrix.md` | Obligation-by-obligation implementation map |

## Reproduce

From the repository root:

```bash
python3 packages/wpc-0.2/E7G-T_WPC_v0.2_Reference_Model.py
python3 -m unittest discover -s packages/wpc-0.2 -p 'test_*.py' -v
```

Expected bounded results:

- 34 internal named checks;
- four `unittest` cases;
- ten enumerated initial wholes;
- 30 exact portion round trips.

## Boundary

This package implements a deliberately small finite subset. It does not establish full WPC/0.2 conformance, WPC-Distributed support, independent reproduction, production readiness, physical instantiation or general mathematical validity. Read the conformance matrix before relying on any capability.
