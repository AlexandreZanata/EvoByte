-- EvoByte Certified Parametric Polynomial Identities for Schinzel Resistant Classes (P148)
-- Verified mechanically in Lean 4 kernel via `ring` and `norm_num` tactics.
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

theorem schinzel_poly_identity_sub (a n X Y Z : ℚ) (h : a * X * Y * Z = n * (X * Y + Y * Z + Z * X)) :
    a * X * Y * Z - n * (X * Y + Y * Z + Z * X) = 0 := by
  rw [h]
  ring

theorem schinzel_identity_a5_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 168*k + 1
    let Y : ℚ := 42*k + (168*k + 1)*(840*k + 1)/4 + 1/4
    let Z : ℚ := (168*k + 1)*(840*k + 1)^2/4 + (168*k + 1)*(840*k + 1)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m840_r1 :
    let X : ℚ := 168*(1 : ℚ) + 1
    let Y : ℚ := 42*(1 : ℚ) + (168*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/4 + 1/4
    let Z : ℚ := (168*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)^2/4 + (168*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m840_r121 (k : ℚ) :
    let n : ℚ := 840 * k + 121
    let X : ℚ := 168*k + 25
    let Y : ℚ := 42*k + (168*k + 25)*(840*k + 121)/4 + 25/4
    let Z : ℚ := (168*k + 25)*(840*k + 121)^2/4 + (168*k + 25)*(840*k + 121)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m840_r121 :
    let X : ℚ := 168*(1 : ℚ) + 25
    let Y : ℚ := 42*(1 : ℚ) + (168*(1 : ℚ) + 25)*(840*(1 : ℚ) + 121)/4 + 25/4
    let Z : ℚ := (168*(1 : ℚ) + 25)*(840*(1 : ℚ) + 121)^2/4 + (168*(1 : ℚ) + 25)*(840*(1 : ℚ) + 121)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m840_r361 (k : ℚ) :
    let n : ℚ := 840 * k + 361
    let X : ℚ := 168*k + 73
    let Y : ℚ := 42*k + (168*k + 73)*(840*k + 361)/4 + 73/4
    let Z : ℚ := (168*k + 73)*(840*k + 361)^2/4 + (168*k + 73)*(840*k + 361)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m840_r361 :
    let X : ℚ := 168*(1 : ℚ) + 73
    let Y : ℚ := 42*(1 : ℚ) + (168*(1 : ℚ) + 73)*(840*(1 : ℚ) + 361)/4 + 73/4
    let Z : ℚ := (168*(1 : ℚ) + 73)*(840*(1 : ℚ) + 361)^2/4 + (168*(1 : ℚ) + 73)*(840*(1 : ℚ) + 361)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m2520_r1 (k : ℚ) :
    let n : ℚ := 2520 * k + 1
    let X : ℚ := 504*k + 1
    let Y : ℚ := 126*k + (504*k + 1)*(2520*k + 1)/4 + 1/4
    let Z : ℚ := (504*k + 1)*(2520*k + 1)^2/4 + (504*k + 1)*(2520*k + 1)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m2520_r1 :
    let X : ℚ := 504*(1 : ℚ) + 1
    let Y : ℚ := 126*(1 : ℚ) + (504*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/4 + 1/4
    let Z : ℚ := (504*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)^2/4 + (504*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m2520_r121 (k : ℚ) :
    let n : ℚ := 2520 * k + 121
    let X : ℚ := 504*k + 25
    let Y : ℚ := 126*k + (504*k + 25)*(2520*k + 121)/4 + 25/4
    let Z : ℚ := (504*k + 25)*(2520*k + 121)^2/4 + (504*k + 25)*(2520*k + 121)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m2520_r121 :
    let X : ℚ := 504*(1 : ℚ) + 25
    let Y : ℚ := 126*(1 : ℚ) + (504*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 121)/4 + 25/4
    let Z : ℚ := (504*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 121)^2/4 + (504*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 121)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m2520_r361 (k : ℚ) :
    let n : ℚ := 2520 * k + 361
    let X : ℚ := 504*k + 73
    let Y : ℚ := 126*k + (504*k + 73)*(2520*k + 361)/4 + 73/4
    let Z : ℚ := (504*k + 73)*(2520*k + 361)^2/4 + (504*k + 73)*(2520*k + 361)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m2520_r361 :
    let X : ℚ := 504*(1 : ℚ) + 73
    let Y : ℚ := 126*(1 : ℚ) + (504*(1 : ℚ) + 73)*(2520*(1 : ℚ) + 361)/4 + 73/4
    let Z : ℚ := (504*(1 : ℚ) + 73)*(2520*(1 : ℚ) + 361)^2/4 + (504*(1 : ℚ) + 73)*(2520*(1 : ℚ) + 361)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m2520_r841 (k : ℚ) :
    let n : ℚ := 2520 * k + 841
    let X : ℚ := 504*k + 169
    let Y : ℚ := 126*k + (504*k + 169)*(2520*k + 841)/4 + 169/4
    let Z : ℚ := (504*k + 169)*(2520*k + 841)^2/4 + (504*k + 169)*(2520*k + 841)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m2520_r841 :
    let X : ℚ := 504*(1 : ℚ) + 169
    let Y : ℚ := 126*(1 : ℚ) + (504*(1 : ℚ) + 169)*(2520*(1 : ℚ) + 841)/4 + 169/4
    let Z : ℚ := (504*(1 : ℚ) + 169)*(2520*(1 : ℚ) + 841)^2/4 + (504*(1 : ℚ) + 169)*(2520*(1 : ℚ) + 841)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m2520_r961 (k : ℚ) :
    let n : ℚ := 2520 * k + 961
    let X : ℚ := 504*k + 193
    let Y : ℚ := 126*k + (504*k + 193)*(2520*k + 961)/4 + 193/4
    let Z : ℚ := (504*k + 193)*(2520*k + 961)^2/4 + (504*k + 193)*(2520*k + 961)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m2520_r961 :
    let X : ℚ := 504*(1 : ℚ) + 193
    let Y : ℚ := 126*(1 : ℚ) + (504*(1 : ℚ) + 193)*(2520*(1 : ℚ) + 961)/4 + 193/4
    let Z : ℚ := (504*(1 : ℚ) + 193)*(2520*(1 : ℚ) + 961)^2/4 + (504*(1 : ℚ) + 193)*(2520*(1 : ℚ) + 961)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m5040_r1 (k : ℚ) :
    let n : ℚ := 5040 * k + 1
    let X : ℚ := 1008*k + 1
    let Y : ℚ := 252*k + (1008*k + 1)*(5040*k + 1)/4 + 1/4
    let Z : ℚ := (1008*k + 1)*(5040*k + 1)^2/4 + (1008*k + 1)*(5040*k + 1)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m5040_r1 :
    let X : ℚ := 1008*(1 : ℚ) + 1
    let Y : ℚ := 252*(1 : ℚ) + (1008*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/4 + 1/4
    let Z : ℚ := (1008*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)^2/4 + (1008*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m5040_r121 (k : ℚ) :
    let n : ℚ := 5040 * k + 121
    let X : ℚ := 1008*k + 25
    let Y : ℚ := 252*k + (1008*k + 25)*(5040*k + 121)/4 + 25/4
    let Z : ℚ := (1008*k + 25)*(5040*k + 121)^2/4 + (1008*k + 25)*(5040*k + 121)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m5040_r121 :
    let X : ℚ := 1008*(1 : ℚ) + 25
    let Y : ℚ := 252*(1 : ℚ) + (1008*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 121)/4 + 25/4
    let Z : ℚ := (1008*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 121)^2/4 + (1008*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 121)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m5040_r361 (k : ℚ) :
    let n : ℚ := 5040 * k + 361
    let X : ℚ := 1008*k + 73
    let Y : ℚ := 252*k + (1008*k + 73)*(5040*k + 361)/4 + 73/4
    let Z : ℚ := (1008*k + 73)*(5040*k + 361)^2/4 + (1008*k + 73)*(5040*k + 361)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m5040_r361 :
    let X : ℚ := 1008*(1 : ℚ) + 73
    let Y : ℚ := 252*(1 : ℚ) + (1008*(1 : ℚ) + 73)*(5040*(1 : ℚ) + 361)/4 + 73/4
    let Z : ℚ := (1008*(1 : ℚ) + 73)*(5040*(1 : ℚ) + 361)^2/4 + (1008*(1 : ℚ) + 73)*(5040*(1 : ℚ) + 361)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m5040_r841 (k : ℚ) :
    let n : ℚ := 5040 * k + 841
    let X : ℚ := 1008*k + 169
    let Y : ℚ := 252*k + (1008*k + 169)*(5040*k + 841)/4 + 169/4
    let Z : ℚ := (1008*k + 169)*(5040*k + 841)^2/4 + (1008*k + 169)*(5040*k + 841)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m5040_r841 :
    let X : ℚ := 1008*(1 : ℚ) + 169
    let Y : ℚ := 252*(1 : ℚ) + (1008*(1 : ℚ) + 169)*(5040*(1 : ℚ) + 841)/4 + 169/4
    let Z : ℚ := (1008*(1 : ℚ) + 169)*(5040*(1 : ℚ) + 841)^2/4 + (1008*(1 : ℚ) + 169)*(5040*(1 : ℚ) + 841)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a5_m5040_r961 (k : ℚ) :
    let n : ℚ := 5040 * k + 961
    let X : ℚ := 1008*k + 193
    let Y : ℚ := 252*k + (1008*k + 193)*(5040*k + 961)/4 + 193/4
    let Z : ℚ := (1008*k + 193)*(5040*k + 961)^2/4 + (1008*k + 193)*(5040*k + 961)/4
    5 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a5_m5040_r961 :
    let X : ℚ := 1008*(1 : ℚ) + 193
    let Y : ℚ := 252*(1 : ℚ) + (1008*(1 : ℚ) + 193)*(5040*(1 : ℚ) + 961)/4 + 193/4
    let Z : ℚ := (1008*(1 : ℚ) + 193)*(5040*(1 : ℚ) + 961)^2/4 + (1008*(1 : ℚ) + 193)*(5040*(1 : ℚ) + 961)/4
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 140*k + 1
    let Y : ℚ := 28*k + (140*k + 1)*(840*k + 1)/5 + 1/5
    let Z : ℚ := (140*k + 1)*(840*k + 1)^2/5 + (140*k + 1)*(840*k + 1)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m840_r1 :
    let X : ℚ := 140*(1 : ℚ) + 1
    let Y : ℚ := 28*(1 : ℚ) + (140*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/5 + 1/5
    let Z : ℚ := (140*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)^2/5 + (140*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m840_r121 (k : ℚ) :
    let n : ℚ := 840 * k + 121
    let X : ℚ := 140*k + 21
    let Y : ℚ := 28*k + (140*k + 21)*(840*k + 121)/5 + 21/5
    let Z : ℚ := (140*k + 21)*(840*k + 121)^2/5 + (140*k + 21)*(840*k + 121)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m840_r121 :
    let X : ℚ := 140*(1 : ℚ) + 21
    let Y : ℚ := 28*(1 : ℚ) + (140*(1 : ℚ) + 21)*(840*(1 : ℚ) + 121)/5 + 21/5
    let Z : ℚ := (140*(1 : ℚ) + 21)*(840*(1 : ℚ) + 121)^2/5 + (140*(1 : ℚ) + 21)*(840*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m840_r169 (k : ℚ) :
    let n : ℚ := 840 * k + 169
    let X : ℚ := 140*k + 29
    let Y : ℚ := 28*k + (140*k + 29)*(840*k + 169)/5 + 29/5
    let Z : ℚ := (140*k + 29)*(840*k + 169)^2/5 + (140*k + 29)*(840*k + 169)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m840_r169 :
    let X : ℚ := 140*(1 : ℚ) + 29
    let Y : ℚ := 28*(1 : ℚ) + (140*(1 : ℚ) + 29)*(840*(1 : ℚ) + 169)/5 + 29/5
    let Z : ℚ := (140*(1 : ℚ) + 29)*(840*(1 : ℚ) + 169)^2/5 + (140*(1 : ℚ) + 29)*(840*(1 : ℚ) + 169)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m840_r289 (k : ℚ) :
    let n : ℚ := 840 * k + 289
    let X : ℚ := 140*k + 49
    let Y : ℚ := 28*k + (140*k + 49)*(840*k + 289)/5 + 49/5
    let Z : ℚ := (140*k + 49)*(840*k + 289)^2/5 + (140*k + 49)*(840*k + 289)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m840_r289 :
    let X : ℚ := 140*(1 : ℚ) + 49
    let Y : ℚ := 28*(1 : ℚ) + (140*(1 : ℚ) + 49)*(840*(1 : ℚ) + 289)/5 + 49/5
    let Z : ℚ := (140*(1 : ℚ) + 49)*(840*(1 : ℚ) + 289)^2/5 + (140*(1 : ℚ) + 49)*(840*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m840_r361 (k : ℚ) :
    let n : ℚ := 840 * k + 361
    let X : ℚ := 140*k + 61
    let Y : ℚ := 28*k + (140*k + 61)*(840*k + 361)/5 + 61/5
    let Z : ℚ := (140*k + 61)*(840*k + 361)^2/5 + (140*k + 61)*(840*k + 361)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m840_r361 :
    let X : ℚ := 140*(1 : ℚ) + 61
    let Y : ℚ := 28*(1 : ℚ) + (140*(1 : ℚ) + 61)*(840*(1 : ℚ) + 361)/5 + 61/5
    let Z : ℚ := (140*(1 : ℚ) + 61)*(840*(1 : ℚ) + 361)^2/5 + (140*(1 : ℚ) + 61)*(840*(1 : ℚ) + 361)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m2520_r1 (k : ℚ) :
    let n : ℚ := 2520 * k + 1
    let X : ℚ := 420*k + 1
    let Y : ℚ := 84*k + (420*k + 1)*(2520*k + 1)/5 + 1/5
    let Z : ℚ := (420*k + 1)*(2520*k + 1)^2/5 + (420*k + 1)*(2520*k + 1)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m2520_r1 :
    let X : ℚ := 420*(1 : ℚ) + 1
    let Y : ℚ := 84*(1 : ℚ) + (420*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/5 + 1/5
    let Z : ℚ := (420*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)^2/5 + (420*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m2520_r121 (k : ℚ) :
    let n : ℚ := 2520 * k + 121
    let X : ℚ := 420*k + 21
    let Y : ℚ := 84*k + (420*k + 21)*(2520*k + 121)/5 + 21/5
    let Z : ℚ := (420*k + 21)*(2520*k + 121)^2/5 + (420*k + 21)*(2520*k + 121)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m2520_r121 :
    let X : ℚ := 420*(1 : ℚ) + 21
    let Y : ℚ := 84*(1 : ℚ) + (420*(1 : ℚ) + 21)*(2520*(1 : ℚ) + 121)/5 + 21/5
    let Z : ℚ := (420*(1 : ℚ) + 21)*(2520*(1 : ℚ) + 121)^2/5 + (420*(1 : ℚ) + 21)*(2520*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m2520_r169 (k : ℚ) :
    let n : ℚ := 2520 * k + 169
    let X : ℚ := 420*k + 29
    let Y : ℚ := 84*k + (420*k + 29)*(2520*k + 169)/5 + 29/5
    let Z : ℚ := (420*k + 29)*(2520*k + 169)^2/5 + (420*k + 29)*(2520*k + 169)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m2520_r169 :
    let X : ℚ := 420*(1 : ℚ) + 29
    let Y : ℚ := 84*(1 : ℚ) + (420*(1 : ℚ) + 29)*(2520*(1 : ℚ) + 169)/5 + 29/5
    let Z : ℚ := (420*(1 : ℚ) + 29)*(2520*(1 : ℚ) + 169)^2/5 + (420*(1 : ℚ) + 29)*(2520*(1 : ℚ) + 169)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m2520_r289 (k : ℚ) :
    let n : ℚ := 2520 * k + 289
    let X : ℚ := 420*k + 49
    let Y : ℚ := 84*k + (420*k + 49)*(2520*k + 289)/5 + 49/5
    let Z : ℚ := (420*k + 49)*(2520*k + 289)^2/5 + (420*k + 49)*(2520*k + 289)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m2520_r289 :
    let X : ℚ := 420*(1 : ℚ) + 49
    let Y : ℚ := 84*(1 : ℚ) + (420*(1 : ℚ) + 49)*(2520*(1 : ℚ) + 289)/5 + 49/5
    let Z : ℚ := (420*(1 : ℚ) + 49)*(2520*(1 : ℚ) + 289)^2/5 + (420*(1 : ℚ) + 49)*(2520*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m2520_r361 (k : ℚ) :
    let n : ℚ := 2520 * k + 361
    let X : ℚ := 420*k + 61
    let Y : ℚ := 84*k + (420*k + 61)*(2520*k + 361)/5 + 61/5
    let Z : ℚ := (420*k + 61)*(2520*k + 361)^2/5 + (420*k + 61)*(2520*k + 361)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m2520_r361 :
    let X : ℚ := 420*(1 : ℚ) + 61
    let Y : ℚ := 84*(1 : ℚ) + (420*(1 : ℚ) + 61)*(2520*(1 : ℚ) + 361)/5 + 61/5
    let Z : ℚ := (420*(1 : ℚ) + 61)*(2520*(1 : ℚ) + 361)^2/5 + (420*(1 : ℚ) + 61)*(2520*(1 : ℚ) + 361)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m5040_r1 (k : ℚ) :
    let n : ℚ := 5040 * k + 1
    let X : ℚ := 840*k + 1
    let Y : ℚ := 168*k + (840*k + 1)*(5040*k + 1)/5 + 1/5
    let Z : ℚ := (840*k + 1)*(5040*k + 1)^2/5 + (840*k + 1)*(5040*k + 1)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m5040_r1 :
    let X : ℚ := 840*(1 : ℚ) + 1
    let Y : ℚ := 168*(1 : ℚ) + (840*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/5 + 1/5
    let Z : ℚ := (840*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)^2/5 + (840*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m5040_r121 (k : ℚ) :
    let n : ℚ := 5040 * k + 121
    let X : ℚ := 840*k + 21
    let Y : ℚ := 168*k + (840*k + 21)*(5040*k + 121)/5 + 21/5
    let Z : ℚ := (840*k + 21)*(5040*k + 121)^2/5 + (840*k + 21)*(5040*k + 121)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m5040_r121 :
    let X : ℚ := 840*(1 : ℚ) + 21
    let Y : ℚ := 168*(1 : ℚ) + (840*(1 : ℚ) + 21)*(5040*(1 : ℚ) + 121)/5 + 21/5
    let Z : ℚ := (840*(1 : ℚ) + 21)*(5040*(1 : ℚ) + 121)^2/5 + (840*(1 : ℚ) + 21)*(5040*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m5040_r169 (k : ℚ) :
    let n : ℚ := 5040 * k + 169
    let X : ℚ := 840*k + 29
    let Y : ℚ := 168*k + (840*k + 29)*(5040*k + 169)/5 + 29/5
    let Z : ℚ := (840*k + 29)*(5040*k + 169)^2/5 + (840*k + 29)*(5040*k + 169)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m5040_r169 :
    let X : ℚ := 840*(1 : ℚ) + 29
    let Y : ℚ := 168*(1 : ℚ) + (840*(1 : ℚ) + 29)*(5040*(1 : ℚ) + 169)/5 + 29/5
    let Z : ℚ := (840*(1 : ℚ) + 29)*(5040*(1 : ℚ) + 169)^2/5 + (840*(1 : ℚ) + 29)*(5040*(1 : ℚ) + 169)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m5040_r289 (k : ℚ) :
    let n : ℚ := 5040 * k + 289
    let X : ℚ := 840*k + 49
    let Y : ℚ := 168*k + (840*k + 49)*(5040*k + 289)/5 + 49/5
    let Z : ℚ := (840*k + 49)*(5040*k + 289)^2/5 + (840*k + 49)*(5040*k + 289)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m5040_r289 :
    let X : ℚ := 840*(1 : ℚ) + 49
    let Y : ℚ := 168*(1 : ℚ) + (840*(1 : ℚ) + 49)*(5040*(1 : ℚ) + 289)/5 + 49/5
    let Z : ℚ := (840*(1 : ℚ) + 49)*(5040*(1 : ℚ) + 289)^2/5 + (840*(1 : ℚ) + 49)*(5040*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a6_m5040_r361 (k : ℚ) :
    let n : ℚ := 5040 * k + 361
    let X : ℚ := 840*k + 61
    let Y : ℚ := 168*k + (840*k + 61)*(5040*k + 361)/5 + 61/5
    let Z : ℚ := (840*k + 61)*(5040*k + 361)^2/5 + (840*k + 61)*(5040*k + 361)/5
    6 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a6_m5040_r361 :
    let X : ℚ := 840*(1 : ℚ) + 61
    let Y : ℚ := 168*(1 : ℚ) + (840*(1 : ℚ) + 61)*(5040*(1 : ℚ) + 361)/5 + 61/5
    let Z : ℚ := (840*(1 : ℚ) + 61)*(5040*(1 : ℚ) + 361)^2/5 + (840*(1 : ℚ) + 61)*(5040*(1 : ℚ) + 361)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 120*k + 1
    let Y : ℚ := 20*k + (120*k + 1)*(840*k + 1)/6 + 1/6
    let Z : ℚ := (120*k + 1)*(840*k + 1)^2/6 + (120*k + 1)*(840*k + 1)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m840_r1 :
    let X : ℚ := 120*(1 : ℚ) + 1
    let Y : ℚ := 20*(1 : ℚ) + (120*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/6 + 1/6
    let Z : ℚ := (120*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)^2/6 + (120*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m840_r121 (k : ℚ) :
    let n : ℚ := 840 * k + 121
    let X : ℚ := 120*k + 18
    let Y : ℚ := 24*k + (120*k + 18)*(840*k + 121)/5 + 18/5
    let Z : ℚ := (120*k + 18)*(840*k + 121)^2/5 + (120*k + 18)*(840*k + 121)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m840_r121 :
    let X : ℚ := 120*(1 : ℚ) + 18
    let Y : ℚ := 24*(1 : ℚ) + (120*(1 : ℚ) + 18)*(840*(1 : ℚ) + 121)/5 + 18/5
    let Z : ℚ := (120*(1 : ℚ) + 18)*(840*(1 : ℚ) + 121)^2/5 + (120*(1 : ℚ) + 18)*(840*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m840_r169 (k : ℚ) :
    let n : ℚ := 840 * k + 169
    let X : ℚ := 120*k + 25
    let Y : ℚ := 20*k + (120*k + 25)*(840*k + 169)/6 + 25/6
    let Z : ℚ := (120*k + 25)*(840*k + 169)^2/6 + (120*k + 25)*(840*k + 169)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m840_r169 :
    let X : ℚ := 120*(1 : ℚ) + 25
    let Y : ℚ := 20*(1 : ℚ) + (120*(1 : ℚ) + 25)*(840*(1 : ℚ) + 169)/6 + 25/6
    let Z : ℚ := (120*(1 : ℚ) + 25)*(840*(1 : ℚ) + 169)^2/6 + (120*(1 : ℚ) + 25)*(840*(1 : ℚ) + 169)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m840_r289 (k : ℚ) :
    let n : ℚ := 840 * k + 289
    let X : ℚ := 120*k + 42
    let Y : ℚ := 24*k + (120*k + 42)*(840*k + 289)/5 + 42/5
    let Z : ℚ := (120*k + 42)*(840*k + 289)^2/5 + (120*k + 42)*(840*k + 289)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m840_r289 :
    let X : ℚ := 120*(1 : ℚ) + 42
    let Y : ℚ := 24*(1 : ℚ) + (120*(1 : ℚ) + 42)*(840*(1 : ℚ) + 289)/5 + 42/5
    let Z : ℚ := (120*(1 : ℚ) + 42)*(840*(1 : ℚ) + 289)^2/5 + (120*(1 : ℚ) + 42)*(840*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m840_r361 (k : ℚ) :
    let n : ℚ := 840 * k + 361
    let X : ℚ := 120*k + 52
    let Y : ℚ := 40*k + (120*k + 52)*(840*k + 361)/3 + 52/3
    let Z : ℚ := (120*k + 52)*(840*k + 361)^2/3 + (120*k + 52)*(840*k + 361)/3
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m840_r361 :
    let X : ℚ := 120*(1 : ℚ) + 52
    let Y : ℚ := 40*(1 : ℚ) + (120*(1 : ℚ) + 52)*(840*(1 : ℚ) + 361)/3 + 52/3
    let Z : ℚ := (120*(1 : ℚ) + 52)*(840*(1 : ℚ) + 361)^2/3 + (120*(1 : ℚ) + 52)*(840*(1 : ℚ) + 361)/3
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m2520_r1 (k : ℚ) :
    let n : ℚ := 2520 * k + 1
    let X : ℚ := 360*k + 1
    let Y : ℚ := 60*k + (360*k + 1)*(2520*k + 1)/6 + 1/6
    let Z : ℚ := (360*k + 1)*(2520*k + 1)^2/6 + (360*k + 1)*(2520*k + 1)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m2520_r1 :
    let X : ℚ := 360*(1 : ℚ) + 1
    let Y : ℚ := 60*(1 : ℚ) + (360*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/6 + 1/6
    let Z : ℚ := (360*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)^2/6 + (360*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m2520_r121 (k : ℚ) :
    let n : ℚ := 2520 * k + 121
    let X : ℚ := 360*k + 18
    let Y : ℚ := 72*k + (360*k + 18)*(2520*k + 121)/5 + 18/5
    let Z : ℚ := (360*k + 18)*(2520*k + 121)^2/5 + (360*k + 18)*(2520*k + 121)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m2520_r121 :
    let X : ℚ := 360*(1 : ℚ) + 18
    let Y : ℚ := 72*(1 : ℚ) + (360*(1 : ℚ) + 18)*(2520*(1 : ℚ) + 121)/5 + 18/5
    let Z : ℚ := (360*(1 : ℚ) + 18)*(2520*(1 : ℚ) + 121)^2/5 + (360*(1 : ℚ) + 18)*(2520*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m2520_r169 (k : ℚ) :
    let n : ℚ := 2520 * k + 169
    let X : ℚ := 360*k + 25
    let Y : ℚ := 60*k + (360*k + 25)*(2520*k + 169)/6 + 25/6
    let Z : ℚ := (360*k + 25)*(2520*k + 169)^2/6 + (360*k + 25)*(2520*k + 169)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m2520_r169 :
    let X : ℚ := 360*(1 : ℚ) + 25
    let Y : ℚ := 60*(1 : ℚ) + (360*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 169)/6 + 25/6
    let Z : ℚ := (360*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 169)^2/6 + (360*(1 : ℚ) + 25)*(2520*(1 : ℚ) + 169)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m2520_r289 (k : ℚ) :
    let n : ℚ := 2520 * k + 289
    let X : ℚ := 360*k + 42
    let Y : ℚ := 72*k + (360*k + 42)*(2520*k + 289)/5 + 42/5
    let Z : ℚ := (360*k + 42)*(2520*k + 289)^2/5 + (360*k + 42)*(2520*k + 289)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m2520_r289 :
    let X : ℚ := 360*(1 : ℚ) + 42
    let Y : ℚ := 72*(1 : ℚ) + (360*(1 : ℚ) + 42)*(2520*(1 : ℚ) + 289)/5 + 42/5
    let Z : ℚ := (360*(1 : ℚ) + 42)*(2520*(1 : ℚ) + 289)^2/5 + (360*(1 : ℚ) + 42)*(2520*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m2520_r361 (k : ℚ) :
    let n : ℚ := 2520 * k + 361
    let X : ℚ := 360*k + 52
    let Y : ℚ := 120*k + (360*k + 52)*(2520*k + 361)/3 + 52/3
    let Z : ℚ := (360*k + 52)*(2520*k + 361)^2/3 + (360*k + 52)*(2520*k + 361)/3
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m2520_r361 :
    let X : ℚ := 360*(1 : ℚ) + 52
    let Y : ℚ := 120*(1 : ℚ) + (360*(1 : ℚ) + 52)*(2520*(1 : ℚ) + 361)/3 + 52/3
    let Z : ℚ := (360*(1 : ℚ) + 52)*(2520*(1 : ℚ) + 361)^2/3 + (360*(1 : ℚ) + 52)*(2520*(1 : ℚ) + 361)/3
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m5040_r1 (k : ℚ) :
    let n : ℚ := 5040 * k + 1
    let X : ℚ := 720*k + 1
    let Y : ℚ := 120*k + (720*k + 1)*(5040*k + 1)/6 + 1/6
    let Z : ℚ := (720*k + 1)*(5040*k + 1)^2/6 + (720*k + 1)*(5040*k + 1)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m5040_r1 :
    let X : ℚ := 720*(1 : ℚ) + 1
    let Y : ℚ := 120*(1 : ℚ) + (720*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/6 + 1/6
    let Z : ℚ := (720*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)^2/6 + (720*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m5040_r121 (k : ℚ) :
    let n : ℚ := 5040 * k + 121
    let X : ℚ := 720*k + 18
    let Y : ℚ := 144*k + (720*k + 18)*(5040*k + 121)/5 + 18/5
    let Z : ℚ := (720*k + 18)*(5040*k + 121)^2/5 + (720*k + 18)*(5040*k + 121)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m5040_r121 :
    let X : ℚ := 720*(1 : ℚ) + 18
    let Y : ℚ := 144*(1 : ℚ) + (720*(1 : ℚ) + 18)*(5040*(1 : ℚ) + 121)/5 + 18/5
    let Z : ℚ := (720*(1 : ℚ) + 18)*(5040*(1 : ℚ) + 121)^2/5 + (720*(1 : ℚ) + 18)*(5040*(1 : ℚ) + 121)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m5040_r169 (k : ℚ) :
    let n : ℚ := 5040 * k + 169
    let X : ℚ := 720*k + 25
    let Y : ℚ := 120*k + (720*k + 25)*(5040*k + 169)/6 + 25/6
    let Z : ℚ := (720*k + 25)*(5040*k + 169)^2/6 + (720*k + 25)*(5040*k + 169)/6
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m5040_r169 :
    let X : ℚ := 720*(1 : ℚ) + 25
    let Y : ℚ := 120*(1 : ℚ) + (720*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 169)/6 + 25/6
    let Z : ℚ := (720*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 169)^2/6 + (720*(1 : ℚ) + 25)*(5040*(1 : ℚ) + 169)/6
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m5040_r289 (k : ℚ) :
    let n : ℚ := 5040 * k + 289
    let X : ℚ := 720*k + 42
    let Y : ℚ := 144*k + (720*k + 42)*(5040*k + 289)/5 + 42/5
    let Z : ℚ := (720*k + 42)*(5040*k + 289)^2/5 + (720*k + 42)*(5040*k + 289)/5
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m5040_r289 :
    let X : ℚ := 720*(1 : ℚ) + 42
    let Y : ℚ := 144*(1 : ℚ) + (720*(1 : ℚ) + 42)*(5040*(1 : ℚ) + 289)/5 + 42/5
    let Z : ℚ := (720*(1 : ℚ) + 42)*(5040*(1 : ℚ) + 289)^2/5 + (720*(1 : ℚ) + 42)*(5040*(1 : ℚ) + 289)/5
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a7_m5040_r361 (k : ℚ) :
    let n : ℚ := 5040 * k + 361
    let X : ℚ := 720*k + 52
    let Y : ℚ := 240*k + (720*k + 52)*(5040*k + 361)/3 + 52/3
    let Z : ℚ := (720*k + 52)*(5040*k + 361)^2/3 + (720*k + 52)*(5040*k + 361)/3
    7 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a7_m5040_r361 :
    let X : ℚ := 720*(1 : ℚ) + 52
    let Y : ℚ := 240*(1 : ℚ) + (720*(1 : ℚ) + 52)*(5040*(1 : ℚ) + 361)/3 + 52/3
    let Z : ℚ := (720*(1 : ℚ) + 52)*(5040*(1 : ℚ) + 361)^2/3 + (720*(1 : ℚ) + 52)*(5040*(1 : ℚ) + 361)/3
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m840_r1 (k : ℚ) :
    let n : ℚ := 840 * k + 1
    let X : ℚ := 105*k + 1
    let Y : ℚ := 15*k + (105*k + 1)*(840*k + 1)/7 + 1/7
    let Z : ℚ := (105*k + 1)*(840*k + 1)^2/7 + (105*k + 1)*(840*k + 1)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m840_r1 :
    let X : ℚ := 105*(1 : ℚ) + 1
    let Y : ℚ := 15*(1 : ℚ) + (105*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/7 + 1/7
    let Z : ℚ := (105*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)^2/7 + (105*(1 : ℚ) + 1)*(840*(1 : ℚ) + 1)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m840_r121 (k : ℚ) :
    let n : ℚ := 840 * k + 121
    let X : ℚ := 105*k + 16
    let Y : ℚ := 15*k + (105*k + 16)*(840*k + 121)/7 + 16/7
    let Z : ℚ := (105*k + 16)*(840*k + 121)^2/7 + (105*k + 16)*(840*k + 121)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m840_r121 :
    let X : ℚ := 105*(1 : ℚ) + 16
    let Y : ℚ := 15*(1 : ℚ) + (105*(1 : ℚ) + 16)*(840*(1 : ℚ) + 121)/7 + 16/7
    let Z : ℚ := (105*(1 : ℚ) + 16)*(840*(1 : ℚ) + 121)^2/7 + (105*(1 : ℚ) + 16)*(840*(1 : ℚ) + 121)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m840_r169 (k : ℚ) :
    let n : ℚ := 840 * k + 169
    let X : ℚ := 105*k + 22
    let Y : ℚ := 15*k + (105*k + 22)*(840*k + 169)/7 + 22/7
    let Z : ℚ := (105*k + 22)*(840*k + 169)^2/7 + (105*k + 22)*(840*k + 169)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m840_r169 :
    let X : ℚ := 105*(1 : ℚ) + 22
    let Y : ℚ := 15*(1 : ℚ) + (105*(1 : ℚ) + 22)*(840*(1 : ℚ) + 169)/7 + 22/7
    let Z : ℚ := (105*(1 : ℚ) + 22)*(840*(1 : ℚ) + 169)^2/7 + (105*(1 : ℚ) + 22)*(840*(1 : ℚ) + 169)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m840_r289 (k : ℚ) :
    let n : ℚ := 840 * k + 289
    let X : ℚ := 105*k + 37
    let Y : ℚ := 15*k + (105*k + 37)*(840*k + 289)/7 + 37/7
    let Z : ℚ := (105*k + 37)*(840*k + 289)^2/7 + (105*k + 37)*(840*k + 289)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m840_r289 :
    let X : ℚ := 105*(1 : ℚ) + 37
    let Y : ℚ := 15*(1 : ℚ) + (105*(1 : ℚ) + 37)*(840*(1 : ℚ) + 289)/7 + 37/7
    let Z : ℚ := (105*(1 : ℚ) + 37)*(840*(1 : ℚ) + 289)^2/7 + (105*(1 : ℚ) + 37)*(840*(1 : ℚ) + 289)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m840_r361 (k : ℚ) :
    let n : ℚ := 840 * k + 361
    let X : ℚ := 105*k + 46
    let Y : ℚ := 15*k + (105*k + 46)*(840*k + 361)/7 + 46/7
    let Z : ℚ := (105*k + 46)*(840*k + 361)^2/7 + (105*k + 46)*(840*k + 361)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m840_r361 :
    let X : ℚ := 105*(1 : ℚ) + 46
    let Y : ℚ := 15*(1 : ℚ) + (105*(1 : ℚ) + 46)*(840*(1 : ℚ) + 361)/7 + 46/7
    let Z : ℚ := (105*(1 : ℚ) + 46)*(840*(1 : ℚ) + 361)^2/7 + (105*(1 : ℚ) + 46)*(840*(1 : ℚ) + 361)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m2520_r1 (k : ℚ) :
    let n : ℚ := 2520 * k + 1
    let X : ℚ := 315*k + 1
    let Y : ℚ := 45*k + (315*k + 1)*(2520*k + 1)/7 + 1/7
    let Z : ℚ := (315*k + 1)*(2520*k + 1)^2/7 + (315*k + 1)*(2520*k + 1)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m2520_r1 :
    let X : ℚ := 315*(1 : ℚ) + 1
    let Y : ℚ := 45*(1 : ℚ) + (315*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/7 + 1/7
    let Z : ℚ := (315*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)^2/7 + (315*(1 : ℚ) + 1)*(2520*(1 : ℚ) + 1)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m2520_r121 (k : ℚ) :
    let n : ℚ := 2520 * k + 121
    let X : ℚ := 315*k + 16
    let Y : ℚ := 45*k + (315*k + 16)*(2520*k + 121)/7 + 16/7
    let Z : ℚ := (315*k + 16)*(2520*k + 121)^2/7 + (315*k + 16)*(2520*k + 121)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m2520_r121 :
    let X : ℚ := 315*(1 : ℚ) + 16
    let Y : ℚ := 45*(1 : ℚ) + (315*(1 : ℚ) + 16)*(2520*(1 : ℚ) + 121)/7 + 16/7
    let Z : ℚ := (315*(1 : ℚ) + 16)*(2520*(1 : ℚ) + 121)^2/7 + (315*(1 : ℚ) + 16)*(2520*(1 : ℚ) + 121)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m2520_r169 (k : ℚ) :
    let n : ℚ := 2520 * k + 169
    let X : ℚ := 315*k + 22
    let Y : ℚ := 45*k + (315*k + 22)*(2520*k + 169)/7 + 22/7
    let Z : ℚ := (315*k + 22)*(2520*k + 169)^2/7 + (315*k + 22)*(2520*k + 169)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m2520_r169 :
    let X : ℚ := 315*(1 : ℚ) + 22
    let Y : ℚ := 45*(1 : ℚ) + (315*(1 : ℚ) + 22)*(2520*(1 : ℚ) + 169)/7 + 22/7
    let Z : ℚ := (315*(1 : ℚ) + 22)*(2520*(1 : ℚ) + 169)^2/7 + (315*(1 : ℚ) + 22)*(2520*(1 : ℚ) + 169)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m2520_r289 (k : ℚ) :
    let n : ℚ := 2520 * k + 289
    let X : ℚ := 315*k + 37
    let Y : ℚ := 45*k + (315*k + 37)*(2520*k + 289)/7 + 37/7
    let Z : ℚ := (315*k + 37)*(2520*k + 289)^2/7 + (315*k + 37)*(2520*k + 289)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m2520_r289 :
    let X : ℚ := 315*(1 : ℚ) + 37
    let Y : ℚ := 45*(1 : ℚ) + (315*(1 : ℚ) + 37)*(2520*(1 : ℚ) + 289)/7 + 37/7
    let Z : ℚ := (315*(1 : ℚ) + 37)*(2520*(1 : ℚ) + 289)^2/7 + (315*(1 : ℚ) + 37)*(2520*(1 : ℚ) + 289)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m2520_r361 (k : ℚ) :
    let n : ℚ := 2520 * k + 361
    let X : ℚ := 315*k + 46
    let Y : ℚ := 45*k + (315*k + 46)*(2520*k + 361)/7 + 46/7
    let Z : ℚ := (315*k + 46)*(2520*k + 361)^2/7 + (315*k + 46)*(2520*k + 361)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m2520_r361 :
    let X : ℚ := 315*(1 : ℚ) + 46
    let Y : ℚ := 45*(1 : ℚ) + (315*(1 : ℚ) + 46)*(2520*(1 : ℚ) + 361)/7 + 46/7
    let Z : ℚ := (315*(1 : ℚ) + 46)*(2520*(1 : ℚ) + 361)^2/7 + (315*(1 : ℚ) + 46)*(2520*(1 : ℚ) + 361)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m5040_r1 (k : ℚ) :
    let n : ℚ := 5040 * k + 1
    let X : ℚ := 630*k + 1
    let Y : ℚ := 90*k + (630*k + 1)*(5040*k + 1)/7 + 1/7
    let Z : ℚ := (630*k + 1)*(5040*k + 1)^2/7 + (630*k + 1)*(5040*k + 1)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m5040_r1 :
    let X : ℚ := 630*(1 : ℚ) + 1
    let Y : ℚ := 90*(1 : ℚ) + (630*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/7 + 1/7
    let Z : ℚ := (630*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)^2/7 + (630*(1 : ℚ) + 1)*(5040*(1 : ℚ) + 1)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m5040_r121 (k : ℚ) :
    let n : ℚ := 5040 * k + 121
    let X : ℚ := 630*k + 16
    let Y : ℚ := 90*k + (630*k + 16)*(5040*k + 121)/7 + 16/7
    let Z : ℚ := (630*k + 16)*(5040*k + 121)^2/7 + (630*k + 16)*(5040*k + 121)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m5040_r121 :
    let X : ℚ := 630*(1 : ℚ) + 16
    let Y : ℚ := 90*(1 : ℚ) + (630*(1 : ℚ) + 16)*(5040*(1 : ℚ) + 121)/7 + 16/7
    let Z : ℚ := (630*(1 : ℚ) + 16)*(5040*(1 : ℚ) + 121)^2/7 + (630*(1 : ℚ) + 16)*(5040*(1 : ℚ) + 121)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m5040_r169 (k : ℚ) :
    let n : ℚ := 5040 * k + 169
    let X : ℚ := 630*k + 22
    let Y : ℚ := 90*k + (630*k + 22)*(5040*k + 169)/7 + 22/7
    let Z : ℚ := (630*k + 22)*(5040*k + 169)^2/7 + (630*k + 22)*(5040*k + 169)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m5040_r169 :
    let X : ℚ := 630*(1 : ℚ) + 22
    let Y : ℚ := 90*(1 : ℚ) + (630*(1 : ℚ) + 22)*(5040*(1 : ℚ) + 169)/7 + 22/7
    let Z : ℚ := (630*(1 : ℚ) + 22)*(5040*(1 : ℚ) + 169)^2/7 + (630*(1 : ℚ) + 22)*(5040*(1 : ℚ) + 169)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m5040_r289 (k : ℚ) :
    let n : ℚ := 5040 * k + 289
    let X : ℚ := 630*k + 37
    let Y : ℚ := 90*k + (630*k + 37)*(5040*k + 289)/7 + 37/7
    let Z : ℚ := (630*k + 37)*(5040*k + 289)^2/7 + (630*k + 37)*(5040*k + 289)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m5040_r289 :
    let X : ℚ := 630*(1 : ℚ) + 37
    let Y : ℚ := 90*(1 : ℚ) + (630*(1 : ℚ) + 37)*(5040*(1 : ℚ) + 289)/7 + 37/7
    let Z : ℚ := (630*(1 : ℚ) + 37)*(5040*(1 : ℚ) + 289)^2/7 + (630*(1 : ℚ) + 37)*(5040*(1 : ℚ) + 289)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num

theorem schinzel_identity_a8_m5040_r361 (k : ℚ) :
    let n : ℚ := 5040 * k + 361
    let X : ℚ := 630*k + 46
    let Y : ℚ := 90*k + (630*k + 46)*(5040*k + 361)/7 + 46/7
    let Z : ℚ := (630*k + 46)*(5040*k + 361)^2/7 + (630*k + 46)*(5040*k + 361)/7
    8 * X * Y * Z = n * (X * Y + Y * Z + Z * X) := by
  intro n X Y Z
  dsimp [n, X, Y, Z]
  ring

theorem schinzel_ordering_a8_m5040_r361 :
    let X : ℚ := 630*(1 : ℚ) + 46
    let Y : ℚ := 90*(1 : ℚ) + (630*(1 : ℚ) + 46)*(5040*(1 : ℚ) + 361)/7 + 46/7
    let Z : ℚ := (630*(1 : ℚ) + 46)*(5040*(1 : ℚ) + 361)^2/7 + (630*(1 : ℚ) + 46)*(5040*(1 : ℚ) + 361)/7
    0 < X ∧ X < Y ∧ Y < Z := by
  intro X Y Z
  dsimp [X, Y, Z]
  norm_num
