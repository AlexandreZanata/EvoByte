#!/usr/bin/env python3
"""Standalone zero-dependency frontier certificate verifier (P184).

Requires ONLY pure Python 3 standard library (no NumPy, no external packages, no network).
Verifies:
  - covering: Covering designs C(v, k, t)
  - schur: Strong Schur partitions (no monochromatic x + y = z, allowing x = y)
  - weak_schur: Weak Schur partitions (no monochromatic distinct x < y with x + y = z)
  - cap_set: Cap sets in F_3^n (no collinear triples summing to 0 mod 3)
  - qecc_stabilizer: Quantum error-correcting stabilizer codes [[n, k, d]]

Scale notice: The standalone QECC verifier uses weight-ordered brute-force search
designed for calibration codes (n <= 10). Larger frontier codes use the P179 verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys


def verify_covering(blocks: object, v: object, k: object, t: object) -> tuple[bool, str]:
    """Verify that blocks form a valid C(v, k, t) covering design."""
    if not isinstance(v, int) or isinstance(v, bool):
        return False, "v must be an integer"
    if not isinstance(k, int) or isinstance(k, bool):
        return False, "k must be an integer"
    if not isinstance(t, int) or isinstance(t, bool):
        return False, "t must be an integer"

    if t < 1 or k < t or v < k:
        return False, f"invalid parameters: require 1 <= t ({t}) <= k ({k}) <= v ({v})"

    num_subsets = math.comb(v, t)
    if not isinstance(blocks, (list, tuple)):
        return False, "blocks must be a list or tuple"
    if len(blocks) == 0:
        return False, "empty blocks collection"

    binom = [[math.comb(n_val, r_val) for r_val in range(t + 1)] for n_val in range(v + 1)]
    bitset = bytearray((num_subsets + 7) // 8)
    covered = 0

    for b_idx, block in enumerate(blocks):
        if not isinstance(block, (list, tuple, set, frozenset)):
            return False, f"block {b_idx} is not a collection"
        if len(block) != k:
            return False, f"block {b_idx} size != {k}"

        sorted_b = []
        for elem in block:
            if not isinstance(elem, int) or isinstance(elem, bool):
                return False, f"element {elem} in block {b_idx} is not an integer"
            if elem < 1 or elem > v:
                return False, f"element {elem} in block {b_idx} out of range 1..{v}"
            sorted_b.append(elem - 1)

        sorted_b.sort()
        for i in range(len(sorted_b) - 1):
            if sorted_b[i] == sorted_b[i + 1]:
                return False, f"duplicate element {sorted_b[i] + 1} in block {b_idx}"

        for sub in itertools.combinations(sorted_b, t):
            r = 0
            for i, c in enumerate(sub):
                r += binom[c][i + 1]
            byte_idx = r >> 3
            bit_mask = 1 << (r & 7)
            if not (bitset[byte_idx] & bit_mask):
                bitset[byte_idx] |= bit_mask
                covered += 1

    if covered == num_subsets:
        return (
            True,
            f"VERIFIED: all {num_subsets} {t}-subsets of 1..{v} covered by {len(blocks)} blocks",
        )
    return False, f"FAILED: only {covered}/{num_subsets} {t}-subsets covered"


def verify_schur(partition: object, k: object) -> tuple[bool, str]:
    """Verify strong Schur partition: no monochromatic x + y = z (allowing x = y)."""
    if not isinstance(partition, (list, tuple)):
        return False, "partition must be a list or tuple"
    n = len(partition)
    if n == 0:
        return False, "empty partition"
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        return False, f"invalid number of classes k: {k}"

    for c in partition:
        if not isinstance(c, int) or isinstance(c, bool) or not (1 <= c <= k):
            return False, f"invalid class {c}"

    for c in range(1, k + 1):
        elems = [i + 1 for i, cl in enumerate(partition) if cl == c]
        elem_set = set(elems)
        for i, x in enumerate(elems):
            for y in elems[i:]:
                if (x + y) in elem_set:
                    return False, f"monochromatic Schur violation: {x} + {y} = {x + y}"

    return True, f"VERIFIED: valid sum-free partition of 1..{n} into {k} classes"


def verify_weak_schur(partition: object, k: object) -> tuple[bool, str]:
    """Verify weak Schur partition: no monochromatic distinct x < y with x + y = z."""
    if not isinstance(partition, (list, tuple)):
        return False, "partition must be a list or tuple"
    n = len(partition)
    if n == 0:
        return False, "empty partition"
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        return False, f"invalid number of classes k: {k}"

    color_sets: list[set[int]] = [set() for _ in range(k + 1)]
    for i, c in enumerate(partition, start=1):
        if not isinstance(c, int) or isinstance(c, bool) or c < 1 or c > k:
            return False, f"invalid color {c} at index {i}"
        color_sets[c].add(i)

    for c in range(1, k + 1):
        s = color_sets[c]
        sorted_s = sorted(s)
        for idx_x, x in enumerate(sorted_s):
            for y in sorted_s[idx_x + 1 :]:
                z = x + y
                if z in s:
                    return False, f"weak Schur violation in color {c}: {x} + {y} = {z}"

    return True, f"VERIFIED: valid weak sum-free partition of 1..{n} into {k} classes"


def verify_cap_set(points: object, n: object) -> tuple[bool, str]:
    """Verify valid cap set in F_3^n: no three distinct collinear points."""
    if not isinstance(points, (list, tuple, set, frozenset)):
        return False, "points must be a collection"
    if len(points) == 0:
        return False, "empty points collection"
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        return False, f"invalid dimension n: {n}"

    seen: set[tuple[int, ...]] = set()
    for p_idx, pt in enumerate(points):
        if not isinstance(pt, (list, tuple)):
            return False, f"point {p_idx} is not a sequence"
        if len(pt) != n:
            return False, f"point {p_idx} dimension != {n}"
        tup = []
        for coord in pt:
            if not isinstance(coord, int) or isinstance(coord, bool) or coord not in (0, 1, 2):
                return False, f"invalid coordinate {coord} in point {p_idx}"
            tup.append(coord)
        p_tup = tuple(tup)
        if p_tup in seen:
            return False, f"duplicate point: {p_tup}"
        seen.add(p_tup)

    pts_list = list(seen)
    num_pts = len(pts_list)
    for i in range(num_pts):
        p1 = pts_list[i]
        for j in range(i + 1, num_pts):
            p2 = pts_list[j]
            third = tuple((-(x + y)) % 3 for x, y in zip(p1, p2))
            if third in seen:
                return False, f"collinear triple in F3^{n}: {p1}, {p2}, {third}"

    return True, f"VERIFIED: valid cap set of size {num_pts} in F3^{n}"


def _gf2_rank(rows: list[int]) -> int:
    basis: list[int] = []
    for v in rows:
        w = v
        for b in basis:
            w = min(w, w ^ b)
        if w:
            hb = w.bit_length() - 1
            for i, b in enumerate(basis):
                if (b >> hb) & 1:
                    basis[i] = b ^ w
            basis.append(w)
            basis.sort(reverse=True)
    return len(basis)


def _in_span(vec: int, rows: list[int]) -> bool:
    w = vec
    basis: list[int] = []
    for v in rows:
        b_val = v
        for b in basis:
            b_val = min(b_val, b_val ^ b)
        if b_val:
            hb = b_val.bit_length() - 1
            for i, b in enumerate(basis):
                if (b >> hb) & 1:
                    basis[i] = b ^ b_val
            basis.append(b_val)
            basis.sort(reverse=True)
    for b in basis:
        if w ^ b < w:
            w ^= b
    return w == 0


def verify_qecc_stabilizer(
    stabilizers: object, n: object, k_claimed: object, d_claimed: object
) -> tuple[bool, str]:
    """Verify quantum stabilizer code [[n, k, d]] using pure stdlib symplectic algebra."""
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        return False, f"invalid n: {n}"
    if not isinstance(k_claimed, int) or isinstance(k_claimed, bool) or k_claimed < 0:
        return False, f"invalid k_claimed: {k_claimed}"
    if not isinstance(d_claimed, int) or isinstance(d_claimed, bool) or d_claimed <= 0:
        return False, f"invalid d_claimed: {d_claimed}"

    if not isinstance(stabilizers, (list, tuple)):
        return False, "stabilizers must be a list or tuple"
    m = len(stabilizers)
    if m == 0:
        return False, "empty stabilizer list"

    mapping = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    parsed: list[tuple[int, int]] = []
    rows: list[int] = []

    for idx, s in enumerate(stabilizers):
        if not isinstance(s, str) or len(s) != n:
            return False, f"stabilizer {idx} must be string of length {n}"
        xi = 0
        zi = 0
        for i, ch in enumerate(s):
            if ch not in mapping:
                return False, f"invalid Pauli character {ch!r} in stabilizer {idx}"
            bx, bz = mapping[ch]
            if bx:
                xi |= 1 << i
            if bz:
                zi |= 1 << i
        parsed.append((xi, zi))
        rows.append(xi | (zi << n))

    mask = (1 << n) - 1
    # Check pairwise commutation
    for i in range(m):
        for j in range(i + 1, m):
            ax, az = parsed[i]
            bx, bz = parsed[j]
            symp = (bin(ax & bz).count("1") + bin(az & bx).count("1")) & 1
            if symp != 0:
                return False, f"generators {i} and {j} do not commute"

    # Check GF(2) rank
    rank = _gf2_rank(rows)
    expected_m = n - k_claimed
    if rank != expected_m:
        return (
            False,
            f"GF(2) rank mismatch: rank {rank} != expected {expected_m} for n={n}, k={k_claimed}",
        )

    # Weight-ordered distance sweep
    for w in range(1, n + 1):
        for positions in itertools.combinations(range(n), w):
            for letters in itertools.product("XYZ", repeat=w):
                xi = 0
                zi = 0
                for p, letter in zip(positions, letters):
                    if letter in ("X", "Y"):
                        xi |= 1 << p
                    if letter in ("Z", "Y"):
                        zi |= 1 << p

                # Check commutation with all generators
                commutes_all = True
                for gx, gz in parsed:
                    if (bin(xi & gz).count("1") + bin(zi & gx).count("1")) & 1 != 0:
                        commutes_all = False
                        break

                if not commutes_all:
                    continue

                # Check if in stabilizer span
                if _in_span(xi | (zi << n), rows):
                    continue

                # First logical operator found sets exact distance
                if w != d_claimed:
                    return False, f"code distance mismatch: discovered d={w} != claimed {d_claimed}"
                return (
                    True,
                    f"VERIFIED: valid quantum stabilizer code [[{n},{k_claimed},{d_claimed}]]",
                )

    return False, "no logical operator found"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="P184 Standalone Frontier Certificate Verifier (Pure stdlib, zero external dependencies)."
    )
    parser.add_argument("certificate", help="Path to certificate JSON file")
    args = parser.parse_args(argv[1:])

    path = args.certificate
    try:
        with open(path, "rb") as f:
            raw_bytes = f.read()
    except Exception as exc:
        print(f"[!] Error reading file: {exc}", file=sys.stderr)
        return 2

    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except Exception as exc:
        print(f"[!] Malformed JSON: {exc}", file=sys.stderr)
        return 2

    target_id = data.get("target_id", "unknown")
    cert_type = data.get("certificate_type")
    print(f"[*] Certificate target: {target_id} (Type: {cert_type})")
    print(f"[*] File SHA-256: {sha256_hash}")

    if cert_type == "covering":
        valid, msg = verify_covering(
            data.get("blocks"), data.get("v"), data.get("k"), data.get("t")
        )
    elif cert_type == "schur":
        valid, msg = verify_schur(data.get("partition"), data.get("k"))
    elif cert_type == "weak_schur":
        valid, msg = verify_weak_schur(data.get("partition"), data.get("k"))
    elif cert_type == "cap_set":
        valid, msg = verify_cap_set(data.get("points"), data.get("n"))
    elif cert_type == "qecc_stabilizer":
        valid, msg = verify_qecc_stabilizer(
            data.get("stabilizers"), data.get("n"), data.get("k_claimed"), data.get("d_claimed")
        )
    else:
        print(f"[!] Unsupported certificate type: {cert_type}", file=sys.stderr)
        return 1

    if valid:
        print(f"[SUCCESS] {msg}")
        return 0
    else:
        print(f"[FAILED] {msg}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
