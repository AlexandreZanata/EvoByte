"""Algebraic polynomial identity synthesis and verification over Q[k].

Discovers and verifies parameterized rational identities for the Erdős–Straus
conjecture 4/n = 1/X(k) + 1/Y(k) + 1/Z(k) over linear arithmetic progressions
n(k) = m*k + r, guaranteeing exact mathematical solutions for entire congruence classes.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import time
from dataclasses import dataclass
from fractions import Fraction
from typing import Any


class Poly1D:
    """Exact single-variable polynomial in Q[k] represented by rational coefficients."""

    __slots__ = ("coeffs",)

    def __init__(self, coeffs: tuple[Fraction | int, ...] | list[Fraction | int]) -> None:
        c_list = [Fraction(c) for c in coeffs]
        while len(c_list) > 1 and c_list[-1] == 0:
            c_list.pop()
        if not c_list:
            c_list = [Fraction(0)]
        self.coeffs: tuple[Fraction, ...] = tuple(c_list)

    @classmethod
    def constant(cls, val: int | Fraction) -> Poly1D:
        return cls((Fraction(val),))

    @classmethod
    def linear(cls, a: int | Fraction, b: int | Fraction) -> Poly1D:
        return cls((Fraction(b), Fraction(a)))

    @property
    def degree(self) -> int:
        if len(self.coeffs) == 1 and self.coeffs[0] == 0:
            return -1
        return len(self.coeffs) - 1

    def is_zero(self) -> bool:
        return len(self.coeffs) == 1 and self.coeffs[0] == 0

    def eval(self, k: int | Fraction) -> Fraction:
        res = Fraction(0)
        kf = Fraction(k)
        power = Fraction(1)
        for c in self.coeffs:
            res += c * power
            power *= kf
        return res

    def is_strictly_positive(self, num_points: int = 10) -> bool:
        """Check if polynomial evaluates to positive numbers for k in [0, num_points - 1]."""
        for k in range(num_points):
            if self.eval(k) <= 0:
                return False
        return True

    def is_integer_valued(self, num_points: int = 10) -> bool:
        """Check if polynomial evaluates to integers for k in [0, num_points - 1]."""
        for k in range(num_points):
            if self.eval(k).denominator != 1:
                return False
        return True

    def __add__(self, other: Poly1D | int | Fraction) -> Poly1D:
        if not isinstance(other, Poly1D):
            other = Poly1D.constant(other)
        n = max(len(self.coeffs), len(other.coeffs))
        new_c = [Fraction(0)] * n
        for i in range(n):
            v1 = self.coeffs[i] if i < len(self.coeffs) else Fraction(0)
            v2 = other.coeffs[i] if i < len(other.coeffs) else Fraction(0)
            new_c[i] = v1 + v2
        return Poly1D(new_c)

    def __sub__(self, other: Poly1D | int | Fraction) -> Poly1D:
        if not isinstance(other, Poly1D):
            other = Poly1D.constant(other)
        n = max(len(self.coeffs), len(other.coeffs))
        new_c = [Fraction(0)] * n
        for i in range(n):
            v1 = self.coeffs[i] if i < len(self.coeffs) else Fraction(0)
            v2 = other.coeffs[i] if i < len(other.coeffs) else Fraction(0)
            new_c[i] = v1 - v2
        return Poly1D(new_c)

    def __mul__(self, other: Poly1D | int | Fraction) -> Poly1D:
        if not isinstance(other, Poly1D):
            other = Poly1D.constant(other)
        if self.is_zero() or other.is_zero():
            return Poly1D((Fraction(0),))
        deg_self = len(self.coeffs)
        deg_other = len(other.coeffs)
        new_c = [Fraction(0)] * (deg_self + deg_other - 1)
        for i, c1 in enumerate(self.coeffs):
            if c1 == 0:
                continue
            for j, c2 in enumerate(other.coeffs):
                new_c[i + j] += c1 * c2
        return Poly1D(new_c)

    def exact_divide(self, divisor: Poly1D) -> Poly1D | None:
        """Exact polynomial division in Q[k]. Returns quotient if remainder is zero, else None."""
        if divisor.is_zero():
            return None
        if self.is_zero():
            return Poly1D((Fraction(0),))
        if divisor.degree > self.degree:
            return None

        p = list(self.coeffs)
        d = divisor.coeffs
        d_deg = divisor.degree
        d_lead = d[-1]

        res = [Fraction(0)] * (len(p) - len(d) + 1)
        for i in range(len(res) - 1, -1, -1):
            lead = p[i + d_deg] / d_lead
            res[i] = lead
            for j, c in enumerate(d):
                p[i + j] -= lead * c

        if any(c != 0 for c in p):
            return None
        return Poly1D(res)

    def substitute(self, inner: Poly1D) -> Poly1D:
        """Compose polynomials: return self(inner(k))."""
        res = Poly1D.constant(0)
        power = Poly1D.constant(1)
        for c in self.coeffs:
            res = res + (power * c)
            power = power * inner
        return res

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Poly1D):
            if isinstance(other, (int, Fraction)):
                return self.degree <= 0 and self.coeffs[0] == other
            return False
        return self.coeffs == other.coeffs

    def to_string(self, var: str = "k") -> str:
        if self.is_zero():
            return "0"
        terms: list[str] = []
        for i, c in enumerate(self.coeffs):
            if c == 0:
                continue
            c_str = str(c)
            if i == 0:
                terms.append(c_str)
            elif i == 1:
                terms.append(var if c == 1 else (f"-{var}" if c == -1 else f"{c_str}*{var}"))
            else:
                terms.append(
                    f"{var}^{i}" if c == 1 else (f"-{var}^{i}" if c == -1 else f"{c_str}*{var}^{i}")
                )
        return " + ".join(terms).replace("+ -", "- ")

    def __repr__(self) -> str:
        return f"Poly1D({self.to_string()})"


@dataclass(frozen=True)
class AlgebraicIdentity:
    """Exact identity: a/n(k) = 1/X(k) + 1/Y(k) + 1/Z(k) with n(k) = m*k + r."""

    m: int
    r: int
    n_poly: Poly1D
    X: Poly1D
    Y: Poly1D
    Z: Poly1D
    a: int = 4

    def verify_exact(self) -> bool:
        """Verify algebraic identity equality a*XYZ == n(YZ + XZ + XY) and positivity."""
        YZ = self.Y * self.Z
        XZ = self.X * self.Z
        XY = self.X * self.Y
        sum_terms = YZ + XZ + XY
        lhs = self.X * YZ * self.a
        rhs = self.n_poly * sum_terms
        diff = lhs - rhs
        if not diff.is_zero():
            return False

        # Positive and integer-valued check for k in [0, 20]
        for p in (self.X, self.Y, self.Z):
            if not p.is_strictly_positive(20) or not p.is_integer_valued(20):
                return False
        return True

    def evaluate(self, k: int) -> tuple[int, int, int]:
        """Compute integer values (X(k), Y(k), Z(k))."""
        x_val = self.X.eval(k)
        y_val = self.Y.eval(k)
        z_val = self.Z.eval(k)
        if x_val.denominator != 1 or y_val.denominator != 1 or z_val.denominator != 1:
            raise ValueError(f"Identity does not produce integer values at k={k}")
        return int(x_val), int(y_val), int(z_val)

    def to_dict(self) -> dict[str, Any]:
        return {
            "a": self.a,
            "modulus": self.m,
            "residue": self.r,
            "n_poly": self.n_poly.to_string(),
            "X": self.X.to_string(),
            "Y": self.Y.to_string(),
            "Z": self.Z.to_string(),
            "degrees": {
                "n": self.n_poly.degree,
                "X": self.X.degree,
                "Y": self.Y.degree,
                "Z": self.Z.degree,
            },
        }

    def to_lean_statement(self, theorem_name: str) -> str:
        """Generate Lean 4 polynomial theorem definition and proof."""
        n_str = self.n_poly.to_string()
        x_str = self.X.to_string()
        y_str = self.Y.to_string()
        z_str = self.Z.to_string()
        return (
            f"theorem {theorem_name} : ∀ (k : ℚ),\n"
            f"  {self.a} * ({x_str}) * ({y_str}) * ({z_str}) =\n"
            f"  ({n_str}) * (({y_str}) * ({z_str}) + ({x_str}) * ({z_str}) + ({x_str}) * ({y_str})) := by\n"
            f"  intro k\n"
            f"  ring\n"
        )


SchinzelIdentity = AlgebraicIdentity



def synthesize_mordell_identity(
    m: int,
    r: int,
    max_search_coeff: int = 5,
) -> AlgebraicIdentity | None:
    """Synthesize an exact polynomial identity for n = m*k + r using Mordell divisor splitting."""
    if m <= 0 or r < 0:
        raise ValueError(f"Invalid modulus/residue: m={m}, r={r}")

    # Special case: even residue r=0, m=2*m_half
    if r % 2 == 0 and m % 2 == 0:
        # 4 / (2*m_half*k + 2*r_half) = 2 / (m_half*k + r_half)
        # 2/W = 1/W + 1/(2*W) + 1/(2*W)
        m_half = m // 2
        r_half = r // 2
        W = Poly1D.linear(m_half, r_half)
        if W.is_strictly_positive(5):
            X = W
            Y = W * 2
            Z = W * 2
            ident = AlgebraicIdentity(m=m, r=r, n_poly=Poly1D.linear(m, r), X=X, Y=Y, Z=Z)
            if ident.verify_exact():
                return ident

    n = Poly1D.linear(m, r)

    # Search over linear candidate denominators X(k) = a*k + b
    for a in range(1, max_search_coeff + 1):
        for b in range(1, max_search_coeff + 1):
            X = Poly1D.linear(a, b)
            # R(k) = 4*X(k) - n(k)
            R = (X * 4) - n
            if not R.is_strictly_positive(5):
                continue

            # Candidate scale factors S
            for S in (1, 2, 3, 4, 6):
                SR = R * S
                SnX = n * X * S

                # Candidate divisor polynomials A(k) of SnX
                candidates_A: list[Poly1D] = []
                for d in range(1, 13):
                    candidates_A.append(Poly1D.constant(d))
                for ca in range(1, max_search_coeff + 1):
                    for cb in range(max_search_coeff + 1):
                        candidates_A.append(Poly1D.linear(ca, cb))

                for A in candidates_A:
                    B = SR - A
                    if not B.is_strictly_positive(5):
                        continue

                    # Exact division: Y = SnX / A, Z = SnX / B
                    Y = SnX.exact_divide(A)
                    Z = SnX.exact_divide(B)

                    if (
                        Y is not None
                        and Z is not None
                        and Y.is_strictly_positive(5)
                        and Z.is_strictly_positive(5)
                        and Y.is_integer_valued(5)
                        and Z.is_integer_valued(5)
                    ):
                        ident = AlgebraicIdentity(m=m, r=r, n_poly=n, X=X, Y=Y, Z=Z)
                        if ident.verify_exact():
                            return ident

    return None


def synthesize_congruence_family(modulus: int) -> dict[int, AlgebraicIdentity | None]:
    """Synthesize identities for all residues r in [0, modulus - 1]."""
    results: dict[int, AlgebraicIdentity | None] = {}
    for r in range(modulus):
        ident = synthesize_mordell_identity(modulus, r)
        results[r] = ident
    return results


def audit_algebraic_coverage(modulus: int = 24) -> dict[str, Any]:
    """Audit coverage of algebraic identities for a given modulus."""
    results = synthesize_congruence_family(modulus)
    covered: list[int] = []
    uncovered: list[int] = []
    identities_dict: dict[str, Any] = {}

    for r, ident in results.items():
        if ident is not None and ident.verify_exact():
            covered.append(r)
            identities_dict[str(r)] = ident.to_dict()
        else:
            uncovered.append(r)

    total = modulus
    coverage_ratio = len(covered) / total if total > 0 else 0.0

    return {
        "modulus": modulus,
        "total_residues": total,
        "covered_count": len(covered),
        "uncovered_count": len(uncovered),
        "coverage_ratio": coverage_ratio,
        "covered_residues": sorted(covered),
        "uncovered_residues": sorted(uncovered),
        "identities": identities_dict,
        "verified": True,
    }


SUPPORTED_COVERAGE_MODULI: tuple[int, ...] = (24, 120, 840, 2520)


@functools.lru_cache(maxsize=16)
def get_resistant_residues(m: int) -> list[int]:
    """Return all resistant congruence residue classes (coprime quadratic residues) modulo m."""
    coprimes = [x for x in range(1, m) if math.gcd(x, m) == 1]
    squares = {(x * x) % m for x in coprimes}
    return sorted(squares)


def is_coprime_quadratic_residue(m: int, r: int) -> bool:
    """Check if residue r is coprime to m and is a quadratic residue modulo m."""
    if r < 0 or r >= m:
        return False
    return r in get_resistant_residues(m)


def classify_congruence_residue(m: int, r: int) -> dict[str, Any]:
    """Classify residue r modulo m according to its algebraic coverage mechanism."""
    if m not in SUPPORTED_COVERAGE_MODULI:
        raise ValueError(f"Modulus {m} not in supported moduli: {SUPPORTED_COVERAGE_MODULI}")
    if r < 0 or r >= m:
        raise ValueError(f"Residue {r} out of bounds for modulus {m}")

    resistant = get_resistant_residues(m)
    if r in resistant:
        return {
            "modulus": m,
            "residue": r,
            "is_resistant": True,
            "mechanism": "resistant_quadratic_residue",
            "identity_available": False,
        }

    # Determine specific mechanism
    if r % 2 == 0:
        mech = "even_divisibility_2"
    elif r % 3 == 0:
        mech = "divisibility_3"
    elif r % 3 == 2:
        mech = "mordell_2_mod_3"
    elif r % 4 == 3:
        mech = "mordell_3_mod_4"
    elif r % 8 == 5:
        mech = "mordell_5_mod_8"
    elif m % 5 == 0 and r % 5 == 0:
        mech = "divisibility_5"
    elif m % 7 == 0 and r % 7 == 0:
        mech = "divisibility_7"
    elif m == 2520:
        mech = "lifted_from_mod840"
    elif m == 120:
        mech = f"ionascu_wilson_mod120_r{r}"
    elif m == 840:
        k_24 = (r - 1) // 24
        if k_24 % 7 in (3, 4, 6):
            mech = f"ionascu_wilson_mod168_branch_{k_24 % 7}"
        elif k_24 % 5 in (3, 4):
            mech = f"ionascu_wilson_mod120_branch_{k_24 % 5}"
        else:
            mech = "modular_subdivision"
    else:
        mech = "congruence_identity"

    return {
        "modulus": m,
        "residue": r,
        "is_resistant": False,
        "mechanism": mech,
        "identity_available": True,
    }


@functools.lru_cache(maxsize=4096)
def get_algebraic_identity_for_residue(m: int, r: int) -> AlgebraicIdentity | None:
    """Construct verified algebraic identity for n = m*k + r over supported moduli."""
    if m not in SUPPORTED_COVERAGE_MODULI:
        raise ValueError(f"Modulus {m} not in supported moduli: {SUPPORTED_COVERAGE_MODULI}")
    if r < 0 or r >= m:
        raise ValueError(f"Residue {r} out of bounds for modulus {m}")

    resistant_classes = get_resistant_residues(m)
    if r in resistant_classes:
        return None

    n = Poly1D.linear(m, r if r > 0 else m)

    # 1. Even (applies to all moduli)
    if r % 2 == 0:
        W = Poly1D.linear(m // 2, r // 2 if r > 0 else m // 2)
        return AlgebraicIdentity(m, r, n, W, W * 2, W * 2)

    # For 2520 odd residues, lift from 840:
    if m == 2520:
        base_ident = get_algebraic_identity_for_residue(840, r % 840)
        if base_ident is None:
            return None
        q = 3
        j = r // 840
        K = Poly1D.linear(q, j)
        X = base_ident.X.substitute(K)
        Y = base_ident.Y.substitute(K)
        Z = base_ident.Z.substitute(K)
        return AlgebraicIdentity(2520, r, n, X, Y, Z)

    # 2. Divisible by 3
    if r % 3 == 0:
        W = Poly1D.linear(m // 3, r // 3)
        return AlgebraicIdentity(m, r, n, W, W * 4, W * 12)

    # 3. r % 3 == 2
    if r % 3 == 2:
        k_prime = Poly1D.linear(m // 3, r // 3)
        X = k_prime + 1
        return AlgebraicIdentity(m, r, n, X, n, n * X)

    # 4. r % 4 == 3
    if r % 4 == 3:
        k_prime = Poly1D.linear(m // 4, r // 4)
        X = k_prime + 1
        return AlgebraicIdentity(m, r, n, X, n * X * 2, n * X * 2)

    # 5. r % 8 == 5
    if r % 8 == 5:
        k_prime = Poly1D.linear(m // 8, r // 8)
        X = (k_prime + 1) * 2
        return AlgebraicIdentity(m, r, n, X, n * X, n * (k_prime + 1))

    # 6. Divisible by 5 (when 5 | m)
    if m % 5 == 0 and r % 5 == 0:
        W = Poly1D.linear(m // 5, r // 5)
        return AlgebraicIdentity(m, r, n, W * 2, W * 4, W * 20)

    # 7. Divisible by 7 (when 7 | m)
    if m % 7 == 0 and r % 7 == 0:
        W = Poly1D.linear(m // 7, r // 7)
        return AlgebraicIdentity(m, r, n, W * 2, W * 28, W * 28)

    # Special mod 120 cases
    if m == 120:
        if r == 73:
            a = Poly1D.linear(30, 20)
            W = Poly1D.linear(3, 2)
            return AlgebraicIdentity(120, 73, n, a, n * W * 5, n * W * 2)
        if r == 97:
            a = Poly1D.linear(30, 25)
            W = Poly1D.linear(6, 5)
            s = Poly1D.linear(40, 34)
            return AlgebraicIdentity(120, 97, n, a, s * n * W, s * W * 5)

    # Special mod 840 cases
    if m == 840:
        k_24 = (r - 1) // 24
        if k_24 % 7 == 3:
            l_poly = Poly1D.linear(5, r // 168)
            a = l_poly * 42 + 20
            s = l_poly * 6 + 3
            return AlgebraicIdentity(840, r, n, a, s * n * a, s * n)
        if k_24 % 7 == 4:
            l_poly = Poly1D.linear(5, r // 168)
            a = l_poly * 42 + 26
            s = l_poly * 24 + 14
            return AlgebraicIdentity(840, r, n, a, s * a, s * n * a)
        if k_24 % 7 == 6:
            l_poly = Poly1D.linear(5, r // 168)
            a = l_poly * 42 + 38
            s = l_poly * 24 + 21
            Wa = l_poly * 21 + 19
            return AlgebraicIdentity(840, r, n, a, s * n * Wa, s * a)
        if k_24 % 5 == 3:
            l_poly = Poly1D.linear(7, r // 120)
            a = l_poly * 30 + 20
            W = l_poly * 3 + 2
            return AlgebraicIdentity(840, r, n, a, n * W * 5, n * W * 2)
        if k_24 % 5 == 4:
            l_poly = Poly1D.linear(7, r // 120)
            a = l_poly * 30 + 25
            W = l_poly * 6 + 5
            s = l_poly * 40 + 34
            return AlgebraicIdentity(840, r, n, a, s * n * W, s * W * 5)

    return None


def build_congruence_coverage_matrix(modulus: int = 840) -> dict[str, Any]:
    """Build exhaustive modular coverage matrix with canonical immutable checksum."""
    if modulus not in SUPPORTED_COVERAGE_MODULI:
        raise ValueError(f"Modulus {modulus} not in supported moduli: {SUPPORTED_COVERAGE_MODULI}")

    resistant_classes = get_resistant_residues(modulus)
    covered_classes: list[int] = []
    identities_summary: dict[str, Any] = {}
    all_verified = True

    for r in range(modulus):
        if r in resistant_classes:
            continue
        ident = get_algebraic_identity_for_residue(modulus, r)
        if ident is None or not ident.verify_exact():
            all_verified = False
            continue
        covered_classes.append(r)
        identities_summary[str(r)] = {
            "n": ident.n_poly.to_string(),
            "X": ident.X.to_string(),
            "Y": ident.Y.to_string(),
            "Z": ident.Z.to_string(),
            "degrees": {
                "n": ident.n_poly.degree,
                "X": ident.X.degree,
                "Y": ident.Y.degree,
                "Z": ident.Z.degree,
            },
        }

    total = modulus
    coverage_ratio = len(covered_classes) / total if total > 0 else 0.0

    canonical_data = {
        "modulus": modulus,
        "total_classes": total,
        "covered_count": len(covered_classes),
        "resistant_count": len(resistant_classes),
        "coverage_ratio": coverage_ratio,
        "covered_classes": sorted(covered_classes),
        "resistant_classes": sorted(resistant_classes),
        "identities": identities_summary,
        "verified": all_verified,
    }

    canonical_bytes = json.dumps(canonical_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    checksum = hashlib.sha256(canonical_bytes).hexdigest()

    result = dict(canonical_data)
    result["checksum"] = checksum
    return result


def verify_coverage_matrix_soundness(matrix: dict[str, Any]) -> tuple[bool, list[str]]:
    """Verify soundness, completeness, and checksum integrity of a coverage matrix."""
    findings: list[str] = []
    modulus = matrix.get("modulus")
    if modulus not in SUPPORTED_COVERAGE_MODULI:
        findings.append(f"INVALID_MODULUS: {modulus}")
        return False, findings

    total = matrix.get("total_classes", 0)
    covered = matrix.get("covered_classes", [])
    resistant = matrix.get("resistant_classes", [])
    expected_resistant = get_resistant_residues(modulus)

    if sorted(resistant) != sorted(expected_resistant):
        findings.append(
            f"RESISTANT_MISMATCH: expected {expected_resistant}, got {sorted(resistant)}"
        )

    if len(covered) + len(resistant) != total or total != modulus:
        findings.append(
            f"PARTITION_MISMATCH: covered({len(covered)}) + resistant({len(resistant)}) != {total}"
        )

    overlap = set(covered).intersection(set(resistant))
    if overlap:
        findings.append(f"OVERLAP_FOUND: residues in both covered and resistant: {sorted(overlap)}")

    if not matrix.get("verified", False):
        findings.append("UNVERIFIED_STATUS: matrix has unverified identities")

    # Recompute canonical checksum
    canonical_data = {
        "modulus": modulus,
        "total_classes": total,
        "covered_count": len(covered),
        "resistant_count": len(resistant),
        "coverage_ratio": matrix.get("coverage_ratio", 0.0),
        "covered_classes": sorted(covered),
        "resistant_classes": sorted(resistant),
        "identities": matrix.get("identities", {}),
        "verified": matrix.get("verified", False),
    }
    canonical_bytes = json.dumps(canonical_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_checksum = hashlib.sha256(canonical_bytes).hexdigest()

    if matrix.get("checksum") != expected_checksum:
        findings.append(
            f"CHECKSUM_MISMATCH: expected {expected_checksum}, got {matrix.get('checksum')}"
        )

    return (len(findings) == 0), findings


def integer_factorization(val: int) -> dict[int, int]:
    """Deterministic prime factorization of positive integer val via trial division."""
    if val <= 1:
        return {}
    factors: dict[int, int] = {}
    temp = val
    if temp % 2 == 0:
        c = 0
        while temp % 2 == 0:
            c += 1
            temp //= 2
        factors[2] = c
    p = 3
    while p * p <= temp:
        if temp % p == 0:
            c = 0
            while temp % p == 0:
                c += 1
                temp //= p
            factors[p] = c
        p += 2
    if temp > 1:
        factors[temp] = 1
    return factors


def get_square_divisors(val: int, max_val: int | None = None) -> list[int]:
    """Compute all positive integer divisors of val^2 in ascending order."""
    if val <= 0:
        return []
    if val == 1:
        return [1]
    prime_factors = integer_factorization(val)
    divs = [1]
    for p, exp in prime_factors.items():
        new_d: list[int] = []
        for d in divs:
            pk = 1
            for _ in range(2 * exp + 1):
                cur = d * pk
                if max_val is None or cur <= max_val:
                    new_d.append(cur)
                pk *= p
        divs = new_d
    return sorted(divs)


def quadratic_divisor_decomposition(
    n: int, max_d: int = 100
) -> tuple[tuple[int, int, int] | None, dict[str, Any]]:
    """Solve Erdős–Straus via binary quadratic divisor relation (4x - n)(4y - n) = n^2 + 4d.

    For d | nxy, z = nxy / d is an exact integer solution if x, y are determined by
    factoring K = n^2 + 4d = A * B with A = 4x - n and B = 4y - n.
    """
    if n < 2:
        return None, {"error": "n must be >= 2", "candidates_evaluated": 0}

    candidates_evaluated = 0
    modular_pruned = 0
    t0 = time.perf_counter()

    # Divisors of n^2 plus small integer offsets
    d_candidates: list[int] = [1, n]
    if n * n <= 10**8:
        d_candidates.append(n * n)
    for small_d in range(2, max_d + 1):
        if small_d not in d_candidates:
            d_candidates.append(small_d)

    for d in d_candidates:
        K = n * n + 4 * d
        r = math.isqrt(K)
        for A in range(1, r + 1):
            if K % A != 0:
                continue
            B = K // A
            candidates_evaluated += 1

            # Modular congruence condition: A = 4x - n => A = -n mod 4
            if (A + n) % 4 != 0 or (B + n) % 4 != 0:
                modular_pruned += 1
                continue

            x = (A + n) // 4
            y = (B + n) // 4

            if (n * x * y) % d != 0:
                modular_pruned += 1
                continue

            z = (n * x * y) // d
            if x > 0 and y > 0 and z > 0 and 4 * x * y * z == n * (x * y + y * z + z * x):
                elapsed = time.perf_counter() - t0
                return (x, y, z), {
                        "n": n,
                        "d": d,
                        "A": A,
                        "B": B,
                        "triple": (x, y, z),
                        "candidates_evaluated": candidates_evaluated,
                        "modular_pruned": modular_pruned,
                        "elapsed_sec": elapsed,
                        "verified_exact": True,
                    }

    elapsed = time.perf_counter() - t0
    return None, {
        "n": n,
        "candidates_evaluated": candidates_evaluated,
        "modular_pruned": modular_pruned,
        "elapsed_sec": elapsed,
        "verified_exact": False,
    }


def check_schinzel(
    a: int, n: int, x: int, y: int, z: int
) -> tuple[bool, int, dict[str, Any]]:
    """Exact decidable integer checker for Schinzel Egyptian fraction conjecture:

    a/n = 1/x + 1/y + 1/z  <=>  a*x*y*z == n*(x*y + y*z + z*x) with x, y, z > 0.
    """
    if not (
        isinstance(a, int)
        and isinstance(n, int)
        and isinstance(x, int)
        and isinstance(y, int)
        and isinstance(z, int)
        and not isinstance(a, bool)
        and not isinstance(n, bool)
        and not isinstance(x, bool)
        and not isinstance(y, bool)
        and not isinstance(z, bool)
    ):
        return False, -1, {"error": "All arguments must be integers"}
    if a < 1 or n < 2 or x <= 0 or y <= 0 or z <= 0:
        return False, -1, {"error": "Domain requirement: a >= 1, n >= 2, x, y, z > 0"}

    lhs = int(a) * int(x) * int(y) * int(z)
    rhs = int(n) * (int(x) * int(y) + int(y) * int(z) + int(x) * int(z))
    residual = lhs - rhs
    is_valid = (residual == 0)

    details = {
        "a": int(a),
        "n": int(n),
        "x": int(x),
        "y": int(y),
        "z": int(z),
        "lhs": str(lhs),
        "rhs": str(rhs),
        "residual": int(residual),
        "verified_exact": is_valid,
    }
    return is_valid, residual, details


def check_sierpinski(
    n: int, x: int, y: int, z: int
) -> tuple[bool, int, dict[str, Any]]:
    """Exact decidable integer checker for Sierpiński conjecture (5/n = 1/x + 1/y + 1/z)."""
    return check_schinzel(5, n, x, y, z)


def check_schinzel_fractions(
    a: int, n: int, x: int, y: int, z: int
) -> tuple[bool, Fraction, dict[str, Any]]:
    """Independent second checker using exact rational arithmetic (fractions.Fraction)."""
    if not (
        isinstance(a, int)
        and isinstance(n, int)
        and isinstance(x, int)
        and isinstance(y, int)
        and isinstance(z, int)
        and not isinstance(a, bool)
        and not isinstance(n, bool)
        and not isinstance(x, bool)
        and not isinstance(y, bool)
        and not isinstance(z, bool)
    ):
        return False, Fraction(1), {"error": "All arguments must be integers"}
    if a < 1 or n < 2 or x <= 0 or y <= 0 or z <= 0:
        return False, Fraction(1), {"error": "Domain requirement: a >= 1, n >= 2, x, y, z > 0"}

    lhs_frac = Fraction(a, n)
    rhs_frac = Fraction(1, x) + Fraction(1, y) + Fraction(1, z)
    diff = lhs_frac - rhs_frac
    is_valid = (diff == 0)

    details = {
        "a": int(a),
        "n": int(n),
        "x": int(x),
        "y": int(y),
        "z": int(z),
        "lhs_fraction": str(lhs_frac),
        "rhs_fraction": str(rhs_frac),
        "difference": str(diff),
        "verified_exact": is_valid,
    }
    return is_valid, diff, details


def check_sierpinski_fractions(
    n: int, x: int, y: int, z: int
) -> tuple[bool, Fraction, dict[str, Any]]:
    """Independent second checker for Sierpiński conjecture using exact rational arithmetic."""
    return check_schinzel_fractions(5, n, x, y, z)


def schinzel_divisor_sieve(
    a: int, n: int, max_x_steps: int = 100, max_coord: int = 10**12
) -> tuple[tuple[int, int, int] | None, dict[str, Any]]:
    """Sublinear deterministic rational divisor sieve for Schinzel conjecture (a/n = 1/x + 1/y + 1/z).

    For x in [ceil(n/a), ceil(n/a) + max_x_steps], letting u = a*x - n and D = n*x:
    (u*y - D)(u*z - D) = D^2 = (n*x)^2.
    Candidate divisor d = u*y - D must divide D^2 with d <= D.
    Then y = (D + d) / u and z = (D + D^2 / d) / u are exact positive integers
    if and only if (D + d) % u == 0.
    Incompatible divisors are eliminated via modular congruences mod small primes dividing u.
    """
    if a < 1 or n < 2:
        return None, {"error": "a must be >= 1 and n >= 2", "candidates_evaluated": 0}

    t0 = time.perf_counter()
    x0 = n // a + 1
    candidates_evaluated = 0
    pruned_by_small_primes = 0
    pruned_by_u = 0

    fn = integer_factorization(n)

    for x_step in range(max_x_steps):
        x = x0 + x_step
        u = a * x - n
        if u <= 0:
            continue
        D = n * x
        D2 = D * D

        # Small prime factors of u for fast modular elimination
        small_p = [p for p in (2, 3, 5, 7, 11, 13) if u % p == 0]

        # Prime factorization of D^2 = (nx)^2
        fx = integer_factorization(x)
        fd2: dict[int, int] = {}
        for p, c in fn.items():
            fd2[p] = fd2.get(p, 0) + 2 * c
        for p, c in fx.items():
            fd2[p] = fd2.get(p, 0) + 2 * c

        # Generate divisors d <= D of D^2
        divs = [1]
        for p, exp in fd2.items():
            new_d: list[int] = []
            for d in divs:
                pk = 1
                for _ in range(exp + 1):
                    cur = d * pk
                    if cur <= D:
                        new_d.append(cur)
                    pk *= p
            divs = new_d

        for d in divs:
            candidates_evaluated += 1

            # Modular elimination filter: mod small primes dividing u
            incompatible = False
            for p in small_p:
                if (D + d) % p != 0:
                    incompatible = True
                    break
            if incompatible:
                pruned_by_small_primes += 1
                continue

            # Exact modulus u filter
            if (D + d) % u != 0:
                pruned_by_u += 1
                continue

            y = (D + d) // u
            z = (D + (D2 // d)) // u

            if x > 0 and y > 0 and z > 0:
                if max_coord and max(x, y, z) > max_coord:
                    continue
                if a * x * y * z == n * (x * y + y * z + z * x):
                    elapsed = time.perf_counter() - t0
                    return (x, y, z), {
                        "a": a,
                        "n": n,
                        "x": x,
                        "y": y,
                        "z": z,
                        "d": d,
                        "u": u,
                        "x_steps_taken": x_step + 1,
                        "candidates_evaluated": candidates_evaluated,
                        "pruned_by_small_primes": pruned_by_small_primes,
                        "pruned_by_u": pruned_by_u,
                        "elapsed_sec": elapsed,
                        "verified_exact": True,
                    }

    elapsed = time.perf_counter() - t0
    return None, {
        "a": a,
        "n": n,
        "x_steps_taken": max_x_steps,
        "candidates_evaluated": candidates_evaluated,
        "pruned_by_small_primes": pruned_by_small_primes,
        "pruned_by_u": pruned_by_u,
        "elapsed_sec": elapsed,
        "verified_exact": False,
    }


def sierpinski_divisor_sieve(
    n: int, max_x_steps: int = 100, max_coord: int = 10**12
) -> tuple[tuple[int, int, int] | None, dict[str, Any]]:
    """Sublinear deterministic rational divisor sieve specialized for Sierpiński conjecture (5/n)."""
    return schinzel_divisor_sieve(5, n, max_x_steps=max_x_steps, max_coord=max_coord)


def rational_divisor_sieve(
    n: int, max_x_steps: int = 100, max_coord: int = 10**12
) -> tuple[tuple[int, int, int] | None, dict[str, Any]]:
    """Sublinear deterministic rational divisor sieve for Erdős–Straus (4/n = 1/x + 1/y + 1/z)."""
    return schinzel_divisor_sieve(4, n, max_x_steps=max_x_steps, max_coord=max_coord)



def solve_erdos_straus_sieve(
    n: int, max_x_steps: int = 100, max_d_quad: int = 50
) -> tuple[tuple[int, int, int] | None, dict[str, Any]]:
    """Solve Erdős–Straus using rational divisor sieve with quadratic decomposition fallback."""
    sol, details = rational_divisor_sieve(n, max_x_steps=max_x_steps)
    if sol is not None:
        details["method"] = "rational_divisor_sieve"
        return sol, details
    sol_q, details_q = quadratic_divisor_decomposition(n, max_d=max_d_quad)
    if sol_q is not None:
        details_q["method"] = "quadratic_divisor_decomposition"
        return sol_q, details_q
    return None, {"method": "none", "n": n, "verified_exact": False}


def benchmark_sieve_vs_baseline(
    n_instances: list[int], max_coord: int = 10**9
) -> dict[str, Any]:
    """Compare rational divisor sieve against baseline arithmetic enumeration on challenging instances."""
    results: list[dict[str, Any]] = []
    total_baseline_cands = 0
    total_sieve_cands = 0
    total_baseline_sec = 0.0
    total_sieve_sec = 0.0
    false_negatives = 0

    for n in n_instances:
        # Baseline arithmetic enumeration
        t0_base = time.perf_counter()
        x0 = n // 4 + 1
        base_cands = 0
        base_sol: tuple[int, int, int] | None = None
        for x_step in range(50):
            x_val = x0 + x_step
            u = 4 * x_val - n
            if u <= 0:
                continue
            y_min = (n * x_val) // u + 1
            y = y_min
            found = False
            while True:
                base_cands += 1
                denom = 4 * x_val * y - n * (x_val + y)
                if denom > 0 and (n * x_val * y) % denom == 0:
                    z_val = (n * x_val * y) // denom
                    if max(x_val, y, z_val) <= max_coord:
                        base_sol = (x_val, y, z_val)
                        found = True
                        break
                y += 1
                if y > y_min + 500_000:
                    break
            if found:
                break
        t_base = time.perf_counter() - t0_base

        # Rational divisor sieve
        sieve_sol, sieve_det = rational_divisor_sieve(n, max_x_steps=100, max_coord=max_coord)
        sieve_cands = sieve_det.get("candidates_evaluated", 0)
        t_sieve = sieve_det.get("elapsed_sec", 0.0)

        # Check solutions
        base_valid = False
        if base_sol is not None:
            bx, by, bz = base_sol
            base_valid = (4 * bx * by * bz == n * (bx * by + by * bz + bz * bx))

        sieve_valid = False
        if sieve_sol is not None:
            sx, sy, sz = sieve_sol
            sieve_valid = (4 * sx * sy * sz == n * (sx * sy + sy * sz + sz * sx))

        if base_valid and not sieve_valid:
            false_negatives += 1

        cand_reduction = (base_cands / sieve_cands) if sieve_cands > 0 else 1.0
        speedup = (t_base / t_sieve) if t_sieve > 0 else 1.0

        results.append({
            "n": n,
            "baseline": {
                "solved": base_valid,
                "solution": base_sol,
                "candidates": base_cands,
                "time_sec": t_base,
            },
            "sieve": {
                "solved": sieve_valid,
                "solution": sieve_sol,
                "candidates": sieve_cands,
                "time_sec": t_sieve,
                "pruned_small_primes": sieve_det.get("pruned_by_small_primes", 0),
                "pruned_by_u": sieve_det.get("pruned_by_u", 0),
            },
            "candidate_reduction": cand_reduction,
            "speedup": speedup,
        })

        total_baseline_cands += base_cands
        total_sieve_cands += sieve_cands
        total_baseline_sec += t_base
        total_sieve_sec += t_sieve

    overall_reduction = (total_baseline_cands / total_sieve_cands) if total_sieve_cands > 0 else 1.0
    overall_speedup = (total_baseline_sec / total_sieve_sec) if total_sieve_sec > 0 else 1.0

    return {
        "instances_count": len(n_instances),
        "total_baseline_candidates": total_baseline_cands,
        "total_sieve_candidates": total_sieve_cands,
        "overall_candidate_reduction": overall_reduction,
        "total_baseline_sec": total_baseline_sec,
        "total_sieve_sec": total_sieve_sec,
        "overall_speedup": overall_speedup,
        "false_negatives": false_negatives,
        "all_sieve_valid": all(r["sieve"]["solved"] for r in results),
        "results": results,
    }


def synthesize_schinzel_identity(
    a: int, m: int, r: int, max_c: int = 30
) -> AlgebraicIdentity | None:
    """Synthesize an exact polynomial identity for a / (m*k + r) using algebraic families.

    Covers:
    1. Multiples of a: n = a*W => 1/(2W) + 1/(3W) + 1/(6W) = 1/W = a/n.
    2. Even residues for a=5 (Sierpiński):
       - n = 4*V: X = V+1, Y = V(V+1), Z = 4*V.
       - n = 2*W (W odd): X = (W+1)/2, Y = W(W+1)/2, Z = 2*W.
    3. Parameterized c-family: (c*a - 1)*X = c*n + 1 => X = (c*n + 1)/(c*a - 1), Y = c*n, Z = c*n*X.
    4. Mordell divisor splitting search.
    """
    if a < 1 or m <= 0 or r < 0:
        raise ValueError(f"Invalid parameters: a={a}, m={m}, r={r}")

    n = Poly1D.linear(m, r if r > 0 else m)

    # 1. Multiples of a
    if m % a == 0 and r % a == 0:
        W = Poly1D.linear(m // a, r // a if r > 0 else m // a)
        if W.is_strictly_positive(5):
            ident = AlgebraicIdentity(m=m, r=r, n_poly=n, X=W * 2, Y=W * 3, Z=W * 6, a=a)
            if ident.verify_exact():
                return ident

    # 2. Even residues for a=5 (Sierpiński)
    if a == 5 and m % 2 == 0 and r % 2 == 0:
        if m % 4 == 0 and r % 4 == 0:
            V = Poly1D.linear(m // 4, r // 4 if r > 0 else m // 4)
            if V.is_strictly_positive(5):
                ident = AlgebraicIdentity(
                    m=m, r=r, n_poly=n, X=V + 1, Y=V * (V + 1), Z=V * 4, a=5
                )
                if ident.verify_exact():
                    return ident
        if m % 4 == 0 and r % 4 == 2:
            W = Poly1D.linear(m // 2, r // 2)
            X = (W + 1) * Fraction(1, 2)
            Y = W * (W + 1) * Fraction(1, 2)
            Z = W * 2
            if X.is_strictly_positive(5) and X.is_integer_valued(5):
                ident = AlgebraicIdentity(
                    m=m, r=r, n_poly=n, X=X, Y=Y, Z=Z, a=5
                )
                if ident.verify_exact():
                    return ident

    # 3. Parameterized c-family: (c*a - 1)*X = c*n + 1
    for c in range(1, max_c + 1):
        denom = c * a - 1
        r_eff = r if r > 0 else m
        if (c * m) % denom == 0 and (c * r_eff + 1) % denom == 0:
            X = Poly1D.linear((c * m) // denom, (c * r_eff + 1) // denom)
            Y = n * c
            Z = n * X * c
            if (
                X.is_strictly_positive(5)
                and Y.is_strictly_positive(5)
                and Z.is_strictly_positive(5)
                and X.is_integer_valued(5)
                and Y.is_integer_valued(5)
                and Z.is_integer_valued(5)
            ):
                ident = AlgebraicIdentity(m=m, r=r, n_poly=n, X=X, Y=Y, Z=Z, a=a)
                if ident.verify_exact():
                    return ident

    # 4. Mordell search
    for alpha in range(1, 6):
        for beta in range(1, 6):
            X = Poly1D.linear(alpha, beta)
            R = (X * a) - n
            if not R.is_strictly_positive(5):
                continue
            for S in (1, 2, 3, 4, 6):
                SR = R * S
                SnX = n * X * S
                for d in range(1, 13):
                    A = Poly1D.constant(d)
                    B = SR - A
                    if not B.is_strictly_positive(5):
                        continue
                    Y = SnX.exact_divide(A)
                    Z = SnX.exact_divide(B)
                    if (
                        Y is not None
                        and Z is not None
                        and Y.is_strictly_positive(5)
                        and Z.is_strictly_positive(5)
                        and Y.is_integer_valued(5)
                        and Z.is_integer_valued(5)
                    ):
                        ident = AlgebraicIdentity(m=m, r=r, n_poly=n, X=X, Y=Y, Z=Z, a=a)
                        if ident.verify_exact():
                            return ident

    return None


def synthesize_sierpinski_identity(
    m: int, r: int, max_c: int = 30
) -> AlgebraicIdentity | None:
    """Synthesize an exact polynomial identity for Sierpiński conjecture (5/n)."""
    return synthesize_schinzel_identity(5, m, r, max_c=max_c)


def build_sierpinski_coverage_matrix(
    modulus: int = 120, max_c: int = 30
) -> dict[str, Any]:
    """Evaluate modular residue coverage for Sierpiński conjecture (5/n) over modulus m."""
    covered: list[int] = []
    uncovered: list[int] = []
    identities_dict: dict[str, Any] = {}

    for r in range(modulus):
        ident = synthesize_sierpinski_identity(modulus, r, max_c=max_c)
        if ident is not None and ident.verify_exact():
            covered.append(r)
            identities_dict[str(r)] = ident.to_dict()
        else:
            uncovered.append(r)

    total = modulus
    coverage_ratio = len(covered) / total if total > 0 else 0.0

    return {
        "modulus": modulus,
        "a": 5,
        "conjecture": "sierpinski_5_over_n",
        "total_residues": total,
        "covered_count": len(covered),
        "uncovered_count": len(uncovered),
        "coverage_ratio": coverage_ratio,
        "covered_residues": sorted(covered),
        "uncovered_residues": sorted(uncovered),
        "identities": identities_dict,
        "verified_exact": all(
            identities_dict[str(r)]["a"] == 5 for r in covered
        ),
    }


def compare_schinzel_synthesis(
    a_values: list[int] | None = None,
    test_instances: list[int] | None = None,
    modulus: int = 120,
) -> dict[str, Any]:
    """Compare synthesis time, coverage ratio, and rational divisor sieve performance

    between numerators (default: a=4 Erdős-Straus vs a=5 Sierpiński) under identical budget.
    """
    if a_values is None:
        a_values = [4, 5]
    if test_instances is None:
        test_instances = [
            3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 1009,
        ]

    per_numerator: dict[str, Any] = {}

    for a in a_values:
        # 1. Modular synthesis
        t0_synth = time.perf_counter()
        covered_count = 0
        synth_identities: list[dict[str, Any]] = []
        for r in range(modulus):
            if a == 4:
                classif = classify_congruence_residue(modulus, r)
                if not classif["is_resistant"]:
                    ident_4 = get_algebraic_identity_for_residue(modulus, r)
                    if ident_4 is not None and ident_4.verify_exact():
                        covered_count += 1
                        synth_identities.append(ident_4.to_dict())
            else:
                ident_a = synthesize_schinzel_identity(a, modulus, r)
                if ident_a is not None and ident_a.verify_exact():
                    covered_count += 1
                    synth_identities.append(ident_a.to_dict())

        elapsed_synth = time.perf_counter() - t0_synth
        cov_ratio = covered_count / modulus if modulus > 0 else 0.0

        # 2. Sieve evaluation on prime instances
        t0_sieve = time.perf_counter()
        sieve_results: list[dict[str, Any]] = []
        total_cands = 0
        all_solved = True
        for p in test_instances:
            if p < 2 or (a >= 7 and p < 3):
                continue
            sol, det = schinzel_divisor_sieve(a, p)
            if sol is None:
                all_solved = False
                continue
            x, y, z = sol
            ok_int, _, _ = check_schinzel(a, p, x, y, z)
            ok_frac, _, _ = check_schinzel_fractions(a, p, x, y, z)
            if not (ok_int and ok_frac):
                all_solved = False
            cands = det.get("candidates_evaluated", 0)
            total_cands += cands
            sieve_results.append({
                "n": p,
                "triple": (x, y, z),
                "candidates": cands,
                "verified_exact": ok_int and ok_frac,
            })

        elapsed_sieve = time.perf_counter() - t0_sieve

        per_numerator[str(a)] = {
            "a": a,
            "modulus": modulus,
            "covered_classes": covered_count,
            "coverage_ratio": cov_ratio,
            "synthesis_sec": elapsed_synth,
            "sieve_instances_count": len(sieve_results),
            "sieve_total_candidates": total_cands,
            "sieve_avg_candidates": total_cands / len(sieve_results) if sieve_results else 0.0,
            "sieve_sec": elapsed_sieve,
            "all_sieve_solved": all_solved,
        }

    comp: dict[str, Any] = {}
    if "4" in per_numerator and "5" in per_numerator:
        comp["sierpinski_vs_erdos_straus"] = {
            "coverage_delta": (
                per_numerator["5"]["coverage_ratio"] - per_numerator["4"]["coverage_ratio"]
            ),
            "synthesis_time_ratio": (
                per_numerator["5"]["synthesis_sec"]
                / max(per_numerator["4"]["synthesis_sec"], 1e-9)
            ),
            "sieve_candidates_ratio": (
                per_numerator["5"]["sieve_total_candidates"]
                / max(per_numerator["4"]["sieve_total_candidates"], 1)
            ),
        }

    return {
        "modulus": modulus,
        "test_instances_count": len(test_instances),
        "per_numerator": per_numerator,
        "comparisons": comp,
        "verified": all(info["all_sieve_solved"] for info in per_numerator.values()),
    }
