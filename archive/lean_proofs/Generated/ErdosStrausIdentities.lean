/-
EvoByte Formal Proof Catalog: Certified Erdős–Straus Polynomial Identities in Q[k].
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Erdős–Straus polynomial identity for congruence class n ≡ 0 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r0 : ∀ k : ℚ,
    4 * ((12 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) =
    ((24 : ℚ) + (24 : ℚ) * k) * (((24 : ℚ) + (24 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((12 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k) + ((12 : ℚ) + (12 : ℚ) * k) * ((24 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 2 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r2 : ∀ k : ℚ,
    4 * ((1 : ℚ) + (12 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) =
    ((2 : ℚ) + (24 : ℚ) * k) * (((2 : ℚ) + (24 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (12 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k) + ((1 : ℚ) + (12 : ℚ) * k) * ((2 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 3 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r3 : ∀ k : ℚ,
    4 * ((1 : ℚ) + (8 : ℚ) * k) * ((4 : ℚ) + (32 : ℚ) * k) * ((12 : ℚ) + (96 : ℚ) * k) =
    ((3 : ℚ) + (24 : ℚ) * k) * (((4 : ℚ) + (32 : ℚ) * k) * ((12 : ℚ) + (96 : ℚ) * k) + ((1 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (96 : ℚ) * k) + ((1 : ℚ) + (8 : ℚ) * k) * ((4 : ℚ) + (32 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 4 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r4 : ∀ k : ℚ,
    4 * ((2 : ℚ) + (12 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) =
    ((4 : ℚ) + (24 : ℚ) * k) * (((4 : ℚ) + (24 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (12 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k) + ((2 : ℚ) + (12 : ℚ) * k) * ((4 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 5 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r5 : ∀ k : ℚ,
    4 * ((2 : ℚ) + (8 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((5 : ℚ) + (24 : ℚ) * k) * (((5 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (8 : ℚ) * k) * ((10 : ℚ) + (88 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((2 : ℚ) + (8 : ℚ) * k) * ((5 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 6 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r6 : ∀ k : ℚ,
    4 * ((3 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) =
    ((6 : ℚ) + (24 : ℚ) * k) * (((6 : ℚ) + (24 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k) + ((3 : ℚ) + (12 : ℚ) * k) * ((6 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 7 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r7 : ∀ k : ℚ,
    4 * ((2 : ℚ) + (6 : ℚ) * k) * ((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2) * ((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2) =
    ((7 : ℚ) + (24 : ℚ) * k) * (((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2) * ((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2) + ((2 : ℚ) + (6 : ℚ) * k) * ((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2) + ((2 : ℚ) + (6 : ℚ) * k) * ((28 : ℚ) + (180 : ℚ) * k + (288 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 8 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r8 : ∀ k : ℚ,
    4 * ((4 : ℚ) + (12 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) =
    ((8 : ℚ) + (24 : ℚ) * k) * (((8 : ℚ) + (24 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (12 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k) + ((4 : ℚ) + (12 : ℚ) * k) * ((8 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 9 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r9 : ∀ k : ℚ,
    4 * ((3 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (32 : ℚ) * k) * ((36 : ℚ) + (96 : ℚ) * k) =
    ((9 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (32 : ℚ) * k) * ((36 : ℚ) + (96 : ℚ) * k) + ((3 : ℚ) + (8 : ℚ) * k) * ((36 : ℚ) + (96 : ℚ) * k) + ((3 : ℚ) + (8 : ℚ) * k) * ((12 : ℚ) + (32 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 10 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r10 : ∀ k : ℚ,
    4 * ((5 : ℚ) + (12 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) =
    ((10 : ℚ) + (24 : ℚ) * k) * (((10 : ℚ) + (24 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (12 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k) + ((5 : ℚ) + (12 : ℚ) * k) * ((10 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 11 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r11 : ∀ k : ℚ,
    4 * ((4 : ℚ) + (8 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (24 : ℚ) * k) * (((11 : ℚ) + (24 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (8 : ℚ) * k) * ((44 : ℚ) + (184 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((4 : ℚ) + (8 : ℚ) * k) * ((11 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 12 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r12 : ∀ k : ℚ,
    4 * ((6 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) =
    ((12 : ℚ) + (24 : ℚ) * k) * (((12 : ℚ) + (24 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k) + ((6 : ℚ) + (12 : ℚ) * k) * ((12 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 13 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r13 : ∀ k : ℚ,
    4 * ((4 : ℚ) + (6 : ℚ) * k) * ((52 : ℚ) + (174 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((26 : ℚ) + (87 : ℚ) * k + (72 : ℚ) * k ^ 2) =
    ((13 : ℚ) + (24 : ℚ) * k) * (((52 : ℚ) + (174 : ℚ) * k + (144 : ℚ) * k ^ 2) * ((26 : ℚ) + (87 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((4 : ℚ) + (6 : ℚ) * k) * ((26 : ℚ) + (87 : ℚ) * k + (72 : ℚ) * k ^ 2) + ((4 : ℚ) + (6 : ℚ) * k) * ((52 : ℚ) + (174 : ℚ) * k + (144 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 14 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r14 : ∀ k : ℚ,
    4 * ((7 : ℚ) + (12 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) =
    ((14 : ℚ) + (24 : ℚ) * k) * (((14 : ℚ) + (24 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) + ((7 : ℚ) + (12 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k) + ((7 : ℚ) + (12 : ℚ) * k) * ((14 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 15 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r15 : ∀ k : ℚ,
    4 * ((5 : ℚ) + (8 : ℚ) * k) * ((20 : ℚ) + (32 : ℚ) * k) * ((60 : ℚ) + (96 : ℚ) * k) =
    ((15 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (32 : ℚ) * k) * ((60 : ℚ) + (96 : ℚ) * k) + ((5 : ℚ) + (8 : ℚ) * k) * ((60 : ℚ) + (96 : ℚ) * k) + ((5 : ℚ) + (8 : ℚ) * k) * ((20 : ℚ) + (32 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 16 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r16 : ∀ k : ℚ,
    4 * ((8 : ℚ) + (12 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) =
    ((16 : ℚ) + (24 : ℚ) * k) * (((16 : ℚ) + (24 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) + ((8 : ℚ) + (12 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k) + ((8 : ℚ) + (12 : ℚ) * k) * ((16 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 17 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r17 : ∀ k : ℚ,
    4 * ((6 : ℚ) + (8 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((17 : ℚ) + (24 : ℚ) * k) * (((17 : ℚ) + (24 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((6 : ℚ) + (8 : ℚ) * k) * ((102 : ℚ) + (280 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((6 : ℚ) + (8 : ℚ) * k) * ((17 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 18 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r18 : ∀ k : ℚ,
    4 * ((9 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) =
    ((18 : ℚ) + (24 : ℚ) * k) * (((18 : ℚ) + (24 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((9 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k) + ((9 : ℚ) + (12 : ℚ) * k) * ((18 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 19 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r19 : ∀ k : ℚ,
    4 * ((5 : ℚ) + (6 : ℚ) * k) * ((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2) * ((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2) =
    ((19 : ℚ) + (24 : ℚ) * k) * (((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2) * ((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2) + ((5 : ℚ) + (6 : ℚ) * k) * ((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2) + ((5 : ℚ) + (6 : ℚ) * k) * ((190 : ℚ) + (468 : ℚ) * k + (288 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 20 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r20 : ∀ k : ℚ,
    4 * ((10 : ℚ) + (12 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) =
    ((20 : ℚ) + (24 : ℚ) * k) * (((20 : ℚ) + (24 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) + ((10 : ℚ) + (12 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k) + ((10 : ℚ) + (12 : ℚ) * k) * ((20 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 21 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r21 : ∀ k : ℚ,
    4 * ((7 : ℚ) + (8 : ℚ) * k) * ((28 : ℚ) + (32 : ℚ) * k) * ((84 : ℚ) + (96 : ℚ) * k) =
    ((21 : ℚ) + (24 : ℚ) * k) * (((28 : ℚ) + (32 : ℚ) * k) * ((84 : ℚ) + (96 : ℚ) * k) + ((7 : ℚ) + (8 : ℚ) * k) * ((84 : ℚ) + (96 : ℚ) * k) + ((7 : ℚ) + (8 : ℚ) * k) * ((28 : ℚ) + (32 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 22 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r22 : ∀ k : ℚ,
    4 * ((11 : ℚ) + (12 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) =
    ((22 : ℚ) + (24 : ℚ) * k) * (((22 : ℚ) + (24 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) + ((11 : ℚ) + (12 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k) + ((11 : ℚ) + (12 : ℚ) * k) * ((22 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 23 [mod 24].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m24_r23 : ∀ k : ℚ,
    4 * ((8 : ℚ) + (8 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (24 : ℚ) * k) * (((23 : ℚ) + (24 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((8 : ℚ) + (8 : ℚ) * k) * ((184 : ℚ) + (376 : ℚ) * k + (192 : ℚ) * k ^ 2) + ((8 : ℚ) + (8 : ℚ) * k) * ((23 : ℚ) + (24 : ℚ) * k)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 73 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r73 : ∀ k : ℚ,
    4 * ((20 : ℚ) + (210 : ℚ) * k) * ((4380 : ℚ) + (140190 : ℚ) * k + (1493100 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3) * ((219 : ℚ) + (4710 : ℚ) * k + (25200 : ℚ) * k ^ 2) =
    ((73 : ℚ) + (840 : ℚ) * k) * (((4380 : ℚ) + (140190 : ℚ) * k + (1493100 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3) * ((219 : ℚ) + (4710 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((20 : ℚ) + (210 : ℚ) * k) * ((219 : ℚ) + (4710 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((20 : ℚ) + (210 : ℚ) * k) * ((4380 : ℚ) + (140190 : ℚ) * k + (1493100 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 97 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r97 : ∀ k : ℚ,
    4 * ((26 : ℚ) + (210 : ℚ) * k) * ((364 : ℚ) + (6060 : ℚ) * k + (25200 : ℚ) * k ^ 2) * ((35308 : ℚ) + (893580 : ℚ) * k + (7534800 : ℚ) * k ^ 2 + (21168000 : ℚ) * k ^ 3) =
    ((97 : ℚ) + (840 : ℚ) * k) * (((364 : ℚ) + (6060 : ℚ) * k + (25200 : ℚ) * k ^ 2) * ((35308 : ℚ) + (893580 : ℚ) * k + (7534800 : ℚ) * k ^ 2 + (21168000 : ℚ) * k ^ 3) + ((26 : ℚ) + (210 : ℚ) * k) * ((35308 : ℚ) + (893580 : ℚ) * k + (7534800 : ℚ) * k ^ 2 + (21168000 : ℚ) * k ^ 3) + ((26 : ℚ) + (210 : ℚ) * k) * ((364 : ℚ) + (6060 : ℚ) * k + (25200 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 193 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r193 : ∀ k : ℚ,
    4 * ((50 : ℚ) + (210 : ℚ) * k) * ((4825 : ℚ) + (41265 : ℚ) * k + (88200 : ℚ) * k ^ 2) * ((1930 : ℚ) + (16506 : ℚ) * k + (35280 : ℚ) * k ^ 2) =
    ((193 : ℚ) + (840 : ℚ) * k) * (((4825 : ℚ) + (41265 : ℚ) * k + (88200 : ℚ) * k ^ 2) * ((1930 : ℚ) + (16506 : ℚ) * k + (35280 : ℚ) * k ^ 2) + ((50 : ℚ) + (210 : ℚ) * k) * ((1930 : ℚ) + (16506 : ℚ) * k + (35280 : ℚ) * k ^ 2) + ((50 : ℚ) + (210 : ℚ) * k) * ((4825 : ℚ) + (41265 : ℚ) * k + (88200 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 241 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r241 : ∀ k : ℚ,
    4 * ((62 : ℚ) + (210 : ℚ) * k) * ((134478 : ℚ) + (1372470 : ℚ) * k + (4668300 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3) * ((2169 : ℚ) + (14790 : ℚ) * k + (25200 : ℚ) * k ^ 2) =
    ((241 : ℚ) + (840 : ℚ) * k) * (((134478 : ℚ) + (1372470 : ℚ) * k + (4668300 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3) * ((2169 : ℚ) + (14790 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((62 : ℚ) + (210 : ℚ) * k) * ((2169 : ℚ) + (14790 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((62 : ℚ) + (210 : ℚ) * k) * ((134478 : ℚ) + (1372470 : ℚ) * k + (4668300 : ℚ) * k ^ 2 + (5292000 : ℚ) * k ^ 3)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 313 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r313 : ∀ k : ℚ,
    4 * ((80 : ℚ) + (210 : ℚ) * k) * ((563400 : ℚ) + (4493325 : ℚ) * k + (11944800 : ℚ) * k ^ 2 + (10584000 : ℚ) * k ^ 3) * ((3600 : ℚ) + (19050 : ℚ) * k + (25200 : ℚ) * k ^ 2) =
    ((313 : ℚ) + (840 : ℚ) * k) * (((563400 : ℚ) + (4493325 : ℚ) * k + (11944800 : ℚ) * k ^ 2 + (10584000 : ℚ) * k ^ 3) * ((3600 : ℚ) + (19050 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((80 : ℚ) + (210 : ℚ) * k) * ((3600 : ℚ) + (19050 : ℚ) * k + (25200 : ℚ) * k ^ 2) + ((80 : ℚ) + (210 : ℚ) * k) * ((563400 : ℚ) + (4493325 : ℚ) * k + (11944800 : ℚ) * k ^ 2 + (10584000 : ℚ) * k ^ 3)) := by
  intro k
  ring

/-- Erdős–Straus polynomial identity for congruence class n ≡ 337 [mod 840].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem erdos_straus_ident_m840_r337 : ∀ k : ℚ,
    4 * ((85 : ℚ) + (210 : ℚ) * k) * ((653106 : ℚ) + (4845596 : ℚ) * k + (11983440 : ℚ) * k ^ 2 + (9878400 : ℚ) * k ^ 3) * ((9690 : ℚ) + (47740 : ℚ) * k + (58800 : ℚ) * k ^ 2) =
    ((337 : ℚ) + (840 : ℚ) * k) * (((653106 : ℚ) + (4845596 : ℚ) * k + (11983440 : ℚ) * k ^ 2 + (9878400 : ℚ) * k ^ 3) * ((9690 : ℚ) + (47740 : ℚ) * k + (58800 : ℚ) * k ^ 2) + ((85 : ℚ) + (210 : ℚ) * k) * ((9690 : ℚ) + (47740 : ℚ) * k + (58800 : ℚ) * k ^ 2) + ((85 : ℚ) + (210 : ℚ) * k) * ((653106 : ℚ) + (4845596 : ℚ) * k + (11983440 : ℚ) * k ^ 2 + (9878400 : ℚ) * k ^ 3)) := by
  intro k
  ring
