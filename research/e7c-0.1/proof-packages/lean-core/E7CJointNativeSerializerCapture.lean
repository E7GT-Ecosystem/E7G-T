import E7CJointSerializerSourceSemantics

/- Receipts for native primitive and frame observations. Checking these literals
establishes their selected-source semantics, not their CPython origin. Native
hooks, denotation, stability, dispatch and completion remain explicit boundaries. -/
namespace E7CJointNativeSerializerCapture
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointCPythonNormalReturnTrace
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceSemantics

abbrev Ledger := List (String × RawJson)

structure CopyCapture where
  inputRefs : List Nat
  outputRefs : List Nat

/-- Compare every retained logical object token at its own position, including
list length. Tokens are not C addresses, source provenance or ownership proofs. -/
def sameCells : List Nat → List Nat → Bool
  | [], [] => true
  | left :: ls, right :: rs => (left == right) && sameCells ls rs
  | _, _ => false

theorem same_cells_exact (input output : List Nat)
    (checked : sameCells input output = true) : output = input := by
  induction input generalizing output with
  | nil => cases output <;> simp_all [sameCells]
  | cons head tail ih =>
      cases output with
      | nil => simp [sameCells] at checked
      | cons other rest =>
          simp only [sameCells, Bool.and_eq_true, beq_iff_eq] at checked
          obtain ⟨same, remaining⟩ := checked
          cases same
          rw [ih rest remaining]

def copiesChecked (copies : List CopyCapture) : Bool :=
  copies.all (fun copy => sameCells copy.inputRefs copy.outputRefs)

theorem checked_copy_positions (copies : List CopyCapture)
    (checked : copiesChecked copies = true) (copy : CopyCapture)
    (member : copy ∈ copies) : copy.outputRefs = copy.inputRefs := by
  exact same_cells_exact _ _ ((List.all_eq_true.mp checked) copy member)

theorem checked_copy_denotation (copies : List CopyCapture)
    (checked : copiesChecked copies = true) (copy : CopyCapture)
    (member : copy ∈ copies) (denote : Nat → RawJson) :
    copy.outputRefs.map denote = copy.inputRefs.map denote := by
  rw [checked_copy_positions copies checked copy member]

def graphPrimitivePlan (graph : WireGraph) : Ledger :=
  let edges := RawJson.array (graph.edges.map RawJson.string)
  [("_graph.call", encodeRawGraph graph), ("_graph.edges", edges),
   ("list.call", edges), ("list.return", edges),
   ("_graph.tag", graph.tag.elim RawJson.null RawJson.string),
   ("_graph.return", encodeRawGraph graph)]

def rowPrimitivePlan (row : WireRow) : Ledger :=
  [("_row.call", encodeRawRow row)] ++ graphPrimitivePlan row.left ++
    graphPrimitivePlan row.right ++
    [("_row.numerator", .integer row.coefficient.num),
     ("_row.denominator", .integer (Int.ofNat row.coefficient.den)),
     ("_row.return", encodeRawRow row)]

/-- This is the declared primitive/frame order of the checked helper syntax.
It does not assert that a native tracing API captures every dispatched opcode. -/
def primitivePlan (rows : List WireRow) : Ledger :=
  [("rows.call", encodeRawRows rows), ("rows.arity", .integer 2),
   ("rows.terms", encodeRawRows rows)] ++ rows.flatMap rowPrimitivePlan ++
    [("rows.return", encodeRawRows rows)]

structure Capture where
  output : RawJson
  events : Ledger
  copies : List CopyCapture

/-- A kernel receipt checks the actual reported result against executable
source-expression semantics, primitive/frame observations, and every copy cell.
No completed admission or serializer statement trace is supplied. -/
def Certificate (rows : List WireRow) (capture : Capture) : Prop :=
  runRows nativeAttributes (.joint 2 rows) = some capture.output ∧
  capture.events = primitivePlan rows ∧ copiesChecked capture.copies = true ∧
  capture.copies.length = 2 * rows.length

theorem checked_capture_yields_statement_trace {rows : List WireRow} {capture : Capture}
    (checked : Certificate rows capture) : RowsStatementTrace rows capture.output :=
  normal_source_run_yields_rows_statement_trace native_attributes_contracts checked.1

theorem checked_capture_exact {rows : List WireRow} {capture : Capture}
    (checked : Certificate rows capture) : capture.output = encodeRawRows rows := by
  have executed := checked.1
  rw [rows_source_run_exact native_attributes_contracts] at executed
  exact (Option.some.inj executed).symm

theorem checked_capture_derives_domain {rows : List WireRow} {capture : Capture}
    (checked : Certificate rows capture) :
    rawJsonWithinFuel 32 capture.output = true ∧
      rawJsonUniqueObjectKeys capture.output = true :=
  normal_source_run_derives_domain native_attributes_contracts checked.1

theorem primitive_plan_length (rows : List WireRow) :
    (primitivePlan rows).length = 16 * rows.length + 4 := by
  have middle : (rows.flatMap rowPrimitivePlan).length = 16 * rows.length := by
    induction rows with
    | nil => rfl
    | cons row rest ih =>
        simp [List.flatMap_cons, rowPrimitivePlan, graphPrimitivePlan, ih] <;> omega
  simp [primitivePlan, middle] <;> omega

theorem checked_capture_counts {rows : List WireRow} {capture : Capture}
    (checked : Certificate rows capture) :
    capture.events.length = 16 * rows.length + 4 ∧
      capture.copies.length = 2 * rows.length := by
  constructor
  · rw [checked.2.1]; exact primitive_plan_length rows
  · exact checked.2.2.2

theorem changed_output_rejected {rows : List WireRow} {capture : Capture}
    (changed : capture.output ≠ encodeRawRows rows) : ¬ Certificate rows capture := by
  intro checked
  exact changed (checked_capture_exact checked)

theorem changed_copy_rejected {rows : List WireRow} {capture : Capture}
    (copy : CopyCapture) (member : copy ∈ capture.copies)
    (changed : copy.outputRefs ≠ copy.inputRefs) : ¬ Certificate rows capture := by
  intro checked
  exact changed (checked_copy_positions capture.copies checked.2.2.1 copy member)

example : sameCells [1, 1, 3] [1, 1, 3] = true := rfl
example : sameCells [1, 1, 3] [1, 3, 1] = false := rfl
example : sameCells [1] [1, 1] = false := rfl

end E7CJointNativeSerializerCapture
