import E7CS1FG3Codec

/-!
Finite admitted FG3 support rows, strict scan, and exact internal collection.
The bridge transports rows without asserting a new theorem about Rat addition
or equivalence with Python's Fraction normalization.
-/

namespace E7CS1RowsCollect

open E7CS1FG3Single E7CS1FG3Rows E7CS1FG3Codec E7CS1ExactCollect

def compatible (rows : List AdmittedRow) : Prop :=
  ∀ row, row ∈ rows → row.left.tag = row.right.tag

theorem compatible_firstBad_none :
    (rows : List AdmittedRow) → compatible rows → firstBad rows = none
  | [], _ => rfl
  | row :: rest, h => by
      have head : row.left.tag = row.right.tag := h row (by simp)
      have tail : compatible rest :=
        fun item member => h item (by simp [member])
      simp [firstBad, head, compatible_firstBad_none rest tail]

theorem compatible_scan_success (rows : List AdmittedRow)
    (h : compatible rows) :
    (scan rows.length rows).terminal = .success (rows.map image) := by
  simpa [expected, compatible_firstBad_none rows h] using
    congrArg Scan.terminal (sufficient_visits_match_source rows)

theorem compatible_perm {rows reordered : List AdmittedRow}
    (h : rows.Perm reordered) (valid : compatible rows) :
    compatible reordered := by
  intro row member
  exact valid row (h.mem_iff.mpr member)

def collectRows (rows : List AdmittedRow) : Collected :=
  collect (fromRatRows (rows.map image))

theorem collectRows_zeroFree (rows : List AdmittedRow) :
    zeroFree (collectRows rows) := collect_zeroFree _

theorem collectRows_uniqueKeys (rows : List AdmittedRow) :
    uniqueKeys (collectRows rows) := collect_uniqueKeys _

theorem finite_admitted_rows (rows reordered : List AdmittedRow)
    (valid : compatible rows) (permutation : rows.Perm reordered)
    (target : Graph) :
    (scan rows.length rows).terminal = .success (rows.map image) ∧
    (scan reordered.length reordered).terminal =
      .success (reordered.map image) ∧
    zeroFree (collectRows rows) ∧
    uniqueKeys (collectRows rows) ∧
    Equivalent (observed target (collectRows rows))
      (observed target (collectRows reordered)) := by
  refine ⟨compatible_scan_success rows valid,
    compatible_scan_success reordered (compatible_perm permutation valid),
    collectRows_zeroFree rows, collectRows_uniqueKeys rows, ?_⟩
  exact fromRatRows_perm (permutation.map image) target

end E7CS1RowsCollect
