# E7G-T source-repository alignment

Direction: `E7-ECO-DIR-2026-09-15.1`  
Baseline reviewed: main `8504d3124ef1e64f008087c46e09ca8acf6d7479`  
Candidate branch: `codex/v014-rec-01`  
Status: `CANDIDATE_ALIGNED_IN_DESIGN`; empirical improvement and independent reproduction remain unestablished.

## Source and profile status

The published experimental canonical source remains `E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md`, revision RGP2. The v0.13/RWP1 draft is the retained self-contained predecessor candidate. `E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md`, revision REC1, is the new candidate successor and does not silently migrate consumers.

| Profile or component | Disposition |
|---|---|
| EEC-Q, SF, CFS, RGP and WPC families | retain without semantic replacement |
| REC/0.1 | add as optional proposed reasoning-audit profile |
| REC-B1/0.1 | add as partial bounded implementation |
| Existing models, IDs, APIs and historical specifications | retain |
| Preserved UC5 body | retain unchanged from the v0.13 predecessor |

No replacement or retirement is authorised by this record.

## REC implementation boundary

REC-B1 demonstrates finite typed claim/evidence admission, four support/refutation information statuses, stale-evidence handling, dependence-group retention, deterministic monotone rules, bounded scope/temporal/modality safety, two decision policies and canonical witnesses. Its separately implemented checker replays the trace and rejects hash tampering and re-signed forged status, conflict and stale-evidence fields. The first-party package passes 34 internal checks and 24 external unit tests.

Proposition text remains opaque. The model does not validate source truth, natural-language extraction, domain-rule soundness, authority legitimacy, general logic, calibrated uncertainty, minimal-change belief revision, empirical AI improvement or independent reproduction.

## Next gate

Run a controlled comparison using the same model and sources under ordinary prompting, checklist prompting, retrieval alone and retrieval plus REC. Measure accuracy, unsupported claims, scope and modality errors, conflict retention, appropriate abstention, latency and cost. Promotion also requires schema/semantic review, expert-reviewed domain rules and an external implementation.
