"""Independent pure-Python recomputation of bivariate bicycle code parameters (P221).

Rules:
- Zero imports from evobyte (stdlib only).
- Ground-truth validation of ranks, logical dimension k, and minimum distance d.
"""

from __future__ import annotations

import itertools


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


def distance(
    hx_mat: list[list[int]], hz_mat: list[list[int]], n_qubits: int
) -> tuple[int, int, int]:
    hx, hz = bits(hx_mat), bits(hz_mat)
    bx, bz = basis_of(hx), basis_of(hz)
    assert all(par(a & b) == 0 for a in hx for b in hz), "Symplectic commutativity failed"
    for w in range(1, n_qubits + 1):
        for s in itertools.combinations(range(n_qubits), w):
            e = sum(1 << (n_qubits - 1 - idx) for idx in s)
            if all(par(e & h) == 0 for h in hz) and not in_span(e, bx):
                return len(bx), len(bz), w
            if all(par(e & h) == 0 for h in hx) and not in_span(e, bz):
                return len(bx), len(bz), w
    raise RuntimeError("No undetectable logical operator found")


def test_recompute_code_20_2_6() -> None:
    """Independent ground-truth recomputation for [[20, 2, 6]] bivariate bicycle code."""
    l, m = 5, 2
    a_exp = [(0, 0), (0, 1), (1, 1), (2, 1)]
    b_exp = [(0, 1), (1, 1), (2, 0), (2, 1)]
    hx, hz = build(l, m, a_exp, b_exp)
    rx, rz, d = distance(hx, hz, 2 * l * m)

    assert rx == 9, f"Expected rx=9, got {rx}"
    assert rz == 9, f"Expected rz=9, got {rz}"
    k = (2 * l * m) - rx - rz
    assert k == 2, f"Expected k=2, got {k}"
    assert d == 6, f"Expected d=6, got {d}"


def test_recompute_code_16_2_4() -> None:
    """Independent ground-truth recomputation for [[16, 2, 4]] bivariate bicycle code."""
    l, m = 2, 4
    a_exp = [(0, 0), (0, 2), (1, 0), (1, 3)]
    b_exp = [(0, 1), (1, 0), (1, 2), (1, 3)]
    hx, hz = build(l, m, a_exp, b_exp)
    rx, rz, d = distance(hx, hz, 2 * l * m)

    assert rx == 7, f"Expected rx=7, got {rx}"
    assert rz == 7, f"Expected rz=7, got {rz}"
    k = (2 * l * m) - rx - rz
    assert k == 2, f"Expected k=2, got {k}"
    assert d == 4, f"Expected d=4, got {d}"
