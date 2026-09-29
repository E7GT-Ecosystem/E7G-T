import E7CJointSerializerSourceSemantics
import E7CJointFirstStageNormalReturnComposition

namespace E7CJointSerializerSourceGuardBridge
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceSemantics
open E7CJointCPythonNormalReturnTrace

/- The serializer premise of #157 is supplied by source-expression execution.
Admission, Joint, final comparison, and running-host adequacy remain separate. -/
open E7CJointAdmissionGenerated E7CJointAdmissionPythonOperations
open E7CJointSortConstructorSemantics E7CJointAdmissionStatementTrace
open E7CJointFirstStageNormalReturnComposition

theorem source_serializer_guard_recursive_equality
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : CompleteAdmissionStatementTrace rawDocument)
    (joint : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows))
    {output : RawJson}
    (helperRun : runRows read (.joint 2
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) =
      some output)
    (contract : CPythonJsonEqualityContract output admission.rawRows)
    (returned : finalRowsGuard contract.pythonEqual output admission.rawRows =
      .returnedNormally) :
    rawJsonObjectKeyExtEq output admission.rawRows :=
  first_stage_guard_recursive_equality admission joint
    (normal_source_run_yields_rows_statement_trace attributes helperRun)
    contract returned

end E7CJointSerializerSourceGuardBridge
