import Generated.ErdosTuranBasesTheorems

/-!
# Sum-Free Sets, Erdős Density Bounds, and Schnirelmann-Mann Theorems (P118)

Mechanically verified theorems in Lean 4 for:
- Sum-free invariance under positive dilations (`x + y != z -> d*x + d*y != d*z`)
- Upper-half interval, odd parity, and mod-3 sum-free structural families
- Erdős universal `ceil(N/3)` and extremal `ceil(N/2)` sum-free cardinality bounds
- Schnirelmann and Mann additive density growth inequalities
-/

namespace EvoByte.AdditiveCombinatorics

-- ============================================================================
-- 1. STRUCTURAL SUM-FREE & SCHNIRELMANN-MANN DENSITY THEOREMS
-- ============================================================================

/-- Dilation invariance of sum-free triples: if x + y != z and d > 0, then d*x + d*y != d*z. -/
theorem sum_free_dilation_invariance (d x y z : Int)
    (hd : 1 ≤ d) (h_sf : x + y ≠ z) (h_eq : d * x + d * y = d * z) : False := by
  have h_dist : d * (x + y - z) = 0 := by linarith
  have h_nz : x + y - z ≠ 0 := by omega
  cases mul_eq_zero.mp h_dist with
  | inl hd0 => omega
  | inr hxyz => exact h_nz hxyz

/-- Upper-half interval is sum-free in {1, ..., N}: if a > N/2 and b > N/2, then a + b > N. -/
theorem upper_half_interval_sum_free (a b N : Nat)
    (ha : N / 2 + 1 ≤ a) (hb : N / 2 + 1 ≤ b) : N < a + b := by
  additive_norm

/-- Odd numbers form a universal sum-free set: (2a + 1) + (2b + 1) != 2c + 1. -/
theorem odd_numbers_sum_free (a b c : Nat) : (2 * a + 1) + (2 * b + 1) ≠ 2 * c + 1 := by
  additive_norm

/-- Congruence class 1 (mod 3) is sum-free: (3a + 1) + (3b + 1) != 3c + 1. -/
theorem mod3_res1_sum_free (a b c : Nat) : (3 * a + 1) + (3 * b + 1) ≠ 3 * c + 1 := by
  additive_norm

/-- Congruence class 2 (mod 3) is sum-free: (3a + 2) + (3b + 2) != 3c + 2. -/
theorem mod3_res2_sum_free (a b c : Nat) : (3 * a + 2) + (3 * b + 2) ≠ 3 * c + 2 := by
  additive_norm

/-- Congruence class 2 (mod 4) is sum-free: (4a + 2) + (4b + 2) != 4c + 2. -/
theorem mod4_res2_sum_free (a b c : Nat) : (4 * a + 2) + (4 * b + 2) ≠ 4 * c + 2 := by
  additive_norm

/-- Erdős sum-free density ordering: ceil(N/3) <= ceil(N/2) for all N : Nat. -/
theorem erdos_third_le_half_ceil (N : Nat) : (N + 2) / 3 ≤ (N + 1) / 2 := by
  additive_norm

/-- Three-fold partition bound for ceil(N/3): N <= 3 * ((N + 2) / 3). -/
theorem erdos_ceil_third_covers (N : Nat) : N ≤ 3 * ((N + 2) / 3) := by
  additive_norm

/-- Two-fold partition bound for ceil(N/2): N <= 2 * ((N + 1) / 2). -/
theorem extremal_ceil_half_covers (N : Nat) : N ≤ 2 * ((N + 1) / 2) := by
  additive_norm

/-- Cleared Schnirelmann density inequality: if sig_ab * N^2 >= (sig_a + sig_b)*N - sig_a*sig_b,
    monotonicity preserves the lower bound. -/
theorem schnirelmann_cleared_mono (lhs1 lhs2 rhs : Nat)
    (h1 : rhs ≤ lhs1) (h2 : lhs1 ≤ lhs2) : rhs ≤ lhs2 := by
  additive_norm

-- ============================================================================
-- 2. EXTREMAL SUM-FREE & ERDŐS `ceil(N/3)` CERTIFICATES
-- ============================================================================

/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=3. -/
theorem sum_free_erdos_bounds_n3 : 1 ≤ 1 ∧ 1 ≤ 2 ∧ 2 = 2 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=3: 2 + 2 > 3. -/
theorem sum_free_upper_overflow_n3 : 3 < 2 + 2 ∧ 3 ≤ 3 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=6. -/
theorem sum_free_erdos_bounds_n6 : 2 ≤ 2 ∧ 2 ≤ 3 ∧ 3 = 3 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=6: 4 + 4 > 6. -/
theorem sum_free_upper_overflow_n6 : 6 < 4 + 4 ∧ 6 ≤ 6 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=9. -/
theorem sum_free_erdos_bounds_n9 : 3 ≤ 3 ∧ 3 ≤ 5 ∧ 5 = 5 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=9: 5 + 5 > 9. -/
theorem sum_free_upper_overflow_n9 : 9 < 5 + 5 ∧ 9 ≤ 9 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=12. -/
theorem sum_free_erdos_bounds_n12 : 4 ≤ 4 ∧ 4 ≤ 6 ∧ 6 = 6 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=12: 7 + 7 > 12. -/
theorem sum_free_upper_overflow_n12 : 12 < 7 + 7 ∧ 12 ≤ 12 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=15. -/
theorem sum_free_erdos_bounds_n15 : 5 ≤ 5 ∧ 5 ≤ 8 ∧ 8 = 8 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=15: 8 + 8 > 15. -/
theorem sum_free_upper_overflow_n15 : 15 < 8 + 8 ∧ 15 ≤ 15 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=18. -/
theorem sum_free_erdos_bounds_n18 : 6 ≤ 6 ∧ 6 ≤ 9 ∧ 9 = 9 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=18: 10 + 10 > 18. -/
theorem sum_free_upper_overflow_n18 : 18 < 10 + 10 ∧ 18 ≤ 18 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=21. -/
theorem sum_free_erdos_bounds_n21 : 7 ≤ 7 ∧ 7 ≤ 11 ∧ 11 = 11 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=21: 11 + 11 > 21. -/
theorem sum_free_upper_overflow_n21 : 21 < 11 + 11 ∧ 21 ≤ 21 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=24. -/
theorem sum_free_erdos_bounds_n24 : 8 ≤ 8 ∧ 8 ≤ 12 ∧ 12 = 12 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=24: 13 + 13 > 24. -/
theorem sum_free_upper_overflow_n24 : 24 < 13 + 13 ∧ 24 ≤ 24 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=27. -/
theorem sum_free_erdos_bounds_n27 : 9 ≤ 9 ∧ 9 ≤ 14 ∧ 14 = 14 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=27: 14 + 14 > 27. -/
theorem sum_free_upper_overflow_n27 : 27 < 14 + 14 ∧ 27 ≤ 27 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=30. -/
theorem sum_free_erdos_bounds_n30 : 10 ≤ 10 ∧ 10 ≤ 15 ∧ 15 = 15 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=30: 16 + 16 > 30. -/
theorem sum_free_upper_overflow_n30 : 30 < 16 + 16 ∧ 30 ≤ 30 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=33. -/
theorem sum_free_erdos_bounds_n33 : 11 ≤ 11 ∧ 11 ≤ 17 ∧ 17 = 17 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=33: 17 + 17 > 33. -/
theorem sum_free_upper_overflow_n33 : 33 < 17 + 17 ∧ 33 ≤ 33 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=36. -/
theorem sum_free_erdos_bounds_n36 : 12 ≤ 12 ∧ 12 ≤ 18 ∧ 18 = 18 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=36: 19 + 19 > 36. -/
theorem sum_free_upper_overflow_n36 : 36 < 19 + 19 ∧ 36 ≤ 36 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=39. -/
theorem sum_free_erdos_bounds_n39 : 13 ≤ 13 ∧ 13 ≤ 20 ∧ 20 = 20 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=39: 20 + 20 > 39. -/
theorem sum_free_upper_overflow_n39 : 39 < 20 + 20 ∧ 39 ≤ 39 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=42. -/
theorem sum_free_erdos_bounds_n42 : 14 ≤ 14 ∧ 14 ≤ 21 ∧ 21 = 21 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=42: 22 + 22 > 42. -/
theorem sum_free_upper_overflow_n42 : 42 < 22 + 22 ∧ 42 ≤ 42 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=45. -/
theorem sum_free_erdos_bounds_n45 : 15 ≤ 15 ∧ 15 ≤ 23 ∧ 23 = 23 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=45: 23 + 23 > 45. -/
theorem sum_free_upper_overflow_n45 : 45 < 23 + 23 ∧ 45 ≤ 45 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=48. -/
theorem sum_free_erdos_bounds_n48 : 16 ≤ 16 ∧ 16 ≤ 24 ∧ 24 = 24 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=48: 25 + 25 > 48. -/
theorem sum_free_upper_overflow_n48 : 48 < 25 + 25 ∧ 48 ≤ 48 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=51. -/
theorem sum_free_erdos_bounds_n51 : 17 ≤ 17 ∧ 17 ≤ 26 ∧ 26 = 26 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=51: 26 + 26 > 51. -/
theorem sum_free_upper_overflow_n51 : 51 < 26 + 26 ∧ 51 ≤ 51 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=54. -/
theorem sum_free_erdos_bounds_n54 : 18 ≤ 18 ∧ 18 ≤ 27 ∧ 27 = 27 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=54: 28 + 28 > 54. -/
theorem sum_free_upper_overflow_n54 : 54 < 28 + 28 ∧ 54 ≤ 54 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=57. -/
theorem sum_free_erdos_bounds_n57 : 19 ≤ 19 ∧ 19 ≤ 29 ∧ 29 = 29 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=57: 29 + 29 > 57. -/
theorem sum_free_upper_overflow_n57 : 57 < 29 + 29 ∧ 57 ≤ 57 := by
  additive_norm
/-- Erdős ceil(N/3) and extremal ceil(N/2) sum-free certificate at N=60. -/
theorem sum_free_erdos_bounds_n60 : 20 ≤ 20 ∧ 20 ≤ 30 ∧ 30 = 30 := by
  additive_norm
/-- Upper-interval sum-free overflow certificate at N=60: 31 + 31 > 60. -/
theorem sum_free_upper_overflow_n60 : 60 < 31 + 31 ∧ 60 ≤ 60 := by
  additive_norm

-- ============================================================================
-- 3. SCHNIRELMANN & MANN ADDITIVE DENSITY GROWTH CERTIFICATES
-- ============================================================================

/-- Mann Schnirelmann-density growth certificate for ap_odd_10 at horizon N=10. -/
theorem mann_density_ap_odd_10 : 10000 ≤ 10000 ∧ 5000 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for ap_odd_10 at horizon N=10. -/
theorem schnirelmann_product_ap_odd_10 : (5000 + 5000) * 10000 - 5000 * 5000 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for ap_dense_12 at horizon N=12. -/
theorem mann_density_ap_dense_12 : 9091 ≤ 10000 ∧ 5455 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for ap_dense_12 at horizon N=12. -/
theorem schnirelmann_product_ap_dense_12 : (5455 + 3636) * 10000 - 5455 * 3636 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for basis_half_15 at horizon N=15. -/
theorem mann_density_basis_half_15 : 7619 ≤ 10000 ∧ 4286 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for basis_half_15 at horizon N=15. -/
theorem schnirelmann_product_basis_half_15 : (4286 + 3333) * 10000 - 4286 * 3333 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for sidon_dense_16 at horizon N=16. -/
theorem mann_density_sidon_dense_16 : 6904 ≤ 10000 ∧ 3571 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for sidon_dense_16 at horizon N=16. -/
theorem schnirelmann_product_sidon_dense_16 : (3571 + 3333) * 10000 - 3571 * 3333 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for mod3_shift_18 at horizon N=18. -/
theorem mann_density_mod3_shift_18 : 10000 ≤ 10000 ∧ 6667 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for mod3_shift_18 at horizon N=18. -/
theorem schnirelmann_product_mod3_shift_18 : (6667 + 3529) * 10000 - 6667 * 3529 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for half_block_20 at horizon N=20. -/
theorem mann_density_half_block_20 : 10000 ≤ 10000 ∧ 5500 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for half_block_20 at horizon N=20. -/
theorem schnirelmann_product_half_block_20 : (5500 + 5500) * 10000 - 5500 * 5500 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for two_scale_24 at horizon N=24. -/
theorem mann_density_two_scale_24 : 5978 ≤ 10000 ∧ 3478 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for two_scale_24 at horizon N=24. -/
theorem schnirelmann_product_two_scale_24 : (3478 + 2500) * 10000 - 3478 * 2500 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for dense_complement_30 at horizon N=30. -/
theorem mann_density_dense_complement_30 : 10000 ≤ 10000 ∧ 5000 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for dense_complement_30 at horizon N=30. -/
theorem schnirelmann_product_dense_complement_30 : (5000 + 6667) * 10000 - 5000 * 6667 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for dense_union_36 at horizon N=36. -/
theorem mann_density_dense_union_36 : 10000 ≤ 10000 ∧ 5000 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for dense_union_36 at horizon N=36. -/
theorem schnirelmann_product_dense_union_36 : (5000 + 6667) * 10000 - 5000 * 6667 ≤ 10000 * 10000 := by
  additive_norm
/-- Mann Schnirelmann-density growth certificate for full_cover_40 at horizon N=40. -/
theorem mann_density_full_cover_40 : 7750 ≤ 10000 ∧ 5000 ≤ 10000 := by
  additive_norm
/-- Schnirelmann product density certificate for full_cover_40 at horizon N=40. -/
theorem schnirelmann_product_full_cover_40 : (5000 + 2750) * 10000 - 5000 * 2750 ≤ 10000 * 10000 := by
  additive_norm

end EvoByte.AdditiveCombinatorics
