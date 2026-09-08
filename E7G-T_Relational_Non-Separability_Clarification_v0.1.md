---
title: "E7G-T Relational Non-Separability Clarification"
version: "0.1"
status: "Informative companion note; not part of canonical kernel conformance"
kernel_reference: "E7G-T v0.12 experimental canonical, revision CFS1"
language_convention: "British English"
---

# E7G-T Relational Non-Separability Clarification v0.1

## 1. Purpose and status

This note gives a disciplined, non-physical meaning to the intuition that a
whole may not be recoverable from isolated descriptions of its parts. It does
not modify the E7G-T v0.12 canonical kernel, introduce a new executable
profile, or add a conformance obligation.

The note deliberately uses **relational non-separability**, not
**entanglement**. Quantum entanglement has established mathematical and
experimental meanings that do not follow from ordinary relation, dependence,
correlation, shared context or holistic description.

## 2. Inquiry-relative definition

Let `E` be a declared joint entity under semantic context `C` and inquiry `I`.
Let

```text
pi_1(E), ..., pi_n(E)
```

be component views that hide some or all connecting relations. Let `P_I` be
the structure protected by the inquiry and let `Q_I` be its declared
equivalence criterion.

`E` is **relationally separable for `(C, I, P_I, Q_I)`** when a declared
composition or reconstruction procedure can recover an entity equivalent to
`E` under `Q_I` from the component views, while preserving `P_I` and without
silently inventing cross-component relations.

`E` is **relationally non-separable for `(C, I, P_I, Q_I)`** when the available
component views do not determine such a reconstruction and the hidden
connecting relations materially affect `P_I`, the phase classification or the
next responsible move.

If the available model or evidence cannot establish either condition, the
result is **undetermined**. Non-separability is therefore not inferred merely
from complexity, proximity, similarity, correlation or lack of information.

This property is inquiry-relative. A document may be separable for word-count
estimation but non-separable for legal-effect translation. A circuit may be
separable for gate inventory but non-separable for a declared quantum-state
criterion supplied by an appropriate quantum profile.

## 3. Existing kernel routes

The clarification routes to existing E7G-T disciplines rather than creating a
parallel calculus:

| Question | Existing route |
|---|---|
| Which relations join the components? | Configuration relation and interface declarations |
| What does separating them hide? | View/projection and preserve/lose account |
| Which wholes fit the isolated views? | Reconstruction fibre |
| Does the ambiguity alter operational classification? | Phase-candidate analysis under a pinned criterion |
| Is dependence shared or independent? | Dependent, independent and constrained extension |
| Can marginals recover the joint construction? | EEC-Q joint-state and marginal distinction where that profile is selected |
| May a conclusion cross contexts or domains? | Bridge mode and stop conditions |

SF family membership, EEC-Q coefficient arithmetic and CFS nesting do not by
themselves establish relational non-separability. The selected model must state
the component views, hidden relations, reconstruction rule, protected
structure and decision criterion.

## 4. Minimal assessment record

An analysis using this clarification should record at least:

```yaml
relationalNonSeparabilityAssessment:
  entityRef:
  semanticContext:
  inquiry:
  components: []
  componentViewRefs: []
  connectingRelations: []
  hiddenBySeparation: []
  protectedStructure: []
  reconstructionProcedureRef:
  equivalenceCriterionRef:
  reconstructionCandidates: []
  result: separable | nonSeparable | undetermined
  evidenceRefs: []
  preserve:
  lose:
  sourceReturnCondition:
  prohibitedInferences: []
```

The result should change a next move. A `nonSeparable` result may require a
joint review, restoration of relation-bearing context, a stronger view or a
domain specialist. An `undetermined` result requires more evidence, a better
model, a repaired boundary or abstention. It must not be rewritten as a
positive universal claim.

## 5. Translation example

Consider:

> The licence remains valid only while both the insurance and certification
> requirements are met.

Separate phrase-level views may preserve `licence valid`, `insurance
requirement` and `certification requirement` while hiding:

- the `only while` dependency;
- the joint `both` condition;
- the scope of `are met` over the two requirements.

For an inquiry concerning legal effect, independently acceptable phrase
translations do not necessarily determine an acceptable sentence-level
translation. The source is relationally non-separable for that inquiry when
the hidden scope and conjunction relations change the licence condition.

The next responsible move is not to invoke quantum language. It is to restore
the joint source view, preserve the dependency and scope relations, compare
the target against that structure, and escalate if several materially
different reconstructions remain.

## 6. “Everything is connected” boundary

E7G-T can investigate a proposed connection; it does not assume one. A usable
connection claim must identify:

1. the connected entities;
2. the typed relation;
3. its semantic and temporal scope;
4. its evidence or stipulated model basis;
5. the inquiry for which it matters;
6. what projection hides it;
7. what conclusion is and is not licensed.

The absence of a recorded relation may mean no relation, an out-of-scope
relation, an unknown relation or a lossy view. These states must not be
collapsed. Conversely, the presence of one relation does not establish that
all entities are connected, that the relation is causal, or that it is
physically fundamental.

## 7. Prohibited inferences

Relational non-separability alone does not establish:

- quantum entanglement;
- a quantum implementation or computational advantage;
- physical interaction or action at a distance;
- causal dependence;
- statistical dependence or probability;
- topological connectedness;
- inseparability under every inquiry;
- consciousness, metaphysical unity or a universal field;
- the proposition that everything is connected.

A domain profile may establish one of these only by supplying its own accepted
mathematics, observations, bridge rules and evidence. The general E7G-T term
then describes the modelling posture; it does not replace the domain result.

## 8. Adoption rule

Use this clarification only when separating a joint entity creates a material
reconstruction, preservation or decision problem not already resolved by an
ordinary relation statement. Otherwise, use the simpler existing kernel
vocabulary.

Promotion into the canonical kernel would require controlled examples showing
that the term changes a real next move across materially different domains and
does not merely rename dependence, context or projection loss.
