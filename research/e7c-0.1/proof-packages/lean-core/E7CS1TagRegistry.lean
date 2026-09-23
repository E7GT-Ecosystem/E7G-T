import E7CS1FG3Codec

/-!
An edition-bound injection from Lean's nominal tag tokens into FG3 string
tags. The registry carries its own left-inverse proof. No particular string
is treated as universally canonical, and unknown strings fail admission.
-/

namespace E7CS1TagRegistry

open E7CS1FG3Single E7CS1FG3Codec

structure TagCodec where
  encode : Nat → Option String
  decode : String → Option Nat
  roundtrip : ∀ (token : Nat) (name : String),
    encode token = some name → decode name = some token

def encodeGraph (codec : TagCodec) (graph : Graph) : Option WireGraph :=
  match graph.tag with
  | none => some ⟨encodeEdges graph, none⟩
  | some token =>
      (codec.encode token).map (fun name => ⟨encodeEdges graph, some name⟩)

def decodeGraph (codec : TagCodec) (wire : WireGraph) : Option Graph :=
  if validEdges wire.edges then
    match wire.tag with
    | none => some ⟨wire.edges.contains "AB", wire.edges.contains "AC",
                    wire.edges.contains "BC", none⟩
    | some name =>
        (codec.decode name).map (fun token =>
          ⟨wire.edges.contains "AB", wire.edges.contains "AC",
           wire.edges.contains "BC", some token⟩)
  else none

theorem graph_roundtrip (codec : TagCodec) (graph : Graph)
    (wire : WireGraph) (admitted : encodeGraph codec graph = some wire) :
    decodeGraph codec wire = some graph := by
  rcases graph with ⟨ab, ac, bc, tag⟩
  cases tag with
  | none =>
      simp [encodeGraph] at admitted
      subst wire
      cases ab <;> cases ac <;> cases bc <;>
        simp [decodeGraph, encodeEdges, validEdges]
  | some token =>
      cases nameResult : codec.encode token with
      | none => simp [encodeGraph, nameResult] at admitted
      | some name =>
          have decoded := codec.roundtrip token name nameResult
          simp [encodeGraph, nameResult] at admitted
          subst wire
          cases ab <;> cases ac <;> cases bc <;>
            simp [decodeGraph, encodeEdges, validEdges, decoded]

theorem unknown_tag_rejected (codec : TagCodec) (wire : WireGraph)
    (name : String) (unknown : codec.decode name = none)
    (tag : wire.tag = some name) : decodeGraph codec wire = none := by
  rcases wire with ⟨edges, wireTag⟩
  change wireTag = some name at tag
  subst wireTag
  simp [decodeGraph, unknown]

end E7CS1TagRegistry
