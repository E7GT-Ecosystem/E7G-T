import E7CJointSerializerOperationRelation

/- Certificates for concrete reported input/output and helper frame ledgers.
Kernel checking establishes their mathematical agreement, not their origin in
CPython. The observer/exporter and native-value denotation remain trusted links. -/
namespace E7CJointSerializerObservedCertificate
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerOperationRelation

abbrev FrameLedger := List (String × RawJson)

def rowFramePlan (row : WireRow) : FrameLedger :=
  [("_row.call", encodeRawRow row),
   ("_graph.call", encodeRawGraph row.left),
   ("_graph.return", encodeRawGraph row.left),
   ("_graph.call", encodeRawGraph row.right),
   ("_graph.return", encodeRawGraph row.right),
   ("_row.return", encodeRawRow row)]

def framePlan (rows : List WireRow) : FrameLedger :=
  [("rows.call", encodeRawRows rows)] ++ rows.flatMap rowFramePlan ++
    [("rows.return", encodeRawRows rows)]

def CaptureValid (rows : List WireRow) (output : RawJson) (ledger : FrameLedger) : Prop :=
  output = encodeRawRows rows ∧ ledger = framePlan rows

theorem frame_plan_length (rows : List WireRow) :
    (framePlan rows).length = 6 * rows.length + 2 := by
  have middle : (rows.flatMap rowFramePlan).length = 6 * rows.length := by
    induction rows with
    | nil => rfl
    | cons row rest ih => simp [rowFramePlan, List.flatMap_cons, ih] <;> omega
  simp [framePlan, middle] <;> omega

/-- A checked concrete output yields a modeled operation derivation. This does
not turn the exporter or frame ledger into an all-input CPython semantics. -/
theorem checked_capture_yields_modeled_derivation
    {rows : List WireRow} {output : RawJson} {ledger : FrameLedger}
    (checked : CaptureValid rows output ledger) :
    RowsNormal (modeledOperations nativeAttributes) (.joint 2 rows) output := by
  rw [checked.1]
  exact modeled_rows_normal rows

theorem checked_capture_derives_domain
    {rows : List WireRow} {output : RawJson} {ledger : FrameLedger}
    (checked : CaptureValid rows output ledger) :
    rawJsonWithinFuel 32 output = true ∧ rawJsonUniqueObjectKeys output = true :=
  operation_normal_derives_domain (modeled_operations_adequate nativeAttributes)
    native_attributes_contracts (checked_capture_yields_modeled_derivation checked)

theorem checked_capture_complete_frame_count
    {rows : List WireRow} {output : RawJson} {ledger : FrameLedger}
    (checked : CaptureValid rows output ledger) : ledger.length = 6 * rows.length + 2 := by
  rw [checked.2]
  exact frame_plan_length rows

end E7CJointSerializerObservedCertificate
