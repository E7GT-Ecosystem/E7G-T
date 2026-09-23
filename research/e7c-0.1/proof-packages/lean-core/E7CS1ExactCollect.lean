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

/- Equality of values is cross multiplication, independent of the particular
positive denominator chosen for an internal fraction. -/
def Equivalent (left right : Fraction) : Prop :=
  left.numerator * (right.denominator : Int) =
    right.numerator * (left.denominator : Int)

theorem equivalent_refl (value : Fraction) : Equivalent value value := rfl

theorem equivalent_symm {left right : Fraction}
    (h : Equivalent left right) : Equivalent right left := h.symm

theorem equivalent_trans {left middle right : Fraction}
    (first : Equivalent left middle)
    (second : Equivalent middle right) : Equivalent left right := by
  have middleDenominatorNonzero : (middle.denominator : Int) ≠ 0 :=
    Int.ofNat_ne_zero.mpr (Nat.ne_of_gt middle.positive)
  apply Int.eq_of_mul_eq_mul_left middleDenominatorNonzero
  calc
    (middle.denominator : Int) *
        (left.numerator * (right.denominator : Int)) =
        (left.numerator * (middle.denominator : Int)) *
          (right.denominator : Int) := by ac_rfl
    _ = (middle.numerator * (left.denominator : Int)) *
          (right.denominator : Int) :=
            congrArg (fun x : Int => x * (right.denominator : Int)) first
    _ = (middle.numerator * (right.denominator : Int)) *
          (left.denominator : Int) := by ac_rfl
    _ = (right.numerator * (middle.denominator : Int)) *
          (left.denominator : Int) :=
            congrArg (fun x : Int => x * (left.denominator : Int)) second
    _ = (middle.denominator : Int) *
          (right.numerator * (left.denominator : Int)) := by ac_rfl

theorem add_comm_equivalent (left right : Fraction) :
    Equivalent (add left right) (add right left) := by
  simp [Equivalent, add, Int.add_comm, Int.mul_comm, Nat.mul_comm]

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

/- Every entry retained by an arbitrary finite collection has a nonzero
coefficient, even after intermediate cancellations. -/
def zeroFree : Collected → Prop
  | [] => True
  | (_, amount) :: rest => isZero amount = false ∧ zeroFree rest

theorem insert_zeroFree (graph : Graph) (amount : Fraction)
    (state : Collected) (h : zeroFree state) :
    zeroFree (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;> simp [insert, hz, zeroFree]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change isZero coefficient = false ∧ zeroFree rest at h
      obtain ⟨hcoeff, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, zeroFree, hrest]
      · simp [insert, heq, zeroFree, hcoeff, ih hrest]

theorem foldl_zeroFree (rows : List (Graph × Fraction))
    (state : Collected) (h : zeroFree state) :
    zeroFree (rows.foldl (fun acc row => insert row.1 row.2 acc) state) := by
  induction rows generalizing state with
  | nil => simpa using h
  | cons row rest ih =>
      simp only [List.foldl_cons]
      exact ih _ (insert_zeroFree row.1 row.2 state h)

theorem collect_zeroFree (rows : List (Graph × Fraction)) :
    zeroFree (collect rows) := by
  exact foldl_zeroFree rows [] trivial

/- keyAbsent and uniqueKeys express the support invariant without imposing
an ordering on graph keys. -/
def keyAbsent (graph : Graph) : Collected → Prop
  | [] => True
  | (existing, _) :: rest => existing ≠ graph ∧ keyAbsent graph rest

def uniqueKeys : Collected → Prop
  | [] => True
  | (existing, _) :: rest => keyAbsent existing rest ∧ uniqueKeys rest

theorem insert_keeps_absent (forbidden graph : Graph) (amount : Fraction)
    (state : Collected) (h : keyAbsent forbidden state)
    (different : graph ≠ forbidden) :
    keyAbsent forbidden (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;>
        simp [insert, hz, keyAbsent, different]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change existing ≠ forbidden ∧ keyAbsent forbidden rest at h
      obtain ⟨hhead, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, keyAbsent, hhead, hrest]
      · simp [insert, heq, keyAbsent, hhead, ih hrest]

theorem insert_uniqueKeys (graph : Graph) (amount : Fraction)
    (state : Collected) (h : uniqueKeys state) :
    uniqueKeys (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;>
        simp [insert, hz, uniqueKeys, keyAbsent]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change keyAbsent existing rest ∧ uniqueKeys rest at h
      obtain ⟨habsent, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, uniqueKeys, habsent, hrest]
      · have hkept := insert_keeps_absent existing graph amount rest habsent heq
        simp [insert, heq, uniqueKeys, hkept, ih hrest]

theorem foldl_uniqueKeys (rows : List (Graph × Fraction))
    (state : Collected) (h : uniqueKeys state) :
    uniqueKeys (rows.foldl (fun acc row => insert row.1 row.2 acc) state) := by
  induction rows generalizing state with
  | nil => simpa using h
  | cons row rest ih =>
      simp only [List.foldl_cons]
      exact ih _ (insert_uniqueKeys row.1 row.2 state h)

theorem collect_uniqueKeys (rows : List (Graph × Fraction)) :
    uniqueKeys (collect rows) := by
  exact foldl_uniqueKeys rows [] trivial

theorem same_graph_opposites_cancel (graph : Graph) (amount : Fraction)
    (nonzero : isZero amount = false) :
    collect [(graph, amount), (graph, opposite amount)] = [] := by
  simp [collect, insert, nonzero, opposite_sum_is_zero]

/- The same rational value can arrive with different unreduced denominators. -/
def half : Fraction := ⟨1, 2, by decide⟩
def negativeHalfUnreduced : Fraction := ⟨-2, 4, by decide⟩

theorem negative_half_equivalent_to_opposite :
    Equivalent negativeHalfUnreduced (opposite half) := by
  unfold Equivalent negativeHalfUnreduced half opposite
  decide

theorem cross_denominator_cancellation (graph : Graph) :
    collect [(graph, half), (graph, negativeHalfUnreduced)] = [] := by
  have firstNonzero : isZero half = false := rfl
  have exactCancel : isZero (add half negativeHalfUnreduced) = true := rfl
  simp [collect, insert, firstNonzero, exactCancel]

theorem colliding_nonzero_pair (graph : Graph) (left right : Fraction)
    (leftNonzero : left.numerator ≠ 0)
    (sumNonzero : (add left right).numerator ≠ 0) :
    collect [(graph, left), (graph, right)] =
      [(graph, add left right)] := by
  simp [collect, insert, isZero, leftNonzero, sumNonzero]

end E7CS1ExactCollect
