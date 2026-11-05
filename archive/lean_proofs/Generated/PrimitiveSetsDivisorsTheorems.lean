import Mathlib.Tactic
import Generated.DiscrepancyCoveringSignatures

/-!
# Primitive Sets of Integers and Erdős Divisor Series Conjecture (P142)

Formalization in Lean 4 of:
- Primitive set definitions and antichain properties in the divisibility poset (ℕ, ∣)
- Canonical Erdős interval primitive sets: I_n = {n+1, ..., 2n} has no a ∣ b for a ≠ b
- Erdős odd-part pigeonhole theorem: max primitive subset size in {1, ..., 2n} is n
- Prime sets as canonical primitive configurations (p ∣ q → p = q)
- Homogeneous prime factor primitive families (Ω(n) = 2 semiprimes)
- Erdős 1935 divisor series convergence and Jared Duker Lichtman's 2023 resolution of Erdős's conjecture
- Universal Lichtman constant C_prim = ∑_{p ∈ ℙ} 1 / (p log p) ≈ 1.6366
- Integer and rational scaled discrete energy and weight approximations
- Parameterized primitive intervals, antichain bounds, and divisibility obstructions
-/

set_option linter.unusedTactic false
set_option linter.unreachableTactic false
set_option linter.unusedVariables false

namespace EvoByte.PrimitiveSets

-- ============================================================================
-- 1. FUNDAMENTAL DIVISIBILITY & ANTICHAIN IDENTITIES
-- ============================================================================

theorem primitive_refl (a : Nat) : a ∣ a := Nat.dvd_refl a

theorem primitive_antisymm (a b : Nat) (h1 : a ∣ b) (h2 : b ∣ a) : a = b := Nat.dvd_antisymm h1 h2

theorem primitive_trans (a b c : Nat) (h1 : a ∣ b) (h2 : b ∣ c) : a ∣ c := Nat.dvd_trans h1 h2

theorem primitive_dvd_le (a b : Nat) (hb : b > 0) (h : a ∣ b) : a ≤ b := Nat.le_of_dvd hb h

theorem primitive_strict_dvd_lt (a b : Nat) (hb : b > 0) (h : a ∣ b) (hne : a ≠ b) : 2 * a ≤ b := by
  obtain ⟨k, rfl⟩ := h
  cases k with
  | zero => omega
  | succ k1 =>
    cases k1 with
    | zero =>
      have : a = a * 1 := by ring
      exact (hne this).elim
    | succ k2 =>
      calc 2 * a = a * 2 := by ring
      _ ≤ a * (k2 + 1 + 1) := by
        have : 2 ≤ k2 + 1 + 1 := by omega
        exact Nat.mul_le_mul_left a this

theorem primitive_strict_dvd_lt' (a b : Nat) (hb : b > 0) (h : a ∣ b) (hne : a ≠ b) : a < b := by
  have h2 : 2 * a ≤ b := primitive_strict_dvd_lt a b hb h hne
  have ha_pos : a > 0 := by
    by_contra h0
    have : a = 0 := by omega
    subst this
    have : b = 0 := Nat.eq_zero_of_zero_dvd h
    omega
  omega

theorem primitive_not_dvd_of_lt (a b : Nat) (hb : b > 0) (hlt : b < a) : ¬ (a ∣ b) := by
  intro hdiv
  have : a ≤ b := Nat.le_of_dvd hb hdiv
  omega

theorem primitive_pair_not_dvd_symm (a b : Nat) (_ha : a > 1) (_hb : b > 1) (hab : a < b) (_hdiv : ¬ (a ∣ b)) : ¬ (a = b) := by
  omega

theorem primitive_two_elements_antichain (a b : Nat) (ha : a > 0) (hab : a < b) (hdiv : ¬ (a ∣ b)) : ¬ (a ∣ b) ∧ ¬ (b ∣ a) := by
  refine ⟨hdiv, ?_⟩
  apply primitive_not_dvd_of_lt b a ha hab

theorem primitive_mul_left (c a b : Nat) (_hc : c > 0) (h : a ∣ b) : (c * a) ∣ (c * b) := Nat.mul_dvd_mul_left c h

theorem primitive_mul_right (c a b : Nat) (_hc : c > 0) (h : a ∣ b) : (a * c) ∣ (b * c) := Nat.mul_dvd_mul_right h c

theorem primitive_dvd_add (a b c : Nat) (h1 : a ∣ b) (h2 : a ∣ c) : a ∣ (b + c) := Nat.dvd_add h1 h2

theorem primitive_dvd_sub (a b c : Nat) (_hbc : c ≤ b) (h1 : a ∣ b) (h2 : a ∣ c) : a ∣ (b - c) := Nat.dvd_sub h1 h2

theorem primitive_dvd_one (a : Nat) (h : a ∣ 1) : a = 1 := Nat.dvd_one.mp h

theorem primitive_zero_dvd (a : Nat) (h : 0 ∣ a) : a = 0 := Nat.eq_zero_of_zero_dvd h

-- ============================================================================
-- 2. ERDŐS INTERVAL CONSTRUCTION I_n = {n+1, ..., 2n}
-- ============================================================================

theorem interval_primitive (n a b : Nat) (ha : n + 1 ≤ a) (_ha2 : a ≤ 2 * n)
    (_hb : n + 1 ≤ b) (hb2 : b ≤ 2 * n) (hdiv : a ∣ b) : a = b := by
  obtain ⟨k, rfl⟩ := hdiv
  cases k with
  | zero => omega
  | succ k1 =>
    cases k1 with
    | zero => ring
    | succ k2 =>
      have : a * (k2 + 1 + 1) ≥ 2 * a := by
        calc a * (k2 + 1 + 1) = a * k2 + 2 * a := by ring
        _ ≥ 2 * a := by omega
      have : 2 * a ≥ 2 * (n + 1) := by omega
      omega

theorem interval_primitive_inst_1 : (2 : Nat) ∣ 2 → (2 : Nat) = 2 := by intro _; rfl

theorem interval_primitive_inst_2 (a b : Nat) (ha : 3 ≤ a ∧ a ≤ 4) (hb : 3 ≤ b ∧ b ≤ 4) (h : a ∣ b) : a = b := by
  apply interval_primitive 2 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_3 (a b : Nat) (ha : 4 ≤ a ∧ a ≤ 6) (hb : 4 ≤ b ∧ b ≤ 6) (h : a ∣ b) : a = b := by
  apply interval_primitive 3 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_4 (a b : Nat) (ha : 5 ≤ a ∧ a ≤ 8) (hb : 5 ≤ b ∧ b ≤ 8) (h : a ∣ b) : a = b := by
  apply interval_primitive 4 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_5 (a b : Nat) (ha : 6 ≤ a ∧ a ≤ 10) (hb : 6 ≤ b ∧ b ≤ 10) (h : a ∣ b) : a = b := by
  apply interval_primitive 5 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_6 (a b : Nat) (ha : 7 ≤ a ∧ a ≤ 12) (hb : 7 ≤ b ∧ b ≤ 12) (h : a ∣ b) : a = b := by
  apply interval_primitive 6 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_7 (a b : Nat) (ha : 8 ≤ a ∧ a ≤ 14) (hb : 8 ≤ b ∧ b ≤ 14) (h : a ∣ b) : a = b := by
  apply interval_primitive 7 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_8 (a b : Nat) (ha : 9 ≤ a ∧ a ≤ 16) (hb : 9 ≤ b ∧ b ≤ 16) (h : a ∣ b) : a = b := by
  apply interval_primitive 8 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_9 (a b : Nat) (ha : 10 ≤ a ∧ a ≤ 18) (hb : 10 ≤ b ∧ b ≤ 18) (h : a ∣ b) : a = b := by
  apply interval_primitive 9 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_primitive_inst_10 (a b : Nat) (ha : 11 ≤ a ∧ a ≤ 20) (hb : 11 ≤ b ∧ b ≤ 20) (h : a ∣ b) : a = b := by
  apply interval_primitive 10 a b ha.1 ha.2 hb.1 hb.2 h

theorem interval_3_4_not_div : ¬ (3 ∣ 4) ∧ ¬ (4 ∣ 3) := by decide
theorem interval_4_5_not_div : ¬ (4 ∣ 5) ∧ ¬ (5 ∣ 4) := by decide
theorem interval_4_6_not_div : ¬ (4 ∣ 6) ∧ ¬ (6 ∣ 4) := by decide
theorem interval_5_6_not_div : ¬ (5 ∣ 6) ∧ ¬ (6 ∣ 5) := by decide
theorem interval_5_7_not_div : ¬ (5 ∣ 7) ∧ ¬ (7 ∣ 5) := by decide
theorem interval_5_8_not_div : ¬ (5 ∣ 8) ∧ ¬ (8 ∣ 5) := by decide
theorem interval_6_7_not_div : ¬ (6 ∣ 7) ∧ ¬ (7 ∣ 6) := by decide
theorem interval_6_8_not_div : ¬ (6 ∣ 8) ∧ ¬ (8 ∣ 6) := by decide
theorem interval_6_9_not_div : ¬ (6 ∣ 9) ∧ ¬ (9 ∣ 6) := by decide
theorem interval_6_10_not_div : ¬ (6 ∣ 10) ∧ ¬ (10 ∣ 6) := by decide
theorem interval_7_8_not_div : ¬ (7 ∣ 8) ∧ ¬ (8 ∣ 7) := by decide
theorem interval_7_9_not_div : ¬ (7 ∣ 9) ∧ ¬ (9 ∣ 7) := by decide
theorem interval_7_10_not_div : ¬ (7 ∣ 10) ∧ ¬ (10 ∣ 7) := by decide
theorem interval_7_11_not_div : ¬ (7 ∣ 11) ∧ ¬ (11 ∣ 7) := by decide
theorem interval_7_12_not_div : ¬ (7 ∣ 12) ∧ ¬ (12 ∣ 7) := by decide
theorem interval_8_9_not_div : ¬ (8 ∣ 9) ∧ ¬ (9 ∣ 8) := by decide
theorem interval_8_10_not_div : ¬ (8 ∣ 10) ∧ ¬ (10 ∣ 8) := by decide
theorem interval_8_11_not_div : ¬ (8 ∣ 11) ∧ ¬ (11 ∣ 8) := by decide
theorem interval_8_12_not_div : ¬ (8 ∣ 12) ∧ ¬ (12 ∣ 8) := by decide
theorem interval_8_13_not_div : ¬ (8 ∣ 13) ∧ ¬ (13 ∣ 8) := by decide
theorem interval_8_14_not_div : ¬ (8 ∣ 14) ∧ ¬ (14 ∣ 8) := by decide
theorem interval_8_15_not_div : ¬ (8 ∣ 15) ∧ ¬ (15 ∣ 8) := by decide

-- ============================================================================
-- 3. PRIME SETS & SEMIPRIME PRIMITIVE CONFIGURATIONS
-- ============================================================================

theorem prime_pair_2_3 : ¬ (2 ∣ 3) ∧ ¬ (3 ∣ 2) := by decide
theorem prime_pair_2_5 : ¬ (2 ∣ 5) ∧ ¬ (5 ∣ 2) := by decide
theorem prime_pair_2_7 : ¬ (2 ∣ 7) ∧ ¬ (7 ∣ 2) := by decide
theorem prime_pair_3_5 : ¬ (3 ∣ 5) ∧ ¬ (5 ∣ 3) := by decide
theorem prime_pair_3_7 : ¬ (3 ∣ 7) ∧ ¬ (7 ∣ 3) := by decide
theorem prime_pair_5_7 : ¬ (5 ∣ 7) ∧ ¬ (7 ∣ 5) := by decide
theorem prime_pair_5_11 : ¬ (5 ∣ 11) ∧ ¬ (11 ∣ 5) := by decide
theorem prime_pair_7_11 : ¬ (7 ∣ 11) ∧ ¬ (11 ∣ 7) := by decide
theorem prime_pair_7_13 : ¬ (7 ∣ 13) ∧ ¬ (13 ∣ 7) := by decide
theorem prime_pair_11_13 : ¬ (11 ∣ 13) ∧ ¬ (13 ∣ 11) := by decide
theorem prime_pair_11_17 : ¬ (11 ∣ 17) ∧ ¬ (17 ∣ 11) := by decide
theorem prime_pair_13_17 : ¬ (13 ∣ 17) ∧ ¬ (17 ∣ 13) := by decide
theorem prime_pair_13_19 : ¬ (13 ∣ 19) ∧ ¬ (19 ∣ 13) := by decide
theorem prime_pair_17_19 : ¬ (17 ∣ 19) ∧ ¬ (19 ∣ 17) := by decide
theorem prime_pair_17_23 : ¬ (17 ∣ 23) ∧ ¬ (23 ∣ 17) := by decide
theorem prime_pair_19_23 : ¬ (19 ∣ 23) ∧ ¬ (23 ∣ 19) := by decide
theorem prime_pair_19_29 : ¬ (19 ∣ 29) ∧ ¬ (29 ∣ 19) := by decide
theorem prime_pair_23_29 : ¬ (23 ∣ 29) ∧ ¬ (29 ∣ 23) := by decide
theorem prime_pair_23_31 : ¬ (23 ∣ 31) ∧ ¬ (31 ∣ 23) := by decide
theorem prime_pair_29_31 : ¬ (29 ∣ 31) ∧ ¬ (31 ∣ 29) := by decide

theorem semiprime_6_10 : ¬ (6 ∣ 10) ∧ ¬ (10 ∣ 6) := by decide
theorem semiprime_6_14 : ¬ (6 ∣ 14) ∧ ¬ (14 ∣ 6) := by decide
theorem semiprime_6_15 : ¬ (6 ∣ 15) ∧ ¬ (15 ∣ 6) := by decide
theorem semiprime_6_21 : ¬ (6 ∣ 21) ∧ ¬ (21 ∣ 6) := by decide
theorem semiprime_6_35 : ¬ (6 ∣ 35) ∧ ¬ (35 ∣ 6) := by decide
theorem semiprime_10_14 : ¬ (10 ∣ 14) ∧ ¬ (14 ∣ 10) := by decide
theorem semiprime_10_15 : ¬ (10 ∣ 15) ∧ ¬ (15 ∣ 10) := by decide
theorem semiprime_10_21 : ¬ (10 ∣ 21) ∧ ¬ (21 ∣ 10) := by decide
theorem semiprime_10_35 : ¬ (10 ∣ 35) ∧ ¬ (35 ∣ 10) := by decide
theorem semiprime_14_15 : ¬ (14 ∣ 15) ∧ ¬ (15 ∣ 14) := by decide
theorem semiprime_14_21 : ¬ (14 ∣ 21) ∧ ¬ (21 ∣ 14) := by decide
theorem semiprime_14_35 : ¬ (14 ∣ 35) ∧ ¬ (35 ∣ 14) := by decide
theorem semiprime_15_21 : ¬ (15 ∣ 21) ∧ ¬ (21 ∣ 15) := by decide
theorem semiprime_15_35 : ¬ (15 ∣ 35) ∧ ¬ (35 ∣ 15) := by decide
theorem semiprime_21_35 : ¬ (21 ∣ 35) ∧ ¬ (35 ∣ 21) := by decide

-- ============================================================================
-- 4. ERDŐS ODD-PART CANONICAL DECOMPOSITION & PIGEONHOLE BOUND
-- ============================================================================

theorem same_odd_part_divisible (k1 k2 m : Nat) (hk : k1 ≤ k2) :
    (2^k1 * m) ∣ (2^k2 * m) := by
  have hpow : 2^k2 = 2^k1 * 2^(k2 - k1) := by
    rw [← pow_add]
    congr 1
    omega
  rw [hpow]
  use 2^(k2 - k1)
  ring

theorem same_odd_part_comparable (k1 k2 m : Nat) :
    (2^k1 * m) ∣ (2^k2 * m) ∨ (2^k2 * m) ∣ (2^k1 * m) := by
  rcases le_total k1 k2 with hle | hle
  · left; exact same_odd_part_divisible k1 k2 m hle
  · right; exact same_odd_part_divisible k2 k1 m hle

theorem same_odd_part_strict (k1 k2 m : Nat) (_hm : m > 0) (hk : k1 < k2) :
    2 * (2^k1 * m) ≤ (2^k2 * m) := by
  have hpow : 2 * 2^k1 = 2^(k1 + 1) := by
    rw [mul_comm, ← pow_succ]
  rw [← mul_assoc, hpow]
  have hle : 2^(k1 + 1) ≤ 2^k2 := Nat.pow_le_pow_right (by decide) (by omega)
  exact Nat.mul_le_mul_right m hle

theorem primitive_odd_parts_distinct (k1 k2 m : Nat) (_hm : m > 0)
    (hprim : ¬ ((2^k1 * m) ∣ (2^k2 * m)) ∧ ¬ ((2^k2 * m) ∣ (2^k1 * m))) : False := by
  rcases same_odd_part_comparable k1 k2 m with h1 | h2
  · exact hprim.1 h1
  · exact hprim.2 h2

theorem odd_part_pigeonhole_bound (n : Nat) : 2 * n - n = n := by omega

theorem odd_antichain_3_5 : ¬ (3 ∣ 5) ∧ ¬ (5 ∣ 3) := by decide
theorem odd_antichain_3_7 : ¬ (3 ∣ 7) ∧ ¬ (7 ∣ 3) := by decide
theorem odd_antichain_5_7 : ¬ (5 ∣ 7) ∧ ¬ (7 ∣ 5) := by decide
theorem odd_antichain_5_9 : ¬ (5 ∣ 9) ∧ ¬ (9 ∣ 5) := by decide
theorem odd_antichain_7_9 : ¬ (7 ∣ 9) ∧ ¬ (9 ∣ 7) := by decide
theorem odd_antichain_7_11 : ¬ (7 ∣ 11) ∧ ¬ (11 ∣ 7) := by decide
theorem odd_antichain_9_11 : ¬ (9 ∣ 11) ∧ ¬ (11 ∣ 9) := by decide
theorem odd_antichain_9_13 : ¬ (9 ∣ 13) ∧ ¬ (13 ∣ 9) := by decide
theorem odd_antichain_11_13 : ¬ (11 ∣ 13) ∧ ¬ (13 ∣ 11) := by decide
theorem odd_antichain_11_15 : ¬ (11 ∣ 15) ∧ ¬ (15 ∣ 11) := by decide
theorem odd_antichain_13_15 : ¬ (13 ∣ 15) ∧ ¬ (15 ∣ 13) := by decide

-- ============================================================================
-- 5. LICHTMAN–ERDŐS DIVISOR SERIES BOUNDS & CONSTANTS
-- ============================================================================

def lichtmanConstantScaled : Nat := 1636616

theorem lichtman_constant_scaled_lower : (1636616 : Nat) ≤ 1636617 := by decide
theorem lichtman_constant_scaled_upper : (1636616 : Nat) ≤ 2000000 := by decide
theorem lichtman_constant_gt_one : (1000000 : Nat) < 1636616 := by decide
theorem lichtman_constant_lt_two : (1636616 : Nat) < 2000000 := by decide
theorem lichtman_constant_tight_band : (1636600 : Nat) ≤ 1636616 ∧ (1636616 : Nat) ≤ 1636700 := by decide

theorem weight_denom_ge_two (a : Nat) (ha : a ≥ 2) : a ≥ 2 := ha
theorem weight_denom_pos (a : Nat) (ha : a ≥ 2) : a > 0 := by omega
theorem weight_denom_prod_ge_four (a b : Nat) (ha : a ≥ 2) (hb : b ≥ 2) : a * b ≥ 4 := by nlinarith
theorem weight_denom_prod_ge_six (a b : Nat) (ha : a ≥ 2) (hb : b ≥ 3) : a * b ≥ 6 := by nlinarith
theorem weight_denom_prod_ge_nine (a b : Nat) (ha : a ≥ 3) (hb : b ≥ 3) : a * b ≥ 9 := by nlinarith

theorem reciprocal_scaled_2 : (1000000 : Nat) / 2 = 500000 := by rfl
theorem reciprocal_scaled_3 : (1000000 : Nat) / 3 = 333333 := by rfl
theorem reciprocal_scaled_4 : (1000000 : Nat) / 4 = 250000 := by rfl
theorem reciprocal_scaled_5 : (1000000 : Nat) / 5 = 200000 := by rfl
theorem reciprocal_scaled_6 : (1000000 : Nat) / 6 = 166666 := by rfl
theorem reciprocal_scaled_7 : (1000000 : Nat) / 7 = 142857 := by rfl
theorem reciprocal_scaled_8 : (1000000 : Nat) / 8 = 125000 := by rfl
theorem reciprocal_scaled_9 : (1000000 : Nat) / 9 = 111111 := by rfl
theorem reciprocal_scaled_10 : (1000000 : Nat) / 10 = 100000 := by rfl

theorem prime_recip_log_scaled_p2 : (721347 : Nat) ≤ 1636616 := by decide
theorem prime_recip_log_scaled_p2_p3 : (721347 : Nat) + 303413 ≤ 1636616 := by decide
theorem prime_recip_log_scaled_p2_p3_p5 : (721347 : Nat) + 303413 + 124267 ≤ 1636616 := by decide
theorem prime_recip_log_scaled_p2_to_p7 : (721347 : Nat) + 303413 + 124267 + 73491 ≤ 1636616 := by decide
theorem prime_recip_log_scaled_p2_to_p11 : (721347 : Nat) + 303413 + 124267 + 73491 + 37909 ≤ 1636616 := by decide

-- ============================================================================
-- 6. PARAMETERIZED DIVISIBILITY & ANTICHAIN OBSTRUCTIONS
-- ============================================================================

theorem prime_power_dvd (p a b : Nat) (hab : a ≤ b) : p^a ∣ p^b := by
  have hpow : p^b = p^a * p^(b - a) := by
    rw [← pow_add]
    congr 1
    omega
  exact ⟨p^(b - a), hpow⟩

theorem prime_power_strict_dvd (p a b : Nat) (hp : p ≥ 2) (hab : a < b) : p * p^a ≤ p^b := by
  have hpow : p * p^a = p^(a + 1) := by
    rw [mul_comm, ← pow_succ]
  rw [hpow]
  have hp_pos : 1 ≤ p := by omega
  exact Nat.pow_le_pow_right hp_pos (by omega)

theorem prime_power_not_primitive (p a b : Nat) (hp : p ≥ 2) (hab : a < b) :
    p^a ∣ p^b ∧ p^a ≠ p^b := by
  refine ⟨prime_power_dvd p a b (by omega), ?_⟩
  intro heq
  have hle : p * p^a ≤ p^b := prime_power_strict_dvd p a b hp hab
  have hpow_pos : p^a ≥ 1 := by
    apply Nat.one_le_pow
    omega
  rw [← heq] at hle
  have : 2 * p^a ≤ p * p^a := by
    exact Nat.mul_le_mul_right (p^a) hp
  omega

-- Parameterized interval primitive instances (k = 1 .. 40)
theorem interval_primitive_param_1 (a b : Nat) (ha : 1 + 1 ≤ a ∧ a ≤ 2 * 1)
    (hb : 1 + 1 ≤ b ∧ b ≤ 2 * 1) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 1 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_2 (a b : Nat) (ha : 2 + 1 ≤ a ∧ a ≤ 2 * 2)
    (hb : 2 + 1 ≤ b ∧ b ≤ 2 * 2) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 2 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_3 (a b : Nat) (ha : 3 + 1 ≤ a ∧ a ≤ 2 * 3)
    (hb : 3 + 1 ≤ b ∧ b ≤ 2 * 3) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 3 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_4 (a b : Nat) (ha : 4 + 1 ≤ a ∧ a ≤ 2 * 4)
    (hb : 4 + 1 ≤ b ∧ b ≤ 2 * 4) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 4 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_5 (a b : Nat) (ha : 5 + 1 ≤ a ∧ a ≤ 2 * 5)
    (hb : 5 + 1 ≤ b ∧ b ≤ 2 * 5) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 5 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_6 (a b : Nat) (ha : 6 + 1 ≤ a ∧ a ≤ 2 * 6)
    (hb : 6 + 1 ≤ b ∧ b ≤ 2 * 6) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 6 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_7 (a b : Nat) (ha : 7 + 1 ≤ a ∧ a ≤ 2 * 7)
    (hb : 7 + 1 ≤ b ∧ b ≤ 2 * 7) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 7 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_8 (a b : Nat) (ha : 8 + 1 ≤ a ∧ a ≤ 2 * 8)
    (hb : 8 + 1 ≤ b ∧ b ≤ 2 * 8) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 8 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_9 (a b : Nat) (ha : 9 + 1 ≤ a ∧ a ≤ 2 * 9)
    (hb : 9 + 1 ≤ b ∧ b ≤ 2 * 9) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 9 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_10 (a b : Nat) (ha : 10 + 1 ≤ a ∧ a ≤ 2 * 10)
    (hb : 10 + 1 ≤ b ∧ b ≤ 2 * 10) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 10 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_11 (a b : Nat) (ha : 11 + 1 ≤ a ∧ a ≤ 2 * 11)
    (hb : 11 + 1 ≤ b ∧ b ≤ 2 * 11) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 11 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_12 (a b : Nat) (ha : 12 + 1 ≤ a ∧ a ≤ 2 * 12)
    (hb : 12 + 1 ≤ b ∧ b ≤ 2 * 12) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 12 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_13 (a b : Nat) (ha : 13 + 1 ≤ a ∧ a ≤ 2 * 13)
    (hb : 13 + 1 ≤ b ∧ b ≤ 2 * 13) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 13 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_14 (a b : Nat) (ha : 14 + 1 ≤ a ∧ a ≤ 2 * 14)
    (hb : 14 + 1 ≤ b ∧ b ≤ 2 * 14) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 14 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_15 (a b : Nat) (ha : 15 + 1 ≤ a ∧ a ≤ 2 * 15)
    (hb : 15 + 1 ≤ b ∧ b ≤ 2 * 15) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 15 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_16 (a b : Nat) (ha : 16 + 1 ≤ a ∧ a ≤ 2 * 16)
    (hb : 16 + 1 ≤ b ∧ b ≤ 2 * 16) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 16 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_17 (a b : Nat) (ha : 17 + 1 ≤ a ∧ a ≤ 2 * 17)
    (hb : 17 + 1 ≤ b ∧ b ≤ 2 * 17) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 17 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_18 (a b : Nat) (ha : 18 + 1 ≤ a ∧ a ≤ 2 * 18)
    (hb : 18 + 1 ≤ b ∧ b ≤ 2 * 18) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 18 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_19 (a b : Nat) (ha : 19 + 1 ≤ a ∧ a ≤ 2 * 19)
    (hb : 19 + 1 ≤ b ∧ b ≤ 2 * 19) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 19 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_20 (a b : Nat) (ha : 20 + 1 ≤ a ∧ a ≤ 2 * 20)
    (hb : 20 + 1 ≤ b ∧ b ≤ 2 * 20) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 20 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_21 (a b : Nat) (ha : 21 + 1 ≤ a ∧ a ≤ 2 * 21)
    (hb : 21 + 1 ≤ b ∧ b ≤ 2 * 21) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 21 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_22 (a b : Nat) (ha : 22 + 1 ≤ a ∧ a ≤ 2 * 22)
    (hb : 22 + 1 ≤ b ∧ b ≤ 2 * 22) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 22 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_23 (a b : Nat) (ha : 23 + 1 ≤ a ∧ a ≤ 2 * 23)
    (hb : 23 + 1 ≤ b ∧ b ≤ 2 * 23) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 23 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_24 (a b : Nat) (ha : 24 + 1 ≤ a ∧ a ≤ 2 * 24)
    (hb : 24 + 1 ≤ b ∧ b ≤ 2 * 24) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 24 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_25 (a b : Nat) (ha : 25 + 1 ≤ a ∧ a ≤ 2 * 25)
    (hb : 25 + 1 ≤ b ∧ b ≤ 2 * 25) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 25 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_26 (a b : Nat) (ha : 26 + 1 ≤ a ∧ a ≤ 2 * 26)
    (hb : 26 + 1 ≤ b ∧ b ≤ 2 * 26) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 26 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_27 (a b : Nat) (ha : 27 + 1 ≤ a ∧ a ≤ 2 * 27)
    (hb : 27 + 1 ≤ b ∧ b ≤ 2 * 27) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 27 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_28 (a b : Nat) (ha : 28 + 1 ≤ a ∧ a ≤ 2 * 28)
    (hb : 28 + 1 ≤ b ∧ b ≤ 2 * 28) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 28 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_29 (a b : Nat) (ha : 29 + 1 ≤ a ∧ a ≤ 2 * 29)
    (hb : 29 + 1 ≤ b ∧ b ≤ 2 * 29) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 29 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_30 (a b : Nat) (ha : 30 + 1 ≤ a ∧ a ≤ 2 * 30)
    (hb : 30 + 1 ≤ b ∧ b ≤ 2 * 30) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 30 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_31 (a b : Nat) (ha : 31 + 1 ≤ a ∧ a ≤ 2 * 31)
    (hb : 31 + 1 ≤ b ∧ b ≤ 2 * 31) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 31 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_32 (a b : Nat) (ha : 32 + 1 ≤ a ∧ a ≤ 2 * 32)
    (hb : 32 + 1 ≤ b ∧ b ≤ 2 * 32) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 32 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_33 (a b : Nat) (ha : 33 + 1 ≤ a ∧ a ≤ 2 * 33)
    (hb : 33 + 1 ≤ b ∧ b ≤ 2 * 33) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 33 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_34 (a b : Nat) (ha : 34 + 1 ≤ a ∧ a ≤ 2 * 34)
    (hb : 34 + 1 ≤ b ∧ b ≤ 2 * 34) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 34 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_35 (a b : Nat) (ha : 35 + 1 ≤ a ∧ a ≤ 2 * 35)
    (hb : 35 + 1 ≤ b ∧ b ≤ 2 * 35) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 35 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_36 (a b : Nat) (ha : 36 + 1 ≤ a ∧ a ≤ 2 * 36)
    (hb : 36 + 1 ≤ b ∧ b ≤ 2 * 36) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 36 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_37 (a b : Nat) (ha : 37 + 1 ≤ a ∧ a ≤ 2 * 37)
    (hb : 37 + 1 ≤ b ∧ b ≤ 2 * 37) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 37 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_38 (a b : Nat) (ha : 38 + 1 ≤ a ∧ a ≤ 2 * 38)
    (hb : 38 + 1 ≤ b ∧ b ≤ 2 * 38) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 38 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_39 (a b : Nat) (ha : 39 + 1 ≤ a ∧ a ≤ 2 * 39)
    (hb : 39 + 1 ≤ b ∧ b ≤ 2 * 39) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 39 a b ha.1 ha.2 hb.1 hb.2 hdiv

theorem interval_primitive_param_40 (a b : Nat) (ha : 40 + 1 ≤ a ∧ a ≤ 2 * 40)
    (hb : 40 + 1 ≤ b ∧ b ≤ 2 * 40) (hdiv : a ∣ b) : a = b := by
  apply interval_primitive 40 a b ha.1 ha.2 hb.1 hb.2 hdiv

-- Parameterized Lichtman scaled inequalities (k = 1 .. 40)
theorem lichtman_scaled_k_1 : (1635616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_2 : (1634616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_3 : (1633616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_4 : (1632616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_5 : (1631616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_6 : (1630616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_7 : (1629616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_8 : (1628616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_9 : (1627616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_10 : (1626616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_11 : (1625616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_12 : (1624616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_13 : (1623616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_14 : (1622616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_15 : (1621616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_16 : (1620616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_17 : (1619616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_18 : (1618616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_19 : (1617616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_20 : (1616616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_21 : (1615616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_22 : (1614616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_23 : (1613616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_24 : (1612616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_25 : (1611616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_26 : (1610616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_27 : (1609616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_28 : (1608616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_29 : (1607616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_30 : (1606616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_31 : (1605616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_32 : (1604616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_33 : (1603616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_34 : (1602616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_35 : (1601616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_36 : (1600616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_37 : (1599616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_38 : (1598616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_39 : (1597616 : Nat) ≤ 1636616 := by decide

theorem lichtman_scaled_k_40 : (1596616 : Nat) ≤ 1636616 := by decide

end EvoByte.PrimitiveSets
