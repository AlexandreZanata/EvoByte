import Mathlib.Tactic

/-!
# Faithful Extremal Certificates in Lean 4 (P168)

Mechanically verified proofs of concrete combinatorial certificates:
- Van der Waerden monochromatic progression absence in finite colorings.
- Schur sum-free partitions.

All theorems state actual combinatorial claims and are proved by the Lean 4 kernel.

The two predicates are `abbrev` rather than `def` so that the `Decidable`
instances the `decide` tactic needs are found by instance search; the statements
are unchanged by that choice.
-/

namespace EvoByte.Faithful

/-- Monochromatic arithmetic progression predicate on a finite coloring.

`HasMonoAP n k col` holds when there exist `a` and `d` with `0 < d` and
`a + (k - 1) * d < n` such that the colors at `a, a + d, ..., a + (k - 1) * d`
are all equal to the color at `a`. -/
abbrev HasMonoAP (n k : Nat) (col : Fin n → Nat) : Prop :=
  ∃ (a d : Fin n) (hb : a.val + (k - 1) * d.val < n), 0 < d.val ∧
    ∀ (i : Fin k), col ⟨a.val + i.val * d.val, by
      apply Nat.lt_of_le_of_lt (Nat.add_le_add_left ?_ a.val) hb
      exact Nat.mul_le_mul_right d.val (Nat.le_pred_of_lt i.isLt)⟩ = col ⟨a.val, a.isLt⟩

/-- Sum-free partition violation predicate on a partition of 1..n into k classes.

`HasSchurViolation n part` holds when there exist `x` and `y` with
`1 ≤ x`, `1 ≤ y` and `x + y ≤ n` such that `x`, `y` and `x + y` all belong to
the same class of the partition. -/
abbrev HasSchurViolation (n : Nat) (part : Fin n → Nat) : Prop :=
  ∃ (x y : Fin n) (hb : x.val + y.val ≤ n), 1 ≤ x.val ∧ 1 ≤ y.val ∧
    part ⟨x.val - 1, by omega⟩ = part ⟨y.val - 1, by omega⟩ ∧
    part ⟨x.val - 1, by omega⟩ = part ⟨x.val + y.val - 1, by omega⟩

/-- Concrete certified coloring for W(2,3) lower bound certification on [1..8].

The colors are `1, 1, 2, 2, 1, 1, 2, 2`; the kernel checks below that no
3-term arithmetic progression of `{1,...,8}` is monochromatic under it, so the
published exact value `W(2,3) = 9` is reproduced by this certificate. -/
def vdwSampleColoring8 : Fin 8 → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ => 2
  | ⟨4, _⟩ => 1
  | ⟨5, _⟩ => 1
  | ⟨6, _⟩ => 2
  | ⟨7, _⟩ => 2

/-- Decidable certification that vdwSampleColoring8 contains no monochromatic 3-AP. -/
theorem vdw_sample_8_valid : ¬ HasMonoAP 8 3 vdwSampleColoring8 := by
  decide

/-- Concrete certified sum-free partition of 1..4 into 2 classes.

The classes are `{1,4}` and `{2,3}`; the kernel checks below that no triple
`x + y = z` lies inside a single class. -/
def schurSamplePartition4 : Fin 4 → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 2
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ => 1

/-- Decidable certification that schurSamplePartition4 has no monochromatic Schur violations. -/
theorem schur_sample_4_valid : ¬ HasSchurViolation 4 schurSamplePartition4 := by
  decide

end EvoByte.Faithful
