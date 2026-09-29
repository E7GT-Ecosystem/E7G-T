import E7CJointAdmissionStatementTrace

/-!
Conditional composition of the operation-level admission prefix and the
serializer/final-guard suffix. Decoder, Joint, serializer, and comparison
outcomes are derived from individual event traces; CPython-to-event adequacy
remains an explicitly open host link.
-/
namespace E7CJointFirstStageNormalReturnComposition

open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution
open E7CJointAdmissionCalls
open E7CJointAdmissionGenerated
open E7CJointAdmissionPythonOperations
open E7CJointRawJsonAdmission
open E7CJointCPythonNormalReturnTrace
open E7CJointAdmissionStatementTrace
open E7CJointSortConstructorSemantics

structure ResourcePolicyStatementTrace (raw : RawJson) where
  fields : List (String × RawJson)
  objectRead : raw = .object fields
  keyCheck : exactKeys fields ["step_bound", "ledger_bound"] = true
  rawSteps : RawJson
  rawLedger : RawJson
  stepsFieldRead : lookupField fields "step_bound" = some rawSteps
  ledgerFieldRead : lookupField fields "ledger_bound" = some rawLedger
  steps : Nat
  stepsInteger : exactInteger rawSteps = some (Int.ofNat steps)
  stepsNonnegative : Int.ofNat steps ≥ 0
  ledger : Nat
  ledgerInteger : exactInteger rawLedger = some (Int.ofNat ledger)
  ledgerNonnegative : Int.ofNat ledger ≥ 0

def ResourcePolicyStatementTrace.output
    {raw : RawJson} (trace : ResourcePolicyStatementTrace raw) : Nat × Nat :=
  (trace.steps, trace.ledger)

theorem resource_policy_decoder_follows_statement_trace
    {raw : RawJson} (trace : ResourcePolicyStatementTrace raw) :
    decodeResourcePolicy raw = some trace.output := by
  simp [decodeResourcePolicy, guard, trace.objectRead, trace.keyCheck,
    trace.stepsFieldRead, trace.ledgerFieldRead, decodeNonnegativeBound,
    trace.stepsInteger, trace.ledgerInteger, trace.stepsNonnegative,
    trace.ledgerNonnegative, ResourcePolicyStatementTrace.output]

structure InterpretationStatementTrace (raw : RawJson) where
  fields : List (String × RawJson)
  objectRead : raw = .object fields
  keyCheck : exactKeys fields ["capability", "obligation"] = true
  rawCapability : RawJson
  rawObligation : RawJson
  capabilityFieldRead : lookupField fields "capability" = some rawCapability
  obligationFieldRead : lookupField fields "obligation" = some rawObligation
  capability : Bool
  capabilityBoolean : rawCapability = .boolean capability
  resolved : Bool
  obligationString :
    rawObligation = .string (if resolved then "resolved" else "unresolved")

def InterpretationStatementTrace.output
    {raw : RawJson} (trace : InterpretationStatementTrace raw) : Bool × Bool :=
  (trace.capability, trace.resolved)

theorem interpretation_decoder_follows_statement_trace
    {raw : RawJson} (trace : InterpretationStatementTrace raw) :
    decodeInterpretation raw = some trace.output := by
  rcases trace with ⟨fields, objectRead, keyCheck, rawCapability,
    rawObligation, capabilityFieldRead, obligationFieldRead, capability,
    capabilityBoolean, resolved, obligationString⟩
  cases resolved <;>
    simp [decodeInterpretation, guard, objectRead, keyCheck,
      capabilityFieldRead, obligationFieldRead, capabilityBoolean,
      obligationString, InterpretationStatementTrace.output]

/-- All top-level and row-level checks are represented separately. No fuel
guard is a field of the trace: successful row-schema visits derive the
model's 32-fuel predicate. The pinned Python code does not check fuel. -/
structure CompleteAdmissionStatementTrace (rawDocument : RawJson) where
  fields : List (String × RawJson)
  documentObjectRead : rawDocument = .object fields
  documentKeyCheck : exactKeys fields expectedDocumentKeys = true
  metadataCheck : expectedMetadata fields = true
  rawRows : RawJson
  rawPolicy : RawJson
  rawInterpretation : RawJson
  rowsFieldRead : lookupField fields "rows" = some rawRows
  policyFieldRead : lookupField fields "resource_policy" = some rawPolicy
  interpretationFieldRead : lookupField fields "interpretation" = some rawInterpretation
  rowsAdmission : RawRowsAdmissionStatementTrace rawRows
  policyAdmission : ResourcePolicyStatementTrace rawPolicy
  interpretationAdmission : InterpretationStatementTrace rawInterpretation

def CompleteAdmissionStatementTrace.document
    {rawDocument : RawJson}
    (trace : CompleteAdmissionStatementTrace rawDocument) : DecodedRawDocument :=
  ⟨trace.rawRows, trace.rowsAdmission.rows,
    trace.policyAdmission.steps, trace.policyAdmission.ledger,
    trace.interpretationAdmission.capability,
    trace.interpretationAdmission.resolved⟩

theorem complete_document_decoder_follows_statement_trace
    {rawDocument : RawJson}
    (trace : CompleteAdmissionStatementTrace rawDocument) :
    decodeRawDocument rawDocument = some trace.document := by
  have hrows := rows_decoder_follows_statement_trace trace.rowsAdmission
  have hpolicy := resource_policy_decoder_follows_statement_trace trace.policyAdmission
  have hinterpretation :=
    interpretation_decoder_follows_statement_trace trace.interpretationAdmission
  simp [decodeRawDocument, guard, trace.documentObjectRead,
    trace.documentKeyCheck, trace.metadataCheck, trace.rowsFieldRead,
    trace.policyFieldRead, trace.interpretationFieldRead, hrows, hpolicy,
    hinterpretation, CompleteAdmissionStatementTrace.document,
    ResourcePolicyStatementTrace.output,
    InterpretationStatementTrace.output]

/-- Running-host outcomes stay disjoint. This increment proves only the
conditional normal-return observation; exception, divergence, and external
resource interruption are not converted into rejection or success. -/
inductive FirstStageHostOutcome where
  | normalReturn
  | invalidInput
  | exception
  | nontermination
  | resourceInterruption
  deriving DecidableEq, Repr

theorem first_stage_host_outcomes_are_distinct :
    FirstStageHostOutcome.invalidInput ≠ FirstStageHostOutcome.exception ∧
    FirstStageHostOutcome.exception ≠ FirstStageHostOutcome.nontermination ∧
    FirstStageHostOutcome.nontermination ≠ FirstStageHostOutcome.resourceInterruption ∧
    FirstStageHostOutcome.resourceInterruption ≠ FirstStageHostOutcome.normalReturn := by
  decide

/-- Compose raw admission, the operation-by-operation Joint trace, the
serializer trace, and the actual final-guard branch observation. No completed
decoded document, Joint result equality, serialized value, equality boolean,
or final equality is an input premise. The modeled 32-fuel condition is
derived from the admitted row schema; pinned Python does not check it. -/
theorem first_stage_normal_return_composition
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : CompleteAdmissionStatementTrace rawDocument)
    (joint : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows))
    {output : RawJson}
    (serializer : RowsStatementTrace
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)
      output)
    (contract : CPythonJsonEqualityContract output admission.rawRows)
    (returned : finalRowsGuard contract.pythonEqual output admission.rawRows =
      .returnedNormally) :
    decodeRawDocument rawDocument = some admission.document ∧
    CanonicalWireRows admission.rowsAdmission.rows ∧
    ParseRowsCall admission.rowsAdmission.rows
      (parseRows admission.rowsAdmission.rows) ∧
    parseRows admission.rowsAdmission.rows = admission.document.rows.map toRow ∧
    runConstructorRows joint.constructorOps 2
      (materializeJointRows ops joint.preSort.finalDictionary joint.sortedKeys) =
      some (jointNormalizer ops (parseRows admission.rowsAdmission.rows)) ∧
    output = encodeRawRows
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow) ∧
    rawJsonUniqueObjectKeys admission.rawRows = true ∧
    rawJsonEquivalent admission.rawRows
      (encodeRawRows
        ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) := by
  have hDocument := complete_document_decoder_follows_statement_trace admission
  have hCanonicalRows := rows_statement_trace_canonical admission.rowsAdmission
  have hParseCall := parse_rows_call_of_canonical hCanonicalRows
  have hDecodedTyped : parseRows admission.rowsAdmission.rows =
      admission.document.rows.map toRow := by
    rfl
  have hJoint := joint_statement_trace_returns_model_rows joint
  have hSerialized := rows_statement_output_exact serializer
  have hOutputFuel := rows_statement_within_fuel serializer
  have hOutputUnique := rows_statement_unique_keys serializer
  have hOriginalFuel :=
    rows_statement_trace_within_fuel admission.rowsAdmission
  have hOriginalUnique :=
    rows_statement_trace_unique_keys admission.rowsAdmission
  have hGuard := normal_guard_execution_yields_extensional_equality
    contract hOutputFuel hOriginalFuel returned
  have hCanonical : rawJsonEquivalent output
      (encodeRawRows
        ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) :=
    rawJsonEquivalent_of_structural_eq hSerialized
      hOutputFuel hOutputUnique
  exact ⟨hDocument, hCanonicalRows, hParseCall, hDecodedTyped, hJoint,
    hSerialized, hOriginalUnique,
    rawJsonEquivalent_trans (rawJsonEquivalent_symmetric hGuard) hCanonical⟩

/-- The actual compared pair in the modeled first-stage guard belongs to
the selected raw carrier. Thus #148's two-way agreement applies to it,
retaining each fraction's original numerator and denominator independently.
The CPython equality observation remains an explicit operation premise. -/
theorem first_stage_guard_recursive_equality
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : CompleteAdmissionStatementTrace rawDocument)
    (joint : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows))
    {output : RawJson}
    (serializer : RowsStatementTrace
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)
      output)
    (contract : CPythonJsonEqualityContract output admission.rawRows)
    (returned : finalRowsGuard contract.pythonEqual output admission.rawRows =
      .returnedNormally) :
    rawJsonObjectKeyExtEq output admission.rawRows := by
  rcases rows_statement_trace_selected_raw admission.rowsAdmission with
    ⟨input, hInput⟩
  let outputRows :=
    (jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow
  have hOutput : output = rawSelectedRows
      (outputRows.map selectedRowFromWire) := by
    rw [rows_statement_output_exact serializer, encoded_rows_selected_raw]
  have hOutputFuel : rawJsonWithinFuel 32 output = true :=
    rows_statement_within_fuel serializer
  have hInputFuel : rawJsonWithinFuel 32 admission.rawRows = true :=
    rows_statement_trace_within_fuel admission.rowsAdmission
  have hOutputUnique : rawJsonUniqueObjectKeys output = true :=
    rows_statement_unique_keys serializer
  have hInputUnique : rawJsonUniqueObjectKeys admission.rawRows = true :=
    rows_statement_trace_unique_keys admission.rowsAdmission
  have hGuard : rawJsonEquivalent output admission.rawRows :=
    normal_guard_execution_yields_extensional_equality contract
      hOutputFuel hInputFuel returned
  rw [hOutput, hInput] at hGuard ⊢
  exact (selectedRawRows_rawJsonEquivalent_iff_recursiveEquality
    (outputRows.map selectedRowFromWire) input
    (by simpa only [hOutput] using hOutputFuel)
    (by simpa only [hInput] using hInputFuel)
    (by simpa only [hOutput] using hOutputUnique)
    (by simpa only [hInput] using hInputUnique)).mp hGuard

end E7CJointFirstStageNormalReturnComposition
