---
title: "E7G-T v0.15 Experimental Canonical Release Manifest"
version: "0.15-experimental-MSC1"
date: "2026-09-25"
status: "Experimental canonical source; incomplete implementation and research gates"
baseline_commit: "86653557f5b5780a984f3a2dab226213ebbe3702"
---

# E7G-T v0.15 experimental release manifest

The [single experimental canonical kernel](E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md)
is the authoritative source edition for **new** E7G-T specifications. It
retains the v0.14 mathematical profile bodies, which carry the v0.13 WPC family and
v0.14 REC profile, and incorporates the complete later MSC/0.1 proposal.
The UC5 body retains its inherited historical text and normative/informative
distinctions. No old source file, implementation, schema, ID or API is
overwritten. See the [successor decision](docs/CANONICAL_SUCCESSOR_DECISION.md).

| Repository path | Role | SHA-256 |
|---|---|---|
| `E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md` | Self-contained canonical source | `2ff419f0cb41b9f4af894f4113c61cf7b44a77322594cc14f0f18566a02f990d` |
| `E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md` | Immutable former canonical source, revision RGP2 | `4c7784bcd653471a097329361b17b13c3b45e1592df6204243370ca0190935b1` |
| `E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md` | Immutable RWP1 draft predecessor | `ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe` |
| `E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md` | Immutable REC1 draft predecessor | `a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a` |
| `packages/wpc-0.2/E7G-T_WPC_v0.2_Reciprocal_Whole-Part_Profile.md` | Versioned WPC companion | `e1ebd7d3b1945f816fa21aee5d1c4802486d0b7cc2e097a99c96ec1c60d1cd3c` |
| `packages/rec-0.1/E7G-T_REC_v0.1_Reasoning-Evidence_Calculus_Profile.md` | Versioned REC companion | `52b88f24e8fbbd2aef7dc221978be844790ae1c476ea7133ceedef9fde0ebbc3` |
| `proposals/msc-0.1/E7G-T_MSC_v0.1_Multi-Scope_Coherence_Proposal.md` | Exact included MSC formal body | `07dba33fe194f0a346b33941f5c7292fcf7397c9f2a22815fc8e274ca68f9cb2` |

The kernel includes MSC §MSC.0–§MSC.13 as §X.21 without changing the
profile body after its original title and metadata. The latter remain
available in the separately pinned companion. The v0.14 source's retained
UC5 section between preservation markers is byte identical in v0.15.

## Profile and evidence dispositions

| Family | Source status | Implementation evidence and remaining boundary |
|---|---|---|
| EEC-Q, SF, CFS | Retained experimental mathematical profiles | Bounded models; all-input actual-code EEC-Q Python/IR-to-Lean link and general fidelity remain open. |
| RGP/0.2 | Inherited v0.13 successor; RGP/0.1 remains pinned to v0.12.1 | Only selected finite behaviour has executable and proof evidence. |
| WPC/0.1 and WPC-Core/0.2 | Distinct inherited profiles | Finite allocation model; no full whole–part conformance. |
| WPC-Evolution/0.1 | Separate optional profile | Partial candidate operations; commitment not established by reconciliation alone. |
| WPC-Distributed/0.1 | Separate optional profile | Unsupported; no distributed-runtime claim. |
| REC/0.1 | Inherited v0.14 proposed profile | REC-B1 finite first-party replay; no source-truth, domain-rule or AI-performance proof. |
| MSC/0.1 | Incorporated optional speculative proposal | MSC-B1 finite first-party model; no full profile, external existence, infinity or independent reproduction. |
| E7C/0.1 | Separate research build | Full calculus and cross-edition implementation links remain open. |

Source authority is distinct from profile conformance, formal implementation
refinement, empirical results and product adoption. An earlier kernel label
on a fixture is historical provenance, not a v0.15 execution result. No
existing consumer is migrated merely by this release.

## Reproduction

From the repository root, check the listed SHA-256 values with `sha256sum`.
Compare the inherited UC5 preservation block and MSC body with their pinned
sources; check the source edition audit before reusing an old E7C result:

```bash
python3 research/e7c-0.1/e7c_edition_source_audit.py
python3 -m unittest discover -s packages/wpc-0.2 -p 'test_*.py'
python3 -m unittest discover -s packages/rec-0.1 -p 'test_*.py'
python3 -m unittest discover -s proposals/msc-0.1 -p 'test_*.py'
```

Those checks assess the pinned predecessors and bounded companion packages.
They do not verify every v0.15 operator or discharge any E7C all-input link.
