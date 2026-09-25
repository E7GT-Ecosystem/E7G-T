import E7CEECQTwoStageExactCodec

/-!
The value-level interpretation of the two complementary first-stage Joint
comprehensions. The checked Python AST selects directly from `source.terms`
and passes both lists to `joint`. This theorem concerns the selection only:
Python's `joint` normalization, admission and serialization still need a
code-semantics link. Entire correlated rows and rational coefficients travel
without modifying their values.
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

/- This premise is precisely the unproved part of `joint` for these admitted
subsets: re-collecting a sorted, unique support must preserve its row order,
graph identities and exact rational values. -/
structure JointNormalization (rs : List Row) where
  normalize : List Row → List Row
  retainedPreserved : normalize (rs.filter (fun r => !r.left.ab)) =
    rs.filter (fun r => !r.left.ab)
  excludedPreserved : normalize (rs.filter (fun r => r.left.ab)) =
    rs.filter (fun r => r.left.ab)

theorem under_normalization_contract (wire : List WireRow)
    (h : JointNormalization (wire.map toRow)) :
    (h.normalize ((select wire).1.map toRow),
     h.normalize ((select wire).2.map toRow)) =
      ((wire.map toRow).filter (fun r => !r.left.ab),
       (wire.map toRow).filter (fun r => r.left.ab)) := by
  apply Prod.ext
  · rw [← h.retainedPreserved]
    exact congrArg h.normalize (congrArg Prod.fst (selection_transport wire))
  · rw [← h.excludedPreserved]
    exact congrArg h.normalize (congrArg Prod.snd (selection_transport wire))

end E7CJointFirstHelperSelection
