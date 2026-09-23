import E7CS1FG3Rows

/-!
Constructive, unreduced exact rational collection of finite FG3 images.
Positive denominators and integer arithmetic avoid classical choice in the
executable collector. A canonical reduced wire encoding is not proved here.
-/

namespace E7CS1ExactCollect

open E7CS1FG3Single

structure Fraction where
  numerator : Int
  denominator : Nat
  positive : 0 < denominator

def opposite (value : Fraction) : Fraction :=
  ⟨-value.numerator, value.denominator, value.positive⟩

/- Cross multiplication represents exact addition. The output fraction may
be unreduced; its denominator remains strictly positive. -/
def add (left right : Fraction) : Fraction :=
  ⟨left.numerator * (right.denominator : Int) +
     right.numerator * (left.denominator : Int),
   left.denominator * right.denominator,
   Nat.mul_pos left.positive right.positive⟩

def isZero (value : Fraction) : Bool := value.numerator == 0

theorem opposite_sum_has_zero_numerator (value : Fraction) :
    (add value (opposite value)).numerator = 0 := by
  simpa [add, opposite, Int.neg_mul] using
    (Int.add_neg_cancel_right 0
      (value.numerator * (value.denominator : Int)))

theorem opposite_sum_is_zero (value : Fraction) :
    isZero (add value (opposite value)) = true := by
  unfold isZero
  rw [opposite_sum_has_zero_numerator]
  rfl

abbrev Collected := List (Graph × Fraction)

/- Store each exact target graph once. On a collision add coefficients and
remove the target if their sum is zero. Input admission precedes this step. -/
def insert (graph : Graph) (amount : Fraction) : Collected → Collected
  | [] => if isZero amount then [] else [(graph, amount)]
  | (existing, coefficient) :: rest =>
      if graph = existing then
        let total := add coefficient amount
        if isZero total then rest else (existing, total) :: rest
      else (existing, coefficient) :: insert graph amount rest

def collect (rows : List (Graph × Fraction)) : Collected :=
  rows.foldl (fun state row => insert row.1 row.2 state) []

theorem same_graph_opposites_cancel (graph : Graph) (amount : Fraction)
    (nonzero : isZero amount = false) :
    collect [(graph, amount), (graph, opposite amount)] = [] := by
  simp [collect, insert, nonzero, opposite_sum_is_zero]

theorem colliding_nonzero_pair (graph : Graph) (left right : Fraction)
    (leftNonzero : left.numerator ≠ 0)
    (sumNonzero : (add left right).numerator ≠ 0) :
    collect [(graph, left), (graph, right)] =
      [(graph, add left right)] := by
  simp [collect, insert, isZero, leftNonzero, sumNonzero]

end E7CS1ExactCollect
