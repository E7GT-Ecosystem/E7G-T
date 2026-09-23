import E7CS1ExactCollect

/-!
Selected S1/FG3 wire bridge for the fixed AB/AC/BC graph labels and the
registered None/"marked" tag pair. Python admits other strings; this module
does not silently identify them with this two-tag Lean fragment. Coefficient
wire pairs are unreduced; value comparison uses cross multiplication.
-/

namespace E7CS1FG3Codec

open E7CS1FG3Single E7CS1ExactCollect

structure WireCoefficient where
  numerator : Int
  denominator : Nat
  deriving DecidableEq, Repr

def encodeCoefficient (value : Fraction) : WireCoefficient :=
  ⟨value.numerator, value.denominator⟩

def decodeCoefficient (wire : WireCoefficient) : Option Fraction :=
  if h : 0 < wire.denominator then
    some ⟨wire.numerator, wire.denominator, h⟩
  else none

theorem coefficient_roundtrip (value : Fraction) :
    decodeCoefficient (encodeCoefficient value) = some value := by
  cases value with
  | mk numerator denominator positive =>
      simp [decodeCoefficient, encodeCoefficient, positive]

theorem zero_denominator_rejected (numerator : Int) :
    decodeCoefficient ⟨numerator, 0⟩ = none := by
  simp [decodeCoefficient]

/- Rat's own denominator is strictly positive. This maps the earlier Lean
pre-collection row carrier into the constructive fraction collector. It is
not a theorem about Rat.add, Python Fraction, or source evaluation. -/
def fromRat (value : Rat) : Fraction :=
  ⟨value.num, value.den, value.den_pos⟩

def fromRatRows (rows : List (Graph × Rat)) : Collected :=
  rows.map (fun row => (row.1, fromRat row.2))

theorem fromRatRows_length (rows : List (Graph × Rat)) :
    (fromRatRows rows).length = rows.length := by
  simp [fromRatRows]

theorem fromRatRows_perm {rows reordered : List (Graph × Rat)}
    (h : rows.Perm reordered) (target : Graph) :
    Equivalent (observed target (collect (fromRatRows rows)))
      (observed target (collect (fromRatRows reordered))) := by
  exact collect_perm_observed target (h.map _)

structure WireGraph where
  edges : List String
  tag : Option String
  deriving DecidableEq, Repr

/- Only the registered two-tag fixture fragment has an encoding here. -/
structure RegisteredGraph where
  graph : Graph
  tagAllowed : graph.tag = none ∨ graph.tag = some 0

def encodeEdges (graph : Graph) : List String :=
  (if graph.ab then ["AB"] else []) ++
  (if graph.ac then ["AC"] else []) ++
  (if graph.bc then ["BC"] else [])

def encodeGraph (value : RegisteredGraph) : WireGraph :=
  ⟨encodeEdges value.graph,
   value.graph.tag.map (fun _ => "marked")⟩

def validEdges (edges : List String) : Bool :=
  edges.all (fun edge => edge == "AB" || edge == "AC" || edge == "BC")

def decodeGraph (wire : WireGraph) : Option Graph :=
  if validEdges wire.edges then
    match wire.tag with
    | none => some ⟨wire.edges.contains "AB", wire.edges.contains "AC",
                    wire.edges.contains "BC", none⟩
    | some tag =>
        if tag = "marked" then
          some ⟨wire.edges.contains "AB", wire.edges.contains "AC",
                wire.edges.contains "BC", some 0⟩
        else none
  else none

theorem registered_graph_roundtrip (value : RegisteredGraph) :
    decodeGraph (encodeGraph value) = some value.graph := by
  rcases value with ⟨⟨ab, ac, bc, tag⟩, allowed⟩
  rcases allowed with h | h
  · change tag = none at h
    subst tag
    cases ab <;> cases ac <;> cases bc <;> decide
  · change tag = some 0 at h
    subst tag
    cases ab <;> cases ac <;> cases bc <;> decide

example : decodeGraph ⟨["BC", "AB", "AB"], some "marked"⟩ =
    some ⟨true, false, true, some 0⟩ := by decide

example : decodeGraph ⟨["BD"], none⟩ = none := by decide

/- The selected cross-denominator cancellation matches Python Fraction's
value-level zero without asserting equal unreduced representations. -/
def markedAB : Graph := ⟨true, false, false, some 0⟩

example : observed markedAB
    (collect [(markedAB, half), (markedAB, negativeHalfUnreduced)]) =
    zero := by rw [cross_denominator_cancellation]; rfl

end E7CS1FG3Codec
