import E7CJointAdmissionExecution

/-!
Conditional operation-by-operation bridge from the selected pinned Python
normal-return calls to the modeled trace of #138.  The fields below are
explicit CPython operation adequacy premises; this file does not execute or
verify CPython itself.  In particular, `joint` still has to be related to the
abstract `normalizer`, and the inputs begin at typed `WireRow` values.

The equality premise describes the behavior of exact built-in list/dict
equality.  The control-flow premise says the pinned function passed its
`if rows(value) != source['rows']` guard.  Neither premise states row-list
equality: that equality is derived from the comparator contract and the
normal-return branch.
-/
namespace E7CJointAdmissionCPythonBridge
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated
open E7CJointAdmissionCalls
open E7CJointAdmissionExecution

/-!
Each field corresponds to one operation in the selected normal path:

* `parsedCall`: `FractionCall` identity on already decoded exact `Rat`
  coefficients, `Config(tuple(edges), tag)` construction and post-init
  canonicalization, plus tuple/list iteration in source order, composed row
  by row. The raw `Fraction(n,d)` refinement is upstream and remains open;
* `jointCall`: exact coefficient aggregation, zero cancellation, ordered-pair
  keys, canonical sorting and `Joint(2, terms)` construction;
* `serializedCall`: `rows`, `_row` and `_graph` output, retaining row order,
  both correlated coordinates and nullable tags;
* `builtinEquality`: exact built-in structural equality, under stable bindings
  and no mutation;
* `normalBranch`: the actual selected control-flow path reached `return value`.

These are conditional operation outcomes.  They do not discharge themselves
from the AST fingerprint, and in particular `jointCall` remains an explicit
implementation link to be proved from the running helper body.
-/
structure CPythonNormalReturnOperations
    (normalizer : List Row → List Row)
    (source : List WireRow) (result : List Row) : Type where
  parsed : List Row
  encoded : List WireRow
  parsedCall : ParseRowsCall source parsed
  jointCall : JointCall normalizer parsed result
  serializedCall : RowsWriteCall result encoded
  guardValue : Bool
  builtinEquality : guardValue = decide (encoded = source)
  normalBranch : guardValue = true

def pinned_normal_return_yields_modeled_trace
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (operations : CPythonNormalReturnOperations normalizer source result) :
    ModeledNormalExecution normalizer source result := by
  have guard : decide (operations.encoded = source) = true := by
    rw [← operations.builtinEquality]
    exact operations.normalBranch
  exact ⟨operations.parsed, operations.encoded,
    AdmissionStep.evaluated
      operations.parsed result operations.encoded
      (parse_rows_exact operations.parsedCall)
      (joint_call_exact operations.jointCall)
      (write_rows_exact operations.serializedCall)
      guard⟩

theorem pinned_normal_return_exact_rows
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (hcanonical : CanonicalWireRows source)
    (operations : CPythonNormalReturnOperations normalizer source result) :
    result = source.map toRow :=
  modeled_normal_execution_exact_rows hcanonical
    (pinned_normal_return_yields_modeled_trace operations)

theorem false_guard_cannot_return_normally
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (operations : CPythonNormalReturnOperations normalizer source result)
    (different : serializeRows result ≠ source) : False := by
  have trace := pinned_normal_return_yields_modeled_trace operations
  exact changed_rows_cannot_take_modeled_normal_return different trace

end E7CJointAdmissionCPythonBridge
