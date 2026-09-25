/-!
Selected MSC-B1/0.1 finite source fixture `MSC-OBSTRUCTION-01`.
The three admitted two-point carriers are encoded as Bool, with source "0"
as false and "1" as true. The fixture's common comparison carrier V is
also Bool. Five of its six maps are identity and `p-rt-flip` negates T. The theorem
is a finite fixture property, not MSC/0.1 adequacy or Python correctness.
-/

namespace E7CMSCObstruction

def pRS (s : Bool) : Bool := s
def cRS (r : Bool) : Bool := r
def pST (t : Bool) : Bool := t
def cST (s : Bool) : Bool := s
def pRTFlip (t : Bool) : Bool := !t
def cRT (r : Bool) : Bool := r

def linkRS (r s : Bool) : Prop := pRS s = cRS r
def linkST (s t : Bool) : Prop := pST t = cST s
def linkRT (r t : Bool) : Prop := pRTFlip t = cRT r

theorem each_declared_link_satisfiable :
    (∃ r s : Bool, linkRS r s) ∧
    (∃ s t : Bool, linkST s t) ∧
    (∃ r t : Bool, linkRT r t) := by
  exact ⟨⟨false, false, rfl⟩, ⟨false, false, rfl⟩, ⟨true, false, rfl⟩⟩

theorem no_global_compatible_family :
    ¬ ∃ r s t : Bool, linkRS r s ∧ linkST s t ∧ linkRT r t := by
  intro ⟨r, s, t, hrs, hst, hrt⟩
  cases r <;> cases s <;> cases t <;>
    simp_all [linkRS, linkST, linkRT, pRS, cRS, pST, cST, pRTFlip, cRT]

theorem linkwise_does_not_imply_global :
    ((∃ r s : Bool, linkRS r s) ∧
     (∃ s t : Bool, linkST s t) ∧
     (∃ r t : Bool, linkRT r t)) ∧
    ¬ (∃ r s t : Bool, linkRS r s ∧ linkST s t ∧ linkRT r t) := by
  exact ⟨each_declared_link_satisfiable, no_global_compatible_family⟩

end E7CMSCObstruction
