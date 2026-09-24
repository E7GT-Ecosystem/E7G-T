Warning: truncated output (original token count: 9204)
Total output lines: 841

import E7CS1StrictCore
import E7CS1FG3Single
import E7CS1FG3Rows
import E7CS1ExactCollect
import E7CS1FG3Codec
import E7CS1RowsCollect
import E7CS1TagRegistry
import E7CB2Sequence
import E7CB2FiniteBridge
import E7CEECQTwoStageBridge
import E7CEECQTwoStageAllInput
import E7CEECQTwoStageOperational

/-!
E7C/0.1 WP4 bounded Lean core extension.

This file extends the accepted feasibility spike with a deliberately small
encoding of the variable, strict-map, source-preserving-view and restriction
fragment. It is not the complete E7C calculus and does not establish adequacy
of the encoding to the external WP2/WP3-S specifications.
-/

namespace E7CLeanCore

inductive CoreType where
  | config
  | familyConfig
  | viewConfig
  | outcomeConfig
  | outcomeFamilyConfig
  deriving DecidableEq, Repr

inductive EffectAtom where
  | evidence (declaration : Nat)
  | partiality (declaration : Nat)
  | inquiry (declaration : Nat)
  | alternatives (declaration : Nat)
  deriving DecidableEq, Repr

/- WP2 rows are extensional sets of atoms. All rows produced by typing are
finite unions of constructor atoms; order and multiplicity are absent here. -/
abbrev EffectRow := EffectAtom → Prop

def emptyEffect : EffectRow := fun _ => False
def effectAtoms (atoms : List EffectAtom) : EffectRow := fun atom => atom ∈ atoms
def effectUnion (left right : EffectRow) : EffectRow :=
  fun atom => left atom ∨ right atom

structure LedgerEntry where
  atom : EffectAtom
  detail : Nat
  deriving DecidableEq, Repr

abbrev Ledger := List LedgerEntry

def ledgerEntry (atom : EffectAtom) : LedgerEntry :=
  { atom := atom, detail := 0 }

inductive Term where
  | var (name : Nat)
  | strictApp (mapName : Nat) (argument : Term)
  | sourceView (viewName : Nat) (argument : Term)
  | restrict (policyName : Nat) (argument : Term)
  deriving DecidableEq, Repr

def staticTrace : Term → List EffectAtom
  | .var _ => []
  | .strictApp mapName argument =>
      staticTrace argument ++ [.evidence mapName, .partiality mapName]
  | .sourceView viewName argument =>
      staticTrace argument ++ [.inquiry viewName, .alternatives viewName]
  | .restrict policyName argument =>
      staticTrace argument ++ [.alternatives policyName]

def staticEffects : Term → EffectRow
  | .var _ => emptyEffect
  | .strictApp mapName argument =>
      effectUnion (staticEffects argument)
        (effectAtoms [.evidence mapName, .partiality mapName])
  | .sourceView viewName argument =>
      effectUnion (staticEffects argument)
        (effectAtoms [.inquiry viewName, .alternatives viewName])
  | .restrict policyName argument =>
      effectUnion (staticEffects argument) (effectAtoms [.alternatives policyName])

abbrev Context := List (Nat × CoreType)

structure Declarations where
  strictMaps : List Nat
  sourceViews : List Nat
  restrictions : List Nat
  deriving DecidableEq, Repr

def PairNamesUnique {α : Type} (entries : List (Nat × α)) : Prop :=
  (entries.map (fun entry => entry.1)).Nodup

def lookupType : Context → Nat → Option CoreType
  | [], _ => none
  | (boundName, type) :: rest, name =>
      if name = boundName then some type else lookupType rest name

inductive HasType (declarations : Declarations) (context : Context) :
    Term → CoreType → EffectRow → Prop where
  | var (found : lookupType context name = some type) :
      HasType declarations context (.var name) type emptyEffect
  | strictApp
      (declared : mapName ∈ declarations.strictMaps)
      (argumentType : HasType declarations context argument .config argumentEffects) :
      HasType declarations context (.strictApp mapName argument) .outcomeConfig
        (effectUnion argumentEffects
          (effectAtoms [.evidence mapName, .partiality mapName]))
  | sourceView
      (declared : viewName ∈ declarations.sourceViews)
      (argumentType : HasType declarations context argument .config argumentEffects) :
      HasType declarations context (.sourceView viewName argument) .viewConfig
        (effectUnion argumentEffects
          (effectAtoms [.inquiry viewName, .alternatives viewName]))
  | restrict
      (declared : policyName ∈ declarations.restrictions)
      (argumentType :
        HasType declarations context argument .familyConfig argumentEffects) :
      HasType declarations context (.restrict policyName argument)
        .outcomeFamilyConfig
          (effectUnion argumentEffects (effectAtoms [.alternatives policyName]))

theorem typing_effects_are_static
    (termType : HasType declarations context term type effects) :
    effects = staticEffects term := by
  induction termType with
  | var => rfl
  | strictApp _ _ inductionHypothesis =>
      simp only [staticEffects]
      rw [inductionHypothesis]
  | sourceView _ _ inductionHypothesis =>
      simp only [staticEffects]
      rw [inductionHypothesis]
  | restrict _ _ inductionHypothesis =>
      simp only [staticEffects]
      rw [inductionHypothesis]

inductive Value where
  | config (code : Nat)
  | familyConfig (members : List Nat)
  | sourceView (representation : Nat) (sourceReturn : Nat)
  | text (code : Nat)
  deriving DecidableEq, Repr

inductive Outcome where
  | success (value : Value)
  | domainError
  | unsupported (capability : Nat)
  deriving DecidableEq, Repr

abbrev EvaluationResult := Outcome × Ledger

inductive Binding where
  | plain (value : Value)
  | terminal (outcome : Outcome)
  deriving DecidableEq, Repr

abbrev Environment := List (Nat × Binding)

def lookupBinding : Environment → Nat → Option Binding
  | [], _ => none
  | (boundName, binding) :: rest, name =>
      if name = boundName then some binding else lookupBinding rest name

structure StrictRow where
  input : Nat
  output : Nat
  deriving DecidableEq, Repr

abbrev StrictTable := List StrictRow

def lookupStrictRow : StrictTable → Nat → Option Nat
  | [], _ => none
  | row :: rest, input =>
      if input = row.input then some row.output else lookupStrictRow rest input

structure StrictEntry where
  name : Nat
  table : StrictTable
  deriving DecidableEq, Repr

structure ViewRow where
  input : Nat
  representation : Nat
  deriving DecidableEq, Repr

abbrev ViewTable := List ViewRow

def lookupViewRow : ViewTable → Nat → Option Nat
  | [], _ => none
  | row :: rest, input =>
      if input = row.input then some row.representation else lookupViewRow rest input

structure ViewEntry where
  name : Nat
  table : ViewTable
  deriving DecidableEq, Repr

structure RestrictionEntry where
  name : Nat
  retained : List Nat
  deriving DecidableEq, Repr

structure Interpretation where
  strictMaps : List StrictEntry
  sourceViews : List ViewEntry
  restrictions : List RestrictionEntry
  deriving DecidableEq, Repr

def lookupStrict : List StrictEntry → Nat → Option StrictTable
  | [], _ => none
  | entry :: rest, name =>
      if name = entry.name then some entry.table else lookupStrict rest name

def lookupView : List ViewEntry → Nat → Option ViewTable
  | [], _ => none
  | entry :: rest, name =>
      if name = entry.name then some entry.table else lookupView rest name

def lookupRestriction : List RestrictionEntry → Nat → Option (List Nat)
  | [], _ => none
  | entry :: rest, name =>
      if name = entry.name then some entry.retained else lookupRestriction rest name

def successCarrier : CoreType → CoreType
  | .outcomeConfig => .config
  | .outcomeFamilyConfig => .familyConfig
  | type => type

def ValueHasType : Value → CoreType → Prop
  | .config _, .config => True
  | .familyConfig _, .familyConfig => True
  | .sourceView _ _, .viewConfig => True
  | _, _ => False

def BindingHasType : Binding → CoreType → Prop
  | .plain value, type => ValueHasType value type
  | .terminal (.success value), .outcomeConfig => ValueHasType value .config
  | .terminal (.success value), .outcomeFamilyConfig =>
      ValueHasType value .familyConfig
  | .terminal .domainError, .outcomeConfig => True
  | .terminal .domainError, .outcomeFamilyConfig => True
  | .terminal (.unsupported _), .outcomeConfig => True
  | .terminal (.unsupported _), .outcomeFamilyConfig => True
  | _, _ => False

def StrictTableWellFormed (table : StrictTable) : Prop :=
  (table.map StrictRow.input).Nodup

def ViewTableWellFormed (table : ViewTable) : Prop :=
  (table.map ViewRow.input).Nodup

structure EnvironmentWellFormed (context : Context) (environment : Environment) : Prop where
  contextNamesUnique : PairNamesUnique context
  environmentNamesUnique : PairNamesUnique environment
  complete : ∀ name type,
    lookupType context name = some type →
      ∃ binding,
        lookupBinding environment name = some binding ∧ BindingHasType binding type
  exact : ∀ name binding,
    lookupBinding environment name = some binding →
      ∃ type,
        lookupType context name = some type ∧ BindingHasType binding type

structure InterpretationWellFormed
    (declarations : Declarations) (interpretation : Interpretation) : Prop where
  strictDeclarationNamesUnique : declarations.strictMaps.Nodup
  viewDeclarationNamesUnique : declarations.sourceViews.Nodup
  restrictionDeclarationNamesUnique : declarations.restrictions.Nodup
  strictNamesUnique : (interpretation.strictMaps.map StrictEntry.name).Nodup
  viewNamesUnique : (interpretation.sourceViews.map ViewEntry.name).Nodup
  restrictionNamesUnique :
    (interpretation.restrictions.map RestrictionEntry.name).Nodup
  strictComplete : ∀ name,
    name ∈ declarations.strictMaps →
      ∃ table,
        lookupStrict interpretation.strictMaps name = some table ∧
        StrictTableWellFormed table
  viewComplete : ∀ name,
    name ∈ declarations.sourceViews →
      ∃ table,
        lookupView interpretation.sourceViews name = some table ∧
        ViewTableWellFormed table
  restrictionComplete : ∀ name,
    name ∈ declarations.restrictions →
      ∃ retained,
        lookupRestriction interpretation.restrictions name = some retained ∧
        retained.Nodup
  strictExact : ∀ name table,
    lookupStrict interpretation.strictMaps name = some table →
      name ∈ declarations.strictMaps ∧ StrictTableWellFormed table
  viewExact : ∀ name table,
    lookupView interpretation.sourceViews name = some table →
      name ∈ declarations.sourceViews ∧ ViewTableWellFormed table
  restrictionExact : ∀ name retained,
    lookupRestriction interpretation.restrictions name = some retained →
      name ∈ declarations.restrictions ∧ retained.Nodup

def evaluateBinding : Binding → Outcome
  | .plain value => .success value
  | .terminal outcome => outcome

def evaluateVariable (environment : Environment) (name : Nat) : EvaluationResult :=
  match lookupBinding environment name with
  | some binding => (evaluateBinding binding, [])
  | none => (.unsupported name, [])

def applyStrict (table : StrictTable) : Value → Outcome
  | .config input =>
      match lookupStrictRow table input with
      | some output => .success (.config output)
      | none => .domainError
  | _ => .domainError

def applySourceView (table : ViewTable) (name : Nat) : Value → Outcome
  | .config input =>
      match lookupViewRow table input with
      | some representation => .success (.sourceView representation input)
      | none => .unsupported name
  | _ => .domainError

def retainMembers : List Nat → List Nat → List Nat
  | [], _ => []
  | member :: rest, retained =>
      if retained.contains member then
        member :: retainMembers rest retained
      else
        retainMembers rest retained

def applyRestriction (retained : List Nat) : Value → Outcome
  | .familyConfig members =>
      .success (.familyConfig (retainMembers members retained))
  | _ => .domainError

def finishWith (child : EvaluationResult) (entries : Ledger)
    (operation : Value → Outcome) : EvaluationResult :=
  match child with
  | (.success value, ledger) => (operation value, ledger ++ entries)
  | (.domainError, ledger) => (.domainError, ledger)
  | (.unsupported capability, ledger) => (.unsupported capability, ledger)

def strictOperation (interpretation : Interpretation) (name : Nat) : Value → Outcome :=
  fun value =>
    match lookupStrict interpretation.strictMaps name with
    | some table => applyStrict table value
    | none => .unsupported name

def viewOperation (interpretation : Interpretation) (name : Nat) : Value → Outcome :=
  fun value =>
    match lookupView interpretation.sourceViews name with
    | some table => applySourceView table name value
    | none => .unsupported name

def restrictionOperation
    (interpretation : Interpretation) (name : Nat) : Value → Outcome :=
  fun value =>
    match lookupRestriction interpretation.restrictions name with
    | some retained => applyRestriction retained value
    | none => .unsupported name

def evaluate (environment : Environment) (interpretation : Interpretation) :
    Term → EvaluationResult
  | .var name => evaluateVariable environment name
  | .strictApp mapName argument =>
      finishWith (evaluate environment interpretation argument)
        [ledgerEntry (.evidence mapName), ledgerEntry (.partiality mapName)]
        (strictOperation interpretation mapName)
  | .sourceView viewName argument =>
      finishWith (evaluate environment interpretation argument)
        [ledgerEntry (.inquiry viewName), ledgerEntry (.alternatives viewName)]
        (viewOperation interpretation viewName)
  | .restrict policyName argument =>
      finishWith (evaluate environment interpretation argument)
        [ledgerEntry (.alternatives policyName)]
        (restrictionOperation interpretation policyName)

/- The constructors below are the Lean rule encoding reviewed against the
external WP3-S variable, strict-map, source-preserving-view and restriction
rules. The later adequacy theorem must relate this encoding to a separately
formalized external judgement; it is not claimed here. -/
inductive SpecEval (environment : Environment) (interpretation : Interpretation) :
    Term → Outcome → Ledger → Prop where
  | wp3Variable :
      SpecEval environment interpretation (.var name)
        (evaluateVariable environment name).1 (evaluateVariable environment name).2
  | wp3Strict
      (argumentEval : SpecEval environment interpretation argument childOutcome childLedger) :
      SpecEval environment interpretation (.strictApp mapName argument)
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.evidence mapName), ledgerEntry (.partiality mapName)]
          (strictOperation interpretation mapName)).1
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.evidence mapName), ledgerEntry (.partiality mapName)]
          (strictOperation interpretation mapName)).2
  | wp3SourceView
      (argumentEval : SpecEval environment interpretation argument childOutcome childLedger) :
      SpecEval environment interpretation (.sourceView viewName argument)
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.inquiry viewName), ledgerEntry (.alternatives viewName)]
          (viewOperation interpretation viewName)).1
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.inquiry viewName), ledgerEntry (.alternatives viewName)]
          (viewOperation interpretation viewName)).2
  | wp3Restriction
      (argumentEval : SpecEval environment interpretation argument childOutcome childLedger) :
      SpecEval environment interpretation (.restrict policyName argument)
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.alternatives policyName)]
          (restrictionOperation interpretation policyName)).1
        (finishWith (childOutcome, childLedger)
          [ledgerEntry (.alternatives policyName)]
          (restrictionOperation interpretation policyName)).2

theorem spec_eval_matches_function
    (derivation : SpecEval environment interpretation term outcome ledger) :
    evaluate environment interpretation term = (outcome, ledger) := by
  induction derivation with
  | wp3Variable => rfl
  | wp3Strict argumentEval inductionHypothesis =>
      simp [evaluate, inductionHypothesis]
  | wp3SourceView argumentEval inductionHypothesis =>
      simp [evaluate, inductionHypothesis]
  | wp3Restriction argumentEval inductionHypothesis =>
      simp [evaluate, inductionHypothesis]

theorem evaluate_has_spec_derivation (term : Term) :
    SpecEval environment interpretation term
      (evaluate environment interpretation term).1
      (evaluate environment interpretation term).2 := by
  induction term with
  | var name => exact SpecEval.wp3Variable
  | strictApp mapName argument inductionHypothesis =>
      simpa [evaluate] using SpecEval.wp3Strict inductionHypothesis
  | sourceView viewName argument inductionHypothesis =>
      simpa [evaluate] using SpecEval.wp3SourceView inductionHypothesis
  | restrict policyName argument inductionHypothesis =>
      simpa [evaluate] using SpecEval.wp3Restriction inductionHypothesis

theorem spec_evaluation_deterministic
    (first : SpecEval environment interpretation term firstOutcome firstLedger)
    (second : SpecEval environment interpretation term secondOutcome secondLedger) :
    firstOutcome = secondOutcome ∧ firstLedger = secondLedger := by
  have firstResult := spec_eval_matches_function first
  have secondResult := spec_eval_matches_function second
  have pairEquality : (firstOutcome, firstLedger) = (secondOutcome, secondLedger) :=
    firstResult.symm.trans secondResult
  exact ⟨congrArg Prod.fst pairEquality, congrArg Prod.snd pairEquality⟩

theorem evaluateBinding_success_has_type
    (bindingType : BindingHasType binding type)
    (successful : evaluateBinding binding = .success output) :
    ValueHasType output (successCarrier type) := by
  cases binding <;> cases type <;>
    simp_all [BindingHasType, evaluateBinding, successCarrier, ValueHasType]

theorem successful_type_preservation
    (termType : HasType declarations context term type effec…204 tokens truncated…ound, _⟩ :=
        interpretationType.strictComplete mapName declared
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
          | success input =>
              have inputType : ValueHasType input .config := by
                apply inductionHypothesis
                simp [argumentResult]
              cases input with
              | config code =>
                  cases rowFound : lookupStrictRow table code with
                  | none =>
                      simp [evaluate, finishWith, argumentResult, strictOperation,
                        tableFound, applyStrict, rowFound] at successful
                  | some mapped =>
                      have outputIsConfig : output = .config mapped := by
                        simpa [evaluate, finishWith, argumentResult, strictOperation,
                          tableFound, applyStrict, rowFound] using successful.symm
                      cases outputIsConfig
                      trivial
              | familyConfig members => simp [ValueHasType] at inputType
              | sourceView representation sourceReturn => simp [ValueHasType] at inputType
              | text content => simp [ValueHasType] at inputType
  | @sourceView viewName argument argumentEffects declared argumentType inductionHypothesis =>
      obtain ⟨table, tableFound, _⟩ :=
        interpretationType.viewComplete viewName declared
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
          | success input =>
              have inputType : ValueHasType input .config := by
                apply inductionHypothesis
                simp [argumentResult]
              cases input with
              | config code =>
                  cases rowFound : lookupViewRow table code with
                  | none =>
                      simp [evaluate, finishWith, argumentResult, viewOperation,
                        tableFound, applySourceView, rowFound] at successful
                  | some representation =>
                      have outputIsView : output = .sourceView representation code := by
                        simpa [evaluate, finishWith, argumentResult, viewOperation,
                          tableFound, applySourceView, rowFound] using successful.symm
                      cases outputIsView
                      trivial
              | familyConfig members => simp [ValueHasType] at inputType
              | sourceView representation sourceReturn => simp [ValueHasType] at inputType
              | text content => simp [ValueHasType] at inputType
  | @restrict policyName argument argumentEffects declared argumentType inductionHypothesis =>
      obtain ⟨retained, retainedFound, _⟩ :=
        interpretationType.restrictionComplete policyName declared
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
          | success input =>
              have inputType : ValueHasType input .familyConfig := by
                apply inductionHypothesis
                simp [argumentResult]
              cases input with
              | familyConfig members =>
                  have outputIsFamily : output =
                      .familyConfig (retainMembers members retained) := by
                    simpa [evaluate, finishWith, argumentResult, restrictionOperation,
                      retainedFound, applyRestriction] using successful.symm
                  cases outputIsFamily
                  trivial
              | config code => simp [ValueHasType] at inputType
              | sourceView representation sourceReturn => simp [ValueHasType] at inputType
              | text content => simp [ValueHasType] at inputType

def LedgerBounded (ledger : Ledger) (effects : EffectRow) : Prop :=
  ∀ entry, entry ∈ ledger → effects entry.atom

def TraceBounded (ledger : Ledger) (trace : List EffectAtom) : Prop :=
  ∀ entry, entry ∈ ledger → entry.atom ∈ trace

def ledgerAtoms : Ledger → List EffectAtom
  | [] => []
  | entry :: rest => entry.atom :: ledgerAtoms rest

theorem ledgerAtoms_append (left right : Ledger) :
    ledgerAtoms (left ++ right) = ledgerAtoms left ++ ledgerAtoms right := by
  induction left with
  | nil => rfl
  | cons entry rest inductionHypothesis =>
      simp only [List.cons_append, ledgerAtoms, inductionHypothesis]

/- The trace is syntax-derived and ordered; it is distinct from the WP2 set. -/
def LedgerOrderPreserved (ledger : Ledger) (trace : List EffectAtom) : Prop :=
  ∃ remaining, trace = ledgerAtoms ledger ++ remaining

theorem ledgerOrder_weaken
    (ordered : LedgerOrderPreserved ledger effects) :
    LedgerOrderPreserved ledger (effects ++ additionalEffects) := by
  obtain ⟨remaining, equality⟩ := ordered
  refine ⟨remaining ++ additionalEffects, ?_⟩
  simp only [equality, List.append_assoc]

theorem successful_ledger_exact
    (term : Term)
    (successful : (evaluate environment interpretation term).1 = .success output) :
    ledgerAtoms (evaluate environment interpretation term).2 = staticTrace term := by
  induction term generalizing output with
  | var name =>
      simp only [evaluate, evaluateVariable]
      split <;> rfl
  | strictApp mapName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
  | sourceView viewName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
  | restrict policyName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful

theorem ordered_ledger_preservation (term : Term) :
    LedgerOrderPreserved (evaluate environment interpretation term).2
      (staticTrace term) := by
  induction term with
  | var name =>
      simp only [evaluate, evaluateVariable, staticTrace]
      split <;> exact ⟨[], rfl⟩
  | strictApp mapName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argument (output := input) (by simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.evidence mapName, .partiality mapName])
                inductionHypothesis
          | unsupported capability =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.evidence mapName, .partiality mapName])
                inductionHypothesis
  | sourceView viewName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argument (output := input) (by simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.inquiry viewName, .alternatives viewName])
                inductionHypothesis
          | unsupported capability =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.inquiry viewName, .alternatives viewName])
                inductionHypothesis
  | restrict policyName argument inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argument (output := input) (by simp [argumentResult])
              rw [argumentResult] at childExact
              simp only [evaluate, argumentResult, finishWith, staticTrace,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact]
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.alternatives policyName]) inductionHypothesis
          | unsupported capability =>
              rw [argumentResult] at inductionHypothesis
              simp only [evaluate, argumentResult, finishWith, staticTrace]
              exact ledgerOrder_weaken
                (additionalEffects := [.alternatives policyName]) inductionHypothesis

theorem ledgerAtom_is_emitted (member : entry ∈ ledger) :
    entry.atom ∈ ledgerAtoms ledger := by
  induction ledger with
  | nil => cases member
  | cons head tail inductionHypothesis =>
      simp only [ledgerAtoms, List.mem_cons] at member ⊢
      cases member with
      | inl equality =>
          subst entry
          exact Or.inl rfl
      | inr tailMember => exact Or.inr (inductionHypothesis tailMember)

theorem ordered_ledger_is_bounded
    (ordered : LedgerOrderPreserved ledger effects) :
    TraceBounded ledger effects := by
  obtain ⟨remaining, equality⟩ := ordered
  intro entry member
  rw [equality]
  simp only [List.mem_append]
  exact Or.inl (ledgerAtom_is_emitted member)

theorem ledger_effect_soundness (term : Term) :
    TraceBounded (evaluate environment interpretation term).2
      (staticTrace term) :=
  ordered_ledger_is_bounded (ordered_ledger_preservation term)

theorem trace_member_is_static (term : Term) (atom : EffectAtom)
    (member : atom ∈ staticTrace term) : staticEffects term atom := by
  induction term with
  | var name => simp [staticTrace] at member
  | strictApp mapName argument inductionHypothesis =>
      simp only [staticTrace, List.mem_append] at member
      simp only [staticEffects, effectUnion, effectAtoms]
      cases member with
      | inl child => exact Or.inl (inductionHypothesis child)
      | inr own => exact Or.inr own
  | sourceView viewName argument inductionHypothesis =>
      simp only [staticTrace, List.mem_append] at member
      simp only [staticEffects, effectUnion, effectAtoms]
      cases member with
      | inl child => exact Or.inl (inductionHypothesis child)
      | inr own => exact Or.inr own
  | restrict policyName argument inductionHypothesis =>
      simp only [staticTrace, List.mem_append] at member
      simp only [staticEffects, effectUnion, effectAtoms]
      cases member with
      | inl child => exact Or.inl (inductionHypothesis child)
      | inr own => exact Or.inr own

theorem typed_ordered_ledger_preservation
    (termType : HasType declarations context term type effects) :
    LedgerOrderPreserved (evaluate environment interpretation term).2
      (staticTrace term) := by
  exact ordered_ledger_preservation term

theorem typed_ledger_effect_soundness
    (termType : HasType declarations context term type effects) :
    LedgerBounded (evaluate environment interpretation term).2 effects := by
  rw [typing_effects_are_static termType]
  intro entry emitted
  exact trace_member_is_static term entry.atom (ledger_effect_soundness term entry emitted)

theorem outcome_variable_is_direct :
    evaluate [(0, .terminal .domainError)]
      { strictMaps := [], sourceViews := [], restrictions := [] } (.var 0) =
      (.domainError, []) := by
  rfl

theorem missing_strict_interpretation_is_unsupported_with_ordered_ledger :
    evaluate [(0, .plain (.config 1))]
      { strictMaps := [], sourceViews := [], restrictions := [] }
      (.strictApp 1 (.var 0)) =
      (.unsupported 1,
        [ledgerEntry (.evidence 1), ledgerEntry (.partiality 1)]) := by
  rfl

theorem source_view_ledger_order_is_exact :
    let interpretation : Interpretation :=
      { strictMaps := [],
        sourceViews := [{ name := 2, table := [{ input := 1, representation := 7 }] }],
        restrictions := [] }
    evaluate [(0, .plain (.config 1))] interpretation
      (.sourceView 2 (.var 0)) =
      (.success (.sourceView 7 1),
        [ledgerEntry (.inquiry 2), ledgerEntry (.alternatives 2)]) := by
  rfl

theorem restriction_ledger_and_result_are_exact :
    let interpretation : Interpretation :=
      { strictMaps := [], sourceViews := [],
        restrictions := [{ name := 3, retained := [1, 3] }] }
    evaluate [(4, .plain (.familyConfig [1, 2, 3]))] interpretation
      (.restrict 3 (.var 4)) =
      (.success (.familyConfig [1, 3]), [ledgerEntry (.alternatives 3)]) := by
  rfl

/- Internal evaluator invariant only: sourceView consumes an Outcome Config here,
which is rejected by HasType and is not an admitted WP3-S term. -/
theorem raw_prior_failure_preserves_ledger_prefix :
    let interpretation : Interpretation :=
      { strictMaps := [{ name := 1, table := [] }],
        sourceViews := [], restrictions := [] }
    evaluate [(0, .plain (.config 1))] interpretation
      (.sourceView 2 (.strictApp 1 (.var 0))) =
      (.domainError,
        [ledgerEntry (.evidence 1), ledgerEntry (.partiality 1)]) := by
  rfl

theorem typed_strict_domain_failure_has_ledger_prefix :
    let declarations : Declarations :=
      { strictMaps := [1], sourceViews := [], restrictions := [] }
    let context : Context := [(0, .config)]
    HasType declarations context (.strictApp 1 (.var 0)) .outcomeConfig
      (effectUnion emptyEffect (effectAtoms [.evidence 1, .partiality 1])) ∧
    evaluate [(0, .plain (.config 1))]
      { strictMaps := [{ name := 1, table := [] }],
        sourceViews := [], restrictions := [] } (.strictApp 1 (.var 0)) =
      (.domainError, [ledgerEntry (.evidence 1), ledgerEntry (.partiality 1)]) := by
  constructor
  · apply HasType.strictApp
    · simp
    · apply HasType.var
      simp [lookupType]
  · rfl

end E7CLeanCore
