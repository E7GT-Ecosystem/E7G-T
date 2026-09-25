/-!
Finite total-map MSC closure model for the v0.15/MSC1 source, §X.21 MSC.3.

`Assignment` is a complete, already enumerated member of the product of
typed scope carriers. Every link compares two total maps into its own common
comparison carrier. The caller supplies the finite candidate enumeration;
its completeness and lack of duplicates, source admission, and Python
execution are separate obligations. This is the exact-map MSC-B1 subset.
-/

namespace E7CMSCFiniteClosure

structure Link (Assignment : Type) where
  Comparison : Type
  [comparisonEq : DecidableEq Comparison]
  projection : Assignment → Comparison
  lowerComparison : Assignment → Comparison

def compatible : List (Link Assignment) → Assignment → Prop
  | [], _ => True
  | link :: rest, assignment =>
      link.projection assignment = link.lowerComparison assignment ∧
      compatible rest assignment

def check : List (Link Assignment) → Assignment → Bool
  | [], _ => true
  | link :: rest, assignment =>
      letI : DecidableEq link.Comparison := link.comparisonEq
      decide (link.projection assignment = link.lowerComparison assignment) &&
      check rest assignment

theorem check_iff (links : List (Link Assignment)) (assignment : Assignment) :
    check links assignment = true ↔ compatible links assignment := by
  induction links with
  | nil => simp [check, compatible]
  | cons link rest ih => simp [check, compatible, ih]

def selected (assignments : List Assignment) (links : List (Link Assignment)) :
    List Assignment :=
  assignments.filter (check links)

theorem selected_iff (assignments : List Assignment)
    (links : List (Link Assignment)) (assignment : Assignment) :
    assignment ∈ selected assignments links ↔
      assignment ∈ assignments ∧ compatible links assignment := by
  simp [selected, check_iff]

theorem incompatible_iff (assignments : List Assignment)
    (links : List (Link Assignment)) :
    selected assignments links = [] ↔
      ∀ assignment ∈ assignments, ¬ compatible links assignment := by
  constructor
  · intro empty assignment admitted good
    have present := (selected_iff assignments links assignment).2 ⟨admitted, good⟩
    simp [empty] at present
  · intro absent
    cases h : selected assignments links with
    | nil => rfl
    | cons assignment rest =>
        have present : assignment ∈ selected assignments links := by simp [h]
        obtain ⟨admitted, good⟩ := (selected_iff assignments links assignment).1 present
        exact False.elim (absent assignment admitted good)

theorem singleton_sound (assignments : List Assignment)
    (links : List (Link Assignment)) (winner : Assignment)
    (single : selected assignments links = [winner]) :
    winner ∈ assignments ∧ compatible links winner ∧
      ∀ other ∈ assignments, compatible links other → other = winner := by
  have present : winner ∈ selected assignments links := by simp [single]
  obtain ⟨admitted, good⟩ := (selected_iff assignments links winner).1 present
  refine ⟨admitted, good, ?_⟩
  intro other otherAdmitted otherGood
  have otherPresent := (selected_iff assignments links other).2
    ⟨otherAdmitted, otherGood⟩
  simpa [single] using otherPresent

inductive Outcome (Assignment : Type) where
  | unsupported
  | resourceLimit
  | incompatible
  | unique (assignment : Assignment)
  | ambiguous (assignments : List Assignment)
  | undetermined
  deriving Repr

def close (mapsReady : Bool) (limit : Nat)
    (assignments : List Assignment) (links : List (Link Assignment)) :
    Outcome Assignment :=
  if !mapsReady then .unsupported
  else if assignments.isEmpty then .unsupported
  else if assignments.length > limit then .resourceLimit
  else match selected assignments links with
    | [] => .incompatible
    | [assignment] => .unique assignment
    | many => .ambiguous many

theorem unsupported_when_unavailable (limit : Nat)
    (assignments : List Assignment) (links : List (Link Assignment)) :
    close false limit assignments links = .unsupported := by
  rfl

theorem unsupported_when_empty (limit : Nat) (links : List (Link Assignment)) :
    close true limit [] links = .unsupported := by
  rfl

theorem exhausted_before_scan (limit : Nat) (assignments : List Assignment)
    (links : List (Link Assignment)) (exhausted : assignments.length > limit) :
    close true limit assignments links = .resourceLimit := by
  cases assignments with
  | nil => simp at exhausted
  | cons assignment rest => simp [close, exhausted]

end E7CMSCFiniteClosure
