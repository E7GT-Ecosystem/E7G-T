import E7CJointSerializerOperationRelation
import E7CJointSerializerSourceGuardBridge

namespace E7CJointSerializerOperationGuardBridge
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceSemantics
open E7CJointSerializerOperationRelation E7CJointCPythonNormalReturnTrace
open E7CJointAdmissionGenerated E7CJointAdmissionPythonOperations
open E7CJointSortConstructorSemantics E7CJointAdmissionStatementTrace
open E7CJointSerializerSourceGuardBridge E7CJointFirstStageNormalReturnComposition

/- The serializer is derived from operation visits. Admission, native Joint
denotation, final Python equality and actual host execution remain conditional. -/
theorem operation_serializer_guard_recursive_equality
    {serializerOps : Operations} {read : Value → String → Option Value}
    (primitives : PrimitiveAdequacy serializerOps read)
    (attributes : AttributeContracts read)
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : CompleteAdmissionStatementTrace rawDocument)
    (joint : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows))
    {output : RawJson}
    (helperNormal : RowsNormal serializerOps (.joint 2
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) output)
    (contract : CPythonJsonEqualityContract output admission.rawRows)
    (returned : finalRowsGuard contract.pythonEqual output admission.rawRows =
      .returnedNormally) :
    rawJsonObjectKeyExtEq output admission.rawRows :=
  source_serializer_guard_recursive_equality attributes admission joint
    (rows_normal_sound primitives helperNormal) contract returned

end E7CJointSerializerOperationGuardBridge
