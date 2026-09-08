---
title: "E7G-T Symbolic Family and Realisation Profile"
version: "0.1-experimental"
profile_id: "SF/0.1"
reference_model: "IC/0.1"
kernel: "0.12-experimental"
date: "2026-09-08"
author: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
status: "Experimental mathematical profile with an exact bounded prototype"
---

# E7G-T Symbolic Family and Realisation Profile v0.1

**Purpose:** make a finitely described family of possible configurations an object of computation; transform and extend that family; obtain a particular entity through a declared realisation rule; retain the family for further work.

This profile develops the proposed “hyperposition” intuition as symbolic mathematics. The family may contain infinitely many configurations. Its executable representation remains finite. Its realisation is a specified operation with inspectable success and failure conditions.

SF/0.1 is an optional profile of E7G-T v0.12. It is independently versioned from the kernel's EEC-Q/0.1 formal-sum profile. The accompanying **E7G-T_Symbolic_Families_v0.1.py** implements the bounded **IC/0.1** interval-and-circle model. The **E7G-T_Symbolic_Families_Validation_v0.1.json** file records the internal run.

## S.0 Scope and terminology

Capitalised MUST, MUST NOT, SHOULD and MAY express obligations on implementations claiming the corresponding capability. A supported model MUST state its expression grammar, parameter domains, constraints, identity rules, available solvers and limits. A declaration of SF compatibility must identify that model and its implemented operations.

| Term | Meaning |
|---|---|
| Symbolic family | A finite description of a set of admitted configurations |
| Hyperposition | Working research term for such a structured space of possibilities; no extra physical meaning is supplied |
| Realisation | Selection under declared criteria, yielding an entity only when the required selection is resolved |
| Residual family | The exact remaining family after the completed selection criteria |
| Family quote | An entity describing the entire family, without selecting a member |
| Operational phase | The inherited E7G-T inquiry-relative equivalence class; distinct from the family and from wave phase |

“Wave → particle” motivates the direction but is not the execution semantics. SF/0.1 has set semantics. It supplies neither amplitudes nor interference, and it does not claim a physical collapse mechanism. A future wave or quantum profile would need additional mathematical and operational rules. No quantum speed advantage is established by this prototype.

The mathematical definitions below are proposed conventions and consequences of those conventions. They are not claims of novelty over existing mathematics or of universal formal validity.

## S.1 Family definition and identity

Pin a configuration signature \(\Sigma\), semantic context and inquiry. A family is described by:

\[
H=\langle\Lambda,K,g\rangle_\Sigma,
\qquad
D_H=\{\lambda\in\Lambda:K(\lambda)\},
\qquad
\llbracket H\rrbracket=\{g(\lambda):\lambda\in D_H\}.
\]

\(\Lambda\) is the parameter carrier, \(K\) the admission constraints, and \(g\) a finite expression constructing a configuration from an admitted assignment. \(g\) must be defined on the admitted domain. The actual carrier, constraints and expressions are declared by the selected model.

This distinguishes three objects: the family description, its parameter assignments, and its image of configurations. Different assignments may yield the same configuration. Equal descriptions under a canonical syntax are not the same assertion as equal denotations under all admissible assignments.

An exact identity procedure is required for the supported concrete configurations and canonical family descriptions. General equality of arbitrary symbolic families is not assumed decidable. A fingerprint identifies a canonical description under a pinned model; it does not prove extensional equality with a differently described family.

An empty admitted domain yields an empty family. Unknown membership, an unavailable solver, a resource limit and an empty family MUST remain distinct outcomes. Absence of a witness is not proof of emptiness.

Every reference to one parameter in \(g\) uses the same assignment. A family with coordinates \(x=t\) and \(z=2t^2-1\) retains their dependence. A second occurrence of `t` does not create a second independent choice.

## S.2 Extension and transformation

**Dependent extension** adds structure using the existing assignment:

\[
\mathsf{Extend}_h(H)
=\langle\Lambda,K,\lambda\mapsto(g(\lambda),h(\lambda))\rangle.
\]

The output signature identifies what the new component means and how it is related to the original configuration. If the extension preserves the original fields, projection to those fields recovers \(g(\lambda)\) for every admitted assignment. This is a pointwise preservation law, not an automatic inverse for every later operation.

**Independent extension** introduces a separately scoped parameter \(\mu\in M\) and a product domain. **Constrained extension** introduces additional parameters with constraints that may relate them to \(\lambda\). An implementation MUST distinguish these cases. IC/0.1 implements dependent extension; general multivariate products and constraints remain outside that prototype.

**Transformation** composes the configuration map with a declared rule: \(\mathsf{Transform}_T(H)=\langle\Lambda,K,T\circ g\rangle\), where the transformation is defined on the admitted image. A transformation that is not defined everywhere needs an explicit domain restriction or rejection. Invalid assignments cannot be silently dropped.

Adding another coordinate need not add an independent degree of freedom. In the circle example, three coordinates still depend on one continuous parameter and a two-chart sign. Mathematical carrier dimension, parameter count, E7G-T order role and quotation rank are separately declared quantities.

## S.3 Projection, viewing, restriction and quotation

| Operation | Result | Selection or loss |
|---|---|---|
| `view(H, fields)` | A view retaining its source family | Hides fields in the display; does not replace the source |
| `project(H, fields)` | A new family whose configurations retain the named fields | Can identify formerly different entities |
| `restrict(H, constraint)` | A family with a smaller admitted parameter domain | Excludes assignments explicitly |
| `pack(H)` | A quote of the complete family | Selects no member |
| `realise(H, criteria)` | A result record, residual family and possibly one entity | Resolves only what the criteria determine |

All operations are pure in IC/0.1: their inputs remain available. Retaining the symbolic source records the model; it does not establish that an unknown physical quantum state can be copied or preserved through measurement.

Restriction is an input change. A realisation criterion is an explicit selection policy. Neither implies that excluded alternatives are physically nonexistent. A quote of an empty family remains a description; it differs from an empty family and from a realised numeric entity.

## S.4 Realisation semantics

A selection request supplies a finite ordered list of objective functions on configurations, each with a `max` or `min` direction. Objectives are applied **lexicographically**: the second optimises only among the first's winners, and so on.

Start with \(W_0=D_H\). For a maximisation objective \(f_i\), define:

\[
b_i=\sup_{\lambda\in W_{i-1}} f_i(g(\lambda)),
\qquad
W_i=\{\lambda\in W_{i-1}:f_i(g(\lambda))=b_i\}.
\]

For minimisation use the infimum. A model must establish the bound and its attainment, or return an appropriate unresolved/unsupported outcome. An optimiser is an implemented procedure, not an oracle attached to the word `realise`.

When all criteria complete, retain:

\[
H_R=\langle\Lambda,\lambda\in W_m,g\rangle,
\qquad R=\llbracket H_R\rrbracket.
\]

If \(R=\{e\}\), return the unique **entity** \(e\). More than one parameter assignment may still describe it. If \(R\) has at least two members, return ambiguity together with the residual family. No arbitrary representative is selected implicitly.

With no objectives, `realise` asks whether the family's existing image already contains exactly one entity. Thus a constant map over an interval can be uniquely realised even though it has infinitely many assignments.

### S.4.1 Outcomes

| Outcome | Required meaning |
|---|---|
| `UNIQUE` | The residual image is established to contain exactly one entity; return it and a membership witness |
| `AMBIGUOUS` | At least two distinct residual entities are established; return the residual family and distinct witnesses where available |
| `EMPTY` | The input family is established to have no admitted assignment |
| `UNATTAINED` | A finite optimal bound is established but no admitted assignment attains it |
| `UNBOUNDED` | The requested objective is established to have no finite bound in the requested direction |
| `UNDETERMINED` | The available reasoning cannot establish the requested property |
| `UNSUPPORTED` | The declared input is valid but the requested operation is outside implemented solver capabilities |
| `RESOURCE_LIMIT` | Exact evaluation stopped at a declared resource bound |

Malformed or out-of-grammar model inputs raise `InvalidInput` before execution. They are not empty families. IC/0.1's admitted continuous objectives are bounded polynomials on bounded domains, so it does not produce `UNBOUNDED`. Its supported uniqueness rules are decisive, so it does not produce `UNDETERMINED`; these outcomes are reserved in the general SF protocol for other models.

An unimplemented expression kind is rejected by the IC constructor/importer. A valid IC polynomial above the continuous solver's degree limit is accepted as data and yields `UNSUPPORTED` when that solver is requested.

After `UNSUPPORTED` or `RESOURCE_LIMIT`, earlier completed objective scores are diagnostic only. The prototype returns no final residual family because the full request has not been resolved.

### S.4.2 Order and purpose matter

Maximising x and then minimising z can differ from minimising z and then maximising x. Realisation need not commute with extension, transformation or projection. For any proposed rewrite, the source domain, mapped criteria, tie policy and failure behaviour must be checked.

For example, projecting a lifted circle to z alone identifies two maximising points. Its projected image can have a unique optimum while the full family still has two distinct optimal entities. A view showing z alone retains that ambiguity in its source.

## S.5 Exact interval-and-circle model IC/0.1

IC/0.1 fixes a small expression language with one real parameter \(t\) and a finite sign parameter \(s\in\{-1,1\}\):

- Domain: a bounded interval with rational endpoints and independently open/closed endpoints, or a finite set of rational points.
- Sign domain: an explicit subset of \(\{-1,1\}\).
- Coordinate expressions: rational polynomials in t of degree at most eight, and the registered expression \(s\sqrt{1-t^2}\).
- Circle-coordinate admission: all admitted t lie in \([-1,1]\).
- Objectives: named polynomial coordinates, with ordered `max`/`min` directions.
- Continuous solver: exact constant, linear and quadratic objectives.
- Finite-domain solver: exact evaluation of any admitted polynomial degree.
- Concrete entity values: exact rationals or canonical signed square roots of non-square positive rationals.

Polynomial arithmetic normalises coefficients. Rational square roots are reduced to rational values. The remaining radicals have only a sign and radicand, which gives an exact identity test within this restricted value grammar. General sums of radicals, trigonometric solving, arbitrary functions and host-language `eval` are not supported.

### S.5.1 Circle representation

The circle is represented by two charts:

\[
-1\leq t\leq1,\qquad s\in\{-1,1\},\qquad
x=t,\quad y=s\sqrt{1-t^2}.
\]

Together they represent the whole unit circle. At \(t=\pm1\), both sign assignments yield the same point. This duplication is retained at the parameter level and removed only when checking equality of resulting entities.

The extension \(z=\cos(2\theta)\) from the earlier trigonometric example becomes the polynomial \(z=2t^2-1\), using \(t=\cos\theta\). The prototype therefore executes that example without a general trigonometric solver or a point grid.

### S.5.2 Why the solver covers its stated interval domain

A nonconstant linear or quadratic polynomial on a bounded interval has its supremum and infimum among the endpoints of the closure and any derivative-zero point inside that closure. The implementation evaluates this finite candidate set exactly. It separately checks whether a winning candidate belongs to the admitted interval.

If an excluded endpoint is the sole winner, the result is `UNATTAINED`. If a closed endpoint or an interior critical point attains the same bound, the bound is attained. A constant objective retains the whole interval. These rules establish the implemented optimisation procedure's scope; evaluating a grid would not establish the same result.

Uniqueness is checked in configuration space. On a finite residual domain, the implementation evaluates and deduplicates exact entities. On a nondegenerate interval, constant coordinates give one entity. A nonconstant polynomial coordinate or the circle coordinate proves variation. Rational interior points are then used to produce two witnesses of that already-established variation. A degree-d nonconstant polynomial cannot take one value at d+1 distinct points; the circle coordinate at a fixed sign takes a given value at at most two parameter values. This supplies the finite witness bound used by the code.

### S.5.3 Limits

The prototype supports at most 32 coordinate fields and 32 ordered objectives, degree-eight polynomial data, 1,024 explicitly supplied parameter points and rationals within its 4,096-bit representation limit. `realise` also accepts a per-stage candidate budget, default 4,096. This is a count limit, not a hard wall-clock or total-memory guarantee.

Python resource exceptions remain possible; they must not be interpreted as successful computation. The API assumes immutable objects created through its constructors. Reflection that bypasses those constructors is outside the input model.

Only admitted model operations are claimed. General multivariate optimisation, arbitrary constraints, infinite sequences, general family equality and quantum lowering are unimplemented.

## S.6 Executable demonstration

Save the companion Python file locally and run:

```bash
python3 E7G-T_Symbolic_Families_v0.1.py
```

It prints the internal checks and exact demonstration records. The Python construction API is:

```python
t = Poly((0, 1))
H = circle()
H3 = H.extend(z=2 * t * t - 1)

result = realise(H3, Objective("z", "max"), Objective("x", "max"))
assert result.status == "UNIQUE"
# result.entity has x=1, y=0, z=1 as exact rational values.
# result.source still holds the complete extended family.
```

The first objective retains t=-1 and t=1; the second retains t=1. Both sign assignments then denote the same entity \((1,0,1)\). Removing the second objective produces `AMBIGUOUS`, with the two distinct entities \((-1,0,1)\) and \((1,0,1)\).

The demonstration also uses the selected entity to initialise a new family with \(x=1+t\), \(y=0\), \(z=1\), for \(-1\leq t\leq1\). Maximising x produces \((2,0,1)\). This executes a complete cycle from a family to an entity and into a new family, with each family retained separately.

For a negative example, let x=t on the open interval \((0,1)\). Its supremum is 1, but x=1 is not admitted. `realise(..., max x)` returns `UNATTAINED`; it does not return the excluded endpoint or a convenient approximate value.

For a constant family, let x=7 throughout \([-1,1]\). With no selection criteria, the result is `UNIQUE` because the configuration image is the singleton \(\{x=7\}\). A unique result is therefore not synonymous with narrowing to one latent assignment.

## S.7 Relationship to EEC-Q and operational phases

EEC-Q/0.1 uses finite signed rational combinations; SF/0.1 uses set-valued denotations represented by expressions. They are different profiles under the same kernel.

Suppose distinct configurations P and Q map to R. In EEC-Q, applying the linear map to \(\mathbf e_P-\mathbf e_Q\) gives zero. In SF, the image of the set \(\{P,Q\}\) is the singleton \(\{R\}\). The two results must not be interchanged.

An adapter from EEC-Q may explicitly extract the support of a canonical formal state, recording that coefficients and their algebra have been discarded. The reverse operation needs an explicit finite enumeration and coefficient assignment. An infinite symbolic family does not automatically become an EEC-Q finite-support state.

Both profiles retain the E7G-T distinctions between source and view, descriptions and entities, domains and unknowns, whole-family quotation and selection. Neither a family nor a quote is automatically an operational phase. A phase abstraction used during realisation must preserve the distinctions and operation availability that the criteria require; the kernel's domain-saturation and congruence conditions remain relevant.

Existing EEC-Q/FG3 programs retain their semantics. SF is opt-in and does not reinterpret their coefficients, cancellation or finite-rank rules. A symbolic family is a finite expression describing a potentially infinite image; this does not make its expression tree infinite or give it infinite quotation rank.

## S.8 Validation and next development boundary

The companion validation report records executable cases covering the lifted circle, ordered tie-breaking, ambiguity, exact interior optima, open-endpoint non-attainment, empty restrictions, constant families, projection versus viewing, quotation, exact radicals, unsupported solvers, limits, malformed inputs, interchange and repeated family/entity construction.

The algebraic solver justification in §S.5.2 and the executable checks serve different purposes: the former states why the bounded mathematical procedure covers its admitted cases; the latter checks its implementation on selected positive and negative cases. Neither establishes correctness of all symbolic computation or independent reproduction.

The immediate operating capability is: **describe an infinite family finitely, extend it while preserving dependence, realise a result under declared criteria, and reuse that result in further construction.**

The next useful expansion would be one additional exact carrier or solver selected by a concrete program that IC/0.1 cannot express. Candidates include jointly constrained multiple parameters, a general typed relational body, or an explicit amplitude profile. Each requires its own semantics and validation; additional physical or performance claims require their own evidence.

## S.9 Recorded internal validation

The reference run on **2026-09-08**, using Python **3.12.13**, passed **48 named checks**. The report contains the exact input formulas, source identity, residual families, membership witnesses, objective bounds and outcomes for the principal examples.

| Demonstration | Recorded outcome |
|---|---|
| Lift the circle and maximise z, then x | `UNIQUE`: (1, 0, 1) |
| Maximise z without the tie-break | `AMBIGUOUS`: two distinct entity witnesses |
| Maximise x on the open interval (0, 1) | `UNATTAINED`: supremum 1 |
| Seed a new family from the selected entity and maximise x | `UNIQUE`: (2, 0, 1) |

Companion code SHA-256: `15f23b124acc626dad48204677fbe0b7ed66afb1d9bd60d0afed479c040eeb0f`.

The result is internal validation of IC/0.1. Independent reproduction, a general symbolic solver and a complete programming language are not claimed.
