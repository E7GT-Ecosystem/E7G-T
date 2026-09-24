/-!
All-list conservation and sufficient-resource agreement for the selected
two-stage correlated Joint rule. The pair of complete FG3 graphs and exact
rational coefficient remain in each row. This is a Lean model relation;
Python admission, its resource machine, and IR decoding need separate bridges.
-/

namespace E7CEECQTwoStageAllInput

structure Graph where
  ab : Bool
  ac : Bool
  bc : Bool
  tag : Option Nat
  deriving DecidableEq, Repr

structure Row where
  left : Graph
  right : Graph
  coefficient : Rat
  deriving DecidableEq, Repr

structure Partition where
  retained : List Row
  firstExcluded : List Row
  secondExcluded : List Row
  deriving DecidableEq, Repr

def source (rs : List Row) : Partition :=
  { retained := rs.filter (fun r => !r.left.ab && !r.right.bc)
    firstExcluded := rs.filter (fun r => r.left.ab)
    secondExcluded := rs.filter (fun r => !r.left.ab && r.right.bc) }

def ir : List Row → Partition
  | [] => ⟨[], [], []⟩
  | r :: rs =>
    let rest := ir rs
    if r.left.ab then
      { rest with firstExcluded := r :: rest.firstExcluded }
    else if r.right.bc then
      { rest with secondExcluded := r :: rest.secondExcluded }
    else
      { rest with retained := r :: rest.retained }

theorem all_rows_partition_agreement (rs : List Row) : ir rs = source rs := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    by_cases h : r.left.ab = true
    · simp [ir, source, h, ih]
    · by_cases k : r.right.bc = true
      · simp [ir, source, h, k, ih]
      · simp [ir, source, h, k, ih]

def weighted (f : Row → Rat) (rs : List Row) : Rat :=
  (rs.map f).sum

theorem exact_weight_conservation (f : Row → Rat) (rs : List Row) :
    weighted f rs = weighted f (source rs).retained +
      weighted f (source rs).firstExcluded +
      weighted f (source rs).secondExcluded := by
  induction rs with
  | nil => simp [source, weighted]
  | cons r rs ih =>
    by_cases h : r.left.ab = true
    · simp [source, weighted, h] at ih ⊢
      simpa [add_assoc, add_comm, add_left_comm] using ih
    · by_cases k : r.right.bc = true
      · simp [source, weighted, h, k] at ih ⊢
        simpa [add_assoc, add_comm, add_left_comm] using ih
      · simp [source, weighted, h, k] at ih ⊢
        simpa [add_assoc, add_comm, add_left_comm] using ih

def keyWeight (left right : Graph) (r : Row) : Rat :=
  if r.left = left ∧ r.right = right then r.coefficient else 0

theorem correlated_rational_conservation (rs : List Row) (left right : Graph) :
    weighted (keyWeight left right) rs =
      weighted (keyWeight left right) (source rs).retained +
      weighted (keyWeight left right) (source rs).firstExcluded +
      weighted (keyWeight left right) (source rs).secondExcluded :=
  exact_weight_conservation (keyWeight left right) rs

def countKey (left right : Graph) (rs : List Row) : Nat :=
  (rs.filter (fun r => decide (r.left = left ∧ r.right = right))).length

theorem all_key_occurrences_conserved (rs : List Row) (left right : Graph) :
    countKey left right rs = countKey left right (source rs).retained +
      countKey left right (source rs).firstExcluded +
      countKey left right (source rs).secondExcluded := by
  induction rs with
  | nil => simp [source, countKey]
  | cons r rs ih =>
    by_cases h : r.left.ab = true
    · simp [source, countKey, h] at ih ⊢
      simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using ih
    · by_cases k : r.right.bc = true
      · simp [source, countKey, h, k] at ih ⊢
        simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using ih
      · simp [source, countKey, h, k] at ih ⊢
        simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using ih

structure Observation where
  partition : Partition
  checkedRows : List Row
  completedSteps : Nat
  completedLedgerEntries : Nat
  deriving DecidableEq, Repr

def sourceObservation (rs : List Row) : Observation :=
  ⟨source rs, rs, rs.length + 1, rs.length + 1⟩

def irObservation (rs : List Row) : Observation :=
  ⟨ir rs, rs, rs.length + 1, rs.length + 1⟩

/- The first successful restriction has already returned its exact retained
rows. One second attempt plus a row event for every retained row fits the
remaining step and ledger budgets. The real first-stage resource counts and
ledger prefix are premises of the external lowering bridge. -/
theorem sufficient_resource_observation_agreement (rs : List Row)
    (remainingSteps remainingLedger : Nat)
    (_steps : rs.length + 1 ≤ remainingSteps)
    (_ledger : rs.length + 1 ≤ remainingLedger) :
    irObservation rs = sourceObservation rs := by
  simp [irObservation, sourceObservation, all_rows_partition_agreement]

end E7CEECQTwoStageAllInput
