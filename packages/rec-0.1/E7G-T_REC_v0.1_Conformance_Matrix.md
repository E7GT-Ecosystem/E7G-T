---
title: "E7G-T REC/0.1 Conformance Matrix"
profile: "REC/0.1-proposed"
model: "REC-B1/0.1"
kernel: "E7G-T v0.14-experimental-REC1-draft"
date: "2026-09-15"
status: "First-party bounded capability map"
---

# REC/0.1 conformance matrix

`Implemented` means exercised in REC-B1's finite propositional information-flow model, not proof of source truth, domain correctness or general REC completeness. `Partial` means a strict special case is implemented. `Specification-only` means no executable claim is made. `Unsupported` means REC-B1 rejects or omits the capability.

## Capability vector

| Capability | Disposition | Evidence |
|---|---|---|
| Typed claim/evidence admission | `partial` | Fixed JSON fields, identities, modalities, polarities, references, timestamps, scopes and editions |
| Four-status information semantics | `implemented` | Independent positive and negative bits; all four outcomes tested |
| Paraconsistent information flow | `partial` | Local `both` retained without automatic unrelated conclusions; no general logical language |
| Finite rule derivation | `implemented` | Canonically ordered monotone fixed-point closure |
| Scope safety | `partial` | Exact mapping-coordinate preservation and narrowing; general semantic subsumption unsupported |
| Temporal safety | `partial` | Equal or input-`any` temporal scope; temporal inference unsupported |
| Modality safety | `partial` | Same-modality flow and explicit authorised bridge |
| Provenance dependence | `partial` | Exact source editions and dependence-group retention; no statistical dependence calculus |
| Belief revision | `partial` | New envelope edition plus replay; no AGM-style minimal-change operator |
| Decision and abstention | `partial` | `report` and `rely_if_supported_only` policies |
| Proof-carrying output | `partial` | Canonical witness and separately implemented deterministic checker |
| Natural-language extraction | `unsupported` | Proposition content is opaque |
| Solver or proof-assistant export | `unsupported` | No SMT-LIB, Alethe, Lean or other formal export |
| Probabilistic support | `unsupported` | No numeric confidence or evidence aggregation |
| Empirical AI improvement | `not_claimed` | No baseline or ablation study in this release |

## Obligation mapping

| Profile obligation | Status | Model evidence or boundary |
|---|---|---|
| Pins kernel, profile, model, reasoning identity and edition | `implemented` | Admission and checker binding tests |
| Keeps claim occurrences distinct | `implemented` | Duplicate IDs reject; equal strings do not merge automatically |
| Keeps support and refutation independent | `implemented` | Two-bit status model |
| Distinguishes `neither` from `refuted` | `implemented` | No-evidence and stale-evidence tests |
| Preserves `both` | `implemented` | Conflicting evidence and forged-conflict rejection tests |
| Prevents explosion | `partial` | Only declared rules can derive bits; no arbitrary formula language |
| Binds evidence to source and edition | `implemented` | Required fields and exact witness inventory |
| Retains provenance groups | `implemented` | Same-origin duplicate remains one group |
| Excludes stale or future evidence from current status | `implemented` | Validity-interval tests and witness stale list |
| Requires explicit rule premises and conclusion | `implemented` | Admission plus rule-application trace |
| Terminates on the declared model | `implemented` | Finite claims/rules, monotone bits, each rule fires once |
| Rejects scope expansion | `partial` | Mapping-coordinate rule; no ontology-backed scope lattice |
| Rejects undeclared temporal change | `partial` | String-scope equality rule |
| Rejects undeclared modality change | `implemented` for fixed modalities | Negative bridge test |
| Records modality-bridge authority | `implemented` | Explicit `from`, `to`, `authority` object |
| Separates status from action | `implemented` | Query policy is distinct from status computation |
| Requires abstention or review when warranted | `implemented` for bounded policy | `both`, `neither`, `refuted` next actions |
| Binds witness to envelope | `implemented` | Canonical SHA-256 and tampering tests |
| Replays rather than trusting witness hash | `implemented` | Re-signed forged query, conflict and stale-list rejection |
| Reports unsupported/resource-limited steps | `partial` | Field is mandatory and empty; no resource-limit engine yet |

## Executed conformance cases

The first-party package run covers 34 internal named checks and 24 external `unittest` cases. The external suite includes deterministic replay, all four statuses, stale/future evidence, provenance grouping, fixed-point chains, duplicate prevention, scope narrowing, scope expansion rejection, temporal change rejection, modality bridges, envelope tampering, witness tampering and re-signed forgery rejection.

## Promotion consequences

REC/0.1 should not be promoted as an AI reasoning improvement until a stable schema and semantics are reviewed, an independent implementation reproduces the traces, at least one domain rule set is expert-reviewed, and controlled comparisons show whether REC changes accuracy, unsupported claims, scope errors, conflict retention, abstention, latency and cost relative to simpler baselines.
