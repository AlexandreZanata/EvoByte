import Mathlib.Tactic.Ring

/-
EvoByte Inductive and Presburger Baseline Lemmas in Nat (P81).
Certified structural induction and linear arithmetic.
-/

/-- Structural induction on Nat: addition with zero right-identity. -/
theorem nat_add_zero_ind : ∀ (n : Nat), n + 0 = n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => rw [Nat.add_zero]

/-- Structural induction on Nat: addition with zero left-identity. -/
theorem nat_zero_add_ind : ∀ (n : Nat), 0 + n = n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => omega

/-- Successor is strictly positive in Nat. -/
theorem nat_succ_pos : ∀ (n : Nat), n + 1 > 0 := by
  intro n
  omega

/-- Successor is greater than or equal to 1 in Nat. -/
theorem nat_succ_ge_one : ∀ (n : Nat), n + 1 ≥ 1 := by
  intro n
  omega

/-- Addition with a strictly positive term is strictly positive. -/
theorem nat_add_pos_left : ∀ (a b : Nat), a > 0 → a + b > 0 := by
  intro a b ha
  omega

/-- Addition with a strictly positive right term is strictly positive. -/
theorem nat_add_pos_right : ∀ (a b : Nat), b > 0 → a + b > 0 := by
  intro a b hb
  omega

/-- Truncated subtraction in Nat does not exceed the minuend. -/
theorem nat_sub_le : ∀ (a b : Nat), a - b ≤ a := by
  intro a b
  omega

/-- Transitivity of order relation in Nat. -/
theorem nat_le_trans : ∀ (a b c : Nat), a ≤ b → b ≤ c → a ≤ c := by
  intro a b c hab hbc
  omega

/-- Product of strictly positive natural numbers is strictly positive. -/
theorem nat_mul_pos : ∀ (a b : Nat), a > 0 → b > 0 → a * b > 0 := by
  intro a b ha hb
  exact Nat.mul_pos ha hb

/-- Strict positivity of denominator 4k + 3 for all k in Nat. -/
theorem es_denom_4k3_pos : ∀ (k : Nat), 4 * k + 3 > 0 := by
  intro k
  omega

/-- Lower bound on denominator 4k + 3 when k >= 1. -/
theorem es_denom_4k3_ge_7 : ∀ (k : Nat), k ≥ 1 → 4 * k + 3 ≥ 7 := by
  intro k hk
  omega

/-- Strict positivity of denominator 3k + 2 for all k in Nat. -/
theorem es_denom_3k2_pos : ∀ (k : Nat), 3 * k + 2 > 0 := by
  intro k
  omega

/-- Lower bound on denominator 3k + 2 when k >= 1. -/
theorem es_denom_3k2_ge_5 : ∀ (k : Nat), k ≥ 1 → 3 * k + 2 ≥ 5 := by
  intro k hk
  omega

/-- Strict positivity of denominator 8k + 5 for all k in Nat. -/
theorem es_denom_8k5_pos : ∀ (k : Nat), 8 * k + 5 > 0 := by
  intro k
  omega

/-- Lower bound on denominator 8k + 5 when k >= 1. -/
theorem es_denom_8k5_ge_13 : ∀ (k : Nat), k ≥ 1 → 8 * k + 5 ≥ 13 := by
  intro k hk
  omega

/-- Strict positivity of denominator 24k + 1 for all k in Nat. -/
theorem es_denom_24k1_pos : ∀ (k : Nat), 24 * k + 1 > 0 := by
  intro k
  omega

/-- Lower bound on denominator 24k + 1 when k >= 1. -/
theorem es_denom_24k1_ge_25 : ∀ (k : Nat), k ≥ 1 → 24 * k + 1 ≥ 25 := by
  intro k hk
  omega

/-- Strict positivity of denominator 120k + 2 for all k in Nat. -/
theorem es_denom_120k2_pos : ∀ (k : Nat), 120 * k + 2 > 0 := by
  intro k
  omega

/-- Lower bound on denominator 120k + 2 when k >= 1. -/
theorem es_denom_120k2_ge_122 : ∀ (k : Nat), k ≥ 1 → 120 * k + 2 ≥ 122 := by
  intro k hk
  omega

/-- Strict positivity of denominator 840k + 1 for all k in Nat. -/
theorem es_denom_840k1_pos : ∀ (k : Nat), 840 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of coordinate k + 1 for all k in Nat. -/
theorem es_coord_x_pos : ∀ (k : Nat), k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of coordinate 2k + 1 for all k in Nat. -/
theorem es_coord_2k1_pos : ∀ (k : Nat), 2 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of coordinate 3k + 1 for all k in Nat. -/
theorem es_coord_3k1_pos : ∀ (k : Nat), 3 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of coordinate 6k + 1 for all k in Nat. -/
theorem es_coord_6k1_pos : ∀ (k : Nat), 6 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of coordinate 12k + 1 for all k in Nat. -/
theorem es_coord_12k1_pos : ∀ (k : Nat), 12 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of denominator 5k + 1 for all k in Nat. -/
theorem sier_denom_5k1_pos : ∀ (k : Nat), 5 * k + 1 > 0 := by
  intro k
  omega

/-- Strict positivity of denominator 5k + 2 for all k in Nat. -/
theorem sier_denom_5k2_pos : ∀ (k : Nat), 5 * k + 2 > 0 := by
  intro k
  omega

/-- Strict positivity of denominator 5k + 3 for all k in Nat. -/
theorem sier_denom_5k3_pos : ∀ (k : Nat), 5 * k + 3 > 0 := by
  intro k
  omega

/-- Strict positivity of denominator 5k + 4 for all k in Nat. -/
theorem sier_denom_5k4_pos : ∀ (k : Nat), 5 * k + 4 > 0 := by
  intro k
  omega

/-- Strict positivity of denominator 120k + r whenever remainder r > 0. -/
theorem sier_denom_120k_rem : ∀ (k r : Nat), r > 0 → 120 * k + r > 0 := by
  intro k r hr
  omega

/-- Diophantine cross-product positivity. -/
theorem dioph_denom_mul_pos : ∀ (x y : Nat), x > 0 → y > 0 → x * y > 0 := by
  intro x y hx hy
  exact Nat.mul_pos hx hy

/-- Diophantine cross-sum positivity for positive coordinates. -/
theorem dioph_cross_sum_pos : ∀ (x y z : Nat), x > 0 → y > 0 → z > 0 → x * y + y * z + x * z > 0 := by
  intro x y z hx hy hz
  have h1 : x * y > 0 := Nat.mul_pos hx hy
  omega

/-- Lower bound on coordinate sum x + y + z in Nat when all >= 1. -/
theorem dioph_coord_bound_sum : ∀ (x y z : Nat), x ≥ 1 → y ≥ 1 → z ≥ 1 → x + y + z ≥ 3 := by
  intro x y z hx hy hz
  omega
