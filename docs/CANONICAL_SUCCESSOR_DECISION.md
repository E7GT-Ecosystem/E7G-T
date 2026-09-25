# Unified experimental canonical successor decision

Direction: `E7-ECO-DIR-2026-09-15.1`
Source baseline: main `86653557f5b5780a984f3a2dab226213ebbe3702`
Successor: `E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md`, revision `MSC1`.

This release deliberately makes one new experimental canonical **source** for
future E7G-T specifications. It does not complete E7C, prove full profile
conformance, change an existing wire edition, or migrate a consumer by default.
The predecessor files remain immutable and usable under their original pins.

| Source or component | Decision | Preservation and migration |
|---|---|---|
| UC5 constitutional body | retain | Same body between preservation markers; informative pilots remain informative. |
| v0.12.1 EEC-Q/0.1, SF/0.1, CFS/0.1 | retain | Exact rational and dependency meanings remain; old edition identifiers and fixtures remain pinned. |
| v0.12.1 RGP/0.1, revision RGP2 | retain as historical profile | v0.13's RGP/0.2 is a distinct successor; the revision label is not a profile identity. |
| v0.13 RGP/0.2, WPC/0.1, WPC-Core/0.2 | adopt into successor source | Keep original profile identifiers, distinct lineage and explicit capability vectors. |
| v0.13 WPC-Evolution/0.1 | retain as separate optional proposal | A candidate successor is not a committed whole. |
| v0.13 WPC-Distributed/0.1 | retain as separate optional, unsupported profile | No distributed runtime or distributed conformance claim. |
| v0.14 REC/0.1 and REC-B1/0.1 | adopt into successor source | Four information statuses and witnesses remain; no source-truth or performance inference. |
| Later MSC/0.1 and MSC-B1/0.1 | integrate the complete formal proposal into §X.21 | Still optional speculative research with a bounded first-party model and an open promotion gate. |
| REC-EVAL, relational non-separability proposal, E7C/0.1 | retain separately at their pinned status | No unpublished or incomplete proposal becomes normative merely by the new edition. |

An E7C source registry, hash, adapter, test, or theorem pinned to v0.12.1,
v0.13 or v0.14 stays attached to that edition. It must not be relabelled
v0.15 without a separate edition-specific admission and semantic comparison.
The required EEC-Q, SF, CFS, RGP, WPC, MSC and REC completion gates remain
open, including the Python/IR-to-Lean actual-code correspondence.

Affected consumers include E7C research, the existing profile packages,
downstream product adapters and documentation. Their data, source pins, IDs,
APIs, schemas and hashes remain unchanged. New consumers can choose the
v0.15 source explicitly; existing consumers record `experimental`, `adopted`,
`deferred` or `not_applicable` at their own declared capability boundary.

Source canonicalisation, profile conformance, independent reproduction and
empirical benefit are separate decisions. This decision supplies the first.
