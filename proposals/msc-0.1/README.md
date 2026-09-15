# MSC/0.1 — Multi-Scope Coherence

MSC/0.1 is an optional speculative formal-research proposal for E7G-T. It asks
whether several independently constituted wholes at different declared scopes
form a compatible family, an ambiguous family, or an obstruction.

MSC does not replace:

- RGP generation and nesting;
- WPC whole–part constitution and evolution;
- REC reasoning/evidence audit;
- SF symbolic descriptions of potentially infinite families; or
- UC5 temporal reconstruction and phase analysis.

It is deliberately not called REC because `REC/0.1` already identifies the
Reasoning–Evidence Calculus. It is not a new kernel version and creates no
product migration obligation.

## Package

- `E7G-T_MSC_v0.1_Multi-Scope_Coherence_Proposal.md` — proposed formal profile;
- `E7G-T_MSC_v0.1_Conformance_Matrix.md` — obligation-level status;
- `msc-diagram-v1.schema.json` — interchange schema;
- `e7gt_msc_v0_1.py` — bounded dependency-free reference model;
- `test_e7gt_msc_v0_1.py` — external standard-library tests;
- `fixtures/` — unique closure and pairwise-compatible global obstruction;
- `AUTHOR_REVIEW_REQUEST.md` — a return-to-author review prompt;
- `E7G-T_MSC_v0.1_Validation.json` — first-party validation and boundaries.

## Reproduce

```bash
python3 proposals/msc-0.1/e7gt_msc_v0_1.py \
  proposals/msc-0.1/fixtures/unique_closure.json
python3 proposals/msc-0.1/e7gt_msc_v0_1.py \
  proposals/msc-0.1/fixtures/global_obstruction.json
python3 -m unittest discover -s proposals/msc-0.1 -p 'test_*.py' -v
python3 -m json.tool proposals/msc-0.1/msc-diagram-v1.schema.json
```

Passing tests establish only the behaviour of this finite first-party model.
They do not establish an infinite hierarchy, physical parallel realities,
metaphysical truth, external existence, general decidability, or product value.

