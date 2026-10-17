-- Generated Erdős-Graham unit fraction decomposition theorems (P109)
-- Distinct positive integers d_i summing to 1 in Q and integer LCM forms.
import Mathlib.Tactic

-- General splitting identity for Egyptian fractions
theorem unit_fraction_split (k : ℚ) (h1 : k ≠ 0) (h2 : k + 1 ≠ 0) : 1 / k = 1 / (k + 1) + 1 / (k * (k + 1)) := by
  field_simp

-- Constructive rational decompositions sum(1/d_i) = 1 in ℚ
theorem erdos_graham_rat_0_2_3_6 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/6 = 1 := by norm_num
theorem erdos_graham_rat_1_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/42 = 1 := by norm_num
theorem erdos_graham_rat_2_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/43 + (1:ℚ)/1806 = 1 := by norm_num
theorem erdos_graham_rat_3_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/44 + (1:ℚ)/924 = 1 := by norm_num
theorem erdos_graham_rat_4_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/45 + (1:ℚ)/630 = 1 := by norm_num
theorem erdos_graham_rat_5_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/46 + (1:ℚ)/483 = 1 := by norm_num
theorem erdos_graham_rat_6_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/48 + (1:ℚ)/336 = 1 := by norm_num
theorem erdos_graham_rat_7_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/49 + (1:ℚ)/294 = 1 := by norm_num
theorem erdos_graham_rat_8_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/51 + (1:ℚ)/238 = 1 := by norm_num
theorem erdos_graham_rat_9_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/54 + (1:ℚ)/189 = 1 := by norm_num
theorem erdos_graham_rat_10_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/56 + (1:ℚ)/168 = 1 := by norm_num
theorem erdos_graham_rat_11_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/60 + (1:ℚ)/140 = 1 := by norm_num
theorem erdos_graham_rat_12_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/63 + (1:ℚ)/126 = 1 := by norm_num
theorem erdos_graham_rat_13_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/70 + (1:ℚ)/105 = 1 := by norm_num
theorem erdos_graham_rat_14_2_3_7 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 + (1:ℚ)/78 + (1:ℚ)/91 = 1 := by norm_num
theorem erdos_graham_rat_15_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/24 = 1 := by norm_num
theorem erdos_graham_rat_16_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/25 + (1:ℚ)/600 = 1 := by norm_num
theorem erdos_graham_rat_17_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/26 + (1:ℚ)/312 = 1 := by norm_num
theorem erdos_graham_rat_18_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/27 + (1:ℚ)/216 = 1 := by norm_num
theorem erdos_graham_rat_19_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/28 + (1:ℚ)/168 = 1 := by norm_num
theorem erdos_graham_rat_20_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/30 + (1:ℚ)/120 = 1 := by norm_num
theorem erdos_graham_rat_21_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/32 + (1:ℚ)/96 = 1 := by norm_num
theorem erdos_graham_rat_22_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/33 + (1:ℚ)/88 = 1 := by norm_num
theorem erdos_graham_rat_23_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/36 + (1:ℚ)/72 = 1 := by norm_num
theorem erdos_graham_rat_24_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/40 + (1:ℚ)/60 = 1 := by norm_num
theorem erdos_graham_rat_25_2_3_8 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/8 + (1:ℚ)/42 + (1:ℚ)/56 = 1 := by norm_num
theorem erdos_graham_rat_26_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/18 = 1 := by norm_num
theorem erdos_graham_rat_27_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/19 + (1:ℚ)/342 = 1 := by norm_num
theorem erdos_graham_rat_28_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/20 + (1:ℚ)/180 = 1 := by norm_num
theorem erdos_graham_rat_29_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/21 + (1:ℚ)/126 = 1 := by norm_num
theorem erdos_graham_rat_30_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/22 + (1:ℚ)/99 = 1 := by norm_num
theorem erdos_graham_rat_31_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/24 + (1:ℚ)/72 = 1 := by norm_num
theorem erdos_graham_rat_32_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/27 + (1:ℚ)/54 = 1 := by norm_num
theorem erdos_graham_rat_33_2_3_9 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/9 + (1:ℚ)/30 + (1:ℚ)/45 = 1 := by norm_num
theorem erdos_graham_rat_34_2_3_10 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/10 + (1:ℚ)/15 = 1 := by norm_num
theorem erdos_graham_rat_35_2_3_10 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/10 + (1:ℚ)/16 + (1:ℚ)/240 = 1 := by norm_num
theorem erdos_graham_rat_36_2_3_10 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/10 + (1:ℚ)/18 + (1:ℚ)/90 = 1 := by norm_num
theorem erdos_graham_rat_37_2_3_10 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/10 + (1:ℚ)/20 + (1:ℚ)/60 = 1 := by norm_num
theorem erdos_graham_rat_38_2_3_10 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/10 + (1:ℚ)/24 + (1:ℚ)/40 = 1 := by norm_num
theorem erdos_graham_rat_39_2_3_11 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/11 + (1:ℚ)/14 + (1:ℚ)/231 = 1 := by norm_num
theorem erdos_graham_rat_40_2_3_11 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/11 + (1:ℚ)/15 + (1:ℚ)/110 = 1 := by norm_num
theorem erdos_graham_rat_41_2_3_11 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/11 + (1:ℚ)/22 + (1:ℚ)/33 = 1 := by norm_num
theorem erdos_graham_rat_42_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/13 + (1:ℚ)/156 = 1 := by norm_num
theorem erdos_graham_rat_43_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/14 + (1:ℚ)/84 = 1 := by norm_num
theorem erdos_graham_rat_44_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/15 + (1:ℚ)/60 = 1 := by norm_num
theorem erdos_graham_rat_45_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/16 + (1:ℚ)/48 = 1 := by norm_num
theorem erdos_graham_rat_46_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/18 + (1:ℚ)/36 = 1 := by norm_num
theorem erdos_graham_rat_47_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/20 + (1:ℚ)/30 = 1 := by norm_num
theorem erdos_graham_rat_48_2_3_12 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/12 + (1:ℚ)/21 + (1:ℚ)/28 = 1 := by norm_num
theorem erdos_graham_rat_49_2_3_14 : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/14 + (1:ℚ)/15 + (1:ℚ)/35 = 1 := by norm_num
theorem erdos_graham_rat_50_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/20 = 1 := by norm_num
theorem erdos_graham_rat_51_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/21 + (1:ℚ)/420 = 1 := by norm_num
theorem erdos_graham_rat_52_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/22 + (1:ℚ)/220 = 1 := by norm_num
theorem erdos_graham_rat_53_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/24 + (1:ℚ)/120 = 1 := by norm_num
theorem erdos_graham_rat_54_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/25 + (1:ℚ)/100 = 1 := by norm_num
theorem erdos_graham_rat_55_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/28 + (1:ℚ)/70 = 1 := by norm_num
theorem erdos_graham_rat_56_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/30 + (1:ℚ)/60 = 1 := by norm_num
theorem erdos_graham_rat_57_2_4_5 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/36 + (1:ℚ)/45 = 1 := by norm_num
theorem erdos_graham_rat_58_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/12 = 1 := by norm_num
theorem erdos_graham_rat_59_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/13 + (1:ℚ)/156 = 1 := by norm_num
theorem erdos_graham_rat_60_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/14 + (1:ℚ)/84 = 1 := by norm_num
theorem erdos_graham_rat_61_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/15 + (1:ℚ)/60 = 1 := by norm_num
theorem erdos_graham_rat_62_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/16 + (1:ℚ)/48 = 1 := by norm_num
theorem erdos_graham_rat_63_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/18 + (1:ℚ)/36 = 1 := by norm_num
theorem erdos_graham_rat_64_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/20 + (1:ℚ)/30 = 1 := by norm_num
theorem erdos_graham_rat_65_2_4_6 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/6 + (1:ℚ)/21 + (1:ℚ)/28 = 1 := by norm_num
theorem erdos_graham_rat_66_2_4_7 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/7 + (1:ℚ)/10 + (1:ℚ)/140 = 1 := by norm_num
theorem erdos_graham_rat_67_2_4_7 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/7 + (1:ℚ)/12 + (1:ℚ)/42 = 1 := by norm_num
theorem erdos_graham_rat_68_2_4_7 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/7 + (1:ℚ)/14 + (1:ℚ)/28 = 1 := by norm_num
theorem erdos_graham_rat_69_2_4_8 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/8 + (1:ℚ)/9 + (1:ℚ)/72 = 1 := by norm_num
theorem erdos_graham_rat_70_2_4_8 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/8 + (1:ℚ)/10 + (1:ℚ)/40 = 1 := by norm_num
theorem erdos_graham_rat_71_2_4_8 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/8 + (1:ℚ)/12 + (1:ℚ)/24 = 1 := by norm_num
theorem erdos_graham_rat_72_2_4_9 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/9 + (1:ℚ)/12 + (1:ℚ)/18 = 1 := by norm_num
theorem erdos_graham_rat_73_2_4_10 : (1:ℚ)/2 + (1:ℚ)/4 + (1:ℚ)/10 + (1:ℚ)/12 + (1:ℚ)/15 = 1 := by norm_num
theorem erdos_graham_rat_74_2_5_6 : (1:ℚ)/2 + (1:ℚ)/5 + (1:ℚ)/6 + (1:ℚ)/8 + (1:ℚ)/120 = 1 := by norm_num
theorem erdos_graham_rat_75_2_5_6 : (1:ℚ)/2 + (1:ℚ)/5 + (1:ℚ)/6 + (1:ℚ)/9 + (1:ℚ)/45 = 1 := by norm_num
theorem erdos_graham_rat_76_2_5_6 : (1:ℚ)/2 + (1:ℚ)/5 + (1:ℚ)/6 + (1:ℚ)/10 + (1:ℚ)/30 = 1 := by norm_num
theorem erdos_graham_rat_77_2_5_6 : (1:ℚ)/2 + (1:ℚ)/5 + (1:ℚ)/6 + (1:ℚ)/12 + (1:ℚ)/20 = 1 := by norm_num
theorem erdos_graham_rat_78_3_4_5 : (1:ℚ)/3 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/6 + (1:ℚ)/20 = 1 := by norm_num

-- Integer LCM scaled identities sum(L/d_i) = L in ℕ
theorem erdos_graham_lcm_0 : 6 / 2 + 6 / 3 + 6 / 6 = 6 := by omega
theorem erdos_graham_lcm_1 : 42 / 2 + 42 / 3 + 42 / 7 + 42 / 42 = 42 := by omega
theorem erdos_graham_lcm_2 : 1806 / 2 + 1806 / 3 + 1806 / 7 + 1806 / 43 + 1806 / 1806 = 1806 := by omega
theorem erdos_graham_lcm_3 : 924 / 2 + 924 / 3 + 924 / 7 + 924 / 44 + 924 / 924 = 924 := by omega
theorem erdos_graham_lcm_4 : 630 / 2 + 630 / 3 + 630 / 7 + 630 / 45 + 630 / 630 = 630 := by omega
theorem erdos_graham_lcm_5 : 966 / 2 + 966 / 3 + 966 / 7 + 966 / 46 + 966 / 483 = 966 := by omega
theorem erdos_graham_lcm_6 : 336 / 2 + 336 / 3 + 336 / 7 + 336 / 48 + 336 / 336 = 336 := by omega
theorem erdos_graham_lcm_7 : 294 / 2 + 294 / 3 + 294 / 7 + 294 / 49 + 294 / 294 = 294 := by omega
theorem erdos_graham_lcm_8 : 714 / 2 + 714 / 3 + 714 / 7 + 714 / 51 + 714 / 238 = 714 := by omega
theorem erdos_graham_lcm_9 : 378 / 2 + 378 / 3 + 378 / 7 + 378 / 54 + 378 / 189 = 378 := by omega
theorem erdos_graham_lcm_10 : 168 / 2 + 168 / 3 + 168 / 7 + 168 / 56 + 168 / 168 = 168 := by omega
theorem erdos_graham_lcm_11 : 420 / 2 + 420 / 3 + 420 / 7 + 420 / 60 + 420 / 140 = 420 := by omega
theorem erdos_graham_lcm_12 : 126 / 2 + 126 / 3 + 126 / 7 + 126 / 63 + 126 / 126 = 126 := by omega
theorem erdos_graham_lcm_13 : 210 / 2 + 210 / 3 + 210 / 7 + 210 / 70 + 210 / 105 = 210 := by omega
theorem erdos_graham_lcm_14 : 546 / 2 + 546 / 3 + 546 / 7 + 546 / 78 + 546 / 91 = 546 := by omega
theorem erdos_graham_lcm_15 : 24 / 2 + 24 / 3 + 24 / 8 + 24 / 24 = 24 := by omega
theorem erdos_graham_lcm_16 : 600 / 2 + 600 / 3 + 600 / 8 + 600 / 25 + 600 / 600 = 600 := by omega
theorem erdos_graham_lcm_17 : 312 / 2 + 312 / 3 + 312 / 8 + 312 / 26 + 312 / 312 = 312 := by omega
theorem erdos_graham_lcm_18 : 216 / 2 + 216 / 3 + 216 / 8 + 216 / 27 + 216 / 216 = 216 := by omega
theorem erdos_graham_lcm_19 : 168 / 2 + 168 / 3 + 168 / 8 + 168 / 28 + 168 / 168 = 168 := by omega
theorem erdos_graham_lcm_20 : 120 / 2 + 120 / 3 + 120 / 8 + 120 / 30 + 120 / 120 = 120 := by omega
theorem erdos_graham_lcm_21 : 96 / 2 + 96 / 3 + 96 / 8 + 96 / 32 + 96 / 96 = 96 := by omega
theorem erdos_graham_lcm_22 : 264 / 2 + 264 / 3 + 264 / 8 + 264 / 33 + 264 / 88 = 264 := by omega
theorem erdos_graham_lcm_23 : 72 / 2 + 72 / 3 + 72 / 8 + 72 / 36 + 72 / 72 = 72 := by omega
theorem erdos_graham_lcm_24 : 120 / 2 + 120 / 3 + 120 / 8 + 120 / 40 + 120 / 60 = 120 := by omega

-- Harmonic density bounds and splitting lemmas
theorem erdos_graham_min_den_bound : ∀ (a b c : ℕ), a ≥ 2 → b ≥ 2 → c ≥ 2 → a + b + c ≥ 6 := by omega
theorem erdos_graham_three_sum_bound : (1:ℚ)/2 + (1:ℚ)/3 + (1:ℚ)/7 < 1 := by norm_num
theorem erdos_graham_four_sum_bound : (1:ℚ)/3 + (1:ℚ)/4 + (1:ℚ)/5 + (1:ℚ)/6 < 1 := by norm_num
theorem erdos_graham_unit_upper_two (d : ℕ) (h : d ≥ 2) : 2 * d ≥ 4 := by omega
theorem erdos_graham_unit_split_three : (1:ℚ)/3 = (1:ℚ)/4 + (1:ℚ)/12 := by norm_num
theorem erdos_graham_unit_split_four : (1:ℚ)/4 = (1:ℚ)/5 + (1:ℚ)/20 := by norm_num
theorem erdos_graham_unit_split_five : (1:ℚ)/5 = (1:ℚ)/6 + (1:ℚ)/30 := by norm_num
theorem erdos_graham_unit_split_six : (1:ℚ)/6 = (1:ℚ)/7 + (1:ℚ)/42 := by norm_num
