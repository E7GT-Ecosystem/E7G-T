---
title: "E7G-T WPC/0.2 Conformance Matrix"
profile: "WPC/0.2-proposed"
model: "allocation-example/0.1"
kernel: "E7G-T v0.13-experimental-RWP1-draft"
date: "2026-09-14"
status: "First-party bounded capability map"
---

# WPC/0.2 conformance matrix

This matrix maps the v0.13 draft obligations to the bounded allocation reference model. `implemented` means exercised in the declared finite model, not general proof. `partial` means that a strict special case is implemented. `specification-only` means no executable claim is made. `unsupported` means the bounded model intentionally rejects or omits the capability.

## Capability declaration

| Capability | Disposition | Evidence |
|---|---|---|
| WPC-Core/0.2 | `partial` | Canonical finite `Whole`, `Assembly`, encode/decode, `alpha`, strict `beta`, membership and exact bounded checks |
| WPC-Evolution/0.1 | `partial` | Local proposals, joint reconciliation, event identity, fixed authority and basic membership candidates |
| WPC-Distributed/0.1 | `unsupported` | No network, messaging, fault model, commitment protocol or recovery implementation |
| All-portions SR4 | `implemented` for the finite canonical-JSON scope | 30 exact portion round trips across ten enumerated initial wholes |
| WPC/0.1 legacy WC levels | `not_claimed` | The model targets WPC/0.2 capability-vector semantics |

## Core-law mapping

| Law | Status | Model evidence or boundary |
|---|---|---|
| WP1 — relations remain separately typed | `partial` | Encoding, decoding, reconciliation and membership are distinct functions; expression, commitment and execution are not implemented |
| WP2 — completeness is coverage-relative | `partial` | Exact manifest/row equality, missing and duplicated occurrence rejection; no general coverage generator or unavailable state |
| WP3 — occurrence, local state and payload differ | `implemented` | Assembly rows carry all three; equal payloads retain three occurrence IDs |
| WP4 — local state, relations, dependencies and history constitute the whole | `partial` | Local allocation, membership and event tuples enter exact identity; arbitrary relations and dependencies are unsupported |
| WP5 — pairwise admission does not imply global admission | `implemented` | Three pairwise-valid allocations fail the joint budget |
| WP6 — constitution establishes no SR tier | `partial` | `Whole` is admitted without encode/decode; SR4 is separately tested; SR0–SR3 are unsupported |
| WP7 — reconstruction uses extraction, constitution and payload agreement | `partial` | `beta` reconstructs from actual rows then checks every payload; general `A`, `epsilon` and ambiguous constitution outcomes are not exposed |
| WP8 — reciprocal closure is domain- and normalisation-bound | `partial` | Both exact laws hold on canonical assemblies; non-trivial normalisation is unsupported |
| WP9 — state-changing expression yields a proposal | `specification-only` | No contextual-expression API |
| WP10 — local proposals may generate a successor | `implemented` | A and B proposals jointly produce `(1,1,0)` |
| WP11 — candidacy does not grant commitment or execution | `partial` | Model labels the result a candidate; no commitment or execution mechanism exists |
| WP12 — proposals are not silently dropped | `partial` | Accepted events are retained; conflicts reject; no deferred or ambiguous result family |
| WP13 — refreshed payloads follow the successor | `partial` | `alpha(successor)` encodes the new whole and mixed old/new payloads fail; no delivery protocol |
| WP14 — membership, rule, scope and representation changes invalidate witnesses | `partial` | Join/leave create new editions and payloads; split/merge, rule and scope change are unsupported |
| WP15 — semantic coherence, currentness, availability and liveness differ | `partial` | Historical stale payload and current-source conflict are distinct; availability and liveness are unsupported |
| WP16 — equal endpoints may have different histories | `implemented` | Different event IDs yield different encoded wholes with equal allocations |
| WP17 — richer state uses a new admitted scope | `specification-only` | No schema extension or residual recovery model |
| WP18 — lineage, edition and continuity differ | `partial` | Epoch alone is rejected as identity; lineage and inquiry-relative continuity are not implemented |
| WP19 — relation cycles do not license self-encoding | `specification-only` | The model avoids self-embedding but has no parser or negative cyclic-quote case |
| WP20 — reconstruction grants no execution or access authority | `partial` | Decode returns immutable data and local writes require fixed actor equality; general access policy is unsupported |

## Minimum conformance-case mapping

| Required case | Status | Named check or explanation |
|---|---|---|
| Exact coverage | `partial` | `missing member`, `duplicate occurrence`, `no vacuous all-portions success` |
| Constitution outcomes | `partial` | Valid and globally incompatible cases; ambiguous, undetermined and unsupported results absent |
| Equal payloads, different occurrences | `implemented` | `equal payloads distinct occurrences` |
| Constitution without encoding | `implemented` | `semantic constitution needs no encoding` |
| Exact versus relative reconstruction | `partial` | Exact only; relative SR3 unsupported |
| Local state conflicts with encoded source | `implemented` | `unencoded semantic local change` |
| Pairwise pass, global fail | `implemented` | `pairwise admission is not global admission` |
| Semantic and assembly round trips | `implemented` on canonical domain | `semantic round trip`, `assembly round trip`, exhaustive ten-value closure |
| Local expression modes | `unsupported` | No expression API |
| Historical stale payload | `implemented` | `stale source remains exact historically`, `mixed sources not current coherent` |
| Membership authority and change | `partial` | Join, leave, retirement and unauthorised change; replace/split/merge unsupported |
| Same endpoint, different history | `implemented` | `same values distinct histories` |
| Cyclic self-embedding rejection | `unsupported` | No quoted-payload parser |
| Resource or solver stop | `unsupported` | Finite model uses direct deterministic checks |
| Bottom-up disjoint changes | `implemented` | `bottom-up joint contribution`, order independence |
| Competing writes | `implemented` | `competing writes` |
| Replay and equivocation | `implemented` | duplicate idempotence, committed replay rejection, event equivocation |
| Stale base | `implemented` | `stale base` |
| Missing causal dependency | `unsupported` | No causal-DAG carrier |
| Commitment and refresh | `partial` | Candidate creation and canonical re-encoding only; no external commit protocol |
| Distributed failure/currentness | `unsupported` | No distributed model |

## Promotion consequences

The 34 internal checks and four `unittest` cases support only the mapped finite subset. They do not establish complete WPC-Core conformance, WPC-Evolution conformance, any WPC-Distributed capability, independent reproduction, production readiness, physical instantiation or superiority over simpler state-machine and event-log baselines.

The next executable priorities are the explicit `ConstitutivePresentation` and `epsilon` API with all constitution outcomes, contextual expression producing typed proposals, non-trivial normalisation, and causal-dependency handling. Distributed commitment should wait for a selected application and fault model.
