"""Independent pure-Python recomputation of projective and affine group orbits (P221).

Rules:
- Zero imports from evobyte (stdlib only).
- Ground-truth validation of group orbits under PGL(2, 13) and AGL(2, 4).
"""

from __future__ import annotations

from collections import deque
import itertools


def test_recompute_pgl2_13_orbits() -> None:
    """Independent ground-truth recomputation for PGL(2, 13) action on 6-subsets of P^1(F13)."""

    # Points: 0..12 represent elements of F13, 13 represents infinity.
    def gen_trans(z: int) -> int:  # z -> z + 1
        if z == 13:
            return 13
        return (z + 1) % 13

    def gen_mult(z: int) -> int:  # z -> 2z (2 is quadratic non-residue mod 13)
        if z == 13:
            return 13
        return (2 * z) % 13

    def gen_inv(z: int) -> int:  # z -> -1/z with 0 <-> infinity
        if z == 13:
            return 0
        if z == 0:
            return 13
        inv = pow(z, 11, 13)  # z^(13-2) mod 13
        return (-inv) % 13

    gens = [gen_trans, gen_mult, gen_inv]

    all_subsets = list(itertools.combinations(range(14), 6))
    assert len(all_subsets) == 3003, f"Expected 3003 6-subsets, got {len(all_subsets)}"
    sub_to_id = {s: i for i, s in enumerate(all_subsets)}

    visited = [False] * len(all_subsets)
    orbit_sizes: list[int] = []

    for start_idx in range(len(all_subsets)):
        if visited[start_idx]:
            continue
        queue = deque([all_subsets[start_idx]])
        visited[start_idx] = True
        size = 1

        while queue:
            curr = queue.popleft()
            for g in gens:
                nxt = tuple(sorted(g(x) for x in curr))
                nxt_idx = sub_to_id[nxt]
                if not visited[nxt_idx]:
                    visited[nxt_idx] = True
                    size += 1
                    queue.append(nxt)

        orbit_sizes.append(size)

    sorted_sizes = sorted(orbit_sizes)
    assert sum(sorted_sizes) == 3003, f"Orbit sum mismatch: {sum(sorted_sizes)} != 3003"
    expected_sizes = [91, 182, 546, 1092, 1092]
    assert sorted_sizes == expected_sizes, (
        f"PGL(2,13) orbit sizes mismatch: {sorted_sizes} != {expected_sizes}"
    )
    assert min(sorted_sizes) > 25, f"Minimal orbit {min(sorted_sizes)} not > 25"


def test_recompute_agl2_4_orbits() -> None:
    """Independent ground-truth recomputation for AGL(2, 4) action on 7-subsets of F_4^2."""
    # GF(4): elements {0, 1, 2, 3}. Addition is XOR (^).
    # Multiplication table for GF(4) under irreducible polynomial x^2 + x + 1:
    mul_table = [
        [0, 0, 0, 0],
        [0, 1, 2, 3],
        [0, 2, 3, 1],
        [0, 3, 1, 2],
    ]

    def gf_add(a: int, b: int) -> int:
        return a ^ b

    def gf_mul(a: int, b: int) -> int:
        return mul_table[a][b]

    def pt_to_id(p: tuple[int, int]) -> int:
        return 4 * p[0] + p[1]

    def id_to_pt(i: int) -> tuple[int, int]:
        return (i // 4, i % 4)

    # Generators: 4 translations + 3 GL(2, 4) matrices generate AGL(2, 4) of order 2880
    translations = [(1, 0), (0, 1), (2, 0), (0, 2)]
    matrices = [
        [[1, 1], [0, 1]],
        [[0, 1], [1, 0]],
        [[2, 0], [0, 1]],
    ]

    gens = []
    for t in translations:

        def make_tr(vec: tuple[int, int]):
            return lambda pt: (gf_add(pt[0], vec[0]), gf_add(pt[1], vec[1]))

        gens.append(make_tr(t))

    for m in matrices:

        def make_mat(mat: list[list[int]]):
            return lambda pt: (
                gf_add(gf_mul(mat[0][0], pt[0]), gf_mul(mat[0][1], pt[1])),
                gf_add(gf_mul(mat[1][0], pt[0]), gf_mul(mat[1][1], pt[1])),
            )

        gens.append(make_mat(m))

    all_subsets = list(itertools.combinations(range(16), 7))
    assert len(all_subsets) == 11440, f"Expected 11440 7-subsets, got {len(all_subsets)}"
    sub_to_id = {s: i for i, s in enumerate(all_subsets)}

    visited = [False] * len(all_subsets)
    orbit_sizes: list[int] = []

    for start_idx in range(len(all_subsets)):
        if visited[start_idx]:
            continue
        queue = deque([all_subsets[start_idx]])
        visited[start_idx] = True
        size = 1

        while queue:
            curr = queue.popleft()
            pts = [id_to_pt(x) for x in curr]
            for g in gens:
                nxt_pts = [g(p) for p in pts]
                nxt = tuple(sorted(pt_to_id(p) for p in nxt_pts))
                nxt_idx = sub_to_id[nxt]
                if not visited[nxt_idx]:
                    visited[nxt_idx] = True
                    size += 1
                    queue.append(nxt)

        orbit_sizes.append(size)

    sorted_sizes = sorted(orbit_sizes)
    assert sum(sorted_sizes) == 11440, f"Orbit sum mismatch: {sum(sorted_sizes)} != 11440"
    expected_sizes = [160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880]
    assert sorted_sizes == expected_sizes, (
        f"AGL(2,4) orbit sizes mismatch: {sorted_sizes} != {expected_sizes}"
    )
    assert min(sorted_sizes) > 24, f"Minimal orbit {min(sorted_sizes)} not > 24"
