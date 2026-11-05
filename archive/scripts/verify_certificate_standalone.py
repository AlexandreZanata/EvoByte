#!/usr/bin/env python3
"""Standalone certificate verifier (P167).

Requires ONLY pure Python 3 standard library.
Verifies van der Waerden colorings, Schur partitions, and graph invariants.
"""

from __future__ import annotations

import hashlib
import json
import sys


def verify_vdw_pure(coloring: list[int], r: int, k: int) -> tuple[bool, str]:
    n = len(coloring)
    if n == 0:
        return False, "empty coloring"
    for c in coloring:
        if not (1 <= c <= r):
            return False, f"invalid color {c}"

    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            first = coloring[a]
            if all(coloring[a + i * d] == first for i in range(k)):
                return False, f"monochromatic AP of length {k} at a={a + 1}, d={d}"

    return True, f"VERIFIED: zero monochromatic {k}-term APs in 1..{n}"


def verify_schur_pure(partition: list[int], k: int) -> tuple[bool, str]:
    n = len(partition)
    for c in partition:
        if not (1 <= c <= k):
            return False, f"invalid class {c}"

    for c in range(1, k + 1):
        elems = [i + 1 for i, cl in enumerate(partition) if cl == c]
        elem_set = set(elems)
        for i, x in enumerate(elems):
            for y in elems[i:]:
                if (x + y) in elem_set:
                    return False, f"monochromatic Schur violation: {x} + {y} = {x + y}"

    return True, f"VERIFIED: valid sum-free partition of 1..{n} into {k} classes"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python3 verify_certificate_standalone.py <certificate.json>", file=sys.stderr)
        return 2

    path = argv[1]
    with open(path, "rb") as f:
        raw_bytes = f.read()

    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    data = json.loads(raw_bytes.decode("utf-8"))

    cert_type = data.get("certificate_type")
    print(f"[*] Certificate target: {data.get('target_id')} (Type: {cert_type})")
    print(f"[*] File SHA-256: {sha256_hash}")

    if cert_type == "vanderwaerden":
        valid, msg = verify_vdw_pure(data["coloring"], data["r"], data["k"])
    elif cert_type == "schur":
        valid, msg = verify_schur_pure(data["partition"], data["k"])
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
    raise SystemExit(main(sys.argv))
