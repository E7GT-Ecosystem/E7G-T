# E7G-T REC/0.1 package

This directory packages the proposed Reasoning–Evidence Calculus introduced by the standalone E7G-T v0.14 experimental draft.

## Contents

| File | Role |
|---|---|
| `E7G-T_REC_v0.1_Reasoning-Evidence_Calculus_Profile.md` | Standalone proposed normative profile |
| `reasoning-envelope-v1.schema.json` | Draft 2020-12 bounded interchange schema |
| `e7gt_rec_v0_1.py` | Dependency-free reference evaluator and 34 internal checks |
| `run_reasoning.py` | Command-line envelope evaluator |
| `check_trace.py` | Separately implemented deterministic witness checker |
| `test_e7gt_rec_v0_1.py` | 24 standard-library external tests |
| `fixtures/translation_clause_envelope.json` | Typed translation-preservation example input |
| `fixtures/translation_clause_witness.json` | Canonical checked output |
| `E7G-T_REC_v0.1_Conformance_Matrix.md` | Obligation-to-implementation map |
| `E7G-T_REC_v0.1_Validation.json` | Recorded run, hashes, scope and omissions |

## Reproduce

From the repository root:

```bash
python3 packages/rec-0.1/e7gt_rec_v0_1.py
python3 -m unittest discover -s packages/rec-0.1 -p 'test_*.py' -v
python3 packages/rec-0.1/check_trace.py \
  packages/rec-0.1/fixtures/translation_clause_envelope.json \
  packages/rec-0.1/fixtures/translation_clause_witness.json
python3 -m json.tool packages/rec-0.1/reasoning-envelope-v1.schema.json
python3 -m json.tool packages/rec-0.1/E7G-T_REC_v0.1_Validation.json
```

## What the bounded model demonstrates

- four non-collapsing information statuses: `supported`, `refuted`, `both`, `neither`;
- finite monotone rule closure and deterministic replay;
- explicit stale-evidence handling;
- dependence-group retention without inferred independence;
- rejection of hidden scope, temporal-scope and modality expansion;
- reliance policies that require conflict resolution or abstention;
- envelope and witness hash binding;
- rejection of re-signed forged trace fields by a separately implemented checker.

## Boundary

REC-B1/0.1 accepts proposition content as opaque text. It checks declared information flow; it does not establish source truth or domain-rule validity. It is not a natural-language semantic parser, general theorem prover, probabilistic engine, production fact checker or evidence that REC improves AI performance. Comparative evaluation and independent reproduction remain promotion gates.
