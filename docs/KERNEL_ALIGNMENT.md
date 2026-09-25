# E7G-T source-repository alignment

Direction: `E7-ECO-DIR-2026-09-15.1`  
Predecessor reviewed: main `86653557f5b5780a984f3a2dab226213ebbe3702`
Successor: `E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md`
Status: `EXPERIMENTAL_CANONICAL_SOURCE`; full profile conformance, empirical improvement and independent reproduction remain unestablished.

## Source and profile status

The new experimental canonical source is `E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md`, revision MSC1. The v0.12.1/RGP2 canonical predecessor and v0.13/RWP1 and v0.14/REC1 drafts remain immutable edition-pinned sources. The new source includes the complete MSC/0.1 formal proposal without claiming complete implementation or automatically migrating consumers. See [the successor decision](CANONICAL_SUCCESSOR_DECISION.md).

| Profile or component | Disposition |
|---|---|
| EEC-Q, SF, CFS, RGP, WPC and REC families | retain without silent semantic replacement |
| MSC/0.1 | include its complete optional formal proposal in §X.21 |
| REC-B1/0.1 and MSC-B1/0.1 | retain as bounded partial implementations |
| Existing models, IDs, APIs and historical specifications | retain |
| Preserved UC5 body | retain unchanged from the v0.13 predecessor |

The v0.12.1 source is superseded for new citations, not erased or migrated. No profile identity, product API, fixture or schema is replaced by this record.

## REC implementation boundary

REC-B1 demonstrates finite typed claim/evidence admission, four support/refutation information statuses, stale-evidence handling, dependence-group retention, deterministic monotone rules, bounded scope/temporal/modality safety, two decision policies and canonical witnesses. Its separately implemented checker replays the trace and rejects hash tampering and re-signed forged status, conflict and stale-evidence fields. The first-party package passes 34 internal checks and 24 external unit tests.

Proposition text remains opaque. The model does not validate source truth, natural-language extraction, domain-rule soundness, authority legitimacy, general logic, calibrated uncertainty, minimal-change belief revision, empirical AI improvement or independent reproduction.

## Next gate

The [active E7C v0.15 build map](../roadmaps/E7C_0.1_V015_ACTIVE_BUILD_MAP.md)
tracks new calculus work without changing historical adapter pins or product
adoption.

Close the edition-specific E7C proof and implementation obligations before claiming full profile conformance; the actual Python/IR-to-Lean refinement is still open. Run a controlled comparison using the same model and sources under ordinary prompting, checklist prompting, retrieval alone and retrieval plus REC. Measure accuracy, unsupported claims, scope and modality errors, conflict retention, appropriate abstention, latency and cost. Mature REC claims still require schema/semantic review, expert-reviewed domain rules and an external implementation; MSC retains its separate typed-map and independent reproduction gates.
