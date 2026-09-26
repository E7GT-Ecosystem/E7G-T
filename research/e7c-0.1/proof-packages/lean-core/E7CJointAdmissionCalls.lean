import E7CJointAdmissionSemantics

/-!
Operation-level semantics for the selected normal `admit` return path.
Each judgment denotes one successful helper or primitive call. These rules
describe the reviewed subset; the assertion that CPython performs each call
according to the rule is still an explicit, separate implementation premise.
In particular, `FractionCall` starts with the decoded exact `Rat` of an
admitted canonical numerator/denominator pair. Deriving that decoding from
CPython `Fraction(n, d)` and proving all exceptional paths remain open.
-/
namespace E7CJointAdmissionCalls
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated

inductive ConfigCall : WireGraph → Graph → Prop where
  | accepted (wire : WireGraph) (canonical : canonicalGraph wire) :
      ConfigCall wire (toGraph wire)

inductive FractionCall : Rat → Rat → Prop where
  | accepted (value : Rat) : FractionCall value value

inductive ParseRowCall : WireRow → Row → Prop where
  | accepted (wire : WireRow) (left right : Graph) (coefficient : Rat)
      (hl : ConfigCall wire.left left) (hr : ConfigCall wire.right right)
      (hc : FractionCall wire.coefficient coefficient) :
      ParseRowCall wire ⟨left, right, coefficient⟩

inductive ParseRowsCall : List WireRow → List Row → Prop where
  | nil : ParseRowsCall [] []
  | cons {wire typed source parsed}
      (head : ParseRowCall wire typed) (tail : ParseRowsCall source parsed) :
      ParseRowsCall (wire :: source) (typed :: parsed)

/- Aggregation may combine, cancel, or reorder rows. The final serializer
   guard, rather than an assumption about aggregation, controls normal return. -/
inductive JointCall (normalizer : List Row → List Row) :
    List Row → List Row → Prop where
  | returned (parsed : List Row) :
      JointCall normalizer parsed (normalizer parsed)

inductive GraphWriteCall : Graph → WireGraph → Prop where
  | returned (graph : Graph) : GraphWriteCall graph (fromGraph graph)

inductive RowWriteCall : Row → WireRow → Prop where
  | returned (row : Row) (left right : WireGraph)
      (hl : GraphWriteCall row.left left)
      (hr : GraphWriteCall row.right right) :
      RowWriteCall row ⟨left, right, row.coefficient⟩

inductive RowsWriteCall : List Row → List WireRow → Prop where
  | nil : RowsWriteCall [] []
  | cons {typed wire rows encoded}
      (head : RowWriteCall typed wire) (tail : RowsWriteCall rows encoded) :
      RowsWriteCall (typed :: rows) (wire :: encoded)

inductive WireEqualCall : List WireRow → List WireRow → Bool → Prop where
  | equal (rows : List WireRow) : WireEqualCall rows rows true
  | different (left right : List WireRow) (h : left ≠ right) :
      WireEqualCall left right false

inductive NormalReturn (normalizer : List Row → List Row) :
    List WireRow → List Row → Prop where
  | returned {source parsed result encoded}
      (parse : ParseRowsCall source parsed)
      (joint : JointCall normalizer parsed result)
      (write : RowsWriteCall result encoded)
      (equal : WireEqualCall encoded source true) :
      NormalReturn normalizer source result

theorem parse_row_exact {wire : WireRow} {typed : Row}
    (h : ParseRowCall wire typed) : typed = toRow wire := by
  cases h with
  | accepted wire left right coefficient hl hr hc =>
      cases hl
      cases hr
      cases hc
      rfl

theorem parse_rows_exact {source : List WireRow} {parsed : List Row}
    (h : ParseRowsCall source parsed) : parsed = parseRows source := by
  induction h with
  | nil => rfl
  | cons head tail ih =>
      simp [parseRows, parseRow, parse_row_exact head, ih]

theorem joint_call_exact {normalizer : List Row → List Row}
    {parsed result : List Row} (h : JointCall normalizer parsed result) :
    result = normalizer parsed := by
  cases h
  rfl

theorem write_row_exact {row : Row} {wire : WireRow}
    (h : RowWriteCall row wire) : wire = serializeRow row := by
  cases h with
  | returned row left right hl hr =>
      cases hl
      cases hr
      rfl

theorem write_rows_exact {rows : List Row} {encoded : List WireRow}
    (h : RowsWriteCall rows encoded) : encoded = serializeRows rows := by
  induction h with
  | nil => rfl
  | cons head tail ih =>
      simp [serializeRows, write_row_exact head, ih]

theorem equal_call_exact {left right : List WireRow}
    (h : WireEqualCall left right true) : left = right := by
  cases h
  rfl

theorem normal_return_matches_generated {normalizer : List Row → List Row}
    {source : List WireRow} {result : List Row}
    (h : NormalReturn normalizer source result) :
    admission normalizer source = some result := by
  cases h with
  | returned parse joint write equal =>
      have parsedEq := parse_rows_exact parse
      have jointEq := joint_call_exact joint
      have wireEq := write_rows_exact write
      have compareEq := equal_call_exact equal
      have normalizerEq : normalizer (parseRows source) = result := by
        rw [← parsedEq]
        exact jointEq.symm
      have serializationEq : serializeRows result = source := by
        rw [← wireEq]
        exact compareEq
      simp [admission, normalizerEq, serializationEq]

theorem normal_return_exact_rows {normalizer : List Row → List Row}
    {source : List WireRow} {result : List Row}
    (h : NormalReturn normalizer source result) :
    result = source.map toRow :=
  E7CJointAdmissionSemantics.normal_return_exact_rows
    normalizer source result (normal_return_matches_generated h)

end E7CJointAdmissionCalls
