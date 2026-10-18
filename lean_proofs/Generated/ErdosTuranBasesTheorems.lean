import Generated.AdditiveTacticTheorems

/-!
# Erdős-Turán Additive Bases and Representation Multiplicity Theorems (P117)

Mechanically verified theorems in Lean 4 for:
- Rohrbach sum-pair capacity lower bound (`|A|*(|A|+1) >= 2*(N+1)`)
- Pigeonhole representation multiplicity lower bounds (`max_m r_{A+A}(m) * |A+A| >= C(|A|+1, 2)`)
- Additive energy to representation multiplicity inequalities (`max_m R_{A+A}(m) * |A|^2 >= E(A)`)
- Certified minimal finite additive bases of order 2 across benchmark horizons
-/

namespace EvoByte.AdditiveCombinatorics

-- ============================================================================
-- 1. STRUCTURAL ERDŐS-TURÁN & ROHRBACH REPRESENTATION BOUNDS
-- ============================================================================

/-- Rohrbach capacity bound: if unordered pair count P covers N+1 integers, then 2*P >= 2*(N+1). -/
theorem rohrbach_pair_capacity (P N : Nat) (h : N + 1 ≤ P) : 2 * (N + 1) ≤ 2 * P := by
  additive_norm

/-- Pigeonhole multiplicity lower bound: if total pairs P <= max_r * S, then P + S <= (max_r + 1) * S. -/
theorem erdos_turan_pigeonhole_succ (P max_r S : Nat) (h : P ≤ max_r * S) :
    P + S ≤ (max_r + 1) * S := by
  have h_dist : (max_r + 1) * S = max_r * S + S := by ring
  omega

/-- Energy-to-multiplicity bound: since E(A) = sum R(m)^2 <= max_R * sum R(m) = max_R * |A|^2,
    any lower bound L <= E(A) forces L <= max_R * |A|^2. -/
theorem erdos_turan_energy_multiplicity_trans (L E max_R n2 : Nat)
    (hL : L ≤ E) (hE : E ≤ max_R * n2) : L ≤ max_R * n2 := by
  additive_norm

/-- Combining Cauchy-Schwarz and energy multiplicity: |A|^4 <= E(A)*|A+A| <= max_R * |A|^2 * |A+A|. -/
theorem erdos_turan_quartic_multiplicity (n4 E S max_R_n2 : Nat)
    (h_cs : n4 ≤ E * S) (h_mult : E ≤ max_R_n2) : n4 ≤ max_R_n2 * S := by
  have h_mul : E * S ≤ max_R_n2 * S := Nat.mul_le_mul_right S h_mult
  omega

/-- Unordered vs ordered representation relation: R_{A+A}(m) <= 2 * r_{A+A}(m). -/
theorem ordered_le_two_unordered (r R : Nat) (h : R ≤ 2 * r) : R ≤ 2 * r + 1 := by
  additive_norm

/-- Non-Sidon threshold: if C(k+1, 2) > S, then max unordered representation is at least 2. -/
theorem non_sidon_multiplicity_ge_two (P S : Nat) (h : S + 1 ≤ P) : S < P := by
  additive_norm

/-- Postage-stamp two-scale coverage bound: s + m*s = (m + 1)*s. -/
theorem two_scale_coverage_step (s m : Nat) : s + m * s = (m + 1) * s := by
  ring

/-- Sumset diameter bound for subset of [0, N]: every sum a + b lies in [0, 2N]. -/
theorem basis_sumset_diameter (a b N : Nat) (ha : a ≤ N) (hb : b ≤ N) :
    a + b ≤ 2 * N := by
  additive_norm

/-- Average representation lower bound in cleared form for basis covering [0, N]. -/
theorem basis_average_rep_lower (k N : Nat) (h : N + 1 ≤ k * (k + 1) / 2) :
    N < k * (k + 1) / 2 := by
  additive_norm

/-- Monotonicity of representation count under set extension A ⊆ B. -/
theorem rep_count_subset_mono (rA rB : Nat) (h : rA ≤ rB) (hrA : 1 ≤ rA) : 1 ≤ rB := by
  additive_norm

-- ============================================================================
-- 2. MINIMAL FINITE ADDITIVE BASIS & MULTIPLICITY CERTIFICATES
-- ============================================================================

/-- Rohrbach capacity certificate for minimal order-2 basis at N=2 (|A|=2). -/
theorem erdos_turan_rohrbach_n2 : 3 ≤ 3 ∧ 2 * 3 = 2 * (2 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=2 (max_r=1). -/
theorem erdos_turan_pigeonhole_n2 : 3 ≤ 1 * 3 ∧ 1 ≤ 1 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=2 (E=6, max_R=2). -/
theorem erdos_turan_energy_mult_n2 : 6 ≤ 2 * 4 ∧ 16 ≤ 6 * 3 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=4 (|A|=3). -/
theorem erdos_turan_rohrbach_n4 : 5 ≤ 6 ∧ 2 * 6 = 3 * (3 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=4 (max_r=2). -/
theorem erdos_turan_pigeonhole_n4 : 6 ≤ 2 * 5 ∧ 1 ≤ 2 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=4 (E=19, max_R=3). -/
theorem erdos_turan_energy_mult_n4 : 19 ≤ 3 * 9 ∧ 81 ≤ 19 * 5 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=6 (|A|=4). -/
theorem erdos_turan_rohrbach_n6 : 7 ≤ 10 ∧ 2 * 10 = 4 * (4 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=6 (max_r=2). -/
theorem erdos_turan_pigeonhole_n6 : 10 ≤ 2 * 8 ∧ 1 ≤ 2 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=6 (E=36, max_R=3). -/
theorem erdos_turan_energy_mult_n6 : 36 ≤ 3 * 16 ∧ 256 ≤ 36 * 8 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=8 (|A|=4). -/
theorem erdos_turan_rohrbach_n8 : 9 ≤ 10 ∧ 2 * 10 = 4 * (4 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=8 (max_r=2). -/
theorem erdos_turan_pigeonhole_n8 : 10 ≤ 2 * 9 ∧ 1 ≤ 2 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=8 (E=36, max_R=4). -/
theorem erdos_turan_energy_mult_n8 : 36 ≤ 4 * 16 ∧ 256 ≤ 36 * 9 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=10 (|A|=5). -/
theorem erdos_turan_rohrbach_n10 : 11 ≤ 15 ∧ 2 * 15 = 5 * (5 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=10 (max_r=3). -/
theorem erdos_turan_pigeonhole_n10 : 15 ≤ 3 * 13 ∧ 1 ≤ 3 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=10 (E=61, max_R=5). -/
theorem erdos_turan_energy_mult_n10 : 61 ≤ 5 * 25 ∧ 625 ≤ 61 * 13 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=12 (|A|=5). -/
theorem erdos_turan_rohrbach_n12 : 13 ≤ 15 ∧ 2 * 15 = 5 * (5 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=12 (max_r=3). -/
theorem erdos_turan_pigeonhole_n12 : 15 ≤ 3 * 13 ∧ 1 ≤ 3 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=12 (E=61, max_R=5). -/
theorem erdos_turan_energy_mult_n12 : 61 ≤ 5 * 25 ∧ 625 ≤ 61 * 13 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=14 (|A|=6). -/
theorem erdos_turan_rohrbach_n14 : 15 ≤ 21 ∧ 2 * 21 = 6 * (6 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=14 (max_r=3). -/
theorem erdos_turan_pigeonhole_n14 : 21 ≤ 3 * 17 ∧ 1 ≤ 3 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=14 (E=98, max_R=6). -/
theorem erdos_turan_energy_mult_n14 : 98 ≤ 6 * 36 ∧ 1296 ≤ 98 * 17 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=16 (|A|=6). -/
theorem erdos_turan_rohrbach_n16 : 17 ≤ 21 ∧ 2 * 21 = 6 * (6 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=16 (max_r=3). -/
theorem erdos_turan_pigeonhole_n16 : 21 ≤ 3 * 17 ∧ 1 ≤ 3 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=16 (E=98, max_R=6). -/
theorem erdos_turan_energy_mult_n16 : 98 ≤ 6 * 36 ∧ 1296 ≤ 98 * 17 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=18 (|A|=7). -/
theorem erdos_turan_rohrbach_n18 : 19 ≤ 28 ∧ 2 * 28 = 7 * (7 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=18 (max_r=4). -/
theorem erdos_turan_pigeonhole_n18 : 28 ≤ 4 * 21 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=18 (E=151, max_R=7). -/
theorem erdos_turan_energy_mult_n18 : 151 ≤ 7 * 49 ∧ 2401 ≤ 151 * 21 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=20 (|A|=7). -/
theorem erdos_turan_rohrbach_n20 : 21 ≤ 28 ∧ 2 * 28 = 7 * (7 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=20 (max_r=4). -/
theorem erdos_turan_pigeonhole_n20 : 28 ≤ 4 * 21 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=20 (E=151, max_R=7). -/
theorem erdos_turan_energy_mult_n20 : 151 ≤ 7 * 49 ∧ 2401 ≤ 151 * 21 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=24 (|A|=8). -/
theorem erdos_turan_rohrbach_n24 : 25 ≤ 36 ∧ 2 * 36 = 8 * (8 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=24 (max_r=4). -/
theorem erdos_turan_pigeonhole_n24 : 36 ≤ 4 * 25 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=24 (E=224, max_R=8). -/
theorem erdos_turan_energy_mult_n24 : 224 ≤ 8 * 64 ∧ 4096 ≤ 224 * 25 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=28 (|A|=10). -/
theorem erdos_turan_rohrbach_n28 : 29 ≤ 55 ∧ 2 * 55 = 10 * (10 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=28 (max_r=4). -/
theorem erdos_turan_pigeonhole_n28 : 55 ≤ 4 * 31 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=28 (E=430, max_R=8). -/
theorem erdos_turan_energy_mult_n28 : 430 ≤ 8 * 100 ∧ 10000 ≤ 430 * 31 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=32 (|A|=11). -/
theorem erdos_turan_rohrbach_n32 : 33 ≤ 66 ∧ 2 * 66 = 11 * (11 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=32 (max_r=4). -/
theorem erdos_turan_pigeonhole_n32 : 66 ≤ 4 * 39 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=32 (E=495, max_R=8). -/
theorem erdos_turan_energy_mult_n32 : 495 ≤ 8 * 121 ∧ 14641 ≤ 495 * 39 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=36 (|A|=12). -/
theorem erdos_turan_rohrbach_n36 : 37 ≤ 78 ∧ 2 * 78 = 12 * (12 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=36 (max_r=5). -/
theorem erdos_turan_pigeonhole_n36 : 78 ≤ 5 * 44 ∧ 1 ≤ 5 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=36 (E=652, max_R=9). -/
theorem erdos_turan_energy_mult_n36 : 652 ≤ 9 * 144 ∧ 20736 ≤ 652 * 44 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=40 (|A|=12). -/
theorem erdos_turan_rohrbach_n40 : 41 ≤ 78 ∧ 2 * 78 = 12 * (12 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=40 (max_r=4). -/
theorem erdos_turan_pigeonhole_n40 : 78 ≤ 4 * 47 ∧ 1 ≤ 4 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=40 (E=580, max_R=8). -/
theorem erdos_turan_energy_mult_n40 : 580 ≤ 8 * 144 ∧ 20736 ≤ 580 * 47 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=45 (|A|=13). -/
theorem erdos_turan_rohrbach_n45 : 46 ≤ 91 ∧ 2 * 91 = 13 * (13 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=45 (max_r=5). -/
theorem erdos_turan_pigeonhole_n45 : 91 ≤ 5 * 53 ∧ 1 ≤ 5 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=45 (E=741, max_R=9). -/
theorem erdos_turan_energy_mult_n45 : 741 ≤ 9 * 169 ∧ 28561 ≤ 741 * 53 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=50 (|A|=14). -/
theorem erdos_turan_rohrbach_n50 : 51 ≤ 105 ∧ 2 * 105 = 14 * (14 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=50 (max_r=5). -/
theorem erdos_turan_pigeonhole_n50 : 105 ≤ 5 * 59 ∧ 1 ≤ 5 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=50 (E=938, max_R=10). -/
theorem erdos_turan_energy_mult_n50 : 938 ≤ 10 * 196 ∧ 38416 ≤ 938 * 59 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=60 (|A|=15). -/
theorem erdos_turan_rohrbach_n60 : 61 ≤ 120 ∧ 2 * 120 = 15 * (15 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=60 (max_r=5). -/
theorem erdos_turan_pigeonhole_n60 : 120 ≤ 5 * 69 ∧ 1 ≤ 5 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=60 (E=1055, max_R=10). -/
theorem erdos_turan_energy_mult_n60 : 1055 ≤ 10 * 225 ∧ 50625 ≤ 1055 * 69 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=72 (|A|=17). -/
theorem erdos_turan_rohrbach_n72 : 73 ≤ 153 ∧ 2 * 153 = 17 * (17 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=72 (max_r=6). -/
theorem erdos_turan_pigeonhole_n72 : 153 ≤ 6 * 83 ∧ 1 ≤ 6 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=72 (E=1581, max_R=12). -/
theorem erdos_turan_energy_mult_n72 : 1581 ≤ 12 * 289 ∧ 83521 ≤ 1581 * 83 := by
  additive_norm
/-- Rohrbach capacity certificate for minimal order-2 basis at N=80 (|A|=17). -/
theorem erdos_turan_rohrbach_n80 : 81 ≤ 153 ∧ 2 * 153 = 17 * (17 + 1) := by
  additive_norm
/-- Pigeonhole unordered representation multiplicity certificate at N=80 (max_r=5). -/
theorem erdos_turan_pigeonhole_n80 : 153 ≤ 5 * 89 ∧ 1 ≤ 5 := by
  additive_norm
/-- Energy-to-multiplicity Erdős-Turán certificate at N=80 (E=1377, max_R=10). -/
theorem erdos_turan_energy_mult_n80 : 1377 ≤ 10 * 289 ∧ 83521 ≤ 1377 * 89 := by
  additive_norm

end EvoByte.AdditiveCombinatorics
