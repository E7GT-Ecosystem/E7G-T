import E7CJointSerializerSourceSemantics

/- Operation-local normal execution for the selected serializer grammar.
The relation is independent of eval and never assumes a completed serializer
result. Its index bounds expression nesting, not CPython steps or resources.
Actual CPython execution supplying this relation remains an open obligation. -/
namespace E7CJointSerializerOperationRelation
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceGenerated
open E7CJointSerializerSourceSemantics E7CJointCPythonNormalReturnTrace

structure Operations where
  lookup : List Value → Nat → Value → Prop
  read : Value → String → Value → Prop
  raw : Value → RawJson → Prop
  bind : Nat → Value → List Value → List Value → Prop
  listCopy : List Value → Value → Prop

/-- Each premise concerns a single primitive, not a helper's return value. -/
structure PrimitiveAdequacy (ops : Operations)
    (readAttribute : Value → String → Option Value) : Prop where
  lookup : ∀ env index value, ops.lookup env index value → env[index]? = some value
  read : ∀ value name output, ops.read value name output →
    readAttribute value name = some output
  raw : ∀ value output, ops.raw value output → toRaw value = some output
  bind : ∀ arity value env scope, ops.bind arity value env scope →
    bindItems arity value env = some scope
  listCopy : ∀ values output, ops.listCopy values output → output = .sequence values

inductive Visits {α β : Type} (relation : α → β → Prop) : List α → List β → Prop where
  | nil : Visits relation [] []
  | cons : relation a b → Visits relation as bs → Visits relation (a :: as) (b :: bs)

/-- Complete positional visits are explicit. A host iterator supplying these
visits without omission/reordering is not proved by defining this relation. -/
def Normal (ops : Operations) (invoke : String → List Value → Value → Prop) :
    Nat → Expr → List Value → Value → Prop
  | 0, _, _, _ => False
  | _ + 1, .variable index, env, output => ops.lookup env index output
  | fuel + 1, .attribute base name, env, output =>
      ∃ value, Normal ops invoke fuel base env value ∧ ops.read value name output
  | fuel + 1, .object fields, env, output =>
      ∃ raws : List RawJson,
        Visits (fun field raw => ∃ value,
          Normal ops invoke fuel field.2 env value ∧ ops.raw value raw) fields raws ∧
        output = .data (.object ((fields.map Prod.fst).zip raws))
  | fuel + 1, .array children, env, output =>
      ∃ raws : List RawJson,
        Visits (fun child raw => ∃ value,
          Normal ops invoke fuel child env value ∧ ops.raw value raw) children raws ∧
        output = .data (.array raws)
  | fuel + 1, .call name args, env, output =>
      ∃ values, Visits (fun arg value => Normal ops invoke fuel arg env value)
        args values ∧ invoke name values output
  | fuel + 1, .comprehension arity iterable body, env, output =>
      ∃ items values,
        Normal ops invoke fuel iterable env (.sequence items) ∧
        Visits (fun item value => ∃ scope,
          ops.bind arity item env scope ∧ Normal ops invoke fuel body scope value)
          items values ∧ output = .sequence values

theorem forall₂_mapM {α β : Type} {relation : α → β → Prop}
    {f : α → Option β} (localStep : ∀ a b, relation a b → f a = some b)
    {inputs : List α} {outputs : List β} (visits : Visits relation inputs outputs) :
    inputs.mapM f = some outputs := by
  induction visits with
  | nil => rfl
  | cons head tail ih => simp [List.mapM_cons, localStep _ _ head, ih]

theorem visits_preserve_length {α β : Type} {relation : α → β → Prop}
    {inputs : List α} {outputs : List β} (visits : Visits relation inputs outputs) :
    inputs.length = outputs.length := by
  induction visits with
  | nil => rfl
  | cons head tail ih => simp [ih]

theorem normal_sound {ops : Operations}
    {read : Value → String → Option Value} (primitives : PrimitiveAdequacy ops read)
    {invoke : String → List Value → Value → Prop}
    {call : String → List Value → Option Value}
    (calls : ∀ name args output, invoke name args output → call name args = some output)
    (fuel : Nat) : ∀ expr env output,
    Normal ops invoke fuel expr env output → eval read call fuel expr env = some output := by
  induction fuel with
  | zero => intro expr env output normal; exact False.elim normal
  | succ fuel ih =>
    intro expr env output normal
    cases expr with
    | «variable» index => exact primitives.lookup _ _ _ normal
    | «attribute» base name =>
      obtain ⟨value, child, observed⟩ := normal
      simp [eval, ih _ _ _ child, primitives.read _ _ _ observed]
    | object fields =>
      obtain ⟨raws, visits, rfl⟩ := normal
      have mapped : fields.mapM (fun field => do
          let value ← eval read call fuel field.2 env
          let raw ← toRaw value
          pure (field.1, raw)) = some ((fields.map Prod.fst).zip raws) := by
        induction visits with
        | nil => rfl
        | @cons field raw rest raws head tail tailProof =>
          obtain ⟨value, child, observed⟩ := head
          simp [List.mapM_cons, ih _ _ _ child, primitives.raw _ _ observed]
          simp at tailProof
          rw [tailProof]
          rfl
      simp only [eval]
      rw [mapped]
      rfl
    | array children =>
      obtain ⟨raws, visits, rfl⟩ := normal
      have mapped := forall₂_mapM (f := fun child => do
          let value ← eval read call fuel child env; toRaw value)
        (fun child raw observed => by
          obtain ⟨value, execution, observed⟩ := observed
          simp [ih _ _ _ execution, primitives.raw _ _ observed]) visits
      simp only [eval]
      rw [mapped]
      rfl
    | call name args =>
      obtain ⟨values, visits, invoked⟩ := normal
      have mapped := forall₂_mapM (fun arg value execution => ih arg env value execution) visits
      simp [eval, mapped, calls _ _ _ invoked]
    | comprehension arity iterable body =>
      obtain ⟨items, values, iterableRun, visits, rfl⟩ := normal
      have mapped := forall₂_mapM (f := fun item => do
          let scope ← bindItems arity item env; eval read call fuel body scope)
        (fun item value observed => by
          obtain ⟨scope, bound, execution⟩ := observed
          simp [primitives.bind _ _ _ _ bound, ih _ _ _ execution]) visits
      simp only [eval, ih _ _ _ iterableRun]
      change ((items.mapM (fun item => do
        let scope ← bindItems arity item env; eval read call fuel body scope)).bind
        (fun output => some (Value.sequence output))) = _
      rw [mapped]
      rfl

def listInvoke (ops : Operations) : String → List Value → Value → Prop
  | "list", [.sequence values], output => ops.listCopy values output
  | _, _, _ => False

def GraphNormal (ops : Operations) (input output : Value) : Prop :=
  Normal ops (listInvoke ops) 16 graphExpr [input] output

def graphInvoke (ops : Operations) : String → List Value → Value → Prop
  | "_graph", [input], output => GraphNormal ops input output
  | _, _, _ => False

def RowNormal (ops : Operations) (atoms coefficient output : Value) : Prop :=
  Normal ops (graphInvoke ops) 16 rowExpr [atoms, coefficient] output

def rowInvoke (ops : Operations) : String → List Value → Value → Prop
  | "_row", [atoms, coefficient], output => RowNormal ops atoms coefficient output
  | _, _, _ => False

def RowsNormal (ops : Operations) (input : Value) (output : RawJson) : Prop :=
  ∃ rows : List WireRow, input = .joint 2 rows ∧
    ops.read input "arity" (.data (.integer 2)) ∧
    ∃ value, Normal ops (rowInvoke ops) 16 rowsExpr [input] value ∧ ops.raw value output

theorem graph_normal_sound {ops : Operations} {read : Value → String → Option Value}
    (primitives : PrimitiveAdequacy ops read) {input output : Value}
    (normal : GraphNormal ops input output) : runGraph read input = some output := by
  apply normal_sound primitives _ 16 graphExpr [input] output normal
  intro name args output invoked
  unfold listInvoke at invoked
  split at invoked
  · simp only [listCall]
    rw [primitives.listCopy _ _ invoked]
  · exact False.elim invoked

theorem row_normal_sound {ops : Operations} {read : Value → String → Option Value}
    (primitives : PrimitiveAdequacy ops read) {atoms coefficient output : Value}
    (normal : RowNormal ops atoms coefficient output) :
    runRow read atoms coefficient = some output := by
  apply normal_sound primitives _ 16 rowExpr [atoms, coefficient] output normal
  intro name args output invoked
  unfold graphInvoke at invoked
  split at invoked
  · exact graph_normal_sound primitives invoked
  · exact False.elim invoked

theorem rows_normal_sound {ops : Operations} {read : Value → String → Option Value}
    (primitives : PrimitiveAdequacy ops read) {input : Value} {output : RawJson}
    (normal : RowsNormal ops input output) : runRows read input = some output := by
  obtain ⟨rows, rfl, guard, value, expression, materialized⟩ := normal
  have calls : ∀ name args output, rowInvoke ops name args output →
      rowCall read name args = some output := by
    intro name args output invoked
    unfold rowInvoke at invoked
    split at invoked
    · exact row_normal_sound primitives invoked
    · exact False.elim invoked
  have body := normal_sound primitives calls 16 rowsExpr _ _ expression
  simp [runRows, primitives.read _ _ _ guard, body, primitives.raw _ _ materialized]

/-- No supplied encoder result or completed RowsStatementTrace premise. The
premise is the operation relation, still not an actual CPython observation. -/
theorem operation_normal_yields_serializer_trace {ops : Operations}
    {read : Value → String → Option Value} (primitives : PrimitiveAdequacy ops read)
    (attributes : AttributeContracts read) {rows : List WireRow} {output : RawJson}
    (normal : RowsNormal ops (.joint 2 rows) output) : RowsStatementTrace rows output :=
  normal_source_run_yields_rows_statement_trace attributes (rows_normal_sound primitives normal)

theorem operation_normal_exact_rows {ops : Operations}
    {read : Value → String → Option Value} (primitives : PrimitiveAdequacy ops read)
    (attributes : AttributeContracts read) {rows : List WireRow} {output : RawJson}
    (normal : RowsNormal ops (.joint 2 rows) output) : output = encodeRawRows rows := by
  have observed := rows_normal_sound primitives normal
  rw [rows_source_run_exact attributes] at observed
  exact (Option.some.inj observed).symm

/-- Mathematical primitive relations, not imported CPython operations. -/
def modeledOperations (read : Value → String → Option Value) : Operations where
  lookup := fun env index value => env[index]? = some value
  read := fun value name output => read value name = some output
  raw := fun value output => toRaw value = some output
  bind := fun arity value env scope => bindItems arity value env = some scope
  listCopy := fun values output => output = .sequence values

theorem modeled_operations_adequate (read : Value → String → Option Value) :
    PrimitiveAdequacy (modeledOperations read) read :=
  ⟨by intros; assumption, by intros; assumption, by intros; assumption,
   by intros; assumption, by intros; assumption⟩

@[simp] theorem visits_nil_iff {α β : Type} (rel : α → β → Prop) :
    Visits rel [] [] ↔ True := ⟨fun _ => trivial, fun _ => .nil⟩

@[simp] theorem visits_cons_iff {α β : Type} (rel : α → β → Prop)
    (a : α) (b : β) (as : List α) (bs : List β) :
    Visits rel (a :: as) (b :: bs) ↔ rel a b ∧ Visits rel as bs := by
  constructor
  · intro h; cases h with | cons head tail => exact ⟨head, tail⟩
  · rintro ⟨head, tail⟩; exact .cons head tail

/-- Non-vacuity: every graph has an explicit local operation derivation. -/
theorem modeled_graph_normal (graph : WireGraph) :
    GraphNormal (modeledOperations nativeAttributes) (.graph graph)
      (.data (encodeRawGraph graph)) := by
  unfold GraphNormal graphExpr Normal
  refine ⟨[.array (graph.edges.map RawJson.string),
    graph.tag.elim RawJson.null RawJson.string], ?_, rfl⟩
  have materialized : toRaw (graphItems graph) =
      some (.array (graph.edges.map RawJson.string)) := by
    simpa [graphItems, List.map_map, Function.comp_def] using
      toRaw_data_sequence (graph.edges.map RawJson.string)
  refine .cons ⟨graphItems graph, ?_, materialized⟩
    (.cons ⟨.data (graph.tag.elim RawJson.null RawJson.string), ?_, by simp [modeledOperations, toRaw]⟩ .nil)
  · refine ⟨[graphItems graph], .cons ?_ .nil, rfl⟩
    exact ⟨.graph graph, rfl, rfl⟩
  · exact ⟨.graph graph, rfl, rfl⟩

theorem modeled_row_normal (row : WireRow) :
    RowNormal (modeledOperations nativeAttributes)
      (.sequence [.graph row.left, .graph row.right]) (.fraction row.coefficient)
      (.data (encodeRawRow row)) := by
  unfold RowNormal rowExpr Normal
  refine ⟨[.array [encodeRawGraph row.left, encodeRawGraph row.right],
    encodeRawFraction row.coefficient], ?_, rfl⟩
  refine .cons ⟨.sequence [.data (encodeRawGraph row.left),
    .data (encodeRawGraph row.right)], ?_, by simp [modeledOperations, toRaw]⟩
    (.cons ⟨.data (encodeRawFraction row.coefficient), ?_, by simp [modeledOperations, toRaw]⟩ .nil)
  · refine ⟨[.graph row.left, .graph row.right],
      [.data (encodeRawGraph row.left), .data (encodeRawGraph row.right)], rfl, ?_, rfl⟩
    refine .cons ?_ (.cons ?_ .nil)
    · refine ⟨[.graph row.left, .sequence [.graph row.left, .graph row.right],
        .fraction row.coefficient], rfl, ?_⟩
      exact ⟨[.graph row.left], .cons rfl .nil, modeled_graph_normal row.left⟩
    · refine ⟨[.graph row.right, .sequence [.graph row.left, .graph row.right],
        .fraction row.coefficient], rfl, ?_⟩
      exact ⟨[.graph row.right], .cons rfl .nil, modeled_graph_normal row.right⟩
  · refine ⟨[.integer row.coefficient.num, .integer (Int.ofNat row.coefficient.den)], ?_, rfl⟩
    refine .cons ⟨.data (.integer row.coefficient.num), ?_, by simp [modeledOperations, toRaw]⟩
      (.cons ⟨.data (.integer (Int.ofNat row.coefficient.den)), ?_, by simp [modeledOperations, toRaw]⟩ .nil)
    · exact ⟨.fraction row.coefficient, rfl, rfl⟩
    · exact ⟨.fraction row.coefficient, rfl, rfl⟩

theorem visits_map_both {α β γ : Type} (rel : β → γ → Prop) (f : α → β) (g : α → γ)
    (each : ∀ a, rel (f a) (g a)) (inputs : List α) :
    Visits rel (inputs.map f) (inputs.map g) := by
  induction inputs with
  | nil => exact .nil
  | cons head tail ih => exact .cons (each head) ih

/-- All finite modeled row lists supply a derivation; this is not a proof
that an actual CPython execution supplies it. No host resource bound follows. -/
theorem modeled_rows_normal (rows : List WireRow) :
    RowsNormal (modeledOperations nativeAttributes) (.joint 2 rows) (encodeRawRows rows) := by
  refine ⟨rows, rfl, rfl, .sequence (rows.map (fun row => .data (encodeRawRow row))), ?_, ?_⟩
  · unfold rowsExpr Normal
    refine ⟨rows.map rowItems, rows.map (fun row => .data (encodeRawRow row)), ?_, ?_, rfl⟩
    · simp [Normal, modeledOperations, nativeAttributes]
    · have visit : ∀ row : WireRow, ∃ scope,
        (modeledOperations nativeAttributes).bind 2 (rowItems row) [.joint 2 rows] scope ∧
        Normal (modeledOperations nativeAttributes) (rowInvoke (modeledOperations nativeAttributes))
          15 (.call "_row" [.variable 0, .variable 1]) scope (.data (encodeRawRow row)) := by
        intro row
        refine ⟨[.sequence [.graph row.left, .graph row.right],
          .fraction row.coefficient, .joint 2 rows], rfl, ?_⟩
        refine ⟨[.sequence [.graph row.left, .graph row.right], .fraction row.coefficient],
          ?_, modeled_row_normal row⟩
        simp [Normal, modeledOperations]
      exact visits_map_both _ _ _ visit rows
  · simpa [modeledOperations, encodeRawRows, List.map_map, Function.comp_def] using
      toRaw_data_sequence (rows.map encodeRawRow)

theorem operation_normal_derives_domain {ops : Operations}
    {read : Value → String → Option Value} (primitives : PrimitiveAdequacy ops read)
    (attributes : AttributeContracts read) {rows : List WireRow} {output : RawJson}
    (normal : RowsNormal ops (.joint 2 rows) output) :
    rawJsonWithinFuel 32 output = true ∧ rawJsonUniqueObjectKeys output = true :=
  normal_source_run_derives_domain attributes (rows_normal_sound primitives normal)

theorem changed_output_has_no_normal_derivation {ops : Operations}
    {read : Value → String → Option Value} (primitives : PrimitiveAdequacy ops read)
    (attributes : AttributeContracts read) {rows : List WireRow} {output : RawJson}
    (changed : output ≠ encodeRawRows rows) : ¬ RowsNormal ops (.joint 2 rows) output := by
  intro normal
  exact changed (operation_normal_exact_rows primitives attributes normal)

end E7CJointSerializerOperationRelation
