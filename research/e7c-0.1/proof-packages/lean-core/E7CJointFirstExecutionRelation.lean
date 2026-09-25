import E7CJointFirstCodeSkeleton

/-!
An explicit first-stage execution relation for the selected code *control*
fragment. Its row cases use the exact encoded Joint row, test coordinate 0
for AB, and charge before attempting each append. Helper behavior (admit,
iteration, partition, key/ledger serialization, IR parse and host execution)
is outside this relation and must be justified separately before it can be
called a semantics for the actual Python functions.
-/

namespace E7CJointFirstExecutionRelation
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageOperational
open E7CJointFirstCodeSkeleton

inductive EvalRows : List Row → List Row → List Row → Nat → Nat → Nat → Nat →
    List Event → ChildObservation → Prop where
  | done (kept excluded : List Row) (i steps fuel capacity : Nat)
      (ledger : List Event) :
      EvalRows [] kept excluded i steps fuel capacity ledger
        (child (.complete kept.reverse excluded.reverse) ledger steps)
  | noStep (r : Row) (rest kept excluded : List Row) (i steps capacity : Nat)
      (ledger : List Event) :
      EvalRows (r :: rest) kept excluded i steps 0 capacity ledger
        (child .resourceLimit ledger steps)
  | noLedger (r : Row) (rest kept excluded : List Row) (i steps fuel : Nat)
      (ledger : List Event) :
      EvalRows (r :: rest) kept excluded i steps (fuel + 1) 0 ledger
        (child .resourceLimit ledger (steps + 1))
  | excluded (r : Row) (rest kept excluded : List Row)
      (i steps fuel capacity : Nat) (ledger : List Event) (out : ChildObservation)
      (predicate : r.left.ab = true)
      (next : EvalRows rest kept (r :: excluded) (i + 1) (steps + 1)
        fuel capacity (.row .first i r true :: ledger) out) :
      EvalRows (r :: rest) kept excluded i steps (fuel + 1) (capacity + 1)
        ledger out
  | retained (r : Row) (rest kept excluded : List Row)
      (i steps fuel capacity : Nat) (ledger : List Event) (out : ChildObservation)
      (predicate : r.left.ab = false)
      (next : EvalRows rest (r :: kept) excluded (i + 1) (steps + 1)
        fuel capacity (.row .first i r false :: ledger) out) :
      EvalRows (r :: rest) kept excluded i steps (fuel + 1) (capacity + 1)
        ledger out

theorem rows_sound {rs kept excluded : List Row} {i steps fuel capacity : Nat}
    {ledger : List Event} {out : ChildObservation}
    (h : EvalRows rs kept excluded i steps fuel capacity ledger out) :
    visit rs kept excluded i steps fuel capacity ledger = out := by
  induction h with
  | done => rfl
  | noStep => rfl
  | noLedger => rfl
  | excluded _ _ _ _ _ _ _ _ _ _ hp _ ih =>
      simp [visit, hp, ih]
  | retained _ _ _ _ _ _ _ _ _ _ hp _ ih =>
      simp [visit, hp, ih]

inductive EvalFirst : List Row → Policy → Nat → Nat → ChildObservation → Prop where
  | noStep (rs : List Row) (policy : Policy) (capacity : Nat) :
      EvalFirst rs policy 0 capacity (child .resourceLimit [] 0)
  | noLedger (rs : List Row) (policy : Policy) (fuel : Nat) :
      EvalFirst rs policy (fuel + 1) 0 (child .resourceLimit [] 1)
  | unsupported (rs : List Row) (fuel capacity : Nat) :
      EvalFirst rs .unsupported (fuel + 1) (capacity + 1)
        (child .unsupported [.attempt .first] 1)
  | undetermined (rs : List Row) (fuel capacity : Nat) :
      EvalFirst rs .undetermined (fuel + 1) (capacity + 1)
        (child .undetermined [.attempt .first] 1)
  | ready (rs : List Row) (fuel capacity : Nat) (out : ChildObservation)
      (rows : EvalRows rs [] [] 0 1 fuel capacity [.attempt .first] out) :
      EvalFirst rs .ready (fuel + 1) (capacity + 1) out

theorem first_sound {rs : List Row} {policy : Policy} {fuel capacity : Nat}
    {out : ChildObservation} (h : EvalFirst rs policy fuel capacity out) :
    run rs policy fuel capacity = out := by
  cases h with
  | noStep => rfl
  | noLedger => rfl
  | unsupported => rfl
  | undetermined => rfl
  | ready _ _ _ _ hrows =>
      simpa [run] using rows_sound hrows

/- The explicit helper premise is a statement about a proposed code-to-model
translation. Nothing here derives it from Python admission or execution. -/
structure HelperContract (sourceRows : List Row) where
  admittedRows : List Row
  preservesOrderAndRationals : admittedRows = sourceRows

theorem under_helper_contract {rs : List Row} {policy : Policy}
    {fuel capacity : Nat} {out : ChildObservation}
    (helpers : HelperContract rs)
    (execution : EvalFirst helpers.admittedRows policy fuel capacity out) :
    run rs policy fuel capacity = out := by
  rw [← helpers.preservesOrderAndRationals]
  exact first_sound execution

end E7CJointFirstExecutionRelation
