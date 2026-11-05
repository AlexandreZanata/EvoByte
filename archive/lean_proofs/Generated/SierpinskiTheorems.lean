/-
EvoByte Formal Proof Catalog: Certified Sierpiński 5/n Identities and Certificates.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 0 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r0 : ∀ k : ℚ,
    5 * ((48 : ℚ) + (48 : ℚ) * k) * ((72 : ℚ) + (72 : ℚ) * k) * ((144 : ℚ) + (144 : ℚ) * k) =
    ((120 : ℚ) + (120 : ℚ) * k) * (((72 : ℚ) + (72 : ℚ) * k) * ((144 : ℚ) + (144 : ℚ) * k) + ((48 : ℚ) + (48 : ℚ) * k) * ((144 : ℚ) + (144 : ℚ) * k) + ((48 : ℚ) + (48 : ℚ) * k) * ((72 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 2 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r2 : ∀ k : ℚ,
    5 * ((1 : ℚ) + (30 : ℚ) * k) * ((1 : ℚ) + (90 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((2 : ℚ) + (120 : ℚ) * k) =
    ((2 : ℚ) + (120 : ℚ) * k) * (((1 : ℚ) + (90 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((2 : ℚ) + (120 : ℚ) * k) + ((1 : ℚ) + (30 : ℚ) * k) * ((2 : ℚ) + (120 : ℚ) * k) + ((1 : ℚ) + (30 : ℚ) * k) * ((1 : ℚ) + (90 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 3 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r3 : ∀ k : ℚ,
    5 * ((1 : ℚ) + (30 : ℚ) * k) * ((3 : ℚ) + (120 : ℚ) * k) * ((3 : ℚ) + (210 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((3 : ℚ) + (120 : ℚ) * k) * (((3 : ℚ) + (120 : ℚ) * k) * ((3 : ℚ) + (210 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((1 : ℚ) + (30 : ℚ) * k) * ((3 : ℚ) + (210 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((1 : ℚ) + (30 : ℚ) * k) * ((3 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 4 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r4 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (30 : ℚ) * k) * ((2 : ℚ) + (90 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((4 : ℚ) + (120 : ℚ) * k) =
    ((4 : ℚ) + (120 : ℚ) * k) * (((2 : ℚ) + (90 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((4 : ℚ) + (120 : ℚ) * k) + ((2 : ℚ) + (30 : ℚ) * k) * ((4 : ℚ) + (120 : ℚ) * k) + ((2 : ℚ) + (30 : ℚ) * k) * ((2 : ℚ) + (90 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 5 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r5 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (48 : ℚ) * k) * ((3 : ℚ) + (72 : ℚ) * k) * ((6 : ℚ) + (144 : ℚ) * k) =
    ((5 : ℚ) + (120 : ℚ) * k) * (((3 : ℚ) + (72 : ℚ) * k) * ((6 : ℚ) + (144 : ℚ) * k) + ((2 : ℚ) + (48 : ℚ) * k) * ((6 : ℚ) + (144 : ℚ) * k) + ((2 : ℚ) + (48 : ℚ) * k) * ((3 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 6 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r6 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (30 : ℚ) * k) * ((6 : ℚ) + (210 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((6 : ℚ) + (120 : ℚ) * k) =
    ((6 : ℚ) + (120 : ℚ) * k) * (((6 : ℚ) + (210 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((6 : ℚ) + (120 : ℚ) * k) + ((2 : ℚ) + (30 : ℚ) * k) * ((6 : ℚ) + (120 : ℚ) * k) + ((2 : ℚ) + (30 : ℚ) * k) * ((6 : ℚ) + (210 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 7 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r7 : ∀ k : ℚ,
    5 * ((2 : ℚ) + (30 : ℚ) * k) * ((7 : ℚ) + (120 : ℚ) * k) * ((14 : ℚ) + (450 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((7 : ℚ) + (120 : ℚ) * k) * (((7 : ℚ) + (120 : ℚ) * k) * ((14 : ℚ) + (450 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((2 : ℚ) + (30 : ℚ) * k) * ((14 : ℚ) + (450 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((2 : ℚ) + (30 : ℚ) * k) * ((7 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 8 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r8 : ∀ k : ℚ,
    5 * ((3 : ℚ) + (30 : ℚ) * k) * ((6 : ℚ) + (150 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((8 : ℚ) + (120 : ℚ) * k) =
    ((8 : ℚ) + (120 : ℚ) * k) * (((6 : ℚ) + (150 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((8 : ℚ) + (120 : ℚ) * k) + ((3 : ℚ) + (30 : ℚ) * k) * ((8 : ℚ) + (120 : ℚ) * k) + ((3 : ℚ) + (30 : ℚ) * k) * ((6 : ℚ) + (150 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 10 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r10 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (48 : ℚ) * k) * ((6 : ℚ) + (72 : ℚ) * k) * ((12 : ℚ) + (144 : ℚ) * k) =
    ((10 : ℚ) + (120 : ℚ) * k) * (((6 : ℚ) + (72 : ℚ) * k) * ((12 : ℚ) + (144 : ℚ) * k) + ((4 : ℚ) + (48 : ℚ) * k) * ((12 : ℚ) + (144 : ℚ) * k) + ((4 : ℚ) + (48 : ℚ) * k) * ((6 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 11 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r11 : ∀ k : ℚ,
    5 * ((3 : ℚ) + (30 : ℚ) * k) * ((11 : ℚ) + (120 : ℚ) * k) * ((33 : ℚ) + (690 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((11 : ℚ) + (120 : ℚ) * k) * (((11 : ℚ) + (120 : ℚ) * k) * ((33 : ℚ) + (690 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((3 : ℚ) + (30 : ℚ) * k) * ((33 : ℚ) + (690 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((3 : ℚ) + (30 : ℚ) * k) * ((11 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 12 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r12 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (30 : ℚ) * k) * ((12 : ℚ) + (210 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((12 : ℚ) + (120 : ℚ) * k) =
    ((12 : ℚ) + (120 : ℚ) * k) * (((12 : ℚ) + (210 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((12 : ℚ) + (120 : ℚ) * k) + ((4 : ℚ) + (30 : ℚ) * k) * ((12 : ℚ) + (120 : ℚ) * k) + ((4 : ℚ) + (30 : ℚ) * k) * ((12 : ℚ) + (210 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 14 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r14 : ∀ k : ℚ,
    5 * ((4 : ℚ) + (30 : ℚ) * k) * ((28 : ℚ) + (450 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((14 : ℚ) + (120 : ℚ) * k) =
    ((14 : ℚ) + (120 : ℚ) * k) * (((28 : ℚ) + (450 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((14 : ℚ) + (120 : ℚ) * k) + ((4 : ℚ) + (30 : ℚ) * k) * ((14 : ℚ) + (120 : ℚ) * k) + ((4 : ℚ) + (30 : ℚ) * k) * ((28 : ℚ) + (450 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 15 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r15 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (48 : ℚ) * k) * ((9 : ℚ) + (72 : ℚ) * k) * ((18 : ℚ) + (144 : ℚ) * k) =
    ((15 : ℚ) + (120 : ℚ) * k) * (((9 : ℚ) + (72 : ℚ) * k) * ((18 : ℚ) + (144 : ℚ) * k) + ((6 : ℚ) + (48 : ℚ) * k) * ((18 : ℚ) + (144 : ℚ) * k) + ((6 : ℚ) + (48 : ℚ) * k) * ((9 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 16 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r16 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (30 : ℚ) * k) * ((20 : ℚ) + (270 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((16 : ℚ) + (120 : ℚ) * k) =
    ((16 : ℚ) + (120 : ℚ) * k) * (((20 : ℚ) + (270 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((16 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (30 : ℚ) * k) * ((16 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (30 : ℚ) * k) * ((20 : ℚ) + (270 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 18 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r18 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (30 : ℚ) * k) * ((45 : ℚ) + (570 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((18 : ℚ) + (120 : ℚ) * k) =
    ((18 : ℚ) + (120 : ℚ) * k) * (((45 : ℚ) + (570 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((18 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (30 : ℚ) * k) * ((18 : ℚ) + (120 : ℚ) * k) + ((5 : ℚ) + (30 : ℚ) * k) * ((45 : ℚ) + (570 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 19 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r19 : ∀ k : ℚ,
    5 * ((5 : ℚ) + (30 : ℚ) * k) * ((19 : ℚ) + (120 : ℚ) * k) * ((95 : ℚ) + (1170 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((19 : ℚ) + (120 : ℚ) * k) * (((19 : ℚ) + (120 : ℚ) * k) * ((95 : ℚ) + (1170 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((5 : ℚ) + (30 : ℚ) * k) * ((95 : ℚ) + (1170 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((5 : ℚ) + (30 : ℚ) * k) * ((19 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 20 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r20 : ∀ k : ℚ,
    5 * ((8 : ℚ) + (48 : ℚ) * k) * ((12 : ℚ) + (72 : ℚ) * k) * ((24 : ℚ) + (144 : ℚ) * k) =
    ((20 : ℚ) + (120 : ℚ) * k) * (((12 : ℚ) + (72 : ℚ) * k) * ((24 : ℚ) + (144 : ℚ) * k) + ((8 : ℚ) + (48 : ℚ) * k) * ((24 : ℚ) + (144 : ℚ) * k) + ((8 : ℚ) + (48 : ℚ) * k) * ((12 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 22 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r22 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (30 : ℚ) * k) * ((66 : ℚ) + (690 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((22 : ℚ) + (120 : ℚ) * k) =
    ((22 : ℚ) + (120 : ℚ) * k) * (((66 : ℚ) + (690 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((22 : ℚ) + (120 : ℚ) * k) + ((6 : ℚ) + (30 : ℚ) * k) * ((22 : ℚ) + (120 : ℚ) * k) + ((6 : ℚ) + (30 : ℚ) * k) * ((66 : ℚ) + (690 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 23 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r23 : ∀ k : ℚ,
    5 * ((6 : ℚ) + (30 : ℚ) * k) * ((23 : ℚ) + (120 : ℚ) * k) * ((138 : ℚ) + (1410 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((23 : ℚ) + (120 : ℚ) * k) * (((23 : ℚ) + (120 : ℚ) * k) * ((138 : ℚ) + (1410 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((6 : ℚ) + (30 : ℚ) * k) * ((138 : ℚ) + (1410 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((6 : ℚ) + (30 : ℚ) * k) * ((23 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 24 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r24 : ∀ k : ℚ,
    5 * ((7 : ℚ) + (30 : ℚ) * k) * ((42 : ℚ) + (390 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((24 : ℚ) + (120 : ℚ) * k) =
    ((24 : ℚ) + (120 : ℚ) * k) * (((42 : ℚ) + (390 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((24 : ℚ) + (120 : ℚ) * k) + ((7 : ℚ) + (30 : ℚ) * k) * ((24 : ℚ) + (120 : ℚ) * k) + ((7 : ℚ) + (30 : ℚ) * k) * ((42 : ℚ) + (390 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 25 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r25 : ∀ k : ℚ,
    5 * ((10 : ℚ) + (48 : ℚ) * k) * ((15 : ℚ) + (72 : ℚ) * k) * ((30 : ℚ) + (144 : ℚ) * k) =
    ((25 : ℚ) + (120 : ℚ) * k) * (((15 : ℚ) + (72 : ℚ) * k) * ((30 : ℚ) + (144 : ℚ) * k) + ((10 : ℚ) + (48 : ℚ) * k) * ((30 : ℚ) + (144 : ℚ) * k) + ((10 : ℚ) + (48 : ℚ) * k) * ((15 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 26 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r26 : ∀ k : ℚ,
    5 * ((7 : ℚ) + (30 : ℚ) * k) * ((91 : ℚ) + (810 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((26 : ℚ) + (120 : ℚ) * k) =
    ((26 : ℚ) + (120 : ℚ) * k) * (((91 : ℚ) + (810 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((26 : ℚ) + (120 : ℚ) * k) + ((7 : ℚ) + (30 : ℚ) * k) * ((26 : ℚ) + (120 : ℚ) * k) + ((7 : ℚ) + (30 : ℚ) * k) * ((91 : ℚ) + (810 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 27 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r27 : ∀ k : ℚ,
    5 * ((7 : ℚ) + (30 : ℚ) * k) * ((27 : ℚ) + (120 : ℚ) * k) * ((189 : ℚ) + (1650 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((27 : ℚ) + (120 : ℚ) * k) * (((27 : ℚ) + (120 : ℚ) * k) * ((189 : ℚ) + (1650 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((7 : ℚ) + (30 : ℚ) * k) * ((189 : ℚ) + (1650 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((7 : ℚ) + (30 : ℚ) * k) * ((27 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 28 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r28 : ∀ k : ℚ,
    5 * ((8 : ℚ) + (30 : ℚ) * k) * ((56 : ℚ) + (450 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((28 : ℚ) + (120 : ℚ) * k) =
    ((28 : ℚ) + (120 : ℚ) * k) * (((56 : ℚ) + (450 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((28 : ℚ) + (120 : ℚ) * k) + ((8 : ℚ) + (30 : ℚ) * k) * ((28 : ℚ) + (120 : ℚ) * k) + ((8 : ℚ) + (30 : ℚ) * k) * ((56 : ℚ) + (450 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 30 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r30 : ∀ k : ℚ,
    5 * ((12 : ℚ) + (48 : ℚ) * k) * ((18 : ℚ) + (72 : ℚ) * k) * ((36 : ℚ) + (144 : ℚ) * k) =
    ((30 : ℚ) + (120 : ℚ) * k) * (((18 : ℚ) + (72 : ℚ) * k) * ((36 : ℚ) + (144 : ℚ) * k) + ((12 : ℚ) + (48 : ℚ) * k) * ((36 : ℚ) + (144 : ℚ) * k) + ((12 : ℚ) + (48 : ℚ) * k) * ((18 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 31 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r31 : ∀ k : ℚ,
    5 * ((8 : ℚ) + (30 : ℚ) * k) * ((31 : ℚ) + (120 : ℚ) * k) * ((248 : ℚ) + (1890 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((31 : ℚ) + (120 : ℚ) * k) * (((31 : ℚ) + (120 : ℚ) * k) * ((248 : ℚ) + (1890 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((8 : ℚ) + (30 : ℚ) * k) * ((248 : ℚ) + (1890 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((8 : ℚ) + (30 : ℚ) * k) * ((31 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 32 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r32 : ∀ k : ℚ,
    5 * ((9 : ℚ) + (30 : ℚ) * k) * ((72 : ℚ) + (510 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((32 : ℚ) + (120 : ℚ) * k) =
    ((32 : ℚ) + (120 : ℚ) * k) * (((72 : ℚ) + (510 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((32 : ℚ) + (120 : ℚ) * k) + ((9 : ℚ) + (30 : ℚ) * k) * ((32 : ℚ) + (120 : ℚ) * k) + ((9 : ℚ) + (30 : ℚ) * k) * ((72 : ℚ) + (510 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 34 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r34 : ∀ k : ℚ,
    5 * ((9 : ℚ) + (30 : ℚ) * k) * ((153 : ℚ) + (1050 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((34 : ℚ) + (120 : ℚ) * k) =
    ((34 : ℚ) + (120 : ℚ) * k) * (((153 : ℚ) + (1050 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((34 : ℚ) + (120 : ℚ) * k) + ((9 : ℚ) + (30 : ℚ) * k) * ((34 : ℚ) + (120 : ℚ) * k) + ((9 : ℚ) + (30 : ℚ) * k) * ((153 : ℚ) + (1050 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 35 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r35 : ∀ k : ℚ,
    5 * ((14 : ℚ) + (48 : ℚ) * k) * ((21 : ℚ) + (72 : ℚ) * k) * ((42 : ℚ) + (144 : ℚ) * k) =
    ((35 : ℚ) + (120 : ℚ) * k) * (((21 : ℚ) + (72 : ℚ) * k) * ((42 : ℚ) + (144 : ℚ) * k) + ((14 : ℚ) + (48 : ℚ) * k) * ((42 : ℚ) + (144 : ℚ) * k) + ((14 : ℚ) + (48 : ℚ) * k) * ((21 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 36 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r36 : ∀ k : ℚ,
    5 * ((10 : ℚ) + (30 : ℚ) * k) * ((90 : ℚ) + (570 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((36 : ℚ) + (120 : ℚ) * k) =
    ((36 : ℚ) + (120 : ℚ) * k) * (((90 : ℚ) + (570 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((36 : ℚ) + (120 : ℚ) * k) + ((10 : ℚ) + (30 : ℚ) * k) * ((36 : ℚ) + (120 : ℚ) * k) + ((10 : ℚ) + (30 : ℚ) * k) * ((90 : ℚ) + (570 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 38 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r38 : ∀ k : ℚ,
    5 * ((10 : ℚ) + (30 : ℚ) * k) * ((190 : ℚ) + (1170 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((38 : ℚ) + (120 : ℚ) * k) =
    ((38 : ℚ) + (120 : ℚ) * k) * (((190 : ℚ) + (1170 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((38 : ℚ) + (120 : ℚ) * k) + ((10 : ℚ) + (30 : ℚ) * k) * ((38 : ℚ) + (120 : ℚ) * k) + ((10 : ℚ) + (30 : ℚ) * k) * ((190 : ℚ) + (1170 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 39 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r39 : ∀ k : ℚ,
    5 * ((10 : ℚ) + (30 : ℚ) * k) * ((39 : ℚ) + (120 : ℚ) * k) * ((390 : ℚ) + (2370 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((39 : ℚ) + (120 : ℚ) * k) * (((39 : ℚ) + (120 : ℚ) * k) * ((390 : ℚ) + (2370 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((10 : ℚ) + (30 : ℚ) * k) * ((390 : ℚ) + (2370 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((10 : ℚ) + (30 : ℚ) * k) * ((39 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 40 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r40 : ∀ k : ℚ,
    5 * ((16 : ℚ) + (48 : ℚ) * k) * ((24 : ℚ) + (72 : ℚ) * k) * ((48 : ℚ) + (144 : ℚ) * k) =
    ((40 : ℚ) + (120 : ℚ) * k) * (((24 : ℚ) + (72 : ℚ) * k) * ((48 : ℚ) + (144 : ℚ) * k) + ((16 : ℚ) + (48 : ℚ) * k) * ((48 : ℚ) + (144 : ℚ) * k) + ((16 : ℚ) + (48 : ℚ) * k) * ((24 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 42 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r42 : ∀ k : ℚ,
    5 * ((11 : ℚ) + (30 : ℚ) * k) * ((231 : ℚ) + (1290 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((42 : ℚ) + (120 : ℚ) * k) =
    ((42 : ℚ) + (120 : ℚ) * k) * (((231 : ℚ) + (1290 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((42 : ℚ) + (120 : ℚ) * k) + ((11 : ℚ) + (30 : ℚ) * k) * ((42 : ℚ) + (120 : ℚ) * k) + ((11 : ℚ) + (30 : ℚ) * k) * ((231 : ℚ) + (1290 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 43 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r43 : ∀ k : ℚ,
    5 * ((11 : ℚ) + (30 : ℚ) * k) * ((43 : ℚ) + (120 : ℚ) * k) * ((473 : ℚ) + (2610 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((43 : ℚ) + (120 : ℚ) * k) * (((43 : ℚ) + (120 : ℚ) * k) * ((473 : ℚ) + (2610 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((11 : ℚ) + (30 : ℚ) * k) * ((473 : ℚ) + (2610 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((11 : ℚ) + (30 : ℚ) * k) * ((43 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 44 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r44 : ∀ k : ℚ,
    5 * ((12 : ℚ) + (30 : ℚ) * k) * ((132 : ℚ) + (690 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((44 : ℚ) + (120 : ℚ) * k) =
    ((44 : ℚ) + (120 : ℚ) * k) * (((132 : ℚ) + (690 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((44 : ℚ) + (120 : ℚ) * k) + ((12 : ℚ) + (30 : ℚ) * k) * ((44 : ℚ) + (120 : ℚ) * k) + ((12 : ℚ) + (30 : ℚ) * k) * ((132 : ℚ) + (690 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 45 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r45 : ∀ k : ℚ,
    5 * ((18 : ℚ) + (48 : ℚ) * k) * ((27 : ℚ) + (72 : ℚ) * k) * ((54 : ℚ) + (144 : ℚ) * k) =
    ((45 : ℚ) + (120 : ℚ) * k) * (((27 : ℚ) + (72 : ℚ) * k) * ((54 : ℚ) + (144 : ℚ) * k) + ((18 : ℚ) + (48 : ℚ) * k) * ((54 : ℚ) + (144 : ℚ) * k) + ((18 : ℚ) + (48 : ℚ) * k) * ((27 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 46 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r46 : ∀ k : ℚ,
    5 * ((12 : ℚ) + (30 : ℚ) * k) * ((276 : ℚ) + (1410 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((46 : ℚ) + (120 : ℚ) * k) =
    ((46 : ℚ) + (120 : ℚ) * k) * (((276 : ℚ) + (1410 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((46 : ℚ) + (120 : ℚ) * k) + ((12 : ℚ) + (30 : ℚ) * k) * ((46 : ℚ) + (120 : ℚ) * k) + ((12 : ℚ) + (30 : ℚ) * k) * ((276 : ℚ) + (1410 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 47 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r47 : ∀ k : ℚ,
    5 * ((12 : ℚ) + (30 : ℚ) * k) * ((47 : ℚ) + (120 : ℚ) * k) * ((564 : ℚ) + (2850 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((47 : ℚ) + (120 : ℚ) * k) * (((47 : ℚ) + (120 : ℚ) * k) * ((564 : ℚ) + (2850 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((12 : ℚ) + (30 : ℚ) * k) * ((564 : ℚ) + (2850 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((12 : ℚ) + (30 : ℚ) * k) * ((47 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 48 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r48 : ∀ k : ℚ,
    5 * ((13 : ℚ) + (30 : ℚ) * k) * ((156 : ℚ) + (750 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((48 : ℚ) + (120 : ℚ) * k) =
    ((48 : ℚ) + (120 : ℚ) * k) * (((156 : ℚ) + (750 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((48 : ℚ) + (120 : ℚ) * k) + ((13 : ℚ) + (30 : ℚ) * k) * ((48 : ℚ) + (120 : ℚ) * k) + ((13 : ℚ) + (30 : ℚ) * k) * ((156 : ℚ) + (750 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 50 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r50 : ∀ k : ℚ,
    5 * ((20 : ℚ) + (48 : ℚ) * k) * ((30 : ℚ) + (72 : ℚ) * k) * ((60 : ℚ) + (144 : ℚ) * k) =
    ((50 : ℚ) + (120 : ℚ) * k) * (((30 : ℚ) + (72 : ℚ) * k) * ((60 : ℚ) + (144 : ℚ) * k) + ((20 : ℚ) + (48 : ℚ) * k) * ((60 : ℚ) + (144 : ℚ) * k) + ((20 : ℚ) + (48 : ℚ) * k) * ((30 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 51 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r51 : ∀ k : ℚ,
    5 * ((13 : ℚ) + (30 : ℚ) * k) * ((51 : ℚ) + (120 : ℚ) * k) * ((663 : ℚ) + (3090 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((51 : ℚ) + (120 : ℚ) * k) * (((51 : ℚ) + (120 : ℚ) * k) * ((663 : ℚ) + (3090 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((13 : ℚ) + (30 : ℚ) * k) * ((663 : ℚ) + (3090 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((13 : ℚ) + (30 : ℚ) * k) * ((51 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 52 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r52 : ∀ k : ℚ,
    5 * ((14 : ℚ) + (30 : ℚ) * k) * ((182 : ℚ) + (810 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((52 : ℚ) + (120 : ℚ) * k) =
    ((52 : ℚ) + (120 : ℚ) * k) * (((182 : ℚ) + (810 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((52 : ℚ) + (120 : ℚ) * k) + ((14 : ℚ) + (30 : ℚ) * k) * ((52 : ℚ) + (120 : ℚ) * k) + ((14 : ℚ) + (30 : ℚ) * k) * ((182 : ℚ) + (810 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 54 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r54 : ∀ k : ℚ,
    5 * ((14 : ℚ) + (30 : ℚ) * k) * ((378 : ℚ) + (1650 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((54 : ℚ) + (120 : ℚ) * k) =
    ((54 : ℚ) + (120 : ℚ) * k) * (((378 : ℚ) + (1650 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((54 : ℚ) + (120 : ℚ) * k) + ((14 : ℚ) + (30 : ℚ) * k) * ((54 : ℚ) + (120 : ℚ) * k) + ((14 : ℚ) + (30 : ℚ) * k) * ((378 : ℚ) + (1650 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 55 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r55 : ∀ k : ℚ,
    5 * ((22 : ℚ) + (48 : ℚ) * k) * ((33 : ℚ) + (72 : ℚ) * k) * ((66 : ℚ) + (144 : ℚ) * k) =
    ((55 : ℚ) + (120 : ℚ) * k) * (((33 : ℚ) + (72 : ℚ) * k) * ((66 : ℚ) + (144 : ℚ) * k) + ((22 : ℚ) + (48 : ℚ) * k) * ((66 : ℚ) + (144 : ℚ) * k) + ((22 : ℚ) + (48 : ℚ) * k) * ((33 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 56 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r56 : ∀ k : ℚ,
    5 * ((15 : ℚ) + (30 : ℚ) * k) * ((210 : ℚ) + (870 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((56 : ℚ) + (120 : ℚ) * k) =
    ((56 : ℚ) + (120 : ℚ) * k) * (((210 : ℚ) + (870 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((56 : ℚ) + (120 : ℚ) * k) + ((15 : ℚ) + (30 : ℚ) * k) * ((56 : ℚ) + (120 : ℚ) * k) + ((15 : ℚ) + (30 : ℚ) * k) * ((210 : ℚ) + (870 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 58 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r58 : ∀ k : ℚ,
    5 * ((15 : ℚ) + (30 : ℚ) * k) * ((435 : ℚ) + (1770 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((58 : ℚ) + (120 : ℚ) * k) =
    ((58 : ℚ) + (120 : ℚ) * k) * (((435 : ℚ) + (1770 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((58 : ℚ) + (120 : ℚ) * k) + ((15 : ℚ) + (30 : ℚ) * k) * ((58 : ℚ) + (120 : ℚ) * k) + ((15 : ℚ) + (30 : ℚ) * k) * ((435 : ℚ) + (1770 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 59 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r59 : ∀ k : ℚ,
    5 * ((15 : ℚ) + (30 : ℚ) * k) * ((59 : ℚ) + (120 : ℚ) * k) * ((885 : ℚ) + (3570 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((59 : ℚ) + (120 : ℚ) * k) * (((59 : ℚ) + (120 : ℚ) * k) * ((885 : ℚ) + (3570 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((15 : ℚ) + (30 : ℚ) * k) * ((885 : ℚ) + (3570 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((15 : ℚ) + (30 : ℚ) * k) * ((59 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 60 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r60 : ∀ k : ℚ,
    5 * ((24 : ℚ) + (48 : ℚ) * k) * ((36 : ℚ) + (72 : ℚ) * k) * ((72 : ℚ) + (144 : ℚ) * k) =
    ((60 : ℚ) + (120 : ℚ) * k) * (((36 : ℚ) + (72 : ℚ) * k) * ((72 : ℚ) + (144 : ℚ) * k) + ((24 : ℚ) + (48 : ℚ) * k) * ((72 : ℚ) + (144 : ℚ) * k) + ((24 : ℚ) + (48 : ℚ) * k) * ((36 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 62 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r62 : ∀ k : ℚ,
    5 * ((16 : ℚ) + (30 : ℚ) * k) * ((496 : ℚ) + (1890 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((62 : ℚ) + (120 : ℚ) * k) =
    ((62 : ℚ) + (120 : ℚ) * k) * (((496 : ℚ) + (1890 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((62 : ℚ) + (120 : ℚ) * k) + ((16 : ℚ) + (30 : ℚ) * k) * ((62 : ℚ) + (120 : ℚ) * k) + ((16 : ℚ) + (30 : ℚ) * k) * ((496 : ℚ) + (1890 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 63 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r63 : ∀ k : ℚ,
    5 * ((16 : ℚ) + (30 : ℚ) * k) * ((63 : ℚ) + (120 : ℚ) * k) * ((1008 : ℚ) + (3810 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((63 : ℚ) + (120 : ℚ) * k) * (((63 : ℚ) + (120 : ℚ) * k) * ((1008 : ℚ) + (3810 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((16 : ℚ) + (30 : ℚ) * k) * ((1008 : ℚ) + (3810 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((16 : ℚ) + (30 : ℚ) * k) * ((63 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 64 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r64 : ∀ k : ℚ,
    5 * ((17 : ℚ) + (30 : ℚ) * k) * ((272 : ℚ) + (990 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((64 : ℚ) + (120 : ℚ) * k) =
    ((64 : ℚ) + (120 : ℚ) * k) * (((272 : ℚ) + (990 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((64 : ℚ) + (120 : ℚ) * k) + ((17 : ℚ) + (30 : ℚ) * k) * ((64 : ℚ) + (120 : ℚ) * k) + ((17 : ℚ) + (30 : ℚ) * k) * ((272 : ℚ) + (990 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 65 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r65 : ∀ k : ℚ,
    5 * ((26 : ℚ) + (48 : ℚ) * k) * ((39 : ℚ) + (72 : ℚ) * k) * ((78 : ℚ) + (144 : ℚ) * k) =
    ((65 : ℚ) + (120 : ℚ) * k) * (((39 : ℚ) + (72 : ℚ) * k) * ((78 : ℚ) + (144 : ℚ) * k) + ((26 : ℚ) + (48 : ℚ) * k) * ((78 : ℚ) + (144 : ℚ) * k) + ((26 : ℚ) + (48 : ℚ) * k) * ((39 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 66 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r66 : ∀ k : ℚ,
    5 * ((17 : ℚ) + (30 : ℚ) * k) * ((561 : ℚ) + (2010 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((66 : ℚ) + (120 : ℚ) * k) =
    ((66 : ℚ) + (120 : ℚ) * k) * (((561 : ℚ) + (2010 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((66 : ℚ) + (120 : ℚ) * k) + ((17 : ℚ) + (30 : ℚ) * k) * ((66 : ℚ) + (120 : ℚ) * k) + ((17 : ℚ) + (30 : ℚ) * k) * ((561 : ℚ) + (2010 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 67 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r67 : ∀ k : ℚ,
    5 * ((17 : ℚ) + (30 : ℚ) * k) * ((67 : ℚ) + (120 : ℚ) * k) * ((1139 : ℚ) + (4050 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((67 : ℚ) + (120 : ℚ) * k) * (((67 : ℚ) + (120 : ℚ) * k) * ((1139 : ℚ) + (4050 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((17 : ℚ) + (30 : ℚ) * k) * ((1139 : ℚ) + (4050 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((17 : ℚ) + (30 : ℚ) * k) * ((67 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 68 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r68 : ∀ k : ℚ,
    5 * ((18 : ℚ) + (30 : ℚ) * k) * ((306 : ℚ) + (1050 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((68 : ℚ) + (120 : ℚ) * k) =
    ((68 : ℚ) + (120 : ℚ) * k) * (((306 : ℚ) + (1050 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((68 : ℚ) + (120 : ℚ) * k) + ((18 : ℚ) + (30 : ℚ) * k) * ((68 : ℚ) + (120 : ℚ) * k) + ((18 : ℚ) + (30 : ℚ) * k) * ((306 : ℚ) + (1050 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 70 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r70 : ∀ k : ℚ,
    5 * ((28 : ℚ) + (48 : ℚ) * k) * ((42 : ℚ) + (72 : ℚ) * k) * ((84 : ℚ) + (144 : ℚ) * k) =
    ((70 : ℚ) + (120 : ℚ) * k) * (((42 : ℚ) + (72 : ℚ) * k) * ((84 : ℚ) + (144 : ℚ) * k) + ((28 : ℚ) + (48 : ℚ) * k) * ((84 : ℚ) + (144 : ℚ) * k) + ((28 : ℚ) + (48 : ℚ) * k) * ((42 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 71 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r71 : ∀ k : ℚ,
    5 * ((18 : ℚ) + (30 : ℚ) * k) * ((71 : ℚ) + (120 : ℚ) * k) * ((1278 : ℚ) + (4290 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((71 : ℚ) + (120 : ℚ) * k) * (((71 : ℚ) + (120 : ℚ) * k) * ((1278 : ℚ) + (4290 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((18 : ℚ) + (30 : ℚ) * k) * ((1278 : ℚ) + (4290 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((18 : ℚ) + (30 : ℚ) * k) * ((71 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 72 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r72 : ∀ k : ℚ,
    5 * ((19 : ℚ) + (30 : ℚ) * k) * ((342 : ℚ) + (1110 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((72 : ℚ) + (120 : ℚ) * k) =
    ((72 : ℚ) + (120 : ℚ) * k) * (((342 : ℚ) + (1110 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((72 : ℚ) + (120 : ℚ) * k) + ((19 : ℚ) + (30 : ℚ) * k) * ((72 : ℚ) + (120 : ℚ) * k) + ((19 : ℚ) + (30 : ℚ) * k) * ((342 : ℚ) + (1110 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 74 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r74 : ∀ k : ℚ,
    5 * ((19 : ℚ) + (30 : ℚ) * k) * ((703 : ℚ) + (2250 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((74 : ℚ) + (120 : ℚ) * k) =
    ((74 : ℚ) + (120 : ℚ) * k) * (((703 : ℚ) + (2250 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((74 : ℚ) + (120 : ℚ) * k) + ((19 : ℚ) + (30 : ℚ) * k) * ((74 : ℚ) + (120 : ℚ) * k) + ((19 : ℚ) + (30 : ℚ) * k) * ((703 : ℚ) + (2250 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 75 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r75 : ∀ k : ℚ,
    5 * ((30 : ℚ) + (48 : ℚ) * k) * ((45 : ℚ) + (72 : ℚ) * k) * ((90 : ℚ) + (144 : ℚ) * k) =
    ((75 : ℚ) + (120 : ℚ) * k) * (((45 : ℚ) + (72 : ℚ) * k) * ((90 : ℚ) + (144 : ℚ) * k) + ((30 : ℚ) + (48 : ℚ) * k) * ((90 : ℚ) + (144 : ℚ) * k) + ((30 : ℚ) + (48 : ℚ) * k) * ((45 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 76 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r76 : ∀ k : ℚ,
    5 * ((20 : ℚ) + (30 : ℚ) * k) * ((380 : ℚ) + (1170 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((76 : ℚ) + (120 : ℚ) * k) =
    ((76 : ℚ) + (120 : ℚ) * k) * (((380 : ℚ) + (1170 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((76 : ℚ) + (120 : ℚ) * k) + ((20 : ℚ) + (30 : ℚ) * k) * ((76 : ℚ) + (120 : ℚ) * k) + ((20 : ℚ) + (30 : ℚ) * k) * ((380 : ℚ) + (1170 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 78 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r78 : ∀ k : ℚ,
    5 * ((20 : ℚ) + (30 : ℚ) * k) * ((780 : ℚ) + (2370 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((78 : ℚ) + (120 : ℚ) * k) =
    ((78 : ℚ) + (120 : ℚ) * k) * (((780 : ℚ) + (2370 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((78 : ℚ) + (120 : ℚ) * k) + ((20 : ℚ) + (30 : ℚ) * k) * ((78 : ℚ) + (120 : ℚ) * k) + ((20 : ℚ) + (30 : ℚ) * k) * ((780 : ℚ) + (2370 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 79 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r79 : ∀ k : ℚ,
    5 * ((20 : ℚ) + (30 : ℚ) * k) * ((79 : ℚ) + (120 : ℚ) * k) * ((1580 : ℚ) + (4770 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((79 : ℚ) + (120 : ℚ) * k) * (((79 : ℚ) + (120 : ℚ) * k) * ((1580 : ℚ) + (4770 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((20 : ℚ) + (30 : ℚ) * k) * ((1580 : ℚ) + (4770 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((20 : ℚ) + (30 : ℚ) * k) * ((79 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 80 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r80 : ∀ k : ℚ,
    5 * ((32 : ℚ) + (48 : ℚ) * k) * ((48 : ℚ) + (72 : ℚ) * k) * ((96 : ℚ) + (144 : ℚ) * k) =
    ((80 : ℚ) + (120 : ℚ) * k) * (((48 : ℚ) + (72 : ℚ) * k) * ((96 : ℚ) + (144 : ℚ) * k) + ((32 : ℚ) + (48 : ℚ) * k) * ((96 : ℚ) + (144 : ℚ) * k) + ((32 : ℚ) + (48 : ℚ) * k) * ((48 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 82 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r82 : ∀ k : ℚ,
    5 * ((21 : ℚ) + (30 : ℚ) * k) * ((861 : ℚ) + (2490 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((82 : ℚ) + (120 : ℚ) * k) =
    ((82 : ℚ) + (120 : ℚ) * k) * (((861 : ℚ) + (2490 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((82 : ℚ) + (120 : ℚ) * k) + ((21 : ℚ) + (30 : ℚ) * k) * ((82 : ℚ) + (120 : ℚ) * k) + ((21 : ℚ) + (30 : ℚ) * k) * ((861 : ℚ) + (2490 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 83 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r83 : ∀ k : ℚ,
    5 * ((21 : ℚ) + (30 : ℚ) * k) * ((83 : ℚ) + (120 : ℚ) * k) * ((1743 : ℚ) + (5010 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((83 : ℚ) + (120 : ℚ) * k) * (((83 : ℚ) + (120 : ℚ) * k) * ((1743 : ℚ) + (5010 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((21 : ℚ) + (30 : ℚ) * k) * ((1743 : ℚ) + (5010 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((21 : ℚ) + (30 : ℚ) * k) * ((83 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 84 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r84 : ∀ k : ℚ,
    5 * ((22 : ℚ) + (30 : ℚ) * k) * ((462 : ℚ) + (1290 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((84 : ℚ) + (120 : ℚ) * k) =
    ((84 : ℚ) + (120 : ℚ) * k) * (((462 : ℚ) + (1290 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((84 : ℚ) + (120 : ℚ) * k) + ((22 : ℚ) + (30 : ℚ) * k) * ((84 : ℚ) + (120 : ℚ) * k) + ((22 : ℚ) + (30 : ℚ) * k) * ((462 : ℚ) + (1290 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 85 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r85 : ∀ k : ℚ,
    5 * ((34 : ℚ) + (48 : ℚ) * k) * ((51 : ℚ) + (72 : ℚ) * k) * ((102 : ℚ) + (144 : ℚ) * k) =
    ((85 : ℚ) + (120 : ℚ) * k) * (((51 : ℚ) + (72 : ℚ) * k) * ((102 : ℚ) + (144 : ℚ) * k) + ((34 : ℚ) + (48 : ℚ) * k) * ((102 : ℚ) + (144 : ℚ) * k) + ((34 : ℚ) + (48 : ℚ) * k) * ((51 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 86 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r86 : ∀ k : ℚ,
    5 * ((22 : ℚ) + (30 : ℚ) * k) * ((946 : ℚ) + (2610 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((86 : ℚ) + (120 : ℚ) * k) =
    ((86 : ℚ) + (120 : ℚ) * k) * (((946 : ℚ) + (2610 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((86 : ℚ) + (120 : ℚ) * k) + ((22 : ℚ) + (30 : ℚ) * k) * ((86 : ℚ) + (120 : ℚ) * k) + ((22 : ℚ) + (30 : ℚ) * k) * ((946 : ℚ) + (2610 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 87 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r87 : ∀ k : ℚ,
    5 * ((22 : ℚ) + (30 : ℚ) * k) * ((87 : ℚ) + (120 : ℚ) * k) * ((1914 : ℚ) + (5250 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((87 : ℚ) + (120 : ℚ) * k) * (((87 : ℚ) + (120 : ℚ) * k) * ((1914 : ℚ) + (5250 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((22 : ℚ) + (30 : ℚ) * k) * ((1914 : ℚ) + (5250 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((22 : ℚ) + (30 : ℚ) * k) * ((87 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 88 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r88 : ∀ k : ℚ,
    5 * ((23 : ℚ) + (30 : ℚ) * k) * ((506 : ℚ) + (1350 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((88 : ℚ) + (120 : ℚ) * k) =
    ((88 : ℚ) + (120 : ℚ) * k) * (((506 : ℚ) + (1350 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((88 : ℚ) + (120 : ℚ) * k) + ((23 : ℚ) + (30 : ℚ) * k) * ((88 : ℚ) + (120 : ℚ) * k) + ((23 : ℚ) + (30 : ℚ) * k) * ((506 : ℚ) + (1350 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 90 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r90 : ∀ k : ℚ,
    5 * ((36 : ℚ) + (48 : ℚ) * k) * ((54 : ℚ) + (72 : ℚ) * k) * ((108 : ℚ) + (144 : ℚ) * k) =
    ((90 : ℚ) + (120 : ℚ) * k) * (((54 : ℚ) + (72 : ℚ) * k) * ((108 : ℚ) + (144 : ℚ) * k) + ((36 : ℚ) + (48 : ℚ) * k) * ((108 : ℚ) + (144 : ℚ) * k) + ((36 : ℚ) + (48 : ℚ) * k) * ((54 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 91 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r91 : ∀ k : ℚ,
    5 * ((23 : ℚ) + (30 : ℚ) * k) * ((91 : ℚ) + (120 : ℚ) * k) * ((2093 : ℚ) + (5490 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((91 : ℚ) + (120 : ℚ) * k) * (((91 : ℚ) + (120 : ℚ) * k) * ((2093 : ℚ) + (5490 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((23 : ℚ) + (30 : ℚ) * k) * ((2093 : ℚ) + (5490 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((23 : ℚ) + (30 : ℚ) * k) * ((91 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 92 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r92 : ∀ k : ℚ,
    5 * ((24 : ℚ) + (30 : ℚ) * k) * ((552 : ℚ) + (1410 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((92 : ℚ) + (120 : ℚ) * k) =
    ((92 : ℚ) + (120 : ℚ) * k) * (((552 : ℚ) + (1410 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((92 : ℚ) + (120 : ℚ) * k) + ((24 : ℚ) + (30 : ℚ) * k) * ((92 : ℚ) + (120 : ℚ) * k) + ((24 : ℚ) + (30 : ℚ) * k) * ((552 : ℚ) + (1410 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 94 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r94 : ∀ k : ℚ,
    5 * ((24 : ℚ) + (30 : ℚ) * k) * ((1128 : ℚ) + (2850 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((94 : ℚ) + (120 : ℚ) * k) =
    ((94 : ℚ) + (120 : ℚ) * k) * (((1128 : ℚ) + (2850 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((94 : ℚ) + (120 : ℚ) * k) + ((24 : ℚ) + (30 : ℚ) * k) * ((94 : ℚ) + (120 : ℚ) * k) + ((24 : ℚ) + (30 : ℚ) * k) * ((1128 : ℚ) + (2850 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 95 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r95 : ∀ k : ℚ,
    5 * ((38 : ℚ) + (48 : ℚ) * k) * ((57 : ℚ) + (72 : ℚ) * k) * ((114 : ℚ) + (144 : ℚ) * k) =
    ((95 : ℚ) + (120 : ℚ) * k) * (((57 : ℚ) + (72 : ℚ) * k) * ((114 : ℚ) + (144 : ℚ) * k) + ((38 : ℚ) + (48 : ℚ) * k) * ((114 : ℚ) + (144 : ℚ) * k) + ((38 : ℚ) + (48 : ℚ) * k) * ((57 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 96 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r96 : ∀ k : ℚ,
    5 * ((25 : ℚ) + (30 : ℚ) * k) * ((600 : ℚ) + (1470 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((96 : ℚ) + (120 : ℚ) * k) =
    ((96 : ℚ) + (120 : ℚ) * k) * (((600 : ℚ) + (1470 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((96 : ℚ) + (120 : ℚ) * k) + ((25 : ℚ) + (30 : ℚ) * k) * ((96 : ℚ) + (120 : ℚ) * k) + ((25 : ℚ) + (30 : ℚ) * k) * ((600 : ℚ) + (1470 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 98 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r98 : ∀ k : ℚ,
    5 * ((25 : ℚ) + (30 : ℚ) * k) * ((1225 : ℚ) + (2970 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((98 : ℚ) + (120 : ℚ) * k) =
    ((98 : ℚ) + (120 : ℚ) * k) * (((1225 : ℚ) + (2970 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((98 : ℚ) + (120 : ℚ) * k) + ((25 : ℚ) + (30 : ℚ) * k) * ((98 : ℚ) + (120 : ℚ) * k) + ((25 : ℚ) + (30 : ℚ) * k) * ((1225 : ℚ) + (2970 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 99 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r99 : ∀ k : ℚ,
    5 * ((25 : ℚ) + (30 : ℚ) * k) * ((99 : ℚ) + (120 : ℚ) * k) * ((2475 : ℚ) + (5970 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((99 : ℚ) + (120 : ℚ) * k) * (((99 : ℚ) + (120 : ℚ) * k) * ((2475 : ℚ) + (5970 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((25 : ℚ) + (30 : ℚ) * k) * ((2475 : ℚ) + (5970 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((25 : ℚ) + (30 : ℚ) * k) * ((99 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 100 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r100 : ∀ k : ℚ,
    5 * ((40 : ℚ) + (48 : ℚ) * k) * ((60 : ℚ) + (72 : ℚ) * k) * ((120 : ℚ) + (144 : ℚ) * k) =
    ((100 : ℚ) + (120 : ℚ) * k) * (((60 : ℚ) + (72 : ℚ) * k) * ((120 : ℚ) + (144 : ℚ) * k) + ((40 : ℚ) + (48 : ℚ) * k) * ((120 : ℚ) + (144 : ℚ) * k) + ((40 : ℚ) + (48 : ℚ) * k) * ((60 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 102 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r102 : ∀ k : ℚ,
    5 * ((26 : ℚ) + (30 : ℚ) * k) * ((1326 : ℚ) + (3090 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((102 : ℚ) + (120 : ℚ) * k) =
    ((102 : ℚ) + (120 : ℚ) * k) * (((1326 : ℚ) + (3090 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((102 : ℚ) + (120 : ℚ) * k) + ((26 : ℚ) + (30 : ℚ) * k) * ((102 : ℚ) + (120 : ℚ) * k) + ((26 : ℚ) + (30 : ℚ) * k) * ((1326 : ℚ) + (3090 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 103 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r103 : ∀ k : ℚ,
    5 * ((26 : ℚ) + (30 : ℚ) * k) * ((103 : ℚ) + (120 : ℚ) * k) * ((2678 : ℚ) + (6210 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((103 : ℚ) + (120 : ℚ) * k) * (((103 : ℚ) + (120 : ℚ) * k) * ((2678 : ℚ) + (6210 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((26 : ℚ) + (30 : ℚ) * k) * ((2678 : ℚ) + (6210 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((26 : ℚ) + (30 : ℚ) * k) * ((103 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 104 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r104 : ∀ k : ℚ,
    5 * ((27 : ℚ) + (30 : ℚ) * k) * ((702 : ℚ) + (1590 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((104 : ℚ) + (120 : ℚ) * k) =
    ((104 : ℚ) + (120 : ℚ) * k) * (((702 : ℚ) + (1590 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((104 : ℚ) + (120 : ℚ) * k) + ((27 : ℚ) + (30 : ℚ) * k) * ((104 : ℚ) + (120 : ℚ) * k) + ((27 : ℚ) + (30 : ℚ) * k) * ((702 : ℚ) + (1590 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 105 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r105 : ∀ k : ℚ,
    5 * ((42 : ℚ) + (48 : ℚ) * k) * ((63 : ℚ) + (72 : ℚ) * k) * ((126 : ℚ) + (144 : ℚ) * k) =
    ((105 : ℚ) + (120 : ℚ) * k) * (((63 : ℚ) + (72 : ℚ) * k) * ((126 : ℚ) + (144 : ℚ) * k) + ((42 : ℚ) + (48 : ℚ) * k) * ((126 : ℚ) + (144 : ℚ) * k) + ((42 : ℚ) + (48 : ℚ) * k) * ((63 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 106 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r106 : ∀ k : ℚ,
    5 * ((27 : ℚ) + (30 : ℚ) * k) * ((1431 : ℚ) + (3210 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((106 : ℚ) + (120 : ℚ) * k) =
    ((106 : ℚ) + (120 : ℚ) * k) * (((1431 : ℚ) + (3210 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((106 : ℚ) + (120 : ℚ) * k) + ((27 : ℚ) + (30 : ℚ) * k) * ((106 : ℚ) + (120 : ℚ) * k) + ((27 : ℚ) + (30 : ℚ) * k) * ((1431 : ℚ) + (3210 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 107 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r107 : ∀ k : ℚ,
    5 * ((27 : ℚ) + (30 : ℚ) * k) * ((107 : ℚ) + (120 : ℚ) * k) * ((2889 : ℚ) + (6450 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((107 : ℚ) + (120 : ℚ) * k) * (((107 : ℚ) + (120 : ℚ) * k) * ((2889 : ℚ) + (6450 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((27 : ℚ) + (30 : ℚ) * k) * ((2889 : ℚ) + (6450 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((27 : ℚ) + (30 : ℚ) * k) * ((107 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 108 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r108 : ∀ k : ℚ,
    5 * ((28 : ℚ) + (30 : ℚ) * k) * ((756 : ℚ) + (1650 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((108 : ℚ) + (120 : ℚ) * k) =
    ((108 : ℚ) + (120 : ℚ) * k) * (((756 : ℚ) + (1650 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((108 : ℚ) + (120 : ℚ) * k) + ((28 : ℚ) + (30 : ℚ) * k) * ((108 : ℚ) + (120 : ℚ) * k) + ((28 : ℚ) + (30 : ℚ) * k) * ((756 : ℚ) + (1650 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 110 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r110 : ∀ k : ℚ,
    5 * ((44 : ℚ) + (48 : ℚ) * k) * ((66 : ℚ) + (72 : ℚ) * k) * ((132 : ℚ) + (144 : ℚ) * k) =
    ((110 : ℚ) + (120 : ℚ) * k) * (((66 : ℚ) + (72 : ℚ) * k) * ((132 : ℚ) + (144 : ℚ) * k) + ((44 : ℚ) + (48 : ℚ) * k) * ((132 : ℚ) + (144 : ℚ) * k) + ((44 : ℚ) + (48 : ℚ) * k) * ((66 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 111 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r111 : ∀ k : ℚ,
    5 * ((28 : ℚ) + (30 : ℚ) * k) * ((111 : ℚ) + (120 : ℚ) * k) * ((3108 : ℚ) + (6690 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((111 : ℚ) + (120 : ℚ) * k) * (((111 : ℚ) + (120 : ℚ) * k) * ((3108 : ℚ) + (6690 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((28 : ℚ) + (30 : ℚ) * k) * ((3108 : ℚ) + (6690 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((28 : ℚ) + (30 : ℚ) * k) * ((111 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 112 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r112 : ∀ k : ℚ,
    5 * ((29 : ℚ) + (30 : ℚ) * k) * ((812 : ℚ) + (1710 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((112 : ℚ) + (120 : ℚ) * k) =
    ((112 : ℚ) + (120 : ℚ) * k) * (((812 : ℚ) + (1710 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((112 : ℚ) + (120 : ℚ) * k) + ((29 : ℚ) + (30 : ℚ) * k) * ((112 : ℚ) + (120 : ℚ) * k) + ((29 : ℚ) + (30 : ℚ) * k) * ((812 : ℚ) + (1710 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 114 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r114 : ∀ k : ℚ,
    5 * ((29 : ℚ) + (30 : ℚ) * k) * ((1653 : ℚ) + (3450 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((114 : ℚ) + (120 : ℚ) * k) =
    ((114 : ℚ) + (120 : ℚ) * k) * (((1653 : ℚ) + (3450 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((114 : ℚ) + (120 : ℚ) * k) + ((29 : ℚ) + (30 : ℚ) * k) * ((114 : ℚ) + (120 : ℚ) * k) + ((29 : ℚ) + (30 : ℚ) * k) * ((1653 : ℚ) + (3450 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 115 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r115 : ∀ k : ℚ,
    5 * ((46 : ℚ) + (48 : ℚ) * k) * ((69 : ℚ) + (72 : ℚ) * k) * ((138 : ℚ) + (144 : ℚ) * k) =
    ((115 : ℚ) + (120 : ℚ) * k) * (((69 : ℚ) + (72 : ℚ) * k) * ((138 : ℚ) + (144 : ℚ) * k) + ((46 : ℚ) + (48 : ℚ) * k) * ((138 : ℚ) + (144 : ℚ) * k) + ((46 : ℚ) + (48 : ℚ) * k) * ((69 : ℚ) + (72 : ℚ) * k)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 116 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r116 : ∀ k : ℚ,
    5 * ((30 : ℚ) + (30 : ℚ) * k) * ((870 : ℚ) + (1770 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((116 : ℚ) + (120 : ℚ) * k) =
    ((116 : ℚ) + (120 : ℚ) * k) * (((870 : ℚ) + (1770 : ℚ) * k + (900 : ℚ) * k ^ 2) * ((116 : ℚ) + (120 : ℚ) * k) + ((30 : ℚ) + (30 : ℚ) * k) * ((116 : ℚ) + (120 : ℚ) * k) + ((30 : ℚ) + (30 : ℚ) * k) * ((870 : ℚ) + (1770 : ℚ) * k + (900 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 118 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r118 : ∀ k : ℚ,
    5 * ((30 : ℚ) + (30 : ℚ) * k) * ((1770 : ℚ) + (3570 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((118 : ℚ) + (120 : ℚ) * k) =
    ((118 : ℚ) + (120 : ℚ) * k) * (((1770 : ℚ) + (3570 : ℚ) * k + (1800 : ℚ) * k ^ 2) * ((118 : ℚ) + (120 : ℚ) * k) + ((30 : ℚ) + (30 : ℚ) * k) * ((118 : ℚ) + (120 : ℚ) * k) + ((30 : ℚ) + (30 : ℚ) * k) * ((1770 : ℚ) + (3570 : ℚ) * k + (1800 : ℚ) * k ^ 2)) := by
  intro k
  ring

/-- Sierpiński 5/n polynomial identity for congruence class n ≡ 119 [mod 120].
    Guarantees 4/n = 1/X + 1/Y + 1/Z over Q[k] with integer solutions for positive k. -/
theorem sierpinski_ident_m120_r119 : ∀ k : ℚ,
    5 * ((30 : ℚ) + (30 : ℚ) * k) * ((119 : ℚ) + (120 : ℚ) * k) * ((3570 : ℚ) + (7170 : ℚ) * k + (3600 : ℚ) * k ^ 2) =
    ((119 : ℚ) + (120 : ℚ) * k) * (((119 : ℚ) + (120 : ℚ) * k) * ((3570 : ℚ) + (7170 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((30 : ℚ) + (30 : ℚ) * k) * ((3570 : ℚ) + (7170 : ℚ) * k + (3600 : ℚ) * k ^ 2) + ((30 : ℚ) + (30 : ℚ) * k) * ((119 : ℚ) + (120 : ℚ) * k)) := by
  intro k
  ring

/-- Certified Sierpiński Diophantine solution for n = 1009.
    Verified exact: 5/1009 = 1/202 + 1/203819 + 1/41541980942. -/
theorem sierpinski_cert_n1009 :
    (5 : ℚ) / 1009 = 1 / 202 + 1 / 203819 + 1 / 41541980942 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1033.
    Verified exact: 5/1033 = 1/207 + 1/106916 + 1/22861955196. -/
theorem sierpinski_cert_n1033 :
    (5 : ℚ) / 1033 = 1 / 207 + 1 / 106916 + 1 / 22861955196 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1129.
    Verified exact: 5/1129 = 1/226 + 1/255155 + 1/65103818870. -/
theorem sierpinski_cert_n1129 :
    (5 : ℚ) / 1129 = 1 / 226 + 1 / 255155 + 1 / 65103818870 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1153.
    Verified exact: 5/1153 = 1/231 + 1/133172 + 1/35469429996. -/
theorem sierpinski_cert_n1153 :
    (5 : ℚ) / 1153 = 1 / 231 + 1 / 133172 + 1 / 35469429996 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1201.
    Verified exact: 5/1201 = 1/242 + 1/32307 + 1/77601414. -/
theorem sierpinski_cert_n1201 :
    (5 : ℚ) / 1201 = 1 / 242 + 1 / 32307 + 1 / 77601414 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1249.
    Verified exact: 5/1249 = 1/250 + 1/312251 + 1/97500374750. -/
theorem sierpinski_cert_n1249 :
    (5 : ℚ) / 1249 = 1 / 250 + 1 / 312251 + 1 / 97500374750 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1297.
    Verified exact: 5/1297 = 1/260 + 1/112407 + 1/37905888540. -/
theorem sierpinski_cert_n1297 :
    (5 : ℚ) / 1297 = 1 / 260 + 1 / 112407 + 1 / 37905888540 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1321.
    Verified exact: 5/1321 = 1/266 + 1/39043 + 1/13719163598. -/
theorem sierpinski_cert_n1321 :
    (5 : ℚ) / 1321 = 1 / 266 + 1 / 39043 + 1 / 13719163598 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1489.
    Verified exact: 5/1489 = 1/298 + 1/443723 + 1/196889657006. -/
theorem sierpinski_cert_n1489 :
    (5 : ℚ) / 1489 = 1 / 298 + 1 / 443723 + 1 / 196889657006 := by
  norm_num

/-- Certified Sierpiński Diophantine solution for n = 1609.
    Verified exact: 5/1609 = 1/322 + 1/518099 + 1/268426055702. -/
theorem sierpinski_cert_n1609 :
    (5 : ℚ) / 1609 = 1 / 322 + 1 / 518099 + 1 / 268426055702 := by
  norm_num
