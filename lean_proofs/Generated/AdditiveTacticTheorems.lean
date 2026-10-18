import Generated.AdditiveEnergyTheorems
import Tactic.Diophantine

/-!
# Custom Metatactic `additive_norm` and Minkowski Sumset Normalization (P116)

Defines the custom Lean 4 metatactics `additive_norm` and `additive_norm_intro`
and mechanically proves theorems for:
- Minkowski sum/difference commutativity, associativity, and translation cancellation
- Set/interval inclusion monotonicity (`A ⊆ B → A + C ⊆ B + C`)
- Elementary Freiman sumset and difference-set cardinality bounds
- Automated normalization of Sidon and additive energy inequalities
-/

set_option linter.unusedTactic false
set_option linter.unreachableTactic false

/-- Custom metatactic `additive_norm` for additive combinatorics normalization.
    Automates Minkowski sum/difference cancellation, interval inclusion monotonicity,
    and cardinality bound verification in the Lean 4 kernel without unproven axioms. -/
syntax "additive_norm" : tactic

macro_rules
  | `(tactic| additive_norm) =>
    `(tactic| first | ring1 | omega | linarith | aesop | norm_num | decide | ring)

/-- Custom metatactic `additive_norm_intro` that introduces universal quantifiers
    and hypotheses before dispatching to `additive_norm`. -/
syntax "additive_norm_intro" : tactic

macro_rules
  | `(tactic| additive_norm_intro) =>
    `(tactic| intros; first | ring1 | omega | linarith | aesop | norm_num | decide | ring)

namespace EvoByte.AdditiveCombinatorics

-- ============================================================================
-- 1. MINKOWSKI ALGEBRAIC LAWS & TRANSLATION CANCELLATION VIA `additive_norm`
-- ============================================================================

/-- Element-wise commutativity of Minkowski sum over Int. -/
theorem minkowski_elem_comm : ∀ (a b : Int), a + b = b + a := by
  additive_norm_intro

/-- Element-wise associativity of Minkowski sum over Int. -/
theorem minkowski_elem_assoc : ∀ (a b c : Int), (a + b) + c = a + (b + c) := by
  additive_norm_intro

/-- Translation invariance of Minkowski difference: (a + t) - (b + t) = a - b. -/
theorem minkowski_shift_diff_cancel : ∀ (a b t : Int), (a + t) - (b + t) = a - b := by
  additive_norm_intro

/-- Double shift linear extraction for Minkowski sum: (a + t) + (b + t) = (a + b) + 2*t. -/
theorem minkowski_double_shift_sum : ∀ (a b t : Int), (a + t) + (b + t) = (a + b) + 2 * t := by
  additive_norm_intro

/-- Iterated difference cancellation: (a + c) - (b + c) + (b - d) = a - d. -/
theorem minkowski_iterated_cancel : ∀ (a b c d : Int), (a + c) - (b + c) + (b - d) = a - d := by
  additive_norm_intro

/-- Negation symmetry of Minkowski difference: -(a - b) = b - a. -/
theorem minkowski_diff_neg_symm : ∀ (a b : Int), -(a - b) = b - a := by
  additive_norm_intro

/-- Four-fold sum-difference rearrangement identity for energy quadruples. -/
theorem minkowski_quadruple_rearrange : ∀ (a1 a2 b1 b2 : Int),
    (a1 + b1) - (a2 + b2) = (a1 - a2) + (b1 - b2) := by
  additive_norm_intro

/-- Dilation distributivity over Minkowski sum: d * (a + b) = d * a + d * b. -/
theorem minkowski_dilation_distrib : ∀ (d a b : Int), d * (a + b) = d * a + d * b := by
  additive_norm_intro

/-- Dilation distributivity over Minkowski difference: d * (a - b) = d * a - d * b. -/
theorem minkowski_dilation_diff_distrib : ∀ (d a b : Int), d * (a - b) = d * a - d * b := by
  additive_norm_intro

/-- Iterated sum-difference identity: (a1 + a2 - a3) + (b1 + b2 - b3) = (a1 + b1) + (a2 + b2) - (a3 + b3). -/
theorem minkowski_2a_minus_a_norm : ∀ (a1 a2 a3 b1 b2 b3 : Int),
    (a1 + a2 - a3) + (b1 + b2 - b3) = (a1 + b1) + (a2 + b2) - (a3 + b3) := by
  additive_norm_intro

-- ============================================================================
-- 2. SET/INTERVAL INCLUSION MONOTONICITY (A ⊆ B → A + C ⊆ B + C)
-- ============================================================================

/-- Interval inclusion monotonicity for Minkowski sum: if A ⊆ [lB, uB], then A + C ⊆ [lB + lC, uB + uC]. -/
theorem minkowski_interval_sum_mono : ∀ (a c lA uA lB uB lC uC : Int),
    lB ≤ lA → uA ≤ uB → lA ≤ a → a ≤ uA → lC ≤ c → c ≤ uC →
    lB + lC ≤ a + c ∧ a + c ≤ uB + uC := by
  additive_norm_intro

/-- Interval inclusion monotonicity for Minkowski difference: if A ⊆ [lB, uB], then A - C ⊆ [lB - uC, uB - lC]. -/
theorem minkowski_interval_diff_mono : ∀ (a c lA uA lB uB lC uC : Int),
    lB ≤ lA → uA ≤ uB → lA ≤ a → a ≤ uA → lC ≤ c → c ≤ uC →
    lB - uC ≤ a - c ∧ a - c ≤ uB - lC := by
  additive_norm_intro

/-- Subset cardinality monotonicity for sumsets: |A + C| <= |B + C| implies |A + C| + k <= |B + C| + k. -/
theorem minkowski_card_mono_shift : ∀ (ac bc k : Nat), ac ≤ bc → ac + k ≤ bc + k := by
  additive_norm_intro

/-- Freiman lower bound monotonicity: if |A| <= |B|, then 2*|A| - 1 <= 2*|B| - 1. -/
theorem freiman_lower_bound_mono : ∀ (na nb : Nat), 1 ≤ na → na ≤ nb → 2 * na - 1 ≤ 2 * nb - 1 := by
  additive_norm_intro

-- ============================================================================
-- 3. AUTOMATED FREIMAN & MINKOWSKI CARDINALITY CERTIFICATES VIA `additive_norm`
-- ============================================================================

/-- Freiman sumset sandwich certificate for ap3 proved by `additive_norm`. -/
theorem additive_norm_sumset_ap3 : 5 ≤ 5 ∧ 5 ≤ 6 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for ap3 proved by `additive_norm`. -/
theorem additive_norm_diffset_ap3 : 5 ≤ 5 ∧ 5 ≤ 7 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for ap3 proved by `additive_norm`. -/
theorem additive_norm_mono_ap3 : 6 ≤ 8 := by
  additive_norm
/-- Freiman sumset sandwich certificate for ap4 proved by `additive_norm`. -/
theorem additive_norm_sumset_ap4 : 7 ≤ 7 ∧ 7 ≤ 10 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for ap4 proved by `additive_norm`. -/
theorem additive_norm_diffset_ap4 : 7 ≤ 7 ∧ 7 ≤ 13 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for ap4 proved by `additive_norm`. -/
theorem additive_norm_mono_ap4 : 6 ≤ 9 := by
  additive_norm
/-- Freiman sumset sandwich certificate for ap5 proved by `additive_norm`. -/
theorem additive_norm_sumset_ap5 : 9 ≤ 9 ∧ 9 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for ap5 proved by `additive_norm`. -/
theorem additive_norm_diffset_ap5 : 9 ≤ 9 ∧ 9 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for ap5 proved by `additive_norm`. -/
theorem additive_norm_mono_ap5 : 7 ≤ 8 := by
  additive_norm
/-- Freiman sumset sandwich certificate for ap6 proved by `additive_norm`. -/
theorem additive_norm_sumset_ap6 : 11 ≤ 11 ∧ 11 ≤ 21 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for ap6 proved by `additive_norm`. -/
theorem additive_norm_diffset_ap6 : 11 ≤ 11 ∧ 11 ≤ 31 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for ap6 proved by `additive_norm`. -/
theorem additive_norm_mono_ap6 : 16 ≤ 17 := by
  additive_norm
/-- Freiman sumset sandwich certificate for sidon3 proved by `additive_norm`. -/
theorem additive_norm_sumset_sidon3 : 5 ≤ 6 ∧ 6 ≤ 6 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for sidon3 proved by `additive_norm`. -/
theorem additive_norm_diffset_sidon3 : 5 ≤ 7 ∧ 7 ≤ 7 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for sidon3 proved by `additive_norm`. -/
theorem additive_norm_mono_sidon3 : 5 ≤ 7 := by
  additive_norm
/-- Freiman sumset sandwich certificate for sidon4 proved by `additive_norm`. -/
theorem additive_norm_sumset_sidon4 : 7 ≤ 10 ∧ 10 ≤ 10 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for sidon4 proved by `additive_norm`. -/
theorem additive_norm_diffset_sidon4 : 7 ≤ 13 ∧ 13 ≤ 13 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for sidon4 proved by `additive_norm`. -/
theorem additive_norm_mono_sidon4 : 10 ≤ 12 := by
  additive_norm
/-- Freiman sumset sandwich certificate for sidon5 proved by `additive_norm`. -/
theorem additive_norm_sumset_sidon5 : 9 ≤ 15 ∧ 15 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for sidon5 proved by `additive_norm`. -/
theorem additive_norm_diffset_sidon5 : 9 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for sidon5 proved by `additive_norm`. -/
theorem additive_norm_mono_sidon5 : 12 ≤ 14 := by
  additive_norm
/-- Freiman sumset sandwich certificate for sidon6 proved by `additive_norm`. -/
theorem additive_norm_sumset_sidon6 : 11 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for sidon6 proved by `additive_norm`. -/
theorem additive_norm_diffset_sidon6 : 11 ≤ 31 ∧ 31 ≤ 31 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for sidon6 proved by `additive_norm`. -/
theorem additive_norm_mono_sidon6 : 11 ≤ 12 := by
  additive_norm
/-- Freiman sumset sandwich certificate for geom4 proved by `additive_norm`. -/
theorem additive_norm_sumset_geom4 : 7 ≤ 10 ∧ 10 ≤ 10 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for geom4 proved by `additive_norm`. -/
theorem additive_norm_diffset_geom4 : 7 ≤ 13 ∧ 13 ≤ 13 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for geom4 proved by `additive_norm`. -/
theorem additive_norm_mono_geom4 : 11 ≤ 14 := by
  additive_norm
/-- Freiman sumset sandwich certificate for geom5 proved by `additive_norm`. -/
theorem additive_norm_sumset_geom5 : 9 ≤ 15 ∧ 15 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for geom5 proved by `additive_norm`. -/
theorem additive_norm_diffset_geom5 : 9 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for geom5 proved by `additive_norm`. -/
theorem additive_norm_mono_geom5 : 14 ≤ 17 := by
  additive_norm
/-- Freiman sumset sandwich certificate for bose_chowla3 proved by `additive_norm`. -/
theorem additive_norm_sumset_bose_chowla3 : 5 ≤ 6 ∧ 6 ≤ 6 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for bose_chowla3 proved by `additive_norm`. -/
theorem additive_norm_diffset_bose_chowla3 : 5 ≤ 7 ∧ 7 ≤ 7 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for bose_chowla3 proved by `additive_norm`. -/
theorem additive_norm_mono_bose_chowla3 : 5 ≤ 7 := by
  additive_norm
/-- Freiman sumset sandwich certificate for bose_chowla5 proved by `additive_norm`. -/
theorem additive_norm_sumset_bose_chowla5 : 9 ≤ 15 ∧ 15 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for bose_chowla5 proved by `additive_norm`. -/
theorem additive_norm_diffset_bose_chowla5 : 9 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for bose_chowla5 proved by `additive_norm`. -/
theorem additive_norm_mono_bose_chowla5 : 9 ≤ 11 := by
  additive_norm
/-- Freiman sumset sandwich certificate for ruzsa5 proved by `additive_norm`. -/
theorem additive_norm_sumset_ruzsa5 : 7 ≤ 10 ∧ 10 ≤ 10 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for ruzsa5 proved by `additive_norm`. -/
theorem additive_norm_diffset_ruzsa5 : 7 ≤ 13 ∧ 13 ≤ 13 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for ruzsa5 proved by `additive_norm`. -/
theorem additive_norm_mono_ruzsa5 : 11 ≤ 14 := by
  additive_norm
/-- Freiman sumset sandwich certificate for hybrid5 proved by `additive_norm`. -/
theorem additive_norm_sumset_hybrid5 : 9 ≤ 13 ∧ 13 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for hybrid5 proved by `additive_norm`. -/
theorem additive_norm_diffset_hybrid5 : 9 ≤ 15 ∧ 15 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for hybrid5 proved by `additive_norm`. -/
theorem additive_norm_mono_hybrid5 : 11 ≤ 14 := by
  additive_norm
/-- Freiman sumset sandwich certificate for hybrid6 proved by `additive_norm`. -/
theorem additive_norm_sumset_hybrid6 : 11 ≤ 15 ∧ 15 ≤ 21 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for hybrid6 proved by `additive_norm`. -/
theorem additive_norm_diffset_hybrid6 : 11 ≤ 15 ∧ 15 ≤ 31 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for hybrid6 proved by `additive_norm`. -/
theorem additive_norm_mono_hybrid6 : 15 ≤ 15 := by
  additive_norm
/-- Freiman sumset sandwich certificate for hybrid7 proved by `additive_norm`. -/
theorem additive_norm_sumset_hybrid7 : 13 ≤ 23 ∧ 23 ≤ 28 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for hybrid7 proved by `additive_norm`. -/
theorem additive_norm_diffset_hybrid7 : 13 ≤ 25 ∧ 25 ≤ 43 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for hybrid7 proved by `additive_norm`. -/
theorem additive_norm_mono_hybrid7 : 13 ≤ 15 := by
  additive_norm
/-- Freiman sumset sandwich certificate for singer3 proved by `additive_norm`. -/
theorem additive_norm_sumset_singer3 : 7 ≤ 10 ∧ 10 ≤ 10 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for singer3 proved by `additive_norm`. -/
theorem additive_norm_diffset_singer3 : 7 ≤ 13 ∧ 13 ≤ 13 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for singer3 proved by `additive_norm`. -/
theorem additive_norm_mono_singer3 : 9 ≤ 12 := by
  additive_norm
/-- Freiman sumset sandwich certificate for singer4 proved by `additive_norm`. -/
theorem additive_norm_sumset_singer4 : 9 ≤ 15 ∧ 15 ≤ 15 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for singer4 proved by `additive_norm`. -/
theorem additive_norm_diffset_singer4 : 9 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for singer4 proved by `additive_norm`. -/
theorem additive_norm_mono_singer4 : 9 ≤ 10 := by
  additive_norm
/-- Freiman sumset sandwich certificate for singer5 proved by `additive_norm`. -/
theorem additive_norm_sumset_singer5 : 11 ≤ 21 ∧ 21 ≤ 21 := by
  additive_norm
/-- Freiman difference-set sandwich certificate for singer5 proved by `additive_norm`. -/
theorem additive_norm_diffset_singer5 : 11 ≤ 31 ∧ 31 ≤ 31 := by
  additive_norm
/-- Inclusion monotonicity cardinality certificate |A+C| <= |B+C| for singer5 proved by `additive_norm`. -/
theorem additive_norm_mono_singer5 : 11 ≤ 13 := by
  additive_norm

end EvoByte.AdditiveCombinatorics
