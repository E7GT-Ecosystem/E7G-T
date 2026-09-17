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

abbrev Environment := List (String × Value)

def lookupValue : Environment → String → Option Value
  | [], _ => none
  | (boundName, value) :: rest, name =>
      if name = boundName then some value else lookupValue rest name

def applyStrict (table : StrictTable) : Value → Outcome
  | .config input =>
      match lookupRow table input with
      | some output => .success (.config output)
      | none => .domainError
  | .text _ => .domainError

def evaluate (environment : Environment) (interpretation : Interpretation) : Term → Outcome
  | .var name =>
      match lookupValue environment name with
      | some value => .success value
      | none => .domainError
  | .strictApp mapName argument =>
      match evaluate environment interpretation argument with
      | .domainError => .domainError
      | .success value =>
          match lookupTable interpretation mapName with
          | none => .domainError
          | some table => applyStrict table value

def successCarrier : B1Type → B1Type
  | .config => .config
  | .outcomeConfig => .config

def ValueHasType : Value → B1Type → Prop
  | .config _, .config => True
  | _, _ => False

def EnvironmentHasType (context : Context) (environment : Environment) : Prop :=
  ∀ name type,
    lookupType context name = some type →
      ∃ value,
        lookupValue environment name = some value ∧
        ValueHasType value (successCarrier type)

theorem applyStrict_success_has_type
    (successful : applyStrict table input = .success output) :
    ValueHasType output .config := by
  cases input with
  | text content =>
      simp [applyStrict] at successful
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
    (environmentType : EnvironmentHasType context environment)
    (successful : evaluate environment interpretation term = .success output) :
    ValueHasType output (successCarrier type) := by
  cases termType with
  | @var name type found =>
      obtain ⟨value, valueFound, valueType⟩ := environmentType name type found
      have valueEqualsOutput : value = output := by
        simpa [evaluate, valueFound] using successful
      cases valueEqualsOutput
      exact valueType
  | @strictApp mapName argument found argumentType =>
      cases argumentResult : evaluate environment interpretation argument with
      | domainError =>
          simp [evaluate, argumentResult] at successful
      | success input =>
          cases tableResult : lookupTable interpretation mapName with
          | none =>
              simp [evaluate, argumentResult, tableResult] at successful
          | some table =>
              have applied : applyStrict table input = .success output := by
                simpa [evaluate, argumentResult, tableResult] using successful
              exact applyStrict_success_has_type applied

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

end E7CProofSpike
