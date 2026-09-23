/-!
S1 strict-union control skeleton. Tags and coefficients are abstract Nat/Int
data; this does not model graph edge union, rational collection, Python
admission, ordered ledger or the complete resource policy. No external
adequacy conclusion follows from these theorems.
-/

namespace E7CS1StrictCore

structure Pair where
  leftTag : Nat
  rightTag : Nat
  coefficient : Int
  deriving DecidableEq, Repr

inductive Terminal where
  | success (coefficients : List Int)
  | domainError
  | resourceLimit
  deriving DecidableEq, Repr

/- A visit is charged before checking each supported pair. Success carries
the coefficient from each pair exactly once and in support order. -/
def run : Nat → List Pair → Terminal
  | _, [] => .success []
  | 0, _ :: _ => .resourceLimit
  | fuel + 1, pair :: rest =>
      if pair.leftTag = pair.rightTag then
        match run fuel rest with
        | .success coefficients => .success (pair.coefficient :: coefficients)
        | .domainError => .domainError
        | .resourceLimit => .resourceLimit
      else .domainError

theorem empty_succeeds (fuel : Nat) : run fuel [] = .success [] := rfl

theorem exhausted_before_first_check (pair : Pair) (rest : List Pair) :
    run 0 (pair :: rest) = .resourceLimit := rfl

theorem incompatible_head_fails (fuel : Nat) (pair : Pair) (rest : List Pair)
    (bad : pair.leftTag ≠ pair.rightTag) :
    run (fuel + 1) (pair :: rest) = .domainError := by
  simp [run, bad]

theorem sufficient_fuel_preserves_coefficients :
    (rows : List Pair) →
    (∀ pair ∈ rows, pair.leftTag = pair.rightTag) →
    run rows.length rows = .success (rows.map Pair.coefficient)
  | [], _ => rfl
  | pair :: rest, allCompatible => by
      have headCompatible : pair.leftTag = pair.rightTag :=
        allCompatible pair (by simp)
      have restCompatible : ∀ next ∈ rest, next.leftTag = next.rightTag := by
        intro next member
        exact allCompatible next (by simp [member])
      simp [run, headCompatible,
        sufficient_fuel_preserves_coefficients rest restCompatible]

theorem sufficient_fuel_fails_whole :
    (rows : List Pair) →
    (∃ pair ∈ rows, pair.leftTag ≠ pair.rightTag) →
    run rows.length rows = .domainError
  | [], bad => by
      rcases bad with ⟨_, member, _⟩
      cases member
  | pair :: rest, bad => by
      by_cases headCompatible : pair.leftTag = pair.rightTag
      · have restBad : ∃ next ∈ rest, next.leftTag ≠ next.rightTag := by
          rcases bad with ⟨next, member, incompatible⟩
          rcases List.mem_cons.mp member with same | tailMember
          · subst next
            exact (incompatible headCompatible).elim
          · exact ⟨next, tailMember, incompatible⟩
        simp [run, headCompatible, sufficient_fuel_fails_whole rest restBad]
      · simp [run, headCompatible]

end E7CS1StrictCore
