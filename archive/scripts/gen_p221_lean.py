#!/usr/bin/env python3
"""Generate BivariateReal.lean formal Lean 4 module for P221.

Generates ground-truth binary check matrix lists and formal Lean lemmas
directly over concrete mathematical representations.
"""

from __future__ import annotations

import itertools
from pathlib import Path


def build(
    l: int, m: int, a_exp: list[tuple[int, int]], b_exp: list[tuple[int, int]]
) -> tuple[list[list[int]], list[list[int]]]:
    n = l * m

    def idx(i: int, j: int) -> int:
        return (i % l) * m + (j % m)

    def mat(p_exp: list[tuple[int, int]], transpose: bool = False) -> list[list[int]]:
        matrix = [[0] * n for _ in range(n)]
        for a, b in p_exp:
            for i in range(l):
                for j in range(m):
                    r, c = idx(i, j), idx(i + a, j + b)
                    if transpose:
                        matrix[c][r] ^= 1
                    else:
                        matrix[r][c] ^= 1
        return matrix

    am, bm = mat(a_exp), mat(b_exp)
    at, bt = mat(a_exp, transpose=True), mat(b_exp, transpose=True)
    hx = [am[i] + bm[i] for i in range(n)]
    hz = [bt[i] + at[i] for i in range(n)]
    return hx, hz


def bits(rows: list[list[int]]) -> list[int]:
    return [int("".join(map(str, r)), 2) for r in rows]


def par(x: int) -> int:
    return bin(x).count("1") & 1


def basis_of(vs: list[int]) -> list[int]:
    basis: list[int] = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def in_span(v: int, basis: list[int]) -> bool:
    for b in basis:
        v = min(v, v ^ b)
    return v == 0


def find_logical_witness(
    hx_mat: list[list[int]], hz_mat: list[list[int]], n_qubits: int
) -> tuple[int, int]:
    hx, hz = bits(hx_mat), bits(hz_mat)
    bx, bz = basis_of(hx), basis_of(hz)
    for w in range(1, n_qubits + 1):
        for s in itertools.combinations(range(n_qubits), w):
            e = sum(1 << (n_qubits - 1 - idx) for idx in s)
            if all(par(e & h) == 0 for h in hz) and not in_span(e, bx):
                return w, e
            if all(par(e & h) == 0 for h in hx) and not in_span(e, bz):
                return w, e
    raise RuntimeError("No logical operator found")


def generate_lean_code() -> str:
    # 1. Target [[20, 2, 6]]
    l20, m20 = 5, 2
    a20 = [(0, 0), (0, 1), (1, 1), (2, 1)]
    b20 = [(0, 1), (1, 1), (2, 0), (2, 1)]
    hx20_mat, hz20_mat = build(l20, m20, a20, b20)
    hx20_bits = bits(hx20_mat)
    hz20_bits = bits(hz20_mat)
    w20, wit20 = find_logical_witness(hx20_mat, hz20_mat, 20)

    # 2. Target [[16, 2, 4]]
    l16, m16 = 2, 4
    a16 = [(0, 0), (0, 2), (1, 0), (1, 3)]
    b16 = [(0, 1), (1, 0), (1, 2), (1, 3)]
    hx16_mat, hz16_mat = build(l16, m16, a16, b16)
    hx16_bits = bits(hx16_mat)
    hz16_bits = bits(hz16_mat)
    w16, wit16 = find_logical_witness(hx16_mat, hz16_mat, 16)

    hx20_str = ", ".join(str(x) for x in hx20_bits)
    hz20_str = ", ".join(str(x) for x in hz20_bits)
    hx16_str = ", ".join(str(x) for x in hx16_bits)
    hz16_str = ", ".join(str(x) for x in hz16_bits)

    return f"""/-!
# Bivariate Real Formal Verification in Lean 4 (P221)

Rigorous formal verification of real bivariate bicycle codes:
1. [[20, 2, 6]] code over F_2[Z_5 x Z_2]:
   - rank(HX) = 9, rank(HZ) = 9 -> k = 2
   - Pairwise binary symplectic commutativity: HX * HZ^T = 0
   - No undetectable logical operator of weight w <= 5 (lowMasks count 21699) -> d >= 6
   - Concrete logical witness of weight 6 -> d <= 6, certifying exact distance d = 6.
2. [[16, 2, 4]] code over F_2[Z_2 x Z_4]:
   - rank(HX) = 7, rank(HZ) = 7 -> k = 2
   - Pairwise binary symplectic commutativity: HX * HZ^T = 0
   - No undetectable logical operator of weight w <= 3 (lowMasks count 696) -> d >= 4
   - Concrete logical witness of weight 4 -> d <= 4, certifying exact distance d = 4.

Certified by the Lean 4 kernel with standard axioms [propext, Classical.choice, Quot.sound].
-/

namespace EvoByte.BivariateReal

-- ===========================================================================
-- Common GF(2) Vector and Linear Algebra Definitions
-- ===========================================================================

def insertVec (basis : List Nat) (v : Nat) : List Nat :=
  let w := basis.foldl (fun v b => min v (v ^^^ b)) v
  if w = 0 then basis else basis ++ [w]

def gf2Rank (rows : List Nat) : Nat :=
  (rows.foldl insertVec []).length

def inSpan (basis : List Nat) (v : Nat) : Bool :=
  (basis.foldl (fun v b => min v (v ^^^ b)) v) == 0

def ofWeight : Nat → Nat → List Nat
  | _, 0 => [0]
  | 0, _+1 => []
  | n+1, w+1 => ofWeight n (w+1) ++ (ofWeight n w).map (· ||| (1 <<< n))

-- ===========================================================================
-- 1. Bivariate Bicycle Code [[20, 2, 6]] over F_2[Z_5 x Z_2]
-- ===========================================================================

def hx20 : List Nat := [{hx20_str}]
def hz20 : List Nat := [{hz20_str}]

def pc20 (x : Nat) : Nat := (List.range 20).foldl (fun a i => a + (x >>> i) % 2) 0
def par20 (x : Nat) : Nat := pc20 x % 2

def bx20 : List Nat := hx20.foldl insertVec []
def bz20 : List Nat := hz20.foldl insertVec []

/-- e is a logical operator if it commutes with HZ and is outside rowspace(HX),
or commutes with HX and is outside rowspace(HZ). -/
def isLogical20 (e : Nat) : Bool :=
  (hz20.all (fun h => par20 (e &&& h) == 0) && !(inSpan bx20 e)) ||
  (hx20.all (fun h => par20 (e &&& h) == 0) && !(inSpan bz20 e))

def lowMasks20 : List Nat :=
  (List.range 6).foldl (fun acc w => acc ++ (if w = 0 then [] else ofWeight 20 w)) []

def wit20 : Nat := {wit20}

-- SCOPE: kernel-checked rank of HX matrix
theorem rank_hx20 : gf2Rank hx20 = 9 := by decide

-- SCOPE: kernel-checked rank of HZ matrix
theorem rank_hz20 : gf2Rank hz20 = 9 := by decide

-- SCOPE: kernel-checked binary symplectic commutativity of 20-qubit code
theorem commute20 : hx20.all (fun a => hz20.all (fun b => par20 (a &&& b) == 0)) = true := by decide

-- SCOPE: exact count of candidate error vectors with weight 1 <= w <= 5
set_option maxRecDepth 100000 in
theorem lowmasks20_count : lowMasks20.length = 21699 := by decide +kernel

-- SCOPE: distance lower bound d >= 6 (absence of undetectable logicals with weight <= 5)
set_option maxRecDepth 100000 in
theorem no_logical_weight_le5_20 : lowMasks20.all (fun e => !isLogical20 e) = true := by decide +kernel

-- SCOPE: distance upper bound d <= 6 (witness logical of weight 6 exists)
theorem logical_weight6_20 : isLogical20 wit20 = true ∧ pc20 wit20 = {w20} := by decide

#print axioms rank_hx20
#print axioms rank_hz20
#print axioms commute20
#print axioms no_logical_weight_le5_20
#print axioms logical_weight6_20

-- ===========================================================================
-- 2. Bivariate Bicycle Code [[16, 2, 4]] over F_2[Z_2 x Z_4]
-- ===========================================================================

def hx16 : List Nat := [{hx16_str}]
def hz16 : List Nat := [{hz16_str}]

def pc16 (x : Nat) : Nat := (List.range 16).foldl (fun a i => a + (x >>> i) % 2) 0
def par16 (x : Nat) : Nat := pc16 x % 2

def bx16 : List Nat := hx16.foldl insertVec []
def bz16 : List Nat := hz16.foldl insertVec []

def isLogical16 (e : Nat) : Bool :=
  (hz16.all (fun h => par16 (e &&& h) == 0) && !(inSpan bx16 e)) ||
  (hx16.all (fun h => par16 (e &&& h) == 0) && !(inSpan bz16 e))

def lowMasks16 : List Nat :=
  (List.range 4).foldl (fun acc w => acc ++ (if w = 0 then [] else ofWeight 16 w)) []

def wit16 : Nat := {wit16}

-- SCOPE: kernel-checked rank of HX matrix
theorem rank_hx16 : gf2Rank hx16 = 7 := by decide

-- SCOPE: kernel-checked rank of HZ matrix
theorem rank_hz16 : gf2Rank hz16 = 7 := by decide

-- SCOPE: kernel-checked binary symplectic commutativity of 16-qubit code
theorem commute16 : hx16.all (fun a => hz16.all (fun b => par16 (a &&& b) == 0)) = true := by decide

-- SCOPE: exact count of candidate error vectors with weight 1 <= w <= 3 (16 + 120 + 560 = 696)
set_option maxRecDepth 100000 in
theorem lowmasks16_count : lowMasks16.length = 696 := by decide +kernel

-- SCOPE: distance lower bound d >= 4 (absence of undetectable logicals with weight <= 3)
set_option maxRecDepth 100000 in
theorem no_logical_weight_le3_16 : lowMasks16.all (fun e => !isLogical16 e) = true := by decide +kernel

-- SCOPE: distance upper bound d <= 4 (witness logical of weight 4 exists)
theorem logical_weight4_16 : isLogical16 wit16 = true ∧ pc16 wit16 = {w16} := by decide

#print axioms rank_hx16
#print axioms rank_hz16
#print axioms commute16
#print axioms no_logical_weight_le3_16
#print axioms logical_weight4_16

end EvoByte.BivariateReal
"""


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    target_lean = repo_root / "lean_proofs" / "Generated" / "BivariateReal.lean"
    lean_src = generate_lean_code()
    target_lean.write_text(lean_src, encoding="utf-8")
    print(f"Generated {target_lean} successfully.")


if __name__ == "__main__":
    main()
