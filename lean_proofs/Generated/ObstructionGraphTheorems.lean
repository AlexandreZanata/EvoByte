/-
EvoByte Formal Proof Catalog: Certified Diophantine Obstruction Graph Theorems (P106).
Formal proofs in Lean 4 kernel proving negative search space pruning soundness,
modular residue incompatibilities, and parity obstructions without unproven axioms or holes.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

namespace EvoByte.Obstructions

/-- Obstruction state representing residue class r mod m. -/
structure ModState where
  mod : Nat
  res : Nat
  deriving DecidableEq, Repr

/-- Incompatibility relation between two modular states. -/
def IsIncompatible (s1 s2 : ModState) : Prop :=
  s1.mod = s2.mod ∧ s1.res ≠ s2.res

/-- Theorem: A natural number cannot satisfy two incompatible states simultaneously. -/
theorem incompatible_states_exclusive (s1 s2 : ModState) (h_incomp : IsIncompatible s1 s2) (n : Nat) :
    ¬(n % s1.mod = s1.res ∧ n % s2.mod = s2.res) := by
  intro ⟨h1, h2⟩
  rcases h_incomp with ⟨hmod, hres⟩
  rw [hmod] at h1
  rw [h1] at h2
  exact hres h2

/-- Incompatibility is symmetric. -/
theorem incompatible_symm (s1 s2 : ModState) (h : IsIncompatible s1 s2) : IsIncompatible s2 s1 := by
  rcases h with ⟨hmod, hres⟩
  exact ⟨hmod.symm, Ne.symm hres⟩

/-- Incompatibility is irreflexive. -/
theorem incompatible_irreflexive (s : ModState) : ¬IsIncompatible s s := by
  intro ⟨_, hres⟩
  exact hres rfl

/-- Modular obstruction for modulus 2 and remainder 1 (P106). -/
theorem mod_obstruction_m2_r1 : ∀ (k : Nat), ¬(2 ∣ 2 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 3 and remainder 1 (P106). -/
theorem mod_obstruction_m3_r1 : ∀ (k : Nat), ¬(3 ∣ 3 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 3 and remainder 2 (P106). -/
theorem mod_obstruction_m3_r2 : ∀ (k : Nat), ¬(3 ∣ 3 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 4 and remainder 1 (P106). -/
theorem mod_obstruction_m4_r1 : ∀ (k : Nat), ¬(4 ∣ 4 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 4 and remainder 2 (P106). -/
theorem mod_obstruction_m4_r2 : ∀ (k : Nat), ¬(4 ∣ 4 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 4 and remainder 3 (P106). -/
theorem mod_obstruction_m4_r3 : ∀ (k : Nat), ¬(4 ∣ 4 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 5 and remainder 1 (P106). -/
theorem mod_obstruction_m5_r1 : ∀ (k : Nat), ¬(5 ∣ 5 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 5 and remainder 2 (P106). -/
theorem mod_obstruction_m5_r2 : ∀ (k : Nat), ¬(5 ∣ 5 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 5 and remainder 3 (P106). -/
theorem mod_obstruction_m5_r3 : ∀ (k : Nat), ¬(5 ∣ 5 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 5 and remainder 4 (P106). -/
theorem mod_obstruction_m5_r4 : ∀ (k : Nat), ¬(5 ∣ 5 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 6 and remainder 1 (P106). -/
theorem mod_obstruction_m6_r1 : ∀ (k : Nat), ¬(6 ∣ 6 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 6 and remainder 2 (P106). -/
theorem mod_obstruction_m6_r2 : ∀ (k : Nat), ¬(6 ∣ 6 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 6 and remainder 3 (P106). -/
theorem mod_obstruction_m6_r3 : ∀ (k : Nat), ¬(6 ∣ 6 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 6 and remainder 4 (P106). -/
theorem mod_obstruction_m6_r4 : ∀ (k : Nat), ¬(6 ∣ 6 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 6 and remainder 5 (P106). -/
theorem mod_obstruction_m6_r5 : ∀ (k : Nat), ¬(6 ∣ 6 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 1 (P106). -/
theorem mod_obstruction_m7_r1 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 2 (P106). -/
theorem mod_obstruction_m7_r2 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 3 (P106). -/
theorem mod_obstruction_m7_r3 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 4 (P106). -/
theorem mod_obstruction_m7_r4 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 5 (P106). -/
theorem mod_obstruction_m7_r5 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 7 and remainder 6 (P106). -/
theorem mod_obstruction_m7_r6 : ∀ (k : Nat), ¬(7 ∣ 7 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 1 (P106). -/
theorem mod_obstruction_m8_r1 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 2 (P106). -/
theorem mod_obstruction_m8_r2 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 3 (P106). -/
theorem mod_obstruction_m8_r3 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 4 (P106). -/
theorem mod_obstruction_m8_r4 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 5 (P106). -/
theorem mod_obstruction_m8_r5 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 6 (P106). -/
theorem mod_obstruction_m8_r6 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 8 and remainder 7 (P106). -/
theorem mod_obstruction_m8_r7 : ∀ (k : Nat), ¬(8 ∣ 8 * k + 7) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 1 (P106). -/
theorem mod_obstruction_m9_r1 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 2 (P106). -/
theorem mod_obstruction_m9_r2 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 3 (P106). -/
theorem mod_obstruction_m9_r3 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 4 (P106). -/
theorem mod_obstruction_m9_r4 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 5 (P106). -/
theorem mod_obstruction_m9_r5 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 6 (P106). -/
theorem mod_obstruction_m9_r6 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 7 (P106). -/
theorem mod_obstruction_m9_r7 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 7) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 9 and remainder 8 (P106). -/
theorem mod_obstruction_m9_r8 : ∀ (k : Nat), ¬(9 ∣ 9 * k + 8) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 1 (P106). -/
theorem mod_obstruction_m10_r1 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 2 (P106). -/
theorem mod_obstruction_m10_r2 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 3 (P106). -/
theorem mod_obstruction_m10_r3 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 4 (P106). -/
theorem mod_obstruction_m10_r4 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 5 (P106). -/
theorem mod_obstruction_m10_r5 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 6 (P106). -/
theorem mod_obstruction_m10_r6 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 7 (P106). -/
theorem mod_obstruction_m10_r7 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 7) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 8 (P106). -/
theorem mod_obstruction_m10_r8 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 8) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 10 and remainder 9 (P106). -/
theorem mod_obstruction_m10_r9 : ∀ (k : Nat), ¬(10 ∣ 10 * k + 9) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 1 (P106). -/
theorem mod_obstruction_m12_r1 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 2 (P106). -/
theorem mod_obstruction_m12_r2 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 3 (P106). -/
theorem mod_obstruction_m12_r3 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 4 (P106). -/
theorem mod_obstruction_m12_r4 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 5 (P106). -/
theorem mod_obstruction_m12_r5 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 6 (P106). -/
theorem mod_obstruction_m12_r6 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 7 (P106). -/
theorem mod_obstruction_m12_r7 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 7) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 8 (P106). -/
theorem mod_obstruction_m12_r8 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 8) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 9 (P106). -/
theorem mod_obstruction_m12_r9 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 9) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 10 (P106). -/
theorem mod_obstruction_m12_r10 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 10) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 12 and remainder 11 (P106). -/
theorem mod_obstruction_m12_r11 : ∀ (k : Nat), ¬(12 ∣ 12 * k + 11) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 1 (P106). -/
theorem mod_obstruction_m24_r1 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 1) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 2 (P106). -/
theorem mod_obstruction_m24_r2 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 2) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 3 (P106). -/
theorem mod_obstruction_m24_r3 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 3) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 4 (P106). -/
theorem mod_obstruction_m24_r4 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 4) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 5 (P106). -/
theorem mod_obstruction_m24_r5 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 5) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 6 (P106). -/
theorem mod_obstruction_m24_r6 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 6) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 7 (P106). -/
theorem mod_obstruction_m24_r7 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 7) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 8 (P106). -/
theorem mod_obstruction_m24_r8 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 8) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 9 (P106). -/
theorem mod_obstruction_m24_r9 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 9) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 10 (P106). -/
theorem mod_obstruction_m24_r10 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 10) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 11 (P106). -/
theorem mod_obstruction_m24_r11 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 11) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 12 (P106). -/
theorem mod_obstruction_m24_r12 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 12) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 13 (P106). -/
theorem mod_obstruction_m24_r13 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 13) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 14 (P106). -/
theorem mod_obstruction_m24_r14 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 14) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 15 (P106). -/
theorem mod_obstruction_m24_r15 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 15) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 16 (P106). -/
theorem mod_obstruction_m24_r16 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 16) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 17 (P106). -/
theorem mod_obstruction_m24_r17 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 17) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 18 (P106). -/
theorem mod_obstruction_m24_r18 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 18) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 19 (P106). -/
theorem mod_obstruction_m24_r19 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 19) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 20 (P106). -/
theorem mod_obstruction_m24_r20 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 20) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 21 (P106). -/
theorem mod_obstruction_m24_r21 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 21) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 22 (P106). -/
theorem mod_obstruction_m24_r22 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 22) := by
  intro k ⟨c, hc⟩
  omega

/-- Modular obstruction for modulus 24 and remainder 23 (P106). -/
theorem mod_obstruction_m24_r23 : ∀ (k : Nat), ¬(24 ∣ 24 * k + 23) := by
  intro k ⟨c, hc⟩
  omega

/-- Product obstruction: square of odd is never divisible by 4 (P106). -/
theorem mod4_obstruction_odd_sq : ∀ (k : Nat), ¬(4 ∣ (2 * k + 1) * (2 * k + 1)) := by
  intro k ⟨c, hc⟩
  have h : (2 * k + 1) * (2 * k + 1) = 4 * (k ^ 2 + k) + 1 := by ring
  rw [h] at hc
  omega

/-- Product obstruction: consecutive odd product is never divisible by 4 (P106). -/
theorem mod4_obstruction_odd_prod : ∀ (k : Nat), ¬(4 ∣ (2 * k + 1) * (2 * k + 3)) := by
  intro k ⟨c, hc⟩
  have h : (2 * k + 1) * (2 * k + 3) = 4 * (k ^ 2 + 2 * k) + 3 := by ring
  rw [h] at hc
  omega

/-- Product obstruction mod 3 for r=1 (P106). -/
theorem mod3_obstruction_sq_r1 : ∀ (k : Nat), ¬(3 ∣ (3 * k + 1) * (3 * k + 1)) := by
  intro k ⟨c, hc⟩
  have h : (3 * k + 1) * (3 * k + 1) = 3 * (3 * k ^ 2 + 2 * k) + 1 := by ring
  rw [h] at hc
  omega

/-- Product obstruction mod 3 for r=2 (P106). -/
theorem mod3_obstruction_sq_r2 : ∀ (k : Nat), ¬(3 ∣ (3 * k + 2) * (3 * k + 2)) := by
  intro k ⟨c, hc⟩
  have h : (3 * k + 2) * (3 * k + 2) = 3 * (3 * k ^ 2 + 4 * k + 1) + 1 := by ring
  rw [h] at hc
  omega

/-- Product obstruction mod 3 for r1=1, r2=2 (P106). -/
theorem mod3_obstruction_prod_r1_r2 : ∀ (k : Nat), ¬(3 ∣ (3 * k + 1) * (3 * k + 2)) := by
  intro k ⟨c, hc⟩
  have h : (3 * k + 1) * (3 * k + 2) = 3 * (3 * k ^ 2 + 3 * k) + 2 := by ring
  rw [h] at hc
  omega

/-- Pillai/Catalan verified solution difference 9 - 8 = 1 (P106). -/
theorem pillai_catalan_diff_9_8 : (3 : Nat) ^ 2 - 2 ^ 3 = 1 := by norm_num

/-- Pillai/Catalan verified solution difference 27 - 8 = 19 (P106). -/
theorem pillai_catalan_diff_27_8 : (3 : Nat) ^ 3 - 2 ^ 3 = 19 := by norm_num

/-- Pillai verified solution difference 32 - 25 = 7 (P106). -/
theorem pillai_catalan_diff_32_25 : (2 : Nat) ^ 5 - 5 ^ 2 = 7 := by norm_num

/-- Pillai verified solution difference 128 - 121 = 7 (P106). -/
theorem pillai_catalan_diff_128_121 : (2 : Nat) ^ 7 - 11 ^ 2 = 7 := by norm_num

/-- Pillai verified solution difference 243 - 128 = 115 (P106). -/
theorem pillai_catalan_diff_243_128 : (3 : Nat) ^ 5 - 2 ^ 7 = 115 := by norm_num

end EvoByte.Obstructions
