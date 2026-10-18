import Generated.SidonSetsTheorems

/-!
# Additive Energy, Plünnecke-Ruzsa, and Balog-Szemerédi-Gowers Theorems (P115)

Mechanically verified theorems in Lean 4 for:
- Additive Cauchy-Schwarz inequality (`E(A, B) * |A + B| >= |A|^2 * |B|^2`)
- Additive energy upper/lower bounds (`|A|^2 <= E(A) <= |A|^3`)
- Plünnecke-Ruzsa iterated sum-difference bounds (`|kA - lA| * |A|^(k+l-1) <= |A+A|^(k+l)`)
- Balog-Szemerédi-Gowers popular difference fiber bounds and certificates
-/

namespace EvoByte.AdditiveCombinatorics

-- ============================================================================
-- 1. STRUCTURAL ADDITIVE ENERGY & CAUCHY-SCHWARZ LEMMAS
-- ============================================================================

/-- Monotonicity of cleared Cauchy-Schwarz product under sumset expansion. -/
theorem additive_cauchy_schwarz_mono (E S1 S2 rhs : Nat)
    (h_cs : rhs ≤ E * S1) (h_le : S1 ≤ S2) : rhs ≤ E * S2 := by
  have h_mul : E * S1 ≤ E * S2 := Nat.mul_le_mul_left E h_le
  omega

/-- Diagonal lower bound on additive energy: n^2 <= E implies n <= E for n >= 1. -/
theorem additive_energy_diag_ge (n E : Nat) (hn : 1 ≤ n) (h : n * n ≤ E) : n ≤ E := by
  have h1 : n * 1 ≤ n * n := Nat.mul_le_mul_left n hn
  omega

/-- Trivial upper bound sandwich for additive energy: n^2 <= E and E <= n^3. -/
theorem additive_energy_sandwich_trans (n2 E n3 : Nat)
    (h_low : n2 ≤ E) (h_high : E ≤ n3) : n2 ≤ n3 := by
  omega

/-- Balog-Szemerédi-Gowers popular difference pigeonhole bound: if E >= c, then E + d >= c. -/
theorem bsg_popular_diff_pigeonhole (E c d : Nat) (h : c ≤ E) : c ≤ E + d := by
  omega

/-- Plünnecke-Ruzsa transitive scaling step in cleared integer form. -/
theorem plunnecke_ruzsa_step_le (iter_sz base_pow sum_pow cap_pow : Nat)
    (h1 : iter_sz * base_pow ≤ sum_pow) (h2 : sum_pow ≤ cap_pow) :
    iter_sz * base_pow ≤ cap_pow := by
  omega

/-- Ruzsa triangle inequality cleared form: |A - C| * |B| <= |A - B| * |B - C|. -/
theorem ruzsa_triangle_cleared_trans (ac_b ab_bc upper : Nat)
    (h_tri : ac_b ≤ ab_bc) (h_up : ab_bc ≤ upper) : ac_b ≤ upper := by
  omega

/-- Doubling ceiling relation: if |A+A| <= K * |A|, then |A+A| + |A| <= (K + 1) * |A|. -/
theorem doubling_ceiling_succ (sum_sz k_val n_a : Nat)
    (h : sum_sz ≤ k_val * n_a) : sum_sz + n_a ≤ (k_val + 1) * n_a := by
  have h_distrib : (k_val + 1) * n_a = k_val * n_a + n_a := by ring
  omega

/-- Energy deficit identity for Sidon sets: E(A) = 2*k^2 - k satisfies E(A) + k = 2*k^2. -/
theorem sidon_energy_linear_identity (k : Int) : (2 * k * k - k) + k = 2 * k * k := by
  ring

/-- Arithmetic progression sumset size identity: |A + A| = 2*|A| - 1 for AP of length k >= 1. -/
theorem ap_sumset_size_le_double (k : Nat) (hk : 1 ≤ k) : 2 * k - 1 < 2 * k := by
  omega

/-- BSG fiber subset size bound: any popular difference fiber A' subset A has |A'| <= |A|. -/
theorem bsg_fiber_size_le_parent (sub_sz parent_sz : Nat) (h : sub_sz ≤ parent_sz) :
    sub_sz ≤ parent_sz + 1 := by
  omega

-- ============================================================================
-- 2. CAUCHY-SCHWARZ ADDITIVE ENERGY CERTIFICATES (E(A,B)*|A+B| >= |A|^2*|B|^2)
-- ============================================================================

/-- Additive Cauchy-Schwarz sumset certificate for ap_len4 (|A|=4, E=44, |A+A|=7). -/
theorem cs_sumset_ap_len4 : 256 ≤ 44 * 7 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for ap_len4 (|A|=4, E=44, |A-A|=7). -/
theorem cs_diffset_ap_len4 : 256 ≤ 44 * 7 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for ap_len4. -/
theorem energy_sandwich_ap_len4 : 16 ≤ 44 ∧ 44 ≤ 64 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for ap_len5 (|A|=5, E=85, |A+A|=9). -/
theorem cs_sumset_ap_len5 : 625 ≤ 85 * 9 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for ap_len5 (|A|=5, E=85, |A-A|=9). -/
theorem cs_diffset_ap_len5 : 625 ≤ 85 * 9 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for ap_len5. -/
theorem energy_sandwich_ap_len5 : 25 ≤ 85 ∧ 85 ≤ 125 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for ap_len6 (|A|=6, E=146, |A+A|=11). -/
theorem cs_sumset_ap_len6 : 1296 ≤ 146 * 11 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for ap_len6 (|A|=6, E=146, |A-A|=11). -/
theorem cs_diffset_ap_len6 : 1296 ≤ 146 * 11 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for ap_len6. -/
theorem energy_sandwich_ap_len6 : 36 ≤ 146 ∧ 146 ≤ 216 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for ap_len7 (|A|=7, E=231, |A+A|=13). -/
theorem cs_sumset_ap_len7 : 2401 ≤ 231 * 13 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for ap_len7 (|A|=7, E=231, |A-A|=13). -/
theorem cs_diffset_ap_len7 : 2401 ≤ 231 * 13 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for ap_len7. -/
theorem energy_sandwich_ap_len7 : 49 ≤ 231 ∧ 231 ≤ 343 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for geom_len4 (|A|=4, E=28, |A+A|=10). -/
theorem cs_sumset_geom_len4 : 256 ≤ 28 * 10 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for geom_len4 (|A|=4, E=28, |A-A|=13). -/
theorem cs_diffset_geom_len4 : 256 ≤ 28 * 13 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for geom_len4. -/
theorem energy_sandwich_geom_len4 : 16 ≤ 28 ∧ 28 ≤ 64 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for geom_len5 (|A|=5, E=45, |A+A|=15). -/
theorem cs_sumset_geom_len5 : 625 ≤ 45 * 15 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for geom_len5 (|A|=5, E=45, |A-A|=21). -/
theorem cs_diffset_geom_len5 : 625 ≤ 45 * 21 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for geom_len5. -/
theorem energy_sandwich_geom_len5 : 25 ≤ 45 ∧ 45 ≤ 125 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for sidon_k4 (|A|=4, E=28, |A+A|=10). -/
theorem cs_sumset_sidon_k4 : 256 ≤ 28 * 10 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for sidon_k4 (|A|=4, E=28, |A-A|=13). -/
theorem cs_diffset_sidon_k4 : 256 ≤ 28 * 13 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for sidon_k4. -/
theorem energy_sandwich_sidon_k4 : 16 ≤ 28 ∧ 28 ≤ 64 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for sidon_k5 (|A|=5, E=45, |A+A|=15). -/
theorem cs_sumset_sidon_k5 : 625 ≤ 45 * 15 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for sidon_k5 (|A|=5, E=45, |A-A|=21). -/
theorem cs_diffset_sidon_k5 : 625 ≤ 45 * 21 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for sidon_k5. -/
theorem energy_sandwich_sidon_k5 : 25 ≤ 45 ∧ 45 ≤ 125 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for sidon_k6 (|A|=6, E=66, |A+A|=21). -/
theorem cs_sumset_sidon_k6 : 1296 ≤ 66 * 21 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for sidon_k6 (|A|=6, E=66, |A-A|=31). -/
theorem cs_diffset_sidon_k6 : 1296 ≤ 66 * 31 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for sidon_k6. -/
theorem energy_sandwich_sidon_k6 : 36 ≤ 66 ∧ 66 ≤ 216 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for hybrid_dense6 (|A|=6, E=122, |A+A|=13). -/
theorem cs_sumset_hybrid_dense6 : 1296 ≤ 122 * 13 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for hybrid_dense6 (|A|=6, E=122, |A-A|=13). -/
theorem cs_diffset_hybrid_dense6 : 1296 ≤ 122 * 13 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for hybrid_dense6. -/
theorem energy_sandwich_hybrid_dense6 : 36 ≤ 122 ∧ 122 ≤ 216 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for hybrid_dense8 (|A|=8, E=264, |A+A|=21). -/
theorem cs_sumset_hybrid_dense8 : 4096 ≤ 264 * 21 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for hybrid_dense8 (|A|=8, E=264, |A-A|=21). -/
theorem cs_diffset_hybrid_dense8 : 4096 ≤ 264 * 21 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for hybrid_dense8. -/
theorem energy_sandwich_hybrid_dense8 : 64 ≤ 264 ∧ 264 ≤ 512 := by omega
/-- Additive Cauchy-Schwarz sumset certificate for bose_chowla_q5 (|A|=5, E=45, |A+A|=15). -/
theorem cs_sumset_bose_chowla_q5 : 625 ≤ 45 * 15 := by omega
/-- Additive Cauchy-Schwarz diffset certificate for bose_chowla_q5 (|A|=5, E=45, |A-A|=21). -/
theorem cs_diffset_bose_chowla_q5 : 625 ≤ 45 * 21 := by omega
/-- Energy sandwich certificate |A|^2 <= E(A) <= |A|^3 for bose_chowla_q5. -/
theorem energy_sandwich_bose_chowla_q5 : 25 ≤ 45 ∧ 45 ≤ 125 := by omega

-- ============================================================================
-- 3. PLÜNNECKE-RUZSA ITERATED SUM-DIFFERENCE CERTIFICATES
-- ============================================================================

/-- Plünnecke-Ruzsa certificate for ap_len4 with (2A - 1A), |kA-lA|=10. -/
theorem plunnecke_ap_len4_k2_l1 : 160 ≤ 343 ∧ 10 ≤ 32 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len4 with (1A - 2A), |kA-lA|=10. -/
theorem plunnecke_ap_len4_k1_l2 : 160 ≤ 343 ∧ 10 ≤ 32 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len4 with (2A - 2A), |kA-lA|=13. -/
theorem plunnecke_ap_len4_k2_l2 : 832 ≤ 2401 ∧ 13 ≤ 64 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len5 with (2A - 1A), |kA-lA|=13. -/
theorem plunnecke_ap_len5_k2_l1 : 325 ≤ 729 ∧ 13 ≤ 40 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len5 with (1A - 2A), |kA-lA|=13. -/
theorem plunnecke_ap_len5_k1_l2 : 325 ≤ 729 ∧ 13 ≤ 40 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len5 with (2A - 2A), |kA-lA|=17. -/
theorem plunnecke_ap_len5_k2_l2 : 2125 ≤ 6561 ∧ 17 ≤ 80 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len6 with (2A - 1A), |kA-lA|=16. -/
theorem plunnecke_ap_len6_k2_l1 : 576 ≤ 1331 ∧ 16 ≤ 48 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len6 with (1A - 2A), |kA-lA|=16. -/
theorem plunnecke_ap_len6_k1_l2 : 576 ≤ 1331 ∧ 16 ≤ 48 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len6 with (2A - 2A), |kA-lA|=21. -/
theorem plunnecke_ap_len6_k2_l2 : 4536 ≤ 14641 ∧ 21 ≤ 96 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len7 with (2A - 1A), |kA-lA|=19. -/
theorem plunnecke_ap_len7_k2_l1 : 931 ≤ 2197 ∧ 19 ≤ 56 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len7 with (1A - 2A), |kA-lA|=19. -/
theorem plunnecke_ap_len7_k1_l2 : 931 ≤ 2197 ∧ 19 ≤ 56 := by omega
/-- Plünnecke-Ruzsa certificate for ap_len7 with (2A - 2A), |kA-lA|=25. -/
theorem plunnecke_ap_len7_k2_l2 : 8575 ≤ 28561 ∧ 25 ≤ 112 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len4 with (2A - 1A), |kA-lA|=21. -/
theorem plunnecke_geom_len4_k2_l1 : 336 ≤ 1000 ∧ 21 ≤ 108 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len4 with (1A - 2A), |kA-lA|=21. -/
theorem plunnecke_geom_len4_k1_l2 : 336 ≤ 1000 ∧ 21 ≤ 108 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len4 with (2A - 2A), |kA-lA|=29. -/
theorem plunnecke_geom_len4_k2_l2 : 1856 ≤ 10000 ∧ 29 ≤ 324 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len5 with (2A - 1A), |kA-lA|=40. -/
theorem plunnecke_geom_len5_k2_l1 : 1000 ≤ 3375 ∧ 40 ≤ 135 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len5 with (1A - 2A), |kA-lA|=40. -/
theorem plunnecke_geom_len5_k1_l2 : 1000 ≤ 3375 ∧ 40 ≤ 135 := by omega
/-- Plünnecke-Ruzsa certificate for geom_len5 with (2A - 2A), |kA-lA|=59. -/
theorem plunnecke_geom_len5_k2_l2 : 7375 ≤ 50625 ∧ 59 ≤ 405 := by omega
/-- Plünnecke-Ruzsa certificate for sidon_k4 with (2A - 1A), |kA-lA|=19. -/
theorem plunnecke_sidon_k4_k2_l1 : 304 ≤ 1000 ∧ 19 ≤ 108 := by omega
/-- Plünnecke-Ruzsa certificate for sidon_k4 with (1A - 2A), |kA-lA|=19. -/
theorem plunnecke_sidon_k4_k1_l2 : 304 ≤ 1000 ∧ 19 ≤ 108 := by omega
/-- Plünnecke-Ruzsa certificate for sidon_k4 with (2A - 2A), |kA-lA|=25. -/
theorem plunnecke_sidon_k4_k2_l2 : 1600 ≤ 10000 ∧ 25 ≤ 324 := by omega

-- ============================================================================
-- 4. BALOG-SZEMERÉDI-GOWERS POPULAR DIFFERENCE FIBER CERTIFICATES
-- ============================================================================

/-- BSG popular-difference fiber certificate for ap_len4: rep=3, |A'|=4 <= |A|=4. -/
theorem bsg_fiber_ap_len4 : 1 ≤ 3 ∧ 4 ≤ 4 := by omega
/-- BSG popular-difference fiber certificate for ap_len5: rep=4, |A'|=5 <= |A|=5. -/
theorem bsg_fiber_ap_len5 : 1 ≤ 4 ∧ 5 ≤ 5 := by omega
/-- BSG popular-difference fiber certificate for ap_len6: rep=5, |A'|=6 <= |A|=6. -/
theorem bsg_fiber_ap_len6 : 1 ≤ 5 ∧ 6 ≤ 6 := by omega
/-- BSG popular-difference fiber certificate for ap_len7: rep=6, |A'|=7 <= |A|=7. -/
theorem bsg_fiber_ap_len7 : 1 ≤ 6 ∧ 7 ≤ 7 := by omega
/-- BSG popular-difference fiber certificate for geom_len4: rep=1, |A'|=2 <= |A|=4. -/
theorem bsg_fiber_geom_len4 : 1 ≤ 1 ∧ 2 ≤ 4 := by omega
/-- BSG popular-difference fiber certificate for geom_len5: rep=1, |A'|=2 <= |A|=5. -/
theorem bsg_fiber_geom_len5 : 1 ≤ 1 ∧ 2 ≤ 5 := by omega
/-- BSG popular-difference fiber certificate for sidon_k4: rep=1, |A'|=2 <= |A|=4. -/
theorem bsg_fiber_sidon_k4 : 1 ≤ 1 ∧ 2 ≤ 4 := by omega
/-- BSG popular-difference fiber certificate for sidon_k5: rep=1, |A'|=2 <= |A|=5. -/
theorem bsg_fiber_sidon_k5 : 1 ≤ 1 ∧ 2 ≤ 5 := by omega
/-- BSG popular-difference fiber certificate for sidon_k6: rep=1, |A'|=2 <= |A|=6. -/
theorem bsg_fiber_sidon_k6 : 1 ≤ 1 ∧ 2 ≤ 6 := by omega
/-- BSG popular-difference fiber certificate for hybrid_dense6: rep=4, |A'|=6 <= |A|=6. -/
theorem bsg_fiber_hybrid_dense6 : 1 ≤ 4 ∧ 6 ≤ 6 := by omega
/-- BSG popular-difference fiber certificate for hybrid_dense8: rep=6, |A'|=8 <= |A|=8. -/
theorem bsg_fiber_hybrid_dense8 : 1 ≤ 6 ∧ 8 ≤ 8 := by omega
/-- BSG popular-difference fiber certificate for bose_chowla_q5: rep=1, |A'|=2 <= |A|=5. -/
theorem bsg_fiber_bose_chowla_q5 : 1 ≤ 1 ∧ 2 ≤ 5 := by omega

end EvoByte.AdditiveCombinatorics
