import E7CJointGraphBytecodeGenerated
import E7CJointSerializerOperationRelation

namespace E7CJointGraphBytecodeSemantics
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceSemantics
open E7CJointSerializerOperationRelation
open E7CJointGraphBytecodeSyntax E7CJointGraphBytecodeGenerated

/-- Only the two reads used by this helper are premises. Fraction/Joint reads,
constructor behavior, canonical edge order and resource budgets are unused. -/
structure GraphReads (read : Value → String → Option Value) : Prop where
  edges : ∀ graph, read (.graph graph) "edges" = some (graphItems graph)
  tag : ∀ graph, read (.graph graph) "tag" =
    some (.data (graph.tag.elim RawJson.null RawJson.string))

theorem native_graph_reads : GraphReads nativeAttributes :=
  ⟨by intro; rfl, by intro; rfl⟩

/-- All graph values under the declared instruction semantics. No completed
helper result, list-copy equality or execution trace is an input premise. -/
theorem graph_bytecode_exact {read : Value → String → Option Value}
    (attributes : GraphReads read) (graph : WireGraph) :
    execute read [.graph graph] graphProgram [] =
      some (.data (encodeRawGraph graph)) := by
  have edgesMap : graph.edges.mapM (fun edge => some (RawJson.string edge)) =
      some (graph.edges.map RawJson.string) :=
    mapM_of_some _ _ (by intro; rfl) graph.edges
  have distinctKeys : ("edges" : String) ≠ "tag" := by decide
  simp only [graphProgram, execute, step, attributes.edges, attributes.tag,
    graphItems, copy_tuple_exact, encodeRawGraph, toRaw,
    List.mapM_map, Function.comp_def, edgesMap, Option.bind_some,
    Option.map_some, Option.pure_def, List.getElem?_cons_zero,
    List.isEmpty_nil, if_neg distinctKeys]

/-- The ordered-append construction replaces the modeled list-copy result
premise. It still needs a separate native tuple/list adequacy theorem. -/
def tupleCopyOperations (read : Value → String → Option Value) : Operations where
  lookup := fun env index value => env[index]? = some value
  read := fun value name output => read value name = some output
  raw := fun value output => toRaw value = some output
  bind := fun arity value env scope => bindItems arity value env = some scope
  listCopy := fun cells output => output = .sequence (copyTuple cells)

theorem tuple_copy_operations_eq (read : Value → String → Option Value) :
    tupleCopyOperations read = modeledOperations read := by
  simp [tupleCopyOperations, modeledOperations, copy_tuple_exact]

theorem tuple_copy_operations_adequate (read : Value → String → Option Value) :
    PrimitiveAdequacy (tupleCopyOperations read) read := by
  rw [tuple_copy_operations_eq]
  exact modeled_operations_adequate read

theorem bytecode_normal_yields_graph_relation (graph : WireGraph) (output : Value)
    (normal : execute nativeAttributes [.graph graph] graphProgram [] = some output) :
    GraphNormal (tupleCopyOperations nativeAttributes) (.graph graph) output := by
  have encoded := graph_bytecode_exact native_graph_reads graph
  rw [encoded] at normal
  cases normal
  rw [tuple_copy_operations_eq]
  exact modeled_graph_normal graph

theorem changed_graph_output_rejected (graph : WireGraph) (output : Value)
    (different : output ≠ .data (encodeRawGraph graph)) :
    execute nativeAttributes [.graph graph] graphProgram [] ≠ some output := by
  rw [graph_bytecode_exact native_graph_reads]
  intro equal
  exact different (Option.some.inj equal).symm

example : execute nativeAttributes [] [.call 1, .returnValue] [] = none := rfl
example : execute nativeAttributes []
    [.loadGlobal "list" false, .returnValue] [] = none := rfl
example : execute nativeAttributes [] [.returnValue, .resume 0]
    [.value (.data .null)] = none := rfl

end E7CJointGraphBytecodeSemantics
