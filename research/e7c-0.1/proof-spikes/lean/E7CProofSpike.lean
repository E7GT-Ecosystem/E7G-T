/-!
E7C/0.1 common proof-assistant spike, Lean 4 candidate.

This is a deliberately small model of the common comparison nucleus. It is
not the E7C calculus and is not evidence of E7C conformance, correctness or
semantic soundness.
-/

namespace E7CProofSpike

inductive B1Type where
  | config
  | outcomeConfig
  deriving DecidableEq, Repr

inductive MapMode where
  | strict
  deriving DecidableEq, Repr

structure MapType where
  source : B1Type
  target : B1Type
  mode : MapMode
  deriving DecidableEq, Repr

def strictConfigMap : MapType :=
  { source := .config, target := .config, mode := .strict }

inductive Term where
  | var (name : String)
  | strictApp (mapName : String) (argument : Term)
  deriving DecidableEq, Repr

abbrev Context := List (String × B1Type)
abbrev MapContext := List (String × MapType)

def PairNamesUnique {α : Type} (entries : List (String × α)) : Prop :=
  (entries.map (fun entry => entry.1)).Nodup

def lookupType : Context → String → Option B1Type
  | [], _ => none
  | (boundName, type) :: rest, name =>
      if name = boundName then some type else lookupType rest name

def lookupMap : MapContext → String → Option MapType
  | [], _ => none
  | (boundName, type) :: rest, name =>
      if name = boundName then some type else lookupMap rest name

inductive HasType (maps : MapContext) (context : Context) : Term → B1Type → Prop where
  | var (found : lookupType context name = some type) :
      HasType maps context (.var name) type
  | strictApp
      (found : lookupMap maps mapName = some strictConfigMap)
      (argumentType : HasType maps context argument .config) :
      HasType maps context (.strictApp mapName argument) .outcomeConfig

def substitute (name : String) (replacement : Term) : Term → Term
  | .var candidate => if candidate = name then replacement else .var candidate
  | .strictApp mapName argument =>
      .strictApp mapName (substitute name replacement argument)

theorem typing_substitution
    (termType : HasType maps ((name, replacementType) :: context) term resultType)
    (replacementHasType : HasType maps context replacement replacementType) :
    HasType maps context (substitute name replacement term) resultType := by
  induction term generalizing resultType with
  | var candidate =>
      cases termType with
      | var found =>
          by_cases sameName : candidate = name
          · subst candidate
            have sameType : replacementType = resultType := by
              simpa [lookupType] using found
            cases sameType
            simpa [substitute] using replacementHasType
          · simp only [substitute, sameName]
            apply HasType.var
            simpa [lookupType, sameName] using found
  | strictApp mapName argument inductionHypothesis =>
      cases termType with
      | strictApp found argumentType =>
          exact HasType.strictApp found (inductionHypothesis argumentType)

inductive Value where
  | config (code : Nat)
  | text (content : String)
  deriving DecidableEq, Repr

inductive Outcome where
  | success (value : Value)
  | domainError
  | unsupported (capability : String)
  deriving DecidableEq, Repr

inductive Binding where
  | plain (value : Value)
  | terminal (outcome : Outcome)
  deriving DecidableEq, Repr

structure StrictRow where
  input : Nat
  output : Nat
  deriving DecidableEq, Repr

abbrev StrictTable := List StrictRow

def lookupRow : StrictTable → Nat → Option Nat
  | [], _ => none
  | row :: rest, input =>
      if input = row.input then some row.output else lookupRow rest input

structure InterpretationEntry where
  mapName : String
  table : StrictTable
  deriving DecidableEq, Repr

abbrev Interpretation := List InterpretationEntry

def lookupTable : Interpretation → String → Option StrictTable
  | [], _ => none
  | entry :: rest, mapName =>
      if mapName = entry.mapName then some entry.table else lookupTable rest mapName

abbrev Environment := List (String × Binding)

def lookupBinding : Environment → String → Option Binding
  | [], _ => none
  | (boundName, binding) :: rest, name =>
      if name = boundName then some binding else lookupBinding rest name

def applyStrict (table : StrictTable) : Value → Outcome
  | .config input =>
      match lookupRow table input with
      | some output => .success (.config output)
      | none => .domainError
  | .text _ => .domainError

def evaluateBinding : Binding → Outcome
  | .plain value => .success value
  | .terminal outcome => outcome

def evaluate (environment : Environment) (interpretation : Interpretation) : Term → Outcome
  | .var name =>
      match lookupBinding environment name with
      | some binding => evaluateBinding binding
      | none => .unsupported name
  | .strictApp mapName argument =>
      match evaluate environment interpretation argument with
      | .domainError => .domainError
      | .success value =>
          match lookupTable interpretation mapName with
          | none => .unsupported mapName
          | some table => applyStrict table value
      | .unsupported capability => .unsupported capability

def successCarrier : B1Type → B1Type
  | .config => .config
  | .outcomeConfig => .config

def ValueHasType : Value → B1Type → Prop
  | .config _, .config => True
  | _, _ => False

def BindingHasType : Binding → B1Type → Prop
  | .plain value, .config => ValueHasType value .config
  | .terminal (.success value), .outcomeConfig => ValueHasType value .config
  | .terminal .domainError, .outcomeConfig => True
  | .terminal (.unsupported _), .outcomeConfig => True
  | _, _ => False

def StrictTableWellFormed (table : StrictTable) : Prop :=
  (table.map StrictRow.input).Nodup

def InterpretationNamesUnique (interpretation : Interpretation) : Prop :=
  (interpretation.map InterpretationEntry.mapName).Nodup

structure EnvironmentWellFormed (context : Context) (environment : Environment) : Prop where
  contextNamesUnique : PairNamesUnique context
  environmentNamesUnique : PairNamesUnique environment
  complete : ∀ name type,
    lookupType context name = some type →
      ∃ binding,
        lookupBinding environment name = some binding ∧
        BindingHasType binding type
  exact : ∀ name binding,
    lookupBinding environment name = some binding →
      ∃ type,
        lookupType context name = some type ∧
        BindingHasType binding type

structure InterpretationWellFormed
    (maps : MapContext) (interpretation : Interpretation) : Prop where
  mapNamesUnique : PairNamesUnique maps
  interpretationNamesUnique : InterpretationNamesUnique interpretation
  complete : ∀ mapName mapType,
    lookupMap maps mapName = some mapType →
      mapType = strictConfigMap ∧
      ∃ table,
        lookupTable interpretation mapName = some table ∧
        StrictTableWellFormed table
  exact : ∀ mapName table,
    lookupTable interpretation mapName = some table →
      lookupMap maps mapName = some strictConfigMap ∧
      StrictTableWellFormed table

theorem evaluateBinding_success_has_type
    (bindingType : BindingHasType binding type)
    (successful : evaluateBinding binding = .success output) :
    ValueHasType output (successCarrier type) := by
  cases binding with
  | plain value =>
      cases type with
      | config =>
          have valueEqualsOutput : value = output := by
            simpa [evaluateBinding] using successful
          cases valueEqualsOutput
          simpa [BindingHasType, successCarrier] using bindingType
      | outcomeConfig =>
          simp [BindingHasType] at bindingType
  | terminal outcome =>
      cases outcome with
      | success value =>
          cases type with
          | config =>
              simp [BindingHasType] at bindingType
          | outcomeConfig =>
              have valueEqualsOutput : value = output := by
                simpa [evaluateBinding] using successful
              cases valueEqualsOutput
              simpa [BindingHasType, successCarrier] using bindingType
      | domainError =>
          simp [evaluateBinding] at successful
      | unsupported capability =>
          simp [evaluateBinding] at successful

theorem applyStrict_success_has_type
    (inputType : ValueHasType input .config)
    (successful : applyStrict table input = .success output) :
    ValueHasType output .config := by
  cases input with
  | text content =>
      simp [ValueHasType] at inputType
  | config code =>
      cases found : lookupRow table code with
      | none =>
          simp [applyStrict, found] at successful
      | some mapped =>
          have outputIsConfig : output = .config mapped := by
            simpa [applyStrict, found] using successful.symm
          cases outputIsConfig
          trivial

theorem successful_type_preservation
    (termType : HasType maps context term type)
    (environmentType : EnvironmentWellFormed context environment)
    (interpretationType : InterpretationWellFormed maps interpretation)
    (successful : evaluate environment interpretation term = .success output) :
    ValueHasType output (successCarrier type) := by
  induction termType generalizing output with
  | @var name type found =>
      obtain ⟨binding, bindingFound, bindingType⟩ :=
        environmentType.complete name type found
      have bindingSuccessful : evaluateBinding binding = .success output := by
        simpa [evaluate, bindingFound] using successful
      exact evaluateBinding_success_has_type bindingType bindingSuccessful
  | @strictApp mapName argument found argumentType inductionHypothesis =>
      obtain ⟨_, table, tableFound, _⟩ :=
        interpretationType.complete mapName strictConfigMap found
      cases argumentResult : evaluate environment interpretation argument with
      | domainError =>
          simp [evaluate, argumentResult] at successful
      | unsupported capability =>
          simp [evaluate, argumentResult] at successful
      | success input =>
          have inputType : ValueHasType input .config :=
            inductionHypothesis argumentResult
          have applied : applyStrict table input = .success output := by
            simpa [evaluate, argumentResult, tableFound] using successful
          exact applyStrict_success_has_type inputType applied

theorem strict_failure_is_domain_error
    (outsideDomain : lookupRow table input = none) :
    applyStrict table (.config input) = .domainError := by
  simp [applyStrict, outsideDomain]

theorem strict_failure_is_not_success
    (outsideDomain : lookupRow table input = none)
    (value : Value) :
    applyStrict table (.config input) ≠ .success value := by
  rw [strict_failure_is_domain_error outsideDomain]
  intro impossible
  cases impossible

theorem strict_failure_is_not_zero_success
    (outsideDomain : lookupRow table input = none) :
    applyStrict table (.config input) ≠ .success (.config 0) :=
  strict_failure_is_not_success outsideDomain (.config 0)

theorem outcome_variable_domain_error_is_direct :
    evaluate [("x", .terminal .domainError)] [] (.var "x") = .domainError := by
  rfl

theorem outcome_variable_success_is_direct :
    evaluate [("x", .terminal (.success (.config 7)))] [] (.var "x") =
      .success (.config 7) := by
  rfl

theorem missing_interpretation_is_unsupported :
    evaluate [("x", .plain (.config 0))] [] (.strictApp "f" (.var "x")) =
      .unsupported "f" := by
  rfl

theorem missing_environment_binding_is_not_well_formed :
    ¬ EnvironmentWellFormed [("x", .config)] [] := by
  intro wellFormed
  have found : lookupType [("x", .config)] "x" = some .config := by
    rfl
  obtain ⟨binding, bindingFound, _⟩ := wellFormed.complete "x" .config found
  simp [lookupBinding] at bindingFound

theorem missing_interpretation_table_is_not_well_formed :
    ¬ InterpretationWellFormed [("f", strictConfigMap)] [] := by
  intro wellFormed
  have found : lookupMap [("f", strictConfigMap)] "f" = some strictConfigMap := by
    rfl
  obtain ⟨_, table, tableFound, _⟩ :=
    wellFormed.complete "f" strictConfigMap found
  simp [lookupTable] at tableFound

end E7CProofSpike
