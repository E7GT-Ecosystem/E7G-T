import E7CEECQTwoStageExactCodec

/-!
The value-level interpretation of the two complementary first-stage Joint
comprehensions. The selected implementation constructs both children directly
from filtered canonical tuples, without invoking `joint` re-collection.
These theorems establish exact selection and preservation of canonical list
invariants in Lean. Linking Python execution and constructor validation to
these theorems still requires an interpreter-semantics argument.
-/

namespace E7CJointFirstHelperSelection
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec

/- Independent recursion modeling the two comprehensions, in original order. -/
def select : List WireRow → List WireRow × List WireRow
  | [] => ([], [])
  | r :: rest =>
      let portions := select rest
      if decide ("AB" ∈ r.left.edges) then
        (portions.1, r :: portions.2)
      else
        (r :: portions.1, portions.2)

theorem selects_exact_rows (rs : List WireRow) :
    select rs =
      (rs.filter (fun r => !decide ("AB" ∈ r.left.edges)),
       rs.filter (fun r => decide ("AB" ∈ r.left.edges))) := by
  induction rs with
  | nil => rfl
  | cons r rest ih =>
      cases h : decide ("AB" ∈ r.left.edges) <;>
        simp [select, h, ih]

theorem selection_transport (rs : List WireRow) :
    ((select rs).1.map toRow, (select rs).2.map toRow) =
      ((rs.map toRow).filter (fun r => !r.left.ab),
       (rs.map toRow).filter (fun r => r.left.ab)) := by
  simp [selects_exact_rows, List.filter_map, Function.comp_def,
    first_predicate_preserved]

/- Every strict canonical ordering relation is inherited by both filtered
subsequences. In the Python constructor the relation is the strict ordering
of tuples of Config.identity() values; strictness also rules out duplicates. -/
theorem canonical_sublist_order {α : Type} (before : α → α → Prop)
    (rs : List α) (p : α → Bool) (h : List.Pairwise before rs) :
    List.Pairwise before (rs.filter p) :=
  h.filter p

theorem canonical_portions_order {α : Type} (before : α → α → Prop)
    (rs : List α) (p : α → Bool) (h : List.Pairwise before rs) :
    List.Pairwise before (rs.filter p) ∧
      List.Pairwise before (rs.filter (fun r => !p r)) := by
  exact ⟨canonical_sublist_order before rs p h,
    canonical_sublist_order before rs (fun r => !p r) h⟩

end E7CJointFirstHelperSelection
