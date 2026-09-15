# MSC/0.1 return-to-author review request

Use this text when returning the formalisation to the author of the original
Recursive Extensional Coherence proposal. Attach or link the complete
`proposals/msc-0.1/` directory, especially the profile, schema, implementation,
fixtures and conformance matrix.

---

I have converted your proposed “Recursive Extensional Coherence” layer into a
standalone E7G-T research package for formal review:

https://github.com/E7GT-Ecosystem/E7G-T/tree/codex/msc-01-proposal/proposals/msc-0.1

The identifier was changed from `REC/0.1` to `MSC/0.1 — Multi-Scope Coherence`
because `REC/0.1` is already assigned to the Reasoning–Evidence Calculus in the
v0.14 candidate. This package does not create v0.15, change the v0.12.1
canonical reference, or impose product migration.

The formalisation makes these substantive decisions:

1. The core is limited to typed finite scope diagrams, link coherence,
   compatible scope families, pairwise/global obstruction, map commutation,
   access quotients, cross-scope invariants and reconstruction fibres.
2. Projection and local comparison maps are explicitly typed into a common
   carrier:

   ```math
   P_e:B_t\rightharpoonup V_e,
   \qquad
   C_e:B_s\rightharpoonup V_e.
   ```

3. The compatible-family construction and distinct closure outcomes are
   retained as the centre of the profile.
4. Your warning that pairwise coherence need not imply global closure is now
   exercised by an executable parity-cycle obstruction.
5. Access-induced quotients and SR0–SR4 strength separation are retained.
6. History envelopes, proposal lifts, capability regimes, fixed-point closure
   and recursive/unbounded families are preserved as proposed compositional
   extensions (`MSC-H`, `MSC-L`, `MSC-C`, `MSC-F`, `MSC-R`) rather than repeated
   inside the core.
7. Symbolically unbounded scope families are routed through SF/0.1 with finite
   evaluated windows; no completed infinity is inferred.
8. The WPC lineage ambiguity is recorded as a promotion dependency: lineage
   must be an explicit input or a deterministic derivation.

Please review the package for fidelity and formal correctness. In particular:

1. Does `MSC/0.1 — Multi-Scope Coherence` preserve the mathematical purpose of
   your proposal despite removing the word “recursive” from the core name?
2. Are the common-codomain types for `P_e` and `C_e` correct, or did your span
   intend a different relationship?
3. Is the definition of `Omega_D` faithful to your intended notion of a
   coherent family of bounded wholes?
4. Does the parity-cycle fixture correctly demonstrate your RE4 claim that
   pairwise compatibility need not produce global closure?
5. Is the fixed MSC-B1 partial-observation policy `co_undefined_equal`
   sufficiently precise? What additional condition would you require for
   stochastic observations in a later profile?
6. Is separating SR0–SR4 from access and authority faithful to the proposal?
7. Did narrowing the core and moving history, regime, lift and fixed-point
   material into extensions remove anything logically necessary for MSC-Core?
8. Is “lower-scope comparison map” correct for `C_e`, with “bridge” reserved
   for the complete common-codomain span?
9. Do the twelve MS laws preserve the intent of your proposed fifteen RE laws?
10. Identify any statement that overclaims existence, infinity, causation,
    authority, or empirical reality.

Please return findings in this form:

| Severity | Location | Finding | Exact proposed replacement |
| --- | --- | --- | --- |
| blocking / material / editorial | section, law, schema field or code path | explanation | replacement text, equation or behaviour |

Please also give one overall verdict:

- `faithful_and_ready_for_external_review`;
- `faithful_with_minor_corrections`;
- `material_revision_required`; or
- `proposal_intent_not_preserved`.

The executable checks are first-party bounded conformance only. Please do not
treat their passing as evidence of an externally instantiated scope hierarchy,
an actually infinite hierarchy, model-independent truth, or external product
value.

---
