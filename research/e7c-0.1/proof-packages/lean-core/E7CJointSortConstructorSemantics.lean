import E7CJointAdmissionPythonOperations

/-!
An abstract identity-key sorting semantics and typed Joint constructor model.
The sort trace records comparison outcomes and individual insertion writes;
a constructor run checks rows and returns its input sequence on success. These
are model events, not claims about the comparison or write sequence executed
by CPython's `sorted` or Timsort.

The CPython host link remains open. It must justify that the pinned key
extraction, tuple comparison, built-in sorting, exact-type and Fraction
operations satisfy the stated observations. Lean derives consequences of the
abstract semantics and supplied premises; it does not verify CPython's C code.
-/
namespace E7CJointSortConstructorSemantics

open E7CJointAdmissionPythonOperations
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated

abbrev JointKey := E7CJointAdmissionPythonOperations.JointKey

/- The key term is the v0.15 `key(Graph)` identity:
   ("graph", ordered edges, tag-is-present, tag-or-empty-string).
   The existing comparison in #144 is its lexicographic decision procedure.
-/
def identityKey (graph : Graph) : Graph := graph

def cpythonIdentityCompare (left right : JointKey) : Ordering :=
  compareJointIdentity left right

structure CPythonSortOperationPremises where
  keyExtraction : Graph → Graph
  compare : JointKey → JointKey → Ordering
  keyExtractionRefines : ∀ graph, keyExtraction graph = identityKey graph
  comparisonRefines : ∀ left right,
    compare left right = compareJointIdentity left right

 /- Abstract insertion step: a model comparison result determines a list
   insertion. Non-less keeps the earlier key in place (stable ties). This does
   not assert CPython uses this comparison/write sequence. -/
inductive AbstractInsertTrace (compare : JointKey → JointKey → Ordering)
    (key : JointKey) : List JointKey → List JointKey → Prop where
  | empty : AbstractInsertTrace compare key [] [key]
  | before (head : JointKey) (tail : List JointKey)
      (comparison : compare key head = .lt) :
      AbstractInsertTrace compare key (head :: tail) (key :: head :: tail)
  | after (head : JointKey) (tail output : List JointKey)
      (comparison : compare key head ≠ .lt)
      (rest : AbstractInsertTrace compare key tail output) :
      AbstractInsertTrace compare key (head :: tail) (head :: output)

theorem insert_trace_refines_model
    {compare : JointKey → JointKey → Ordering} {key : JointKey}
    {input output : List JointKey}
    (trace : AbstractInsertTrace compare key input output)
    (comparisonRefines : compare = compareJointIdentity) :
  output = insertJointKey key input := by
  induction trace with
  | empty => rfl
  | before head tail h =>
      have hc : compareJointIdentity key head = .lt := by
        simpa [comparisonRefines] using h
      have hl : jointKeyLt key head = true := by
        simp [jointKeyLt, hc]
      simp [insertJointKey, hl]
  | @after head tail output h rest ih =>
      have hc : compareJointIdentity key head ≠ .lt := by
        simpa [comparisonRefines] using h
      have hl : jointKeyLt key head = false := by
        simp [jointKeyLt, hc]
      simp [insertJointKey, hl, ih]

/- The abstract list-sort operation is represented by sequential insertion
   traces. Its steps are individual comparisons and list writes, not an assumed
   sorted-list output. Host adequacy to CPython `sorted` is stated separately. -/
inductive AbstractIdentitySortTrace
    (compare : JointKey → JointKey → Ordering) :
    List JointKey → List JointKey → Prop where
  | nil : AbstractIdentitySortTrace compare [] []
  | cons (key : JointKey) (rest sortedRest output : List JointKey)
      (tail : AbstractIdentitySortTrace compare rest sortedRest)
      (insert : AbstractInsertTrace compare key sortedRest output) :
      AbstractIdentitySortTrace compare (key :: rest) output

theorem sort_trace_refines_model
    {compare : JointKey → JointKey → Ordering} {input output : List JointKey}
    (trace : AbstractIdentitySortTrace compare input output)
    (comparisonRefines : compare = compareJointIdentity) :
    output = sortJointKeys input := by
  induction trace with
  | nil => rfl
  | @cons key rest sortedRest output tail insert ih =>
      rw [insert_trace_refines_model insert comparisonRefines, ih]
      rfl

structure CPythonBuiltinSortAdequacy
    (ops : CPythonSortOperationPremises)
    (input : List JointKey) (pythonOutput : List JointKey) : Prop where
  keyCallsArePerElement : ∀ graph, ops.keyExtraction graph = identityKey graph
  comparisonCallsRefineTupleOrder : ∀ left right,
    ops.compare left right = compareJointIdentity left right
  observedComparisonsAndWrites :
    AbstractIdentitySortTrace ops.compare input pythonOutput

theorem cpython_sort_output_refines_model
    {ops : CPythonSortOperationPremises}
    {input pythonOutput : List JointKey}
    (adequacy : CPythonBuiltinSortAdequacy ops input pythonOutput) :
    pythonOutput = sortJointKeys input := by
  have hcompare : ops.compare = compareJointIdentity := by
    funext left right
    exact adequacy.comparisonCallsRefineTupleOrder left right
  exact sort_trace_refines_model adequacy.observedComparisonsAndWrites hcompare

/- Constructor rows are checked independently. The Boolean observations model
   Python's exact built-in type tests, arity checks, atom admission, and
   Fraction/nonzero checks at each row visit. -/
structure CPythonJointConstructorOps where
  exactPositiveInt : Nat → Bool
  exactAtomTuple : Row → Bool
  exactFraction : Row → Bool
  nonzeroFraction : Row → Bool
  exactOuterTuple : Bool
  canonicalOrder : List Row → Bool
  positiveIntRefines : ∀ arity, exactPositiveInt arity = decide (0 < arity)
  atomTupleRefines : ∀ row, exactAtomTuple row = true
  fractionRefines : ∀ row, exactFraction row = true
  nonzeroRefines : ∀ row, nonzeroFraction row = decide (row.coefficient ≠ 0)
  outerTupleRefines : exactOuterTuple = true

def constructorRowAccepted (ops : CPythonJointConstructorOps) (arity : Nat)
    (row : Row) : Bool :=
  ops.exactAtomTuple row && ops.exactFraction row &&
    ops.nonzeroFraction row && decide (arity = 2)

inductive JointRowVisitTrace (ops : CPythonJointConstructorOps) (arity : Nat) :
    List Row → Prop where
  | nil : JointRowVisitTrace ops arity []
  | cons (row : Row) (rest : List Row)
      (accepted : constructorRowAccepted ops arity row = true)
      (tail : JointRowVisitTrace ops arity rest) :
      JointRowVisitTrace ops arity (row :: rest)

def runConstructorRows (ops : CPythonJointConstructorOps) (arity : Nat)
    (rows : List Row) : Option (List Row) :=
  if ops.exactPositiveInt arity && ops.exactOuterTuple &&
      rows.all (constructorRowAccepted ops arity) && ops.canonicalOrder rows
  then some rows else none

structure CPythonJointConstructorTrace (ops : CPythonJointConstructorOps)
    (arity : Nat) (rows : List Row) : Prop where
  positiveArity : ops.exactPositiveInt arity = true
  outerTuple : ops.exactOuterTuple = true
  visitedRows : JointRowVisitTrace ops arity rows
  canonicalOrder : ops.canonicalOrder rows = true

theorem row_visit_trace_checks_all
    {ops : CPythonJointConstructorOps} {arity : Nat} {rows : List Row}
    (trace : JointRowVisitTrace ops arity rows) :
    rows.all (constructorRowAccepted ops arity) = true := by
  induction trace with
  | nil => rfl
  | @cons row rest accepted tail ih => simp [accepted, ih]

theorem constructor_trace_builds_rows
    {ops : CPythonJointConstructorOps} {arity : Nat} {rows : List Row}
    (trace : CPythonJointConstructorTrace ops arity rows) :
    runConstructorRows ops arity rows = some rows := by
  simp [runConstructorRows, trace.positiveArity, trace.outerTuple,
    row_visit_trace_checks_all trace.visitedRows, trace.canonicalOrder]

theorem constructor_rejects_bad_row
    (ops : CPythonJointConstructorOps) (arity : Nat) (row : Row)
    (rest : List Row)
    (positive : ops.exactPositiveInt arity = true)
    (bad : constructorRowAccepted ops arity row = false) :
    runConstructorRows ops arity (row :: rest) = none := by
  simp [runConstructorRows, positive, bad]

theorem constructor_rejects_noncanonical_rows
    (ops : CPythonJointConstructorOps) (arity : Nat) (rows : List Row)
    (positive : ops.exactPositiveInt arity = true)
    (outer : ops.exactOuterTuple = true)
    (visits : JointRowVisitTrace ops arity rows)
    (badOrder : ops.canonicalOrder rows = false) :
    runConstructorRows ops arity rows = none := by
  have hall := row_visit_trace_checks_all visits
  simp [runConstructorRows, positive, outer, hall, badOrder]

/-
A deliberately weaker pre-sort record. It contains only the ordered
dictionary-loop and nonzero-filter observations from the helper boundary; in
particular it has no complete sorted-output or constructor-copy equality.
-/
structure PreSortJointHelperTrace
    (ops : CPythonJointPrimitives) (parsed : List Row) : Type where
  finalDictionary : List JointEntry
  dictionaryLoop : JointDictionaryTrace ops parsed [] finalDictionary
  pythonFilteredKeys : List JointKey
  filterResult : pythonFilteredKeys = nonzeroKeys ops finalDictionary

def materializeJointRows (ops : CPythonJointPrimitives)
    (entries : List JointEntry) (keys : List JointKey) : List Row :=
  keys.map (entryRow ops entries)

theorem sort_trace_materializes_normalizer
    {ops : CPythonJointPrimitives} {parsed : List Row}
    (trace : PreSortJointHelperTrace ops parsed)
    (sortedKeys : List JointKey)
    (sortTrace : AbstractIdentitySortTrace cpythonIdentityCompare
      trace.pythonFilteredKeys sortedKeys) :
    materializeJointRows ops trace.finalDictionary sortedKeys =
      jointNormalizer ops parsed := by
  have hsorted : sortedKeys = sortJointKeys trace.pythonFilteredKeys :=
    sort_trace_refines_model sortTrace (by funext; rfl)
  have hdict : trace.finalDictionary = jointDictRun ops parsed [] :=
    dictionaryTrace_computes_run trace.dictionaryLoop
  unfold materializeJointRows jointNormalizer jointModelRows
  rw [hsorted, trace.filterResult, hdict]

theorem joint_constructor_trace_builds_normalizer
    {jops : CPythonJointPrimitives} {parsed : List Row}
    (jointTrace : PreSortJointHelperTrace jops parsed)
    (sortedKeys : List JointKey)
    (sortTrace : AbstractIdentitySortTrace cpythonIdentityCompare
      jointTrace.pythonFilteredKeys sortedKeys)
    (cops : CPythonJointConstructorOps)
    (constructorTrace : CPythonJointConstructorTrace cops 2
      (materializeJointRows jops jointTrace.finalDictionary sortedKeys)) :
    runConstructorRows cops 2
      (materializeJointRows jops jointTrace.finalDictionary sortedKeys) =
      some (jointNormalizer jops parsed) := by
  rw [constructor_trace_builds_rows constructorTrace]
  congr 1
  exact sort_trace_materializes_normalizer jointTrace sortedKeys sortTrace

theorem edge_AB_precedes_AC :
    compareGraphIdentity
      ({ ab := true, ac := false, bc := false, tag := none } : Graph)
      ({ ab := false, ac := true, bc := false, tag := none } : Graph) = .lt := rfl

theorem null_tag_precedes_empty_tag :
    compareGraphIdentity
      ({ ab := false, ac := false, bc := false, tag := none } : Graph)
      ({ ab := false, ac := false, bc := false, tag := some "" } : Graph) = .lt := rfl

theorem empty_edges_precede_AB :
    compareGraphIdentity
      ({ ab := false, ac := false, bc := false, tag := none } : Graph)
      ({ ab := true, ac := false, bc := false, tag := none } : Graph) = .lt := rfl

end E7CJointSortConstructorSemantics
