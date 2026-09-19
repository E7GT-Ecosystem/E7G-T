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

abbrev EffectRow := List EffectAtom

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
      HasType declarations context (.var name) type []
  | strictApp
      (declared : mapName ∈ declarations.strictMaps)
      (argumentType : HasType declarations context argument .config argumentEffects) :
      HasType declarations context (.strictApp mapName argument) .outcomeConfig
        (argumentEffects ++ [.evidence mapName, .partiality mapName])
  | sourceView
      (declared : viewName ∈ declarations.sourceViews)
      (argumentType : HasType declarations context argument .config argumentEffects) :
      HasType declarations context (.sourceView viewName argument) .viewConfig
        (argumentEffects ++ [.inquiry viewName, .alternatives viewName])
  | restrict
      (declared : policyName ∈ declarations.restrictions)
      (argumentType :
        HasType declarations context argument .familyConfig argumentEffects) :
      HasType declarations context (.restrict policyName argument)
        .outcomeFamilyConfig (argumentEffects ++ [.alternatives policyName])

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
    (termType : HasType declarations context term type effects)
    (environmentType : EnvironmentWellFormed context environment)
    (interpretationType : InterpretationWellFormed declarations interpretation)
    (successful : (evaluate environment interpretation term).1 = .success output) :
    ValueHasType output (successCarrier type) := by
  induction termType generalizing output with
  | @var name type found =>
      obtain ⟨binding, bindingFound, bindingType⟩ :=
        environmentType.complete name type found
      have bindingSuccessful : evaluateBinding binding = .success output := by
        simpa [evaluate, evaluateVariable, bindingFound] using successful
      exact evaluateBinding_success_has_type bindingType bindingSuccessful
  | @strictApp mapName argument argumentEffects declared argumentType inductionHypothesis =>
      obtain ⟨table, tableFound, _⟩ :=
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
  ∀ entry, entry ∈ ledger → entry.atom ∈ effects

def ledgerAtoms : Ledger → EffectRow
  | [] => []
  | entry :: rest => entry.atom :: ledgerAtoms rest

theorem ledgerAtoms_append (left right : Ledger) :
    ledgerAtoms (left ++ right) = ledgerAtoms left ++ ledgerAtoms right := by
  induction left with
  | nil => rfl
  | cons entry rest inductionHypothesis =>
      simp only [List.cons_append, ledgerAtoms, inductionHypothesis]

/- This is the ordered counterpart of `LedgerBounded`: the runtime atoms must
be an initial segment of the statically ordered fragment row. The external WP2
row remains a set; the list order here records the WP3 constructor order used
by this bounded projection. -/
def LedgerOrderPreserved (ledger : Ledger) (effects : EffectRow) : Prop :=
  ∃ remaining, effects = ledgerAtoms ledger ++ remaining

theorem ledgerBounded_weaken
    (bounded : LedgerBounded ledger effects) :
    LedgerBounded ledger (effects ++ additionalEffects) := by
  intro entry member
  simp only [List.mem_append]
  exact Or.inl (bounded entry member)

theorem ledgerBounded_append
    (leftBounded : LedgerBounded leftLedger leftEffects)
    (rightBounded : LedgerBounded rightLedger rightEffects) :
    LedgerBounded (leftLedger ++ rightLedger) (leftEffects ++ rightEffects) := by
  intro entry member
  simp only [List.mem_append] at member ⊢
  cases member with
  | inl leftMember => exact Or.inl (leftBounded entry leftMember)
  | inr rightMember => exact Or.inr (rightBounded entry rightMember)

theorem ledgerOrder_weaken
    (ordered : LedgerOrderPreserved ledger effects) :
    LedgerOrderPreserved ledger (effects ++ additionalEffects) := by
  obtain ⟨remaining, equality⟩ := ordered
  refine ⟨remaining ++ additionalEffects, ?_⟩
  simp only [equality, List.append_assoc]

theorem successful_ledger_exact
    (termType : HasType declarations context term type effects)
    (successful : (evaluate environment interpretation term).1 = .success output) :
    ledgerAtoms (evaluate environment interpretation term).2 = effects := by
  induction termType generalizing output with
  | @var name type found =>
      simp only [evaluate, evaluateVariable]
      split <;> rfl
  | @strictApp mapName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith]
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
  | @sourceView viewName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith]
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful
  | @restrict policyName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := inductionHypothesis (output := input) (by
                simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith]
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry]
          | domainError => simp [evaluate, finishWith, argumentResult] at successful
          | unsupported capability =>
              simp [evaluate, finishWith, argumentResult] at successful

theorem ordered_ledger_preservation
    (termType : HasType declarations context term type effects) :
    LedgerOrderPreserved (evaluate environment interpretation term).2 effects := by
  induction termType with
  | @var name type found =>
      simp only [evaluate, evaluateVariable]
      split <;> exact ⟨[], rfl⟩
  | @strictApp mapName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argumentType (output := input) (by simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.evidence mapName, .partiality mapName])
                  childOrdered)
          | unsupported capability =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.evidence mapName, .partiality mapName])
                  childOrdered)
  | @sourceView viewName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argumentType (output := input) (by simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.inquiry viewName, .alternatives viewName])
                  childOrdered)
          | unsupported capability =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.inquiry viewName, .alternatives viewName])
                  childOrdered)
  | @restrict policyName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          cases argumentOutcome with
          | success input =>
              have childExact := successful_ledger_exact
                (environment := environment) (interpretation := interpretation)
                argumentType (output := input) (by simp [argumentResult])
              have childExact' : ledgerAtoms argumentLedger = argumentEffects := by
                rw [argumentResult] at childExact
                exact childExact
              simp only [evaluate, argumentResult, finishWith,
                LedgerOrderPreserved]
              refine ⟨[], ?_⟩
              rw [ledgerAtoms_append, childExact']
              simp only [ledgerAtoms, ledgerEntry, List.append_nil]
          | domainError =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.alternatives policyName]) childOrdered)
          | unsupported capability =>
              have childOrdered : LedgerOrderPreserved argumentLedger argumentEffects := by
                simpa [argumentResult] using inductionHypothesis
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerOrder_weaken
                  (additionalEffects := [.alternatives policyName]) childOrdered)

theorem ledger_effect_soundness
    (termType : HasType declarations context term type effects) :
    LedgerBounded (evaluate environment interpretation term).2 effects := by
  induction termType with
  | @var name type found =>
      simp only [evaluate, evaluateVariable]
      split <;> simp [LedgerBounded]
  | @strictApp mapName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          have childBounded : LedgerBounded argumentLedger argumentEffects := by
            simpa [argumentResult] using inductionHypothesis
          cases argumentOutcome with
          | success input =>
              simpa [evaluate, finishWith, argumentResult] using
                ledgerBounded_append childBounded
                  (show LedgerBounded
                    [ledgerEntry (.evidence mapName), ledgerEntry (.partiality mapName)]
                    [.evidence mapName, .partiality mapName] by
                      simp [LedgerBounded, ledgerEntry])
          | domainError =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.evidence mapName, .partiality mapName]) childBounded)
          | unsupported capability =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.evidence mapName, .partiality mapName]) childBounded)
  | @sourceView viewName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          have childBounded : LedgerBounded argumentLedger argumentEffects := by
            simpa [argumentResult] using inductionHypothesis
          cases argumentOutcome with
          | success input =>
              simpa [evaluate, finishWith, argumentResult] using
                ledgerBounded_append childBounded
                  (show LedgerBounded
                    [ledgerEntry (.inquiry viewName), ledgerEntry (.alternatives viewName)]
                    [.inquiry viewName, .alternatives viewName] by
                      simp [LedgerBounded, ledgerEntry])
          | domainError =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.inquiry viewName, .alternatives viewName]) childBounded)
          | unsupported capability =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.inquiry viewName, .alternatives viewName]) childBounded)
  | @restrict policyName argument argumentEffects declared argumentType inductionHypothesis =>
      cases argumentResult : evaluate environment interpretation argument with
      | mk argumentOutcome argumentLedger =>
          have childBounded : LedgerBounded argumentLedger argumentEffects := by
            simpa [argumentResult] using inductionHypothesis
          cases argumentOutcome with
          | success input =>
              simpa [evaluate, finishWith, argumentResult] using
                ledgerBounded_append childBounded
                  (show LedgerBounded [ledgerEntry (.alternatives policyName)]
                    [.alternatives policyName] by
                      simp [LedgerBounded, ledgerEntry])
          | domainError =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.alternatives policyName]) childBounded)
          | unsupported capability =>
              simpa [evaluate, finishWith, argumentResult] using
                (ledgerBounded_weaken
                  (additionalEffects := [.alternatives policyName]) childBounded)

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

theorem prior_failure_preserves_ledger_prefix :
    let interpretation : Interpretation :=
      { strictMaps := [{ name := 1, table := [] }],
        sourceViews := [], restrictions := [] }
    evaluate [(0, .plain (.config 1))] interpretation
      (.sourceView 2 (.strictApp 1 (.var 0))) =
      (.domainError,
        [ledgerEntry (.evidence 1), ledgerEntry (.partiality 1)]) := by
  rfl

end E7CLeanCore
