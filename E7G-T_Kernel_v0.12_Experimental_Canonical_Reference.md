---
title: "E7G-T Unified Geometry-Thinking Kernel"
subtitle: "Executable Extension and Composition of Geometric Configurations"
version: "0.12-experimental"
date: "2026-09-08"
revision: "CFS1"
author: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
license_url: "https://creativecommons.org/licenses/by-sa/4.0/"
status: "Experimental canonical reference; explicit formal calculus with bounded executable reference models"
base_version: "0.11-UC5"
calculus_profile: "EEC-Q/0.1"
optional_symbolic_profile: "SF/0.1"
optional_combined_profile: "CFS/0.1"
combined_reference_model: "CG3/0.1"
symbolic_reference_model: "IC/0.1"
example_model: "FG3/0.1"
language_convention: "British English"
normativity: "Part I defines v0.12 scope and conditional EEC-Q, SF and CFS executable-profile obligations. Part II preserves the UC5 reference text and its existing normative/informative distinctions. Appendices V and VI contain limited implementation and validation accounts. Canonical means the current authoritative v0.12 experimental reference; it does not assert stable adoption, production readiness or maturity-gate completion."
ai_use: "Treat E7G-T as a geometry-first modelling language with an experimental constructive and executable direction. Distinguish entities, descriptions, configurations, formal combinations, quoted constructions, views and phases. Apply EEC-Q, SF, or the optional CFS combined family-state profile only when explicitly selected. Distinguish SF set-valued families and realisation from EEC-Q signed combinations. Preserve joint alternatives, explicit interfaces, domain conditions and loss accounts. Do not replace the constructive objective with evidence reporting alone. Do not infer physical dimensions, quantum implementation, computational advantage or general correctness from the formal calculus or example model."
---

# E7G-T Kernel v0.12 — Experimental

**Executable Extension and Composition of Geometric Configurations**

**Authors:** Alexander Gregory Wingate and Oleksandr Razinkov
**Copyright:** © 2026 Alexander Gregory Wingate and Oleksandr Razinkov
**Licence:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

> **v0.12 working definition.** E7G-T is a geometry-first modelling language and practical calculus for constructing, extending, combining, transforming and viewing bounded relational entities, and for examining their preservation, loss, histories and inquiry-relative phases. Its experimental executable profile makes families of configurations and whole constructions available as objects of computation.

> **Constructive question.** What can this entity become when its internal structure, connections, alternatives and rules can themselves be extended and combined?

The inherited practical question remains relevant: what does a representation preserve or lose, which differences matter, and what use does the result support?

## Reading map

| Part | Content | Role |
|---|---|---|
| I, §§X.0–X.17 | v0.12 definitions, rules, examples, implementation contract and migration | New experimental specification |
| Appendices V–VI | Runnable finite example models and validation scopes | Executable companions, with explicitly limited coverage |
| II, UC5 §§0–20 and Appendices A–C | Complete inherited reference body | Constitutional context, temporal geometry, phases, overlays and prior examples |

References written **UC5 §n** point into Part II. References written **§X.n** point into Part I. The source's historical front matter is recorded before Part II; only the front matter at the beginning of this document describes v0.12.

# Part I — Executable Extension and Composition

## X.0 Status, purpose and normative boundaries

This version develops E7G-T's original constructive direction into an explicit mathematical specification. A configuration can be constructed; several configurations can be combined formally; their extensions can depend on shared choices; a complete construction can become an entity inside a larger one. The intended result is an implementable calculus that can underpin a programming language.

The geometric starting point is structural: entities have boundaries, incidence, interfaces and ways of changing. A dot, line, surface or solid may be a useful representation, but the semantics reside in declared structure and operations. A visual shape alone does not define a class, a computation or a quantum state.

The following distinctions govern this version:

| Layer | What is specified | Status |
|---|---|---|
| Inherited constitution | Entity, context, inquiry, boundary, projection, phase and bridge disciplines | Retained from UC5 |
| Executable extension and composition, EEC | A typed operation contract for configurations, families, joints and reification | New experimental definitions |
| EEC-Q/0.1 | One exact rational-coefficient interpretation of that contract | New selected mathematical profile |
| FG3/0.1 | A finite labelled-graph example model and executable checks | Implemented subset in Appendix V |
| SF/0.1 and IC/0.1 | Optional symbolic families and realisation, with an exact interval-and-circle prototype | Added in §X.16; independent from signed-sum semantics |
| CFS/0.1 and CG3/0.1 | Optional SF-outside/EEC-inside family-state semantics and bounded graph prototype | Added in §X.17; composes the two profiles without identifying their meanings |
| Geometric language, editor, compiler and OS | Potential applications of the calculus | Development directions; not delivered implementations |

**MUST**, **MUST NOT**, **SHOULD** and **MAY** have the obligation meanings used in UC5. An EEC-Q requirement applies only to an implementation or derivation declaring that profile. SF requirements apply only when SF is selected; CFS requirements apply only when the combined profile is selected. Each supported model and capability scope must be declared. Ordinary E7G-T analyses do not acquire a requirement to use rational coefficients, finite graphs, cancellation or this execution model.

Part I governs v0.12 version status and the new profile. Part II governs inherited concepts except for the explicit refinements listed in §X.14. Nothing here promotes UC5's informative observation, temporal-orientation, topology or relative-support pilots to the normative constitutional core.

The new equations are stipulated definitions or propositions derived under stated assumptions. They are not asserted to be mathematically unprecedented. The example model demonstrates that a useful finite interpretation can be executed; it is not a proof of consistency of the entire E7G-T framework.

The calculus permits speculative mathematical development on ordinary computers. It does not assume that a formal combination is a physically preparable quantum state. A quantum interpretation would require its own state space, allowed operations, measurement semantics and compiler mapping. No such mapping, speed advantage or extension of physical measurement limits is established by this version.

## X.1 Entities, carriers and the meanings of extension

### X.1.1 Inherited configuration envelope

The UC5 configuration envelope remains:

\[
\Gamma=\langle N,R,J,K,A,Ev,U\rangle.
\]

Here entities or local objects, typed relations, interfaces, constraints, attributes, evidence and unknowns retain their UC5 §3.6 meanings. An executable profile supplies a concrete representation for an admitted subset of these descriptions. It MUST declare what it cannot encode.

A profile pins a semantic context \(C\), an inquiry \(I\), a carrier signature \(\Sigma\), and an admission predicate. Write \(B_\Sigma\) for the set of admitted, exactly identifiable configurations of one signature. A signature states entity and relation kinds, interfaces, attribute types, identity rules and constraints. Different signatures MUST NOT be silently pooled into one state space.

Omission is explicit. An unknown attribute is an `unknown` value with declared meaning, not a missing node, false predicate, empty state or coefficient zero. For a profile with decidable admission, a condition it cannot decide produces `unsupported` or `undetermined` at the validation boundary; it is not silently accepted as true.

### X.1.2 Four distinct kinds of structure

| Term | Meaning in v0.12 | What does not follow automatically |
|---|---|---|
| Structural extension | Adding entities, incidence or interfaces to a configuration | Increase in Euclidean dimension |
| Variation | Specifying several configurations and their combination semantics | Independence, probability or quantum preparation |
| Reification, also called construction lifting | Making a finite construction an explicit entity with an interface | Linear behaviour or execution of its contents |
| Carrier dimension | Dimension supplied by a declared mathematical substrate | Equality with nesting depth or a D-role number |

D0–D7 and TD0–TD7 remain modelling roles under UC5 §5. The executable hierarchy has a separate finite **rank**, introduced in §X.7. Rank can grow beyond seven; this does not redefine D7 or invent additional physical dimensions. A relationship graph does not automatically supply a surface, volume, topology or metric.

### X.1.3 Symbol bindings

A glyph or textual name can refer to an entity, configuration, whole state, operator or history. Its binding MUST include the referenced sort, signature and immutable definition edition. The same visible glyph with a different binding is a different program reference.

Moving the camera or changing a glyph's font is a viewing operation unless the language explicitly makes orientation or shape a semantic input. A 3D interface can therefore display the calculus without making display coordinates the execution semantics.

## X.2 Exact formal combinations: EEC-Q/0.1

### X.2.1 Carrier and coefficients

For each signature, define the free rational vector space with finite support:

\[
\mathcal F_\Sigma=\mathbb Q^{(B_\Sigma)},\qquad
S=\sum_{\Gamma\in B_\Sigma}a_\Gamma\,\mathbf e_\Gamma.
\]

The basis symbol \(\mathbf e_\Gamma\) denotes a configuration. It is distinct from the phase class \([\Gamma]_Q\), from a description of \(\Gamma\), and from a physical state vector. Finite support means only finitely many coefficients are nonzero. The basis carrier itself need not be finite.

The coefficients are exact rationals. They express the formal combination selected by this profile. They are **not** the relative-support values of UC5 §9.15 and do not carry probability, plausibility, frequency or physical-amplitude semantics. Implementations MUST NOT convert a support score into a coefficient without a separately declared conversion and justification.

Addition and scalar multiplication are coefficientwise. Coefficients of the same basis configuration are added; zero coefficients are removed. The zero state is the empty coefficient map. A basis configuration representing an empty structure, when admitted, still has its own basis vector and is not the zero state.

For example, \(\mathbf e_P-\mathbf e_P=0\), whereas \(\mathbf e_P-\mathbf e_Q\ne0\) for distinct admitted \(P,Q\). No normalisation is automatic. Replacing all coefficients by non-negative values, their magnitudes or probabilities changes the profile.

### X.2.2 Identity and canonicalisation

A profile MUST give a terminating procedure for exact identity in its supported representation. In a finite labelled relational representation this includes stable entity IDs, relation kinds and endpoints, semantic attributes, interface declarations, constraints and any semantically retained branch labels. Ordering of sets and rational-number encodings is canonicalised.

Graph isomorphism, visual resemblance, equal output, equal support and inquiry-relative phase equivalence are not exact configuration identity. Renaming or quotienting requires an explicit map. A digest is an index into a canonical definition, not a substitute for that definition and its identity checks.

Imported terms MUST be syntax- and admission-checked before cancellation. Two malformed terms with opposite coefficients do not validate each other. A supplied malformed zero-coefficient term is also rejected. Once inputs are admitted and canonicalised, subsequent operators act on their nonzero support; a valid term cancelled earlier is no longer an execution branch.

Semantic metadata participates in identity. Diagnostic derivation records may live outside it, but this separation MUST be declared. A record that survives formal cancellation documents a calculation; it does not mean that an operational branch survived that cancellation.

### X.2.3 A useful meaning for “multi-superposition”

Within this research direction, **multi-superposition** is a working name for formal alternatives that may concern node attributes, relationships, whole configurations, histories, operator choices and nested constructions. EEC-Q gives one exact interpretation of some of these combinations.

The term does not introduce an additional physical effect. At a fixed rank and signature there is one finite formal state; alternatives within alternatives require either explicit joint dependence or quotation of a lower-rank state. Nesting alone does not determine multiplication of coefficients or create independent choices.

## X.3 Typed operators and execution outcomes

The core sorts are:

- `Config[Σ]`: one admitted configuration;
- `State[Σ]`: one finite formal combination in \(\mathcal F_\Sigma\);
- `Joint[Σ₁,…,Σₙ]`: a formal combination over admitted tuples, with their dependence retained;
- `Rule[Σ→Τ]`: a finite typed operator description with a declared domain;
- `Quote[r,σ]`: an immutable entity describing a construction of sort \(\sigma\) and rank \(r\);
- `View[σ]`: a representation retaining an explicit reference to its source;
- `Phase[Σ,Q]`: a phase class under a pinned equivalence criterion.

`Config` injects into `State` as \(\Gamma\mapsto\mathbf e_\Gamma\). There are no implicit coercions from `View`, `Phase` or `Quote` into an executable `State`.

For a total deterministic configuration map \(f:B_\Sigma\to B_\Tau\), its linear extension is:

\[
f_*S=\sum_\Gamma a_\Gamma\mathbf e_{f(\Gamma)}.
\]

Equal resulting configurations are collected. This is a map of formal states, not necessarily a reversible transformation or a physical operation.

For a partial map \(f:D_f\subseteq B_\Sigma\to B_\Tau\), **strict execution** is defined only when \(\operatorname{supp}S\subseteq D_f\). It checks every supported configuration and returns the whole result or a domain failure. It MUST NOT discard invalid branches, retain only positive coefficients or renormalise the remainder. On zero support it succeeds with zero after checking the operator's declared type.

The execution protocol distinguishes:

| Outcome | Meaning |
|---|---|
| `success(state)` | The declared operation completed under the pinned profile |
| `invalid_input` | Input syntax, typing, identity or admission failed |
| `domain_error` | At least one supported argument is outside the operation's domain |
| `unsupported` | A required sort, predicate or operation is unavailable |
| `resource_limit` | The implementation stopped before computing the exact result |

The last four outcomes are not algebraic zero. Arithmetic allocation or resource failures MUST NOT be reported as successful empty states. Approximate computation requires a separate profile and an error account.

## X.4 Extension of independent configurations and states

### X.4.1 Configuration-level gluing

Retain UC5 §8.14 notation:

\[
e_J(\Gamma,\Delta)=\Gamma\oplus_J\Delta.
\]

The declaration \(J\) specifies interface matches or newly created relations, entity identity scope, overlap and deduplication, constraint policy, result boundary and the admitted output signature. Compatibility is checked before constructing the result.

A concrete gluing implementation MUST specify whether inputs are disjointly named instances or intentionally share identities. It MUST NOT use accidental ID collisions to merge entities. Permitted overlaps must agree on all retained semantic fields. Relations incident on removed or fused entities need an explicit rewriting rule.

One straightforward relational implementation takes a namespaced union, performs only declared compatible identifications, adds declared typed connections, checks constraints, and canonicalises. This is a profile choice. Neither the general kernel nor the word “gluing” implies a topological pushout.

### X.4.2 Independent composition

For declared independent operands
\(S=\sum_i a_i\mathbf e_{\Gamma_i}\) and
\(T=\sum_j b_j\mathbf e_{\Delta_j}\), define:

\[
S\boxtimes T=\sum_{i,j}a_i b_j\mathbf e_{(\Gamma_i,\Delta_j)},
\qquad
\mathsf{Extend}_J(S,T)=(e_J)_*(S\boxtimes T).
\]

All pairs in the support of the tensor product MUST be admitted by \(e_J\). Otherwise strict extension fails. Selecting compatible pairs first is a different, explicit restriction operation (§X.6).

The independence declaration licenses this factorised joint combination. It is not established by different variable names, separate views or two reads of the same state. When two operands originate in the same unresolved choice, use the joint source described next.

On a domain where all required pairs are admitted, this extension is bilinear:

\[
\mathsf{Extend}_J(aS+bT,U)
=a\mathsf{Extend}_J(S,U)+b\mathsf{Extend}_J(T,U).
\]

This is an equality of values on that common domain. It does not justify rewriting partial programs whose failure behaviour differs after cancellation.

## X.5 Shared alternatives and variable connections

### X.5.1 Joint state as the authoritative object

For dependent components the primitive input is a joint state:

\[
W=\sum_{i,j}c_{ij}\mathbf e_{(\Gamma_i,\Delta_j)}.
\]

Its extension is \((e_J)_*W\). The joint coefficient appears once. Marginal states, obtained by explicit coordinate maps, generally do not determine \(W\). Multiplying those marginals invents a different joint state unless a factorisation is supplied.

For a shared two-way choice, suppose:

\[
W=2\mathbf e_{(\mathrm{round},\mathrm{red})}
-\mathbf e_{(\mathrm{square},\mathrm{blue})}.
\]

Gluing yields those two alternatives with coefficients \(2,-1\). Multiplying its marginals instead would introduce four pairs with coefficients \(4,-2,-2,1\), including round–blue and square–red. That result is a different program.

### X.5.2 Choice environment and scope

An implementation may retain choices symbolically instead of expanding them. A choice ID identifies one variable and its finite domain; several references to the same ID use the same assignment. Two IDs do not by themselves establish a product distribution or coefficient rule: the joint table or factorisation still supplies that rule.

For exact interchange, any symbolic choice representation MUST specify its finite assignment space \(\Omega\), coefficient function \(w:\Omega\to\mathbb Q\), and configuration construction \(b:\Omega\to B_\Sigma\), with meaning:

\[
\sum_{\omega\in\Omega}w(\omega)\mathbf e_{b(\omega)}.
\]

Assignments yielding the same semantic configuration are collected. If assignment identity must remain accessible after execution, it must be included in the configuration itself. A diagnostic row number cannot silently prevent cancellation.

### X.5.3 Alternatives in the connection pattern

Connections may also vary:

\[
W_J=\sum_{i,j,k}c_{ijk}
\mathbf e_{(\Gamma_i,\Delta_j,J_k)},\qquad
\mathsf{Join}(W_J)=\sum_{i,j,k}c_{ijk}
\mathbf e_{\Gamma_i\oplus_{J_k}\Delta_j}.
\]

Every supported triple needs a valid, typed gluing declaration. No factorisation of \(c_{ijk}\) is assumed. This is where a program can act on alternatives in its relational structure rather than only on values stored in fixed nodes.

Rule alternatives work similarly. A joint state of a finite rule description and an argument can be mapped by evaluation, once every rule is admitted and terminating in the selected sublanguage. A quoted rule is inert data until this explicit evaluation step. Arbitrary host-language source strings are not rules in EEC-Q/0.1.

## X.6 Viewing, identification, restriction and cancellation

These operations have different execution semantics even when the same reduced drawing could represent their outputs.

### X.6.1 View without replacing the source

\(\mathsf{View}_\pi(S)\) returns a source reference, a viewing declaration and a representation of the selected structure. It does not replace \(S\) or collect its coefficients under the identity of the displayed objects. Multiple source configurations may have the same display. Their distinctions remain available through the source reference.

The view MUST state hidden or coarsened information and source-return conditions as in UC5 §6.6. It cannot be used as a state argument through implicit conversion.

### X.6.2 Identify through an explicit map

\(\mathsf{Identify}_f(S)=f_*S\) replaces each basis configuration by a declared target configuration. If \(f\) removes a semantic distinction, previously different basis configurations can coincide and their coefficients can cancel.

For \(P\ne Q\) with \(f(P)=f(Q)=R\):

\[
f_*(\mathbf e_P-\mathbf e_Q)=0,\qquad
f_*(\mathbf e_P+\mathbf e_Q)=2\mathbf e_R.
\]

This behaviour is the algebraic consequence of the chosen identification. It does not prove that two physical alternatives have been destroyed or interfered. A non-injective \(f\) has no general inverse; a reconstruction account must retain the appropriate fibre or acknowledge ambiguity.

### X.6.3 Restrict explicitly

For a declared decidable predicate \(p\) on the basis:

\[
\mathsf{Restrict}_p(S)=
\sum_{\Gamma:p(\Gamma)}a_\Gamma\mathbf e_\Gamma.
\]

Return both the retained and excluded formal states, with the predicate edition. There is no automatic normalisation, redistribution of coefficients or claim that excluded configurations are impossible. Fixed-predicate restriction is linear; choosing the predicate adaptively from the coefficients is a different operation with separately defined semantics.

Applying restriction to the supported compatible pairs before a join is permitted when explicit. It changes the input. A strict join that fails MUST NOT silently perform that restriction itself.

### X.6.4 Relationship to inherited projection

UC5 uses projection and viewing to describe representational operations. It does not prescribe signed-coefficient arithmetic. In EEC-Q, a projection request MUST additionally specify `view` or `identify`; an exclusion request specifies `restrict`. This refines execution typing without redefining every UC5 projection as algebraic identification.

## X.7 Construction lifting and recursive extension

### X.7.1 Finite ranks

Define rank-zero configurations to contain no quoted constructions. A rank-\(r+1\) configuration may contain immutable quotes of configurations, states, rules or histories whose rank is at most \(r\). Finite sums and tuples take the maximum rank of their contents. Each quote increases the rank of its payload by one.

Every concrete object has finite rank and finite description. Named definitions form a directed acyclic dependency structure in this profile. Cyclic references, unrestricted self-application and infinite histories require a different recursion or limit profile; they are not obtained by omitting the rank check.

This is an unbounded hierarchy of finite constructions: there is no fixed maximum rank in the mathematical definition. Implementations may impose explicit resource limits.

### X.7.2 Pack the whole construction

For an admitted finite construction \(x\), define:

\[
\mathsf{Pack}(x)=q_x,\qquad
\mathsf{Unpack}(q_x)=x.
\]

The quote carries the exact canonical payload, sort, rank, signature and boundary contract. `Pack` returns an entity description, which can be inserted into a configuration. It does not execute, choose a branch of, or linearise its payload.

For a state \(S\), the unit state \(\mathbf e_{q_S}\) contains one quoted whole. In general:

\[
\mathbf e_{q_{S+T}}\ne
\mathbf e_{q_S}+\mathbf e_{q_T}.
\]

The left side contains one entity describing the combined state. The right side is a formal combination of two different quoted entities. Both sides must first be placed in the same declared quote-configuration signature for this comparison. In particular \(\mathbf e_{q_0}\ne0\): a description of zero is still a description.

This is a deliberate non-linear construction operation in the overall language. The rational arithmetic on each fixed state carrier remains linear; not every operation between different sorts is required to be linear.

### X.7.3 Extend outside, transform inside

A quote can be connected to another entity through its exposed boundary. External gluing does not automatically change the quoted interior. An interior transformation is an explicit operation:

\[
\mathsf{Inside}_f(q_S)=q_{f_*S},
\]

when \(f_*S\) is admitted and the result can be represented by the quote's output contract. It creates a new immutable quote. Other references to the old quote keep the old definition.

Changing a quote's interface requires a new contract edition and revalidation of its external connections. If a profile wants external connections to act inside the payload, the interface must specify the binding and invocation rules. A displayed port alone does not supply executable behaviour.

`MapPack(S)`, when offered, means \(\sum_i a_i\mathbf e_{q_{\mathbf e_{\Gamma_i}}}\). It differs from `Pack(S)` because it quotes each basis alternative separately. A language MUST spell out which operation it performs.

### X.7.4 Extension–lifting compatibility is conditional

An implementation may introduce an outer operation \(\widehat e_J\) whose purpose is to unpack two quoted states, apply the declared extension and repack the result:

\[
\widehat e_J(q_S,q_T)=q_{\mathsf{Extend}_J(S,T)}.
\]

This equation defines that particular operator on its admitted domain. It is not a theorem that arbitrary external gluing commutes with quotation. For shared alternatives, \(\widehat e\) must receive a quoted joint source rather than two marginal quotes.

This gives a concrete recursive programming pattern: construct a family, preserve its dependency structure, transform it, quote the whole, expose a boundary, and extend the resulting entity again.

## X.8 Operational phases and well-defined abstraction

### X.8.1 Configuration phase and formal state are separate sorts

An operational phase remains an inquiry-relative equivalence class under a pinned criterion \(Q\). A formal state can contain configurations in several phases. Phase classification does not by itself add their coefficients.

A `phaseView(S,Q)` may group source terms for inspection while retaining the source. An explicit quotient map \(q:B_\Sigma\to B_\Sigma/{\approx_Q}\), followed by \(q_*\), instead produces a new formal state over phase classes. Coefficients can cancel there. Such a quotient state represents the declared abstraction; it is not evidence that its original configurations were identical.

### X.8.2 Domain stability and congruence

For a partial map \(f:D_f\subseteq B_\Sigma\to B_\Tau\), a partial phase operation
\(\bar f([\Gamma]_Q)=[f(\Gamma)]_{Q'}\) requires both:

1. **Domain saturation:** if \(\Gamma\approx_Q\Gamma'\), then \(\Gamma\in D_f\) if and only if \(\Gamma'\in D_f\).
2. **Result congruence:** equivalent admitted inputs have equivalent outputs under the pinned target criterion \(Q'\).

Then the operation is defined on precisely those phase classes contained in \(D_f\), and its value is independent of the representative. Domain saturation is an explicit v0.12 refinement of the execution condition in UC5 §8.7.

For gluing, both compatibility and output phase MUST be invariant under replacing either input by an equivalent representative, with the same mapped interface contract. Otherwise use configuration-level operations or a declared representative-selection policy; do not present the latter as an intrinsic operation on phases.

### X.8.3 A minimal failure example

Let \(P\) and \(Q\) be labelled three-node graphs with edges
\(P=\{AB,BC\}\) and \(Q=\{AC,BC\}\). Under the criterion “same edge count”, they share a phase.

Adding edge \(AB\) leaves \(P\) at two edges but takes \(Q\) to three. The operation is therefore not congruent with this phase criterion. Separately, a rule available only when \(AB\) is absent fails domain saturation on the same phase, even if its admitted outputs would all share a phase.

These are two distinct reasons to reject phase-level execution. A sample showing no failure does not prove either property for an unbounded carrier.

## X.9 Histories, rule families and operation order

A finite history consists of admitted configurations, typed transition descriptions and the context needed to interpret their order. It can be a configuration payload, an alternative within a joint family, or a quoted whole. Histories with the same endpoints need not be identical.

Successive snapshots of a shared choice MUST retain that shared assignment. Forming an independent product of time slices generally creates histories that were not in the source. A projection to the last configuration is an explicit map that may identify distinct histories; a view of the last configuration can retain the history source instead.

A history rank is a syntactic containment property. TD roles, temporal orientation, clocks, causality and operational temporal phases retain their own UC5 meanings. No global simultaneity or reversal of physical causation follows from quoting a history.

Rule descriptions may be nodes in larger configurations and may vary in a joint family with their arguments. Evaluation requires a finite typed rule language with an explicit domain and an interpreter. This creates a route towards programs that construct and transform program structure. It does not make every stored object automatically executable.

For composable total deterministic maps \(f,g\):

\[
(g\circ f)_*=g_*\circ f_*.
\]

Neither configuration operations nor their lifts need commute: \(g_*f_*\) and \(f_*g_*\) may differ. With partial operations, observational equivalence of programs includes success or failure and the declared output, not just equality of successful state values.

## X.10 Laws and their proof obligations

The following are the mathematical commitments of EEC-Q/0.1. They are not inferred from a diagram.

| ID | Law or condition | Scope |
|---|---|---|
| L1 | Exact canonical finite-sum addition is associative and commutative, with zero and additive inverses | One pinned basis identity and signature |
| L2 | \(f_*\) is linear | A total configuration map, or the vector space supported inside a fixed partial domain |
| L3 | Identity and composition of total maps are preserved by linear extension | Compatible input/output signatures |
| L4 | Independent extension is bilinear | Fixed gluing semantics and a common admitted domain |
| L5 | Associativity of configuration gluing transfers to state extension | Compatible interfaces, all intermediate domains, and an explicit final identity or isomorphism map |
| L6 | Shared alternatives are transformed as one joint state | No undeclared factorisation or extra multiplication |
| L7 | A many-to-one identification may cancel a nonzero formal state | Exact signed coefficients; it need not preserve information |
| L8 | \(\mathsf{Unpack}(\mathsf{Pack}(x))=x\) | Canonical finite payload; quotation is not a linear state operator |
| L9 | A partial operation descends to phases when domain saturation and result congruence hold | Pinned source and target equivalences |
| L10 | Display-only viewing leaves its source unchanged | No implicit conversion of a view to a state |

**Derivation of L2 and L3.** Write a state as a finite sum. Distributing rational coefficients through \(f_*\) gives linearity. Applying \(g_*\) to each resulting basis term gives \(\mathbf e_{g(f(\Gamma))}\); finite collection gives the same coefficients as the composite map. For partial maps, the statements apply where all required intermediate terms are admitted.

**Derivation of L4.** Expand the two finite input sums. Each independent pair has coefficient \(a_i b_j\). Distributivity of rational multiplication over addition gives bilinearity before collection, and collection preserves the equality. If evaluating one side introduces a domain failure that cancellation avoids on the other side, this calculation cannot justify a program rewrite.

**Conditional derivation of L5.** Suppose configuration-level left and right bracketings agree after one specified canonical identity or isomorphism map, and both intermediate bracketings are admitted. Both expansions give the same final configuration for each triple with coefficient \(a_i b_j c_k\). Therefore the state results agree under that map. This does not assert associativity for arbitrary constraints or interfaces.

**Derivation of L7.** If \(f(P)=f(Q)\) for distinct basis elements, then \(\mathbf e_P-\mathbf e_Q\) is nonzero and its image is zero. The linear map consequently has a nontrivial kernel. It cannot be inverted on all formal states.

**Derivation of L9.** Domain saturation makes admission a property of an equivalence class. Result congruence makes every admitted representative yield the same target class. If either condition fails, a class-level result or its availability depends on the chosen representative.

These are elementary derivations for the selected finite-sum construction. They do not prove that an unspecified domain model satisfies the hypotheses, that arbitrary graph gluing is associative, or that a compiler preserves these semantics.

## X.11 Worked executable construction

### X.11.1 Extend a family until a distinction disappears

Use the fixed labelled node set \(\{A,B,C\}\), one undirected relation kind and no loops or parallel edges. Let:

\[
P=\{AB,BC\},\quad Q=\{AC,BC\},\quad
S=\mathbf e_P-\mathbf e_Q.
\]

`add(AB)` adds the edge idempotently:

\[
S\longmapsto\mathbf e_P-\mathbf e_{\{AB,AC,BC\}}.
\]

Applying `add(AC)` then gives zero because both configurations become the same labelled triangle. Applying one rule that adds both edges gives the same result. The original state is nonzero; this particular formal transformation loses the difference that sustained it.

If the configurations also retain semantic attributes `branch=first` and `branch=second`, the result instead has two distinct tagged triangles and is nonzero. An explicit rule removing those attributes then produces zero. A drawing hiding the attributes does not.

### X.11.2 Promote the family into a larger entity

Let \(q_S=\mathsf{Pack}(S)\). It is one entity describing the entire two-term family. Attach it to another entity through an explicit `contains` or `uses` relation. This creates a configuration that can itself participate in a higher-rank formal family.

Running both edge additions inside the quote produces \(q_0\). The outside configuration does not vanish: it now contains a quoted zero state. By contrast, unpacking and executing the family at state level produces zero. This distinction gives construction lifting operational meaning.

### X.11.3 Minimal proposed surface syntax

The following is illustrative syntax, not a shipped parser:

```text
profile EEC-Q/0.1 with FG3/0.1

P := config { nodes A, B, C; edges AB, BC }
Q := config { nodes A, B, C; edges AC, BC }
S := basis(P) - basis(Q)

G := pack(S)
T := map(add_edge(AB), S)
U := map(add_edge(AC), T)
G2 := inside(add_edges(AB, AC), G)

assert U == zero
assert unpack(G2) == zero
assert basis(quote_config(G2)) != zero
```

A future glyph may name `G`, `add_edge`, a quoted rule or an entire subprogram. The binding determines its meaning. A glyph that names a large definition shortens source notation; it does not remove the definition's execution cost.

## X.12 Implementation and interchange contract

### X.12.1 A minimal implementation boundary

A practical first runtime accepts finite typed configurations and rational formal states, checks admission, evaluates selected registered operations and returns exact normal forms or explicit errors. It may run on an ordinary CPU. This is sufficient to test the algebra without committing to a visual editor, quantum backend or operating system.

A full EEC-Q implementation MUST declare supported signatures, relation kinds, constraint language, rule grammar, quotation sorts, canonical identities, limits and conformance cases. It MUST implement or explicitly reject each requested operation. Unsupported geometry or rules cannot silently degrade into strings with no semantics.

### X.12.2 Machine-oriented example

This JSON record is a complete **FG3** state payload. Its profile fixes the three `vertex` entities A, B, C, the undirected `link` relation, an empty interface, no semantic attributes when `tag` is null, and exact labelled identity. Evidence and unknown fields are outside this deliberately complete toy model, rather than defaulted to false.

```json
{
  "kernel": "0.12-experimental",
  "profile": "EEC-Q/0.1",
  "model": "FG3/0.1",
  "context": "finite labelled graph algebra",
  "inquiry": "effect of edge addition on a formal difference",
  "state": [
    {"coefficient": "1/1", "config": {"edges": ["AB", "BC"], "tag": null}},
    {"coefficient": "-1/1", "config": {"edges": ["AC", "BC"], "tag": null}}
  ]
}
```

A general interchange format MUST additionally carry signature and definition editions, canonical semantic payloads or resolvable immutable references, interface declarations, admission constraints, choice dependence, rank information and operation domains. Fractions use reduced numerator/positive-denominator form; floating-point approximations are not interchangeable with exact coefficients.

External references cannot be fetched or executed merely because a glyph names them. Imports require explicit resolution. Rendering metadata and diagnostic logs are separated from semantic identity. Interchange must preserve the exact distinctions that affect canonical collection.

### X.12.3 Execution and complexity

Exact expansion of independent states with support sizes \(m,n\) has up to \(mn\) pairs before collection. Repeated independent composition can grow rapidly. Sharing, symbolic expressions and memoisation can avoid some repeated work, but they must preserve joint dependencies and exact results.

Packing a state may make its outer representation compact; the stored payload still exists. A symbolic state, a GPU representation or a 3D display is not by itself a complexity improvement. Resource limits must interrupt explicitly. Performance claims require a workload, baseline, equivalent outputs, cost model and reproducible measurement.

Appendix V provides a runnable **FG3/0.1 example evaluator**, not a complete EEC-Q compiler. It covers rational states, deterministic edge rules, independent and joint pair composition, restriction, display/source separation, exact identification, whole-state quotation and selected failure checks. It does not implement arbitrary interfaces, arbitrary rule quotation, topology, full temporal semantics, a glyph parser or a quantum lowering.

## X.13 Conformance cases and current validation

The minimum useful validation suite MUST test differences that can change a result:

| Case | Required observation |
|---|---|
| Exact identity | Distinct labelled configurations do not merge merely because they have the same edge count |
| Zero versus empty structure | A unit empty-structure configuration differs from the zero state |
| Shared choice | The joint two-branch example does not become the four-term independent product |
| Dependent wiring | A supported joint argument uses its own connection declaration and coefficient once |
| Strict domain | One invalid supported branch makes the strict operation fail |
| Invalid cancellation | Malformed terms cannot be hidden by opposite or zero coefficients |
| Restriction | Excluded terms are explicit and coefficients are not renormalised |
| Identification | A many-to-one map can cancel a nonzero state |
| Semantic tags | Retained branch tags prevent cancellation until explicitly removed |
| Whole-state quotation | A quoted zero is an entity; packing is not implicit branchwise distribution |
| Phase results | The equal-edge-count counterexample rejects the proposed phase operation |
| Phase domain | Unequal admission among equivalent representatives rejects phase descent |
| Operation order | At least one admitted pair of operations is shown not to commute |
| Partial rewrite | Equal algebraic values do not conceal unequal failure behaviour |
| Canonical interchange | Serialised exact states retain identity and rational coefficients on round trip |

Some rows are obligations for implementations beyond FG3. Appendix V records exactly which are exercised and which remain unimplemented. A finite test is evidence about that model and run, not universal proof. Independent review and reproduction have not been established by creating this document.

## X.14 Compatibility and migration from UC5

| UC5 element | v0.12 treatment | Compatibility consequence |
|---|---|---|
| Configuration envelope, UC5 §3.6 | Retained; executable signatures select representable subsets | No requirement that every E7G-T entity be a graph |
| Admission, unknowns and support | Retained | Formal coefficients cannot replace support or unknown semantics |
| D/TD roles, UC5 §5 | Retained; finite rank introduced separately | Rank is not an extra physical dimension or a renamed D-role |
| Extension, UC5 §6.4 | Given selected executable interpretations | Existing modelling notation remains valid |
| Viewing/projection, UC5 §6.6 | New operational tags distinguish view, identify and restrict | Importers must choose a meaning; no automatic coefficient merging |
| Phase operations, UC5 §8.7 | Domain saturation made explicit alongside result congruence | A phase operation accepted using only jointly admitted representatives may now fail the executable-profile check |
| Gluing, UC5 §8.14 | Concrete domains, identity rules and formal-state lift added | Generic associativity or topology still requires its own conditions |
| Formalisation, UC5 §§16.3–16.5 | EEC-Q instantiates a bounded formal direction | FG3 does not claim full UC5 formal-implementation conformance |
| Informative overlays | Status unchanged | No automatic promotion or dependency on EEC-Q |
| Practical output profiles | Retained | Calculus evaluation adds an output kind; it does not replace existing analyses |

The working definition at the beginning of v0.12 makes construction and computation explicit. It extends the project's direction while retaining the UC5 distinction between source, representation, phase and evidence. It does not turn every E7G-T use into an algebraic execution.

The supplied UC5 file contains older UC4 wording in its maturity statement and closing line. Its front matter identifies it as 0.11-UC5. Those historical strings are preserved in Part II as source text; they do not specify the version or maturity of this document.

Migration procedure:

1. Keep existing UC5 artefacts pinned to their original version.
2. For a v0.12 executable artefact, declare `kernel=0.12-experimental`, `profile=EEC-Q/0.1` and the supported model edition.
3. Supply exact configuration identity, coefficient semantics and joint-dependence declarations.
4. Type every projection as view, identification or restriction at the execution boundary.
5. Recheck phase operations for domain saturation and result congruence.
6. State omitted UC5 features and unimplemented profile features. Do not claim full compatibility on the basis of a shared version label.

E7Q remains an independently versioned quantum evidence and verification direction. EEC-Q is a constructive language foundation within E7G-T; it can be developed without requiring E7Q to become that language. Future adapters can connect them through explicit contracts. The ecosystem operating kernel remains a separate document and is not revised by this release candidate.

## X.15 Development questions and promotion conditions

The next mathematical work is to explore which extension laws are useful under different concrete interpretations. EEC-Q chooses bilinear independent gluing and deterministic pushforward; other profiles may choose sets, constrained families, different coefficient structures or explicitly non-linear operations. Such changes need their own versioned semantics and examples. They cannot silently inherit every EEC-Q law.

Priority questions are:

- Which interface theories make repeated extension associative, and which require an explicit order or coherence map?
- When does a useful phase criterion preserve both operation results and operation availability?
- How can dependent choices remain compact through repeated lifting and unfolding?
- Which limited rule language supports safe construction of new rules and dependable termination?
- Which concrete geometric carriers make incidence, projection and transformation easier to express than ordinary source code?
- What problem benefits enough from this language to justify its implementation and review cost?

A stable successor should require a published grammar and interchange schema, an implementation covering its declared profile, independent reproduction of positive and negative cases, at least one useful end-to-end program, and a reviewed compatibility account. Performance or quantum claims require separate evidence appropriate to those claims.

The v0.12 deliverables include the experimental calculus, its worked constructions, a runnable finite example model, the optional SF symbolic-family profile, and the optional CFS family-state composition introduced below. A full language, OS, hardware mechanism and general-purpose verifier remain future engineering or research work. This is an implementable foundation for that work rather than a claim that the destination has already been reached.


## X.16 Optional symbolic families and realisation — SF/0.1

Added in revision **SF1**, 2026-09-08. This section reproduces the Symbolic Family and Realisation Profile v0.1. Its S-numbered references are local to this optional profile. The implementation and validation report are separate companions; the complete mathematical profile is included here.

**Purpose:** make a finitely described family of possible configurations an object of computation; transform and extend that family; obtain a particular entity through a declared realisation rule; retain the family for further work.

This profile develops the proposed “hyperposition” intuition as symbolic mathematics. The family may contain infinitely many configurations. Its executable representation remains finite. Its realisation is a specified operation with inspectable success and failure conditions.

SF/0.1 is an optional profile of E7G-T v0.12. It is independently versioned from the kernel's EEC-Q/0.1 formal-sum profile. The accompanying **E7G-T_Symbolic_Families_v0.1.py** implements the bounded **IC/0.1** interval-and-circle model. The **E7G-T_Symbolic_Families_Validation_v0.1.json** file records the internal run.

### S.0 Scope and terminology

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

### S.1 Family definition and identity

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

### S.2 Extension and transformation

**Dependent extension** adds structure using the existing assignment:

\[
\mathsf{Extend}_h(H)
=\langle\Lambda,K,\lambda\mapsto(g(\lambda),h(\lambda))\rangle.
\]

The output signature identifies what the new component means and how it is related to the original configuration. If the extension preserves the original fields, projection to those fields recovers \(g(\lambda)\) for every admitted assignment. This is a pointwise preservation law, not an automatic inverse for every later operation.

**Independent extension** introduces a separately scoped parameter \(\mu\in M\) and a product domain. **Constrained extension** introduces additional parameters with constraints that may relate them to \(\lambda\). An implementation MUST distinguish these cases. IC/0.1 implements dependent extension; general multivariate products and constraints remain outside that prototype.

**Transformation** composes the configuration map with a declared rule: \(\mathsf{Transform}_T(H)=\langle\Lambda,K,T\circ g\rangle\), where the transformation is defined on the admitted image. A transformation that is not defined everywhere needs an explicit domain restriction or rejection. Invalid assignments cannot be silently dropped.

Adding another coordinate need not add an independent degree of freedom. In the circle example, three coordinates still depend on one continuous parameter and a two-chart sign. Mathematical carrier dimension, parameter count, E7G-T order role and quotation rank are separately declared quantities.

### S.3 Projection, viewing, restriction and quotation

| Operation | Result | Selection or loss |
|---|---|---|
| `view(H, fields)` | A view retaining its source family | Hides fields in the display; does not replace the source |
| `project(H, fields)` | A new family whose configurations retain the named fields | Can identify formerly different entities |
| `restrict(H, constraint)` | A family with a smaller admitted parameter domain | Excludes assignments explicitly |
| `pack(H)` | A quote of the complete family | Selects no member |
| `realise(H, criteria)` | A result record, residual family and possibly one entity | Resolves only what the criteria determine |

All operations are pure in IC/0.1: their inputs remain available. Retaining the symbolic source records the model; it does not establish that an unknown physical quantum state can be copied or preserved through measurement.

Restriction is an input change. A realisation criterion is an explicit selection policy. Neither implies that excluded alternatives are physically nonexistent. A quote of an empty family remains a description; it differs from an empty family and from a realised numeric entity.

### S.4 Realisation semantics

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

#### S.4.1 Outcomes

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

#### S.4.2 Order and purpose matter

Maximising x and then minimising z can differ from minimising z and then maximising x. Realisation need not commute with extension, transformation or projection. For any proposed rewrite, the source domain, mapped criteria, tie policy and failure behaviour must be checked.

For example, projecting a lifted circle to z alone identifies two maximising points. Its projected image can have a unique optimum while the full family still has two distinct optimal entities. A view showing z alone retains that ambiguity in its source.

### S.5 Exact interval-and-circle model IC/0.1

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

#### S.5.1 Circle representation

The circle is represented by two charts:

\[
-1\leq t\leq1,\qquad s\in\{-1,1\},\qquad
x=t,\quad y=s\sqrt{1-t^2}.
\]

Together they represent the whole unit circle. At \(t=\pm1\), both sign assignments yield the same point. This duplication is retained at the parameter level and removed only when checking equality of resulting entities.

The extension \(z=\cos(2\theta)\) from the earlier trigonometric example becomes the polynomial \(z=2t^2-1\), using \(t=\cos\theta\). The prototype therefore executes that example without a general trigonometric solver or a point grid.

#### S.5.2 Why the solver covers its stated interval domain

A nonconstant linear or quadratic polynomial on a bounded interval has its supremum and infimum among the endpoints of the closure and any derivative-zero point inside that closure. The implementation evaluates this finite candidate set exactly. It separately checks whether a winning candidate belongs to the admitted interval.

If an excluded endpoint is the sole winner, the result is `UNATTAINED`. If a closed endpoint or an interior critical point attains the same bound, the bound is attained. A constant objective retains the whole interval. These rules establish the implemented optimisation procedure's scope; evaluating a grid would not establish the same result.

Uniqueness is checked in configuration space. On a finite residual domain, the implementation evaluates and deduplicates exact entities. On a nondegenerate interval, constant coordinates give one entity. A nonconstant polynomial coordinate or the circle coordinate proves variation. Rational interior points are then used to produce two witnesses of that already-established variation. A degree-d nonconstant polynomial cannot take one value at d+1 distinct points; the circle coordinate at a fixed sign takes a given value at at most two parameter values. This supplies the finite witness bound used by the code.

#### S.5.3 Limits

The prototype supports at most 32 coordinate fields and 32 ordered objectives, degree-eight polynomial data, 1,024 explicitly supplied parameter points and rationals within its 4,096-bit representation limit. `realise` also accepts a per-stage candidate budget, default 4,096. This is a count limit, not a hard wall-clock or total-memory guarantee.

Python resource exceptions remain possible; they must not be interpreted as successful computation. The API assumes immutable objects created through its constructors. Reflection that bypasses those constructors is outside the input model.

Only admitted model operations are claimed. General multivariate optimisation, arbitrary constraints, infinite sequences, general family equality and quantum lowering are unimplemented.

### S.6 Executable demonstration

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

### S.7 Relationship to EEC-Q and operational phases

EEC-Q/0.1 uses finite signed rational combinations; SF/0.1 uses set-valued denotations represented by expressions. They are different profiles under the same kernel.

Suppose distinct configurations P and Q map to R. In EEC-Q, applying the linear map to \(\mathbf e_P-\mathbf e_Q\) gives zero. In SF, the image of the set \(\{P,Q\}\) is the singleton \(\{R\}\). The two results must not be interchanged.

An adapter from EEC-Q may explicitly extract the support of a canonical formal state, recording that coefficients and their algebra have been discarded. The reverse operation needs an explicit finite enumeration and coefficient assignment. An infinite symbolic family does not automatically become an EEC-Q finite-support state.

Both profiles retain the E7G-T distinctions between source and view, descriptions and entities, domains and unknowns, whole-family quotation and selection. Neither a family nor a quote is automatically an operational phase. A phase abstraction used during realisation must preserve the distinctions and operation availability that the criteria require; the kernel's domain-saturation and congruence conditions remain relevant.

Existing EEC-Q/FG3 programs retain their semantics. SF is opt-in and does not reinterpret their coefficients, cancellation or finite-rank rules. A symbolic family is a finite expression describing a potentially infinite image; this does not make its expression tree infinite or give it infinite quotation rank.

### S.8 Validation and next development boundary

The companion validation report records executable cases covering the lifted circle, ordered tie-breaking, ambiguity, exact interior optima, open-endpoint non-attainment, empty restrictions, constant families, projection versus viewing, quotation, exact radicals, unsupported solvers, limits, malformed inputs, interchange and repeated family/entity construction.

The algebraic solver justification in §S.5.2 and the executable checks serve different purposes: the former states why the bounded mathematical procedure covers its admitted cases; the latter checks its implementation on selected positive and negative cases. Neither establishes correctness of all symbolic computation or independent reproduction.

The immediate operating capability is: **describe an infinite family finitely, extend it while preserving dependence, realise a result under declared criteria, and reuse that result in further construction.**

The next useful expansion would be one additional exact carrier or solver selected by a concrete program that IC/0.1 cannot express. Candidates include jointly constrained multiple parameters, a general typed relational body, or an explicit amplitude profile. Each requires its own semantics and validation; additional physical or performance claims require their own evidence.

### S.9 Recorded internal validation

The reference run on **2026-09-08**, using Python **3.12.13**, passed **48 named checks**. The report contains the exact input formulas, source identity, residual families, membership witnesses, objective bounds and outcomes for the principal examples.

| Demonstration | Recorded outcome |
|---|---|
| Lift the circle and maximise z, then x | `UNIQUE`: (1, 0, 1) |
| Maximise z without the tie-break | `AMBIGUOUS`: two distinct entity witnesses |
| Maximise x on the open interval (0, 1) | `UNATTAINED`: supremum 1 |
| Seed a new family from the selected entity and maximise x | `UNIQUE`: (2, 0, 1) |

Companion code SHA-256: `0a827d55cc95c4840ba5427e8585378b23ee6a3b00296856f192176cb4a2dca8`.

The result is internal validation of IC/0.1. Independent reproduction, a general symbolic solver and a complete programming language are not claimed.



## X.17 Optional combined family-state profile — CFS/0.1

Added in revision **CFS1**, 2026-09-08. This section reproduces the Combined Family-State Profile v0.1. Its C-numbered references are local to this optional profile. CFS places an EEC state inside an SF family while keeping both component profiles independently usable.

**Purpose:** place an EEC-Q formal configuration state inside an SF symbolic family, so a whole algebraic combination can vary, extend, transform and later be realised without losing the distinction between family membership and formal coefficient arithmetic.

CFS/0.1 combines two independently usable E7G-T v0.12 profiles. SF supplies the outer parameter domain, constraints, symbolic dependence and realisation protocol. EEC-Q supplies the inner finite formal state, exact rational coefficients, pushforward, cancellation and typed extension. The combination does not equate a set of possible entities with a formal sum.

The companion **E7G-T_Combined_Family_State_v0.1.py** implements the bounded **CG3/0.1** model by combining the IC/0.1 interval carrier and polynomial expressions with FG3/0.1 graph states. The validation report records its internal checks.

### C.0 Status and terms

Capitalised MUST, MUST NOT, SHOULD and MAY express obligations on implementations claiming CFS compatibility. A declaration of compatibility MUST identify the outer SF model, inner EEC model, coefficient-expression grammar, supported operations, equality procedures and resource limits.

| Term | Meaning |
|---|---|
| Outer assignment | One admitted value of the SF parameter carrier |
| Inner state | The EEC-Q formal state constructed at one outer assignment |
| State family | A finite symbolic description of a family of inner states |
| Evaluation | Construction of the inner state at a supplied admitted assignment |
| Realisation | Selection over the outer family under declared objectives |
| Shared composition | Pointwise composition of state families using the same outer assignment |

CFS coefficients retain the meaning of their selected EEC profile. In CFS/0.1 they are exact rational formal coefficients. They are not probabilities, evidence weights or physical amplitudes. CFS/0.1 provides no interference, measurement or quantum execution semantics.

### C.1 Combined carrier

Pin an outer symbolic model, an inner configuration signature \(\Sigma\), context and inquiry. A combined family-state object is:

\[
\mathcal H=\langle\Lambda,K,S\rangle_\Sigma,
\qquad
D_{\mathcal H}=\{\lambda\in\Lambda:K(\lambda)\},
\]

where each admitted assignment constructs an inner EEC-Q state

\[
S(\lambda)
=\sum_{i=1}^{n} a_i(\lambda)\,\mathbf e_{\Gamma_i(\lambda)}
\in\mathcal F_\Sigma.
\]

The expression is finite: it has finitely many symbolic terms even when \(D_{\mathcal H}\) or the image of \(S\) is infinite. At every admitted assignment, inner canonicalisation collects equal configurations and removes coefficients that evaluate to zero.

The denotation of the outer family is the set of canonical inner states:

\[
\llbracket\mathcal H\rrbracket
=\{S(\lambda):\lambda\in D_{\mathcal H}\}.
\]

This is a set at the outer level. No addition or cancellation occurs merely because two assignments produce the same state. Within each \(S(\lambda)\), the selected EEC coefficient algebra applies.

Two parameter assignments may therefore denote the same inner state. A uniquely realised state does not imply a unique parameter assignment. An empty outer family differs from a nonempty family whose every member is the EEC zero state.

### C.2 Why the nesting direction matters

CFS/0.1 selects **SF outside and EEC inside**:

\[
\lambda\longmapsto S(\lambda).
\]

The outer family preserves symbolic variation and shared dependence. The inner state gives each assignment a complete algebraic configuration combination. This permits an unresolved program or construction to be transformed as a whole before a particular state is selected.

The reverse construction—an EEC formal sum whose basis elements are quoted SF families—is also meaningful, but it answers another question. It combines whole family descriptions algebraically; it does not create a parameterised state or license pointwise evaluation. Conversion between these two arrangements is never implicit.

### C.3 Evaluation, restriction, viewing and quotation

Evaluation at an admitted assignment is:

\[
\operatorname{eval}_\lambda(\mathcal H)=S(\lambda).
\]

Evaluation uses a supplied assignment. It is not realisation and does not assert that the assignment is optimal, observed or physically selected.

Restriction strengthens the outer constraint:

\[
\operatorname{restrict}_L(\mathcal H)
=\langle\Lambda,K\land L,S\rangle.
\]

A view retains the complete source and displays selected outer or inner properties. A projection constructs a new family and MUST state what information it identifies or discards. Quotation makes the whole combined construction an entity without evaluating or realising it.

### C.4 Pointwise algebra and pushforward

For compatible state families over the same pinned outer domain and context:

\[
(\mathcal H+\mathcal G)(\lambda)=S(\lambda)+T(\lambda),
\qquad
(b\mathcal H)(\lambda)=b(\lambda)S(\lambda),
\]

where the coefficient expression \(b\) and every resulting product must belong to the declared expression grammar.

For a total inner configuration map \(f\), pushforward is pointwise:

\[
(f_*\mathcal H)(\lambda)=f_*S(\lambda).
\]

Configuration images are collected inside each state. Thus a transformation can turn a varying family into a constant one through identification and symbolic coefficient collection.

For a partial inner rule, a strict CFS transformation is admitted only if the rule is defined on every configuration that occurs with a nonzero coefficient at at least one admitted assignment. Implementations MAY support a stronger symbolic proof procedure. They MUST NOT silently discard assignments or terms on which the rule fails.

Pointwise cancellation is evaluated under the outer assignment. A symbolic coefficient that is zero everywhere on the admitted domain contributes no inner branch. A coefficient that vanishes only at particular assignments removes the branch only at those assignments.

### C.5 Extension and dependence

Extension by a fixed inner state \(U\) is:

\[
\operatorname{Extend}_J(\mathcal H,U)(\lambda)
=\operatorname{Extend}_J(S(\lambda),U).
\]

For two families sharing the same outer assignment, dependent extension is pointwise:

\[
\operatorname{SharedExtend}_J(\mathcal H,\mathcal G)(\lambda)
=(e_J)_*\big(S(\lambda)\boxtimes T(\lambda)\big).
\]

The same \(\lambda\) appears in both operands. Replacing it with two independently chosen parameters changes the program. Shared extension can therefore create coefficient products such as \(a_i(\lambda)b_j(\lambda)\), while preserving their common origin.

Independent outer extension introduces a fresh parameter \(\mu\):

\[
\langle\Lambda\times M,K(\lambda)\land L(\mu),
(\lambda,\mu)\mapsto
\operatorname{Extend}_J(S(\lambda),T(\mu))\rangle.
\]

Constrained extension may introduce \(\mu\) together with a relation \(C(\lambda,\mu)\). An implementation MUST distinguish shared, independent and constrained outer parameters. CG3/0.1 implements shared pointwise composition and extension by a fixed inner state; general multivariate outer carriers remain outside the model.

### C.6 Realisation over inner states

A realisation objective is a declared function on canonical inner states. In the bounded reference model it is a rational linear observable:

\[
\ell\!\left(\sum_\Gamma c_\Gamma\mathbf e_\Gamma\right)
=\sum_\Gamma w_\Gamma c_\Gamma.
\]

Composing it with the state family produces an outer scalar expression:

\[
p_\ell(\lambda)=\ell(S(\lambda)).
\]

The SF realisation protocol then applies ordered objectives lexicographically. If the final residual image contains exactly one canonical inner state, the result is `UNIQUE`. If it contains at least two, it is `AMBIGUOUS`. `EMPTY`, `UNATTAINED`, `UNSUPPORTED`, `UNDETERMINED`, `UNBOUNDED` and `RESOURCE_LIMIT` retain their SF meanings when supported by the selected outer model.

The returned entity of a successful CFS realisation is an inner EEC state, including the zero state. The residual state family and source family remain available. No arbitrary member is selected from an ambiguous residual image.

Realisation and inner pushforward need not commute. A pushforward can identify previously distinct configurations and make a family uniquely realisable. Conversely, an objective may distinguish states using information that a pushforward removes. Any interchange law requires a mapped objective and proof over the admitted domain.

### C.7 Adapters to the component profiles

The following adapters are explicit:

1. Evaluating a CFS family at an admitted assignment returns one EEC state.
2. A CFS family whose inner image is proved singleton can be realised as one EEC state without choosing a unique assignment.
3. An EEC state can be embedded as a constant CFS family over any declared nonempty outer domain.
4. Replacing each inner state by its support produces an SF family of finite sets and discards coefficient values and cancellation semantics.
5. Turning an arbitrary SF family of configurations into CFS requires an explicit injection and coefficient assignment.

An infinite SF image cannot automatically become one finite-support EEC state. An EEC state cannot recover an outer parameterisation that was discarded.

### C.8 Bounded reference model CG3/0.1

CG3/0.1 combines these existing executable subsets:

- outer domains: IC/0.1 bounded rational intervals or finite rational point sets;
- inner configurations: FG3/0.1 fixed-labelled graphs;
- symbolic coefficients: exact rational polynomials in one parameter \(t\), degree at most eight;
- inner coefficients after evaluation: exact rational numbers;
- transformations: registered FG3 graph rules when total on the active symbolic support;
- extension: graph union or pairing with a fixed inner state;
- shared composition: pointwise graph union of two families over the identical domain and context;
- objectives: rational linear functionals on inner graph-state coefficients;
- continuous optimisation: inherited IC/0.1 constant, linear and quadratic exact optimisation;
- finite-domain optimisation: exact evaluation of admitted polynomial objectives.

The model accepts at most 64 interchange terms, 32 ordered objectives, 1,024 explicit outer points and the inherited 4,096-bit rational and degree-eight polynomial limits. The default per-stage candidate limit is 4,096.

CG3 does not implement graph-valued symbolic coordinates, arbitrary constraints, multivariate parameters, general EEC configurations, nonlinear observables, automatic theorem proving or quantum lowering.

### C.9 Worked construction

Let \(A\) be the empty FG3 graph and \(B\) the graph containing edge `AB`. Over \(0\le t\le1\), define:

\[
S(t)=t\mathbf e_A+(1-t)\mathbf e_B.
\]

At \(t=0\), evaluation gives \(\mathbf e_B\). At \(t=1\), it gives \(\mathbf e_A\). At \(t=\tfrac12\), it gives the exact state

\[
\tfrac12\mathbf e_A+\tfrac12\mathbf e_B.
\]

Without an objective, the outer state image is ambiguous. Maximising the coefficient of \(A\) realises \(t=1\) and returns \(\mathbf e_A\).

Now apply the total FG3 rule that adds edge `AB`. Both \(A\) and \(B\) map to \(B\), so:

\[
S'(t)=t\mathbf e_B+(1-t)\mathbf e_B=\mathbf e_B.
\]

The resulting outer family is constant and realises uniquely without an objective. This demonstrates a specifically combined behaviour: symbolic variation is retained outside, while configuration identification and coefficient collection occur inside.

For shared composition, if

\[
S(t)=t\mathbf e_A+(1-t)\mathbf e_B,
\qquad
T(t)=t\mathbf e_C+(1-t)\mathbf e_D,
\]

then their pointwise inner product uses coefficients \(t^2\), \(t(1-t)\) and \((1-t)^2\). It does not introduce an independent parameter \(u\).

### C.10 Laws and proof obligations

Within a common admitted domain and where every operation succeeds, CG3 checks representative instances of:

\[
\operatorname{eval}_\lambda(f_*\mathcal H)
=f_*\operatorname{eval}_\lambda(\mathcal H),
\]

\[
\operatorname{eval}_\lambda(\mathcal H+\mathcal G)
=\operatorname{eval}_\lambda(\mathcal H)
+\operatorname{eval}_\lambda(\mathcal G),
\]

and

\[
\operatorname{eval}_\lambda(
\operatorname{SharedExtend}_J(\mathcal H,\mathcal G))
=\operatorname{Extend}_J(
\operatorname{eval}_\lambda\mathcal H,
\operatorname{eval}_\lambda\mathcal G).
\]

These equalities do not license rewrites that change domain failures, resource outcomes, parameter dependence or the coefficient-expression grammar. A transformation that exceeds the polynomial-degree limit is unsupported even if some individual evaluations could be computed.

### C.11 Quantum and language boundary

CFS supplies a language-level form for an unresolved structured program: one symbol can denote a family of formal states, and connections between symbols can extend those states while preserving shared parameters. A compiler may later realise, specialise or lower such a construction.

A quantum profile would need a different or additional inner carrier with normalised complex amplitudes, physically valid state representations, permitted channels or unitary transformations, tensor-product and entanglement rules, measurement semantics and a mapping to an executable quantum intermediate representation. CFS rational cancellation alone does not provide those properties.

### C.12 Validation and development boundary

The companion implementation checks construction, endpoint and interior evaluation, ambiguity, exact realisation, pointwise pushforward, symbolic cancellation, the distinction between an empty outer family and a zero inner state, fixed extension, shared composition, lexicographic objectives, strict partial-rule failure, canonical interchange and malformed-input rejection.

The internal reference run on 2026-09-08 passed 40 named checks. These checks validate the bounded implementation against the rules above; they do not establish completeness of the general combined calculus.

The next useful expansion should be selected by a concrete program requiring one of: a jointly constrained multivariate outer carrier, configuration-valued symbolic terms, richer exact observables, or a separately specified complex-amplitude inner profile.

# Appendix V — Executable example model and validation

## V.1 Model boundary and invocation

The companion **E7G-T_v0.12_Executable_Examples.py** contains the same source as §V.4. It runs with Python 3.10 or newer using only the standard library:

```bash
python3 E7G-T_v0.12_Executable_Examples.py
```

The script performs local, deterministic mathematical checks and prints a JSON report. It reads no email, contacts no service, uses no private compiler and submits no hardware jobs. The code is included as a specification example under this document's CC BY-SA 4.0 licence; no third-party implementation rights are asserted.

FG3/0.1 has the following exact representation choices:

| Object | Representation and identity |
|---|---|
| `Graph` | Fixed vertex identities A, B, C; a set of undirected links from AB, AC, BC; an optional semantic string tag |
| `State` | Sorted finite map from exact atoms to nonzero `Fraction` values |
| `Box` | Immutable quote of a complete `State`; payload equality determines quote equality |
| `Assembly` | Ordered left and right atoms and a relation label `uses` or `contains`; both labels are structural, with no automatic invocation |
| `Joint` | Canonical finite coefficient map over same-arity tuples of atoms |
| `Rule` | One of `add`, `remove`, `require_absent`, `forget_tag`, `empty`, with a validated edge argument where needed |
| `View` | Unchanged source state plus display rows; hidden tags remain in the source |

All these atoms live in the one explicitly chosen recursive FG3 signature. Graphs are its rank-zero base; boxes raise rank; assemblies take the maximum operand rank. The interface of a box in this model is an opaque reference. Assemblies may reference it, but only `inside` executes a registered graph rule on its payload. Arbitrary ports, dispatch behaviour or user-supplied code are not inferred from these labels.

The union operation intentionally overlaps the fixed A/B/C identities, requires equal tags and deduplicates the permitted edges. This is one fully specified gluing instance. Its associativity is not evidence for arbitrary interface fusion or constraint systems.

The Python API constructs objects directly. There is no parser for §X.11.3's proposed surface language. The JSON loader handles the graph-state payload of §X.12.2; it does not serialise boxes, assemblies, arbitrary UC5 envelopes or external references. Context/inquiry fields in that example are descriptive record metadata, not a new runtime signature. A general importer must preserve and validate its own full context contract.

The example API expects ordinary immutable objects constructed by its constructors; Python reflection that bypasses frozen dataclasses is outside its input model. The mathematical definition admits arbitrarily high finite ranks, while Python's memory and recursion limits still apply. Host resource exceptions are not successful zero results.

## V.2 Recorded internal run

- Runtime: Python **3.12.13**.
- Named checks passed: **39**.
- Fixed untagged basis graphs considered for the phase and associativity checks: **8**.
- Graph-union associativity triples checked exhaustively on that basis: **512**.
- Adding AB: domain saturated on the enumerated basis, result congruence fails under equal-edge-count phases.
- Requiring AB absent: domain saturation fails on that basis, although the admitted representatives preserve their edge-count classes.

The run checks the normal and rejected cases listed below. It does not establish independent reproduction, full-profile conformance, arbitrary-gluing laws, quantum executability, useful speed improvement or physical validity.

```json
{
  "kernel": "0.12-experimental",
  "profile": "EEC-Q/0.1",
  "example_model": "FG3/0.1",
  "python": "3.12.13",
  "checks_passed": 39,
  "basis_graphs": 8,
  "associativity_triples": 512,
  "phase_add_AB": {
    "domain_saturated": true,
    "result_congruent": false
  },
  "phase_require_absent_AB": {
    "domain_saturated": false,
    "result_congruent": true
  },
  "checks": [
    "exact configurations stay distinct",
    "empty graph is not zero",
    "exact cancellation",
    "fraction arithmetic",
    "first extension",
    "second extension cancels",
    "total-map composition",
    "total-map linearity",
    "semantic tags preserve distinction",
    "explicit tag removal cancels",
    "view retains source",
    "identical displayed graphs do not merge",
    "strict supported-domain rejection",
    "restriction preserves signed coefficients",
    "restriction accounts for input",
    "unknown node rejected",
    "invalid opposite terms rejected",
    "invalid zero term rejected",
    "float coefficient rejected",
    "shared coefficient used once",
    "marginal product changes dependencies",
    "joint wiring alternatives",
    "strict incompatible gluing",
    "bilinear independent gluing",
    "whole-family unpack",
    "packing is not branchwise distribution",
    "quoted zero is an entity",
    "recursive construction rank",
    "immutable original quote",
    "no implicit quote execution",
    "fixed-label union associativity",
    "phase-result counterexample",
    "phase-domain counterexample",
    "noncommuting operations",
    "zero support succeeds under a partial rule",
    "partial composition cannot be rewritten across cancellation",
    "zero under a total map",
    "exact JSON round trip",
    "invalid imported zero term rejected"
  ],
  "scope": "Finite internal checks; no general gluing, hardware, performance or full-kernel proof."
}
```

## V.3 Remaining implementation obligations

| Area | Delivered coverage | Remaining work |
|---|---|---|
| Exact finite algebra | Graph, quote and assembly states; signed rational collection | Other coefficient and carrier profiles |
| Dependency | Joint pairs and triples, independent products, dependent connection labels | Symbolic choice grammar, dependency analysis and scalable factorisation |
| Gluing | Fixed-label union and binary structural assemblies | General typed ports, fusion, overlap witnesses and global constraints |
| Reification | Whole-state quotes, nested assembly and explicit interior rules | Quoted rule families, general histories and a complete quotation interchange |
| Projection | Source-preserving graph view, tag identification and explicit restriction | General view reconstruction and quotient-state tooling |
| Phases | Concrete result and domain counterexamples over eight graphs | Proofs or decision procedures for other declared carriers |
| Language | Python construction API and illustrative source syntax | Parser, type checker, compiler, editor and stable interchange schema |
| Integration | Standalone local example | Domain pilot, independent reproduction and any E7Q/backend adapter |

The minimum tangible next programme is a language implementation of this declared subset with one full program that constructs a dependent family, extends it, quotes it and inspects the changed result. Additional profiles should be admitted because they solve a demonstrated limitation, not because a geometric metaphor alone suggests a law.

## V.4 Complete executable source

```python
#!/usr/bin/env python3
"""E7G-T v0.12 experimental: FG3/0.1 finite example evaluator.

Authors: Alexander Gregory Wingate and Oleksandr Razinkov.
Specification companion, CC BY-SA 4.0.
Python 3.10+, standard library only. Run this file to print its checks.
This is a bounded example model, not a full EEC-Q interpreter or compiler.
FG3 includes fixed-labelled graphs, immutable state quotes and binary assemblies.
Only the registered graph rules below are executable rule descriptions.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
import json
import sys

KERNEL = "0.12-experimental"
PROFILE = "EEC-Q/0.1"
MODEL = "FG3/0.1"
EDGES = frozenset(("AB", "AC", "BC"))


class InvalidInput(ValueError):
    pass


class DomainError(ValueError):
    pass


def rational(x):
    if type(x) not in (int, Fraction):
        raise InvalidInput("exact integer or Fraction required")
    return Fraction(x)


@dataclass(frozen=True)
class Graph:
    edges: tuple = ()
    tag: str | None = None

    def __post_init__(self):
        if not isinstance(self.edges, tuple) or any(
            type(e) is not str or e not in EDGES for e in self.edges
        ):
            raise InvalidInput("FG3 edges must be AB, AC or BC")
        if self.tag is not None and type(self.tag) is not str:
            raise InvalidInput("tag must be a string or null")
        object.__setattr__(self, "edges", tuple(sorted(set(self.edges))))


@dataclass(frozen=True)
class State:
    # Construct through state(); entries are (atom, coefficient).
    terms: tuple = ()

    def __post_init__(self):
        if type(self.terms) is not tuple:
            raise InvalidInput("canonical tuple required")
        keys = []
        for atom, coefficient in self.terms:
            keys.append(key(atom))
            if type(coefficient) is not Fraction or not coefficient:
                raise InvalidInput("canonical nonzero Fraction required")
        if keys != sorted(set(keys)):
            raise InvalidInput("state terms must be unique and canonical")


@dataclass(frozen=True)
class Box:
    payload: State

    def __post_init__(self):
        if not isinstance(self.payload, State):
            raise InvalidInput("this model quotes whole states only")


@dataclass(frozen=True)
class Assembly:
    left: object
    right: object
    relation: str = "uses"

    def __post_init__(self):
        key(self.left)
        key(self.right)
        if self.relation not in ("uses", "contains"):
            raise InvalidInput("unsupported assembly relation")


def key(atom):
    if isinstance(atom, Graph):
        return ("graph", atom.edges, atom.tag is not None, atom.tag or "")
    if isinstance(atom, Box):
        return ("box", tuple((key(a), c.numerator, c.denominator)
                             for a, c in atom.payload.terms))
    if isinstance(atom, Assembly):
        return ("assembly", atom.relation, key(atom.left), key(atom.right))
    raise InvalidInput("unsupported configuration sort")


def state(*rows):
    # Rows are (coefficient, atom); validate each row before collection.
    totals = {}
    for coefficient, atom in rows:
        key(atom)
        coefficient = rational(coefficient)
        totals[atom] = totals.get(atom, Fraction(0)) + coefficient
    return State(tuple(sorted(((a, c) for a, c in totals.items() if c),
                              key=lambda pair: key(pair[0]))))


def unit(atom):
    return state((1, atom))


def add(*states):
    return state(*((c, a) for s in states for a, c in s.terms))


def scale(c, s):
    c = rational(c)
    return state(*((c * d, a) for a, d in s.terms))


@dataclass(frozen=True)
class Rule:
    name: str
    edge: str | None = None

    def __post_init__(self):
        if self.name not in ("add", "remove", "require_absent", "forget_tag", "empty"):
            raise InvalidInput("unregistered rule")
        if self.name in ("add", "remove", "require_absent"):
            if self.edge not in EDGES:
                raise InvalidInput("rule requires one FG3 edge")
        elif self.edge is not None:
            raise InvalidInput("this rule takes no edge parameter")

    def apply(self, atom):
        if not isinstance(atom, Graph):
            raise DomainError("graph rule cannot implicitly enter a quote or assembly")
        edges = set(atom.edges)
        if self.name == "add":
            edges.add(self.edge)
        elif self.name == "remove":
            edges.discard(self.edge)
        elif self.name == "require_absent" and self.edge in edges:
            raise DomainError("required absent edge is present")
        elif self.name == "empty":
            edges.clear()
        tag = None if self.name == "forget_tag" else atom.tag
        return Graph(tuple(sorted(edges)), tag)


def push(rule, s):
    if not isinstance(rule, Rule):
        raise InvalidInput("registered Rule required")
    # Construct all images before returning a canonical result: strict execution.
    images = [(c, rule.apply(a)) for a, c in s.terms]
    return state(*images)


def restrict_absent(edge, s):
    if edge not in EDGES:
        raise InvalidInput("invalid restriction edge")
    retained, excluded = [], []
    for atom, c in s.terms:
        if not isinstance(atom, Graph):
            raise DomainError("graph predicate required")
        (retained if edge not in atom.edges else excluded).append((c, atom))
    return state(*retained), state(*excluded)


def joint(*rows):
    totals = {}
    arity = None
    for coefficient, atoms in rows:
        if type(atoms) is not tuple or not atoms:
            raise InvalidInput("nonempty tuple required")
        if arity is None:
            arity = len(atoms)
        if len(atoms) != arity:
            raise InvalidInput("mixed joint arity")
        for atom in atoms:
            key(atom)
        c = rational(coefficient)
        totals[atoms] = totals.get(atoms, Fraction(0)) + c
    return tuple(sorted(((atoms, c) for atoms, c in totals.items() if c),
                        key=lambda row: tuple(key(a) for a in row[0])))


def independent(s, t):
    return joint(*((a * b, (x, y)) for x, a in s.terms for y, b in t.terms))


def union_graphs(x, y):
    if not isinstance(x, Graph) or not isinstance(y, Graph) or x.tag != y.tag:
        raise DomainError("union requires graphs agreeing on their shared tag")
    # The fixed identities A/B/C intentionally overlap; links deduplicate.
    return Graph(tuple(sorted(set(x.edges) | set(y.edges))), x.tag)


def join(rows, mode="union"):
    if mode not in ("union", "pair", "wire_choice"):
        raise InvalidInput("unregistered join mode")
    images = []
    for atoms, coefficient in rows:
        expected = 3 if mode == "wire_choice" else 2
        if len(atoms) != expected:
            raise DomainError("joint arity differs from join domain")
        x, y = atoms[:2]
        if mode == "union":
            target = union_graphs(x, y)
        elif mode == "pair":
            target = Assembly(x, y, "uses")
        else:
            wiring = atoms[2]
            if not isinstance(wiring, Graph) or wiring.edges or wiring.tag not in ("uses", "contains"):
                raise DomainError("unsupported connection declaration")
            target = Assembly(x, y, wiring.tag)
        images.append((coefficient, target))
    return state(*images)


def marginal(rows, coordinate):
    return state(*((c, atoms[coordinate]) for atoms, c in rows))


def pack(s):
    return Box(s)


def unpack(box):
    if not isinstance(box, Box):
        raise InvalidInput("Box required")
    return box.payload


def inside(rule, box):
    return pack(push(rule, unpack(box)))


def rank(atom):
    if isinstance(atom, Graph):
        return 0
    if isinstance(atom, Box):
        return 1 + max((rank(a) for a, _ in atom.payload.terms), default=0)
    if isinstance(atom, Assembly):
        return max(rank(atom.left), rank(atom.right))
    raise InvalidInput("unsupported atom")


@dataclass(frozen=True)
class View:
    source: State
    displayed_rows: tuple


def edge_view(s):
    if any(not isinstance(a, Graph) for a, _ in s.terms):
        raise DomainError("edge view only supports Graph")
    return View(s, tuple((a.edges, str(c)) for a, c in s.terms))


def dump_graph_state(s):
    if any(not isinstance(a, Graph) for a, _ in s.terms):
        raise DomainError("JSON interchange only supports Graph states")
    return json.dumps({"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
                       "state": [{"coefficient": f"{c.numerator}/{c.denominator}",
                                  "config": {"edges": list(a.edges), "tag": a.tag}}
                                 for a, c in s.terms]}, sort_keys=True)


def load_graph_state(text):
    obj = json.loads(text)
    if not isinstance(obj, dict) or set(obj) - {"kernel", "profile", "model", "context", "inquiry", "state"}:
        raise InvalidInput("invalid top-level record")
    if (obj.get("kernel"), obj.get("profile"), obj.get("model")) != (KERNEL, PROFILE, MODEL):
        raise InvalidInput("version mismatch")
    if type(obj.get("state")) is not list:
        raise InvalidInput("state array required")
    rows = []
    for row in obj["state"]:
        if not isinstance(row, dict) or set(row) != {"coefficient", "config"}:
            raise InvalidInput("invalid term record")
        cfg = row["config"]
        if not isinstance(cfg, dict) or set(cfg) != {"edges", "tag"} or type(cfg["edges"]) is not list:
            raise InvalidInput("invalid graph record")
        atom = Graph(tuple(cfg["edges"]), cfg["tag"])
        raw = row["coefficient"]
        if type(raw) is not str:
            raise InvalidInput("rational string required")
        try:
            coefficient = Fraction(raw)
        except (ValueError, ZeroDivisionError) as exc:
            raise InvalidInput("invalid rational") from exc
        if raw != f"{coefficient.numerator}/{coefficient.denominator}":
            raise InvalidInput("reduced rational encoding required")
        rows.append((coefficient, atom))
    return state(*rows)


def phase_status(rule, basis):
    groups = {}
    for g in basis:
        groups.setdefault(len(g.edges), []).append(g)
    domain_stable, congruent = True, True
    for group in groups.values():
        outcomes = []
        for g in group:
            try:
                outcomes.append(len(rule.apply(g).edges))
            except DomainError:
                outcomes.append(None)
        if any(o is None for o in outcomes) and any(o is not None for o in outcomes):
            domain_stable = False
        if len({o for o in outcomes if o is not None}) > 1:
            congruent = False
    return {"domain_saturated": domain_stable, "result_congruent": congruent}


def run_checks():
    passed = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    def rejects(name, operation, expected):
        try:
            operation()
        except expected:
            passed.append(name)
        else:
            raise AssertionError(name)

    p, q = Graph(("AB", "BC")), Graph(("AC", "BC"))
    empty, triangle = Graph(), Graph(("AB", "AC", "BC"))
    zero = state()
    s = state((1, p), (-1, q))
    ab, ac = Rule("add", "AB"), Rule("add", "AC")
    check("exact configurations stay distinct", len(s.terms) == 2)
    check("empty graph is not zero", unit(empty) != zero)
    check("exact cancellation", state((1, p), (-1, p)) == zero)
    check("fraction arithmetic", state((Fraction(1, 3), p), (Fraction(2, 3), p)) == unit(p))
    check("first extension", push(ab, s) == state((1, p), (-1, triangle)))
    check("second extension cancels", push(ac, push(ab, s)) == zero)
    check("total-map composition", push(ac, push(ab, s)) ==
          state(*((c, ac.apply(ab.apply(a))) for a, c in s.terms)))
    check("total-map linearity", push(ab, add(s, scale(2, unit(q)))) ==
          add(push(ab, s), scale(2, push(ab, unit(q)))))

    tagged = state((1, Graph(p.edges, "first")), (-1, Graph(q.edges, "second")))
    kept = push(ac, push(ab, tagged))
    check("semantic tags preserve distinction", len(kept.terms) == 2)
    check("explicit tag removal cancels", push(Rule("forget_tag"), kept) == zero)
    view = edge_view(kept)
    check("view retains source", view.source == kept and len(view.source.terms) == 2)
    check("identical displayed graphs do not merge", view.displayed_rows[0][0] == view.displayed_rows[1][0])

    require = Rule("require_absent", "AB")
    rejects("strict supported-domain rejection", lambda: push(require, s), DomainError)
    retained, excluded = restrict_absent("AB", s)
    check("restriction preserves signed coefficients", retained == scale(-1, unit(q)) and excluded == unit(p))
    check("restriction accounts for input", add(retained, excluded) == s)
    rejects("unknown node rejected", lambda: Graph(("AD",)), InvalidInput)
    rejects("invalid opposite terms rejected", lambda: state((1, object()), (-1, object())), InvalidInput)
    rejects("invalid zero term rejected", lambda: state((0, object())), InvalidInput)
    rejects("float coefficient rejected", lambda: state((0.1, p)), InvalidInput)

    rnd, sqr = Graph((), "round"), Graph((), "square")
    red, blue = Graph((), "red"), Graph((), "blue")
    shared = joint((2, (rnd, red)), (-1, (sqr, blue)))
    direct = join(shared, "pair")
    wrong = join(independent(marginal(shared, 0), marginal(shared, 1)), "pair")
    check("shared coefficient used once", direct == state((2, Assembly(rnd, red)), (-1, Assembly(sqr, blue))))
    check("marginal product changes dependencies", len(wrong.terms) == 4 and wrong != direct)
    wiring = joint((2, (rnd, red, Graph((), "uses"))),
                   (-1, (rnd, red, Graph((), "contains"))))
    check("joint wiring alternatives", join(wiring, "wire_choice") ==
          state((2, Assembly(rnd, red, "uses")), (-1, Assembly(rnd, red, "contains"))))
    rejects("strict incompatible gluing", lambda: join(joint((1, (p, q)), (1, (rnd, red)))), DomainError)
    check("bilinear independent gluing", join(independent(add(unit(p), unit(q)), unit(empty))) ==
          add(join(independent(unit(p), unit(empty))), join(independent(unit(q), unit(empty)))))

    box = pack(s)
    check("whole-family unpack", unpack(box) == s)
    check("packing is not branchwise distribution", unit(box) != state((1, pack(unit(p))), (-1, pack(unit(q)))))
    box_zero = inside(ac, inside(ab, box))
    check("quoted zero is an entity", unpack(box_zero) == zero and unit(box_zero) != zero)
    outer = Assembly(box, Graph((), "consumer"), "uses")
    check("recursive construction rank", rank(pack(unit(outer))) == 2)
    check("immutable original quote", unpack(box) == s)
    rejects("no implicit quote execution", lambda: push(ab, unit(box)), DomainError)

    all_graphs = [Graph(tuple(es)) for n in range(4) for es in combinations(sorted(EDGES), n)]
    count = 0
    for a, b, c in product(all_graphs, repeat=3):
        if union_graphs(union_graphs(a, b), c) != union_graphs(a, union_graphs(b, c)):
            raise AssertionError("fixed-label union associativity")
        count += 1
    check("fixed-label union associativity", count == 512)
    phase_add = phase_status(ab, all_graphs)
    phase_domain = phase_status(require, all_graphs)
    check("phase-result counterexample", not phase_add["result_congruent"])
    check("phase-domain counterexample", not phase_domain["domain_saturated"])
    remove = Rule("remove", "AB")
    check("noncommuting operations", push(remove, push(ab, unit(empty))) != push(ab, push(remove, unit(empty))))

    # A cancelled intermediate state can avoid a later partial-domain failure.
    forget = Rule("empty")
    # Use a partial rule whose failure appears after a many-to-one total map.
    intermediate = push(ab, push(ac, s))
    check("zero support succeeds under a partial rule", push(require, intermediate) == zero)
    rejects("partial composition cannot be rewritten across cancellation",
            lambda: state(*((c, require.apply(ab.apply(ac.apply(a)))) for a, c in s.terms)), DomainError)
    check("zero under a total map", push(forget, zero) == zero)

    encoded = dump_graph_state(tagged)
    check("exact JSON round trip", load_graph_state(encoded) == tagged)
    invalid = json.loads(encoded)
    invalid["state"][0]["config"]["edges"] = ["AD"]
    invalid["state"][0]["coefficient"] = "0/1"
    rejects("invalid imported zero term rejected", lambda: load_graph_state(json.dumps(invalid)), InvalidInput)
    return {"kernel": KERNEL, "profile": PROFILE, "example_model": MODEL,
            "python": sys.version.split()[0], "checks_passed": len(passed),
            "basis_graphs": len(all_graphs), "associativity_triples": count,
            "phase_add_AB": phase_add, "phase_require_absent_AB": phase_domain,
            "checks": passed,
            "scope": "Finite internal checks; no general gluing, hardware, performance or full-kernel proof."}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, ensure_ascii=False))
```


# Appendix VI — Combined family-state executable model

## VI.1 Scope

The following companion implements CG3/0.1 by importing the separately versioned IC/0.1 and FG3/0.1 companions. It is reproduced here exactly as stored in **E7G-T_Combined_Family_State_v0.1.py**. Its internal run on 2026-09-08 passed **40** named checks. The complete machine-readable record is stored in **E7G-T_Combined_Family-State_Validation_v0.1.json**.

## VI.2 Source

```python
#!/usr/bin/env python3
"""E7G-T CFS/0.1, CG3/0.1 combined family-state prototype.

Authors: Alexander Gregory Wingate and Oleksandr Razinkov.
Specification example, CC BY-SA 4.0.
Python 3.10+, standard library only. Keep this file beside the SF and EEC
companions. Run it to execute the demonstration and checks.

The outer value is an SF-style exact symbolic family. Each member of that
family is an EEC-Q/FG3 finite rational state. This is a bounded reference
model, not a general solver, compiler, quantum state model or CAD kernel.
"""

from dataclasses import dataclass
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import json
import sys


KERNEL = "0.12-experimental"
PROFILE = "CFS/0.1"
MODEL = "CG3/0.1"
HERE = Path(__file__).resolve().parent


def _load(name, filename):
    spec = spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load required companion {filename}")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sf = _load("e7gt_sf_v01", "E7G-T_Symbolic_Families_v0.1.py")
eec = _load("e7gt_eec_v012", "E7G-T_v0.12_Executable_Examples.py")

Poly = sf.Poly
Interval = sf.Interval
Points = sf.Points
Graph = eec.Graph
State = eec.State
Rule = eec.Rule


class InvalidInput(ValueError):
    pass


class DomainError(ValueError):
    pass


class Unsupported(ValueError):
    pass


class ResourceLimit(ValueError):
    pass


def _domain_key(domain):
    if isinstance(domain, Interval):
        return ("interval", sf.qstr(domain.lo), sf.qstr(domain.hi),
                domain.left_closed, domain.right_closed)
    if isinstance(domain, Points):
        return ("points", tuple(sf.qstr(t) for t in domain.values))
    raise InvalidInput("CG3 requires an IC/0.1 Interval or Points domain")


def _active(poly, domain):
    if poly == Poly((0,)):
        return False
    if isinstance(domain, Interval):
        return domain.lo < domain.hi or domain.contains(domain.lo)
    return any(poly.at(t) != 0 for t in domain.values)


def _canonical_terms(domain, rows):
    totals = {}
    for atom, coefficient in rows:
        eec.key(atom)
        if not isinstance(coefficient, Poly):
            coefficient = Poly((coefficient,))
        totals[atom] = totals.get(atom, Poly((0,))) + coefficient
    return tuple(sorted(((atom, poly) for atom, poly in totals.items()
                         if _active(poly, domain)), key=lambda row: eec.key(row[0])))


@dataclass(frozen=True)
class StateFamily:
    """A finite symbolic description t -> finite EEC-Q state."""

    domain: object
    terms: tuple
    context: str = "CG3/0.1"

    def __post_init__(self):
        try:
            domain = sf.normal_domain(self.domain)
        except sf.InvalidInput as exc:
            raise InvalidInput(str(exc)) from exc
        _domain_key(domain)
        if type(self.terms) is not tuple:
            raise InvalidInput("state-family terms must be a tuple")
        if type(self.context) is not str or not self.context or len(self.context) > 256:
            raise InvalidInput("bounded nonempty context required")
        canonical = _canonical_terms(domain, self.terms)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "terms", canonical)

    @property
    def empty(self):
        return isinstance(self.domain, Points) and not self.domain.values

    def instantiate(self, t):
        t = sf.q(t)
        if not self.domain.contains(t):
            raise InvalidInput("assignment outside state-family domain")
        return eec.state(*((poly.at(t), atom) for atom, poly in self.terms))

    def restrict(self, domain):
        return StateFamily(sf.intersect(self.domain, domain), self.terms, self.context)

    def add(self, other):
        _same_outer(self, other)
        return StateFamily(self.domain, self.terms + other.terms, self.context)

    def scale(self, coefficient):
        coefficient = coefficient if isinstance(coefficient, Poly) else Poly((coefficient,))
        return StateFamily(self.domain,
                           tuple((atom, coefficient * poly) for atom, poly in self.terms),
                           self.context)

    def transform(self, rule):
        if not isinstance(rule, Rule):
            raise InvalidInput("registered FG3 Rule required")
        images = []
        for atom, poly in self.terms:
            try:
                images.append((rule.apply(atom), poly))
            except eec.DomainError as exc:
                raise DomainError(f"rule is not total on the admitted family: {exc}") from exc
        return StateFamily(self.domain, tuple(images), self.context)

    def extend_fixed(self, fixed, mode="union"):
        if not isinstance(fixed, State):
            raise InvalidInput("fixed inner EEC state required")
        if mode not in ("union", "pair"):
            raise InvalidInput("CG3 supports union or pair extension")
        rows = []
        for left, poly in self.terms:
            for right, coefficient in fixed.terms:
                try:
                    target = (eec.union_graphs(left, right) if mode == "union"
                              else eec.Assembly(left, right, "uses"))
                except eec.DomainError as exc:
                    raise DomainError(f"extension is not total on the admitted family: {exc}") from exc
                rows.append((target, poly * coefficient))
        return StateFamily(self.domain, tuple(rows), self.context)

    def shared_union(self, other):
        """Pointwise inner product and graph union using the same outer t."""
        _same_outer(self, other)
        rows = []
        for left, p in self.terms:
            for right, q in other.terms:
                try:
                    target = eec.union_graphs(left, right)
                except eec.DomainError as exc:
                    raise DomainError(f"shared union is not total: {exc}") from exc
                rows.append((target, p * q))
        return StateFamily(self.domain, tuple(rows), self.context)

    def fingerprint(self):
        raw = json.dumps(to_record(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


def _same_outer(left, right):
    if not isinstance(right, StateFamily):
        raise InvalidInput("StateFamily required")
    if _domain_key(left.domain) != _domain_key(right.domain) or left.context != right.context:
        raise InvalidInput("shared composition requires the same pinned outer domain and context")


@dataclass(frozen=True)
class Observable:
    """A rational linear functional on the inner graph-state coefficients."""

    name: str
    weights: tuple
    direction: str = "max"

    def __post_init__(self):
        if type(self.name) is not str or not self.name or self.direction not in ("min", "max"):
            raise InvalidInput("observable requires a name and min/max direction")
        if type(self.weights) is not tuple:
            raise InvalidInput("observable weights must be a tuple")
        totals = {}
        for atom, weight in self.weights:
            eec.key(atom)
            weight = sf.q(weight)
            totals[atom] = totals.get(atom, Fraction(0)) + weight
        object.__setattr__(self, "weights", tuple(sorted(
            ((atom, weight) for atom, weight in totals.items() if weight),
            key=lambda row: eec.key(row[0]))))

    def expression(self, family):
        weights = dict(self.weights)
        result = Poly((0,))
        for atom, poly in family.terms:
            result = result + poly * weights.get(atom, Fraction(0))
        return result


def coefficient(atom, direction="max"):
    return Observable(f"coefficient:{eec.key(atom)}", ((atom, Fraction(1)),), direction)


@dataclass(frozen=True)
class FamilyQuote:
    payload: StateFamily

    def __post_init__(self):
        if not isinstance(self.payload, StateFamily):
            raise InvalidInput("family-state quote requires StateFamily")


@dataclass(frozen=True)
class Realisation:
    status: str
    source: StateFamily
    residual: StateFamily | None
    state: State | None = None
    witnesses: tuple = ()
    scores: tuple = ()
    reason: str = ""


def _inspect_state_image(family, budget):
    if isinstance(family.domain, Points):
        points = family.domain.values
        varying = False
    else:
        varying = any(poly.degree > 0 for _, poly in family.terms)
        degree = max((poly.degree for _, poly in family.terms), default=0)
        count = max(2, degree + 1) if varying else 1
        points = tuple(sf.q(family.domain.lo +
                            (family.domain.hi - family.domain.lo) * Fraction(i + 1, count + 1))
                       for i in range(count))
    if len(points) > budget:
        raise ResourceLimit("state-image witness candidate limit")
    found = {}
    for t in points:
        state = family.instantiate(t)
        found.setdefault(state, t)
        if len(found) == 2:
            return None, tuple((state, witness) for state, witness in found.items())
    if varying:
        raise AssertionError("nonconstant coefficient failed exact variation witness bound")
    if not found:
        raise AssertionError("nonempty family had no state witness")
    state = next(iter(found))
    return state, ((state, found[state]),)


def realise(family, *objectives, max_candidates=4096):
    if not isinstance(family, StateFamily) or any(not isinstance(o, Observable) for o in objectives):
        raise InvalidInput("StateFamily and Observable objects required")
    if type(max_candidates) is not int or max_candidates < 1:
        raise InvalidInput("positive candidate limit required")
    if len(objectives) > 32:
        raise InvalidInput("at most 32 objectives")
    if family.empty:
        return Realisation("EMPTY", family, family, reason="outer domain is empty")
    current, scores = family, []
    try:
        for objective in objectives:
            expression = objective.expression(current)
            try:
                domain, bound, attained = sf.argopt(
                    expression, current.domain, objective.direction, max_candidates)
            except sf.Unsupported as exc:
                raise Unsupported(str(exc)) from exc
            except sf.ResourceLimit as exc:
                raise ResourceLimit(str(exc)) from exc
            scores.append((objective.name, objective.direction, bound, attained))
            current = current.restrict(domain)
            if not attained:
                return Realisation("UNATTAINED", family, current, scores=tuple(scores),
                                   reason="exact bound exists but is not attained")
        state, witnesses = _inspect_state_image(current, max_candidates)
        return Realisation("UNIQUE" if state is not None else "AMBIGUOUS",
                           family, current, state, witnesses, tuple(scores),
                           "one inner state in the residual image" if state is not None
                           else "at least two distinct residual inner states")
    except Unsupported as exc:
        return Realisation("UNSUPPORTED", family, None, scores=tuple(scores), reason=str(exc))
    except ResourceLimit as exc:
        return Realisation("RESOURCE_LIMIT", family, None, scores=tuple(scores), reason=str(exc))


def _graph_record(graph):
    return {"edges": list(graph.edges), "tag": graph.tag}


def _graph_from_record(record):
    if type(record) is not dict or set(record) != {"edges", "tag"} or type(record["edges"]) is not list:
        raise InvalidInput("invalid graph record")
    return Graph(tuple(record["edges"]), record["tag"])


def to_record(family):
    kind = _domain_key(family.domain)
    domain = ({"kind": "interval", "lo": kind[1], "hi": kind[2],
               "left_closed": kind[3], "right_closed": kind[4]}
              if kind[0] == "interval" else {"kind": "points", "values": list(kind[1])})
    return {"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
            "context": family.context, "domain": domain,
            "terms": [{"config": _graph_record(atom),
                       "coefficient": [sf.qstr(c) for c in poly.coefficients]}
                      for atom, poly in family.terms]}


def from_record(record):
    required = {"kernel", "profile", "model", "context", "domain", "terms"}
    if type(record) is not dict or set(record) != required:
        raise InvalidInput("invalid combined-family record")
    if (record["kernel"], record["profile"], record["model"]) != (KERNEL, PROFILE, MODEL):
        raise InvalidInput("unsupported combined-profile version")
    d = record["domain"]
    if type(d) is not dict:
        raise InvalidInput("domain record required")
    if d.get("kind") == "interval" and set(d) == {"kind", "lo", "hi", "left_closed", "right_closed"}:
        domain = Interval(sf.qparse(d["lo"]), sf.qparse(d["hi"]),
                          d["left_closed"], d["right_closed"])
    elif d.get("kind") == "points" and set(d) == {"kind", "values"} and type(d["values"]) is list:
        domain = Points(tuple(sf.qparse(x) for x in d["values"]))
    else:
        raise InvalidInput("unsupported domain record")
    if type(record["terms"]) is not list or len(record["terms"]) > 64:
        raise InvalidInput("bounded term array required")
    rows = []
    for row in record["terms"]:
        if type(row) is not dict or set(row) != {"config", "coefficient"} or type(row["coefficient"]) is not list:
            raise InvalidInput("invalid symbolic term record")
        rows.append((_graph_from_record(row["config"]),
                     Poly(tuple(sf.qparse(c) for c in row["coefficient"]))))
    return StateFamily(domain, tuple(rows), record["context"])


def state_record(state):
    return [{"config": _graph_record(atom), "coefficient": sf.qstr(value)}
            for atom, value in state.terms]


def result_record(result):
    return {"status": result.status, "source_id": result.source.fingerprint(),
            "residual": None if result.residual is None else to_record(result.residual),
            "state": None if result.state is None else state_record(result.state),
            "scores": [{"name": n, "direction": d, "bound": sf.qstr(v), "attained": a}
                       for n, d, v, a in result.scores],
            "witnesses": [{"t": sf.qstr(t), "state": state_record(state)}
                          for state, t in result.witnesses], "reason": result.reason}


def run_checks():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def rejects(name, operation, expected=InvalidInput):
        try:
            operation()
        except expected:
            checks.append(name)
        else:
            raise AssertionError(name)

    t = Poly((0, 1))
    one_minus_t = Poly((1, -1))
    empty = Graph()
    ab = Graph(("AB",))
    ac = Graph(("AC",))
    bc = Graph(("BC",))
    domain = Interval(0, 1)

    family = StateFamily(domain, ((empty, t), (ab, one_minus_t)))
    check("outer family retains two symbolic inner terms", len(family.terms) == 2)
    check("left endpoint instantiates exact EEC state", family.instantiate(0) == eec.unit(ab))
    check("right endpoint instantiates exact EEC state", family.instantiate(1) == eec.unit(empty))
    check("interior instantiation uses rational coefficients",
          family.instantiate(Fraction(1, 2)) == eec.state((Fraction(1, 2), empty),
                                                          (Fraction(1, 2), ab)))
    check("unresolved family is ambiguous", realise(family).status == "AMBIGUOUS")

    choose_empty = realise(family, coefficient(empty))
    check("observable realisation is unique", choose_empty.status == "UNIQUE")
    check("observable selects the winning inner state", choose_empty.state == eec.unit(empty))
    check("observable records exact optimum", choose_empty.scores[0][2] == 1)
    choose_ab = realise(family, coefficient(ab))
    check("opposite observable selects other endpoint", choose_ab.state == eec.unit(ab))

    mapped = family.transform(Rule("add", "AB"))
    check("pushforward collects equal configuration images", len(mapped.terms) == 1)
    check("symbolic coefficients combine before instantiation", mapped.terms[0][1] == Poly((1,)))
    check("constant mapped state realises without objectives", realise(mapped).state == eec.unit(ab))
    check("pointwise pushforward law",
          mapped.instantiate(Fraction(1, 3)) == eec.push(Rule("add", "AB"),
                                                        family.instantiate(Fraction(1, 3))))

    cancelled = StateFamily(domain, ((empty, t), (empty, -t)))
    check("pointwise symbolic cancellation produces zero family", not cancelled.terms)
    check("zero state family has singleton image", realise(cancelled).state == State())

    restricted = family.restrict(Points((Fraction(1, 2),)))
    check("restriction preserves exact pointwise state", realise(restricted).status == "UNIQUE")
    check("restriction result is mixed inner state",
          realise(restricted).state == family.instantiate(Fraction(1, 2)))
    check("empty outer restriction remains distinct from zero inner state",
          realise(family.restrict(Points(()))).status == "EMPTY")
    degenerate_open = StateFamily(Interval(0, 0, False, False), ((empty, Poly((1,))),))
    check("degenerate open interval normalises to empty outer family",
          realise(degenerate_open).status == "EMPTY")

    open_family = StateFamily(Interval(0, 1, True, False), ((empty, t),))
    check("open optimum is unattained", realise(open_family, coefficient(empty)).status == "UNATTAINED")
    constant = StateFamily(domain, ((ac, Poly((2,))),))
    check("constant inner state over infinite outer domain is unique",
          realise(constant).state == eec.state((2, ac)))

    fixed_extended = family.extend_fixed(eec.unit(ac), "union")
    check("fixed extension acts pointwise",
          fixed_extended.instantiate(Fraction(1, 2)) ==
          eec.join(eec.independent(family.instantiate(Fraction(1, 2)), eec.unit(ac))))

    left = StateFamily(domain, ((empty, t), (ab, one_minus_t)))
    right = StateFamily(domain, ((ac, t), (bc, one_minus_t)))
    shared = left.shared_union(right)
    check("shared composition uses one outer parameter", shared.instantiate(0) == eec.unit(Graph(("AB", "BC"))))
    check("shared composition right endpoint", shared.instantiate(1) == eec.unit(ac))
    expected_mid = eec.join(eec.independent(left.instantiate(Fraction(1, 2)),
                                             right.instantiate(Fraction(1, 2))))
    check("shared composition equals pointwise EEC extension", shared.instantiate(Fraction(1, 2)) == expected_mid)
    check("shared coefficients multiply as polynomials",
          any(poly.degree == 2 for _, poly in shared.terms))

    summed = family.add(StateFamily(domain, ((empty, one_minus_t), (ab, t))))
    check("family addition is pointwise", summed.instantiate(Fraction(2, 5)) ==
          eec.add(family.instantiate(Fraction(2, 5)),
                  StateFamily(domain, ((empty, one_minus_t), (ab, t))).instantiate(Fraction(2, 5))))
    check("symbolic scaling is pointwise", family.scale(t).instantiate(Fraction(1, 2)) ==
          eec.scale(Fraction(1, 2), family.instantiate(Fraction(1, 2))))

    record = to_record(shared)
    check("canonical interchange round trip", from_record(record) == shared)
    check("canonical fingerprint round trip", from_record(record).fingerprint() == shared.fingerprint())
    check("family quote retains whole combined object", FamilyQuote(shared).payload is shared)

    two_stage = StateFamily(Interval(-1, 1), ((empty, Poly((1, 0, -1))),
                                              (ab, Poly((0, 1, 1)))))
    result = realise(two_stage, coefficient(empty), coefficient(ab))
    check("lexicographic objectives are supported", result.status == "UNIQUE")
    check("first objective fixes its winner before second", result.state == eec.unit(empty))

    partial = StateFamily(domain, ((ab, Poly((1,))),))
    rejects("partial rule is rejected over active family",
            lambda: partial.transform(Rule("require_absent", "AB")), DomainError)
    inactive = StateFamily(Points((0,)), ((ab, t), (empty, Poly((1,)))))
    check("inactive finite-domain term is removed", len(inactive.terms) == 1)
    check("removed inactive term causes no false domain error",
          inactive.transform(Rule("require_absent", "AB")).instantiate(0) == eec.unit(empty))
    rejects("shared composition rejects different outer domains",
            lambda: family.shared_union(StateFamily(Interval(0, 2), ((ac, t),))))
    rejects("assignment outside domain is rejected", lambda: family.instantiate(2))
    rejects("non-rational symbolic coefficient is rejected", lambda: StateFamily(domain, ((empty, 0.5),)), sf.InvalidInput)
    rejects("malformed interchange record is rejected", lambda: from_record({}))

    demonstration = {
        "source": to_record(family),
        "source_at_half": state_record(family.instantiate(Fraction(1, 2))),
        "realisation": result_record(choose_empty),
        "pushforward": to_record(mapped),
        "shared_composition": to_record(shared),
        "shared_at_half": state_record(shared.instantiate(Fraction(1, 2))),
    }
    return checks, demonstration


if __name__ == "__main__":
    checks, demonstration = run_checks()
    print(json.dumps({"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
                      "python": sys.version.split()[0], "passed": len(checks),
                      "checks": checks, "demonstration": demonstration},
                     indent=2, sort_keys=True))
```

## VI.3 Validation boundary

The run validates the bounded Python reference model. It is not an independent reproduction, a proof of the general CFS calculus, a performance comparison or a quantum execution result. The recorded implementation SHA-256 is `ed6ba76f6638c859e65d9908ecd4ef2539cd1348df8249471ca706a51b94d542`.

# Part II — Preserved UC5 constitutional reference

The following reference body is reproduced unchanged from the repository's current **E7G-T_Kernel_v0.11_UC5_Unified_Public_Reference_Specification.md** predecessor. Its internal section numbering, older version strings, public-reference anchors and informative module labels are historical source content. Read its concepts together with the v0.12 scope in §X.0 and the explicit migration refinements in §X.14. This inclusion makes the document self-contained; it does not claim that the predecessor's maturity gates have been passed.

Source metadata, retained for provenance rather than as v0.12 front matter:

```yaml
title: "E7G-T Unified Geometry-Thinking Kernel"
subtitle: "Extensional–Projective–Phase Geometry of Configurations and Time"
version: "0.11-UC5"
date: "2026-08-24"
author: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
license_url: "https://creativecommons.org/licenses/by-sa/4.0/"
status: "Unified canonical reference candidate with restored first-class temporal geometry and informative observational-claim, temporal-orientation, topological-overlay, and relative-support pilot modules"
normativity: "Normative within this candidate unless explicitly marked informative; the observational-claim module in §3.9 and its labelled extensions, the temporal-orientation module in §§5.13.1–5.13.6 and its labelled extensions, the topological-overlay module in §§8.13.1–8.13.6 and its labelled extensions, and the relative-support module in §9.15 and its labelled extensions remain informative pending pilot validation"
family_posture: "Proposed successor-integration of E7G-T v0.9 and E7GT-Φ v0.3.2"
language_convention: "British English"
ai_use: "Load as a modular modelling and reasoning kernel. Apply the shared constitutional core first, then use the extensional-projective, temporal-geometry, operational-phase, or combined route. Treat time as a first-class extensional, projective, and inquiry-relative phase structure when temporal distinctions matter. When the observational-claim pilot module is invoked, distinguish observation records and observational claims from interpretations, preserve observer, viewing, protocol, temporal support, conflict, and unknowns, and do not mistake an admissible observational field for complete reality. When the temporal-orientation pilot module is invoked, declare the observer locality and relation kind, keep reverse reconstruction distinct from time-reversal symmetry and causal reversal, distinguish history-whole membership from clock simultaneity, and treat history relevance narrowing as epistemic unless a stronger bridge is supplied. When the topological-overlay pilot module is invoked, declare the carrier and topology, keep operational adjacency and phase boundaries distinct from topological neighbourhood and boundary, and do not infer continuity, homeomorphism, metric, order, orientation, or causation from geometric vocabulary alone. When the relative-support pilot module is invoked, distinguish admissibility from degree of support, declare the support carrier, semantics, provenance, update rule, and calibration posture, preserve low-support alternatives unless separately excluded, and do not treat stronger support as truth or weaker support as impossibility. Select the smallest output profile that changes the next responsible move without hiding risk."
```

<!-- BEGIN PRESERVED UC5 BODY -->

# E7G-T Unified Geometry-Thinking Kernel

## Extensional–Projective–Phase Geometry of Configurations and Time

**Authors:** Alexander Gregory Wingate and Oleksandr Razinkov

**Copyright:** © 2026 Alexander Gregory Wingate and Oleksandr Razinkov

**Licence:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

> **Canonical public definition.** E7G-T is a geometry-first modelling language and practical calculus for making structural and temporal extension, projection, preservation, loss, reconstruction, operational sameness, material boundaries, transition paths, bridge mode, and admissible use visible.

> **Canonical practical question.** What is being modelled, what does the current representation preserve or lose, which differences matter for this inquiry, and what is the next responsible move?

Capitalised **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL** state obligations on conforming analyses, reports, implementations, or validators. Mathematical definitions and conditions are stated declaratively.

---

## 0. Status, Scope, and Use Posture

E7G-T v0.11-UC5 is a unified reference candidate integrating three complementary routes:

1. the **extensional–projective route**, which explains construction, order-role placement, viewing, projection, preservation, loss, transformation, reconstruction, and bridge discipline; and
2. the **temporal-geometry route**, which applies extension, viewing, projection, reconstruction, transformation, and inquiry-relative phase classification to temporal structures themselves; and
3. the **operational-phase route**, which explains inquiry-relative sameness, phase classification, material boundaries, admitted transitions, path choice, operation order, representative dependence, and abstraction stability.

UC2 additionally includes an **informative observational-claim pilot module**. The module makes explicit how declared viewings license observational claims, how interpretations depend on observations and added inferential machinery, how observer-indexed fields may be composed without erasing disagreement or unknowns, and how temporal support bounds generalisation. It is not yet part of the normative constitutional core.

UC3 additionally includes an **informative temporal-orientation, observer-locality, and history-relevance pilot module**. It distinguishes a reversed view or reconstruction from time-reversal symmetry and reversed physical causation; distinguishes joint membership in a history-whole from clock simultaneity; and defines observer-relative narrowing of compatible histories without treating excluded alternatives as destroyed, unrealised, or nonexistent. It is not yet part of the normative constitutional core.

UC4 additionally includes an **informative topological-overlay pilot module**. It permits a declared carrier to be equipped with a declared topology when continuity, connectedness, separation, neighbourhood, path, quotient, or deformation structure is material to the inquiry. It keeps operational adjacency, phase boundaries, order, orientation, metric, and causation distinct from topology and requires topological claims to satisfy their own mathematical conditions. It is not yet part of the normative constitutional core.

UC5 additionally includes an **informative relative-support overlay pilot module**. It permits admitted reconstruction candidates, histories, phase candidates, or other declared alternatives to carry inquiry-relative support relations without treating support as truth, probability, exclusion, causation, or ontology. The module is substrate-neutral: ordinal rankings, scored support, probabilistic measures, likelihood-like structures, or domain-specific support models may be used only when their carrier, semantics, provenance, update rule, calibration posture, and stop conditions are explicitly declared. Bayesian inference is therefore one possible formal implementation, not part of E7G-T's required vocabulary or constitutional core.

The unified kernel is:

- a modelling and reasoning discipline;
- a practical calculus for inspecting representations and changes;
- a reference semantics for inquiry-relative operational phase analysis;
- a candidate target for software tools and machine-checkable implementations;
- suitable for AI-output review, translation QA, document workflows, dashboards, software review, engineering analysis, proof-path accounting, and disciplined speculative bridging.

The unified kernel is **not**:

- established mathematics as a whole;
- empirical physics;
- a proof system;
- a universal ontology;
- a Theory of Everything;
- an authorisation, acceptance decision, performed action, or evidence of success;
- a replacement for mature formal, empirical, legal, medical, engineering, translation, statistical, scientific, or domain-specific methods.

### 0.1 Proper role

E7G-T may:

- frame a difficult object or claim;
- expose hidden context or inquiry changes;
- distinguish source from view;
- record what a projection preserves and loses;
- distinguish an event from an interval, a history, and a history-space;
- expose what a temporal slice, summary, sampling, branch selection, or synchronisation preserves and loses;
- distinguish an observation record and observational claim from an interpretation when the pilot module is invoked;
- expose the viewing, protocol, temporal support, evidence path, assumptions, divergences, and unknowns that bound a warranted claim;
- distinguish atemporality, unboundedness, recurrence, branching, and completion;
- classify temporal structures into inquiry-relative temporal phases;
- apply a declared topological overlay when qualitative continuity, connectedness, separation, or quotient structure materially changes the inquiry;
- represent differential support among still-admissible reconstructions, histories, or phase candidates when the relative-support pilot is explicitly invoked;
- show when reconstruction is ambiguous;
- define which variations count as operationally equivalent;
- identify phase-boundary crossings;
- compare transition paths and operation order;
- reveal representative dependence hidden by abstraction;
- route the user to stronger domain methods;
- state an admissible next move or a justified stop.

E7G-T MUST NOT be used to bypass stronger tools or convert formal-looking notation into unsupported authority.

### 0.2 Smallest-use rule

> Use the smallest route and output profile that changes the next responsible move without hiding material risk.

Do not construct a phase geometry when a direct correction, ordinary invariant check, projection-loss note, D-role placement, or established domain test already determines the action.

Do not construct a full extensional account when the only relevant question is whether two admitted configurations preserve the same protected condition.

### 0.3 Unified operating cycle

```text
modelled entity
      ↓
semantic context and inquiry
      ↓
admitted configuration description
      ↓
extension / transformation / viewing / projection
      ↓
preservation, loss, and reconstruction account
      ↓
claim typing and support account, where invoked
      ↓
operational-phase classification
      ↓
transition, boundary, path, source return, reliance, or stop
```

A compact form is:

```text
construct → temporally situate → represent → project → claim → compare → classify → navigate → verify → rely or stop
```

---

## 1. Canonical Definition and Core Thesis

### 1.1 Canonical definition

E7G-T models an entity through an inquiry-bounded relational configuration and permits three complementary geometrical analyses:

- an **extensional–projective analysis** of how the configuration is constructed, transformed, viewed, projected, and reconstructed; and
- a **temporal-geometry analysis** of how temporal localities extend into intervals, histories, history families, possibility spaces, rule spaces, and contexts, and how those structures are sliced, projected, reconstructed, transformed, and phase-classified; and
- an **operational-phase analysis** of which admitted configurations count as equivalent, which transitions cross material boundaries, and which paths preserve required invariants.

Time is not merely a label attached to a configuration or transition graph. When temporally relevant, time is itself an admitted modelling structure on which the same constitutional disciplines of extension, projection, preservation and loss, reconstruction, transformation, inquiry-relative equivalence, boundary crossing, support, and stop conditions apply.

### 1.2 Operational phase

> An operational phase is an inquiry-relative equivalence class of admitted configuration descriptions.

Configurations belong to the same operational phase when they may differ in tolerated ways while preserving the relations, invariants, behaviours, interfaces, or permitted-action signatures required for the intended use.

A phase boundary is crossed when an admitted typed change produces a target configuration that is not phase-equivalent to its source under the pinned criterion.

### 1.3 Unified core thesis

```text
A representation is not automatically its source.
A projection is not automatically a reconstruction.
A configuration is not automatically its phase.
A phase difference is not automatically a transition history.
A viewing-supported record is not automatically an interpretation, ontology, or complete reality.
A formal-looking report is not automatically evidence, proof, authorisation, or performed work.
```

### 1.4 Two modelling directions

**Extensional ascent** asks:

```text
How is the object built, bounded, related, transformed, and made accountable?
```

**Projective descent** asks:

```text
How does a richer source, whole, or configuration appear through a selected lower-order view?
```

These directions are not interchangeable. A lower-order view may be compatible with several higher-order or richer source configurations.

### 1.5 Phase-first qualification

“Phase-first” means that phase equivalence is established before an OPTIONAL D0–D7 interpretation is used to characterise the configuration. It does not mean that phase is ontologically prior to the entity, context, inquiry, or configuration description.

The dependency is:

```text
modelled entity and semantic context
        ↓
inquiry and admitted configuration descriptions
        ↓
temporal geometry where temporally relevant
        ↓
configuration and temporal phase criteria
        ↓
typed transitions, paths, boundaries, and views
        ↓
optional D0–D7 compatibility lens and derived temporal-regime profile
```

---

## 2. Route Selection and Applicability

### 2.1 Extensional–projective applicability

Use the extensional–projective route when the main question concerns:

- what is being constructed or represented;
- order-role placement;
- operational boundary selection;
- extension or composition;
- viewing or projection;
- preservation and loss;
- source reconstruction;
- transformation and transformation invariants;
- bridge-mode control around a representation;
- source versus view confusion.

### 2.2 Operational-phase applicability

Use the operational-phase route when at least one of the following is true:

- several different configurations may count as equivalent for the current purpose;
- a material boundary needs to be identified;
- admissible transitions or reachability matter;
- two possible paths may have different protected effects;
- operation order may matter;
- a phase-level abstraction may hide representative dependence;
- a projected view is being used to infer operational status;
- cross-context or cross-inquiry phase comparison is proposed;
- an operation is intended to apply uniformly to every configuration in a phase;
- a local trade-off is claimed to be unavoidable.

### 2.3 Temporal-geometry applicability

Use the temporal-geometry route when at least one of the following is true:

- an event, interval, sequence, history, history family, or temporal possibility space is the entity of concern;
- a temporal point, slice, summary, sample, branch, window, synchronisation, or final state is being used to represent a richer temporal source;
- ordering, duration, simultaneity, recurrence, branching, persistence, deadline, completion, or temporal frame affects the claim;
- several histories may produce the same observed result;
- an apparent temporal whole may be only one branch or one bounded window;
- temporal reconstruction, temporal preservation or loss, or temporal phase classification affects the next move;
- the rules, clocks, granularity, or frame by which time is described change;
- atemporality, unboundedness, recurrence, and completion need to be distinguished.

The temporal-geometry route does not require metric clock time. A partially ordered event set, discrete revision history, branching scenario family, cyclic process, or declared atemporal object may be the appropriate temporal carrier.

### 2.4 Combined applicability

Use two or more routes together when:

- an observation record or observational claim is being used to support an interpretation or operational decision;
- observations from several observers, instruments, dashboards, tests, translations, or source views are being composed;
- an interpretation extends beyond the semantic, spatial, resolution, population, or temporal support of its observations;
- a projected, summarised, translated, measured, or dashboard view is used to classify operational status;
- a temporal slice, final state, trend, forecast, deadline marker, or history summary is used to classify configuration or temporal status;
- source ambiguity may span several operational phases;
- temporal reconstruction ambiguity may span several temporal phases;
- a transformation is evaluated both for preserved structure and phase-boundary effect;
- a phase-level decision relies on a lossy representation;
- a configuration projection and a temporal projection may not commute;
- a workflow path may propagate a projection or reconstruction error into a material phase change.

### 2.5 Routing table

| Primary question | Preferred route |
| --- | --- |
| What is being constructed or projected? | Extensional–projective |
| What does the representation preserve or lose? | Extensional–projective |
| Which source configurations could explain the view? | Extensional–projective, with reconstruction-fibre semantics |
| What temporal structure does an event, interval, history, or scenario represent? | Temporal geometry |
| What does a temporal slice, sample, branch selection, or summary preserve or lose? | Temporal geometry |
| Which histories could explain the temporal view? | Temporal geometry, with temporal reconstruction-fibre semantics |
| What does the declared viewing actually license as an observational claim? | Extensional–projective, with the informative observational-claim module |
| Which assumptions or bridge rules turn observations into an interpretation? | Informative observational-claim module, optionally combined |
| Can several observers' claims be composed without hiding conflict or absence? | Informative shared-observational-field module |
| Which temporal structures count as equivalent for this inquiry? | Temporal phase |
| Which different configurations count as operationally equivalent? | Operational phase |
| Which change crosses a material boundary? | Operational phase |
| Which path preserves protected invariants? | Operational phase |
| Can one operation be applied to all phase representatives? | Operational phase |
| Does a projected view support a phase classification? | Combined |
| Does a final state or temporal summary support both configuration and temporal classification? | Combined |
| Is a bridge merely interpretive or empirically testable? | Extensional–projective bridge discipline, optionally combined |

### 2.6 Canonical non-use rule

Do not invoke E7G-T merely to create formal-looking prose.

Use ordinary prose or the relevant domain method when:

- one typo or value can be corrected directly;
- a standard test already decides the issue;
- no representation, transition, equivalence, or boundary ambiguity exists;
- the kernel does not change what can now be inspected, repaired, compared, tested, or stopped.

---

## 3. Shared Constitutional Core

### 3.1 Core dependency and notation

Let:

```text
E      = modelled entity
C      = semantic context
I      = inquiry profile
Γ      = relational configuration description of E
B      = operational model boundary
A      = admissibility predicate for configurations
Q      = phase criterion under C and I
≈Q     = phase-equivalence relation under Q
φ      = operational phase class [Γ]Q
Θ      = admitted temporal geometry for E under C and I
QΘ     = temporal-phase criterion under C and I
≈QΘ    = temporal-phase equivalence under QΘ
φΘ     = temporal phase class [θ]QΘ
≺Θ     = declared temporal precedence or causal-order relation
ExtΘ   = declared temporal extension relation or construction family
ΠΘ     = declared temporal viewing and projection family
RecΘ   = temporal reconstruction fibre
H      = admitted histories or trajectories
KΘ     = optional clock or coordinate family
RΘ     = temporal evolution, recurrence, synchronisation, or frame rules
λ      = typed change label
Tλ     = admitted configuration-level transition relation
π      = modelled-entity-preserving viewing or projection
Recπ   = reconstruction fibre under π
β      = bridge across contexts, inquiries, criteria, domains, or formalisms
LD     = optional D0–D7 compatibility lens
LΘD    = optional TD0–TD7 temporal order-role lens
LTR    = derived temporal-regime profile
Oi     = declared observer, instrument, process, or observing system
ω      = observation record produced under a declared viewing and protocol
o      = observational claim licensed by one or more observation records
ι      = interpretation derived from observations and declared inferential machinery
FO     = admissible observational field for observer O and the current inquiry
FS     = shared observational field for a declared observer set S
```

Let:

```text
Confadm(E,C,I,B,A)
```

be the family of configuration descriptions admitted for the current inquiry.

The phase classification map is:

```text
qQ : Confadm(E,C,I,B,A) → Confadm(E,C,I,B,A) / ≈Q
qQ(Γ) = [Γ]Q
```

The unified local kernel structure is:

```text
KU(E,C,I,Q,QΘ) = ⟨Confadm, Λ, T, ≈Q, Π, Θ, J, B, S⟩
```

where:

- `Λ` is the family of typed change labels;
- `T` is the labelled admitted transition relation;
- `Π` is the declared viewing family;
- `Θ` is the first-class temporal subkernel where temporal distinctions are relevant;
- `J` is the declared interface and gluing discipline;
- `B` is the boundary discipline;
- `S` is the support and evidence discipline.

This notation records a modelling lens. It does not make the modelled entity a graph, quotient object, state machine, manifold, category, physical phase space, or literal higher-dimensional structure. The temporal subkernel does not claim that physical reality has multiple literal time dimensions.

### 3.2 Shared envelope

Every non-trivial unified analysis MUST state or inherit:

```yaml
E7Envelope:
  analysisId:
  modelledEntityRef:
  semanticContextRef:
  inquiryProfileRef:
  operationalBoundaryRef:
  admittedConfigurationPredicateRef:
  routesUsed:
    - extensionalProjective
    - temporalGeometry
    - operationalPhase
  admissibleUse:
  nonAdmissibleUse:
  validityWindow:
  stopOrReopenCondition:
```

A lightweight profile MAY state these fields in prose rather than YAML.

### 3.3 Modelled entity

The modelled entity is the thing, system, text, formal object, state, claim, relation, or process being considered.

A description, report, diagram, dashboard, translation, proof text, database row, API response, or AI answer is not identical to its entity of concern unless formal identity is explicitly declared and justified.

### 3.4 Semantic context

The semantic context is the local frame governing the meanings of terms, relations, invariants, roles, and admissibility conditions.

The same words may carry different meanings in different contexts. Shared spelling creates no automatic identity or substitution right.

### 3.5 Inquiry profile

The inquiry determines which differences matter for one use.

```yaml
InquiryProfile:
  inquiryId:
  modelledEntityRef:
  purpose:
  operationalBoundary:
  observables:
  requiredInvariants:
  toleratedVariation:
  admissibilityConditions:
  resolutionPolicy:
  evidencePolicy:
  admissibleUse:
  nonAdmissibleUse:
  validityWindow:
  stopCondition:
```

The same semantic context may support several inquiries. The same configuration may receive different phase classifications under different inquiries without contradiction.

### 3.6 Configuration description

A configuration description is a bounded, typed, attributed relational account of the modelled entity for one semantic context and inquiry.

```text
Γ = ⟨N, R, J, K, A, Ev, U⟩
```

where:

- `N` — described entities, regions, states, claims, or local objects;
- `R` — typed relation assertions;
- `J` — open interfaces or environment relations;
- `K` — constraints and validity conditions;
- `A` — relevant attributes or state assertions;
- `Ev` — evidence and source references;
- `U` — unknown, omitted, contested, or unresolved positions.

This form does not require graph representation. A table, theory, proof state, structured text, architectural model, transition system, typed graph, or domain-specific formalism may be used.

```yaml
RelationAssertion:
  relationId:
  relationKind:
  sourceRef:
  targetRefs:
  semanticContextRef:
  scope:
  validityConditions:
  structuralStatus: holds | weakened | broken | created | notApplicable
  supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
  supportStatus: established | supported | suspected | disputed | unknown
  evidenceRefs:
  requiredForPhaseCriterion: false
```

### 3.7 Admission

A configuration is **admitted** when it satisfies the declared applicability, typing, boundary, and validity conditions for the current semantic context and inquiry.

Admission does not by itself mean:

- true;
- safe;
- authorised;
- accepted;
- performed;
- empirically validated;
- ready for operational reliance.

### 3.8 Support basis and support status

Every consequential structural or phase claim SHOULD distinguish:

```text
supportBasis:
  stipulation
  formalDerivation
  observation
  empiricalCalibration
  operationalValidation
  mixed
  none

supportStatus:
  established
  supported
  suspected
  disputed
  unknown
```

`supportBasis` states the kind of justification. `supportStatus` states how settled the claim is. They are not one total quality scale.

Coherence rules:

- `supportBasis: none` requires `supportStatus: unknown`;
- `established` or `supported` requires a non-`none` basis and the references appropriate to that basis;
- a stipulation may be established as a stipulation without becoming formally, empirically, or operationally established.

### 3.9 Candidate observational and interpretive claim discipline

> **Status — informative pilot module.** This section and the explicitly labelled observational-claim extensions elsewhere in UC2 are candidate constitutional material. Their capitalised requirement words define the conditions for a pilot claiming conformance to this module; they do not yet add obligations to ordinary E7G-T conformance. Promotion to the normative core requires the pilot evidence specified in §19.7 and the decision test in §19.9.

#### 3.9.1 Purpose

The existing kernel distinguishes entity, configuration, source, view, projection, reconstruction, support basis, and support status. This module adds an explicit claim-type boundary between:

```text
declared viewing and protocol
        ↓
observation record
        ↓
observational claim
        ↓
interpretation
        ↓
decision, classification, prediction, or action
```

The arrows are support dependencies, not automatic entailments. Every downward step may add loss, selection, assumptions, bridge rules, uncertainty, or decision criteria.

#### 3.9.2 Observer and observation record

An **observer** is a declared person, instrument, software process, institution, model, or composite system to which an observation record is indexed. Calling something an observer does not imply consciousness, neutrality, independence, completeness, or accuracy.

An **observation record** is an observer-indexed record produced through a declared viewing or measurement protocol under declared semantic and temporal contexts.

```yaml
ObservationRecord:
  observationId:
  observerRef:
  modelledEntityRef:
  inquiryProfileRef:
  semanticContextRef:
  viewingOrMeasurementRef:
  observationProtocolRef:
  observedAtOrDuring:
  temporalSupport:
  spatialOrPopulationSupport:
  resolution:
  recordedContent:
  provenanceRefs: []
  evidenceRefs: []
  knownLimitations: []
  unknownPositions: []
```

The record MAY contain readings, events, selections, classifications supplied by an instrument, or source-tethered descriptions. It is not thereby an unmediated copy of reality. Instrument design, categories, sampling, resolution, boundary choice, and recording rules may already structure it.

#### 3.9.3 Observational claim

An **observational claim** is a claim whose asserted content is licensed by one or more declared observation records without requiring an undeclared inference, causal explanation, value judgement, generalisation, or ontology claim.

A pilot-conforming observational claim:

- SHALL identify or inherit its observation record, observer, inquiry, semantic context, viewing or measurement, protocol, temporal support, resolution, and evidence path;
- SHALL assert no more than those declarations license;
- SHALL preserve relevant limitations, unknowns, and disputed positions;
- SHALL NOT silently convert absence of a recorded event into proof that no event occurred outside the observation system, boundary, or validity window;
- SHALL NOT be strengthened merely because several records use the same label or agree.

The distinction is operational rather than metaphysical. It asks whether the claim outruns its declared support; it does not claim that observations are theory-free or that the observer exhausts the entity.

#### 3.9.4 Interpretation

An **interpretation** is a claim derived from one or more observational claims through declared assumptions, inference rules, bridge rules, criteria, comparison classes, or external models.

```yaml
InterpretationRecord:
  interpretationId:
  supportingObservationClaimRefs: []
  assumptionRefs: []
  inferenceRuleRefs: []
  bridgeRefs: []
  externalModelRefs: []
  criterionRefs: []
  conclusion:
  inheritedLimitations: []
  addedLimitations: []
  supportBasis:
  supportStatus:
  admissibleUse:
  nonAdmissibleUse:
  validityWindow:
  stopOrReopenCondition:
```

A pilot-conforming interpretation:

- SHALL be explicitly distinguished from its supporting observations;
- SHALL preserve the limitations of every load-bearing observation;
- SHALL declare its added assumptions, inference rules, bridges, criteria, and external models;
- SHALL state the domain and temporal extent of the conclusion;
- SHALL NOT receive a stronger support status than its weakest load-bearing component unless independent evidence supplies the additional support.

Interpretation is not prohibited. The purpose of the distinction is to make the transition from record to conclusion inspectable.

#### 3.9.5 Admissible observational field

For observer `O`, define the inquiry-relative admissible observational field:

```text
FO(O; C,I,B,V,P,Θ)
  = { o | o is licensed by observation records available to O
          under semantic context C, inquiry I, boundary B,
          declared viewing or measurement V, protocol P,
          and temporal context Θ }
```

`FO` is not named `Reality(O)` because the set defines what the observer may responsibly use as observational support for the current inquiry. It does not define complete reality, complete ontology, all possible evidence, or all that exists.

Different observers may have different admissible observational fields without implying that contradictory propositions are all true. Differences may arise from access, boundary, protocol, granularity, timing, instrumentation, semantics, or error.

#### 3.9.6 Shared observational field

A shared observational field is constructed rather than assumed as primitive.

For a declared observer set `S = {O1, …, On}`:

```text
FS(S) = ⟨Cjoint, D, U⟩
```

where:

- `Cjoint` contains observations that can be jointly admitted, aligned, or composed under declared semantic bridges, provenance, admissibility, resolution, independence, and temporal conditions;
- `D` contains unresolved divergences, contradictions, calibration differences, or non-composable observations;
- `U` contains relevant unobserved, unavailable, inaccessible, or indeterminate positions.

A pilot-conforming shared-field construction:

- SHALL declare the participating observers and observation records;
- SHALL state the semantic, temporal, resolution, provenance, admissibility, and independence conditions used for composition;
- SHALL preserve relevant disagreement in `D` rather than forcing consensus;
- SHALL preserve relevant absence or indeterminacy in `U` rather than treating it as agreement;
- SHALL NOT treat inter-observer agreement as sufficient proof of truth, causal independence, complete ontology, or absence of systematic error.

Compatible observations may be mutually reinforcing, complementary, redundant, or dependent. Those relations SHALL be distinguished where they affect reliance.

#### 3.9.7 Temporal observation discipline

Every observation record has temporal support, even if that support is declared atemporal, unknown, recurring, or unbounded under a model.

An interpretation SHALL NOT be generalised beyond the temporal support of its load-bearing observations unless the extension is separately supported and the bridge from observed interval to claimed interval is declared.

For example, the disciplined observational claim is not simply:

```text
No current readers.
```

but, where supported:

```text
The declared analytics system recorded zero qualifying reader events
between t1 and t2 under protocol P and boundary B.
```

Possible interpretations include:

```text
No qualifying events were recorded during the declared window.
The contribution currently lacks readership.
The contribution lacks value.
The contribution will not gain readers.
```

Each successive formulation requires additional semantic rules, measurement assumptions, value criteria, population claims, or temporal extrapolation. None is licensed merely by the wording of the first record.

#### 3.9.8 Relation to projection, reconstruction, and phase

An observation record is normally a view or projection of a richer entity, configuration, or history. Its source possibilities remain bounded by the relevant reconstruction fibre.

An observational claim cannot license a configuration, temporal, or joint phase classification stronger than the phase candidates of its supporting view permit. An interpretation cannot repair phase-spread by assertion.

If an interpretation depends on observations from several fields, its support path MUST preserve:

```text
observation provenance
→ viewing and protocol
→ preservation and loss
→ temporal support
→ composition or divergence status
→ assumptions and bridge rules
→ conclusion and admissible use
```

#### 3.9.9 Promotion gate

This module SHOULD be promoted into the normative constitutional core only if controlled pilots show that the observation/interpretation distinction and shared-field construction:

- catch recurring material errors not already resolved by ordinary source/view, support, or reconstruction rules alone;
- remain stable across at least four materially different domains;
- can be applied without turning every statement into an unusable record burden;
- preserve disagreement and unknowns without collapsing into relativism;
- improve the next responsible move or stop decision;
- survive independent review and counterexample testing.

Until that gate is met, analyses MAY invoke the module explicitly, but ordinary E7G-T analyses are not non-conforming merely because they omit it.

### 3.10 Strict distinctions

| Distinction | Rule |
| --- | --- |
| Entity vs configuration description | The thing is not its model unless identity is declared and justified. |
| Configuration description vs report | A card, graph, table, file, or dashboard may carry a configuration; it is not the configuration merely by carrying it. |
| Semantic context vs inquiry | Context governs local meaning. Inquiry governs purpose, tolerated variation, admissible use, and stop condition. |
| Configuration vs phase | A configuration is one relational arrangement. A phase is an equivalence class of admitted configurations. |
| Exact identity vs same phase | Exact identity is stronger than phase equivalence. |
| Static phase difference vs boundary crossing | Different phases may be established without claiming a transition occurred. |
| World transformation vs configuration revision | A world transformation changes the entity or its state. A revision changes its description. |
| Viewing vs retargeting | Viewing preserves the modelled-entity reference. Retargeting changes it. |
| Reframing vs transition | Changing context, inquiry, criterion, or edition may reclassify a fixed configuration without changing the entity. |
| Classification vs support | A classification is a claim. Evidence may support it but is not identical to it. |
| Observation record vs observational claim | A record is the indexed result of a declared viewing or protocol. A claim states what that record licenses. |
| Observational claim vs interpretation | An observational claim remains within declared observational support. An interpretation adds inference, assumptions, bridges, criteria, or external models. |
| Admissible observational field vs reality | An observer-indexed field bounds responsible observational support for an inquiry; it does not define complete reality or ontology. |
| Shared field vs consensus | A shared field preserves jointly admissible content, divergence, and unknowns. Agreement alone does not establish truth or independence. |
| Structural effect vs support | `broken`, `preserved`, and `weakened` describe the model. Support fields describe justification. |
| Method vs operator vs work | A method is a way of doing. An operator is a rule. Work is a dated occurrence. |
| Phase vs lifecycle stage | An operational phase is not a project stage or time slice unless deliberately defined by a criterion. |
| D7 role vs semantic context | D7 is a compatibility-lens role, not the semantic context itself. |
| Notation vs discipline | Notation records declarations; it does not create validity. |

### 3.11 Guarded terminology

Within this kernel, unqualified **phase** means `OperationalPhaseClass`.

Use qualified terms for:

- temporal phase slice;
- lifecycle phase;
- project phase;
- thermodynamic phase;
- quantum phase;
- signal phase.

---

## 4. Boundary Discipline

The unified kernel distinguishes three boundary kinds that MUST NOT be silently collapsed. Where temporal geometry is active, the same distinctions apply to the temporal carrier.

### 4.1 Model boundary

The **model boundary** declares what belongs to the current configuration account and which interfaces remain open.

```yaml
ModelBoundary:
  boundaryRef:
  includedEntitiesOrRegions:
  excludedEntitiesOrRegions:
  openInterfaces:
  environmentRelations:
  unknownParts:
  boundaryRationale:
  inquiryProfileRef:
```

### 4.2 Admissibility boundary

The **admissibility boundary** separates configuration descriptions that satisfy the current typing, applicability, validity, and evidence-entry conditions from those that do not.

A target may leave the admitted family without being classified into another phase.

### 4.3 Phase boundary

The **phase boundary** separates configurations that are not equivalent under the pinned phase criterion.

A phase boundary is crossed only by a declared transition or path:

```text
BoundaryCrossQ(Γ —λ→ Γ′)  iff  Γ ≉Q Γ′
```

Static comparison may establish:

```text
Γ ≉Q Γ′
```

without claiming that a transition connected them.

### 4.4 Boundary rule

Boundary is contextual but not arbitrary. Each boundary MUST match the claim, inquiry, and intended use.

A change may:

- remain inside the model boundary but cross a phase boundary;
- remain in one phase but cross the admissibility boundary;
- alter the model boundary without changing the entity;
- change the entity while a report still displays the old boundary.

For temporal geometry, distinguish:

- the **temporal model boundary** — which events, intervals, histories, branches, clocks, or frames are included;
- the **temporal admissibility boundary** — which temporal descriptions satisfy the declared typing, evidence, and validity conditions;
- the **temporal phase boundary** — which admitted temporal descriptions are non-equivalent under `QΘ`.

A history may remain within the temporal model boundary while crossing a temporal phase boundary, or leave the admitted temporal family without entering another classified temporal phase.

---

## 5. D0–D7 Order Roles and First-Class Temporal Geometry

### 5.1 Status of D0–D7

D0–D7 are modelling-order roles and OPTIONAL compatibility lenses. They are not literal physical dimensions, coordinate axes, metric scores, levels of truth, or phase identifiers by default.

```text
LD : ConfigurationDescription → DRoleProfile
```

```yaml
DRoleProfile:
  configurationRef:
  activeRoles:
  roleBindings:
  dominantPresentationRole:
  criticalInvariantRoles:
  conditioningRoles:
  relationsAmongRoleBindings:
  admissibleUse:
```

### 5.2 D-role table

| D role | Unified reading |
| --- | --- |
| **D0** | locality, local mark, scalar output, accepted state, trace, pixel, point-like result |
| **D1** | path, interval, sequence, procedure, timeline segment, proof-step order |
| **D2** | surface, field, map, text, diagram, dashboard, screen, visible representation |
| **D3** | structured object, body, artefact, local system, product, formal object |
| **D4** | history, process, versioned development, world-form, event sequence |
| **D5** | possibility family, branch set, design space, model alternatives, proof-search space |
| **D6** | transformation rule, law, tactic, function, protocol, method, operator family |
| **D7** | interpretive, measurement, publication, bridge-governance, or admissible-use role |

### 5.3 D7 rule

D7 is not identical to semantic context or inquiry. It records context-like participation inside an optional order-role interpretation.

### 5.4 Independence of structural and temporal order

The D-role profile and temporal-order profile are independent coordinates of the analysis.

```text
Placement(X) = ⟨LD(X), LΘD(X), C, I⟩
```

One D2 document may be:

- a single snapshot at `TD0`;
- a version history across `TD1`;
- one member of several alternative revision histories across `TD2`.

One D3 body may be described at one event, across one life history, or across a family of possible histories. A higher structural D-role does not imply a higher temporal order, and a higher temporal order does not imply a higher structural D-role.

### 5.5 Temporal subkernel

When temporal distinctions affect the claim or next move, the analysis MUST declare or inherit a temporal subkernel:

```text
Θ(E,C,I,QΘ)
  = ⟨Tempadm, ExtΘ, ≺Θ, ΠΘ, ≈QΘ, ΛΘ, H, KΘ, RΘ, BΘ, SΘ⟩
```

where:

- `Tempadm` is the admitted family of temporal descriptions;
- `ExtΘ` is temporal extension or temporal construction;
- `≺Θ` is the declared precedence, causal-order, or other temporal-order relation;
- `ΠΘ` is the family of temporal views and projections;
- `≈QΘ` is inquiry-relative temporal-phase equivalence;
- `ΛΘ` is the family of admitted temporal change labels;
- `H` is the admitted family of histories, trajectories, or history systems;
- `KΘ` is an OPTIONAL family of clocks or temporal coordinates;
- `RΘ` is the family of evolution, branching, recurrence, synchronisation, persistence, or frame rules;
- `BΘ` is the temporal boundary discipline;
- `SΘ` is the support and evidence discipline for temporal claims.

`Θ` may be minimal. A two-version document comparison may require only an ordered pair and a declared projection. A distributed system may require partial order, clocks, synchronisation rules, and several histories.

### 5.6 TD0–TD7 temporal order-role ladder

TD0–TD7 are modelling-order roles for temporal extension. They do not assert eight physical dimensions of time.

| Temporal role | Geometric intuition | Unified temporal reading |
| --- | --- | --- |
| **TD0** | temporal point/locality | event, instant, unresolved now, dated state, local occurrence |
| **TD1** | temporal line/extension | interval, directed sequence, duration, trajectory, one history |
| **TD2** | temporal surface | related or alternative timelines; a branch, scenario, observer, or version parameter across progression |
| **TD3** | temporal body | organised history-space containing interacting, coupled, or causally related families of histories |
| **TD4** | temporal world-history | a bounded evolving whole or complete system history under the inquiry |
| **TD5** | temporal variation space | possible futures, counterfactual histories, forecasts, branch families, uncertainty over histories |
| **TD6** | temporal transformation space | clocks, evolution laws, recurrence rules, synchronisation rules, branch-generation rules, temporal operators |
| **TD7** | temporal context | frame in which ordering, simultaneity, granularity, completion, unboundedness, and admissible temporal claims are interpreted |

The ladder describes richer temporal structure, not a universal ontological sequence. A use MAY activate several roles simultaneously.

### 5.7 Temporal point, line, surface, and higher extension

A temporal locality may be represented by an event or indexed configuration:

```text
Γ(t0)
```

A temporal line may be represented by a history:

```text
h : J → Confadm
```

where `J` is an admitted ordered index set. `J` may be discrete, continuous, partially ordered, cyclically indexed, or domain-specific. No real-number clock is required by default.

A temporal surface may be represented by a family of histories:

```text
Γ : J × A → Confadm
Γ(t, α)
```

where `t ∈ J` locates a configuration along a history and `α ∈ A` identifies a branch, scenario, observer, version line, model, or alternative history.

Higher temporal roles organise relations, transformations, or possibility structures among such histories. This notation is a formal-compatibility option, not a claim that physical reality literally has two or more independent time axes.

### 5.8 Temporal extension

Temporal extension constructs a richer temporal structure from declared components:

```text
θ ↑Θ n
```

Examples include:

- event → interval;
- ordered events → history;
- one history → branching or comparative history family;
- history family → interacting history system;
- observed histories → possibility or counterfactual space;
- temporal structures → rule or context account.

Extension MUST declare:

- the temporal carrier;
- the construction or inclusion relation;
- order or compatibility constraints;
- temporal boundary;
- unresolved gaps;
- whether the result is observed, stipulated, inferred, simulated, or merely possible.

Temporal extension is not projection and does not prove that the extended structure exists outside the declared model.

### 5.9 Temporal viewing and projection

A temporal view preserves the temporal entity reference while changing access or representation:

```text
vΘ : θ ↦ vΘ(θ)
```

A temporal projection renders a reduced temporal view:

```text
πΘ^{n→k}(θ) = yΘ,  k < n
```

Common temporal projections include:

- selecting one event from an interval or history;
- selecting one interval or window from a longer history;
- selecting one branch from a history family;
- reducing a history to its initial state, final state, milestone set, trend, average, or summary;
- sampling a continuous or dense process;
- aggregating several clocks or sequences into one timeline;
- forgetting duration while preserving order;
- forgetting order while preserving event membership;
- collapsing alternative histories into one forecast or published outcome;
- presenting the current document while hiding its revision history.

Every consequential temporal projection MUST state:

```text
preservesΘ: PΘ
losesΘ: LΘ
```

Temporal loss may include order, duration, simultaneity assumptions, intermediate states, abandoned branches, recurrence evidence, causal dependencies, clock uncertainty, or the difference between observed and counterfactual history.

### 5.10 Temporal reconstruction fibre

Temporal reconstruction is set-valued unless uniqueness is established:

```text
RecΘ,π(yΘ)
  = { θ ∈ Tempadm | πΘ(θ) ≈VΘ yΘ }
```

The same final state, event record, trend, or history summary may be compatible with several histories. A temporal projection is not a temporal reconstruction.

Temporal source return is required when the compatible temporal sources differ in a way material to the inquiry, including temporal phase, deadline status, causation, audit path, recurrence, synchronisation, or admissible use.

### 5.11 Inquiry-relative temporal phase

A temporal phase is an inquiry-relative equivalence class of admitted temporal descriptions:

```text
qQΘ : Tempadm → Tempadm / ≈QΘ
qQΘ(θ) = [θ]QΘ
```

`≈QΘ` MUST be reflexive, symmetric, and transitive over the admitted temporal family.

Two non-identical histories may be in the same temporal phase when they preserve the temporal properties required for the inquiry. Examples include:

- different routes that reach the required result before the same deadline;
- histories with different local steps but the same protected precedence constraints;
- cyclic processes with different starting points but the same recurrence structure;
- revision histories that differ in wording edits but preserve the same required review and approval sequence.

They may be in different temporal phases when:

- one meets a deadline and the other does not;
- one contains the required review path and the other does not;
- one is recurrent and the other terminates;
- one preserves causal or dependency order and the other reverses it;
- one is complete under the declared closure criterion and the other has unresolved required successors.

A temporal phase is not merely a stage label. It is an equivalence class under a pinned temporal criterion and edition.

### 5.12 Temporal phase boundary and temporal phase candidates

A temporal phase boundary is crossed by an admitted temporal change when:

```text
TemporalBoundaryCrossQΘ(θ —λΘ→ θ′)
  iff  θ ≉QΘ θ′
```

For a temporal view `yΘ`, define:

```text
TemporalPhaseCandidatesQΘ(yΘ)
  = { [θ]QΘ | θ ∈ RecΘ,π(yΘ) }
```

A temporal view supports unique temporal-phase classification only when this set contains one supported candidate under the declared admission, evidence, and validity conditions. A single candidate phase does not prove a unique history.

### 5.13 Histories, order, clocks, and recurrence

A history is a configuration-indexing map or equivalent domain representation:

```text
h : J → Confadm
```

When `i ≺J j`, the declared semantics MUST state whether this means sequence, precedence, causation, dependency, clock order, or another relation. These meanings MUST NOT be silently interchanged.

An OPTIONAL clock is a map:

```text
κ : Events → K
```

where `K` is a declared coordinate or value domain. Clock equality establishes simultaneity only relative to that clock and synchronisation model.

Useful derived predicates include:

```text
BeforeΘ(a,b)       iff a ≺Θ b
Simultaneousκ(a,b) iff κ(a) = κ(b)
RecursQΘ(h,i,j)    iff i ≺J j and h(i) ≈QΘ h(j)
```

Completion MUST be defined by a closure or stop criterion. It is not inferred merely from the absence of visible later events.

### 5.13.1 Candidate temporal-orientation module

> **Informative pending pilot validation.** §§5.13.1–5.13.6 introduce optional vocabulary for applying the existing temporal and observational disciplines. They do not assert that physical time is orientation-neutral, that causal order is reversible, or that alternative histories are physically realised.

### 5.13.2 Temporal orientation and reverse representation

A **temporal orientation** is the declared direction from which a temporal structure is viewed, traversed, narrated, or reconstructed relative to its admitted order carrier.

**Extension–orientation separability.** Temporal extension, admitted temporal order, representational orientation, and directional meaning are distinct modelling ingredients. `ExtΘ` constructs or admits temporal extension. `≺Θ` records whatever ordering relation is declared. Orientation selects a direction of viewing, traversal, narration, or reconstruction relative to that structure. Neither extension alone nor a chosen representational orientation establishes causation, admissible evolution, or a physical arrow of time.

For a history:

```text
h : J → Confadm
```

and an order-reversing map `ρ : Jop → J`, a reverse representation may be written:

```text
hop = h ∘ ρ
```

Constructing `hop` establishes only that the same admitted content can be represented under the opposite orientation. It does not establish that `hop` satisfies the evolution rules `RΘ`, that a physical process can run in reverse, or that causal arrows reverse.

A conforming invocation of this module distinguishes:

```text
viewpoint reversal
≠ time-reversal symmetry
≠ causal reversal or causal neutrality
```

### 5.13.3 Observer temporal locality

An **observer temporal locality** `ℓΘ(O)` identifies the admitted locality from which observer `O` views or reconstructs a history. It is distinct from:

- the clock coordinates of the events described;
- the temporal boundary selected for the inquiry;
- the direction of generative causation;
- the full history or history-space.

A fact available at a later clock coordinate may be observationally or reconstructively first for an observer situated there without becoming chronologically first. A locality may be an endpoint under one bounded inquiry and an interior point under a wider temporal boundary.

### 5.13.4 Typed directional relations

When direction matters, the relation kind SHOULD be selected explicitly from an open typed vocabulary such as:

| Relation kind | Meaning |
| --- | --- |
| `clockPrecedence` | one event has an earlier declared clock coordinate |
| `sequence` | one item occurs earlier in an admitted ordering |
| `dependency` | one item depends on another under declared rules |
| `observationalPrecedence` | one fact becomes available to the observer before another |
| `reconstructivePrecedence` | one established fact is used first to reconstruct a history |
| `generativeCausation` | one event or condition physically or operationally produces another under an admitted causal substrate |
| `finalConstraint` | a terminal or boundary condition restricts the family of admissible complete histories |
| `globalConsistency` | events or constraints jointly belong to a self-consistent history without an asserted production direction |

These relations MAY coincide in a particular model. They MUST NOT be silently identified. In particular, a final constraint does not by itself establish that a later event physically produced an earlier event.

### 5.13.5 Orientation preservation and anti-conflation

Reversing the orientation of a history may preserve event membership, adjacency, compatibility, and complete-history identity while reversing earlier/later, antecedent/result, approach/departure, or narrative roles. The analysis MUST state which relations are preserved, reversed, hidden, or unsupported.

> Reversal of observational, narrative, or reconstructive orientation SHALL NOT be interpreted as reversal of generative causation unless the admitted causal substrate, temporal rules, and supporting evidence establish that relation.

Time-reversal symmetry requires a separate test of whether the reversed history remains admissible under `RΘ`. Physical retrocausation requires a still stronger empirical or formal bridge.

### 5.13.6 History-whole membership and observer-relative history relevance

Joint membership of events in one TD4 history-whole SHALL NOT by itself be interpreted as:

- simultaneity under a clock;
- atemporality;
- absence of preserved order;
- physical coexistence outside the declared model.

For observer `O` with accumulated valid record `r_k`, define the compatible-history family:

```text
HO(rk)
  = { h ∈ H | h remains compatible with rk
                under the fixed C, I, B, Θ, viewing, protocol,
                assumptions, and admission rules }
```

Under fixed conditions and cumulative, consistent, unretracted records:

```text
HO(rk+1) ⊆ HO(rk)
```

This is **observer-relative history relevance narrowing**. A history excluded from `HO(rk)` no longer supports the observer's current reconstruction under the declared conditions. The exclusion does not establish that the history was destroyed, unrealised, or nonexistent.

A correction, retraction, changed model, changed boundary, changed assumptions, or newly admitted cross-branch interaction may enlarge or otherwise alter the compatible-history family. Monotonic narrowing MUST NOT be claimed when those fixed conditions do not hold.

### 5.14 Atemporality, unboundedness, recurrence, and completion

These properties are distinct:

- **atemporal / timeless (`⊥Θ`)** — temporal ordering is inapplicable under the declared inquiry;
- **unbounded (`∞Θ`)** — the admitted temporal extent has no declared finite upper bound, lower bound, or both;
- **cyclic or recurrent** — a state, configuration phase, or temporal phase recurs under a declared criterion;
- **completed or closed** — a bounded region satisfies a declared completion or closure criterion;
- **indefinite or unknown** — the available account does not establish a bound or completion.

`∞Θ` is a property of extent, not an additional TD order. `⊥Θ` is an applicability status, not the highest temporal order. A cycle may be finite, an unbounded line need not recur, and a completed history need not be timeless.

The word **eternal** MUST be qualified as unbounded duration, recurrence without declared terminal bound, atemporality, or another explicit meaning.

### 5.15 Derived temporal-regime profile

The temporal-regime vocabulary is retained as a derived, non-exclusive profile of `Θ`. It is not the temporal calculus itself.

The kernel distinguishes:

```text
DeclaredTemporalProfile
```

from:

```text
DerivedTransitionMotif
```

A declared profile states how time is being treated. A derived motif states what the admitted temporal and transition structure actually exhibits.

| Regime | Derived condition |
| --- | --- | --- |
| **TR0** | temporal order is declared inapplicable for the inquiry |
| **TR1** | a local directed order, interval, sequence, or history is present |
| **TR2** | two or more histories or clocks have an explicit synchronisation or coordination relation |
| **TR3** | an admitted event or configuration has several alternative successors, or a declared scenario/history family is present |
| **TR4** | exact or criterion-relative recurrence is witnessed |
| **TR5** | clocks, temporal criteria, transition rules, evolution rules, granularity, or temporal frames themselves change |
| **TR6** | a terminal, completed, or closed region is established under an explicit criterion and stop condition |

A temporal label alone does not prove the corresponding structure. Several regimes may apply simultaneously; for example, a branching history family may also contain synchronised and recurrent substructures.

### 5.16 Coupling configuration and temporal geometry

A temporally situated configuration may be written:

```text
Γ[d, θ] / C ; I
```

or, for an indexed history:

```text
Γ : J → Confadm
```

Configuration and temporal projections are distinct and need not commute:

```text
πΓ ∘ πΘ  ≠  πΘ ∘ πΓ
```

For example, projecting each revision into a plain-text view and then summarising the history may differ materially from first selecting the final rich document and then projecting it to plain text.

When a single view is used to infer both configuration and temporal status, define the joint candidate set:

```text
JointPhaseCandidatesQ,QΘ(v)
  = { ([Γ]Q, [θ]QΘ) | (Γ,θ) is admitted and compatible with v }
```

If the joint candidates span several configuration phases or temporal phases material to the intended use, the analysis MUST abstain, obtain another view, return to source or history, or weaken the claim.

---

## 6. Extensional–Projective Calculus

### 6.1 Placement

Declare the entity’s modelling role, temporal order where relevant, derived temporal regimes where established, semantic context, and inquiry.

```text
X : Dn [Θ: TDm; TR: {TRi...}] / C ; I
```

The temporal component MAY be omitted when time is immaterial or declared inapplicable. Legacy `X : Dn @ TRi / C ; I` notation remains readable but treats `TRi` only as a declared or derived regime, not as a substitute for temporal geometry.

This is a modelling placement, not a formal type judgement unless a formal type substrate is explicitly defined.

### 6.2 Bound

Declare the operational model boundary.

```text
∂I X = B
```

The inquiry subscript reminds the user that operational delimitation depends on purpose.

### 6.3 Incide

Declare a typed structural relation.

```text
A ⋈C,r B
```

where `r` identifies the relation kind. Vague words such as “linked”, “connected”, or “belongs” SHOULD be replaced by a declared relation where the relation is load-bearing.

### 6.4 Extend

Move toward a richer construction by adding declared extension.

```text
X ↑ n
```

Expanded form:

```text
Extn(X | boundary, incidence, transformationClass, invariantSpec, context, inquiry)
```

### 6.5 Slice

Select a local, temporal, or contextual view.

```text
SC,I^s(X)
```

Slice selection MUST state what is selected and what remains outside the slice when that omission matters.

A temporal slice is a temporal viewing and SHOULD use `SΘ` or `πΘ` when temporal preservation, loss, or reconstruction matters.

### 6.6 View and project

A **viewing** changes selected or represented structure while preserving the modelled-entity reference:

```text
π : Γ → V
```

An **order projection** is a viewing that renders a lower-order or reduced representation:

```text
πC,I^{n→k}(X) = Y
```

```yaml
ViewingDeclaration:
  viewingId:
  sourceConfigurationRef:
  modelledEntityRef:
  viewpointOrPurpose:
  selectedStructure:
  representationScheme:
  preservedStructure:
  hiddenOrLostStructure:
  admissibleUse:
  nonAdmissibleUse:
  sourceReturnCondition:
```

If `modelledEntityRef` changes, the operation is retargeting rather than viewing.

### 6.7 Preserve and lose

Every consequential projection or transformation MUST state what is preserved and what is lost, hidden, coarsened, or made uncertain.

```text
Preserve(π): P
Lose(π): L
Risk(π): R
Return(π): source-return condition
```

Loss in a projection stack cannot be silently regained.

### 6.8 Transform

Apply a declared rule, law, method, protocol, operator, or transition schema.

```text
τT(X) = Y
```

At reference level, every transformation arrow MUST carry a typed change kind as defined in Section 7.

### 6.9 Transformation invariant

```text
InvT(X) = K
```

No transformation invariant claim is complete without the transformation class `T`.

A transformation invariant is not automatically phase-defining. A phase criterion MUST separately declare whether and how it contributes to operational equivalence.

### 6.10 Reconstruct

Attempt source recovery from a view or trace.

```text
ρC,I(Y | π, K, Inv) ⇒ {X1, X2, ...}
```

Reconstruction is set-valued by default. A unique source may be claimed only when rival candidates have been bounded and eliminated by declared constraints, proof, or evidence.

### 6.11 Bridge or stop

```text
βM^{A↔B}
Stop(reason)
```

Bridge mode MUST be declared before claim strength is raised across domains, contexts, or substrates.

### 6.12 Eleven primitive practical moves

| Move | Question answered |
| --- | --- |
| Place | What kind of thing is this for the current use? |
| Bound | What makes this the current object rather than an unbounded blur? |
| Incide | Which typed relations matter? |
| Extend | What richer construction is being formed? |
| Temporally situate | Is this an event, interval, history, history family, temporal rule space, or atemporal object, and what temporal projection is in use? |
| Slice | Which local view is selected? |
| Project | What reduced or lower-order view is produced? |
| Preserve/Lose | What survives and what disappears? |
| Transform | What typed rule or change is applied? |
| Reconstruct | Which sources remain compatible with the view? |
| Bridge/Stop | May the claim cross frames, or must it stop? |

### 6.13 Minimal extensional–projective derivation

```text
E7-EP Derivation:
  1. Entity
  2. Semantic context and inquiry
  3. Placement and boundary
  4. Temporal geometry where temporally material
  5. Extension or construction account
  6. Viewing or projection account
  7. Typed transformation and transformation class
  8. Preserved structure
  9. Lost, hidden, or uncertain structure
  10. Configuration and temporal reconstruction status
  11. Bridge mode
  12. Next admissible move or stop
```

---

## 7. Typed Change Discipline

Every arrow is typed. Arrow shape alone creates no claim about world change, method, work, evidence, or causality.

### 7.1 Core change kinds

| Change kind | What changes |
| --- | --- |
| `worldTransformation` | the modelled entity or its state |
| `configurationRevision` | the configuration description |
| `viewing` | selected or represented structure while preserving the entity reference |
| `temporalViewing` | a temporal slice, branch selection, sampling, aggregation, or other temporal projection |
| `retargeting` | the modelled-entity reference |
| `reframing` | semantic context, inquiry, criterion, or criterion edition |
| `temporalReframing` | temporal order, clock, granularity, temporal criterion, temporal boundary, or frame |
| `classification` | the assigned phase reference or classification report |
| `temporalClassification` | the assigned temporal-phase reference or temporal-regime report |
| `observationUpdate` | evidence-bearing assertions in the configuration description |
| `composition` | a larger configuration formed through declared interfaces |
| `decomposition` | a selected subconfiguration or interface view |
| `workOccurrence` | a dated performed action is recorded |
| `dynamicsModelUpdate` | a reusable state-change model is revised or recalibrated |

### 7.2 Change record

```yaml
ChangeRecord:
  changeId:
  changeKind:
  sourceModelledEntityRef:
  targetModelledEntityRef:
  sourceConfigurationRef:
  targetConfigurationRef:
  operatorRef:
  methodRef:
  actingSystemRef:
  workOccurrenceRef:
  semanticContextRef:
  inquiryProfileRef:
  admissibilityPredicateRef:
  relationEffects:
  invariantEffects:
  evidenceRefs:
  resultStatus: achieved | partiallyAchieved | notAchieved | blocked | undetermined | notApplicable
  representativeDependence: absent | present | suspected | unknown | notApplicable
  validityWindow:
```

An operator, method, acting system, and work occurrence are distinct references.

`resultStatus` reports whether a declared postcondition was achieved. It does not by itself establish truth, safety, authorisation, acceptance, or successful work.

### 7.3 Transition schema

```yaml
TransitionSchema:
  transitionKindId:
  changeKind:
  sourceConfigurationPredicateRef:
  targetConfigurationPredicateRef:
  preconditions:
  postconditions:
  protectedInvariantRefs:
  permittedRelationEffects:
  forbiddenRelationEffects:
  resourceOrRiskConditions:
  evidenceRequirements:
  methodRequirements:
  workRequirements:
  applicabilityWindow:
```

A relation edit, boundary edit, graph rewrite, code patch, or textual revision is only a candidate implementation until admitted by the transition schema or stronger domain rule.

---

## 8. Operational Phase Calculus

### 8.1 Phase criterion

A `PhaseCriterion` defines operational sameness for one admitted configuration family.

```yaml
PhaseCriterion:
  phaseCriterionRef:
  phaseCriterionEdition:
  semanticContextRef:
  inquiryProfileRef:
  admittedConfigurationPredicateRef:
  classificationAspect: structural | epistemic | operationalReadiness | combined
  combinedProfileRef:

  equivalenceDefinition:
    mode: signature | directRelation | canonicalisation | behavioural
    phaseSignatureFunctionRef:
    equivalenceRelationRef:
    canonicalisationRuleRef:
    behaviouralEquivalenceRef:

  requiredInvariantRefs:
  exclusionConditions:
  evidencePolicyRef:
  witnessFormRef:
  validityWindow:
  revisionTrigger:
```

Structural, epistemic, and operational-readiness distinctions MAY be combined only through an explicit combined profile.

### 8.2 Signature construction

A common practical construction uses:

```text
σQ : Confadm(E,C,I) → SigQ
```

and defines:

```text
Γ ≈Q Γ′  iff  σQ(Γ) = σQ(Γ′)
```

A signature may include:

- invariant truth values;
- observational outcomes;
- interface behaviour;
- test-suite behaviour under a pinned input domain;
- canonicalised relation structures;
- rule satisfaction;
- permitted-action sets;
- domain-specific functional behaviour.

Signature equality is a practical construction, not the only admissible one. Direct equivalence, canonicalisation, bisimulation-like relations, or other formal relations MAY be used when explicitly defined.

### 8.3 Equivalence validity

A relation called phase equivalence is reflexive, symmetric, and transitive over the admitted configuration family.

If these properties are absent, use a more accurate term:

| Property | Preferred term |
| --- | --- |
| reflexive and symmetric but not transitive | similarity or proximity |
| reflexive and transitive but not symmetric | preorder or refinement |
| directional behaviour preservation | simulation |
| matched behaviour in both directions | bisimulation or behavioural equivalence, when justified |
| threshold distance without stable partition | neighbourhood or approximate similarity |

A raw tolerance threshold is generally not transitive and does not create phases by itself.

### 8.4 Operational phase and reference

For admitted `Γ`:

```text
φ = [Γ]Q = {Γ′ ∈ Confadm(E,C,I) | Γ′ ≈Q Γ}
```

```yaml
PhaseRef:
  modelledEntityRef:
  semanticContextRef:
  inquiryProfileRef:
  phaseCriterionRef:
  phaseCriterionEdition:

  classIdentification:
    mode: signatureValue | canonicalRepresentative | classIdentifier | membershipWitness
    signatureValue:
    canonicalRepresentativeRef:
    classIdentifier:
    representativeConfigurationRef:
    membershipWitnessRef:

  representativeConfigurationRefs:
  validityWindow:
```

A phase label without semantic context, inquiry, criterion, and criterion edition is incomplete.

### 8.5 Equivalence witness

```yaml
EquivalenceWitness:
  witnessId:
  phaseCriterionRef:
  phaseCriterionEdition:
  leftConfigurationRef:
  rightConfigurationRef:
  admittedConfigurationChecks:
  equivalenceChecks:
  requiredInvariantChecks:
  toleratedDifferences:
  evidenceRefs:
  result: equivalent | notEquivalent | undetermined
  supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
  supportStatus: established | supported | suspected | disputed | unknown
  validityWindow:
  reopenCondition:
```

`undetermined` reports that the analysis or evidence does not establish whether equivalence holds. It is not a third mathematical equivalence value.

### 8.6 Admitted configuration transitions

At configuration level:

```text
Γ —λ→ Γ′
```

means that a transition schema of kind `λ` admits the move under the current semantic context and inquiry.

### 8.7 Lifting operations to phase level

For deterministic configuration operation `τ`, the intended phase-level operation is:

```text
τ̄([Γ]Q) = [τ(Γ)]Q
```

This is well-defined only when:

```text
Γ ≈Q Γ′  ⇒  τ(Γ) ≈Q τ(Γ′)
```

whenever `τ` is admitted for both representatives.

If compatibility is not established, the operation remains configuration-level and MUST report:

```text
representativeDependence: present | suspected | unknown
```

### 8.8 Representative outcomes

```yaml
RepresentativeOutcome:
  representativeRef:
  resultConfigurationRef:
  resultPhaseRef:
  resultPhaseRelationToInput: samePhase | differentPhase | undetermined
  boundaryStatus: notCrossed | crossed | undetermined
```

The collection of representative outcomes supports, but does not replace, the separate relation among result branches.

### 8.9 Adjacency and neighbourhood

```text
WeakAdjλ(φ, ψ)
```

holds when at least one representative of `φ` has an admitted `λ` transition to a representative of `ψ`.

```text
StableAdjλ(φ, ψ)
```

holds when the transition is phase-compatible and defines a stable phase-level edge.

Weak adjacency supports exploration. Stable adjacency supports phase-level action guidance.

No generic edit-distance adjacency, nearest phase, or shortest path is assumed.

### 8.10 Phase boundaries

Under signature mode:

```text
BoundaryCrossQ(Γ —λ→ Γ′)  iff  σQ(Γ) ≠ σQ(Γ′)
```

A boundary report states:

- source and target classifications;
- the changed phase-defining component;
- responsible relation or invariant effects;
- change kind and transition schema;
- support basis, support status, and evidence;
- admitted or blocked next use.

The same change may cross a boundary under one inquiry and remain inside one phase under another.

### 8.11 Paths and operation order

A path is a composable sequence of admitted transitions:

```text
p = λn ∘ … ∘ λ2 ∘ λ1
```

Path comparison levels:

```text
p ≡config q      same target configuration
p ≡phase,Q q     target configurations in the same operational phase
p ≡audit,Q q     same phase plus equivalent protected effects and evidence obligations
```

A square may:

- commute strictly;
- commute up to phase;
- commute up to audit equivalence;
- fail to commute;
- remain undetermined.

```yaml
CommuteCheck:
  pathA:
  pathB:
  comparisonLevel: configuration | phase | audit
  phaseCriterionRef:
  phaseCriterionEdition:
  endpointResult: sameConfiguration | samePhase | auditEquivalent | different | undetermined | notApplicable
  intermediateInvariantDifferences:
  relationEffectDifferences:
  evidenceDifferences:
  nextMove:
```

### 8.12 Relation and invariant effects

```yaml
RelationEffect:
  relationRef:
  beforeStatus:
  afterStatus:
  structuralEffect: preserved | weakened | broken | created | notApplicable
  supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
  supportStatus: established | supported | suspected | disputed | unknown
  evidenceRefs:
  phaseDefining: true | false
```

```yaml
InvariantEffect:
  invariantRef:
  beforeValue:
  afterValue:
  structuralEffect: preserved | violated | restored | notApplicable
  supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
  supportStatus: established | supported | suspected | disputed | unknown
  evidenceRefs:
  phaseBoundaryEffect: notApplicable | notCrossed | crossed | undetermined
```

Effects do not silently cancel. An improvement in one characteristic does not compensate for a protected violation unless a separate decision model explicitly permits the trade-off and still exposes the violation.

### 8.13 Minimal local geometry

| Geometric notion | Kernel meaning |
| --- | --- |
| point-like item | one operational phase class under a pinned criterion |
| neighbourhood | phases connected by admitted transitions |
| directed edge | weak or stable typed adjacency |
| boundary | change in phase classification or exit from the admitted family |
| reachability | existence of an admitted path under a named transition family |
| overlap | shared configuration substructure or interface, not overlap of classes in one partition |
| gluing | composition along compatible interfaces |
| obstruction | declared reason a transition, lift, composition, or reconstruction cannot be formed |

The following are OPTIONAL and never inferred from the word geometry:

- preorder or partial order;
- topology;
- metric or pseudometric;
- path cost;
- probability or measure;
- relative-support or evidential-weight structures;
- resource valuation;
- risk model;
- information-loss functional;
- optimisation objective;
- manifold or coordinate structure;
- category-theoretic or higher compositional structure.

Any optional overlay MUST state its carrier, operations, laws, preserved structure, lost structure, applicability, and stop condition.

### 8.13.1 Topological overlay — informative pilot

This subsection and §§8.13.2–8.13.6 are **informative pilot material** in v0.11-UC4.

When continuity, connectedness, separation, neighbourhood structure, topological path structure, quotient structure, or deformation is material to an inquiry, an E7G-T analysis MAY equip a declared carrier `X` with a topology `τ`:

```text
(X, τ)
```

where `τ` is a family of subsets of `X` containing `∅` and `X`, closed under arbitrary unions and finite intersections.

The carrier MAY be, when justified:

- an admitted configuration carrier;
- a temporal carrier or history family;
- an operational-phase quotient;
- another explicitly declared E7G-T carrier.

Invocation is not justified merely because every set can be given a topology. The selected topology MUST have an inquiry-relevant construction, interpretation, or formal purpose. Operational transition structure does not automatically induce a topology, and the word *geometry* does not supply one.

### 8.13.2 Separation laws

The following distinctions SHALL be preserved whenever the pilot is invoked:

```text
operational adjacency       ≠ topological neighbourhood
operational phase boundary  ≠ topological boundary
phase equivalence           ≠ homeomorphism
E7G-T projection            ≠ continuous map
E7G-T gluing                ≠ topological gluing
topology                    ≠ metric
topology                    ≠ order
topology                    ≠ orientation
topology                    ≠ causation
```

A relation between these notions MAY be established only by an explicit construction or bridge.

In particular:

- an operational neighbourhood in §8.13 is graph-like reachability by admitted transitions; it is not a topological neighbourhood unless separately shown to be one;
- an operational phase boundary records a change of phase classification or exit from an admitted family; it is not the topological boundary of a subset unless a topology and the relevant subset have been declared;
- phase equivalence identifies configurations under an inquiry-relative criterion; it does not imply that representatives are homeomorphic;
- a viewing or projection is not called continuous merely because it is structurally well behaved in the E7G-T sense.

### 8.13.3 Topology declaration

A pilot analysis SHOULD expose at least:

```yaml
TopologyDeclaration:
  invoked: true
  carrierRef:
  carrierKind: configuration | phaseQuotient | temporal | history | other
  topologyRef:
  topologyConstruction:
  openSetOrBasisSemantics:
  justificationRef:
  continuityClaims: []
  connectednessClaims: []
  separationClaims: []
  pathClaims: []
  quotientClaims: []
  homeomorphismClaims: []
  deformationClaims: []
  preservedStructure: []
  hiddenOrUnrepresentedStructure: []
  applicability:
  nonAdmissibleUse:
  stopCondition:
```

A basis, subbasis, metric-induced topology, order-induced topology, quotient construction, product construction, or other standard construction MAY be used, but its source and conditions MUST be stated. Calling a topology `metric-induced` or `order-induced` does not make metric or order part of the E7G-T core.

### 8.13.4 Maps, invariants, and phase quotients

For declared topological spaces `(X,τX)` and `(Y,τY)`, a map `f : X → Y` SHALL be called **continuous** only when the corresponding topological condition is established; equivalently, the inverse image of every `τY`-open set is `τX`-open.

Two carriers SHALL be called **homeomorphic** only when there exists a bijection between them that is continuous with continuous inverse. A property SHALL be called a **topological invariant** only where invariance under the relevant homeomorphisms is established or supplied by the formal substrate.

Connectedness, path-connectedness, separation properties, compactness, and deformation claims MUST NOT be inferred from visual similarity, operational adjacency, or informal geometric language.

If an admitted carrier `X` has a declared topology `τ` and a pinned phase equivalence `≈Q`, the operational-phase quotient

```text
qQ : X → X/≈Q
```

MAY be equipped with the quotient topology

```text
τQ = { U ⊆ X/≈Q | qQ⁻¹(U) ∈ τ }.
```

Under that construction, `qQ` is a continuous quotient map by definition. This does **not** imply that the phase criterion is topological, that the quotient topology is operationally useful, or that topological sameness and operational sameness coincide. Those are separate claims.

Topological gluing MAY be asserted only when the required topological carriers, identifications or interface maps, and resulting topology are supplied. The interface composition of §8.14 alone is insufficient.

### 8.13.5 Temporal carriers and orientation

A temporal carrier MAY receive a declared topology when topological structure is material. Such a declaration does not supply a temporal order, orientation, clock, or causal relation.

Therefore:

```text
temporal-carrier topology
        ≠ temporal order
        ≠ temporal orientation
        ≠ causal direction
```

For example, with its standard topology the interval `[0,1]` admits the homeomorphism

```text
r(t) = 1 - t.
```

The map reverses the usual coordinate orientation while preserving the underlying topology. This demonstrates only that topology and orientation are different structures. It does not establish physical time-reversal symmetry, reversed causation, retrocausation, or the physical reversibility of any process.

If an order topology, causal topology, Alexandrov topology, or other structure derived from directional relations is used, the derivation and its assumptions MUST be declared. Directionality SHALL NOT be smuggled into the topological carrier and then reported as if topology alone produced it.

### 8.13.6 Applicability and stop condition

Invoke the pilot only if topological structure changes at least one material result, such as:

- whether an admitted region is connected or path-connected;
- whether a transformation is continuous;
- whether a qualitative property is invariant under an established homeomorphism;
- whether phase quotienting merges or separates relevant regions;
- whether every admissible topological path satisfying declared conditions must meet a specified region;
- whether a temporal orientation change preserves the underlying topology while changing other declared structure.

Stop or route to the relevant mathematical or domain method when:

- no inquiry-relevant topology can be justified;
- the claim requires metric, measure, differential, probabilistic, causal, or domain-specific structure not supplied by the topology;
- a topological term is being used only as a metaphor;
- the overlay adds notation without changing a reconstruction, classification, comparison, next move, reliance limit, or stop decision.

Ordinary E7G-T conformance does not require this pilot unless it is explicitly invoked.

### 8.14 Interface composition and gluing

Let `ΓA` and `ΓB` expose compatible interfaces over `J`.

```text
ΓA ⊕J ΓB
```

is defined only when a declared compatibility predicate holds.

```yaml
GluingDeclaration:
  leftConfigurationRef:
  rightConfigurationRef:
  interfaceRef:
  interfaceMapping:
  compatibilityPredicateRef:
  sharedConstraintPolicy:
  overlapOrDeduplicationPolicy:
  resultingBoundary:
  preservedRelations:
  createdRelations:
  lostOrHiddenRelations:
```

Phase-level gluing requires composition to respect the phase equivalences of both operands. Otherwise composition remains representative-dependent at configuration level.

### 8.15 Reframing and reclassification

A reframing changes one or more of:

```text
C → C′
I → I′
Q → Q′
phaseCriterionEdition → new edition
```

A fixed configuration may then receive a different classification without any world transformation.

```yaml
ReframingRecord:
  configurationRef:
  sourceSemanticContextRef:
  targetSemanticContextRef:
  sourceInquiryRef:
  targetInquiryRef:
  sourcePhaseCriterionRef:
  targetPhaseCriterionRef:
  reason:
  preservedMeanings:
  changedMeanings:
  changedAdmissibleUse:
  bridgeRefs:
```

---

## 9. Combined Configuration-and-Temporal Projection-to-Phase Calculus

This section is the principal unification layer.

### 9.1 Phase-view compatibility

A viewing descends to a phase-level map only when:

```text
Γ ≈Q Γ′  ⇒  π(Γ) ≈V π(Γ′)
```

for a declared view-equivalence relation `≈V`.

If this condition is not established, the view remains configuration-level or representative-dependent.

### 9.2 Reconstruction fibre

Given a view `v`:

```text
Recπ(v) = {Γ ∈ Confadm | π(Γ) ≈V v}
```

A reconstruction report SHOULD state:

- the view and viewing declaration;
- admitted source family;
- candidate set or generating rule;
- assumptions and exclusions;
- ambiguity or non-identifiability;
- evidence and currentness;
- uniqueness status;
- source-return condition.

### 9.3 Phase-candidate set of a view

For phase criterion `Q`, define:

```text
PhaseCandidatesQ(v) = { [Γ]Q | Γ ∈ Recπ(v) }
```

This set records which operational phases remain compatible with the visible view.

### 9.4 Determinate phase inference

A view supports a unique phase classification only when:

```text
|PhaseCandidatesQ(v)| = 1
```

and the evidence, validity window, bridge mode, and reliance requirements for the intended use are satisfied.

A single phase candidate does not by itself prove that the reconstructed source is unique.

### 9.5 Phase-spread ambiguity

If:

```text
|PhaseCandidatesQ(v)| > 1
```

then the view spans several operational phases and does not support determinate phase classification.

Required next moves include one or more of:

```text
abstain
inspect source
obtain another view
increase resolution
strengthen evidence
narrow the admitted source family
revise the inquiry or criterion
```

The system MUST NOT select one phase merely because it is fluent, probable, convenient, or visually dominant.

### 9.6 Empty candidate set

If:

```text
PhaseCandidatesQ(v) = ∅
```

then the view is incompatible with the admitted source family, current modelling assumptions, or criterion.

Required next moves include:

```text
repair the model
revise the boundary
reopen source acquisition
revise the criterion
mark the view invalid
stop
```

### 9.7 Phase-information loss

A projection may preserve enough information for one inquiry but lose information required for another.

Define a qualitative phase-information posture:

```text
PhaseInfoπ,Q(v):
  phaseDeterminate
  phaseNarrowing
  phaseSpanning
  phaseIncompatible
  undetermined
```

These are operational report statuses, not probabilities or information-theoretic quantities unless a formal substrate is separately declared.

### 9.8 Combined source-return rule

Source return is required when:

- the reconstruction fibre spans several phases relevant to the intended action;
- the view hides a phase-defining relation or invariant;
- phase-view compatibility is not established;
- the criterion requires evidence unavailable in the view;
- the source validity window is stale or disputed;
- representative dependence may change the result.

### 9.9 Combined derivation

```text
E7-Combined Derivation:
  1. Entity, semantic context, inquiry, and boundary
  2. Admitted configuration family
  3. Temporal carrier and temporal boundary where relevant
  4. Source configuration, temporal source, or available view
  5. Configuration and temporal viewing/projection declarations
  6. Structurally and temporally preserved and lost information
  7. Configuration and temporal reconstruction fibres
  8. Configuration and temporal phase criteria and editions
  9. PhaseCandidatesQ(view), TemporalPhaseCandidatesQΘ(view), or joint candidates
  10. Configuration-phase and temporal-phase view compatibility
  11. Typed change or path, if any
  12. Boundary and representative-dependence status
  13. Support basis and support status
  14. Admissible use
  15. Source/history return, next move, or stop
```

### 9.10 Combined use law

> No operational phase may be inferred from a view more strongly than the view’s preserved structure, reconstruction fibre, phase compatibility, and weakest support point allow.

### 9.11 Temporal-view compatibility

A temporal viewing descends to a temporal-phase map only when:

```text
θ ≈QΘ θ′  ⇒  πΘ(θ) ≈VΘ πΘ(θ′)
```

If this is not established, the temporal view remains representative-dependent and MUST NOT be treated as a temporal-phase invariant.

### 9.12 Temporal phase-spread

For:

```text
TemporalPhaseCandidatesQΘ(vΘ)
  = { [θ]QΘ | θ ∈ RecΘ,π(vΘ) }
```

the same determinate, narrowing, spanning, incompatible, and undetermined postures apply as for configuration phase. A final state may determine the current configuration phase while leaving the temporal phase indeterminate because compliant, non-compliant, audited, unaudited, timely, and late histories can end in the same visible state.

### 9.13 Joint configuration–temporal inference

Let a view `v` be compatible with admitted configuration–temporal pairs `(Γ,θ)`. Define:

```text
JointRec(v)
  = { (Γ,θ) | (Γ,θ) is admitted and compatible with v }

JointPhaseCandidatesQ,QΘ(v)
  = { ([Γ]Q,[θ]QΘ) | (Γ,θ) ∈ JointRec(v) }
```

Joint classification is determinate only when all candidate pairs agree on every configuration and temporal phase component material to the intended use.

### 9.14 Non-commuting structural and temporal projections

When both configuration and temporal reduction occur, the analysis SHOULD test:

```text
πΓ(πΘ(Γ,θ))  ?=  πΘ(πΓ(Γ,θ))
```

Possible results are:

```text
commutesStrictly
commutesUpToConfigurationPhase
commutesUpToTemporalPhase
commutesUpToJointPhase
failsToCommute
undetermined
notApplicable
```

Failure to commute is material when the order of summarising, sampling, selecting a branch, translating, redacting, aggregating, or otherwise projecting changes the supported classification or next move.

### 9.15 Relative-support overlay — informative pilot

> **Informative pending pilot validation.** This section adds an optional inquiry-relative support structure over alternatives that remain admissible after ordinary E7G-T reconstruction, temporal reconstruction, or phase-candidate analysis. It does not make support a constitutional requirement of E7G-T and does not require probability theory.

#### 9.15.1 Purpose

Ordinary E7G-T distinguishes compatible from incompatible sources and determinate from phase-spanning views. In some inquiries, however, several candidates remain admissible but are not equally supported by the currently available evidence. The relative-support overlay records that difference without collapsing possibility into probability or support into truth.

Let `A` be a declared carrier of admitted alternatives, such as:

```text
A ⊆ Recπ(v)
A ⊆ RecΘ,π(vΘ)
A ⊆ PhaseCandidatesQ(v)
A ⊆ TemporalPhaseCandidatesQΘ(vΘ)
A ⊆ JointPhaseCandidatesQ,QΘ(v)
```

A support structure is declared as:

```text
Σ = ⟨A, S, ≽S, u, P, R, V⟩
```

where:

- `A` — admitted alternatives;
- `S` — support-value domain, if any;
- `≽S` — relative-support relation;
- `u` — OPTIONAL support-value assignment;
- `P` — provenance and evidence basis;
- `R` — update or revision rule;
- `V` — validity, calibration, and stop conditions.

The overlay MAY be purely ordinal:

```text
Γ1 ≻S Γ2 ≻S Γ3
```

or numerical:

```text
u(Γ1)=s1, u(Γ2)=s2, u(Γ3)=s3
```

Numerical values SHALL NOT be called probabilities unless a probability space and its conditions are separately declared.

#### 9.15.2 Separation laws

Whenever this overlay is invoked, the following distinctions SHALL be preserved:

```text
admissible            ≠ well-supported
well-supported        ≠ true
weakly supported      ≠ false
weakly supported      ≠ excluded
unsupported           ≠ impossible
probability           ≠ generic support
confidence            ≠ probability unless defined so
model fit             ≠ empirical truth
relative ranking      ≠ calibrated magnitude
```

An alternative leaves the admitted family only through the ordinary E7G-T admissibility, reconstruction, criterion, or evidence rules. A support score by itself SHALL NOT delete it.

#### 9.15.3 Support declaration

A pilot-conforming declaration SHOULD expose:

```yaml
RelativeSupportDeclaration:
  invoked: true
  carrierRef:
  carrierKind: reconstructionCandidates | historyCandidates | phaseCandidates | jointCandidates | other
  supportSemantics: ordinal | score | probability | likelihoodLike | confidenceLike | domainSpecific
  supportDomainRef:
  relationOrScoringRuleRef:
  evidenceAndProvenanceRefs: []
  priorOrInitialisationRuleRef:
  updateRuleRef:
  calibrationStatus: notApplicable | uncalibrated | partiallyCalibrated | calibrated | unknown
  normalisationRuleRef:
  independenceAssumptions: []
  knownDependencies: []
  currentSupportAssignments: []
  exclusionRuleRef:
  admissibleUse:
  nonAdmissibleUse:
  validityWindow:
  stopOrReopenCondition:
```

Only fields material to the inquiry need be used.

#### 9.15.4 Update discipline

Let `Σk` be the support structure after evidence state `Ek`. New evidence may revise support:

```text
UpdateR(Σk, Ek+1) = Σk+1
```

The update rule MUST state whether it is:

- purely ordinal;
- score-based;
- frequency-based;
- likelihood-based;
- probabilistic;
- expert-elicited;
- model-derived;
- hybrid.

A conforming update SHALL preserve provenance and indicate whether changes arise from:

```text
new evidence
retracted evidence
changed observation protocol
changed boundary
changed semantic context
changed inquiry
changed model
changed update rule
changed calibration
```

A changed support ranking caused by reframing SHALL NOT be misreported as if the world itself changed.

#### 9.15.5 Relation to narrowing and exclusion

Relative support and candidate narrowing are independent operations. New evidence may:

```text
change support while leaving A unchanged;
remove candidates while preserving the ranking of survivors;
add previously inadmissible candidates after a model or boundary revision;
change both admissibility and support.
```

For observer-relative history relevance, a history may remain in `HO(rk)` while becoming weakly supported relative to others. Conversely, a highly supported history may later be removed from `HO(rk+1)` if new valid evidence makes it incompatible.

The overlay therefore distinguishes:

```text
possible
→ differentially supported
→ excluded
```

without treating these as one scalar continuum.

#### 9.15.6 Probabilistic formalisation as one implementation

A probabilistic implementation MAY be used when a valid probability model is declared. In that case a support assignment may take the form:

```text
P(a | e)
```

for alternatives `a ∈ A` and evidence `e`. If Bayesian updating is used, the implementation SHALL declare at least:

- the hypothesis or state carrier;
- prior distribution or initial measure;
- likelihood or observation model;
- conditioning or update rule;
- normalisation conditions;
- independence or conditional-independence assumptions;
- calibration or validation posture;
- handling of zero-probability and model-misspecification cases.

The public E7G-T concept remains **relative support**. Bayesian inference is one formal neighbourhood or implementation substrate and SHALL NOT be implied when only ordinal or generic support is declared.

#### 9.15.7 Support and phase inference

Relative support MAY rank phase candidates but SHALL NOT repair phase-spread by assertion. If:

```text
|PhaseCandidatesQ(v)| > 1
```

then the view remains phase-spanning even if one candidate has much higher support than the others. The result MAY be reported as:

```text
phaseSpanning; bestSupportedCandidate = φ1
```

but SHALL NOT be silently upgraded to:

```text
phaseDeterminate
```

unless the ordinary E7G-T conditions for determinate classification are satisfied.

The same rule applies to temporal and joint phase candidates.

#### 9.15.8 Decision-use boundary

A decision rule MAY use relative support, but the decision criterion is a separate object. For example:

```text
ChooseAction(a) = f(Σ, costs, risks, constraints, obligations)
```

Support alone does not determine what should be done. Loss functions, legal duties, safety margins, thresholds, or domain-specific obligations require their own declared substrate.

#### 9.15.9 Candidate laws

> **Informative pending pilot validation.**

**Candidate Law S1 — Admissibility and support remain distinct.** An admitted alternative may be weakly supported; a strongly supported alternative may remain only one among several admissible candidates.

**Candidate Law S2 — Support is inquiry-relative.** Relative support is meaningful only under a declared carrier, evidence basis, semantic context, inquiry, validity window, and support semantics.

**Candidate Law S3 — Stronger support is not truth.** A support ranking or score does not by itself establish truth, proof, causation, ontology, or operational safety.

**Candidate Law S4 — Weaker support is not exclusion.** An alternative remains admissible until the applicable exclusion rule removes it.

**Candidate Law S5 — Numerical support requires semantics.** Numbers SHALL NOT be treated as probabilities, calibrated confidence, or comparable magnitudes unless the corresponding mathematical or empirical conditions are declared.

**Candidate Law S6 — Updates require provenance.** Every material support update SHOULD expose what evidence, rule, frame, or calibration change produced it.

**Candidate Law S7 — Support cannot cure projection ambiguity.** A phase-spanning or temporally phase-spanning view remains structurally ambiguous even when one candidate is best supported.

#### 9.15.10 Promotion gate

Promote this module into the normative constitutional core only if pilots show that relative-support accounting:

- catches recurring decision errors not already resolved by admissibility and source-return rules alone;
- remains substrate-neutral across probabilistic and non-probabilistic domains;
- improves handling of evolving evidence without encouraging false precision;
- keeps weakly supported alternatives visible until valid exclusion;
- survives use in at least four materially different domains;
- improves the next responsible move, stop decision, or evidence-acquisition choice;
- survives independent review and counterexample testing.

Until then, ordinary E7G-T conformance does not require this overlay unless explicitly invoked.

---

## 10. Bridge Modes and Claim Strength

### 10.1 Bridge modes

| Mode | Use |
| --- | --- |
| **none** | no cross-frame bridge is claimed |
| **contemplative-what-if** | imaginative, reflective, fictional, or exploratory use |
| **philosophical-interpretation** | conceptual interpretation without formal or empirical force |
| **formal-analogy** | declared structural resemblance without identity or empirical support |
| **formal-compatibility** | mapping into or comparison with a recognised formal substrate under definitions |
| **empirical-testable** | standard substrate, observation protocol, measurement map, prediction or constraint, falsification condition, and evidence path are supplied |

Bridge mode MUST be declared before claim strength is raised.

### 10.2 Cross-context and cross-inquiry bridges

Phase references from different semantic contexts, inquiries, criteria, or editions are not directly equal.

```yaml
FrameBridge:
  bridgeId:
  sourcePhaseRef:
  targetPhaseRef:
  sourceSemanticContextRef:
  targetSemanticContextRef:
  sourceInquiryRef:
  targetInquiryRef:
  sourcePhaseCriterionRef:
  targetPhaseCriterionRef:
  mappingMode:
  direction:
  preservedStructure:
  lostStructure:
  fitOrCongruenceStatement:
  counterexampleOrInvariantEvidence:
  admittedUse:
  nonAdmittedUse:
  evidenceRefs:
  validityWindow:
  revisionTrigger:
```

A bridge transfers only what it explicitly admits. Shared labels create no substitution right.

### 10.3 Claim-strength ladder

1. intuition;
2. metaphor;
3. contemplative-what-if;
4. philosophical interpretation;
5. formal analogy;
6. formal compatibility;
7. formal proof;
8. empirical-testable proposal;
9. empirically supported model;
10. validated operational method.

Do not upgrade claim strength without completing the required bridge, proof, test, or validation.

### 10.4 Weakest-link rule

A bridge, path, or combined analysis cannot support a stronger claim than its least-supported load-bearing component.

### 10.5 Empirical-language rule

Reality-facing empirical claims require:

- a standard substrate;
- an observation protocol;
- a measurement map;
- a prediction or constraint;
- a falsification or failure condition;
- an evidence path;
- a declared validity window.

E7G-T may organise these declarations but does not replace the relevant science or engineering.

---

## 11. Practical Output Profiles

The unified kernel uses modular profiles. A user should not be forced to complete every possible field.

### 11.1 Profile U1 — E7-Line

Use for immediate orientation, caution, or local repair.

```text
E7-Line:
For <purpose>, <entity or view> is treated as <role or configuration> under <context and inquiry>.
Temporal posture: <TD role, temporal projection, atemporal, or not material>.
Protected condition: <condition or not applicable>.
Assessment: <projection / same phase / different phase / same temporal phase / different temporal phase / joint phase spread / undetermined / not applicable>.
Support: <basis and status where material>.
Next move: <action>.
Blocked overread: <one phrase>.
```

Minimum fields:

1. purpose;
2. entity or view;
3. semantic context or recoverable local frame;
4. protected condition where phase use is present;
5. assessment;
6. next move;
7. blocked overread.

### 11.2 Profile U2 — E7-Check

Use for routine QA, software inspection, document workflows, dashboard review, translation review, and AI-output review.

```yaml
E7Check:
  modelledEntity:
  semanticContext:
  inquiry:
  operationalBoundary:
  routesUsed:
    - extensionalProjective
    - temporalGeometry
    - operationalPhase

  assessmentTarget:
    mode: placement | projectionReview | reconstructionReview | currentClassification | staticComparison | proposedChange | observedChange | projectionInference | pathComparison
    sourceConfigurationRef:
    currentConfigurationRef:
    referencePhaseRef:
    leftConfigurationRef:
    rightConfigurationRef:
    changeRef:
    viewRef:
    pathARef:
    pathBRef:

  protectedConditions: []
  toleratedDifferences: []

  temporalGeometry:
    applicability: active | inapplicable | immaterial | undetermined
    temporalOrderRoles: []
    temporalCarrierRef:
    temporalBoundaryRef:
    orderOrCausalityRef:
    clockOrCoordinateRefs: []
    historyRefs: []
    temporalProjectionRef:
    temporallyPreserved: []
    temporallyHiddenOrLost: []
    temporalReconstructionStatus: notClaimed | unique | setValued | underdetermined | incompatible
    temporalPhaseCriterionRef:
    temporalPhaseCriterionEdition:
    temporalPhaseCandidateRefs: []
    temporalPhaseInformationPosture: notApplicable | phaseDeterminate | phaseNarrowing | phaseSpanning | phaseIncompatible | undetermined
    derivedRegimes: []
    extentStatus: bounded | upperUnbounded | lowerUnbounded | biUnbounded | atemporal | indefinite | unknown

  projection:
    preserved: []
    hiddenOrLost: []
    reconstructionStatus: notClaimed | unique | setValued | underdetermined | incompatible
    phaseInformationPosture: notApplicable | phaseDeterminate | phaseNarrowing | phaseSpanning | phaseIncompatible | undetermined

  effects:
    preserved: []
    weakened: []
    broken: []
    created: []

  classification:
    currentPhaseRef:
    phaseRelation: samePhase | differentPhase | undetermined | notApplicable
    boundaryStatus: notApplicable | notCrossed | crossed | undetermined
    representativeDependence: absent | present | suspected | unknown | notApplicable

  support:
    supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
    supportStatus: established | supported | suspected | disputed | unknown
    evidenceRefs: []
    unresolvedQuestions: []

  bridgeMode: none | contemplative-what-if | philosophical-interpretation | formal-analogy | formal-compatibility | empirical-testable
  nextMove:
  blockedOverread:
  stopOrReopenCondition:
```

### 11.3 Profile U3 — E7-Analysis

Use for consequential decisions, repeated workflows, disputed classifications, publication, legal or high-severity review, engineering or safety analysis, formal implementation, and cross-context bridging.

```yaml
E7Analysis:
  analysisId:
  modelledEntityRef:

  semanticContext:
    semanticContextRef:
    semanticContextEdition:
    localVocabularyRefs:
    localInvariantRefs:

  inquiryProfile:
    inquiryProfileRef:
    purpose:
    operationalBoundary:
    observables:
    requiredInvariants:
    toleratedVariation:
    admissibilityConditions:
    admissibleUse:
    nonAdmissibleUse:
    validityWindow:
    stopCondition:

  configurationDescription:
    configurationRef:
    configurationEdition:
    entitiesOrRegions:
    typedRelations:
    interfaces:
    constraints:
    unknownOrContestedPositions:
    evidenceRefs:

  compatibilityLenses:
    dRoleProfileRef:
    temporalOrderRoleProfileRef:
    derivedTemporalRegimeProfileRef:

  temporalGeometryAccount:
    applicability:
    temporalSubkernelRef:
    temporalCarrierRef:
    temporalBoundaryRef:
    temporalOrderRoles:
    precedenceOrCausalityRef:
    clockOrCoordinateRefs:
    historyRefs:
    temporalExtensionPath:
    temporalViewingRefs:
    temporalProjectionPath:
    temporallyPreserved:
    temporallyHiddenOrLost:
    temporalReconstructionFibreRef:
    temporalSourceReturnCondition:
    temporalPhaseCriterionRef:
    temporalPhaseCriterionEdition:
    temporalPhaseCandidateRefs:
    temporalPhaseInformationPosture:
    derivedTemporalRegimes:
    extentStatus:
    recurrenceWitnessRefs:
    completionCriterionRef:

  extensionalProjectiveAccount:
    placement:
    constructionPath:
    viewingRefs:
    projectionPath:
    preservedStructure:
    hiddenOrLostStructure:
    transformationClassRefs:
    reconstructionFibreRef:
    sourceReturnCondition:

  phaseCriterion:
    phaseCriterionRef:
    phaseCriterionEdition:
    classificationAspect: structural | epistemic | operationalReadiness | combined
    combinedProfileRef:
    equivalenceDefinitionMode:
    phaseSignatureFunctionRef:
    equivalenceRelationRef:
    canonicalisationRuleRef:
    behaviouralEquivalenceRef:
    equivalenceJustification:

  classification:
    currentPhaseRef:
    classIdentification:
      mode: signatureValue | canonicalRepresentative | classIdentifier | membershipWitness
      signatureValue:
      canonicalRepresentativeRef:
      classIdentifier:
      representativeConfigurationRef:
      membershipWitnessRef:
    result: classified | notClassified | undetermined
    supportBasis: stipulation | formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
    supportStatus: established | supported | suspected | disputed | unknown

  combinedViewPhaseAccount:
    viewRef:
    viewPhaseCompatibility:
    phaseCandidateRefs:
    phaseInformationPosture:
    uniquenessStatus:
    sourceReturnRequired: true | false | undetermined

  jointConfigurationTemporalAccount:
    jointReconstructionFibreRef:
    jointPhaseCandidateRefs:
    jointPhaseInformationPosture:
    structuralTemporalCommuteCheckRef:
    historyReturnRequired: true | false | undetermined

  localGeometry:
    stableAdjacentPhases:
    weakOrRepresentativeDependentAdjacencies:
    forbiddenOrBlockedTransitions:
    nearestRelevantBoundaryConditions:

  changeAudit:
    changeKind:
    transitionRef:
    sourceConfigurationRef:
    targetConfigurationRef:
    relationEffects:
    invariantEffects:
    phaseRelation: samePhase | differentPhase | undetermined | notApplicable
    boundaryStatus: notApplicable | notCrossed | crossed | undetermined
    boundaryReason:
    representativeDependence: absent | present | suspected | unknown | notApplicable
    representativeOutcomes: []
    outputPhaseRelation: samePhase | differentPhase | undetermined | notApplicable
    commuteCheckRef:

  bridges:
    bridgeRefs:
    bridgeMode:
    crossContextOrInquiryLoss:

  proofAndSupport:
    proofOfPathRef:
    weakestSupportPoint:
    unresolvedObligations:

  useBoundary:
    admittedOperationalUse:
    blockedOverread:
    nextAdmissibleMove:
    reopenCondition:
```

### 11.4 Candidate supplement — Observation/Interpretation Check

> **Informative.** Append this lightweight block to `E7Check` or `E7Analysis` only when the §3.9 pilot module is invoked.

```yaml
ObservationInterpretationCheck:
  observerRefs: []
  observationRecordRefs: []
  viewingOrMeasurementRefs: []
  observationProtocolRefs: []
  observationalClaim:
  semanticSupport:
  temporalSupport:
  spatialOrPopulationSupport:
  resolution:
  knownLimitations: []
  unknownPositions: []
  interpretation:
  assumptionRefs: []
  inferenceRuleRefs: []
  bridgeRefs: []
  externalModelRefs: []
  sharedField:
    jointlyAdmissible: []
    divergences: []
    unobservedOrIndeterminate: []
  temporalExtensionJustification:
  nextMove:
  blockedOverread:
```

Use only the fields that affect the inquiry. The supplement SHOULD remain shorter than the problem it clarifies.

### 11.5 Profile U4 — Formalisation Card

Use when a machine-checkable or mathematically well-defined construction is needed.

```yaml
FormalisationCard:
  targetPhenomenon:
  candidateMathematicalObject:
  mappingMode:
  carrierSetOrClass:
  admittedConfigurationPredicate:
  equivalenceDefinition:
  transitionStructure:
  temporalCarrier:
  temporalExtensionStructure:
  temporalOrderOrCausalityStructure:
  temporalViewingStructure:
  temporalReconstructionFibreSemantics:
  temporalEquivalenceDefinition:
  temporalTransitionAndRecurrenceStructure:
  clockOrCoordinateStructure:
  compositionStructure:
  viewingStructure:
  reconstructionFibreSemantics:
  preservedStructure:
  lostStructure:
  proofObligations:
  validationBoundary:
  blockedOverread:
  stopCondition:
```

Formalisation is need-driven. It is not a higher-status output merely because it is more symbolic.

### 11.6 Legacy compatibility profiles

The following earlier profiles remain recognised as route-specific views:

- `E7-OneLine` maps to `E7-Line` with extensional–projective emphasis;
- `MiniCard` maps to `E7-Check` with a reduced projection module;
- `FullCard` maps to `E7-Analysis` with the phase module omitted where not applicable;
- `Φ-Line` maps to `E7-Line` with operational-phase emphasis;
- `Φ-Check` maps to `E7-Check` with the projection module omitted where not applicable;
- `PhaseAnalysis` maps to `E7-Analysis` with the extensional–projective module reduced where not applicable.

No migration requires filling irrelevant fields.

---

## 12. Proof-of-Path, Reality Bridge, and Formal Neighbourhood

### 12.1 Proof-of-Path

Proof-of-Path is a structured account of the admissible route by which a claim, model, proof, output, classification, or transition moves through placement, transformations, projections, checks, bridges, and stop conditions to a stated reliance tier.

It is not a replacement for proof.

```yaml
ProofOfPathCard:
  id:
  claim:
  entity:
  substrate:
  assumptions:
  semanticContext:
  inquiry:
  placement:
  boundary:
  definitions:
  transformations:
  temporalCarrier:
  temporalOrderAndClockRefs:
  temporalExtensionEvents:
  temporalProjectionEvents:
  temporalReconstructionEvents:
  temporalPhaseClassificationEvents:
  temporalBoundaryEvents:
  projectionEvents:
  phaseClassificationEvents:
  boundaryEvents:
  preservedInvariants:
  losses:
  checks:
  unresolvedObligations:
  bridgeMode:
  relianceTier:
  stopCondition:
  sourceLinks:
```

A Proof-of-Path can include a formal proof, but it does not become a formal proof merely by documenting a path.

### 12.2 Reality Bridge

Reality-facing language requires Reality Bridge discipline.

```yaml
RealityBridgeCard:
  claim:
  sourceDomain:
  targetDomain:
  bridgeMode:
  standardSubstrate:
  observationProtocol:
  measurementMap:
  predictionOrConstraint:
  falsificationCondition:
  evidencePath:
  relevantPhaseCriterionRef:
  weakestLink:
  admissibleUse:
  nonAdmissibleUse:
  stopCondition:
```

`empirical-testable` is the only bridge mode that can support empirical claims.

### 12.3 Formal neighbourhood

```yaml
FormalNeighbourhoodCard:
  field:
  e7gtElement:
  resemblance:
  establishedTool:
  currentBridgeMode:
  whatE7GTCanLearn:
  whatE7GTMustNotClaim:
  possibleFormalisationPath:
  stopCondition:
```

Neighbourhood is not identity.

### 12.4 Joint attainability and trade-off claims

A trade-off is not established by different labels, one failed implementation, or one selected path.

```yaml
JointAttainabilityAnalysis:
  configurationOrPhaseFamilyRef:
  protectedRequirementRefs:
  constraintSetRef:
  resourceAndScaleWindow:
  feasibleRegionDescription:
  transitionFamilyRef:
  obstructionOrMechanism:
  supportBasis: formalDerivation | observation | empiricalCalibration | operationalValidation | mixed | none
  supportStatus: established | supported | suspected | disputed | unknown
  evidenceRefs:
  alternativeExplanations:
  nextMove:
```

An unavoidable trade-off requires a named mechanism and declared scale. Poor implementation is not a fundamental bound.

---

## 13. Unified Core Laws

### 13.1 Constitutional laws

**Law 1 — Entity and description remain distinct.** A configuration, view, report, equation, diagram, translation, or AI answer is not the modelled entity by form alone.

**Law 2 — Meaning is context-local.** Relations, invariants, and admissibility conditions hold inside a named semantic context or through a declared bridge.

**Law 3 — Inquiry precedes phase.** No phase claim is complete without purpose, operational boundary, protected conditions, tolerated variation, admissible use, and stop condition.

**Law 4 — Typing precedes operation.** Place or otherwise type the entity and arrow before relying on an operation.

**Law 5 — Boundary kinds remain distinct.** Model, admissibility, and phase boundaries MUST NOT be silently collapsed.

### 13.2 Extensional–projective laws

**Law 6 — Extension is not projection.** Building richer structure is not the same as rendering a reduced view.

**Law 7 — Viewing is not world transformation.** Changing what is represented does not automatically change what is modelled.

**Law 8 — Projection is not reconstruction.** A view of a source is not recovery of the source.

**Law 9 — Reconstruction is generally set-valued.** A view yields a fibre of compatible sources unless uniqueness is separately justified.

**Law 10 — Projection loss accumulates.** Lost structure cannot be silently regained later in a projection stack.

**Law 11 — Slice and projection need not commute.** Slicing before projection and projecting before slicing may yield materially different results.

**Law 12 — Invariance requires a transformation class.** No transformation invariant is complete without stating what transformations it survives.

### 13.3 Operational-phase laws

**Law 13 — Phase is derived equivalence.** A phase is an equivalence class under a pinned criterion, not a synonym for state, exact configuration, status, stage, or time slice.

**Law 14 — Approximation is not automatically equivalence.** Similarity and proximity retain their names until a valid equivalence construction is supplied.

**Law 15 — Phase identity is criterion- and edition-relative.** Reframing may reclassify a fixed configuration without changing the entity.

**Law 16 — Phase difference is not transition history.** Static comparison may establish different phases. Boundary crossing requires a typed transition or path.

**Law 17 — Adjacency follows admissibility.** A syntactic edit is not a phase edge until an admitted transition schema supports it.

**Law 18 — Phase-level operations require compatibility.** An operation lifts to phase level only when it respects phase equivalence or representative dependence remains explicit.

**Law 19 — Path equivalence is declared.** Same target configuration, same target phase, and same audit effects are different claims.

**Law 20 — Geometry has no automatic metric.** Distance, topology, cost, probability, order, or optimisation requires a separate overlay.

### 13.4 Combined laws

**Law 21 — Phase views require compatibility.** A view is phase-level only when it respects the pinned phase equivalence.

**Law 22 — View-based phase inference is fibre-bounded.** A view cannot support a stronger phase classification than its reconstruction fibre permits.

**Law 23 — Phase-spanning views require abstention or source return.** When compatible sources occupy several operational phases, the view does not determine the phase.

**Law 24 — Cross-frame sameness requires a bridge.** Phase references from different contexts, inquiries, criteria, domains, or editions are not directly equal.

**Law 25 — Bridge claims inherit the weakest link.** A bridge cannot support a stronger claim than its least-supported load-bearing component.

### 13.5 Support and use laws

**Law 26 — Structural and support status remain separate.** A relation may be broken but weakly evidenced, or preserved but disputed.

**Law 27 — Effects are relation- and invariant-specific.** Preserved, weakened, broken, created, violated, and restored effects do not net out into an undeclared scalar.

**Law 28 — Report form creates no authority.** A card, diagram, validator result, or formal notation is not by form alone an authorisation, acceptance decision, completed check, performed action, proof, or evidence of success.

**Law 29 — Empirical language requires an empirical bridge.** Measurement, prediction, falsification, and evidence paths govern empirical claims.

**Law 30 — D0–D7 are optional compatibility lenses.** They do not silently determine phase identity or physical ontology.

**Law 31 — The next move is the practical test.** The value of the analysis is shown by the admissible action, inspection, repair, test, comparison, source return, or stop it clarifies.

**Law 32 — Stronger tools govern stronger claims.** E7G-T frames and inspects stronger methods; it does not bypass them.

### 13.6 Temporal-geometry laws

**Law 33 — Time is a first-class modelling carrier.** When temporal distinctions affect the claim, time MUST be modelled through temporal structure rather than supplied only as a label on configurations or arrows.

**Law 34 — Structural and temporal order are independent.** A D-role does not determine a TD-role, and a TD-role does not determine a D-role.

**Law 35 — Temporal extension is not elapsed clock time.** Extending an event into an interval, history, history family, rule space, or context does not by itself assign a metric duration.

**Law 36 — Temporal projection is not temporal reconstruction.** An event, final state, trend, sample, branch, or history summary does not uniquely determine its temporal source.

**Law 37 — Endpoint identity is not history identity.** Histories with the same visible endpoint may differ in protected order, duration, audit path, causation, recurrence, deadline status, or temporal phase.

**Law 38 — Temporal phase is inquiry-relative equivalence.** A temporal phase is not a synonym for timestamp, lifecycle stage, named period, or exact history.

**Law 39 — Atemporality, unboundedness, recurrence, and completion remain distinct.** None of these properties silently entails another.

**Law 40 — Clocks are declared maps.** A clock supplies temporal coordinates under a model; it does not by itself establish absolute order, simultaneity, causation, or ontology.

**Law 41 — Temporal regimes are derived profiles.** TR0–TR6 summarise established temporal structure and do not replace its carrier, relations, projections, criteria, or witnesses.

**Law 42 — Structural and temporal projections need not commute.** Their order MUST be checked when it can change preservation, loss, classification, or the next move.

**Law 43 — Joint inference is fibre-bounded.** A view cannot support a stronger configuration–temporal classification than its joint reconstruction fibre permits.

### 13.7 Candidate observational-claim laws

> **Informative pending pilot validation.** The following candidate laws apply only when §3.9 is explicitly invoked.

**Candidate Law O1 — Observation is viewing-bounded.** An observational claim cannot assert more than its declared observation records, viewings or measurements, protocols, boundaries, resolutions, evidence paths, and temporal supports license.

**Candidate Law O2 — Record, claim, and interpretation remain distinct.** A record is not automatically a warranted observational claim, and an observational claim is not automatically an interpretation, explanation, prediction, valuation, or ontology claim.

**Candidate Law O3 — Interpretation inherits and adds limitations.** An interpretation inherits the limitations of its load-bearing observations and adds the limitations introduced by assumptions, inference rules, bridges, criteria, and external models.

**Candidate Law O4 — Shared fields preserve disagreement and absence.** Multi-observer composition MUST preserve jointly admissible observations, unresolved divergence, and relevant unknowns as distinct components.

**Candidate Law O5 — Agreement is not automatic truth.** Convergence among observers or instruments does not by itself establish truth, independence of evidence, complete ontology, or absence of systematic error.

**Candidate Law O6 — Temporal support bounds generalisation.** No interpretation may be extended beyond the temporal support of its observations without a separately supported temporal bridge.

**Candidate Law O7 — Observational fields are epistemic boundaries, not ontologies.** An admissible observational field identifies what may support the current inquiry; it does not define all that exists.

### 13.8 Candidate temporal-orientation laws

> **Informative pending pilot validation.** The following candidate laws apply only when §§5.13.1–5.13.6 are explicitly invoked.

**Candidate Law T0 — Extension does not entail orientation.** Admitting the localities and extension structure of a temporal interval, path, or history does not by itself select a representational orientation or assign meaning to a direction. Extension, order, orientation, and directional semantics MUST NOT be silently collapsed.

**Candidate Law T1 — Orientation is declared.** A reversed view or reconstruction is an orientation choice, not evidence that the governing dynamics or causal order reverse.

**Candidate Law T2 — Observer locality is not event chronology.** The fact first available or first used in reconstruction need not be first under the declared clock or sequence.

**Candidate Law T3 — Directional relations remain typed.** Clock precedence, sequence, dependency, observational precedence, reconstructive precedence, generative causation, final constraint, and global consistency MUST NOT be silently interchanged.

**Candidate Law T4 — Reverse representation is not time-reversal symmetry.** A reversed representation is dynamically admissible only when the declared temporal rules establish it.

**Candidate Law T5 — Reverse reconstruction is not retrocausation.** Reversing observational or reconstructive orientation does not establish backward physical production.

**Candidate Law T6 — History-whole membership is not simultaneity.** Events may jointly belong to a complete ordered history without sharing a clock coordinate or establishing physical coexistence outside the model.

**Candidate Law T7 — Relevance narrowing is epistemic by default.** Exclusion from an observer's compatible-history family changes the current reconstruction under declared conditions; it does not by itself establish ontological destruction, non-realisation, or nonexistence.

---

## 14. Failure Modes, Anti-Patterns, and Linting

### 14.1 Core failure modes

Check for:

- false identity between entity and description;
- observation record mistaken for complete entity state;
- observational claim silently expanded into interpretation;
- observer agreement mistaken for truth or independent confirmation;
- divergence or non-observation erased during shared-field composition;
- temporal extrapolation beyond observational support;
- viewpoint reversal mistaken for time-reversal symmetry or causal reversal;
- observer locality mistaken for clock precedence;
- history-whole membership mistaken for simultaneity or physical coexistence;
- history relevance narrowing mistaken for ontological collapse;
- false reconstruction;
- hidden boundary shift;
- collapsed model, admissibility, and phase boundaries;
- undeclared semantic context;
- undeclared inquiry;
- missing or overloaded temporal declaration;
- temporal regime used without temporal carrier or witness;
- structural D-role silently treated as temporal order;
- temporal point, line, surface, or higher role treated as a literal physical dimension without bridge support;
- final state mistaken for its history;
- one selected branch mistaken for the history family;
- temporal projection mistaken for temporal reconstruction;
- temporal phase without criterion or criterion edition;
- atemporality confused with unboundedness, recurrence, or completion;
- clock equality mistaken for absolute simultaneity;
- precedence, causation, dependency, and clock order silently interchanged;
- structural and temporal projection order left unchecked where material;
- projection-loss denial;
- slice mistaken for whole;
- invariant without transformation class;
- phase criterion without valid equivalence;
- phase label without criterion edition;
- similarity mistaken for phase equivalence;
- static phase difference reported as a transition;
- viewing mistaken for world transformation;
- retargeting mistaken for viewing;
- reframing mistaken for entity change;
- phase-level arrow hiding representative dependence;
- path endpoints compared at an undeclared level;
- phase inference from a view spanning several phases;
- relative support mistaken for truth, probability, or exclusion;
- support values used without declared semantics, provenance, update rule, or calibration posture;
- phase-spread hidden by selecting the highest-supported candidate;
- weakly supported candidates silently deleted without an exclusion rule;
- bridge inflation;
- formal-neighbourhood overclaim;
- empirical language without empirical bridge;
- proof text mistaken for proof object;
- Proof-of-Path mistaken for proof;
- AI fluency mistaken for evidence;
- dashboard accepted state mistaken for system state;
- report form mistaken for authorisation or performed work;
- replacement of mature tools;
- missing stop or reopen condition.

### 14.2 Modelling-bias checks

Before relying on a model, ask:

- Did the chosen inquiry exclude a material stakeholder or use?
- Were tolerated differences selected because they were convenient rather than justified?
- Does the configuration omit unknown or contested positions?
- Was an equivalence criterion designed to force a desired partition?
- Does a view conceal phase-defining relations?
- Are representative-specific failures hidden by a phase label?
- Is a path favoured because it produces a cleaner report rather than a safer or more faithful result?
- Is an apparent trade-off merely a limitation of the chosen implementation?
- Has an old criterion edition or stale evidence been reused?
- Does a conclusion exceed the declared viewing, observation protocol, resolution, population, or temporal support?
- Were several observations treated as independent without checking shared provenance, instrumentation, or systematic error?

### 14.3 Practical linter

A consequential E7G-T analysis SHOULD pass the following checks:

```text
[ ] Entity of concern is recoverable.
[ ] Semantic context is named.
[ ] Inquiry and intended use are named.
[ ] Operational boundary is declared.
[ ] Unknown or contested positions are visible.
[ ] Every load-bearing arrow has a change kind.
[ ] Every projection states preservation and loss.
[ ] Every material temporal account states carrier, boundary, and order-role.
[ ] Every temporal projection states temporal preservation and loss.
[ ] Temporal reconstruction is set-valued unless uniqueness is justified.
[ ] Temporal phase use names a criterion and edition.
[ ] TR0–TR6 labels have declared derivation support.
[ ] Atemporality, unboundedness, recurrence, and completion are not conflated.
[ ] Structural–temporal projection order is checked where material.
[ ] Reconstruction is set-valued unless uniqueness is justified.
[ ] Phase use names a criterion and edition.
[ ] Equivalence is valid over the admitted family.
[ ] Static difference is not misreported as transition history.
[ ] Phase-level operations are representative-independent or marked otherwise.
[ ] View-based classification checks PhaseCandidatesQ(view).
[ ] Support basis and support status are separate.
[ ] Relative-support semantics, provenance, update rule, and exclusion rule are declared where the pilot is invoked.
[ ] High support is not treated as truth and low support is not treated as exclusion.
[ ] Bridge mode matches claim strength.
[ ] Admissible and blocked uses are stated.
[ ] Next move or stop condition is explicit.
```

If the analysis cannot complete the first four checks, it is not yet a reusable E7G-T analysis. It is only a cue or sketch.

### 14.4 Candidate observational-claim pilot linter

When §3.9 is invoked, the pilot analysis SHOULD additionally pass:

```text
[ ] Observer or observing system is declared.
[ ] Observation record is distinct from the observational claim.
[ ] Viewing or measurement and protocol are declared.
[ ] Spatial, population, resolution, and temporal support are bounded.
[ ] Evidence path, provenance, known limitations, and unknowns are visible.
[ ] The observational claim asserts no more than the record licenses.
[ ] Interpretation is explicitly typed and linked to supporting claims.
[ ] Added assumptions, inference rules, bridges, criteria, and models are declared.
[ ] Interpretation preserves inherited limitations and adds its own.
[ ] Shared-field composition separates joint content, divergence, and unknowns.
[ ] Agreement is not treated as automatic truth or independent confirmation.
[ ] Temporal extension has a separately supported bridge.
[ ] Resulting next move, reliance limit, source return, or stop is explicit.
```

Failure to pass this supplemental linter means only that the analysis is not conforming to the candidate observational-claim module. It does not by itself invalidate an otherwise conforming ordinary E7G-T analysis.

### 14.5 Candidate temporal-orientation pilot linter

When §§5.13.1–5.13.6 are invoked, the pilot analysis SHOULD additionally pass:

```text
[ ] Temporal orientation and observer locality are declared.
[ ] Temporal extension, admitted order, chosen orientation, and directional semantics are distinguished where material.
[ ] Clock, sequence, dependency, observation, reconstruction, causation, final constraint, and global consistency relations are typed where material.
[ ] Reverse representation is distinguished from time-reversal symmetry.
[ ] Reverse observation or reconstruction is not treated as causal reversal without a supporting substrate and evidence.
[ ] Structure preserved, reversed, hidden, or unsupported under orientation change is stated.
[ ] TD4 history-whole membership is not treated as clock simultaneity or model-independent physical coexistence.
[ ] Compatible-history relevance is tied to a declared accumulated record and fixed conditions.
[ ] Monotonic narrowing is not claimed across corrections, retractions, or changed models, boundaries, assumptions, or interaction rules.
[ ] Excluded histories are not described as destroyed, unrealised, or nonexistent without a separate Reality Bridge.
[ ] The module changes a reconstruction, reliance limit, next move, or stop condition rather than merely adding terminology.
```

Failure to pass this supplemental linter means only that the analysis is not conforming to the candidate temporal-orientation module. It does not by itself invalidate an otherwise conforming ordinary E7G-T analysis.

### 14.6 Candidate topological-overlay pilot linter

When §§8.13.1–8.13.6 are invoked, the pilot analysis SHOULD additionally pass:

```text
[ ] Carrier and topology are explicitly declared.
[ ] The topology has inquiry-relevant construction or justification.
[ ] Operational adjacency is not silently treated as topological neighbourhood.
[ ] Operational phase boundary is not silently treated as topological boundary.
[ ] Continuity claims satisfy the declared topologies.
[ ] Homeomorphism claims include the required bijection, continuity, and continuous inverse.
[ ] Connectedness, path, compactness, separation, and deformation claims are not inferred from visual or operational resemblance.
[ ] Phase quotient topology, when used, is explicitly constructed from a declared topology and pinned phase equivalence.
[ ] Topological gluing is not inferred from interface composition alone.
[ ] Topology is kept distinct from metric, order, orientation, and causation.
[ ] Temporal topology is not used to infer time direction, causal direction, or physical reversibility.
[ ] The overlay changes a material result or next move rather than merely adding terminology.
```

Failure to pass this supplemental linter means only that the analysis is not conforming to the candidate topological-overlay module. It does not by itself invalidate an otherwise conforming ordinary E7G-T analysis.

---

## 15. Worked Unified Examples

### 15.1 AI answer used as a source

**Modelled entity.** A current factual claim about a legal or administrative rule.

**Available view.** An AI-generated answer.

**Extensional–projective account.** The answer is a D2 textual representation produced under a prompt, model state, tool state, and publication context. It may preserve a useful summary while losing source provenance, exceptions, jurisdictional detail, and currentness.

```text
AIAnswer : D2 @ TR1 / UserQuestionContext ; CurrentRuleInquiry
```

```text
Preserve: stated conclusion, some explanatory relations
Lose: source chain, full exception set, possibly currentness
Reconstruction: underdetermined without source return
```

**Phase criterion.** For reliance, answers are equivalent only when they preserve the same operative rule, jurisdiction, effective date, exceptions, and source support posture.

If the reconstruction fibre contains source states belonging to both `ruleApplies` and `ruleDoesNotApply` phases, then:

```text
|PhaseCandidatesQ(AIAnswer)| > 1
```

The answer does not support operational reliance.

**Next move.** Return to authoritative sources, verify the effective date and exceptions, then reclassify.

**Blocked overread.** Fluent explanation is not current legal evidence.

### 15.2 Certified translation and legal modality

**Modelled entity.** A source-tethered certified translation package.

**Semantic context.** `CertifiedTranslation.Contract.SelectedJurisdiction`.

**Inquiry.** Preserve document identity, names, dates, numbers, legal modality, and source traceability while allowing natural target-language variation.

Protected conditions:

```text
source-document identity
party and name identity
dates and numbers
legal modality
scope of rights and obligations
source anchors for uncertain readings
```

Tolerated differences:

```text
line wrapping
font substitution
non-semantic spacing
natural target-language syntax
```

Suppose the source says:

```text
The party may terminate the agreement.
```

A target reading equivalent to “has the right to terminate” may remain in the same legal-modality phase under the selected criterion.

A target reading equivalent to:

```text
The party shall terminate the agreement.
```

changes discretionary force into obligation and crosses the phase boundary.

An OCR view with two plausible name readings produces:

```text
RecOCR(nameImage) = {ΓnameA, ΓnameB}
```

If the candidates belong to different identity phases, source return is mandatory before normalisation.

**Next move.** Restore legal-force equivalence, resolve the source ambiguity, and rerun QA.

### 15.3 Software refactoring and representative dependence

**Modelled entity.** A software component described through an interface-level behavioural phase.

**Inquiry.** Treat implementations as equivalent when they preserve the public API, authorised state transitions, error semantics, and data-entitlement behaviour under a pinned test domain.

Two implementations `ΓA` and `ΓB` may be in the same phase under the current public-interface criterion.

A migration operator `τ` changes internal storage assumptions. If:

```text
τ(ΓA)
```

preserves entitlement behaviour while:

```text
τ(ΓB)
```

silently exposes restricted records, then:

```text
ΓA ≈Q ΓB
```

but:

```text
τ(ΓA) ≉Q τ(ΓB)
```

The phase-level operation is not well-defined. Representative dependence is present.

**Next move.** Keep the operation configuration-level, strengthen the criterion or preconditions, and test all representatives before publication as a phase-safe refactoring.

### 15.4 Dashboard used to classify business health

**Modelled entity.** A business operating system.

**View.** A dashboard with green revenue, margin, and conversion tiles.

**Projection account.** The dashboard preserves selected aggregated metrics and windows. It may lose transaction-level anomalies, cohort structure, data-quality uncertainty, cash timing, causal explanations, and unreported liabilities.

**Phase inquiry.** Classify the business as `operationallyHealthy` only when liquidity, profitability quality, customer concentration, fulfilment stability, and data freshness satisfy the criterion.

If a green dashboard is compatible with both healthy and cash-constrained source configurations, then the view is phase-spanning.

**Next move.** Reopen source records and inspect cash conversion, concentration, exceptions, and freshness before relying on the health classification.

**Blocked overread.** The dashboard is not the business, and green tiles are not proof of health.

### 15.5 Proof assistant session

**Modelled entity.** A formal theorem and its proof state inside a declared proof assistant.

**Views.** Proof text, tactic script, goal display, and explanatory prose.

The interface view may preserve current goals and tactic effects while hiding elaborated proof terms or kernel-checking details.

The operational phase criterion may classify proof states by unresolved obligations under the formal substrate.

A tactic is a typed transformation. A proof script may document a path. A completed Proof-of-Path is not itself a proof.

Only the proof assistant’s checking substrate establishes formal acceptance.

**Next move.** Identify the formal substrate, unresolved goals, elaboration result, and kernel acceptance status.

### 15.6 Speculative holographic analogy

**Modelled entity.** A philosophical or speculative model of lower-order appearance from richer structure.

**Bridge mode.** `contemplative-what-if` or `formal-analogy` unless a recognised mathematical and empirical substrate is supplied.

A lower-order projection may illustrate how several sources can produce similar appearances. It does not establish that the physical universe is literally a hologram or that D0–D7 are physical dimensions.

**Next move.** State the analogy, preserved structure, lost structure, formal neighbourhood, and empirical stop condition.

### 15.7 Translation workflow as temporal geometry

**Modelled entity.** A translated document and its production history.

**Structural placement.** The current DOCX is a D2/D3 representation and artefact.

**Temporal placement.**

- the current file snapshot is `TD0`;
- its ordered OCR → translation → revision → QA → delivery history is `TD1`;
- alternative revision branches or competing translation histories form `TD2`;
- workflow rules, deadlines, and approval requirements participate at `TD6`;
- the client instruction and audit frame participate at `TD7`.

The delivered file is a temporal projection of the workflow history:

```text
πΘ^TD1→TD0(workflowHistory) = deliveredFile
```

It may preserve the final content while losing intermediate revisions, rejected alternatives, reviewer identity, chronology, unresolved warnings, and evidence that the required QA step occurred.

Two histories may end in byte-identical final files but occupy different temporal phases under an audit criterion:

```text
h1 = OCR → translation → revision → QA → delivery
h2 = OCR → translation → delivery
```

If the inquiry protects only final-file content, `h1 ≈QΘ h2` may hold. If the inquiry protects performance of revision and QA before delivery, `h1 ≉QΘ h2`.

The final file alone therefore may determine the configuration phase while leaving the temporal audit phase indeterminate:

```text
|PhaseCandidatesQ(finalFile)| = 1
|TemporalPhaseCandidatesQΘ(finalFile)| > 1
```

**Next move.** Return to version history, QA records, and delivery evidence before claiming that the required process was completed.

**Blocked overread.** The final document is not its production history.

### 15.8 Candidate observation-to-interpretation pilot examples

> **Informative.** These compact cases show the proposed module's intended discrimination. They are pilot fixtures, not evidence that the module has passed the promotion gate.

| Domain | Observation record or bounded observational claim | Interpretation requiring added support | Typical blocked overread |
| --- | --- | --- | --- |
| AI output | The declared model produced text `v` under prompt, model, tool, and time context `P`. | The answer accurately states the current external rule. | Generated fluency is treated as observation of the external world. |
| Dashboard | System `A` recorded zero qualifying events in window `[t1,t2]` under protocol `P`. | The contribution has no readers, lacks value, or will not gain readers. | Instrument-bounded non-recording is treated as timeless absence or valuation. |
| Translation QA | Reviewer `O` found no listed critical errors in sample `S` under rubric `R`. | The complete translation is error-free and fit for every intended use. | Sampled review is generalised beyond its scope, rubric, or competence boundary. |
| Software testing | Test suite `T` passed implementation `Γ` in environment `E` at commit `c`. | The implementation is correct, secure, and reliable in all environments. | Tested behaviour is treated as implementation truth beyond the test domain. |
| Scientific measurement | Instrument `M` produced readings `r` under calibration and protocol `P`. | A selected external model uniquely explains the phenomenon. | Measurement record is collapsed into ontology or unique causation. |
| Interpersonal reasoning | Observer `O` recorded behaviour `b` in context and interval `Θ`. | The person intended motive `m`, has enduring trait `q`, or will always behave so. | Behavioural evidence is converted into intention, identity, or timeless prediction. |

For the dashboard case, a pilot record may be written:

```yaml
ObservationRecord:
  observationId: analytics-zero-events-001
  observerRef: analytics-system-A
  modelledEntityRef: contribution-readership
  inquiryProfileRef: current-recorded-engagement
  semanticContextRef: declared-analytics-schema
  viewingOrMeasurementRef: qualifying-reader-event-query
  observationProtocolRef: protocol-P
  observedAtOrDuring: [t1, t2]
  temporalSupport: closed-window-t1-t2
  spatialOrPopulationSupport: instrumented-channels-and-consenting-users
  resolution: event-count
  recordedContent: zero-qualifying-events
  knownLimitations:
    - blocked-or-disabled-analytics
    - offline-reading
    - uninstrumented-channels
  unknownPositions:
    - readership-outside-measurement-boundary
```

Admissible observational claim:

```text
The declared analytics system recorded zero qualifying reader events
between t1 and t2 under protocol P.
```

Interpretation requiring declared assumptions and criteria:

```text
The contribution currently has no readers.
```

Unsupported overread:

```text
Therefore the contribution lacks value and will not gain readers.
```

**Next move.** Check instrumentation coverage, source logs, alternative channels, time window, and the decision criterion before drawing a readership, value, or future-performance conclusion.

---

## 16. Conformance and Formalisation

### 16.1 Minimal ordinary conformance

A valid ordinary E7G-T claim includes, as applicable:

1. modelled entity;
2. semantic context;
3. inquiry or purpose;
4. operational boundary;
5. selected route;
6. temporal carrier and temporal boundary where temporal distinctions are material;
7. relevant configuration or temporal projection, transformation, or phase criterion;
8. structurally and temporally preserved and lost information where a view is involved;
9. required invariants and tolerated variation where configuration or temporal phase use is involved;
10. support basis and support status for consequential claims;
11. next move or stop condition.

### 16.2 Reference-analysis conformance

A reference analysis additionally includes, when relevant:

- typed relations;
- criterion edition;
- equivalence or membership witness;
- typed transition;
- representative-dependence status;
- representative-specific outcomes;
- relation and invariant effects;
- phase-view compatibility;
- temporal-order and causality semantics;
- temporal projection and reconstruction ambiguity;
- temporal criterion and edition;
- temporal-phase view compatibility;
- structural–temporal projection commute status;
- reconstruction ambiguity;
- cross-context bridge;
- validity window;
- admitted and blocked uses.

### 16.3 Formal implementation conformance

A formal implementation MUST settle:

- configuration syntax and identity;
- admitted configuration predicate;
- equivalence validity;
- transition compatibility;
- phase-level operation validity;
- path composition;
- typed commute-check result semantics;
- interface gluing;
- viewing descent;
- reconstruction-fibre semantics;
- `PhaseCandidatesQ(view)` semantics;
- temporal carrier, extension, and order-role semantics;
- temporal viewing and temporal reconstruction-fibre semantics;
- temporal equivalence validity;
- `TemporalPhaseCandidatesQΘ(view)` semantics;
- joint configuration–temporal candidate semantics;
- clock, recurrence, unboundedness, atemporality, and completion semantics where implemented;
- structural–temporal projection commute-check semantics;
- optional overlay definitions;
- machine-checkable examples and counterexamples.

### 16.4 Formal maturity statuses

Recommended maturity labels:

```text
conceptual
specified
formallyMapped
machineEncoded
proofChecked
empiricallyCalibrated
operationallyValidated
```

These are not a single inevitable ladder. A use may be formally mapped without empirical calibration, or operationally useful without full mathematical formalisation.

### 16.5 Formalisation obligations

A proposed mathematical formalisation SHOULD state:

- the selected mathematical object;
- mapping mode;
- carrier;
- definitions;
- laws and proof obligations;
- preserved and lost structure;
- counterexamples;
- domain validation boundary;
- stop condition.

Formal resemblance does not establish ontology, empirical truth, or operational validity.

### 16.6 Candidate observational-claim module conformance

An analysis MAY declare:

```text
E7G-T observational-claim pilot module invoked
```

Such an analysis additionally includes, where applicable:

- observer or observing-system identity;
- observation-record references;
- viewing or measurement and protocol;
- semantic, temporal, spatial, population, and resolution support;
- provenance, evidence, limitations, and unknowns;
- an explicit claim type: `observationalClaim` or `interpretation`;
- interpretation dependencies, assumptions, inference rules, bridges, criteria, and external models;
- shared-field composition as `⟨Cjoint,D,U⟩` where several observers are composed;
- temporal-extension justification where the conclusion exceeds the observed window;
- admissible use, non-admissible use, and stop or reopen condition.

Until promotion under §3.9.9 and §19.10, omission of these fields does not make an ordinary analysis non-conforming under §§16.1–16.3.

### 16.7 Candidate temporal-orientation module conformance

An analysis MAY declare:

```text
E7G-T temporal-orientation pilot module invoked
```

Such an analysis additionally includes, where applicable:

- temporal orientation and observer temporal locality;
- the declared relation kind for each load-bearing directional claim;
- the reverse representation or reconstruction being considered;
- relations preserved, reversed, hidden, or unsupported under orientation change;
- separate status for time-reversal symmetry and causal reversal;
- the TD4 history-whole and applicable clock or synchronisation model;
- the observer's accumulated valid record and compatible-history family;
- fixed-condition references required for monotonic narrowing;
- corrections, retractions, model changes, or interaction rules that may alter relevance;
- admissible use, non-admissible use, and stop or reopen condition.

Until promotion under §19.11, omission of these fields does not make an ordinary analysis non-conforming under §§16.1–16.3.

### 16.8 Candidate topological-overlay module conformance

An analysis MAY declare:

```text
E7G-T topological-overlay pilot module invoked
```

Such an analysis additionally includes, where applicable:

- carrier identity and carrier kind;
- the declared topology and its construction, basis, subbasis, or other semantics;
- justification for why the topology is material to the inquiry;
- continuity, connectedness, separation, path, quotient, homeomorphism, or deformation claims actually used;
- witnesses, proofs, references, or formal-substrate results supporting load-bearing topological claims;
- preserved and unrepresented structure;
- explicit separation from metric, order, orientation, and causation;
- admissible use, non-admissible use, and stop or reopen condition.

Until promotion under §19.13, omission of these fields does not make an ordinary analysis non-conforming under §§16.1–16.3.

---

## 17. Public-Use Cautions and Maturity Statement

### 17.1 Public cautions

When presenting E7G-T publicly:

- do not call it established mathematics;
- do not call it new physics;
- do not claim D0–D7 are literal physical dimensions;
- do not claim TD0–TD7 are literal physical time dimensions;
- do not present a temporal surface or higher temporal role as empirical physics without a defined formal and empirical bridge;
- do not confuse atemporality, unboundedness, recurrence, and completion;
- do not present a reversed view or reconstruction as time-reversal symmetry or reversed causation;
- do not present membership in a history-whole as clock simultaneity or model-independent physical coexistence;
- do not present observer-relative history relevance narrowing as destruction or nonexistence of alternatives;
- do not call operational adjacency a topological neighbourhood or a phase boundary a topological boundary unless a topology and the required relation are established;
- do not infer continuity, homeomorphism, metric, order, orientation, causation, or physical reversibility from a topological overlay alone;
- do not claim a holographic reading proves a holographic universe;
- do not call an E7G-T arrow a morphism unless the category is defined;
- do not call an E7G-T placement a type judgement unless a type substrate is defined;
- do not call a phase a physical phase unless the relevant physical formalism and evidence are supplied;
- do not call Proof-of-Path a formal proof;
- do not present a report or validator result as authorisation, acceptance, or completed work;
- do not present an admissible observational field as complete reality or ontology;
- do not present inter-observer agreement as automatic truth, independence, or completeness;
- do not conceal an interpretation inside observational wording;
- do not replace domain standards or expert review.

### 17.2 Preferred public sentence

> E7G-T helps people inspect representations, histories, and changes before relying on them. It asks what a structural or temporal view preserves or loses, which source configurations and histories remain possible, which differences matter for the current purpose, whether a material boundary has been crossed, and what the next responsible move should be.

### 17.3 Maturity statement

E7G-T v0.11-UC4 is a unified canonical reference candidate with first-class extensional–projective–phase temporal geometry restored for pilot testing and informative observational-claim, temporal-orientation, and topological-overlay modules added for controlled cross-domain validation.

It is ready for:

- controlled practical pilots;
- AI-output and source-return review;
- translation QA experiments;
- document and software version-history analysis;
- deadline, recurrence, branch, synchronisation, and temporal audit pilots;
- dashboard and document-workflow analysis;
- software representative-dependence tests;
- proof-path prototypes;
- formal-neighbourhood review;
- observation-to-interpretation claim-typing pilots;
- multi-observer field-composition pilots that retain divergence and unknowns;
- topological-overlay pilots on declared configuration, phase-quotient, temporal, or history carriers;
- implementation-schema prototyping.

It is not ready for:

- claims of established mathematics;
- claims of empirical physics;
- claims of universal formal validity;
- safety authorisation;
- replacement of domain tools;
- v1.0 stability.

### 17.4 v1.0 gate

Do not move to v1.0 until:

- shared terminology is stable;
- all three boundary kinds are used consistently;
- D7/context and TD7/temporal-context distinctions survive pilot use;
- TD0–TD7 order roles and TR0–TR6 derived regimes survive pilot use without being treated as physical dimensions;
- extensional–projective, temporal-geometry, and phase routes can be used separately without ambiguity;
- the combined `PhaseCandidatesQ(view)` calculus is tested on real cases;
- `TemporalPhaseCandidatesQΘ(view)` and joint configuration–temporal candidates are tested on real histories;
- atemporality, unboundedness, recurrence, and completion are distinguished consistently;
- temporal projection and reconstruction claims are tested against cases with identical endpoints and different histories;
- structural–temporal projection order is tested on at least one non-commuting workflow;
- representative-dependence examples are independently reviewed;
- at least three domain applications are piloted;
- at least two lightweight worksheets are tested;
- at least one formalisation prototype is implemented or clearly bounded;
- public wording and reference anchors are reviewed;
- the candidate observational-claim module passes its §19.10 promotion test or is revised, retained as informative, or removed;
- the candidate temporal-orientation module passes its §19.11 promotion test or is revised, retained as informative, or removed;
- the candidate topological-overlay module passes its §19.13 promotion test or is revised, retained as informative, or removed;
- overclaim risks are reduced.

---

## 18. Migration from E7G-T v0.9 and E7GT-Φ v0.3.2

### 18.1 Status of predecessor documents

This unified candidate proposes to supersede the two predecessor kernels for future integrated testing, while preserving them as historical and source specifications until the unified candidate passes regression and pilot review.

### 18.2 Preserved strengths from E7G-T v0.9

- D0–D7 modelling-order vocabulary;
- temporal-regime vocabulary;
- explicit context and boundary;
- extension, projection, and reconstruction as distinct moves;
- preservation and loss accounting;
- transformation-class discipline for invariants;
- bridge modes and weakest-link caution;
- OneLine/MiniCard/FullCard practical escalation;
- Proof-of-Path;
- Reality Bridge;
- Formal Neighbourhood;
- anti-replacement and public-use cautions;
- next-admissible-move test.

### 18.3 Preserved strengths from E7GT-Φ v0.3.2

- semantic context and inquiry as distinct declarations;
- relational configurations rather than independent scalar axes;
- phase as inquiry-relative equivalence;
- criterion and edition pinning;
- typed change kinds;
- admitted transitions rather than edit-distance adjacency;
- representative dependence;
- phase-level lifting conditions;
- relation- and invariant-specific effects;
- configuration, phase, and audit path comparison;
- phase-view compatibility;
- reconstruction fibres;
- reframing and cross-frame bridges;
- support-basis/support-status separation;
- joint-attainability discipline.

### 18.4 Resolved conflicts

| Earlier tension | Unified resolution |
| --- | --- |
| D7 treated as context | semantic context is constitutional; D7 is an optional context-like role |
| phase placement after D-order interpretation | phase criterion is defined independently; D-role interpretation is optional |
| one undifferentiated boundary | model, admissibility, and phase boundaries are distinct |
| broad transformation arrow | every reference-level arrow has a typed change kind |
| invariant used ambiguously | transformation invariants and phase-defining invariants are separately declared |
| projection and viewing used interchangeably | viewing is general entity-preserving representation change; order projection is a subtype |
| temporal regimes treated as the whole temporal layer | temporal geometry is first-class; TR0–TR6 are derived, non-exclusive profiles |
| separate practical card families | unified modular profiles with legacy compatibility mappings |
| projection analysis and phase classification merely adjacent | explicit `PhaseCandidatesQ(view)` combined calculus |

### 18.5 Earlier construct mapping

| Earlier construct | Unified treatment |
| --- | --- |
| `X : Dn @ TRi / C` | `X : Dn [Θ: TDm; TR: {TRi...}] / C ; I`; the legacy form remains readable |
| `∂X` | model boundary, distinguished from admissibility and phase boundaries |
| `τT(X)=Y` | compact notation backed by a typed `ChangeRecord` |
| `ρ(Y)⇒{Xi}` | reconstruction fibre under a declared viewing |
| D-order path | retained in the extensional–projective route |
| operational phase | equivalence class under a pinned criterion |
| PhaseCard | historical; mapped to modular `E7-Check` or `E7-Analysis` |
| `Φ-Line` | route-specific view of `E7-Line` |
| `Φ-Check` | route-specific view of `E7-Check` |
| `PhaseAnalysis` | phase-focused view of `E7-Analysis` |
| OneLine/MiniCard/FullCard | extensional–projective views of unified profiles |

### 18.6 Temporal restoration in v0.11

v0.10 retained temporal vocabulary but reduced most temporal content to declared profiles and transition motifs. v0.11 restores the stronger intended architecture:

- time is a first-class modelling carrier rather than an optional label;
- TD0–TD7 express temporal locality, line, surface, body, world-history, variation, transformation, and context roles;
- temporal extension, projection, preservation and loss, reconstruction, and inquiry-relative phase are defined explicitly;
- TR0–TR6 remain useful as derived regime profiles;
- structural and temporal order are independent;
- atemporality, unboundedness, recurrence, and completion are distinct;
- joint configuration–temporal inference is bounded by its reconstruction fibre;
- structural and temporal projections are checked for non-commutativity.

### 18.7 Observational-claim pilot addition in v0.11-UC2

UC2 preserves the normative core of UC1 and adds a labelled informative module that:

- distinguishes observation records, observational claims, and interpretations;
- defines an inquiry-relative admissible observational field without equating it with reality;
- models a shared observational field as jointly admissible content, unresolved divergence, and relevant unknowns;
- makes temporal support and extrapolation explicit;
- connects observational support to projection, reconstruction fibres, phase candidates, and weakest-link discipline;
- supplies cross-domain pilot fixtures, a supplemental linter, conformance fields, and a promotion gate.

This addition does not yet assert that observation is a new normative primitive. It creates a testable candidate whose practical contribution must be distinguished from machinery already present in UC1.

### 18.8 Temporal-orientation pilot addition in v0.11-UC3

UC3 preserves the normative core and UC2 observational-claim pilot module, and adds a labelled informative temporal module that:

- makes explicit the separability of temporal extension, admitted order, representational orientation, and directional meaning;
- declares temporal orientation and observer temporal locality;
- separates viewpoint reversal, time-reversal symmetry, and causal reversal;
- types observational and reconstructive precedence, generative causation, final constraint, and global consistency;
- distinguishes TD4 history-whole membership from clock simultaneity and model-independent physical coexistence;
- defines observer-relative compatible-history relevance narrowing under fixed conditions;
- preserves corrections, retractions, model changes, and interaction rules as possible reasons for non-monotonic change;
- supplies candidate laws, linting, conformance fields, machine-oriented fields, and a pilot promotion gate.

This addition does not assert fundamental time neutrality, retrocausation, supertime, or physical realisation of every alternative history. Those remain separately bridged theoretical or ontological hypotheses.

### 18.9 Topological-overlay pilot addition in v0.11-UC4

UC4 preserves the normative core and the UC2–UC3 informative pilots, and adds a labelled informative topological module that:

- permits a declared configuration, phase-quotient, temporal, history, or other justified carrier to receive a declared topology;
- defines a topology declaration with carrier, construction, semantics, support, applicability, and stop conditions;
- separates operational adjacency from topological neighbourhood and operational phase boundary from topological boundary;
- requires continuity, homeomorphism, connectedness, quotient, and gluing claims to satisfy their own mathematical conditions;
- permits a pinned operational-phase quotient to receive the quotient topology when an underlying topology is declared and the construction is useful;
- makes temporal-carrier topology explicitly independent of temporal order, orientation, clocks, and causation;
- supplies supplemental linting, conformance fields, machine-oriented fields, Pilot I, and a promotion gate.

This addition does not make E7G-T inherently topological and does not assert that every operational transition structure has a privileged topology. Topology remains optional and inquiry-justified.

### 18.10 Regression rule

A unified revision MUST NOT silently change the intended result of a predecessor worked example. If the result changes, the revision MUST identify whether the cause is:

- corrected semantics;
- changed inquiry;
- changed criterion;
- changed evidence;
- resolved ambiguity;
- discovered representative dependence;
- earlier error.

---

## 19. Recommended Pilot Programme

### 19.1 Pilot A — AI answer phase-spread

Test whether `PhaseCandidatesQ(view)` identifies cases where a fluent answer is compatible with several current-rule phases.

### 19.2 Pilot B — Translation invariant and phase QA

Test whether the combined route catches legal modality, identity, number, date, documentary status, and source-trace changes missed by ordinary fluency review.

### 19.3 Pilot C — Software representative dependence

Test whether apparently phase-safe operations behave differently across representative implementations.

### 19.4 Pilot D — Dashboard operational classification

Test whether phase-spread analysis prevents health, readiness, or compliance classification from a lossy dashboard view.

### 19.5 Pilot E — Proof-path accounting

Test whether the unified kernel separates proof object, proof state, tactic path, explanation, and phase of unresolved obligations.

### 19.6 Pilot F — Temporal projection and audit phase

Use a versioned translation, document, or software workflow to test whether identical or equivalent final states can arise from histories in different temporal phases, whether the final-state view is temporally phase-spanning, and whether source/history return changes the reliance decision.

### 19.7 Pilot G — Observation, interpretation, and shared-field composition

Test the §3.9 candidate module in at least four materially different domains, including:

1. AI output or automated summary;
2. dashboard or analytics evidence;
3. translation QA or document review;
4. software testing or scientific measurement.

An interpersonal-reasoning case MAY be included to test whether the same discipline transfers beyond instrument-centred domains without claiming privileged access to intention.

Each case SHOULD compare:

```text
ordinary review
vs
existing UC1 source/view + support + reconstruction analysis
vs
UC2 observational-claim module
```

Record whether the module uniquely or more clearly identifies:

- an observational claim that exceeds its record;
- an interpretation hidden in observational wording;
- undeclared assumptions, bridges, criteria, or external models;
- erased divergence or unknowns in multi-observer composition;
- false independence among agreeing records;
- unsupported temporal generalisation;
- a changed next move, reliance limit, source return, or stop decision;
- unacceptable burden, ambiguity, redundancy, or false precision introduced by the module.

### 19.8 Pilot H — Temporal orientation, observer locality, and history relevance

Test §§5.13.1–5.13.6 in at least four materially different settings, including:

1. biographical or planning reconstruction;
2. forensic, audit, or version-history reconstruction;
3. scientific, engineering, or software-process interpretation;
4. branching scenarios, forecasts, or decision paths.

Each case SHOULD compare:

```text
ordinary temporal narration
vs
existing UC2 temporal + observational analysis
vs
UC3 temporal-orientation module
```

Record whether the module uniquely or more clearly:

- separates later observer locality from earlier clock precedence;
- distinguishes reverse reconstruction from time-reversal symmetry and causal reversal;
- prevents final constraint or global consistency from being misreported as generative causation;
- prevents history-whole membership from being misreported as simultaneity;
- represents relevance narrowing without ontological collapse;
- exposes when corrections, retractions, changed models, boundaries, assumptions, or interaction rules break monotonic narrowing;
- changes a reconstruction, reliance limit, next move, source return, or stop decision;
- introduces unacceptable burden, ambiguity, redundancy, or false precision.

### 19.9 General pilot evaluation question

> Did the unified kernel catch a material structural or temporal risk, distinguish a hidden change kind or history, expose a configuration- or temporal-phase-spanning view, or clarify a next responsible move that ordinary review missed?

Do not expand the theory merely because more notation is possible. Expand only where pilot evidence shows a recurring unresolved modelling need.

### 19.10 Observational-claim promotion decision

After Pilot G, assign one of four outcomes:

```text
promoteToNormativeCore
reviseAndRepilot
retainAsInformativeModule
removeAsRedundantOrHarmful
```

Promotion requires all of the following:

- material value demonstrated in at least four materially different domains;
- at least two cases in which the module catches or clarifies a consequential issue not adequately exposed by the ordinary UC1 application alone;
- no unresolved contradiction with source/view, projection/reconstruction, support, phase, bridge, or temporal disciplines;
- stable discrimination among observation record, observational claim, and interpretation under independent review;
- shared-field use that preserves conflict and unknowns without implying that consensus creates truth;
- acceptable documentation burden under at least one lightweight profile;
- explicit counterexamples showing when the module should not be invoked;
- a documented decision explaining whether each candidate rule is promoted, revised, retained as informative, or rejected.

Pilot results MUST NOT be described as validation merely because the module can be applied. The relevant question is whether it improves warranted claims and responsible decisions under controlled comparison.

### 19.11 Temporal-orientation promotion decision

After Pilot H, assign one of the four outcomes used in §19.10.

Promotion requires all of the following:

- material value demonstrated in at least four materially different settings;
- at least two cases in which the module prevents a consequential orientation, causation, simultaneity, or collapse conflation not adequately exposed by ordinary UC2 application alone;
- stable discrimination among viewpoint reversal, time-reversal symmetry, and causal reversal under independent review;
- stable typing of directional relations without forcing one ontology of time;
- relevance narrowing that handles fixed conditions, corrections, retractions, and model changes without false monotonicity;
- acceptable documentation burden under at least one lightweight profile;
- explicit counterexamples showing when the module should not be invoked;
- a documented decision explaining whether each candidate rule is promoted, revised, retained as informative, or rejected.

Pilot results MUST NOT be described as evidence for fundamental time neutrality, retrocausation, supertime, or physical realisation of alternative histories. Those claims require independent formal or empirical bridges.

### 19.12 Pilot I — Topological overlay

Test §§8.13.1–8.13.6 in at least four materially different settings, including:

1. a configuration carrier where operational adjacency and topological neighbourhood could be confused;
2. an operational-phase quotient where quotient topology may expose or erase relevant separation or connectivity structure;
3. a temporal or history carrier where topology must remain distinct from order and orientation;
4. a representation or transformation case where continuity or homeomorphism is a load-bearing claim.

Each case SHOULD compare:

```text
ordinary E7G-T analysis
vs
informal use of neighbourhood/path/boundary language
vs
UC4 declared topological overlay
```

Record whether the module uniquely or more clearly:

- prevents an operational relation from being mislabeled as topological;
- identifies a connectedness, path, separation, continuity, or quotient issue that changes the result;
- clarifies which qualitative structure survives a transformation;
- clarifies what phase quotienting does to the declared topology;
- separates temporal carrier structure from orientation or causal direction;
- changes a reconstruction, classification, reliance limit, next move, source return, or stop decision;
- introduces unacceptable burden, arbitrariness, redundancy, or false precision.

### 19.13 Topological-overlay promotion decision

After Pilot I, assign one of the four outcomes used in §19.10.

Promotion requires all of the following:

- material value demonstrated in at least four materially different settings;
- at least two cases in which the overlay catches or clarifies a consequential structural issue not adequately exposed by ordinary E7G-T vocabulary alone;
- stable discrimination between operational adjacency and topological neighbourhood, and between operational phase boundary and topological boundary;
- mathematically correct use of continuity, homeomorphism, quotient topology, connectedness, path, and gluing claims under independent review;
- stable separation of topology from metric, order, orientation, and causation;
- at least one temporal case showing the overlay can preserve topology while separately accounting for orientation or directional semantics;
- acceptable documentation burden under at least one lightweight profile;
- explicit counterexamples showing when no topological overlay should be invoked;
- a documented decision explaining whether each candidate rule is promoted, revised, retained as informative, or rejected.

Pilot results MUST NOT be described as evidence that E7G-T is itself a new topology, that topology determines physical time direction, or that a mathematically available topology is operationally privileged. Those claims require separate justification.


### 19.14 Pilot J — Relative support under evolving evidence

Test §9.15 in at least four materially different settings, including:

1. a source-reconstruction problem with several compatible candidates;
2. a temporal-history problem with sequential evidence updates;
3. an operational classification where one phase candidate is much better supported than others;
4. a decision context where support, risk, and action thresholds must remain distinct.

Each case SHOULD compare:

```text
ordinary E7G-T admissibility/reconstruction analysis
vs
ad hoc confidence or probability language
vs
UC5 relative-support overlay
```

Record whether the module uniquely or more clearly:

- distinguishes survival in the candidate set from degree of support;
- prevents stronger support from being reported as truth or determinacy;
- prevents weaker support from being silently treated as exclusion;
- exposes the semantics and provenance of numerical or ordinal support;
- records support changes caused by new evidence separately from changes caused by reframing or model revision;
- preserves phase-spread even when one candidate dominates the support ranking;
- improves evidence acquisition, source return, decision thresholds, reliance limits, or stop conditions;
- introduces unacceptable burden, false precision, or pressure to force probabilistic semantics where none are justified.

### 19.15 Relative-support promotion decision

After Pilot J, assign one of the four outcomes used in §19.10.

Promotion requires all of the following:

- material value demonstrated in at least four materially different settings;
- at least two cases in which the module improves a consequential decision or inference beyond ordinary admissibility and reconstruction rules;
- stable separation of admissibility, support, exclusion, phase determinacy, and decision criteria;
- successful use with at least one non-probabilistic support model and one formally probabilistic model;
- no requirement that ordinary E7G-T analyses invent numerical confidence values;
- acceptable handling of provenance, evidence dependence, recalibration, model revision, and retraction;
- acceptable documentation burden under at least one lightweight profile;
- explicit counterexamples showing when the overlay should not be invoked.

Pilot results MUST NOT be described as validation of a probabilistic model merely because the overlay can carry one. Formal probability, Bayesian updating, calibration, and empirical adequacy remain responsibilities of their own declared substrates.

---

## 20. Selected Formal Neighbourhoods and Public Reference Anchors

This section is informative. References identify established neighbouring fields and stronger tools. They do not prove E7G-T.

### 20.1 Geometry and projection

- Eric W. Weisstein, “Projective Geometry,” *MathWorld — A Wolfram Resource*.  
  <https://mathworld.wolfram.com/ProjectiveGeometry.html>

E7G-T uses projection more broadly than projective geometry. Do not claim projective-geometric structure unless it is defined.

### 20.2 Category theory

- Jean-Pierre Marquis, “Category Theory,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/category-theory/>

E7G-T arrows are not automatically morphisms. Projection stacks are not automatically commutative diagrams. Bridges are not automatically functors.

### 20.3 Type theory

- Thierry Coquand, “Type Theory,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/type-theory/>

E7G-T placement is not a formal type judgement unless a type-theoretic substrate is supplied.

### 20.4 Proof assistants and Lean

- *The Lean Language Reference*.  
  <https://lean-lang.org/doc/reference/latest/>

- Lean Programming Language official site.  
  <https://lean-lang.org/>

A proof assistant supplies the checking substrate. Proof-of-Path documents movement and obligations; it does not replace checking.

### 20.5 Diagrammatic reasoning

- Sun-Joo Shin, Oliver Lemon, and Mateja Jamnik, “Diagrams and Diagrammatical Reasoning,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/diagrams/>

A diagram may support reasoning under a declared system. An informal diagram is not automatically proof.

### 20.6 Scientific models and representation

- Roman Frigg and Stephan Hartmann, “Models in Science,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/models-science/>

- “Scientific Representation,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/scientific-representation/>

Models and views may be useful without being identical to their targets.

### 20.7 Measurement

- Luca Mari, Mark Wilson, and Andrew Maul, “Measurement in Science,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/measurement-science/>

Measurement-facing claims require domain protocols, uncertainty, calibration, and evidence.

### 20.8 Information, compression, and data

- Pieter Adriaans, “Information,” *The Stanford Encyclopedia of Philosophy*.  
  <https://plato.stanford.edu/entries/information/>

Do not use information, compression, or loss as technical information-theoretic terms unless the relevant substrate is declared.

### 20.9 Translation and translation QA

- ISO 17100:2015, “Translation services — Requirements for translation services.”  
  <https://www.iso.org/standard/59149.html>

E7G-T may frame translation QA as source-tethered invariant-preserving projection and phase-sensitive transformation. It does not replace professional competence, revision, client specifications, or applicable standards.

### 20.10 Topology

- The Stacks Project Authors, “Topological Spaces,” *The Stacks Project*.  
  <https://stacks.math.columbia.edu/tag/0059>

- James R. Munkres, *Topology*, 2nd ed., Prentice Hall, 2000.

Topology supplies precise notions of open sets, neighbourhood, continuity, connectedness, quotient spaces, and homeomorphism. E7G-T uses those notions only when a topological overlay is explicitly declared. Operational adjacency, phase classification, temporal order, orientation, and causation remain separate structures unless an explicit construction relates them.

### 20.11 Source-use rule

When E7G-T refers to an established field, use one of these postures:

1. **Neighbourhood** — E7G-T stands near the field without claiming identity.
2. **Borrowed caution** — the field supplies a warning against overclaiming.
3. **Formalisation candidate** — tools from the field may support later formalisation.
4. **Application domain** — E7G-T may inspect artefacts in the field without replacing it.
5. **Stop condition** — the field has stronger tools and governs the stronger claim.

Use internal project documents to reason.

Use public sources to support public claims.

Use domain experts to review domain-facing applications.

Use formal substrates to make formal claims.

Use empirical protocols to make empirical claims.

---

## Appendix A — Compact Unified Notation

### Placement

```text
X : Dn [Θ: TDm; TR: {TRi...}] / C ; I
```

### Temporal subkernel

```text
Θ(E,C,I,QΘ)
  = ⟨Tempadm, ExtΘ, ≺Θ, ΠΘ, ≈QΘ, ΛΘ, H, KΘ, RΘ, BΘ, SΘ⟩
```

### Temporal extension

```text
θ ↑Θ n
```

### Temporal projection

```text
πΘ^{n→k}(θ) = yΘ
```

### Temporal reconstruction fibre

```text
RecΘ,π(yΘ)
  = { θ ∈ Tempadm | πΘ(θ) ≈VΘ yΘ }
```

### Temporal phase

```text
θ ≈QΘ θ′
[θ]QΘ
```

### Temporal phase-candidate set

```text
TemporalPhaseCandidatesQΘ(yΘ)
  = { [θ]QΘ | θ ∈ RecΘ,π(yΘ) }
```

### Joint configuration–temporal candidate set

```text
JointPhaseCandidatesQ,QΘ(v)
  = { ([Γ]Q,[θ]QΘ) | (Γ,θ) ∈ JointRec(v) }
```

### Candidate temporal orientation and reverse representation

```text
ℓΘ(O) ∈ J
hop = h ∘ ρ
```

where `ℓΘ(O)` is observer `O`'s admitted temporal locality and `ρ : Jop → J` reverses the declared orientation. Reverse representation does not establish time-reversal symmetry or causal reversal.

### Candidate compatible-history relevance

```text
HO(rk)
  = { h ∈ H | h remains compatible with rk
                under fixed declared conditions }
```

Under cumulative, consistent, unretracted records and fixed conditions:

```text
HO(rk+1) ⊆ HO(rk)
```

### Candidate admissible observational field

```text
FO(O; C,I,B,V,P,Θ)
  = { o | o is licensed by records available to observer O
          under C, I, B, V, P, and Θ }
```

### Candidate shared observational field

```text
FS({O1,…,On}) = ⟨Cjoint,D,U⟩
```

where `Cjoint` is jointly admissible or composable observational content, `D` is unresolved divergence, and `U` is relevant absence or indeterminacy.

### Candidate claim dependency

```text
observationRecord → observationalClaim → interpretation
```

Each arrow requires declared licensing conditions. It is not an automatic inference.

### Model boundary

```text
∂I X = B
```

### Typed incidence

```text
A ⋈C,r B
```

### Extension

```text
X ↑ n
```

### Slice

```text
SC,I^s(X)
```

### Viewing or projection

```text
πC,I^{n→k}(X) = Y
```

### Transformation

```text
τT,λ(X) = Y
```

### Transformation invariant

```text
InvT(X) = K
```

### Phase criterion

```text
Γ ≈Q Γ′
```

### Phase class

```text
[Γ]Q
```

### Admitted transition

```text
Γ —λ→ Γ′
```

### Phase-level lift

```text
τ̄([Γ]Q) = [τ(Γ)]Q
```

### Reconstruction fibre

```text
Recπ(v) = {Γ | π(Γ) ≈V v}
```

### Phase-candidate set

```text
PhaseCandidatesQ(v) = { [Γ]Q | Γ ∈ Recπ(v) }
```

### Topological overlay

```text
(X, τ)

qQ : X → X/≈Q
τQ = { U ⊆ X/≈Q | qQ⁻¹(U) ∈ τ }
```

The second expression defines the quotient topology only when `(X,τ)` and the pinned phase quotient are part of an invoked topological overlay.

### Bridge

```text
βM^{A↔B}
```

### Stop

```text
Stop(reason)
```

Notation records discipline. It does not create discipline.

---

## Appendix B — Minimal Machine-Oriented Unified Record

```yaml
E7UnifiedRecord:
  recordId:
  version:

  envelope:
    modelledEntityRef:
    semanticContextRef:
    inquiryProfileRef:
    modelBoundaryRef:
    admissibilityPredicateRef:
    validityWindow:

  configuration:
    configurationRef:
    configurationEdition:
    relationRefs: []
    interfaceRefs: []
    constraintRefs: []
    evidenceRefs: []
    unknownPositions: []

  lenses:
    dRoleProfileRef:
    temporalOrderRoleProfileRef:
    derivedTemporalRegimeProfileRef:

  temporalGeometry:
    applicability:
    temporalSubkernelRef:
    temporalCarrierRef:
    temporalBoundaryRef:
    temporalOrderRoles: []
    precedenceOrCausalityRef:
    clockOrCoordinateRefs: []
    historyRefs: []
    temporalExtensionPath:
    temporalViewingRefs: []
    temporalProjectionPath:
    temporallyPreserved: []
    temporallyHiddenOrLost: []
    temporalReconstructionFibreRef:
    temporalPhaseCriterionRef:
    temporalPhaseCriterionEdition:
    temporalPhaseCandidateRefs: []
    temporalPhaseInformationPosture:
    derivedTemporalRegimes: []
    extentStatus:
    recurrenceWitnessRefs: []
    completionCriterionRef:

    temporalOrientationPilot:
      invoked: false
      orientationRef:
      observerTemporalLocalityRef:
      directionalRelationKinds: []
      reverseRepresentationRef:
      preservedUnderReversal: []
      reversedHiddenOrUnsupported: []
      timeReversalSymmetryStatus:
      causalReversalStatus:
      finalConstraintRefs: []
      globalConsistencyRefs: []
      historyWholeRef:
      clockOrSynchronisationModelRef:
      accumulatedValidRecordRef:
      compatibleHistoryFamilyRef:
      fixedConditionRefs: []
      excludedHistoryRefs: []
      exclusionMeaning:
      correctionOrRetractionRefs: []
      interactionRuleRefs: []

  projection:
    viewingRef:
    preservedStructure: []
    hiddenOrLostStructure: []
    reconstructionFibreRef:
    sourceReturnCondition:

  phase:
    phaseCriterionRef:
    phaseCriterionEdition:
    currentPhaseRef:
    phaseCandidateRefs: []
    phaseInformationPosture:

  jointConfigurationTemporal:
    jointReconstructionFibreRef:
    jointPhaseCandidateRefs: []
    jointPhaseInformationPosture:
    structuralTemporalCommuteCheckRef:

  topologicalOverlayPilot:
    invoked: false
    topologyDeclarationRefs: []
    carrierRefs: []
    carrierKinds: []
    topologyRefs: []
    topologyConstructionRefs: []
    openSetOrBasisSemanticsRefs: []
    justificationRefs: []
    continuityClaimRefs: []
    connectednessClaimRefs: []
    separationClaimRefs: []
    pathClaimRefs: []
    quotientClaimRefs: []
    homeomorphismClaimRefs: []
    deformationClaimRefs: []
    preservedStructure: []
    hiddenOrUnrepresentedStructure: []
    metricOrderOrientationCausationSeparationCheckRef:
    admissibleUse:
    nonAdmissibleUse:
    stopOrReopenCondition:

  change:
    changeRef:
    changeKind:
    transitionRef:
    relationEffectRefs: []
    invariantEffectRefs: []
    boundaryStatus:
    representativeDependence:
    representativeOutcomeRefs: []

  support:
    supportBasis:
    supportStatus:
    evidenceRefs: []
    weakestSupportPoint:

  observationalClaimPilot:
    invoked: false
    observerRefs: []
    observationRecordRefs: []
    viewingOrMeasurementRefs: []
    observationProtocolRefs: []
    observationalClaimRefs: []
    semanticSupportRef:
    temporalSupportRef:
    spatialOrPopulationSupportRef:
    resolutionRef:
    provenanceRefs: []
    knownLimitations: []
    unknownPositions: []
    interpretationRefs: []
    assumptionRefs: []
    inferenceRuleRefs: []
    externalModelRefs: []
    sharedField:
      jointlyAdmissibleClaimRefs: []
      divergenceRefs: []
      unobservedOrIndeterminateRefs: []
      independenceConditionRefs: []
      compositionConditionRefs: []
    temporalExtensionBridgeRefs: []

  bridge:
    bridgeMode:
    bridgeRefs: []

  disposition:
    admissibleUse:
    nonAdmissibleUse:
    nextAdmissibleMove:
    stopOrReopenCondition:
```

---

## Appendix C — Closing Rule

> Read the shared core for meaning and boundaries. Use the extensional–projective route for construction and representation. Use the temporal-geometry route when events, intervals, histories, history-spaces, clocks, recurrence, unboundedness, or temporal views matter. Use the operational-phase route for inquiry-relative sameness and transition. Use the combined calculus when a structural or temporal view is used to classify or navigate operational status. When the informative observational-claim module is invoked, distinguish record, observational claim, and interpretation; preserve observer, protocol, temporal support, divergence, and unknowns; and never equate an admissible field with complete reality. When the informative topological-overlay module is invoked, declare the carrier and topology, preserve the separation between operational and topological notions, and require topological claims to meet their own mathematical conditions. Route stronger claims to stronger tools. Stop when the source, history, criterion, observation, topology, evidence, inference, or bridge cannot support the intended use.

---

End of **E7G-T Unified Geometry-Thinking Kernel v0.11-UC4**.

<!-- END PRESERVED UC5 BODY -->

# v0.12 provenance and closing anchor

| Source | Role | SHA-256 of release bytes |
|---|---|---|
| E7G-T Kernel v0.11-UC5 | Full constitutional reference body retained in Part II | `6192cfc014ea02f0e2e724dde821547bc09c06f86a0a9af80a9837bcc72e1649` |
| E7G-T Ecosystem Operating Kernel v0.1 | Independence, profile and development context; not modified | `52779f83a9c2c3f17ec5b179f73a059f24f9b0d33c385ab08c5f828931a503af` |
| E7G-T_v0.12_Executable_Examples.py | Companion code reproduced in §V.4 | `0b4b2b24de73059e47d3f3ab7865bcdf616eaf00b493063da9d6faba16f32f94` |
| E7G-T_Symbolic_Family_Realisation_Profile_v0.1.md | Optional profile reproduced in §X.16 | `3eaed99a842b7e99774b9f0caa6b9ab904de5fb0345d593ce42c9be7b7c978b4` |
| E7G-T_Symbolic_Families_v0.1.py | SF/IC prototype | `0a827d55cc95c4840ba5427e8585378b23ee6a3b00296856f192176cb4a2dca8` |
| E7G-T_Symbolic_Families_Validation_v0.1.json | Recorded symbolic-family validation | `96a76d4859376676891f966457ba3f577725463c0602ae32e7630cc8d0e82dc7` |
| E7G-T_Combined_Family-State_Profile_v0.1.md | Optional combined profile reproduced in §X.17 | `a3e5b9096c7243066ab3367df214e3724a3de2063044f2806e49d0ec7bfe42d5` |
| E7G-T_Combined_Family_State_v0.1.py | CFS/CG3 bounded executable model reproduced in Appendix VI | `ed6ba76f6638c859e65d9908ecd4ef2539cd1348df8249471ca706a51b94d542` |
| E7G-T_Combined_Family-State_Validation_v0.1.json | Recorded combined-profile validation | `84686137b3fc6c084eb28feb81288c915165363d06d244b800b14b11aa63da71` |

This document adds Part I and Appendices V–VI and records the inherited metadata separately. Revision CFS1 retains the SF1 symbolic-family work and adds the optional combined family-state profile in §X.17, its CG3 prototype and its validation companion. The 2026-09-07 v0.12 draft remains preceding development material. The UC5 body between the preservation markers is unchanged from the repository predecessor. No changes have been made to that predecessor or the ecosystem file. All new worked configurations are constructed examples; this specification includes no private collaborator implementation or experimental data.

**Working anchor:** construct entities with declared boundaries; retain the dependence among their alternatives; extend through typed interfaces; distinguish viewing from changing the state; promote whole constructions explicitly; and test every claimed abstraction law on its actual domain.

End of **E7G-T Kernel v0.12-experimental — Executable Extension and Composition**.
