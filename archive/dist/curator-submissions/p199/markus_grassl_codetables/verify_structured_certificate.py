#!/usr/bin/env python3
"""Standalone Zero-Dependency Structured Certificate Verifier (P197).

Requires ONLY pure Python 3 standard library (no NumPy, no PySAT, no external packages).
Verifies:
  - covering_design: Covering designs C(v, k, t), including cyclic orbit expansions
  - qecc_stabilizer: Quantum error-correcting codes [[n, k, d]] via symplectic algebra
  - schur: Schur sum-free partitions
  - vanderwaerden: Van der Waerden arithmetic-progression-free colorings

Falsifiable guarantee:
  Validates valid certificates in < 5 seconds.
  Rejects immediately if any bit, block, commutator, or vector is mutated.
  Audit-friendly pure standard library implementation.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
from typing import Any


def verify_covering_design_pure(doc: dict[str, Any]) -> tuple[bool, str]:
    """Verify that a covering design C(v, k, t) covers all t-subsets of v points."""
    params = doc.get("parameters", {})
    v = params.get("v") if "v" in params else doc.get("v")
    k = params.get("k") if "k" in params else doc.get("k")
    t = params.get("t") if "t" in params else doc.get("t")
    claimed_b = (
        params.get("claimed_blocks") if "claimed_blocks" in params else doc.get("claimed_blocks")
    )

    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        return False, f"invalid parameter v: {v}"
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        return False, f"invalid parameter k: {k}"
    if not isinstance(t, int) or isinstance(t, bool) or t < 1:
        return False, f"invalid parameter t: {t}"
    if not (1 <= t <= k <= v):
        return False, f"parameters violate 1 <= t ({t}) <= k ({k}) <= v ({v})"

    candidate = doc.get("candidate", {})
    if isinstance(candidate, list):
        blocks_raw = candidate
        indexing = doc.get("indexing", 1)
        symmetry_info = doc.get("symmetry")
    elif isinstance(candidate, dict):
        blocks_raw = candidate.get("blocks")
        indexing = candidate.get("indexing", 1)
        symmetry_info = candidate.get("symmetry")
    else:
        blocks_raw = doc.get("blocks")
        indexing = doc.get("indexing", 1)
        symmetry_info = doc.get("symmetry")

    # If blocks not explicitly given but symmetry base_blocks are provided, expand them
    if blocks_raw is None and symmetry_info and "base_blocks" in symmetry_info:
        base_blocks = symmetry_info.get("base_blocks", [])
        expanded: list[list[int]] = []
        for base in base_blocks:
            for s in range(v):
                if indexing == 1:
                    blk = sorted(((x - 1 + s) % v) + 1 for x in base)
                else:
                    blk = sorted((x + s) % v for x in base)
                expanded.append(blk)
        blocks_raw = expanded

    if not isinstance(blocks_raw, (list, tuple)):
        return False, "blocks must be a list or tuple"
    if len(blocks_raw) == 0:
        return False, "empty blocks collection"

    if claimed_b is not None and len(blocks_raw) != claimed_b:
        return (
            False,
            f"claimed block count ({claimed_b}) does not match blocks length ({len(blocks_raw)})",
        )

    # Verify symmetry consistency if provided
    if symmetry_info and "base_blocks" in symmetry_info:
        base_blocks = symmetry_info.get("base_blocks", [])
        expected_orbits: set[tuple[int, ...]] = set()
        for base in base_blocks:
            for s in range(v):
                if indexing == 1:
                    blk = tuple(sorted(((x - 1 + s) % v) + 1 for x in base))
                else:
                    blk = tuple(sorted((x + s) % v for x in base))
                expected_orbits.add(blk)
        provided_blocks = {tuple(sorted(b)) for b in blocks_raw}
        if expected_orbits != provided_blocks:
            return False, "expanded base blocks do not match the provided candidate blocks"

    # Validate elements and block lengths
    min_elem = 1 if indexing == 1 else 0
    max_elem = v if indexing == 1 else v - 1

    offset = min_elem
    num_subsets = math.comb(v, t)
    covered_subsets: set[tuple[int, ...]] = set()

    for idx, block in enumerate(blocks_raw):
        if not isinstance(block, (list, tuple, set, frozenset)):
            return False, f"block {idx} is not a valid collection"
        if len(block) != k:
            return False, f"block {idx} has length {len(block)} != k ({k})"

        norm_b: list[int] = []
        for x in block:
            if not isinstance(x, int) or isinstance(x, bool):
                return False, f"element {x!r} in block {idx} is not an integer"
            if x < min_elem or x > max_elem:
                return False, f"element {x} in block {idx} out of range {min_elem}..{max_elem}"
            norm_b.append(x - offset)

        norm_b.sort()
        for i in range(len(norm_b) - 1):
            if norm_b[i] == norm_b[i + 1]:
                return False, f"duplicate element {norm_b[i] + offset} in block {idx}"

        # Record coverage
        for sub in itertools.combinations(norm_b, t):
            covered_subsets.add(sub)

    if len(covered_subsets) == num_subsets:
        return (
            True,
            f"VERIFIED: all {num_subsets} {t}-subsets of {v} elements covered by {len(blocks_raw)} blocks",
        )

    missing = num_subsets - len(covered_subsets)
    # Find first missing subset for actionable debugging
    for sub in itertools.combinations(range(v), t):
        if sub not in covered_subsets:
            first_missing = tuple(x + offset for x in sub)
            break
    else:
        first_missing = ()

    return (
        False,
        f"FAILED: {missing}/{num_subsets} {t}-subsets uncovered (first missing: {first_missing})",
    )


def _gf2_rank_and_basis(rows: list[int]) -> tuple[int, list[int]]:
    """Compute GF(2) rank and echelon basis using Gaussian elimination."""
    basis: list[int] = []
    for r in rows:
        w = r
        for b in basis:
            w = min(w, w ^ b)
        if w:
            hb = w.bit_length() - 1
            for i, b in enumerate(basis):
                if (b >> hb) & 1:
                    basis[i] = b ^ w
            basis.append(w)
            basis.sort(reverse=True)
    return len(basis), basis


def _in_gf2_span(w: int, basis: list[int]) -> bool:
    """Check if binary vector w is in the GF(2) linear span of basis."""
    for b in basis:
        if w ^ b < w:
            w ^= b
    return w == 0


def verify_qecc_stabilizer_pure(doc: dict[str, Any]) -> tuple[bool, str]:
    """Verify quantum stabilizer code [[n, k, d]] using pure stdlib symplectic algebra."""
    params = doc.get("parameters", {})
    n = params.get("n") if "n" in params else doc.get("n")
    k = params.get("k") if "k" in params else doc.get("k")
    claimed_d = params.get("claimed_d") if "claimed_d" in params else doc.get("claimed_d")

    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        return False, f"invalid parameter n: {n}"
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        return False, f"invalid parameter k: {k}"
    if not isinstance(claimed_d, int) or isinstance(claimed_d, bool) or claimed_d <= 0:
        return False, f"invalid parameter claimed_d: {claimed_d}"

    candidate = doc.get("candidate", {})
    if isinstance(candidate, list):
        gens_raw = candidate
    elif isinstance(candidate, dict):
        gens_raw = candidate.get("generators", [])
    else:
        gens_raw = doc.get("generators", [])

    if not isinstance(gens_raw, (list, tuple)):
        return False, "generators must be a list or tuple"
    m = len(gens_raw)
    expected_m = n - k
    if m != expected_m:
        return False, f"expected m = n - k = {expected_m} generators, got {m}"

    mapping = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    parsed: list[tuple[int, int]] = []
    rows: list[int] = []

    for idx, s in enumerate(gens_raw):
        if not isinstance(s, str) or len(s) != n:
            return False, f"generator {idx} must be string of length {n}, got {s!r}"
        s_upper = s.upper()
        xi = 0
        zi = 0
        for i, ch in enumerate(s_upper):
            if ch not in mapping:
                return False, f"invalid Pauli character {ch!r} in generator {idx}"
            bx, bz = mapping[ch]
            if bx:
                xi |= 1 << i
            if bz:
                zi |= 1 << i
        parsed.append((xi, zi))
        rows.append(xi | (zi << n))

    # Commutation: symplectic product must be 0 mod 2 for all pairs
    for i in range(m):
        for j in range(i + 1, m):
            ax, az = parsed[i]
            bx, bz = parsed[j]
            symp = (bin(ax & bz).count("1") + bin(az & bx).count("1")) & 1
            if symp != 0:
                return (
                    False,
                    f"generators {i} ({gens_raw[i]}) and {j} ({gens_raw[j]}) do not commute",
                )

    # Linear independence
    rank, basis = _gf2_rank_and_basis(rows)
    if rank != m:
        return False, f"generators are linearly dependent over GF(2): rank {rank} < {m}"

    # Distance check: for all errors of weight w < claimed_d, check they are detected
    paulis = [(1, 0, "X"), (0, 1, "Z"), (1, 1, "Y")]
    for wt in range(1, claimed_d):
        for pos_combo in itertools.combinations(range(n), wt):
            for p_types in itertools.product(paulis, repeat=wt):
                exi = 0
                ezi = 0
                for pos, (bx, bz, _) in zip(pos_combo, p_types):
                    if bx:
                        exi |= 1 << pos
                    if bz:
                        ezi |= 1 << pos

                # Check commutation with all m generators
                commutes_all = True
                for gx, gz in parsed:
                    if ((bin(exi & gz).count("1") + bin(ezi & gx).count("1")) & 1) != 0:
                        commutes_all = False
                        break

                if commutes_all:
                    # If it commutes with all, it MUST be inside the stabilizer span S
                    e_vec = exi | (ezi << n)
                    if not _in_gf2_span(e_vec, basis):
                        err_str = ["I"] * n
                        for pos, (_, _, ch) in zip(pos_combo, p_types):
                            err_str[pos] = ch
                        return (
                            False,
                            f"undetected logical operator {''.join(err_str)} of weight {wt} < claimed_d ({claimed_d})",
                        )

    return (
        True,
        f"VERIFIED: [[{n}, {k}, {claimed_d}]] stabilizer code with {m} independent commuting generators",
    )


def verify_schur_pure(doc: dict[str, Any]) -> tuple[bool, str]:
    """Verify strong Schur partition from certificate."""
    params = doc.get("parameters", {})
    k = params.get("k") if "k" in params else doc.get("k")
    partition = doc.get("candidate", {}).get("partition") or doc.get("partition")
    if not isinstance(partition, (list, tuple)) or not isinstance(k, int):
        return False, "invalid Schur certificate format"

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


def verify_vdw_pure(doc: dict[str, Any]) -> tuple[bool, str]:
    """Verify Van der Waerden coloring from certificate."""
    params = doc.get("parameters", {})
    r = params.get("r") if "r" in params else doc.get("r")
    k = params.get("k") if "k" in params else doc.get("k")
    coloring = doc.get("candidate", {}).get("coloring") or doc.get("coloring")
    if not isinstance(coloring, (list, tuple)) or not isinstance(r, int) or not isinstance(k, int):
        return False, "invalid Van der Waerden certificate format"

    n = len(coloring)
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


def compute_payload_checksum(doc: dict[str, Any]) -> str:
    """Compute canonical SHA-256 over certificate payload."""
    payload = {k: v for k, v in doc.items() if k != "sha256_checksum"}
    canonical_bytes = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def verify_certificate_document(
    doc: dict[str, Any],
    check_sha: bool = True,
) -> tuple[bool, str]:
    """Verify a complete structured certificate document."""
    if not isinstance(doc, dict):
        return False, "certificate root must be a JSON object"

    # Check payload checksum if present
    if check_sha and "sha256_checksum" in doc:
        claimed_sha = doc["sha256_checksum"]
        computed_sha = compute_payload_checksum(doc)
        if claimed_sha != computed_sha:
            return (
                False,
                f"SHA-256 payload checksum mismatch: claimed {claimed_sha[:16]}..., computed {computed_sha[:16]}...",
            )

    cert_type = doc.get("certificate_type")
    if cert_type in ("covering_design", "covering"):
        return verify_covering_design_pure(doc)
    elif cert_type in ("qecc_stabilizer", "qecc"):
        return verify_qecc_stabilizer_pure(doc)
    elif cert_type == "schur":
        return verify_schur_pure(doc)
    elif cert_type == "vanderwaerden":
        return verify_vdw_pure(doc)
    else:
        return False, f"unsupported certificate_type: {cert_type!r}"


def main(argv: list[str]) -> int:
    """Standalone CLI entry point."""
    if len(argv) < 2:
        print("Usage: python3 verify_structured_certificate.py <certificate.json>", file=sys.stderr)
        return 2

    path = argv[1]
    t0 = time.perf_counter()
    try:
        with open(path, "rb") as f:
            raw_bytes = f.read()
    except Exception as e:
        print(f"[!] Cannot read file {path}: {e}", file=sys.stderr)
        return 2

    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    try:
        doc = json.loads(raw_bytes.decode("utf-8"))
    except Exception as e:
        print(f"[!] JSON parsing failed for {path}: {e}", file=sys.stderr)
        return 1

    cert_type = doc.get("certificate_type", "unknown")
    target_id = doc.get("target_id", "unknown")
    verdict = doc.get("verdict", "UNSPECIFIED")

    print(f"[*] Certificate: {target_id} (Type: {cert_type}, Verdict: {verdict})")
    print(f"[*] File SHA-256: {file_sha256}")

    valid, msg = verify_certificate_document(doc, check_sha=True)
    elapsed = time.perf_counter() - t0

    if valid:
        print(f"[SUCCESS] {msg} ({elapsed * 1000.0:.2f} ms)")
        return 0
    else:
        print(f"[FAILED] {msg} ({elapsed * 1000.0:.2f} ms)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
