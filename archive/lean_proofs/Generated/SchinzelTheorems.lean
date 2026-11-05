/-
EvoByte Formal Proof Catalog: Generalized Schinzel Conjecture Theorems (a/n, P90).
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 0 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r0 : ∀ k : ℚ,
    4 * ((12 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (18 : ℚ) * k) * ((36 : ℚ) + (36 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((18 : ℚ) + (18 : ℚ) * k) * ((36 : ℚ) + (36 : ℚ) * k) + ((12 : ℚ) + (12 : ℚ) * k) * ((36 : ℚ) + (36 : ℚ) * k) + ((12 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 2 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r2 : ∀ k : ℚ,
    4 * ((1 : ℚ) + (8 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) * ((2 : ℚ) + (40 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((2 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (24 : ℚ) * k) * ((2 : ℚ) + (40 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((1 : ℚ) + (8 : ℚ) * k) * ((2 : ℚ) + (40 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((1 : ℚ) + (8 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 4 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r4 : ∀ k : ℚ,
    4 * ((2 : ℚ) + (12 : ℚ) * k) * ((3 : ℚ) + (18 : ℚ) * k) * ((6 : ℚ) + (36 : ℚ) * k) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((3 : ℚ) + (18 : ℚ) * k) * ((6 : ℚ) + (36 : ℚ) * k) + ((2 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (36 : ℚ) * k) + ((2 : ℚ) + (12 : ℚ) * k) * ((3 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 5 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r5 : ∀ k : ℚ,
    4 * ((2 : ℚ) + (8 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((5 : ℚ) + (24 : ℚ) * k) * (((5 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (8 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (8 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 8 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r8 : ∀ k : ℚ,
    4 * ((4 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (18 : ℚ) * k) * ((12 : ℚ) + (36 : ℚ) * k) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (18 : ℚ) * k) * ((12 : ℚ) + (36 : ℚ) * k) + ((4 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (36 : ℚ) * k) + ((4 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 11 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r11 : ∀ k : ℚ,
    4 * ((4 : ℚ) + (8 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (24 : ℚ) * k) * (((11 : ℚ) + (24 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (8 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (8 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 12 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r12 : ∀ k : ℚ,
    4 * ((6 : ℚ) + (12 : ℚ) * k) * ((9 : ℚ) + (18 : ℚ) * k) * ((18 : ℚ) + (36 : ℚ) * k) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((9 : ℚ) + (18 : ℚ) * k) * ((18 : ℚ) + (36 : ℚ) * k) + ((6 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (36 : ℚ) * k) + ((6 : ℚ) + (12 : ℚ) * k) * ((9 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 14 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r14 : ∀ k : ℚ,
    4 * ((5 : ℚ) + (8 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) * ((70 : ℚ) + (232 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((14 : ℚ) + (24 : ℚ) * k) * (((14 : ℚ) + (24 : ℚ) * k) * ((70 : ℚ) + (232 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((5 : ℚ) + (8 : ℚ) * k) * ((70 : ℚ) + (232 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((5 : ℚ) + (8 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 16 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r16 : ∀ k : ℚ,
    4 * ((8 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (18 : ℚ) * k) * ((24 : ℚ) + (36 : ℚ) * k) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (18 : ℚ) * k) * ((24 : ℚ) + (36 : ℚ) * k) + ((8 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (36 : ℚ) * k) + ((8 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 17 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r17 : ∀ k : ℚ,
    4 * ((6 : ℚ) + (8 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((17 : ℚ) + (24 : ℚ) * k) * (((17 : ℚ) + (24 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((6 : ℚ) + (8 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((6 : ℚ) + (8 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 20 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r20 : ∀ k : ℚ,
    4 * ((10 : ℚ) + (12 : ℚ) * k) * ((15 : ℚ) + (18 : ℚ) * k) * ((30 : ℚ) + (36 : ℚ) * k) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((15 : ℚ) + (18 : ℚ) * k) * ((30 : ℚ) + (36 : ℚ) * k) + ((10 : ℚ) + (12 : ℚ) * k) * ((30 : ℚ) + (36 : ℚ) * k) + ((10 : ℚ) + (12 : ℚ) * k) * ((15 : ℚ) + (18 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 4, congruence class n ≡ 23 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a4_m24_r23 : ∀ k : ℚ,
    4 * ((8 : ℚ) + (8 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((23 : ℚ) + (24 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((8 : ℚ) + (8 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((8 : ℚ) + (8 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 0 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r0 : ∀ k : ℚ,
    5 * ((7 : ℚ) + (6 : ℚ) * k) * ((42 : ℚ) + (78 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((24 : ℚ) + (24 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((42 : ℚ) + (78 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((24 : ℚ) + (24 : ℚ) * k) + ((7 : ℚ) + (6 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((7 : ℚ) + (6 : ℚ) * k) * ((42 : ℚ) + (78 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 2 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r2 : ∀ k : ℚ,
    5 * ((1 : ℚ) + (6 : ℚ) * k) * ((1 : ℚ) + (18 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((2 : ℚ) + (24 : ℚ) * k) =
    ((2 : ℚ) + (24 : ℚ) * k) * (((1 : ℚ) + (18 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((2 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (6 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (6 : ℚ) * k) * ((1 : ℚ) + (18 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 3 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r3 : ∀ k : ℚ,
    5 * ((1 : ℚ) + (6 : ℚ) * k) * ((3 : ℚ) + (24 : ℚ) * k) * ((3 : ℚ) + (42 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((3 : ℚ) + (24 : ℚ) * k) * (((3 : ℚ) + (24 : ℚ) * k) * ((3 : ℚ) + (42 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((1 : ℚ) + (6 : ℚ) * k) * ((3 : ℚ) + (42 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((1 : ℚ) + (6 : ℚ) * k) * ((3 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 4 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r4 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (6 : ℚ) * k) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((4 : ℚ) + (24 : ℚ) * k) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((4 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 6 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r6 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((6 : ℚ) + (24 : ℚ) * k) =
    ((6 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 7 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r7 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (6 : ℚ) * k) * ((7 : ℚ) + (24 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((7 : ℚ) + (24 : ℚ) * k) * (((7 : ℚ) + (24 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((2 : ℚ) + (6 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((2 : ℚ) + (6 : ℚ) * k) * ((7 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 8 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r8 : ∀ k : ℚ,
    5 * ((3 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (30 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((8 : ℚ) + (24 : ℚ) * k) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (30 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((8 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (6 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (30 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 10 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r10 : ∀ k : ℚ,
    5 * ((3 : ℚ) + (6 : ℚ) * k) * ((15 : ℚ) + (66 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((10 : ℚ) + (24 : ℚ) * k) =
    ((10 : ℚ) + (24 : ℚ) * k) * (((15 : ℚ) + (66 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((10 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (6 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (6 : ℚ) * k) * ((15 : ℚ) + (66 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 11 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r11 : ∀ k : ℚ,
    5 * ((3 : ℚ) + (6 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k) * ((33 : ℚ) + (138 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (24 : ℚ) * k) * (((11 : ℚ) + (24 : ℚ) * k) * ((33 : ℚ) + (138 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((3 : ℚ) + (6 : ℚ) * k) * ((33 : ℚ) + (138 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((3 : ℚ) + (6 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 12 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r12 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (6 : ℚ) * k) * ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((12 : ℚ) + (24 : ℚ) * k) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((12 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 14 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r14 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (6 : ℚ) * k) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((14 : ℚ) + (24 : ℚ) * k) =
    ((14 : ℚ) + (24 : ℚ) * k) * (((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((14 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 15 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r15 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (6 : ℚ) * k) * ((15 : ℚ) + (24 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((15 : ℚ) + (24 : ℚ) * k) * (((15 : ℚ) + (24 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((4 : ℚ) + (6 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((4 : ℚ) + (6 : ℚ) * k) * ((15 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 16 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r16 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (6 : ℚ) * k) * ((20 : ℚ) + (54 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((16 : ℚ) + (24 : ℚ) * k) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (54 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((16 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (6 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (6 : ℚ) * k) * ((20 : ℚ) + (54 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 18 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r18 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (6 : ℚ) * k) * ((45 : ℚ) + (114 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((18 : ℚ) + (24 : ℚ) * k) =
    ((18 : ℚ) + (24 : ℚ) * k) * (((45 : ℚ) + (114 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((18 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (6 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (6 : ℚ) * k) * ((45 : ℚ) + (114 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 19 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r19 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (6 : ℚ) * k) * ((19 : ℚ) + (24 : ℚ) * k) * ((95 : ℚ) + (234 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((19 : ℚ) + (24 : ℚ) * k) * (((19 : ℚ) + (24 : ℚ) * k) * ((95 : ℚ) + (234 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((5 : ℚ) + (6 : ℚ) * k) * ((95 : ℚ) + (234 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((5 : ℚ) + (6 : ℚ) * k) * ((19 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 20 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r20 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (6 : ℚ) * k) * ((30 : ℚ) + (66 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((20 : ℚ) + (24 : ℚ) * k) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((30 : ℚ) + (66 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((20 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((30 : ℚ) + (66 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 21 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r21 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (5 : ℚ) * k) * ((35 : ℚ) + (75 : ℚ) * k + (40 : ℚ) * k ^ 2) * ((105 : ℚ) + (120 : ℚ) * k) =
    ((21 : ℚ) + (24 : ℚ) * k) * (((35 : ℚ) + (75 : ℚ) * k + (40 : ℚ) * k ^ 2) * ((105 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (5 : ℚ) * k) * ((105 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (5 : ℚ) * k) * ((35 : ℚ) + (75 : ℚ) * k + (40 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 22 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r22 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (6 : ℚ) * k) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((22 : ℚ) + (24 : ℚ) * k) =
    ((22 : ℚ) + (24 : ℚ) * k) * (((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((22 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 5, congruence class n ≡ 23 [mod 24].
    Guarantees 5/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a5_m24_r23 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (6 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((23 : ℚ) + (24 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((6 : ℚ) + (6 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((6 : ℚ) + (6 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 0 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r0 : ∀ k : ℚ,
    6 * ((8 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((8 : ℚ) + (8 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((8 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (12 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 2 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r2 : ∀ k : ℚ,
    6 * ((1 : ℚ) + (4 : ℚ) * k) * ((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((2 : ℚ) + (24 : ℚ) * k) * (((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((1 : ℚ) + (16 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 3 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r3 : ∀ k : ℚ,
    6 * ((1 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2) * ((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2) =
    ((3 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2) * ((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k + (64 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 4 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r4 : ∀ k : ℚ,
    6 * ((1 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (40 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 5 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r5 : ∀ k : ℚ,
    6 * ((1 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((5 : ℚ) + (24 : ℚ) * k) * (((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 6 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r6 : ∀ k : ℚ,
    6 * ((2 : ℚ) + (8 : ℚ) * k) * ((3 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) =
    ((6 : ℚ) + (24 : ℚ) * k) * (((3 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (8 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (8 : ℚ) * k) * ((3 : ℚ) + (12 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 8 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r8 : ∀ k : ℚ,
    6 * ((2 : ℚ) + (4 : ℚ) * k) * ((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((8 : ℚ) + (40 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 9 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r9 : ∀ k : ℚ,
    6 * ((2 : ℚ) + (4 : ℚ) * k) * ((18 : ℚ) + (84 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((9 : ℚ) + (42 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((9 : ℚ) + (24 : ℚ) * k) * (((18 : ℚ) + (84 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((9 : ℚ) + (42 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((9 : ℚ) + (42 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((18 : ℚ) + (84 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 10 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r10 : ∀ k : ℚ,
    6 * ((2 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((10 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (88 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 11 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r11 : ∀ k : ℚ,
    6 * ((2 : ℚ) + (4 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (24 : ℚ) * k) * (((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 12 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r12 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (8 : ℚ) * k) * ((6 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (8 : ℚ) * k) * ((6 : ℚ) + (12 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 14 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r14 : ∀ k : ℚ,
    6 * ((3 : ℚ) + (4 : ℚ) * k) * ((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((14 : ℚ) + (24 : ℚ) * k) * (((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((21 : ℚ) + (64 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 15 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r15 : ∀ k : ℚ,
    6 * ((3 : ℚ) + (4 : ℚ) * k) * ((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2) * ((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2) =
    ((15 : ℚ) + (24 : ℚ) * k) * (((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2) * ((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((30 : ℚ) + (88 : ℚ) * k + (64 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 16 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r16 : ∀ k : ℚ,
    6 * ((3 : ℚ) + (4 : ℚ) * k) * ((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((48 : ℚ) + (136 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 17 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r17 : ∀ k : ℚ,
    6 * ((3 : ℚ) + (4 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((17 : ℚ) + (24 : ℚ) * k) * (((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 18 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r18 : ∀ k : ℚ,
    6 * ((6 : ℚ) + (8 : ℚ) * k) * ((9 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) =
    ((18 : ℚ) + (24 : ℚ) * k) * (((9 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (8 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (8 : ℚ) * k) * ((9 : ℚ) + (12 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 19 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r19 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (4 : ℚ) * k) * ((76 : ℚ) + (172 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((19 : ℚ) + (43 : ℚ) * k + (24 : ℚ) * k ^ 2) =
    ((19 : ℚ) + (24 : ℚ) * k) * (((76 : ℚ) + (172 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((19 : ℚ) + (43 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((19 : ℚ) + (43 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((76 : ℚ) + (172 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 20 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r20 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (4 : ℚ) * k) * ((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((40 : ℚ) + (88 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 21 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r21 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (4 : ℚ) * k) * ((84 : ℚ) + (180 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((21 : ℚ) + (24 : ℚ) * k) * (((84 : ℚ) + (180 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((84 : ℚ) + (180 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 22 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r22 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (4 : ℚ) * k) * ((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((22 : ℚ) + (24 : ℚ) * k) * (((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2) * ((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((88 : ℚ) + (184 : ℚ) * k + (96 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 6, congruence class n ≡ 23 [mod 24].
    Guarantees 6/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a6_m24_r23 : ∀ k : ℚ,
    6 * ((4 : ℚ) + (4 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 0 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r0 : ∀ k : ℚ,
    7 * ((5 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (36 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((24 : ℚ) + (24 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (36 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((24 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (4 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (36 : ℚ) * k + (16 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 3 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r3 : ∀ k : ℚ,
    7 * ((1 : ℚ) + (4 : ℚ) * k) * ((1 : ℚ) + (12 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((3 : ℚ) + (24 : ℚ) * k) =
    ((3 : ℚ) + (24 : ℚ) * k) * (((1 : ℚ) + (12 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((3 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (4 : ℚ) * k) * ((3 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (4 : ℚ) * k) * ((1 : ℚ) + (12 : ℚ) * k + (32 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 4 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r4 : ∀ k : ℚ,
    7 * ((1 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (20 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((4 : ℚ) + (24 : ℚ) * k) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (20 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((4 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (20 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 5 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r5 : ∀ k : ℚ,
    7 * ((1 : ℚ) + (4 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k) * ((5 : ℚ) + (44 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((5 : ℚ) + (24 : ℚ) * k) * (((5 : ℚ) + (24 : ℚ) * k) * ((5 : ℚ) + (44 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((5 : ℚ) + (44 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((1 : ℚ) + (4 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 6 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r6 : ∀ k : ℚ,
    7 * ((2 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (12 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((6 : ℚ) + (24 : ℚ) * k) =
    ((6 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (12 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((2 : ℚ) + (12 : ℚ) * k + (16 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 8 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r8 : ∀ k : ℚ,
    7 * ((2 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (20 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((8 : ℚ) + (24 : ℚ) * k) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((4 : ℚ) + (20 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((8 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((4 : ℚ) + (20 : ℚ) * k + (24 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 9 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r9 : ∀ k : ℚ,
    7 * ((2 : ℚ) + (4 : ℚ) * k) * ((6 : ℚ) + (28 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((9 : ℚ) + (24 : ℚ) * k) =
    ((9 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (28 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((9 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((9 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((6 : ℚ) + (28 : ℚ) * k + (32 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 10 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r10 : ∀ k : ℚ,
    7 * ((2 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((10 : ℚ) + (24 : ℚ) * k) =
    ((10 : ℚ) + (24 : ℚ) * k) * (((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((10 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 11 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r11 : ∀ k : ℚ,
    7 * ((2 : ℚ) + (4 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k) * ((22 : ℚ) + (92 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (24 : ℚ) * k) * (((11 : ℚ) + (24 : ℚ) * k) * ((22 : ℚ) + (92 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((22 : ℚ) + (92 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((2 : ℚ) + (4 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 12 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r12 : ∀ k : ℚ,
    7 * ((3 : ℚ) + (4 : ℚ) * k) * ((6 : ℚ) + (20 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((12 : ℚ) + (24 : ℚ) * k) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (20 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((12 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((6 : ℚ) + (20 : ℚ) * k + (16 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 15 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r15 : ∀ k : ℚ,
    7 * ((3 : ℚ) + (4 : ℚ) * k) * ((15 : ℚ) + (44 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((15 : ℚ) + (24 : ℚ) * k) =
    ((15 : ℚ) + (24 : ℚ) * k) * (((15 : ℚ) + (44 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((15 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((15 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((15 : ℚ) + (44 : ℚ) * k + (32 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 16 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r16 : ∀ k : ℚ,
    7 * ((3 : ℚ) + (4 : ℚ) * k) * ((24 : ℚ) + (68 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((16 : ℚ) + (24 : ℚ) * k) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((24 : ℚ) + (68 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((16 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (4 : ℚ) * k) * ((24 : ℚ) + (68 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 17 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r17 : ∀ k : ℚ,
    7 * ((3 : ℚ) + (4 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k) * ((51 : ℚ) + (140 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((17 : ℚ) + (24 : ℚ) * k) * (((17 : ℚ) + (24 : ℚ) * k) * ((51 : ℚ) + (140 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((51 : ℚ) + (140 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((3 : ℚ) + (4 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 18 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r18 : ∀ k : ℚ,
    7 * ((4 : ℚ) + (4 : ℚ) * k) * ((12 : ℚ) + (28 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((18 : ℚ) + (24 : ℚ) * k) =
    ((18 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (28 : ℚ) * k + (16 : ℚ) * k ^ 2) * ((18 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((12 : ℚ) + (28 : ℚ) * k + (16 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 20 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r20 : ∀ k : ℚ,
    7 * ((4 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((20 : ℚ) + (24 : ℚ) * k) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((20 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 21 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r21 : ∀ k : ℚ,
    7 * ((4 : ℚ) + (4 : ℚ) * k) * ((28 : ℚ) + (60 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((21 : ℚ) + (24 : ℚ) * k) =
    ((21 : ℚ) + (24 : ℚ) * k) * (((28 : ℚ) + (60 : ℚ) * k + (32 : ℚ) * k ^ 2) * ((21 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((21 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((28 : ℚ) + (60 : ℚ) * k + (32 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 22 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r22 : ∀ k : ℚ,
    7 * ((4 : ℚ) + (4 : ℚ) * k) * ((44 : ℚ) + (92 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((22 : ℚ) + (24 : ℚ) * k) =
    ((22 : ℚ) + (24 : ℚ) * k) * (((44 : ℚ) + (92 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((22 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (4 : ℚ) * k) * ((44 : ℚ) + (92 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 7, congruence class n ≡ 23 [mod 24].
    Guarantees 7/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a7_m24_r23 : ∀ k : ℚ,
    7 * ((4 : ℚ) + (4 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k) * ((92 : ℚ) + (188 : ℚ) * k + (96 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((23 : ℚ) + (24 : ℚ) * k) * ((92 : ℚ) + (188 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((92 : ℚ) + (188 : ℚ) * k + (96 : ℚ) * k ^ 2) + ((4 : ℚ) + (4 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 0 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r0 : ∀ k : ℚ,
    8 * ((6 : ℚ) + (6 : ℚ) * k) * ((9 : ℚ) + (9 : ℚ) * k) * ((18 : ℚ) + (18 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((9 : ℚ) + (9 : ℚ) * k) * ((18 : ℚ) + (18 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((18 : ℚ) + (18 : ℚ) * k) + ((6 : ℚ) + (6 : ℚ) * k) * ((9 : ℚ) + (9 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 4 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r4 : ∀ k : ℚ,
    8 * ((1 : ℚ) + (3 : ℚ) * k) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((2 : ℚ) + (18 : ℚ) * k + (36 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 6 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r6 : ∀ k : ℚ,
    8 * ((1 : ℚ) + (3 : ℚ) * k) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) =
    ((6 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((6 : ℚ) + (42 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 7 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r7 : ∀ k : ℚ,
    8 * ((1 : ℚ) + (3 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((7 : ℚ) + (24 : ℚ) * k) * (((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((1 : ℚ) + (3 : ℚ) * k) * ((14 : ℚ) + (90 : ℚ) * k + (144 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 8 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r8 : ∀ k : ℚ,
    8 * ((2 : ℚ) + (6 : ℚ) * k) * ((3 : ℚ) + (9 : ℚ) * k) * ((6 : ℚ) + (18 : ℚ) * k) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((3 : ℚ) + (9 : ℚ) * k) * ((6 : ℚ) + (18 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (18 : ℚ) * k) + ((2 : ℚ) + (6 : ℚ) * k) * ((3 : ℚ) + (9 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 10 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r10 : ∀ k : ℚ,
    8 * ((2 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((5 : ℚ) + (12 : ℚ) * k) =
    ((10 : ℚ) + (24 : ℚ) * k) * (((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((5 : ℚ) + (12 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((5 : ℚ) + (12 : ℚ) * k) + ((2 : ℚ) + (4 : ℚ) * k) * ((10 : ℚ) + (44 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 12 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r12 : ∀ k : ℚ,
    8 * ((2 : ℚ) + (3 : ℚ) * k) * ((24 : ℚ) + (84 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((8 : ℚ) + (28 : ℚ) * k + (24 : ℚ) * k ^ 2) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((24 : ℚ) + (84 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((8 : ℚ) + (28 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((8 : ℚ) + (28 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((24 : ℚ) + (84 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 14 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r14 : ∀ k : ℚ,
    8 * ((2 : ℚ) + (3 : ℚ) * k) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) =
    ((14 : ℚ) + (24 : ℚ) * k) * (((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((28 : ℚ) + (90 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 15 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r15 : ∀ k : ℚ,
    8 * ((2 : ℚ) + (3 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((15 : ℚ) + (24 : ℚ) * k) * (((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((2 : ℚ) + (3 : ℚ) * k) * ((60 : ℚ) + (186 : ℚ) * k + (144 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 16 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r16 : ∀ k : ℚ,
    8 * ((4 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (9 : ℚ) * k) * ((12 : ℚ) + (18 : ℚ) * k) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (9 : ℚ) * k) * ((12 : ℚ) + (18 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((12 : ℚ) + (18 : ℚ) * k) + ((4 : ℚ) + (6 : ℚ) * k) * ((6 : ℚ) + (9 : ℚ) * k)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 18 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r18 : ∀ k : ℚ,
    8 * ((3 : ℚ) + (3 : ℚ) * k) * ((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2) =
    ((18 : ℚ) + (24 : ℚ) * k) * (((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2) * ((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((18 : ℚ) + (42 : ℚ) * k + (24 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 20 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r20 : ∀ k : ℚ,
    8 * ((3 : ℚ) + (3 : ℚ) * k) * ((60 : ℚ) + (132 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((60 : ℚ) + (132 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((20 : ℚ) + (44 : ℚ) * k + (24 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((60 : ℚ) + (132 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 21 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r21 : ∀ k : ℚ,
    8 * ((3 : ℚ) + (3 : ℚ) * k) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) =
    ((21 : ℚ) + (24 : ℚ) * k) * (((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((42 : ℚ) + (90 : ℚ) * k + (48 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 22 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r22 : ∀ k : ℚ,
    8 * ((3 : ℚ) + (3 : ℚ) * k) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) =
    ((22 : ℚ) + (24 : ℚ) * k) * (((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((66 : ℚ) + (138 : ℚ) * k + (72 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel polynomial identity for numerator a = 8, congruence class n ≡ 23 [mod 24].
    Guarantees 8/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k (P90). -/
theorem schinzel_ident_a8_m24_r23 : ∀ k : ℚ,
    8 * ((3 : ℚ) + (3 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2) + ((3 : ℚ) + (3 : ℚ) * k) * ((138 : ℚ) + (282 : ℚ) * k + (144 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Schinzel instance certificate for numerator a = 4, denominator n = 11.
    Certified exact rational solution (4/11 = 1/3 + 1/34 + 1/1122) via norm_num (P90). -/
theorem schinzel_cert_a4_n11 : (4 : ℚ) / 11 = (1 : ℚ) / 3 + (1 : ℚ) / 34 + (1 : ℚ) / 1122 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 13.
    Certified exact rational solution (4/13 = 1/4 + 1/18 + 1/468) via norm_num (P90). -/
theorem schinzel_cert_a4_n13 : (4 : ℚ) / 13 = (1 : ℚ) / 4 + (1 : ℚ) / 18 + (1 : ℚ) / 468 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 17.
    Certified exact rational solution (4/17 = 1/5 + 1/30 + 1/510) via norm_num (P90). -/
theorem schinzel_cert_a4_n17 : (4 : ℚ) / 17 = (1 : ℚ) / 5 + (1 : ℚ) / 30 + (1 : ℚ) / 510 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 19.
    Certified exact rational solution (4/19 = 1/5 + 1/96 + 1/9120) via norm_num (P90). -/
theorem schinzel_cert_a4_n19 : (4 : ℚ) / 19 = (1 : ℚ) / 5 + (1 : ℚ) / 96 + (1 : ℚ) / 9120 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 23.
    Certified exact rational solution (4/23 = 1/6 + 1/139 + 1/19182) via norm_num (P90). -/
theorem schinzel_cert_a4_n23 : (4 : ℚ) / 23 = (1 : ℚ) / 6 + (1 : ℚ) / 139 + (1 : ℚ) / 19182 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 29.
    Certified exact rational solution (4/29 = 1/8 + 1/78 + 1/9048) via norm_num (P90). -/
theorem schinzel_cert_a4_n29 : (4 : ℚ) / 29 = (1 : ℚ) / 8 + (1 : ℚ) / 78 + (1 : ℚ) / 9048 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 31.
    Certified exact rational solution (4/31 = 1/8 + 1/249 + 1/61752) via norm_num (P90). -/
theorem schinzel_cert_a4_n31 : (4 : ℚ) / 31 = (1 : ℚ) / 8 + (1 : ℚ) / 249 + (1 : ℚ) / 61752 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 37.
    Certified exact rational solution (4/37 = 1/10 + 1/125 + 1/9250) via norm_num (P90). -/
theorem schinzel_cert_a4_n37 : (4 : ℚ) / 37 = (1 : ℚ) / 10 + (1 : ℚ) / 125 + (1 : ℚ) / 9250 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 41.
    Certified exact rational solution (4/41 = 1/11 + 1/154 + 1/6314) via norm_num (P90). -/
theorem schinzel_cert_a4_n41 : (4 : ℚ) / 41 = (1 : ℚ) / 11 + (1 : ℚ) / 154 + (1 : ℚ) / 6314 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 4, denominator n = 43.
    Certified exact rational solution (4/43 = 1/11 + 1/474 + 1/224202) via norm_num (P90). -/
theorem schinzel_cert_a4_n43 : (4 : ℚ) / 43 = (1 : ℚ) / 11 + (1 : ℚ) / 474 + (1 : ℚ) / 224202 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 11.
    Certified exact rational solution (5/11 = 1/3 + 1/9 + 1/99) via norm_num (P90). -/
theorem schinzel_cert_a5_n11 : (5 : ℚ) / 11 = (1 : ℚ) / 3 + (1 : ℚ) / 9 + (1 : ℚ) / 99 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 13.
    Certified exact rational solution (5/13 = 1/3 + 1/20 + 1/780) via norm_num (P90). -/
theorem schinzel_cert_a5_n13 : (5 : ℚ) / 13 = (1 : ℚ) / 3 + (1 : ℚ) / 20 + (1 : ℚ) / 780 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 17.
    Certified exact rational solution (5/17 = 1/4 + 1/23 + 1/1564) via norm_num (P90). -/
theorem schinzel_cert_a5_n17 : (5 : ℚ) / 17 = (1 : ℚ) / 4 + (1 : ℚ) / 23 + (1 : ℚ) / 1564 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 19.
    Certified exact rational solution (5/19 = 1/4 + 1/77 + 1/5852) via norm_num (P90). -/
theorem schinzel_cert_a5_n19 : (5 : ℚ) / 19 = (1 : ℚ) / 4 + (1 : ℚ) / 77 + (1 : ℚ) / 5852 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 23.
    Certified exact rational solution (5/23 = 1/5 + 1/58 + 1/6670) via norm_num (P90). -/
theorem schinzel_cert_a5_n23 : (5 : ℚ) / 23 = (1 : ℚ) / 5 + (1 : ℚ) / 58 + (1 : ℚ) / 6670 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 29.
    Certified exact rational solution (5/29 = 1/6 + 1/175 + 1/30450) via norm_num (P90). -/
theorem schinzel_cert_a5_n29 : (5 : ℚ) / 29 = (1 : ℚ) / 6 + (1 : ℚ) / 175 + (1 : ℚ) / 30450 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 31.
    Certified exact rational solution (5/31 = 1/7 + 1/56 + 1/1736) via norm_num (P90). -/
theorem schinzel_cert_a5_n31 : (5 : ℚ) / 31 = (1 : ℚ) / 7 + (1 : ℚ) / 56 + (1 : ℚ) / 1736 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 37.
    Certified exact rational solution (5/37 = 1/8 + 1/99 + 1/29304) via norm_num (P90). -/
theorem schinzel_cert_a5_n37 : (5 : ℚ) / 37 = (1 : ℚ) / 8 + (1 : ℚ) / 99 + (1 : ℚ) / 29304 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 41.
    Certified exact rational solution (5/41 = 1/9 + 1/93 + 1/11439) via norm_num (P90). -/
theorem schinzel_cert_a5_n41 : (5 : ℚ) / 41 = (1 : ℚ) / 9 + (1 : ℚ) / 93 + (1 : ℚ) / 11439 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 5, denominator n = 43.
    Certified exact rational solution (5/43 = 1/9 + 1/194 + 1/75078) via norm_num (P90). -/
theorem schinzel_cert_a5_n43 : (5 : ℚ) / 43 = (1 : ℚ) / 9 + (1 : ℚ) / 194 + (1 : ℚ) / 75078 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 11.
    Certified exact rational solution (6/11 = 1/2 + 1/23 + 1/506) via norm_num (P90). -/
theorem schinzel_cert_a6_n11 : (6 : ℚ) / 11 = (1 : ℚ) / 2 + (1 : ℚ) / 23 + (1 : ℚ) / 506 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 13.
    Certified exact rational solution (6/13 = 1/3 + 1/8 + 1/312) via norm_num (P90). -/
theorem schinzel_cert_a6_n13 : (6 : ℚ) / 13 = (1 : ℚ) / 3 + (1 : ℚ) / 8 + (1 : ℚ) / 312 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 17.
    Certified exact rational solution (6/17 = 1/3 + 1/52 + 1/2652) via norm_num (P90). -/
theorem schinzel_cert_a6_n17 : (6 : ℚ) / 17 = (1 : ℚ) / 3 + (1 : ℚ) / 52 + (1 : ℚ) / 2652 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 19.
    Certified exact rational solution (6/19 = 1/4 + 1/16 + 1/304) via norm_num (P90). -/
theorem schinzel_cert_a6_n19 : (6 : ℚ) / 19 = (1 : ℚ) / 4 + (1 : ℚ) / 16 + (1 : ℚ) / 304 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 23.
    Certified exact rational solution (6/23 = 1/4 + 1/93 + 1/8556) via norm_num (P90). -/
theorem schinzel_cert_a6_n23 : (6 : ℚ) / 23 = (1 : ℚ) / 4 + (1 : ℚ) / 93 + (1 : ℚ) / 8556 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 29.
    Certified exact rational solution (6/29 = 1/5 + 1/146 + 1/21170) via norm_num (P90). -/
theorem schinzel_cert_a6_n29 : (6 : ℚ) / 29 = (1 : ℚ) / 5 + (1 : ℚ) / 146 + (1 : ℚ) / 21170 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 31.
    Certified exact rational solution (6/31 = 1/6 + 1/39 + 1/806) via norm_num (P90). -/
theorem schinzel_cert_a6_n31 : (6 : ℚ) / 31 = (1 : ℚ) / 6 + (1 : ℚ) / 39 + (1 : ℚ) / 806 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 37.
    Certified exact rational solution (6/37 = 1/7 + 1/52 + 1/13468) via norm_num (P90). -/
theorem schinzel_cert_a6_n37 : (6 : ℚ) / 37 = (1 : ℚ) / 7 + (1 : ℚ) / 52 + (1 : ℚ) / 13468 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 41.
    Certified exact rational solution (6/41 = 1/7 + 1/288 + 1/82656) via norm_num (P90). -/
theorem schinzel_cert_a6_n41 : (6 : ℚ) / 41 = (1 : ℚ) / 7 + (1 : ℚ) / 288 + (1 : ℚ) / 82656 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 6, denominator n = 43.
    Certified exact rational solution (6/43 = 1/8 + 1/69 + 1/23736) via norm_num (P90). -/
theorem schinzel_cert_a6_n43 : (6 : ℚ) / 43 = (1 : ℚ) / 8 + (1 : ℚ) / 69 + (1 : ℚ) / 23736 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 11.
    Certified exact rational solution (7/11 = 1/2 + 1/8 + 1/88) via norm_num (P90). -/
theorem schinzel_cert_a7_n11 : (7 : ℚ) / 11 = (1 : ℚ) / 2 + (1 : ℚ) / 8 + (1 : ℚ) / 88 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 13.
    Certified exact rational solution (7/13 = 1/2 + 1/27 + 1/702) via norm_num (P90). -/
theorem schinzel_cert_a7_n13 : (7 : ℚ) / 13 = (1 : ℚ) / 2 + (1 : ℚ) / 27 + (1 : ℚ) / 702 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 17.
    Certified exact rational solution (7/17 = 1/3 + 1/13 + 1/663) via norm_num (P90). -/
theorem schinzel_cert_a7_n17 : (7 : ℚ) / 17 = (1 : ℚ) / 3 + (1 : ℚ) / 13 + (1 : ℚ) / 663 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 19.
    Certified exact rational solution (7/19 = 1/3 + 1/29 + 1/1653) via norm_num (P90). -/
theorem schinzel_cert_a7_n19 : (7 : ℚ) / 19 = (1 : ℚ) / 3 + (1 : ℚ) / 29 + (1 : ℚ) / 1653 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 23.
    Certified exact rational solution (7/23 = 1/4 + 1/20 + 1/230) via norm_num (P90). -/
theorem schinzel_cert_a7_n23 : (7 : ℚ) / 23 = (1 : ℚ) / 4 + (1 : ℚ) / 20 + (1 : ℚ) / 230 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 29.
    Certified exact rational solution (7/29 = 1/5 + 1/25 + 1/725) via norm_num (P90). -/
theorem schinzel_cert_a7_n29 : (7 : ℚ) / 29 = (1 : ℚ) / 5 + (1 : ℚ) / 25 + (1 : ℚ) / 725 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 31.
    Certified exact rational solution (7/31 = 1/5 + 1/39 + 1/6045) via norm_num (P90). -/
theorem schinzel_cert_a7_n31 : (7 : ℚ) / 31 = (1 : ℚ) / 5 + (1 : ℚ) / 39 + (1 : ℚ) / 6045 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 37.
    Certified exact rational solution (7/37 = 1/6 + 1/45 + 1/3330) via norm_num (P90). -/
theorem schinzel_cert_a7_n37 : (7 : ℚ) / 37 = (1 : ℚ) / 6 + (1 : ℚ) / 45 + (1 : ℚ) / 3330 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 41.
    Certified exact rational solution (7/41 = 1/6 + 1/247 + 1/60762) via norm_num (P90). -/
theorem schinzel_cert_a7_n41 : (7 : ℚ) / 41 = (1 : ℚ) / 6 + (1 : ℚ) / 247 + (1 : ℚ) / 60762 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 7, denominator n = 43.
    Certified exact rational solution (7/43 = 1/10 + 1/16 + 1/3440) via norm_num (P90). -/
theorem schinzel_cert_a7_n43 : (7 : ℚ) / 43 = (1 : ℚ) / 10 + (1 : ℚ) / 16 + (1 : ℚ) / 3440 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 13.
    Certified exact rational solution (8/13 = 1/2 + 1/9 + 1/234) via norm_num (P90). -/
theorem schinzel_cert_a8_n13 : (8 : ℚ) / 13 = (1 : ℚ) / 2 + (1 : ℚ) / 9 + (1 : ℚ) / 234 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 19.
    Certified exact rational solution (8/19 = 1/3 + 1/12 + 1/228) via norm_num (P90). -/
theorem schinzel_cert_a8_n19 : (8 : ℚ) / 19 = (1 : ℚ) / 3 + (1 : ℚ) / 12 + (1 : ℚ) / 228 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 23.
    Certified exact rational solution (8/23 = 1/3 + 1/70 + 1/4830) via norm_num (P90). -/
theorem schinzel_cert_a8_n23 : (8 : ℚ) / 23 = (1 : ℚ) / 3 + (1 : ℚ) / 70 + (1 : ℚ) / 4830 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 29.
    Certified exact rational solution (8/29 = 1/4 + 1/39 + 1/4524) via norm_num (P90). -/
theorem schinzel_cert_a8_n29 : (8 : ℚ) / 29 = (1 : ℚ) / 4 + (1 : ℚ) / 39 + (1 : ℚ) / 4524 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 31.
    Certified exact rational solution (8/31 = 1/4 + 1/125 + 1/15500) via norm_num (P90). -/
theorem schinzel_cert_a8_n31 : (8 : ℚ) / 31 = (1 : ℚ) / 4 + (1 : ℚ) / 125 + (1 : ℚ) / 15500 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 37.
    Certified exact rational solution (8/37 = 1/5 + 1/62 + 1/11470) via norm_num (P90). -/
theorem schinzel_cert_a8_n37 : (8 : ℚ) / 37 = (1 : ℚ) / 5 + (1 : ℚ) / 62 + (1 : ℚ) / 11470 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 41.
    Certified exact rational solution (8/41 = 1/6 + 1/36 + 1/1476) via norm_num (P90). -/
theorem schinzel_cert_a8_n41 : (8 : ℚ) / 41 = (1 : ℚ) / 6 + (1 : ℚ) / 36 + (1 : ℚ) / 1476 := by
  norm_num

/-- Schinzel instance certificate for numerator a = 8, denominator n = 43.
    Certified exact rational solution (8/43 = 1/6 + 1/52 + 1/6708) via norm_num (P90). -/
theorem schinzel_cert_a8_n43 : (8 : ℚ) / 43 = (1 : ℚ) / 6 + (1 : ℚ) / 52 + (1 : ℚ) / 6708 := by
  norm_num
