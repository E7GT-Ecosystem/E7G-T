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

/-- All top-level and row-level checks are represented separately. The
32-fuel guard remains an explicit model-domain condition in the rows trace;
this structure does not claim that pinned Python checks fuel. -/
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
or final equality is an input premise. The bounded 32-fuel admission guard
remains explicit through CompleteAdmissionStatementTrace. -/
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
  have hOriginalFuel := decodeJointRows_within_fuel
    (rows_decoder_follows_statement_trace admission.rowsAdmission)
  have hGuard := normal_guard_execution_yields_extensional_equality
    contract hOutputFuel hOriginalFuel returned
  have hCanonical : rawJsonEquivalent output
      (encodeRawRows
        ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) :=
    rawJsonEquivalent_of_structural_eq hSerialized
  exact ⟨hDocument, hCanonicalRows, hParseCall, hDecodedTyped, hJoint,
    hSerialized,
    rawJsonEquivalent_trans (rawJsonEquivalent_symmetric hGuard) hCanonical⟩

end E7CJointFirstStageNormalReturnComposition
