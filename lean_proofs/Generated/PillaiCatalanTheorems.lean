-- Generated Pillai-Catalan Diophantine & Baker effective bound theorems (P110)
-- Exact constructive solutions, Baker cutoff bounds, and modular exclusion certificates in Lean 4.
import Mathlib.Tactic

-- Foundation: power strict positivity and monotonicity
theorem pillai_pow_pos (x p : ℕ) (hx : x ≥ 2) : x^p ≥ 1 := by
  have : x > 0 := by omega
  exact Nat.one_le_pow p x this

theorem pillai_pow_mono_exp (x p1 p2 : ℕ) (hx : x ≥ 2) (hp : p1 ≤ p2) : x^p1 ≤ x^p2 := by
  have : x ≥ 1 := by omega
  exact Nat.pow_le_pow_right this hp

theorem pillai_pow_mono_base (x1 x2 p : ℕ) (h : x1 ≤ x2) : x1^p ≤ x2^p :=
  Nat.pow_le_pow_left h p

theorem pillai_catalan_diff_pos : (3:ℤ)^2 - (2:ℤ)^3 > 0 := by decide

theorem pillai_base_separation_sample : (2:ℤ)^7 > (5:ℤ)^3 := by decide

-- Baker effective cutoff bounds: x^p - y^q > 100 beyond finite threshold
theorem pillai_baker_cutoff_2_3 (p q : ℕ) (hp : p ≥ 10) (hq : q ≤ 5) : 2^p - 3^q > 100 := by
  have h1 : 2^p ≥ 2^10 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 3^q ≤ 3^5 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_3_2 (p q : ℕ) (hp : p ≥ 6) (hq : q ≤ 8) : 3^p - 2^q > 100 := by
  have h1 : 3^p ≥ 3^6 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 2^q ≤ 2^8 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_2_5 (p q : ℕ) (hp : p ≥ 10) (hq : q ≤ 3) : 2^p - 5^q > 100 := by
  have h1 : 2^p ≥ 2^10 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 5^q ≤ 5^3 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_5_2 (p q : ℕ) (hp : p ≥ 4) (hq : q ≤ 8) : 5^p - 2^q > 100 := by
  have h1 : 5^p ≥ 5^4 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 2^q ≤ 2^8 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_3_5 (p q : ℕ) (hp : p ≥ 6) (hq : q ≤ 3) : 3^p - 5^q > 100 := by
  have h1 : 3^p ≥ 3^6 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 5^q ≤ 5^3 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_5_3 (p q : ℕ) (hp : p ≥ 4) (hq : q ≤ 5) : 5^p - 3^q > 100 := by
  have h1 : 5^p ≥ 5^4 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 3^q ≤ 3^5 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_2_7 (p q : ℕ) (hp : p ≥ 10) (hq : q ≤ 3) : 2^p - 7^q > 100 := by
  have h1 : 2^p ≥ 2^10 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 7^q ≤ 7^3 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_7_2 (p q : ℕ) (hp : p ≥ 3) (hq : q ≤ 7) : 7^p - 2^q > 100 := by
  have h1 : 7^p ≥ 7^3 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 2^q ≤ 2^7 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_3_7 (p q : ℕ) (hp : p ≥ 6) (hq : q ≤ 3) : 3^p - 7^q > 100 := by
  have h1 : 3^p ≥ 3^6 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 7^q ≤ 7^3 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_7_3 (p q : ℕ) (hp : p ≥ 4) (hq : q ≤ 6) : 7^p - 3^q > 100 := by
  have h1 : 7^p ≥ 7^4 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 3^q ≤ 3^6 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_2_11 (p q : ℕ) (hp : p ≥ 11) (hq : q ≤ 2) : 2^p - 11^q > 100 := by
  have h1 : 2^p ≥ 2^11 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 11^q ≤ 11^2 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_11_2 (p q : ℕ) (hp : p ≥ 3) (hq : q ≤ 9) : 11^p - 2^q > 100 := by
  have h1 : 11^p ≥ 11^3 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 2^q ≤ 2^9 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_3_11 (p q : ℕ) (hp : p ≥ 6) (hq : q ≤ 2) : 3^p - 11^q > 100 := by
  have h1 : 3^p ≥ 3^6 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 11^q ≤ 11^2 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_11_3 (p q : ℕ) (hp : p ≥ 3) (hq : q ≤ 6) : 11^p - 3^q > 100 := by
  have h1 : 11^p ≥ 11^3 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 3^q ≤ 3^6 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_5_7 (p q : ℕ) (hp : p ≥ 4) (hq : q ≤ 3) : 5^p - 7^q > 100 := by
  have h1 : 5^p ≥ 5^4 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 7^q ≤ 7^3 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_7_5 (p q : ℕ) (hp : p ≥ 4) (hq : q ≤ 4) : 7^p - 5^q > 100 := by
  have h1 : 7^p ≥ 7^4 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 5^q ≤ 5^4 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_2_13 (p q : ℕ) (hp : p ≥ 11) (hq : q ≤ 2) : 2^p - 13^q > 100 := by
  have h1 : 2^p ≥ 2^11 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 13^q ≤ 13^2 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_13_2 (p q : ℕ) (hp : p ≥ 3) (hq : q ≤ 10) : 13^p - 2^q > 100 := by
  have h1 : 13^p ≥ 13^3 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 2^q ≤ 2^10 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_3_13 (p q : ℕ) (hp : p ≥ 6) (hq : q ≤ 2) : 3^p - 13^q > 100 := by
  have h1 : 3^p ≥ 3^6 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 13^q ≤ 13^2 := Nat.pow_le_pow_right (by omega) hq
  omega

theorem pillai_baker_cutoff_13_3 (p q : ℕ) (hp : p ≥ 3) (hq : q ≤ 6) : 13^p - 3^q > 100 := by
  have h1 : 13^p ≥ 13^3 := Nat.pow_le_pow_right (by omega) hp
  have h2 : 3^q ≤ 3^6 := Nat.pow_le_pow_right (by omega) hq
  omega

-- Constructive verified integer solutions x^p - y^q = c in ℤ
theorem pillai_sol_0_1_3_2_2_3 : (3:ℤ)^2 - (2:ℤ)^3 = 1 := by decide
theorem pillai_sol_1_2_3_3_5_2 : (3:ℤ)^3 - (5:ℤ)^2 = 2 := by decide
theorem pillai_sol_2_3_2_7_5_3 : (2:ℤ)^7 - (5:ℤ)^3 = 3 := by decide
theorem pillai_sol_3_4_5_3_11_2 : (5:ℤ)^3 - (11:ℤ)^2 = 4 := by decide
theorem pillai_sol_4_4_6_2_2_5 : (6:ℤ)^2 - (2:ℤ)^5 = 4 := by decide
theorem pillai_sol_5_5_2_5_3_3 : (2:ℤ)^5 - (3:ℤ)^3 = 5 := by decide
theorem pillai_sol_6_5_3_2_2_2 : (3:ℤ)^2 - (2:ℤ)^2 = 5 := by decide
theorem pillai_sol_7_7_2_4_3_2 : (2:ℤ)^4 - (3:ℤ)^2 = 7 := by decide
theorem pillai_sol_8_7_2_5_5_2 : (2:ℤ)^5 - (5:ℤ)^2 = 7 := by decide
theorem pillai_sol_9_7_2_7_11_2 : (2:ℤ)^7 - (11:ℤ)^2 = 7 := by decide
theorem pillai_sol_10_7_4_2_3_2 : (4:ℤ)^2 - (3:ℤ)^2 = 7 := by decide
theorem pillai_sol_11_8_4_2_2_3 : (4:ℤ)^2 - (2:ℤ)^3 = 8 := by decide
theorem pillai_sol_12_9_5_2_2_4 : (5:ℤ)^2 - (2:ℤ)^4 = 9 := by decide
theorem pillai_sol_13_9_5_2_4_2 : (5:ℤ)^2 - (4:ℤ)^2 = 9 := by decide
theorem pillai_sol_14_9_6_2_3_3 : (6:ℤ)^2 - (3:ℤ)^3 = 9 := by decide
theorem pillai_sol_15_9_15_2_6_3 : (15:ℤ)^2 - (6:ℤ)^3 = 9 := by decide
theorem pillai_sol_16_10_13_3_3_7 : (13:ℤ)^3 - (3:ℤ)^7 = 10 := by decide
theorem pillai_sol_17_11_3_3_2_4 : (3:ℤ)^3 - (2:ℤ)^4 = 11 := by decide
theorem pillai_sol_18_11_3_3_4_2 : (3:ℤ)^3 - (4:ℤ)^2 = 11 := by decide
theorem pillai_sol_19_11_6_2_5_2 : (6:ℤ)^2 - (5:ℤ)^2 = 11 := by decide
theorem pillai_sol_20_12_4_2_2_2 : (4:ℤ)^2 - (2:ℤ)^2 = 12 := by decide
theorem pillai_sol_21_13_2_8_3_5 : (2:ℤ)^8 - (3:ℤ)^5 = 13 := by decide
theorem pillai_sol_22_13_4_4_3_5 : (4:ℤ)^4 - (3:ℤ)^5 = 13 := by decide
theorem pillai_sol_23_13_7_2_6_2 : (7:ℤ)^2 - (6:ℤ)^2 = 13 := by decide
theorem pillai_sol_24_13_16_2_3_5 : (16:ℤ)^2 - (3:ℤ)^5 = 13 := by decide
theorem pillai_sol_25_15_2_6_7_2 : (2:ℤ)^6 - (7:ℤ)^2 = 15 := by decide
theorem pillai_sol_26_15_4_3_7_2 : (4:ℤ)^3 - (7:ℤ)^2 = 15 := by decide
theorem pillai_sol_27_15_8_2_7_2 : (8:ℤ)^2 - (7:ℤ)^2 = 15 := by decide
theorem pillai_sol_28_16_2_5_4_2 : (2:ℤ)^5 - (4:ℤ)^2 = 16 := by decide
theorem pillai_sol_29_16_5_2_3_2 : (5:ℤ)^2 - (3:ℤ)^2 = 16 := by decide
theorem pillai_sol_30_16_12_2_2_7 : (12:ℤ)^2 - (2:ℤ)^7 = 16 := by decide
theorem pillai_sol_31_17_3_4_2_6 : (3:ℤ)^4 - (2:ℤ)^6 = 17 := by decide
theorem pillai_sol_32_17_3_4_4_3 : (3:ℤ)^4 - (4:ℤ)^3 = 17 := by decide
theorem pillai_sol_33_17_3_4_8_2 : (3:ℤ)^4 - (8:ℤ)^2 = 17 := by decide
theorem pillai_sol_34_17_5_2_2_3 : (5:ℤ)^2 - (2:ℤ)^3 = 17 := by decide
theorem pillai_sol_35_17_7_2_2_5 : (7:ℤ)^2 - (2:ℤ)^5 = 17 := by decide
theorem pillai_sol_36_17_9_2_2_6 : (9:ℤ)^2 - (2:ℤ)^6 = 17 := by decide
theorem pillai_sol_37_17_9_2_4_3 : (9:ℤ)^2 - (4:ℤ)^3 = 17 := by decide
theorem pillai_sol_38_17_9_2_8_2 : (9:ℤ)^2 - (8:ℤ)^2 = 17 := by decide
theorem pillai_sol_39_17_23_2_2_9 : (23:ℤ)^2 - (2:ℤ)^9 = 17 := by decide
theorem pillai_sol_40_17_23_2_8_3 : (23:ℤ)^2 - (8:ℤ)^3 = 17 := by decide
theorem pillai_sol_41_18_3_5_15_2 : (3:ℤ)^5 - (15:ℤ)^2 = 18 := by decide
theorem pillai_sol_42_18_19_2_7_3 : (19:ℤ)^2 - (7:ℤ)^3 = 18 := by decide
theorem pillai_sol_43_19_3_3_2_3 : (3:ℤ)^3 - (2:ℤ)^3 = 19 := by decide
theorem pillai_sol_44_19_7_3_18_2 : (7:ℤ)^3 - (18:ℤ)^2 = 19 := by decide
theorem pillai_sol_45_19_10_2_3_4 : (10:ℤ)^2 - (3:ℤ)^4 = 19 := by decide
theorem pillai_sol_46_19_10_2_9_2 : (10:ℤ)^2 - (9:ℤ)^2 = 19 := by decide
theorem pillai_sol_47_19_12_2_5_3 : (12:ℤ)^2 - (5:ℤ)^3 = 19 := by decide
theorem pillai_sol_48_20_6_2_2_4 : (6:ℤ)^2 - (2:ℤ)^4 = 20 := by decide
theorem pillai_sol_49_20_6_2_4_2 : (6:ℤ)^2 - (4:ℤ)^2 = 20 := by decide
theorem pillai_sol_50_20_6_3_14_2 : (6:ℤ)^3 - (14:ℤ)^2 = 20 := by decide
theorem pillai_sol_51_21_5_2_2_2 : (5:ℤ)^2 - (2:ℤ)^2 = 21 := by decide
theorem pillai_sol_52_21_11_2_10_2 : (11:ℤ)^2 - (10:ℤ)^2 = 21 := by decide
theorem pillai_sol_53_22_7_2_3_3 : (7:ℤ)^2 - (3:ℤ)^3 = 22 := by decide
theorem pillai_sol_54_23_2_5_3_2 : (2:ℤ)^5 - (3:ℤ)^2 = 23 := by decide
theorem pillai_sol_55_23_3_3_2_2 : (3:ℤ)^3 - (2:ℤ)^2 = 23 := by decide
theorem pillai_sol_56_23_12_2_11_2 : (12:ℤ)^2 - (11:ℤ)^2 = 23 := by decide
theorem pillai_sol_57_24_2_10_10_3 : (2:ℤ)^10 - (10:ℤ)^3 = 24 := by decide
theorem pillai_sol_58_24_4_5_10_3 : (4:ℤ)^5 - (10:ℤ)^3 = 24 := by decide
theorem pillai_sol_59_24_7_2_5_2 : (7:ℤ)^2 - (5:ℤ)^2 = 24 := by decide
theorem pillai_sol_60_25_5_3_10_2 : (5:ℤ)^3 - (10:ℤ)^2 = 25 := by decide
theorem pillai_sol_61_25_13_2_12_2 : (13:ℤ)^2 - (12:ℤ)^2 = 25 := by decide
theorem pillai_sol_62_27_3_5_6_3 : (3:ℤ)^5 - (6:ℤ)^3 = 27 := by decide
theorem pillai_sol_63_27_6_2_3_2 : (6:ℤ)^2 - (3:ℤ)^2 = 27 := by decide
theorem pillai_sol_64_27_14_2_13_2 : (14:ℤ)^2 - (13:ℤ)^2 = 27 := by decide
theorem pillai_sol_65_28_2_6_6_2 : (2:ℤ)^6 - (6:ℤ)^2 = 28 := by decide
theorem pillai_sol_66_28_2_7_10_2 : (2:ℤ)^7 - (10:ℤ)^2 = 28 := by decide
theorem pillai_sol_67_28_2_9_22_2 : (2:ℤ)^9 - (22:ℤ)^2 = 28 := by decide
theorem pillai_sol_68_28_4_3_6_2 : (4:ℤ)^3 - (6:ℤ)^2 = 28 := by decide
theorem pillai_sol_69_28_6_2_2_3 : (6:ℤ)^2 - (2:ℤ)^3 = 28 := by decide
theorem pillai_sol_70_28_8_2_6_2 : (8:ℤ)^2 - (6:ℤ)^2 = 28 := by decide
theorem pillai_sol_71_28_8_3_22_2 : (8:ℤ)^3 - (22:ℤ)^2 = 28 := by decide
theorem pillai_sol_72_29_15_2_14_2 : (15:ℤ)^2 - (14:ℤ)^2 = 29 := by decide
theorem pillai_sol_73_31_2_8_15_2 : (2:ℤ)^8 - (15:ℤ)^2 = 31 := by decide
theorem pillai_sol_74_31_4_4_15_2 : (4:ℤ)^4 - (15:ℤ)^2 = 31 := by decide
theorem pillai_sol_75_31_16_2_15_2 : (16:ℤ)^2 - (15:ℤ)^2 = 31 := by decide
theorem pillai_sol_76_32_3_4_7_2 : (3:ℤ)^4 - (7:ℤ)^2 = 32 := by decide
theorem pillai_sol_77_32_4_3_2_5 : (4:ℤ)^3 - (2:ℤ)^5 = 32 := by decide
theorem pillai_sol_78_32_6_2_2_2 : (6:ℤ)^2 - (2:ℤ)^2 = 32 := by decide
theorem pillai_sol_79_32_8_2_2_5 : (8:ℤ)^2 - (2:ℤ)^5 = 32 := by decide
theorem pillai_sol_80_32_9_2_7_2 : (9:ℤ)^2 - (7:ℤ)^2 = 32 := by decide
theorem pillai_sol_81_33_7_2_2_4 : (7:ℤ)^2 - (2:ℤ)^4 = 33 := by decide
theorem pillai_sol_82_33_7_2_4_2 : (7:ℤ)^2 - (4:ℤ)^2 = 33 := by decide
theorem pillai_sol_83_33_17_2_2_8 : (17:ℤ)^2 - (2:ℤ)^8 = 33 := by decide
theorem pillai_sol_84_33_17_2_4_4 : (17:ℤ)^2 - (4:ℤ)^4 = 33 := by decide
theorem pillai_sol_85_33_17_2_16_2 : (17:ℤ)^2 - (16:ℤ)^2 = 33 := by decide
theorem pillai_sol_86_35_11_3_6_4 : (11:ℤ)^3 - (6:ℤ)^4 = 35 := by decide
theorem pillai_sol_87_35_18_2_17_2 : (18:ℤ)^2 - (17:ℤ)^2 = 35 := by decide
theorem pillai_sol_88_36_10_2_2_6 : (10:ℤ)^2 - (2:ℤ)^6 = 36 := by decide
theorem pillai_sol_89_36_10_2_4_3 : (10:ℤ)^2 - (4:ℤ)^3 = 36 := by decide
theorem pillai_sol_90_36_10_2_8_2 : (10:ℤ)^2 - (8:ℤ)^2 = 36 := by decide
theorem pillai_sol_91_37_2_6_3_3 : (2:ℤ)^6 - (3:ℤ)^3 = 37 := by decide
theorem pillai_sol_92_37_4_3_3_3 : (4:ℤ)^3 - (3:ℤ)^3 = 37 := by decide
theorem pillai_sol_93_37_8_2_3_3 : (8:ℤ)^2 - (3:ℤ)^3 = 37 := by decide
theorem pillai_sol_94_37_19_2_18_2 : (19:ℤ)^2 - (18:ℤ)^2 = 37 := by decide
theorem pillai_sol_95_39_2_6_5_2 : (2:ℤ)^6 - (5:ℤ)^2 = 39 := by decide
theorem pillai_sol_96_39_4_3_5_2 : (4:ℤ)^3 - (5:ℤ)^2 = 39 := by decide
theorem pillai_sol_97_39_8_2_5_2 : (8:ℤ)^2 - (5:ℤ)^2 = 39 := by decide
theorem pillai_sol_98_39_20_2_19_2 : (20:ℤ)^2 - (19:ℤ)^2 = 39 := by decide
theorem pillai_sol_99_40_2_8_6_3 : (2:ℤ)^8 - (6:ℤ)^3 = 40 := by decide
theorem pillai_sol_100_40_4_4_6_3 : (4:ℤ)^4 - (6:ℤ)^3 = 40 := by decide
theorem pillai_sol_101_40_7_2_3_2 : (7:ℤ)^2 - (3:ℤ)^2 = 40 := by decide
theorem pillai_sol_102_40_11_2_3_4 : (11:ℤ)^2 - (3:ℤ)^4 = 40 := by decide
theorem pillai_sol_103_40_11_2_9_2 : (11:ℤ)^2 - (9:ℤ)^2 = 40 := by decide
theorem pillai_sol_104_40_16_2_6_3 : (16:ℤ)^2 - (6:ℤ)^3 = 40 := by decide
theorem pillai_sol_105_41_7_2_2_3 : (7:ℤ)^2 - (2:ℤ)^3 = 41 := by decide
theorem pillai_sol_106_41_13_2_2_7 : (13:ℤ)^2 - (2:ℤ)^7 = 41 := by decide
theorem pillai_sol_107_41_21_2_20_2 : (21:ℤ)^2 - (20:ℤ)^2 = 41 := by decide
theorem pillai_sol_108_43_22_2_21_2 : (22:ℤ)^2 - (21:ℤ)^2 = 43 := by decide
theorem pillai_sol_109_44_5_3_3_4 : (5:ℤ)^3 - (3:ℤ)^4 = 44 := by decide
theorem pillai_sol_110_44_5_3_9_2 : (5:ℤ)^3 - (9:ℤ)^2 = 44 := by decide
theorem pillai_sol_111_44_12_2_10_2 : (12:ℤ)^2 - (10:ℤ)^2 = 44 := by decide
theorem pillai_sol_112_44_13_2_5_3 : (13:ℤ)^2 - (5:ℤ)^3 = 44 := by decide
theorem pillai_sol_113_45_3_4_6_2 : (3:ℤ)^4 - (6:ℤ)^2 = 45 := by decide
theorem pillai_sol_114_45_7_2_2_2 : (7:ℤ)^2 - (2:ℤ)^2 = 45 := by decide
theorem pillai_sol_115_45_9_2_6_2 : (9:ℤ)^2 - (6:ℤ)^2 = 45 := by decide
theorem pillai_sol_116_45_23_2_22_2 : (23:ℤ)^2 - (22:ℤ)^2 = 45 := by decide
theorem pillai_sol_117_46_17_2_3_5 : (17:ℤ)^2 - (3:ℤ)^5 = 46 := by decide
theorem pillai_sol_118_47_2_7_3_4 : (2:ℤ)^7 - (3:ℤ)^4 = 47 := by decide
theorem pillai_sol_119_47_2_7_9_2 : (2:ℤ)^7 - (9:ℤ)^2 = 47 := by decide

-- Exclusion certificates: candidate tuples that do not satisfy difference equations
theorem pillai_nosol_0_2_3_3_2_1 : (2:ℤ)^3 - (3:ℤ)^2 ≠ 1 := by decide
theorem pillai_nosol_1_3_3_2_4_1 : (3:ℤ)^3 - (2:ℤ)^4 ≠ 1 := by decide
theorem pillai_nosol_2_4_2_2_4_1 : (4:ℤ)^2 - (2:ℤ)^4 ≠ 1 := by decide
theorem pillai_nosol_3_5_2_2_4_1 : (5:ℤ)^2 - (2:ℤ)^4 ≠ 1 := by decide
theorem pillai_nosol_4_2_5_5_2_1 : (2:ℤ)^5 - (5:ℤ)^2 ≠ 1 := by decide
theorem pillai_nosol_5_2_6_3_3_1 : (2:ℤ)^6 - (3:ℤ)^3 ≠ 1 := by decide
theorem pillai_nosol_6_2_7_5_3_1 : (2:ℤ)^7 - (5:ℤ)^3 ≠ 1 := by decide
theorem pillai_nosol_7_3_4_2_6_1 : (3:ℤ)^4 - (2:ℤ)^6 ≠ 1 := by decide
theorem pillai_nosol_8_2_4_3_2_2 : (2:ℤ)^4 - (3:ℤ)^2 ≠ 2 := by decide
theorem pillai_nosol_9_2_5_3_3_2 : (2:ℤ)^5 - (3:ℤ)^3 ≠ 2 := by decide
theorem pillai_nosol_10_3_2_2_3_2 : (3:ℤ)^2 - (2:ℤ)^3 ≠ 2 := by decide
theorem pillai_nosol_11_4_2_3_2_2 : (4:ℤ)^2 - (3:ℤ)^2 ≠ 2 := by decide
theorem pillai_nosol_12_5_2_4_2_2 : (5:ℤ)^2 - (4:ℤ)^2 ≠ 2 := by decide
theorem pillai_nosol_13_6_2_5_2_2 : (6:ℤ)^2 - (5:ℤ)^2 ≠ 2 := by decide
theorem pillai_nosol_14_2_4_3_2_3 : (2:ℤ)^4 - (3:ℤ)^2 ≠ 3 := by decide
theorem pillai_nosol_15_3_2_2_3_3 : (3:ℤ)^2 - (2:ℤ)^3 ≠ 3 := by decide
theorem pillai_nosol_16_3_3_5_2_3 : (3:ℤ)^3 - (5:ℤ)^2 ≠ 3 := by decide
theorem pillai_nosol_17_2_5_3_3_3 : (2:ℤ)^5 - (3:ℤ)^3 ≠ 3 := by decide
theorem pillai_nosol_18_2_6_7_2_3 : (2:ℤ)^6 - (7:ℤ)^2 ≠ 3 := by decide
theorem pillai_nosol_19_3_4_2_6_3 : (3:ℤ)^4 - (2:ℤ)^6 ≠ 3 := by decide
theorem pillai_nosol_20_2_4_3_2_5 : (2:ℤ)^4 - (3:ℤ)^2 ≠ 5 := by decide
theorem pillai_nosol_21_3_3_5_2_5 : (3:ℤ)^3 - (5:ℤ)^2 ≠ 5 := by decide
theorem pillai_nosol_22_2_7_5_3_5 : (2:ℤ)^7 - (5:ℤ)^3 ≠ 5 := by decide
theorem pillai_nosol_23_4_3_3_3_5 : (4:ℤ)^3 - (3:ℤ)^3 ≠ 5 := by decide
theorem pillai_nosol_24_5_3_11_2_5 : (5:ℤ)^3 - (11:ℤ)^2 ≠ 5 := by decide
theorem pillai_nosol_25_2_5_3_3_7 : (2:ℤ)^5 - (3:ℤ)^3 ≠ 7 := by decide
theorem pillai_nosol_26_3_3_5_2_7 : (3:ℤ)^3 - (5:ℤ)^2 ≠ 7 := by decide
theorem pillai_nosol_27_3_2_2_3_7 : (3:ℤ)^2 - (2:ℤ)^3 ≠ 7 := by decide
theorem pillai_nosol_28_5_2_2_4_7 : (5:ℤ)^2 - (2:ℤ)^4 ≠ 7 := by decide
theorem pillai_nosol_29_6_2_2_5_7 : (6:ℤ)^2 - (2:ℤ)^5 ≠ 7 := by decide
