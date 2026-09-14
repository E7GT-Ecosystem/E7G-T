# E7G-T source-repository alignment

Direction: `E7-ECO-DIR-2026-09-14.1`  
Baseline reviewed: main `8e3d8d97c59c6fafd6d621779a45f15bb1dc0555`  
Candidate branch: `codex/v013-rwp1-package`  
Status: `CANDIDATE_ALIGNED_IN_DESIGN`; independent reproduction and product adoption remain unestablished.

## Source and profile status

The published experimental canonical source remains `E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md`, revision RGP2. `E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md`, revision RWP1, is a self-contained candidate successor and does not silently migrate consumers.

| Profile or component | Disposition |
|---|---|
| EEC-Q/0.1, SF/0.1 and CFS/0.1 | retain |
| RGP/0.2 kernel material | adapt to reciprocal whole–part terminology while preserving separate profile identity |
| WPC/0.1 | retain as legacy compatibility material |
| WPC-Core/0.2 | add as proposed; bounded implementation partial |
| WPC-Evolution/0.1 | add as optional proposed capability; bounded implementation partial |
| WPC-Distributed/0.1 | add as optional proposed capability; implementation unsupported |
| FG3, IC, CG3 and RGP-B1 models | retain unchanged |
| Preserved UC5 body | retain unchanged from the v0.12.2 predecessor |
| Existing IDs, APIs and historical specifications | retain |

No replacement or retirement is authorized by this record.

## WPC implementation boundary

The WPC allocation model demonstrates finite constitution, canonical whole encodings, exact bounded closure, distinct occurrence identity, bottom-up disjoint proposals, global-constraint rejection, basic join/leave transitions, event replay/equivocation checks and historical stale-payload distinction. It passes 34 internal checks and four external first-party tests.

It omits the general constitutive-presentation and extraction API, ambiguous constitution, relative reconstruction, contextual expression, split/merge, general causal DAGs, rule evolution, distributed commitment and arbitrary solvers. Passing results do not establish full profile conformance, independent reproduction, external instantiation, production readiness or product value.

## Repository responsibility and next gate

Preserve immutable published editions, exact manifests, conformance cases and attribution. Consumers must pin source/profile/model editions and state scope, limits, preservation/loss and migration effects.

Promotion requires formal review, a normative interchange schema, implementations and negative tests for every claimed capability, independent reproduction and one end-to-end comparison against a simpler state-machine or event-log baseline. Shared cross-product contracts still require two concrete consumer mappings without semantic distortion.
