import E7CJointAdmissionGenerated

/-!
The generated normal-path admission program is tied to selected Python AST
sites by `e7c_joint_admission_translation.py --check`. These theorems prove
that, for the *translated program*, a normal result's typed correlated rows
are exactly the typed interpretation of the source's ordered wire rows.
The code-to-CPython adequacy of Fraction, Config, list/dict equality, and
the parser/serializer helpers remains a separately named premise.
-/
namespace E7CJointAdmissionSemantics
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated

theorem parsed_serialization_roundtrip (rows : List Row) :
    (serializeRows rows).map parseRow = rows := by
  simp [serializeRows, serializeRow, parseRow, List.map_map,
    Function.comp_def, row_roundtrip]

theorem normal_return_exact_rows (normalizer : List Row → List Row)
    (sourceRows : List WireRow) (returned : List Row)
    (normal : admission normalizer sourceRows = some returned) :
    returned = sourceRows.map parseRow := by
  have equality : serializeRows returned = sourceRows := by
    by_cases guard : serializeRows (normalizer (parseRows sourceRows)) = sourceRows
    · have result : normalizer (parseRows sourceRows) = returned := by
        simpa [admission, guard] using normal
      rw [result] at guard
      exact guard
    · simp [admission, guard] at normal
  calc
    returned = (serializeRows returned).map parseRow :=
      (parsed_serialization_roundtrip returned).symm
    _ = sourceRows.map parseRow := congrArg (List.map parseRow) equality

theorem normal_return_exact_partition (normalizer : List Row → List Row)
    (sourceRows : List WireRow) (returned : List Row)
    (normal : admission normalizer sourceRows = some returned) :
    E7CEECQTwoStageAllInput.source returned =
      E7CEECQTwoStageAllInput.source (sourceRows.map toRow) := by
  rw [normal_return_exact_rows normalizer sourceRows returned normal]
  rfl

theorem changed_serialized_rows_rejected (normalizer : List Row → List Row)
    (sourceRows : List WireRow)
    (changed : serializeRows (normalizer (parseRows sourceRows)) ≠ sourceRows) :
    admission normalizer sourceRows = none := by
  simp [admission, changed]

def signedNullEmpty : WireRow :=
  ⟨⟨["AB"], none⟩, ⟨["AC"], some ""⟩, (-2 / 3 : Rat)⟩

theorem signed_null_empty_normal :
    admission id [signedNullEmpty] = some [toRow signedNullEmpty] := by
  have canonical : fromRow (toRow signedNullEmpty) = signedNullEmpty := by
    simp [signedNullEmpty, fromRow, toRow, fromGraph, toGraph]
  simp [admission, parseRows, parseRow, serializeRows, serializeRow,
    canonical]

theorem signed_null_empty_changed_coefficient_rejected :
    admission (fun _ => [⟨toGraph signedNullEmpty.left,
      toGraph signedNullEmpty.right, (1 / 7 : Rat)⟩])
      [signedNullEmpty] = none := by
  apply changed_serialized_rows_rejected
  have differentCoefficient : (1 / 7 : Rat) ≠ (-2 / 3 : Rat) := by decide
  simpa [serializeRows, serializeRow, signedNullEmpty, fromRow, fromGraph,
    toGraph] using differentCoefficient

end E7CJointAdmissionSemantics
