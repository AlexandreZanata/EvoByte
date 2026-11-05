"""Exhaustive exact census of small bivariate bicycle codes (P222).

Reference implementation frozen under D049 / P222.
Computes exact logical dimension k and exact minimum distance d (up to wmax)
for 2-block bivariate bicycle codes over F_2[Z_l x Z_m] with n = 2*l*m.
"""

from __future__ import annotations

import itertools
import multiprocessing as mp
import os
import time
from typing import Any, Callable, Iterable

import numpy as np


def reg_rows(l: int, m: int, P: Iterable[tuple[int, int]]) -> list[int]:
    """Generate row bitmasks for circulant polynomial P over Z_l x Z_m."""
    L = l * m
    rows: list[int] = []
    for i in range(l):
        for j in range(m):
            v = 0
            for a, b in P:
                v ^= 1 << (L - 1 - (((i + a) % l) * m + ((j + b) % m)))
            rows.append(v)
    return rows


def checks(
    l: int,
    m: int,
    A: Iterable[tuple[int, int]],
    B: Iterable[tuple[int, int]],
) -> tuple[list[int], list[int]]:
    """Compute parity check rows hx and hz for bivariate bicycle code (A, B)."""
    L = l * m
    star_a = {((-a) % l, (-b) % m) for a, b in A}
    star_b = {((-a) % l, (-b) % m) for a, b in B}
    ra, rb = reg_rows(l, m, A), reg_rows(l, m, B)
    rsa, rsb = reg_rows(l, m, star_a), reg_rows(l, m, star_b)
    hx = [(a << L) | b for a, b in zip(ra, rb)]
    hz = [(a << L) | b for a, b in zip(rsb, rsa)]  # (B* | A*)
    return hx, hz


def basis_of(rows: list[int]) -> list[int]:
    """Compute echelon basis of row vectors."""
    basis: list[int] = []
    for v in rows:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def in_span(v: int, basis: list[int]) -> bool:
    """Check if vector v is in the GF(2) span of basis."""
    for b in basis:
        v = min(v, v ^ b)
    return v == 0


_MASKS: dict[tuple[int, int], np.ndarray] = {}


def masks_of_weight(n: int, w: int) -> np.ndarray:
    """Return all n-bit uint64 masks of exact Hamming weight w."""
    key = (n, w)
    if key not in _MASKS:
        _MASKS[key] = np.fromiter(
            (sum(1 << (n - 1 - s) for s in S) for S in itertools.combinations(range(n), w)),
            dtype=np.uint64,
        )
    return _MASKS[key]


def parity64(x: np.ndarray) -> np.ndarray:
    """Vectorized parity of uint64 array."""
    if hasattr(np, "bitwise_count"):
        return (np.bitwise_count(x) & np.uint64(1)).astype(bool)
    for s in (32, 16, 8, 4, 2, 1):
        x = x ^ (x >> np.uint64(s))
    return (x & np.uint64(1)).astype(bool)


def exact_distance(hx: list[int], hz: list[int], n: int, wmax: int = 7) -> tuple[int, int | None]:
    """Returns (k, d) with d=None meaning d > wmax; k<=0 returns (k, None)."""
    bx, bz = basis_of(hx), basis_of(hz)
    k = n - len(bx) - len(bz)
    if k <= 0:
        return k, None
    for w in range(1, wmax + 1):
        M = masks_of_weight(n, w)
        for chk, other in ((hz, bx), (hx, bz)):
            cur = M
            for h in chk:
                cur = cur[~parity64(cur & np.uint64(h))]
                if len(cur) == 0:
                    break
            for e in cur:
                if not in_span(int(e), other):
                    return k, w
    return k, None


def enumerate_A(l: int, m: int) -> list[tuple[tuple[int, int], ...]]:
    """Enumerate all valid A subsets with (0,0) in A and |A| in {3, 4}."""
    pts = [(i, j) for i in range(l) for j in range(m)]
    pts_rem = pts[1:]  # pts[0] is (0, 0)
    origin = (0, 0)
    a_list: list[tuple[tuple[int, int], ...]] = []
    # |A| = 3: (0,0) + 2 points from pts_rem
    for S in itertools.combinations(pts_rem, 2):
        a_list.append((origin,) + S)
    # |A| = 4: (0,0) + 3 points from pts_rem
    for S in itertools.combinations(pts_rem, 3):
        a_list.append((origin,) + S)
    return a_list


def enumerate_B(l: int, m: int) -> list[tuple[tuple[int, int], ...]]:
    """Enumerate all valid B subsets with |B| in {3, 4}."""
    pts = [(i, j) for i in range(l) for j in range(m)]
    b_list: list[tuple[tuple[int, int], ...]] = []
    for S in itertools.combinations(pts, 3):
        b_list.append(S)
    for S in itertools.combinations(pts, 4):
        b_list.append(S)
    return b_list


def enumerate_space(
    l: int, m: int
) -> list[tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]]:
    """Enumerate all (A, B) candidate pairs for group Z_l x Z_m."""
    a_list = enumerate_A(l, m)
    b_list = enumerate_B(l, m)
    return [(a, b) for a in a_list for b in b_list]


def enumerate_groups(max_lm: int = 16, min_l: int = 2) -> list[tuple[int, int]]:
    """Enumerate abelian group pairs (l, m) with min_l <= l <= m and l*m <= max_lm."""
    groups: list[tuple[int, int]] = []
    for l in range(min_l, max_lm + 1):
        if l * l > max_lm:
            break
        for m in range(l, max_lm // l + 1):
            if l * m <= max_lm:
                groups.append((l, m))
    groups.sort(key=lambda g: (g[0] * g[1], g[0]))
    return groups


# Record tuple type: (n, k, l, m, A, B, d_exact, d_gt)
RecordTuple = tuple[
    int,
    int,
    int,
    int,
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    int | None,
    int | None,
]


def _eval_chunk(
    args: tuple[int, int, tuple[tuple[int, int], ...], list[tuple[tuple[int, int], ...]], int],
) -> tuple[list[RecordTuple], int]:
    """Worker task evaluating one fixed A across all B in B_list."""
    l, m, A, b_list, wmax = args
    n = 2 * l * m
    k0_count = 0
    records: list[RecordTuple] = []

    for B in b_list:
        hx, hz = checks(l, m, A, B)
        k, d = exact_distance(hx, hz, n, wmax=wmax)
        if k <= 0:
            k0_count += 1
            continue
        d_exact = d if d is not None else None
        d_gt = None if d is not None else wmax
        records.append((n, k, l, m, A, B, d_exact, d_gt))

    return records, k0_count


def run_census(
    max_lm: int = 16,
    wmax: int = 7,
    workers: int = 16,
    min_l: int = 2,
    log_fn: Callable[[str], None] | None = None,
) -> tuple[list[RecordTuple], dict[str, Any]]:
    """Run parallel exact census over groups up to max_lm.

    Evaluates groups in ascending order of l*m (10 -> 12 -> 14 -> 16).
    Returns (sorted_records, summary_dict).
    """

    def log(msg: str) -> None:
        if log_fn:
            log_fn(msg)

    groups = enumerate_groups(max_lm=max_lm, min_l=min_l)
    log(f"Enumerating {len(groups)} groups with {min_l} <= l <= m and l*m <= {max_lm}: {groups}")

    all_records: list[RecordTuple] = []
    total_pairs = 0
    total_k0 = 0
    group_stats: dict[str, dict[str, int]] = {}

    t_start = time.time()

    # Stages: partition groups into <=10, <=12, <=14, <=16
    stages: list[tuple[str, list[tuple[int, int]]]] = [
        ("lm <= 10", [g for g in groups if g[0] * g[1] <= 10]),
        ("10 < lm <= 12", [g for g in groups if 10 < g[0] * g[1] <= 12]),
        ("12 < lm <= 14", [g for g in groups if 12 < g[0] * g[1] <= 14]),
        ("14 < lm <= 16", [g for g in groups if 14 < g[0] * g[1] <= 16]),
    ]

    with mp.Pool(processes=workers) as pool:
        for stage_name, stage_groups in stages:
            if not stage_groups:
                continue
            stage_start = time.time()
            log(
                f"--- Starting stage: {stage_name} ({len(stage_groups)} groups: {stage_groups}) ---"
            )

            for l, m in stage_groups:
                g_start = time.time()
                a_list = enumerate_A(l, m)
                b_list = enumerate_B(l, m)
                g_pairs = len(a_list) * len(b_list)
                total_pairs += g_pairs

                chunk_args = [(l, m, A, b_list, wmax) for A in a_list]
                g_k0 = 0
                g_pos = 0

                for chunk_records, chunk_k0 in pool.imap_unordered(
                    _eval_chunk, chunk_args, chunksize=1
                ):
                    all_records.extend(chunk_records)
                    g_k0 += chunk_k0
                    g_pos += len(chunk_records)

                total_k0 += g_k0
                g_elapsed = time.time() - g_start
                group_key = f"{l}x{m}"
                group_stats[group_key] = {
                    "l": l,
                    "m": m,
                    "lm": l * m,
                    "n": 2 * l * m,
                    "total_pairs": g_pairs,
                    "k_zero": g_k0,
                    "k_pos": g_pos,
                    "elapsed_s": round(g_elapsed, 2),
                }
                log(
                    f"Group ({l}, {m}): {g_pairs} pairs -> {g_pos} k>0, {g_k0} k=0 in {g_elapsed:.2f}s"
                )

            stage_elapsed = time.time() - stage_start
            log(
                f"Completed {stage_name} in {stage_elapsed:.2f}s (total records so far: {len(all_records)})"
            )

    t_total = time.time() - t_start
    log(f"Sorting {len(all_records)} records deterministically by (n, k, l, m, A, B)...")
    all_records.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[4], r[5]))

    # Compute summary and best_d
    best_d_map: dict[str, dict[str, Any]] = {}
    d_gt_count = 0

    for r in all_records:
        n, k, l, m, A, B, d_exact, d_gt = r
        if d_gt is not None:
            d_gt_count += 1
        key = f"{n}_{k}"
        d_val = d_exact if d_exact is not None else (d_gt + 1 if d_gt is not None else 0)

        if key not in best_d_map:
            best_d_map[key] = {
                "n": n,
                "k": k,
                "best_d": d_val,
                "is_exact": d_exact is not None,
                "count": 1,
                "example": {
                    "l": l,
                    "m": m,
                    "A": [list(p) for p in A],
                    "B": [list(p) for p in B],
                    "d_exact": d_exact,
                    "d_gt": d_gt,
                },
            }
        else:
            cur = best_d_map[key]
            if d_val > cur["best_d"]:
                cur["best_d"] = d_val
                cur["is_exact"] = d_exact is not None
                cur["count"] = 1
                cur["example"] = {
                    "l": l,
                    "m": m,
                    "A": [list(p) for p in A],
                    "B": [list(p) for p in B],
                    "d_exact": d_exact,
                    "d_gt": d_gt,
                }
            elif d_val == cur["best_d"]:
                cur["count"] += 1

    summary = {
        "max_lm": max_lm,
        "wmax": wmax,
        "workers": workers,
        "min_l": min_l,
        "total_pairs_enumerated": total_pairs,
        "total_k_zero": total_k0,
        "total_k_pos": len(all_records),
        "total_d_gt": d_gt_count,
        "elapsed_seconds": round(t_total, 2),
        "groups": group_stats,
        "best_d": best_d_map,
    }

    return all_records, summary
