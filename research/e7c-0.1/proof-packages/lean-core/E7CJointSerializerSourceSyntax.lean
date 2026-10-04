import E7CJointRawJsonAdmission

/- A selected expression language for the three pinned serializer helpers.
Its evaluator is specified here, independently of the row encoder. It is not
a semantics of the complete Python language or an adequacy proof for CPython. -/
namespace E7CJointSerializerSourceSyntax
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission

inductive Value where
  | data (raw : RawJson)
  | graph (value : WireGraph)
  | fraction (value : Rat)
  | joint (arity : Nat) (rows : List WireRow)
  | sequence (values : List Value)

inductive Expr where
  | variable (index : Nat)
  | attribute (base : Expr) (name : String)
  | object (fields : List (String × Expr))
  | array (children : List Expr)
  | call (name : String) (args : List Expr)
  | comprehension (arity : Nat) (iterable body : Expr)
  deriving Repr

def toRaw : Value → Option RawJson
  | .data raw => some raw
  | .sequence values => RawJson.array <$> values.mapM toRaw
  | _ => none

def bindItems (arity : Nat) (value : Value) (environment : List Value) :
    Option (List Value) :=
  match arity, value with
  | 1, value => some (value :: environment)
  | 2, .sequence [left, right] => some (left :: right :: environment)
  | _, _ => none

def eval (readAttribute : Value → String → Option Value)
    (call : String → List Value → Option Value) :
    Nat → Expr → List Value → Option Value
  | 0, _, _ => none
  | _ + 1, .variable index, environment => environment[index]?
  | fuel + 1, .attribute base name, environment => do
      let value ← eval readAttribute call fuel base environment
      readAttribute value name
  | fuel + 1, .object fields, environment => do
      let output ← fields.mapM fun field => do
        let value ← eval readAttribute call fuel field.2 environment
        let raw ← toRaw value
        pure (field.1, raw)
      pure (.data (.object output))
  | fuel + 1, .array children, environment => do
      let output ← children.mapM fun child => do
        let value ← eval readAttribute call fuel child environment
        toRaw value
      pure (.data (.array output))
  | fuel + 1, .call name args, environment => do
      let values ← args.mapM (fun arg => eval readAttribute call fuel arg environment)
      call name values
  | fuel + 1, .comprehension arity iterable body, environment => do
      let .sequence items ← eval readAttribute call fuel iterable environment | none
      let output ← items.mapM fun item => do
        let scope ← bindItems arity item environment
        eval readAttribute call fuel body scope
      pure (.sequence output)

def listCall : String → List Value → Option Value
  | "list", [.sequence values] => some (.sequence values)
  | _, _ => none

def graphItems (graph : WireGraph) : Value :=
  .sequence (graph.edges.map (fun edge => .data (.string edge)))

def rowItems (row : WireRow) : Value :=
  .sequence [.sequence [.graph row.left, .graph row.right],
    .fraction row.coefficient]

structure AttributeContracts (readAttribute : Value → String → Option Value) : Prop where
  edges : ∀ graph, readAttribute (.graph graph) "edges" = some (graphItems graph)
  tag : ∀ graph, readAttribute (.graph graph) "tag" =
    some (.data (graph.tag.elim RawJson.null RawJson.string))
  numerator : ∀ coefficient, readAttribute (.fraction coefficient) "numerator" =
    some (.data (.integer coefficient.num))
  denominator : ∀ coefficient, readAttribute (.fraction coefficient) "denominator" =
    some (.data (.integer (Int.ofNat coefficient.den)))
  terms : ∀ arity rows, readAttribute (.joint arity rows) "terms" =
    some (.sequence (rows.map rowItems))
  arity : ∀ arity rows, readAttribute (.joint arity rows) "arity" =
    some (.data (.integer (Int.ofNat arity)))

def nativeAttributes : Value → String → Option Value
  | .graph graph, "edges" => some (graphItems graph)
  | .graph graph, "tag" => some (.data (graph.tag.elim RawJson.null RawJson.string))
  | .fraction coefficient, "numerator" => some (.data (.integer coefficient.num))
  | .fraction coefficient, "denominator" =>
      some (.data (.integer (Int.ofNat coefficient.den)))
  | .joint _ rows, "terms" => some (.sequence (rows.map rowItems))
  | .joint arity _, "arity" => some (.data (.integer (Int.ofNat arity)))
  | _, _ => none

theorem native_attributes_contracts : AttributeContracts nativeAttributes :=
  ⟨by intro; rfl, by intro; rfl, by intro; rfl,
   by intro; rfl, by intros; rfl, by intros; rfl⟩

end E7CJointSerializerSourceSyntax
