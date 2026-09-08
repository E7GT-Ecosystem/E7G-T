# E7G-T Kernel v0.9 Draft — Reference Specification with References

**Version:** 0.9 draft / reference-backed layer  
**Date:** 2026-06-29  
**Status:** non-canonical reference-backed draft kernel  
**Canonical kernel:** `E7G-T_Kernel_v0.9_RC1_Public_Reference_Specification.md`  
**Public posture:** source-anchoring layer for reviewer orientation; not the active RC1 kernel wording

---

## 0. Status and Use Posture

This document is the reference-backed companion to the E7G-T v0.9 kernel draft.

It is included to help public readers see which established fields E7G-T stands near, borrows caution from, or may later interface with.

It is **not** the canonical kernel.  
The canonical v0.9 RC1 kernel is:

```text
E7G-T_Kernel_v0.9_RC1_Public_Reference_Specification.md
```

E7G-T is a geometry-first modelling language and practical calculus.

It is **not** established mathematics.  
It is **not** empirical physics.  
It is **not** a proof system.  
It is **not** a Theory of Everything.  
It is **not** a replacement for domain expertise.

Its purpose is to make the following visible:

- entity;
- order;
- time posture;
- context;
- boundary;
- projection;
- preservation;
- loss;
- reconstruction status;
- bridge mode;
- claim strength;
- admissible use;
- next move.

---

## 1. Public Definition

> E7G-T is a geometry-first modelling language and practical calculus for making projection, loss, reconstruction, bridge mode, and admissible use visible.

Expanded:

> E7G-T helps users inspect representations before relying on them. It asks what a chart, AI answer, proof text, translation, model, legal summary, or dashboard preserves, what it loses, what source it points to, what claim strength it can support, and what the next responsible move should be.

---

## 2. Why This Reference Layer Exists

E7G-T uses words such as **projection**, **transformation**, **type**, **bridge**, **proof path**, **model**, **measurement**, **information**, and **translation**.

Many of these words already have strong meanings in established fields.

This file prevents overclaim by declaring a reference posture:

- E7G-T may stand near established fields.
- E7G-T may borrow caution from them.
- E7G-T may later attempt formal compatibility with them.
- E7G-T does not automatically inherit their authority.
- E7G-T must not imply identity with an established discipline unless the bridge is explicitly built.

---

## 3. Core Kernel Summary

### 3.1 Core question

> What do I do next with this concrete object, claim, proof, model, output, observation, system, or representation?

### 3.2 Core discipline

Before relying on a representation, identify:

1. entity;
2. order profile;
3. temporal regime;
4. context;
5. boundary;
6. operation;
7. preservation/loss;
8. reconstruction status;
9. bridge mode;
10. claim strength;
11. admissible use;
12. stop condition.

### 3.3 Minimum rule

Use the smallest level that changes the next move without hiding risk.

---

## 4. D-Order Summary

D-orders are modelling orders, not literal physical dimensions by default.

| Order | Practical reading |
|---|---|
| **D0** | mark, scalar, trace, pixel, result, accepted state |
| **D1** | path, sequence, interval, procedure, timeline segment |
| **D2** | text, diagram, chart, dashboard, screen, map, interface |
| **D3** | object, artefact, body, product, local system, structured proof artefact |
| **D4** | process, history, version, event sequence, lived development |
| **D5** | option set, possibility field, design space, proof search, scenario space |
| **D6** | rule, operator, tactic, function, method, protocol, verification rule |
| **D7** | purpose, interpretation, measurement frame, bridge governance, admissible-use frame |

### Rule

Do not treat a lower-order view as the whole higher-order source.

---

## 5. Temporal Regime Summary

Temporal regimes describe modelling posture, not ultimate metaphysics.

| Regime | Practical reading |
|---|---|
| **TR0** | no-time / atemporal treatment |
| **TR1** | local ordered sequence |
| **TR2** | coordinated time across sequences |
| **TR3** | alternatives, forecasts, proof search, scenarios |
| **TR4** | recurrence, rhythm, iteration |
| **TR5** | meta-time / model-time governing object-time |
| **TR6** | closed whole under declared closure context |

### Rule

State the temporal regime when time posture affects the claim.

---

## 6. Primitive Moves

```text
Place:       X : Dn @ TRi / C
Bound:       ∂X = B
Incide:      A ⋈_C B
Extend:      X ↑ n
Slice:       S_C^s(X)
Project:     π_C^{n→k}(X) = Y
Transform:   τ_T(X) = Y
Reconstruct: ρ_C(Y) ⇒ {X_i}
Bridge:      β_M^{A↔B}
Stop:        Stop(reason)
```

Notation records discipline. It does not create discipline.

---

## 7. Practical Laws

1. **Typing Before Operation** — place the entity before operating on it.
2. **Extension Is Not Projection** — building richer structure is not rendering a lower-order view.
3. **Projection Is Not Reconstruction** — a view of a source is not recovery of the source.
4. **Projection Loss Accumulates** — loss in a projection stack cannot be silently regained.
5. **Slice and Projection Need Not Commute** — changing the order of slicing and projection may change the result.
6. **Boundary Is Contextual But Not Arbitrary** — boundary may vary by use, but it must match the claim.
7. **Invariance Requires a Transformation Class** — no invariant claim is complete without declaring what transformations it survives.
8. **Bridge Claims Inherit the Weakest Link** — a bridge cannot support a stronger claim than its least-supported component.
9. **Empirical Language Requires Empirical Bridge** — reality-facing empirical claims require measurement, prediction or constraint, falsification condition, and evidence path.
10. **The Next Move Is the Practical Test** — the value of the model is shown by the next admissible action it clarifies.

---

## 8. Bridge Modes

| Mode | Meaning |
|---|---|
| **none** | no cross-domain bridge is claimed |
| **contemplative-what-if** | imaginative or reflective use |
| **philosophical-interpretation** | conceptual interpretation |
| **formal-analogy** | structural resemblance under declared mapping |
| **formal-compatibility** | compatible with recognised formal substrate under definitions |
| **formal-proof** | proof discharged inside declared formal substrate |
| **empirical-testable** | claim tied to observation, measurement, prediction, falsification, evidence |
| **authority-source-linked** | claim tied to an official or authoritative source under scope |

### Bridge rule

Do not raise claim strength without the bridge mode required for that strength.

---

## 9. Claim-Strength Ladder

1. intuition;
2. metaphor;
3. contemplative what-if;
4. philosophical interpretation;
5. formal analogy;
6. formal compatibility;
7. formal proof;
8. empirical-testable proposal;
9. empirically supported model;
10. validated operational method;
11. authority-issued decision.

### Upgrade rule

Do not upgrade a claim by rhetoric. Upgrade only by completing the required source, proof, test, authority, review, or validation path.

---

## 10. Core Anti-Overread Rules

- A projection is not the source.
- A summary is not the document.
- A chart is not the business.
- An AI answer is not the source.
- A translation is not source identity.
- A proof sketch is not proof.
- An accepted interface state is not necessarily human explanation.
- A legal/admin summary is not authority.
- An analogy is not proof.
- A model is not reality.

---

## 11. Formal Neighbourhood Discipline

A FormalNeighbourhoodCard should include:

```yaml
field:
E7GTElement:
resemblance:
establishedTool:
currentBridgeMode:
whatE7GTCanLearn:
whatE7GTMustNotClaim:
possibleFormalisationPath:
stopCondition:
```

### Neighbourhood rule

Neighbourhood is not identity.

An E7G-T arrow is not automatically a morphism.  
An E7G-T projection is not automatically a formal projection.  
An E7G-T bridge is not automatically a functor, proof, measurement protocol, legal authority, or empirical model.

---

# Selected Public Reference Anchors

## 12. Geometry and Projection

### Projective geometry

- Eric W. Weisstein, “Projective Geometry,” *MathWorld — A Wolfram Resource*.  
  <https://mathworld.wolfram.com/ProjectiveGeometry.html>

### E7G-T use

Projective geometry is an established mathematical field dealing with properties and invariants under projection. E7G-T uses “projection” more broadly as a modelling term.

### Kernel caution

Do not call an E7G-T projection a projective-geometric projection unless the mathematical structure is actually defined.

---

## 13. Category Theory

- Jean-Pierre Marquis, “Category Theory,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/category-theory/>

### E7G-T use

Category theory is a formal mathematical language of structures and structure-preserving relations. E7G-T may stand near category-theoretic thinking when it speaks about arrows, transformations, bridges, and diagrams.

### Kernel caution

E7G-T arrows are not automatically morphisms. Projection stacks are not automatically commutative diagrams. Bridges are not automatically functors.

---

## 14. Type Theory

- Thierry Coquand, “Type Theory,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/type-theory/>

### E7G-T use

Type theory is relevant to E7G-T’s placement discipline, proof-assistant ambitions, and “typing before operation” law.

### Kernel caution

`X : Dn @ TRi / C` is a modelling placement, not a formal type judgement unless a formal type-theoretic substrate is explicitly defined.

---

## 15. Proof Assistants and Lean

- *The Lean Language Reference*.  
  <https://lean-lang.org/doc/reference/latest/>

- Lean Programming Language official site.  
  <https://lean-lang.org/>

### E7G-T use

Lean is relevant to Proof-of-Path, proof-state slicing, tactic-as-transformation, and interface-as-projection work.

### Kernel caution

Proof-of-Path can document proof movement, but Lean or another proof assistant supplies the formal checking substrate. A Proof-of-Path record is not itself a formal proof.

---

## 16. Diagrammatic Reasoning

- Sun-Joo Shin, Oliver Lemon, and Mateja Jamnik, “Diagrams and Diagrammatical Reasoning,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/diagrams/>

### E7G-T use

Diagrammatic reasoning is relevant to E7G-T’s treatment of diagrams as projections that may carry reasoning structure.

### Kernel caution

A diagram may support reasoning, explanation, or even formal work in a declared diagrammatic system. But an informal diagram is not automatically proof.

---

## 17. Models and Scientific Representation

- Roman Frigg and Stephan Hartmann, “Models in Science,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/models-science/>

- “Scientific Representation,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/scientific-representation/>

### E7G-T use

These anchors support E7G-T’s caution that models, maps, diagrams, equations, dashboards, and simulations should not be treated as reality itself.

### Kernel caution

A model can be useful without being identical to its target. The source/view distinction must remain visible.

---

## 18. Measurement

- Luca Mari, Mark Wilson, and Andrew Maul, “Measurement in Science,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/measurement-science/>

### E7G-T use

Measurement is relevant to E7G-T’s claim that observations and recorded values are protocol-governed projections of systems into representational forms.

### Kernel caution

Measurement-facing claims require domain standards, protocols, uncertainty, calibration, and evidence. E7G-T can frame this; it cannot replace it.

---

## 19. Information, Compression, and Data

- Pieter Adriaans, “Information,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/information/>

### E7G-T use

Information theory and philosophy of information are relevant to projection, compression, loss, encoding, uncertainty, and representation.

### Kernel caution

Do not use “information,” “compression,” or “loss” as technical information-theoretic terms unless the relevant formal substrate is declared.

---

## 20. Translation and Translation QA

- ISO 17100:2015, “Translation services — Requirements for translation services.”  
  <https://www.iso.org/standard/59149.html>

### E7G-T use

Translation is one of the strongest practical domains for E7G-T because translation is visibly a purpose-bound projection from source text into target text.

### Kernel caution

E7G-T can help frame translation QA as invariant-preserving projection, but professional translation quality still depends on linguistic competence, domain expertise, revision, client specification, and applicable standards.

---

## 21. Source-Use Rule

When public-facing E7G-T text refers to an established field, it should use one of the following source postures:

1. **Neighbourhood** — E7G-T stands near this field but does not claim identity.
2. **Borrowed caution** — E7G-T uses the field to avoid overclaiming.
3. **Formalisation candidate** — E7G-T may later be formalised using tools from this field.
4. **Application domain** — E7G-T may be applied to artefacts in this field, without replacing the field.
5. **Stop condition** — the field has stronger tools, so E7G-T should route the user back to those tools.

---

## 22. Public-Reference Rule

Use internal project documents to reason.

Use public sources to support public claims.

Use domain experts to review domain-facing applications.

Use formal substrates to make formal claims.

Use empirical protocols to make empirical claims.

---

## 23. Relationship to RC1

This file should be treated as a **reference/source layer**, not as the canonical kernel.

For active modelling, quote:

```text
E7G-T_Kernel_v0.9_RC1_Public_Reference_Specification.md
```

For public-source anchoring, quote this file only where external reference posture is needed.

---

End of reference-backed v0.9 draft kernel.
