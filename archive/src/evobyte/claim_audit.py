"""Claim audit helpers (P161): integrality of unit-fraction identities.

The Erdos-Straus / Sierpinski / Schinzel problems require POSITIVE INTEGERS
x, y, z with a/n = 1/x + 1/y + 1/z. An identity that only holds in Q[k] is not
a solution. This module re-evaluates generated Lean identities exactly.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from pathlib import Path

_IDENTITY_RE = re.compile(
    r"theorem schinzel_identity_a(\d+)_m(\d+)_r(\d+) \(k : ℚ\) :\s*"
    r"let n : ℚ := (.+?)\n\s*let X : ℚ := (.+?)\n\s*let Y : ℚ := (.+?)\n"
    r"\s*let Z : ℚ := (.+?)\n"
)
_SAFE_EXPR_RE = re.compile(r"^[0-9k+\-*/^() ]+$")


@dataclass(frozen=True)
class UnitFractionIdentity:
    a: int
    m: int
    r: int
    n_expr: str
    x_expr: str
    y_expr: str
    z_expr: str


def parse_schinzel_identities(text: str) -> list[UnitFractionIdentity]:
    """Parse every `schinzel_identity_a*_m*_r*` theorem in a Lean source text."""
    out = []
    for a, m, r, n_e, x_e, y_e, z_e in _IDENTITY_RE.findall(text):
        out.append(
            UnitFractionIdentity(
                int(a), int(m), int(r), n_e.strip(), x_e.strip(), y_e.strip(), z_e.strip()
            )
        )
    return out


def evaluate_expr(expr: str, k: int) -> Fraction:
    """Exactly evaluate a polynomial/rational expression in k (whitelisted chars only)."""
    if not _SAFE_EXPR_RE.match(expr):
        raise ValueError(f"unsafe or unsupported expression: {expr!r}")
    py = re.sub(r"(\d+)", r"Fraction(\1)", expr).replace("^", "**")
    value = eval(py, {"__builtins__": {}, "Fraction": Fraction}, {"k": Fraction(k)})
    return Fraction(value)


def integral_k_count(identity: UnitFractionIdentity, k_values: range) -> int:
    """Count k for which (x, y, z) are positive integers; raise if the identity is false."""
    count = 0
    for k in k_values:
        n = evaluate_expr(identity.n_expr, k)
        x = evaluate_expr(identity.x_expr, k)
        y = evaluate_expr(identity.y_expr, k)
        z = evaluate_expr(identity.z_expr, k)
        if identity.a * x * y * z != n * (x * y + y * z + z * x):
            raise ValueError(f"rational identity fails for {identity} at k={k}")
        if all(v.denominator == 1 and v > 0 for v in (x, y, z)):
            count += 1
    return count


def is_quadratic_residue(r: int, m: int) -> bool:
    """True when gcd(r, m) = 1 and r is a square modulo m."""
    return gcd(r, m) == 1 and any((t * t - r) % m == 0 for t in range(m))


def audit_schinzel_text(text: str, k_max: int = 50) -> dict:
    """Summarize integrality of every parsed identity for k in range(k_max)."""
    ids = parse_schinzel_identities(text)
    rows = []
    for ident in ids:
        good = integral_k_count(ident, range(k_max))
        rows.append(
            {
                "a": ident.a,
                "m": ident.m,
                "r": ident.r,
                "quadratic_residue": is_quadratic_residue(ident.r, ident.m),
                "integral_k": good,
            }
        )
    return {
        "k_max": k_max,
        "identities": len(rows),
        "quadratic_residue_classes": sum(r["quadratic_residue"] for r in rows),
        "integral_for_all_k": sum(r["integral_k"] == k_max for r in rows),
        "integral_for_no_k": sum(r["integral_k"] == 0 for r in rows),
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 -m evobyte.claim_audit <lean_file>", file=sys.stderr)
        return 2
    summary = audit_schinzel_text(Path(argv[1]).read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
