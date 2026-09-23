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
      change some ⟨encodeEdges ⟨ab, ac, bc, none⟩, none⟩ = some wire at admitted
      have hwire := Option.some.inj admitted
      rw [← hwire]
      cases ab <;> cases ac <;> cases bc <;>
        simp [decodeGraph, encodeEdges, validEdges]
  | some token =>
      cases nameResult : codec.encode token with
      | none =>
          change (codec.encode token).map
            (fun name => ⟨encodeEdges ⟨ab, ac, bc, some token⟩, some name⟩) =
            some wire at admitted
          rw [nameResult] at admitted
          cases admitted
      | some name =>
          have decoded := codec.roundtrip token name nameResult
          change (codec.encode token).map
            (fun name => ⟨encodeEdges ⟨ab, ac, bc, some token⟩, some name⟩) =
            some wire at admitted
          rw [nameResult] at admitted
          have hwire := Option.some.inj admitted
          rw [← hwire]
          cases ab <;> cases ac <;> cases bc <;>
            simp [decodeGraph, encodeEdges, validEdges, decoded]

theorem unknown_tag_rejected (codec : TagCodec) (wire : WireGraph)
    (name : String) (unknown : codec.decode name = none)
    (tag : wire.tag = some name) : decodeGraph codec wire = none := by
  rcases wire with ⟨edges, wireTag⟩
  change wireTag = some name at tag
  subst wireTag
  simp [decodeGraph, unknown]

/- The named fixture registry is deliberately small and edition-bound. The
generic law above applies to any separately admitted codec. -/
def fixtureCodec : TagCodec where
  encode := fun token =>
    if token = 0 then some "marked"
    else if token = 1 then some "phase-x"
    else none
  decode := fun name =>
    if name = "marked" then some 0
    else if name = "phase-x" then some 1
    else none
  roundtrip := by
    intro token name admitted
    by_cases zero : token = 0
    · subst token
      change some "marked" = some name at admitted
      have hn := Option.some.inj admitted
      subst name
      rfl
    · by_cases one : token = 1
      · subst token
        change some "phase-x" = some name at admitted
        have hn := Option.some.inj admitted
        subst name
        rfl
      · rw [if_neg zero, if_neg one] at admitted
        cases admitted

example : decodeGraph fixtureCodec ⟨["AC"], some "phase-x"⟩ =
    some ⟨false, true, false, some 1⟩ := by decide

example : decodeGraph fixtureCodec ⟨["AC"], some "other"⟩ = none := by decide

end E7CS1TagRegistry
