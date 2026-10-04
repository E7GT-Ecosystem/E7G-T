import E7CJointAdmissionPythonOperations

/-!
An event-level relation for the aggregation loop in the pinned `joint`
helper. Each row visit exposes the results of lookup, exact addition, and
dictionary update separately. The relation derives the abstract dictionary
trace from those per-operation observations; it does not take a completed
`JointDictionaryTrace` or final dictionary as an input premise.

The relation is a typed Lean event model. Decoding profiler packets into these
events, and proving each event adequate for CPython, remain host links.
-/
namespace E7CJointNativeDictionaryTrace
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated
open E7CJointAdmissionCalls
open E7CJointAdmissionExecution
open E7CJointAdmissionPythonOperations

structure JointDictionaryRowEvent (ops : CPythonJointPrimitives)
    (before : List JointEntry) (row : Row) (after : List JointEntry) where
  lookupResult : Rat
  additionResult : Rat
  lookupRefines : lookupResult =
    dictLookup ops.keyEqual before (rowKey row)
  additionRefines : additionResult =
    ops.add lookupResult row.coefficient
  updateRefines : after =
    dictSet ops.keyEqual before (rowKey row) additionResult

theorem rowEvent_refines_jointDictStep
    {ops : CPythonJointPrimitives} {before after : List JointEntry}
    {row : Row} (event : JointDictionaryRowEvent ops before row after) :
    after = jointDictStep ops before row := by
  calc
    after = dictSet ops.keyEqual before (rowKey row) event.additionResult :=
      event.updateRefines
    _ = dictSet ops.keyEqual before (rowKey row)
        (ops.add event.lookupResult row.coefficient) := by
      rw [event.additionRefines]
    _ = dictSet ops.keyEqual before (rowKey row)
        (ops.add (dictLookup ops.keyEqual before (rowKey row))
          row.coefficient) := by
      rw [event.lookupRefines]
    _ = jointDictStep ops before row := rfl

inductive JointDictionaryEventTrace (ops : CPythonJointPrimitives) :
    List Row → List JointEntry → List JointEntry → Type where
  | nil (entries : List JointEntry) :
      JointDictionaryEventTrace ops [] entries entries
  | cons (row : Row) (rows : List Row)
      (before after final : List JointEntry)
      (event : JointDictionaryRowEvent ops before row after)
      (tail : JointDictionaryEventTrace ops rows after final) :
      JointDictionaryEventTrace ops (row :: rows) before final

theorem eventTrace_derives_dictionaryTrace
    {ops : CPythonJointPrimitives} {rows : List Row}
    {before final : List JointEntry}
    (events : JointDictionaryEventTrace ops rows before final) :
    JointDictionaryTrace ops rows before final := by
  induction events with
  | nil entries => exact .nil entries
  | @cons row rows before after final event tail ih =>
      exact .cons row rows before after final
        (rowEvent_refines_jointDictStep event) ih

theorem eventTrace_final_is_run
    {ops : CPythonJointPrimitives} {rows : List Row}
    {before final : List JointEntry}
    (events : JointDictionaryEventTrace ops rows before final) :
    final = jointDictRun ops rows before := by
  exact dictionaryTrace_computes_run (eventTrace_derives_dictionaryTrace events)

end E7CJointNativeDictionaryTrace
