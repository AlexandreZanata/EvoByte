"""Independent verifier for quantum stabilizer codes [[n,k,d]] (P179).

Pure stdlib (+ NumPy only for the optional batch helper, never for the
exact core): Pauli operators as binary pairs (x|z), symplectic product,
GF(2) rank by integer bit-vectors, exact distance by weight-ordered sweep
of the Pauli centralizer. Every public function returns (ok, payload);
malformed input is (False, reason), never an exception.
"""

from __future__ import annotations

import itertools


def _valid_pauli_pair(pauli) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
    try:
        x, z = pauli
    except Exception:
        return None
    try:
        xr = tuple(x)
        zr = tuple(z)
    except Exception:
        return None
    if len(xr) != len(zr) or len(xr) == 0:
        return None
    if any(isinstance(b, bool) for b in xr) or any(isinstance(b, bool) for b in zr):
        return None
    if any(b not in (0, 1) for b in xr) or any(b not in (0, 1) for b in zr):
        return None
    return tuple(xr), tuple(zr)


def _bits(rows: list[int]) -> list[int]:
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
    return basis


def _gf2_rank(rows: list[int]) -> int:
    return len(_bits(rows))


def _in_span(vec: int, rows: list[int]) -> bool:
    w = vec
    for b in _bits(rows):
        if w ^ b < w:
            w ^= b
    return w == 0


def _row_bits(xl: tuple[int, ...], zl: tuple[int, ...]) -> int:
    n = len(xl)
    v = 0
    for i, b in enumerate(xl):
        if b:
            v |= 1 << i
    for i, b in enumerate(zl):
        if b:
            v |= 1 << (n + i)
    return v


def _symplectic_int(ax: int, az: int, bx: int, bz: int, mask: int) -> int:
    return (bin(ax & bz).count("1") + bin(az & bx).count("1")) & 1


def parse_pauli(s, n) -> tuple[bool, object]:
    """Parse 'IXYZ' string of length n into binary (x, z) tuples."""
    try:
        nn = int(n)
    except Exception:
        return False, f"invalid n: {n!r}"
    if isinstance(nn, bool) or nn <= 0:
        return False, f"invalid n: {n!r}"
    if not isinstance(s, str):
        return False, f"pauli must be a string, got {type(s).__name__}"
    if len(s) != nn:
        return False, f"length {len(s)} != n ({nn})"
    mapping = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    try:
        xz = [mapping[c] for c in s]
    except KeyError:
        bad = next(c for c in s if c not in mapping)
        return False, f"character {bad!r} outside IXYZ"
    return True, ([p[0] for p in xz], [p[1] for p in xz])


def _split_generator(gen) -> tuple[bool, object, object, object]:
    """Normalize a generator into (phase_ok, phase, pauli_string, error).

    Plain strings imply phase +1. Tuples (phase, string) accept phases
    1 / "+1" / "+" only; anything else is phase-unsupported (never silent).
    """
    if isinstance(gen, str):
        return True, 1, gen, ""
    if isinstance(gen, (list, tuple)) and len(gen) == 2:
        phase, s = gen[0], gen[1]
        if phase in (1, "+1", "+") and not isinstance(phase, bool):
            return True, 1, s, ""
        return False, None, None, "phase not supported"
    return (
        False,
        None,
        None,
        f"generator must be a string or (phase, string) pair, got {type(gen).__name__}",
    )


def _parse_generators(generators) -> tuple[bool, object, object]:
    """Parse a generator list into (n, rows, error).

    rows: list of (x_int, z_int) with x in low n bits, z in high n bits.
    """
    if not isinstance(generators, (list, tuple)):
        return False, None, f"generators must be a list or tuple, got {type(generators).__name__}"
    if len(generators) == 0:
        return False, None, "empty generator list"
    parsed: list[tuple[int, int]] = []
    n: int | None = None
    for idx, gen in enumerate(generators):
        ok, _phase, s, err = _split_generator(gen)
        if not ok:
            return False, None, f"generator {idx}: {err}"
        if not isinstance(s, str):
            return False, None, f"generator {idx}: pauli must be a string"
        if n is None:
            n = len(s)
            if n == 0:
                return False, None, "generator 0: empty pauli string"
        elif len(s) != n:
            return False, None, f"generator {idx}: inconsistent length {len(s)} != {n}"
        okp, payload = parse_pauli(s, n)
        if not okp:
            return False, None, f"generator {idx}: {payload}"
        xl, zl = payload
        xi = sum(b << i for i, b in enumerate(xl))
        zi = sum(b << i for i, b in enumerate(zl))
        parsed.append((xi, zi))
    assert n is not None
    return True, (n, parsed), ""


def commutes(a, b) -> tuple[bool, object]:
    """Symplectic product == 0 (binary Pauli pairs)."""
    pa = _valid_pauli_pair(a)
    pb = _valid_pauli_pair(b)
    if pa is None or pb is None:
        return False, "malformed pauli pair(s)"
    if len(pa[0]) != len(pb[0]):
        return False, "pauli pairs have different n"
    n = len(pa[0])
    mask = (1 << n) - 1
    ax = sum(v << i for i, v in enumerate(pa[0])) & mask
    az = sum(v << i for i, v in enumerate(pa[1])) & mask
    bx = sum(v << i for i, v in enumerate(pb[0])) & mask
    bz = sum(v << i for i, v in enumerate(pb[1])) & mask
    return True, _symplectic_int(ax, az, bx, bz, mask) == 0


def _rows_of(parsed: list[tuple[int, int]], n: int) -> list[int]:
    return [(xi | (zi << n)) for xi, zi in parsed]


def check_stabilizer(generators) -> tuple[bool, object]:
    """Pairwise commutation + GF(2) independence + supported phases."""
    ok, payload, err = _parse_generators(generators)
    if not ok:
        return False, err
    n, parsed = payload
    m = len(parsed)
    mask = (1 << n) - 1
    for i in range(m):
        for j in range(i + 1, m):
            ax, az = parsed[i]
            bx, bz = parsed[j]
            if _symplectic_int(ax & mask, az & mask, bx & mask, bz & mask, mask) != 0:
                return False, f"generators {i} and {j} do not commute"
    rank = _gf2_rank(_rows_of(parsed, n))
    if rank != m:
        return False, f"dependent generators: rank {rank} != {m}"
    k = n - m
    if k < 0:
        return False, f"negative k ({k}): more generators than qubits"
    return True, {"n": n, "k": k, "rank": rank}


def centralizer_contains(pauli, generators) -> tuple[bool, object]:
    """True iff <pauli, g> == 0 for every generator g."""
    pp = _valid_pauli_pair(pauli)
    if pp is None:
        return False, "malformed pauli pair"
    ok, payload, err = _parse_generators(generators)
    if not ok:
        return False, err
    n, parsed = payload
    if len(pp[0]) != n:
        return False, f"pauli length {len(pp[0])} != code n ({n})"
    mask = (1 << n) - 1
    px = sum(v << i for i, v in enumerate(pp[0])) & mask
    pz = sum(v << i for i, v in enumerate(pp[1])) & mask
    for xi, zi in parsed:
        if _symplectic_int(px, pz, xi & mask, zi & mask, mask) != 0:
            return True, False
    return True, True


def stabilizer_contains(pauli, generators) -> tuple[bool, object]:
    """True iff pauli lies in the GF(2)-span of the generator rows."""
    pp = _valid_pauli_pair(pauli)
    if pp is None:
        return False, "malformed pauli pair"
    ok, payload, err = _parse_generators(generators)
    if not ok:
        return False, err
    n, parsed = payload
    if len(pp[0]) != n:
        return False, f"pauli length {len(pp[0])} != code n ({n})"
    vec = _row_bits(pp[0], pp[1])
    return True, _in_span(vec, _rows_of(parsed, n))


def _weight_positions(n: int, w: int):
    return itertools.combinations(range(n), w)


def code_distance(generators) -> tuple[bool, object]:
    """Exact distance: lowest weight w in 1..n with a logical of weight w.

    Weight-ordered sweep (lexicographic position combos x XYZ assignments,
    deterministic, no randomness): the first Pauli in C(S) \\ S sets d.
    """
    ok, payload, err = _parse_generators(generators)
    if not ok:
        return False, err
    n, parsed = payload
    okc, payloadc = check_stabilizer(generators)
    if not okc:
        return False, payloadc
    k = payloadc["k"]
    if k < 0:
        return False, f"negative k ({k})"
    if k == 0:
        return False, "no logical operator found"
    rows = _rows_of(parsed, n)
    mask = (1 << n) - 1
    for w in range(1, n + 1):
        for positions in _weight_positions(n, w):
            for letters in itertools.product("XYZ", repeat=w):
                xi = 0
                zi = 0
                for p, letter in zip(positions, letters):
                    if letter in ("X", "Y"):
                        xi |= 1 << p
                    if letter in ("Z", "Y"):
                        zi |= 1 << p
                bad = False
                for gx, gz in parsed:
                    if _symplectic_int(xi, zi, gx & mask, gz & mask, mask) != 0:
                        bad = True
                        break
                if bad:
                    continue
                if _in_span(xi | (zi << n), rows):
                    continue
                chars = []
                for i in range(n):
                    xb = (xi >> i) & 1
                    zb = (zi >> i) & 1
                    chars.append("IXZY"[(zb << 1) | xb] if (xb or zb) else "I")
                return True, {"n": n, "k": k, "d": w, "logical": "".join(chars)}
    return False, "no logical operator found"
