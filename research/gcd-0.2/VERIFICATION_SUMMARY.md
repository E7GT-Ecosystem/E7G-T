# GCD/0.2 — First-party verification summary

**Research profile:** `GCD/0.2-research`  
**Bounded evaluator:** `GCD-B1/0.2`  
**Pinned kernel:** `v0.15-experimental-MSC1`, unchanged  
**Validation environment:** Python `3.13.5`, `Linux` / `x86_64`  
**Date:** 2026-11-11  
**Status:** INTERNALLY TESTED; **not independently reproduced**.

## Execution result

- **35 named tests:** PASS; 0 errors, 0 failures.
- **5 end-to-end operation receipts:** replay-valid.
- **15 expected-negative receipts:** replay-valid with expected distinct non-success results.
- **11 admitted configurations** across three exact carriers: sizes 1, 4 and 6.
- **24 candidate stage subsets** evaluated for admission across all three signatures.
- **88 ordered-pair checks** of strict-refinement implication; 46 strict pair witnesses recorded (counted across three bridge comparisons).
- **16 and 64 exact family subsets** assessed under semantic refinement at successive signature extensions.
- **60 within-signature and 90 signature-generator candidate cases** evaluated.
- **378 candidate/family membership checks** across all nonempty `Σ2` families: 192 member selections and 186 rejected non-members.
- **6 source-carrier left-inverse cases** checked for registered embedding/grounding pairs.
- **9 finite ranks** (0–8) checked; rank 9 explicitly returns `resource_limit`.

## End-to-end modelled sequence

`constitutive_refinement → expansive_within_signature → expansive_signature_generation → selected → model_committed`

The final transition is a **synthetic in-memory model event only**. It is **not** a real WPC commitment, authenticated choice, publication, deployment or external action.

## Integrity and source isolation

Original supplied `GCD/0.1`, `v0.15` canonical reference and ecosystem operating kernel v0.2 SHA-256 values were checked against their pre-development values and were unchanged. `SOURCE_PINS.json` records their exact filenames and hashes. All new work is isolated under `E7GT_GCD_0.2_research/`.

## Reproduce

```sh
./run_verification.sh
python3 replay_all.py evidence/end_to_end_receipts.json evidence/negative_receipts.json
sha256sum -c SHA256SUMS.txt
```

**Scope boundary:** All enumerations are exhaustive **only within the frozen finite GCD-B1 carrier and the two registered generator rules**. The tests are first-party and share the implementation's semantic assumptions. They do not establish universal GCD validity, implementation independence, external authenticity, physical hypotheses, production security, commercial value or conformance of other E7G-T profiles.
