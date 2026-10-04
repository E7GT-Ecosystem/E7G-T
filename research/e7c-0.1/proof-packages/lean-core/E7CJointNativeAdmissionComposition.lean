import E7CJointAdmissionStatementTrace
import E7CJointNativeSerializerCapture
import E7CJointNativeAdmissionCapture

/- Composition retains the inherited raw decoder's Rat-division axiom
dependencies. Its audit is separate from the strict integer receipt above. -/
namespace E7CJointNativeAdmissionComposition
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointAdmissionExecution
open E7CJointAdmissionStatementTrace
open E7CJointNativeSerializerCapture
open E7CJointNativeAdmissionCapture

structure ConfigCapture where
  input : RawJson
  fields : List (String × RawJson)
  edgesOperand : List String
  tagOperand : Option String
  output : WireGraph

structure ConfigReceipt (capture : ConfigCapture) : Prop where
  objectRead : capture.input = .object capture.fields
  keyCheck : exactKeys capture.fields ["edges", "tag"] = true
  edgesRead : lookupField capture.fields "edges" =
    some (.array (capture.edgesOperand.map RawJson.string))
  tagRead : lookupField capture.fields "tag" = some (selectedTagRaw capture.tagOperand)
  canonicalOperand : canonicalEdges capture.edgesOperand = true
  outputFields : capture.output = ⟨capture.edgesOperand, capture.tagOperand⟩

private theorem string_array_decode (values : List String) :
    decodeStringList (.array (values.map RawJson.string)) = some values := by
  have decoded : decodeStringValues (values.map RawJson.string) = some values := by
    induction values with
    | nil => rfl
    | cons head tail ih => simp [decodeStringValues, ih]
  exact decoded

def config_trace (capture : ConfigCapture) (checked : ConfigReceipt capture) :
    GraphAdmissionStatementTrace capture.input where
  fields := capture.fields
  objectRead := checked.objectRead
  keyCheck := checked.keyCheck
  rawEdges := .array (capture.edgesOperand.map RawJson.string)
  rawTag := selectedTagRaw capture.tagOperand
  edgesFieldRead := checked.edgesRead
  tagFieldRead := checked.tagRead
  edges := capture.edgesOperand
  stringArrayDecode := string_array_decode _
  edgeOrderCheck := checked.canonicalOperand
  tag := capture.tagOperand
  tagDecode := by cases capture.tagOperand <;> rfl

theorem config_trace_output (capture : ConfigCapture) (checked : ConfigReceipt capture) :
    (config_trace capture checked).output = capture.output := checked.outputFields.symm

theorem checked_config_decodes (capture : ConfigCapture) (checked : ConfigReceipt capture) :
    decodeGraph capture.input = some capture.output := by
  rw [← config_trace_output capture checked]
  exact graph_decoder_follows_statement_trace _

structure FractionCapture where
  input : RawJson
  fields : List (String × RawJson)
  numeratorOperand : Int
  denominatorOperand : Int
  output : Rat

structure FractionReceipt (capture : FractionCapture) : Prop where
  objectRead : capture.input = .object capture.fields
  keyCheck : exactKeys capture.fields ["numerator", "denominator"] = true
  numeratorRead : lookupField capture.fields "numerator" = some (.integer capture.numeratorOperand)
  denominatorRead : lookupField capture.fields "denominator" = some (.integer capture.denominatorOperand)
  denominatorPositive : capture.denominatorOperand > 0
  numeratorNonzero : capture.numeratorOperand ≠ 0
  nativeFields : fractionFieldsChecked capture.numeratorOperand capture.denominatorOperand
    capture.output.num capture.output.den = true

/-- The rational constructor equation is derived from the strict integer
cross-product receipt, rather than supplied as an additional result premise. -/
theorem checked_fraction_value (capture : FractionCapture) (checked : FractionReceipt capture) :
    capture.output = (capture.numeratorOperand : Rat) / (capture.denominatorOperand : Rat) := by
  have fields := checked_fraction_fields capture.numeratorOperand capture.denominatorOperand
    capture.output.num capture.output.den checked.nativeFields
  have inputDenNZ : capture.denominatorOperand ≠ 0 := Int.ne_of_gt fields.1
  have outputDenNZ : (capture.output.den : Int) ≠ 0 :=
    Int.ne_of_gt (Int.natCast_pos.mpr fields.2.2.1)
  calc
    capture.output = Rat.divInt capture.output.num (capture.output.den : Int) :=
      (Rat.num_divInt_den capture.output).symm
    _ = Rat.divInt capture.numeratorOperand capture.denominatorOperand :=
      (Rat.divInt_eq_divInt_iff outputDenNZ inputDenNZ).2 fields.2.2.2
    _ = (capture.numeratorOperand : Rat) / (capture.denominatorOperand : Rat) :=
      Rat.divInt_eq_div _ _

def fraction_trace (capture : FractionCapture) (checked : FractionReceipt capture) :
    FractionAdmissionStatementTrace capture.input where
  fields := capture.fields
  objectRead := checked.objectRead
  keyCheck := checked.keyCheck
  rawNumerator := .integer capture.numeratorOperand
  rawDenominator := .integer capture.denominatorOperand
  numeratorFieldRead := checked.numeratorRead
  denominatorFieldRead := checked.denominatorRead
  numerator := capture.numeratorOperand
  numeratorExactInt := rfl
  denominator := capture.denominatorOperand
  denominatorExactInt := rfl
  positiveDenominator := checked.denominatorPositive
  nonzeroNumerator := checked.numeratorNonzero

theorem fraction_trace_output (capture : FractionCapture) (checked : FractionReceipt capture) :
    (fraction_trace capture checked).output = capture.output := (checked_fraction_value capture checked).symm

theorem checked_fraction_decodes (capture : FractionCapture) (checked : FractionReceipt capture) :
    decodeFractionPair capture.input = some capture.output := by
  rw [← fraction_trace_output capture checked]
  exact fraction_decoder_follows_statement_trace _

structure RowCapture where
  input : RawJson
  fields : List (String × RawJson)
  left : ConfigCapture
  right : ConfigCapture
  fraction : FractionCapture

def RowCapture.output (capture : RowCapture) : WireRow :=
  ⟨capture.left.output, capture.right.output, capture.fraction.output⟩

structure RowReceipt (capture : RowCapture) : Prop where
  objectRead : capture.input = .object capture.fields
  keyCheck : exactKeys capture.fields ["atoms", "coefficient"] = true
  atomsRead : lookupField capture.fields "atoms" = some (.array [capture.left.input, capture.right.input])
  coefficientRead : lookupField capture.fields "coefficient" = some capture.fraction.input
  left : ConfigReceipt capture.left
  right : ConfigReceipt capture.right
  fraction : FractionReceipt capture.fraction

def row_trace (capture : RowCapture) (checked : RowReceipt capture) :
    JointRowAdmissionStatementTrace capture.input where
  fields := capture.fields
  objectRead := checked.objectRead
  keyCheck := checked.keyCheck
  rawAtoms := .array [capture.left.input, capture.right.input]
  rawCoefficient := capture.fraction.input
  atomsFieldRead := checked.atomsRead
  coefficientFieldRead := checked.coefficientRead
  rawLeft := capture.left.input
  rawRight := capture.right.input
  twoCoordinateArrayRead := rfl
  leftGraph := config_trace capture.left checked.left
  rightGraph := config_trace capture.right checked.right
  coefficient := fraction_trace capture.fraction checked.fraction

theorem row_trace_output (capture : RowCapture) (checked : RowReceipt capture) :
    (row_trace capture checked).output = capture.output := by
  change ⟨(config_trace capture.left checked.left).output,
    (config_trace capture.right checked.right).output,
    (fraction_trace capture.fraction checked.fraction).output⟩ = capture.output
  rw [config_trace_output, config_trace_output, fraction_trace_output]
  rfl

def AllRowReceipts : List RowCapture → Prop
  | [] => True
  | capture :: rest => RowReceipt capture ∧ AllRowReceipts rest

theorem checked_row_visits (captures : List RowCapture) (checked : AllRowReceipts captures) :
    RawRowsVisitTrace (captures.map RowCapture.input) (captures.map RowCapture.output) := by
  induction captures with
  | nil => exact .nil
  | cons capture rest ih =>
      change RowReceipt capture ∧ AllRowReceipts rest at checked
      simp only [List.map_cons]
      rw [← row_trace_output capture checked.1]
      exact .cons (row_trace capture checked.1) (ih checked.2)

structure PrefixReceipt (raw : RawJson) (captures : List RowCapture)
    (actualParsed : List WireRow) : Prop where
  arrayRead : raw = .array (captures.map RowCapture.input)
  rowBound : captures.length ≤ 64
  rows : AllRowReceipts captures
  parsedCallOperand : actualParsed = captures.map RowCapture.output

def rows_trace {raw : RawJson} {captures : List RowCapture} {actualParsed : List WireRow}
    (checked : PrefixReceipt raw captures actualParsed) : RawRowsAdmissionStatementTrace raw where
  rawRows := captures.map RowCapture.input
  arrayRead := checked.arrayRead
  rows := captures.map RowCapture.output
  visits := checked_row_visits captures checked.rows
  capCheck := by simpa using checked.rowBound

/-- The complete raw-row result follows from checked local constructor
operands/results. No decoder result or prebuilt statement trace is a premise. -/
theorem checked_prefix_decoder {raw : RawJson} {captures : List RowCapture}
    {actualParsed : List WireRow} (checked : PrefixReceipt raw captures actualParsed) :
    decodeJointRows raw = some actualParsed := by
  rw [checked.parsedCallOperand]
  exact rows_decoder_follows_statement_trace (rows_trace checked)

theorem checked_prefix_domain {raw : RawJson} {captures : List RowCapture}
    {actualParsed : List WireRow} (checked : PrefixReceipt raw captures actualParsed) :
    CanonicalWireRows actualParsed ∧ rawJsonWithinFuel 32 raw = true ∧
      rawJsonUniqueObjectKeys raw = true := by
  refine ⟨?_, rows_statement_trace_within_fuel (rows_trace checked),
    rows_statement_trace_unique_keys (rows_trace checked)⟩
  rw [checked.parsedCallOperand]
  exact rows_statement_trace_canonical (rows_trace checked)

structure ConstructorCapture where
  arity : Nat
  storedArity : Nat
  inputRows : List WireRow
  outputRows : List WireRow
  inputTupleRef : Nat
  outputTupleRef : Nat
  cells : CopyCapture

structure ConstructorReceipt (capture : ConstructorCapture) : Prop where
  binary : capture.arity = 2
  arityCopied : capture.storedArity = capture.arity
  tupleCopied : capture.outputTupleRef = capture.inputTupleRef
  cellsCopied : sameCells capture.cells.inputRefs capture.cells.outputRefs = true
  completeCells : capture.cells.inputRefs.length = capture.inputRows.length
  fieldsCopied : capture.outputRows = capture.inputRows

/-- Pointwise logical-token and literal preservation of the observed Joint
constructor operand. This says nothing about how joint aggregated/sorted it. -/
theorem checked_constructor_preserves (capture : ConstructorCapture)
    (checked : ConstructorReceipt capture) :
    capture.storedArity = 2 ∧ capture.outputRows = capture.inputRows ∧
      capture.cells.outputRefs = capture.cells.inputRefs ∧
      capture.cells.outputRefs.length = capture.outputRows.length := by
  have cells := same_cells_exact _ _ checked.cellsCopied
  refine ⟨checked.arityCopied.trans checked.binary, checked.fieldsCopied, cells, ?_⟩
  rw [cells, checked.fieldsCopied]
  exact checked.completeCells

theorem changed_constructor_field_rejected (capture : ConstructorCapture)
    (changed : capture.outputRows ≠ capture.inputRows) : ¬ ConstructorReceipt capture := by
  intro checked
  exact changed checked.fieldsCopied

theorem changed_fraction_value_rejected (capture : FractionCapture)
    (changed : capture.output ≠
      (capture.numeratorOperand : Rat) / (capture.denominatorOperand : Rat)) :
    ¬ FractionReceipt capture := by
  intro checked
  exact changed (checked_fraction_value capture checked)

end E7CJointNativeAdmissionComposition
