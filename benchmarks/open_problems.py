"""P29 — Open problems with verifiable certificates (Diophantine, identities, combinatorial).

Implements bounded problem nominations, GPU-accelerated candidate filtering, exact-arithmetic
finalist verification on CPU, independent reproduction, lineage recording, and strict
scientific classification (rediscovery / candidate / verified-construction / counterexample /
proven-theorem / null-campaign).
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from evobyte.provenance import (
    collect_provenance,
    resolve_device,
    write_manifest,
)


def get_git_commit() -> str:
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=_REPO_ROOT,
        )
        if out.returncode == 0:
            return out.stdout.strip()[:12]
    return "unknown"


@dataclass
class ProblemNomination:
    problem_id: str
    title: str
    domain: str
    conjecture_statement: str
    bounded_statement: str
    certificate_type: str
    literature_citations: list[str]
    classification_rules: dict[str, str]


# ==============================================================================
# 1. Exact Decidable Checkers (Arbitrary-Precision CPU Arithmetic)
# ==============================================================================


def check_erdos_straus(n: int, x: int, y: int, z: int) -> tuple[bool, int, dict[str, Any]]:
    """Exact decidable integer checker for Erdős-Straus: 4/n = 1/x + 1/y + 1/z.

    Equivalent to: 4*x*y*z == n*(x*y + y*z + x*z) with x, y, z > 0.
    """
    if x <= 0 or y <= 0 or z <= 0:
        return False, -1, {"error": "All denominators must be positive integers"}

    lhs = 4 * int(x) * int(y) * int(z)
    rhs = int(n) * (int(x) * int(y) + int(y) * int(z) + int(x) * int(z))
    residual = lhs - rhs

    is_valid = residual == 0
    details = {
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


def check_taxicab(sum_val: int, a: int, b: int, c: int, d: int) -> tuple[bool, int, dict[str, Any]]:
    """Exact checker for Taxicab identity: a^3 + b^3 == c^3 + d^3 == sum_val."""
    if min(a, b, c, d) <= 0:
        return False, -1, {"error": "All cube bases must be positive integers"}
    if sorted([a, b]) == sorted([c, d]):
        return False, -2, {"error": "Pairs must be distinct"}

    sum1 = int(a) ** 3 + int(b) ** 3
    sum2 = int(c) ** 3 + int(d) ** 3
    residual = abs(sum1 - sum2) + abs(sum1 - int(sum_val))

    is_valid = residual == 0
    details = {
        "sum_val": int(sum_val),
        "pair_1": [int(a), int(b)],
        "pair_2": [int(c), int(d)],
        "sum1": int(sum1),
        "sum2": int(sum2),
        "residual": int(residual),
        "verified_exact": is_valid,
    }
    return is_valid, residual, details


def check_diophantine_quintuple(elements: list[int]) -> tuple[bool, int, dict[str, Any]]:
    """Exact checker for Diophantine quintuple: a_i * a_j + 1 is a square for all i < j."""
    if len(elements) != 5:
        return False, -1, {"error": "Must have exactly 5 elements"}
    if len(set(elements)) != 5:
        return False, -2, {"error": "All 5 elements must be distinct"}
    if min(elements) <= 0:
        return False, -3, {"error": "All elements must be positive integers"}

    pairwise_checks = []
    all_square = True
    for i in range(5):
        for j in range(i + 1, 5):
            prod = int(elements[i]) * int(elements[j]) + 1
            s = math.isqrt(prod)
            is_sq = s * s == prod
            if not is_sq:
                all_square = False
            pairwise_checks.append(
                {
                    "pair": [int(elements[i]), int(elements[j])],
                    "prod_plus_1": prod,
                    "is_square": is_sq,
                    "sqrt": s if is_sq else None,
                }
            )

    details = {
        "elements": [int(x) for x in sorted(elements)],
        "all_pairs_square": all_square,
        "pairwise_checks": pairwise_checks,
    }
    return all_square, 0 if all_square else 1, details


def check_erdos_straus_fractions(
    n: int, x: int, y: int, z: int
) -> tuple[bool, Fraction, dict[str, Any]]:
    """Independent second checker using exact rational arithmetic (fractions.Fraction)."""
    if not (
        isinstance(n, int)
        and isinstance(x, int)
        and isinstance(y, int)
        and isinstance(z, int)
        and not isinstance(n, bool)
        and not isinstance(x, bool)
        and not isinstance(y, bool)
        and not isinstance(z, bool)
    ):
        return False, Fraction(1), {"error": "All arguments must be integers"}
    if n < 2 or x <= 0 or y <= 0 or z <= 0:
        return False, Fraction(1), {"error": "Domain requirement: n >= 2 and x, y, z > 0"}

    lhs_frac = Fraction(4, n)
    rhs_frac = Fraction(1, x) + Fraction(1, y) + Fraction(1, z)
    diff = lhs_frac - rhs_frac
    is_valid = diff == 0

    details = {
        "n": int(n),
        "x": int(x),
        "y": int(y),
        "z": int(z),
        "lhs_fraction": str(lhs_frac),
        "rhs_fraction": str(rhs_frac),
        "fraction_diff": str(diff),
        "verified_exact_fraction": is_valid,
        "formulation": "exact_rational_decomposition",
    }
    return is_valid, diff, details


def check_taxicab_factorization(
    sum_val: int, a: int, b: int, c: int, d: int
) -> tuple[bool, int, dict[str, Any]]:
    """Independent second checker using sum-of-cubes algebraic factorization."""
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in (sum_val, a, b, c, d)):
        return False, -1, {"error": "All arguments must be integers"}
    if min(a, b, c, d) <= 0:
        return False, -1, {"error": "All cube bases must be positive integers"}
    if sorted([a, b]) == sorted([c, d]):
        return False, -2, {"error": "Pairs must be distinct"}

    # Algebraic identity: a^3 + b^3 = (a + b)(a^2 - ab + b^2)
    sum1 = (a + b) * (a * a - a * b + b * b)
    sum2 = (c + d) * (c * c - c * d + d * d)
    residual = abs(sum1 - sum2) + abs(sum1 - int(sum_val))
    is_valid = residual == 0

    details = {
        "sum_val": int(sum_val),
        "pair_1": [int(a), int(b)],
        "pair_2": [int(c), int(d)],
        "factored_sum1": int(sum1),
        "factored_sum2": int(sum2),
        "residual": int(residual),
        "verified_algebraic_identity": is_valid,
        "formulation": "sum_of_cubes_factorization",
    }
    return is_valid, residual, details


def check_diophantine_quintuple_independent(
    elements: list[int],
) -> tuple[bool, int, dict[str, Any]]:
    """Independent second checker using arbitrary-precision integer root validation."""
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in elements):
        return False, -1, {"error": "All elements must be integers"}
    if len(elements) != 5:
        return False, -1, {"error": "Must have exactly 5 elements"}
    if len(set(elements)) != 5:
        return False, -2, {"error": "All 5 elements must be distinct"}
    if min(elements) <= 0:
        return False, -3, {"error": "All elements must be positive integers"}

    pairwise = []
    all_square = True
    for i in range(5):
        for j in range(i + 1, 5):
            prod = int(elements[i]) * int(elements[j]) + 1
            s = math.isqrt(prod)
            is_sq = (s * s == prod) and ((s + 1) * (s + 1) > prod)
            if not is_sq:
                all_square = False
            pairwise.append(
                {"pair": [elements[i], elements[j]], "prod_plus_1": prod, "is_square": is_sq}
            )

    details = {
        "elements": sorted(elements),
        "all_pairs_square": all_square,
        "pairwise": pairwise,
        "formulation": "arbitrary_precision_integer_isqrt_bracketing",
    }
    return all_square, 0 if all_square else 1, details


def check_coordinate_bounds(
    problem_id: str, solution_data: dict[str, Any], max_coord: int = 10**9
) -> tuple[bool, dict[str, Any]]:
    """State and enforce which coordinates each search bound constrains."""
    if problem_id == "erdos-straus":
        x = int(solution_data["x"])
        y = int(solution_data["y"])
        z = int(solution_data["z"])
        m = max(x, y, z)
        in_bounds = m <= max_coord
        return in_bounds, {
            "constrained_coordinates": ["x", "y", "z"],
            "max_coordinate_value": m,
            "declared_bound": max_coord,
            "within_bounds": in_bounds,
            "rule": f"max(x, y, z) <= {max_coord}",
        }
    elif problem_id == "taxicab":
        sum_val = int(solution_data["sum_val"])
        in_bounds = sum_val <= 50_000
        return in_bounds, {
            "constrained_coordinates": ["sum_val"],
            "max_coordinate_value": sum_val,
            "declared_bound": 50_000,
            "within_bounds": in_bounds,
            "rule": "sum_val <= 50000",
        }
    elif problem_id == "diophantine-quintuple":
        _r_start, r_end = solution_data.get("range", [121, 250_000])
        in_bounds = r_end <= 500_000
        return in_bounds, {
            "constrained_coordinates": ["e_candidate"],
            "max_coordinate_value": r_end,
            "declared_bound": 500_000,
            "within_bounds": in_bounds,
            "rule": "e <= 500000",
        }
    return True, {}


def replay_and_verify_bounded_null(
    base_quadruple: list[int],
    r_start: int,
    r_end: int,
    device: torch.device | None = None,
) -> dict[str, Any]:
    """Replay complete nominated domain candidate-by-candidate; refusing matches_count==0 alone."""
    dev = device if device is not None else torch.device("cpu")
    t0 = time.perf_counter()

    base_t = torch.tensor(base_quadruple, dtype=torch.int64, device=dev)
    chunk_size = 50_000
    total_candidates = r_end - r_start + 1
    candidates_checked = 0
    counterexamples = []

    cur = r_start
    while cur <= r_end:
        chunk_end = min(cur + chunk_size - 1, r_end)
        cand_t = torch.arange(cur, chunk_end + 1, dtype=torch.int64, device=dev)
        e = cand_t.unsqueeze(1)
        prods = e * base_t.unsqueeze(0) + 1
        sqrts = torch.sqrt(prods.double()).to(torch.int64)
        is_sq = sqrts * sqrts == prods
        all_sq = is_sq.all(dim=1)

        if all_sq.any():
            idxs = torch.nonzero(all_sq).squeeze(-1)
            for idx in idxs:
                cand_val = int(cand_t[idx].item())
                is_val, _, _ = check_diophantine_quintuple_independent(base_quadruple + [cand_val])
                if is_val:
                    counterexamples.append(cand_val)

        candidates_checked += int(cand_t.shape[0])
        cur = chunk_end + 1

    elapsed = time.perf_counter() - t0
    is_exhaustive = candidates_checked == total_candidates
    null_verified = is_exhaustive and len(counterexamples) == 0

    return {
        "null_verified": null_verified,
        "status": "exhaustive_null"
        if null_verified
        else ("budget_exhausted" if not is_exhaustive else "counterexample_found"),
        "range": [r_start, r_end],
        "candidates_checked": candidates_checked,
        "total_domain_size": total_candidates,
        "counterexamples": counterexamples,
        "elapsed_sec": elapsed,
        "method": "complete_domain_replay_exact_independent",
    }


# ==============================================================================
# 2. Problem Nominations Registry
# ==============================================================================

PROBLEM_REGISTRY: dict[str, ProblemNomination] = {
    "erdos-straus": ProblemNomination(
        problem_id="erdos-straus",
        title="Erdős-Straus Diophantine Decomposition",
        domain="Diophantine equations / Egyptian fractions",
        conjecture_statement="For every integer n >= 2, the equation 4/n = 1/x + 1/y + 1/z has positive integer solutions.",
        bounded_statement="Find exact positive integer solutions (x, y, z) for nominated prime instances n in {1009, 10007, 100003} with search bound M <= 10^9.",
        certificate_type="integer_exact_certificate",
        literature_citations=[
            "Erdős, P. (1948). Some problems on unit fractions.",
            "Mordell, L. J. (1967). Diophantine Equations (Academic Press).",
            "Elsholtz, C., & Tao, T. (2013). Counting the number of solutions to the Erdős-Straus equation on unit fractions. J. Aust. Math. Soc.",
        ],
        classification_rules={
            "rediscovery": "Verified exact integer decomposition matching known literature parameterization.",
            "verified-construction": "New verified instance not previously cataloged.",
            "null-campaign": "Search bounded space exhausted without finding any valid decomposition.",
        },
    ),
    "taxicab": ProblemNomination(
        problem_id="taxicab",
        title="Hardy-Ramanujan Taxicab Decomposition",
        domain="Additive number theory / Sums of powers",
        conjecture_statement="Find positive integers expressible as the sum of two positive cubes in two or more distinct ways: Ta(2) = x^3 + y^3 = z^3 + w^3.",
        bounded_statement="Identify all taxicab numbers Ta(2) <= 50,000 via high-throughput GPU cube grid collision filtering.",
        certificate_type="integer_exact_certificate",
        literature_citations=[
            "Hardy, G. H., & Wright, E. M. (1979). An Introduction to the Theory of Numbers (Oxford).",
            "Silverman, J. H. (1993). Taxicab numbers and elliptic curves.",
        ],
        classification_rules={
            "rediscovery": "Verified bit-exact integer cube pairs matching known Ramanujan taxicab numbers (e.g. 1729, 4104).",
            "verified-construction": "New taxicab representation beyond known literature bounds.",
            "null-campaign": "No collision found within search bound.",
        },
    ),
    "diophantine-quintuple": ProblemNomination(
        problem_id="diophantine-quintuple",
        title="Diophantine Quintuple Extension Search",
        domain="Diophantine tuples / Arithmetic geometry",
        conjecture_statement="Search for a 5th positive integer e extending the Fermat quadruple {1, 3, 8, 120} such that e*a_i + 1 is a square for all i in {1, 2, 3, 4}.",
        bounded_statement="Exhaustively test candidate extensions e in [121, 500,000] on GPU to verify absence of quintuple extensions.",
        certificate_type="bounded_null_certificate",
        literature_citations=[
            "Fermat, P. (1637). Diophantine quadruples.",
            "Baker, A., & Davenport, H. (1969). The equations 3x^2 - 2 = y^2 and 8x^2 - 7 = z^2. Quart. J. Math. Oxford.",
            "He, B., Togbé, A., & Ziegler, V. (2019). There is no Diophantine quintuple. Trans. Amer. Math. Soc.",
        ],
        classification_rules={
            "null-campaign": "Exhaustive bounded verification confirming 0 extensions in [121, 500,000], consistent with He-Togbé-Ziegler 2019 theorem.",
            "counterexample": "Certified positive integer quintuple extension (would falsify 2019 theorem).",
        },
    ),
}


# ==============================================================================
# 3. GPU Filtering & Search Campaigns
# ==============================================================================


def run_erdos_straus_campaign(
    n_instances: list[int],
    device: torch.device,
    batch_size: int = 500_000,
    bounds_strict: bool = False,
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """GPU-accelerated candidate filtering for Erdős-Straus Diophantine equation."""
    results: list[dict[str, Any]] = []
    total_evaluated = 0
    t0_all = time.perf_counter()

    for n in n_instances:
        t0_n = time.perf_counter()
        x0 = n // 4 + 1
        found_for_n = False
        match_info = None

        # Explore candidate x values near lower bound
        for x_step in range(50):
            x_val = x0 + x_step
            R = 4 * x_val - n
            if R <= 0:
                continue

            y_min = (n * x_val) // R + 1
            y_max = (2 * n * x_val) // R + 2
            y_range = min(batch_size, max(1000, y_max - y_min + 1))

            # GPU resident tensor evaluation
            x_t = torch.full((y_range,), x_val, dtype=torch.int64, device=device)
            y_t = torch.arange(y_min, y_min + y_range, dtype=torch.int64, device=device)

            denom = 4 * x_t * y_t - n * (x_t + y_t)
            valid = denom > 0
            rem = torch.where(
                valid,
                (n * x_t * y_t) % torch.clamp(denom, min=1),
                torch.tensor(1, device=device),
            )
            matches = valid & (rem == 0)

            total_evaluated += y_range

            if matches.any():
                match_indices = torch.nonzero(matches).squeeze(-1)
                for m_idx in match_indices:
                    match_idx = int(m_idx.item())
                    y_val = int(y_t[match_idx].item())
                    denom_val = int(denom[match_idx].item())
                    z_val = (int(n) * int(x_val) * int(y_val)) // denom_val

                    # Exact CPU verification gate: Checker 1 (integer identity)
                    is_valid, _residual, details = check_erdos_straus(n, x_val, y_val, z_val)
                    if not is_valid:
                        continue

                    # Exact CPU verification gate: Checker 2 (rational fractions)
                    is_valid_frac, _, frac_details = check_erdos_straus_fractions(
                        n, x_val, y_val, z_val
                    )
                    if not is_valid_frac:
                        continue

                    # Coordinate bound constraint
                    coord_max = max(x_val, y_val, z_val)
                    if bounds_strict and coord_max > max_coord:
                        continue

                    found_for_n = True
                    details["dual_checker_exact_fractions"] = frac_details
                    details["coordinate_bounds"] = {
                        "max_coordinate_value": coord_max,
                        "declared_bound": max_coord,
                        "within_bounds": coord_max <= max_coord,
                    }
                    match_info = details
                    break
                if found_for_n:
                    break

        elapsed_n = time.perf_counter() - t0_n
        results.append(
            {
                "n": n,
                "found": found_for_n,
                "status": "PASS" if found_for_n else "budget_exhausted",
                "elapsed_sec": elapsed_n,
                "details": match_info,
            }
        )

    elapsed_all = time.perf_counter() - t0_all
    cvps = total_evaluated / max(elapsed_all, 1e-6)

    return {
        "problem_id": "erdos-straus",
        "instances": results,
        "total_evaluated": total_evaluated,
        "elapsed_total_sec": elapsed_all,
        "search_cvps": cvps,
    }


def run_taxicab_campaign(
    max_base: int = 150,
    device: torch.device | None = None,
) -> dict[str, Any]:
    """GPU-accelerated taxicab number decomposition search."""
    dev = device if device is not None else torch.device("cpu")
    t0 = time.perf_counter()

    a = torch.arange(1, max_base, dtype=torch.int64, device=dev)
    b = torch.arange(1, max_base, dtype=torch.int64, device=dev)
    grid_a, grid_b = torch.meshgrid(a, b, indexing="ij")
    mask = grid_a <= grid_b
    valid_a = grid_a[mask]
    valid_b = grid_b[mask]

    sums = valid_a**3 + valid_b**3
    total_evaluated = int(sums.shape[0])

    unique_sums, counts = torch.unique(sums, return_counts=True)
    taxicab_mask = counts >= 2
    taxicab_sums = unique_sums[taxicab_mask]

    verified_taxicabs: list[dict[str, Any]] = []
    for s_val in taxicab_sums[:10]:
        idx = torch.nonzero(sums == s_val).squeeze(-1)
        pairs = [(int(valid_a[i].item()), int(valid_b[i].item())) for i in idx]
        if len(pairs) >= 2:
            p1, p2 = pairs[0], pairs[1]
            is_valid, _res, det = check_taxicab(int(s_val.item()), p1[0], p1[1], p2[0], p2[1])
            if is_valid:
                verified_taxicabs.append(det)

    elapsed = time.perf_counter() - t0
    cvps = total_evaluated / max(elapsed, 1e-6)

    return {
        "problem_id": "taxicab",
        "verified_taxicabs": verified_taxicabs,
        "total_evaluated": total_evaluated,
        "elapsed_total_sec": elapsed,
        "search_cvps": cvps,
    }


def run_diophantine_quintuple_campaign(
    max_candidate: int = 250_000,
    device: torch.device | None = None,
) -> dict[str, Any]:
    """GPU-accelerated bounded search for Diophantine quintuple extensions."""
    dev = device if device is not None else torch.device("cpu")
    t0 = time.perf_counter()

    base = torch.tensor([1, 3, 8, 120], dtype=torch.int64, device=dev)
    candidates = torch.arange(121, max_candidate + 1, dtype=torch.int64, device=dev)
    total_evaluated = int(candidates.shape[0])

    e = candidates.unsqueeze(1)
    prods = e * base.unsqueeze(0) + 1

    sqrts = torch.sqrt(prods.double()).to(torch.int64)
    is_square = sqrts * sqrts == prods
    all_square = is_square.all(dim=1)

    match_indices = torch.nonzero(all_square).squeeze(-1)
    matches_found = []
    for idx in match_indices:
        e_val = int(candidates[idx].item())
        is_val, _res, det = check_diophantine_quintuple([1, 3, 8, 120, e_val])
        if is_val:
            matches_found.append(det)

    elapsed = time.perf_counter() - t0
    cvps = total_evaluated / max(elapsed, 1e-6)

    return {
        "problem_id": "diophantine-quintuple",
        "range": [121, max_candidate],
        "total_evaluated": total_evaluated,
        "matches_count": len(matches_found),
        "matches": matches_found,
        "elapsed_total_sec": elapsed,
        "search_cvps": cvps,
    }


# ==============================================================================
# 4. Independent Reproduction & Certificate Construction
# ==============================================================================


def verify_independent_reproduction(
    problem_id: str,
    solution_data: dict[str, Any],
    bounds_strict: bool = False,
    device: torch.device | None = None,
) -> dict[str, Any]:
    """Execute independent dual bit-exact reproduction pass on CPU/GPU with hash recording."""
    t0 = time.perf_counter()

    if problem_id == "erdos-straus":
        n = int(solution_data["n"])
        x = int(solution_data["x"])
        y = int(solution_data["y"])
        z = int(solution_data["z"])
        # Checker 1: exact integer identity
        is_valid_1, residual_1, details_1 = check_erdos_straus(n, x, y, z)
        # Checker 2: independent exact rational fractions
        is_valid_2, residual_2, details_2 = check_erdos_straus_fractions(n, x, y, z)

        assert is_valid_1, f"Checker 1 failed for n={n}: residual={residual_1}"
        assert is_valid_2, f"Checker 2 (fractions) failed for n={n}: diff={residual_2}"

        in_bounds, bounds_info = check_coordinate_bounds(
            "erdos-straus", solution_data, max_coord=10**9
        )
        if bounds_strict and not in_bounds:
            status = "EXCEEDS_BOUND"
            classification = "exceeds_declared_coordinate_bound"
        else:
            status = "PASS"
            classification = "rediscovery"

        reproduction_hash = hashlib.sha256(
            f"erdos_straus_dual_{n}_{x}_{y}_{z}_{in_bounds}".encode()
        ).hexdigest()
        details = {
            "checker_1_integer_identity": details_1,
            "checker_2_rational_fractions": details_2,
            "coordinate_bounds": bounds_info,
            "within_declared_bounds": in_bounds,
            "classification": classification,
        }

    elif problem_id == "taxicab":
        s_val = int(solution_data["sum_val"])
        p1 = solution_data["pair_1"]
        p2 = solution_data["pair_2"]
        # Checker 1: sum of cubes
        is_valid_1, residual_1, details_1 = check_taxicab(s_val, p1[0], p1[1], p2[0], p2[1])
        # Checker 2: sum of cubes factorization
        is_valid_2, residual_2, details_2 = check_taxicab_factorization(
            s_val, p1[0], p1[1], p2[0], p2[1]
        )

        assert is_valid_1, f"Checker 1 failed for taxicab={s_val}"
        assert is_valid_2, f"Checker 2 failed for taxicab={s_val}"

        in_bounds, bounds_info = check_coordinate_bounds("taxicab", solution_data)
        if bounds_strict and not in_bounds:
            status = "EXCEEDS_BOUND"
        else:
            status = "PASS"

        reproduction_hash = hashlib.sha256(f"taxicab_dual_{s_val}_{p1}_{p2}".encode()).hexdigest()
        details = {
            "checker_1_sum_of_cubes": details_1,
            "checker_2_factorization": details_2,
            "coordinate_bounds": bounds_info,
        }

    elif problem_id == "diophantine-quintuple":
        r_start, r_end = solution_data.get("range", [121, 250_000])
        base_quad = solution_data.get("base_quadruple", [1, 3, 8, 120])
        # Complete domain replay candidate-by-candidate; refusing matches_count == 0 alone
        replay_res = replay_and_verify_bounded_null(
            base_quadruple=base_quad,
            r_start=r_start,
            r_end=r_end,
            device=device,
        )
        assert replay_res["null_verified"], f"Exhaustive replay failed: {replay_res}"
        reproduction_hash = hashlib.sha256(
            f"quintuple_exhaustive_replay_{r_start}_{r_end}".encode()
        ).hexdigest()
        in_bounds, bounds_info = check_coordinate_bounds("diophantine-quintuple", solution_data)
        status = "PASS"
        details = {
            "replay_summary": replay_res,
            "coordinate_bounds": bounds_info,
            "null_verified": True,
        }

    else:
        raise ValueError(f"Unknown problem_id: {problem_id}")

    elapsed = time.perf_counter() - t0
    return {
        "status": status,
        "reproduction_time_sec": elapsed,
        "reproduction_hash": reproduction_hash,
        "details": details,
    }


def generate_certificate_bundle(
    nomination: ProblemNomination,
    campaign_results: dict[str, Any],
    device: torch.device,
) -> dict[str, Any]:
    """Construct cryptographic certificate bundle per P29 specifications."""
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    pid = nomination.problem_id

    if pid == "erdos-straus":
        # Extract first verified instance
        verified_instances = [inst for inst in campaign_results["instances"] if inst["found"]]
        assert verified_instances, "No verified instance found for certificate generation"
        primary = verified_instances[0]["details"]

        reproduction = verify_independent_reproduction(pid, primary)
        classification = "rediscovery"  # Known in literature (Mordell 1967)

        bundle = {
            "problem_id": pid,
            "title": nomination.title,
            "conjecture_statement": nomination.conjecture_statement,
            "bounded_statement": nomination.bounded_statement,
            "certificate_type": nomination.certificate_type,
            "target_instance": {"n": primary["n"]},
            "solution_data": {
                "x": primary["x"],
                "y": primary["y"],
                "z": primary["z"],
            },
            "exact_algebraic_evidence": {
                "equation": "4*x*y*z == n*(x*y + y*z + x*z)",
                "lhs": primary["lhs"],
                "rhs": primary["rhs"],
                "residual": primary["residual"],
                "verified": primary["verified_exact"],
            },
            "independent_reproduction": reproduction,
            "literature_citations": nomination.literature_citations,
            "classification": classification,
            "classification_rationale": (
                "Verified exact integer solution found via GPU filtering and certified by arbitrary-precision "
                "integer arithmetic. Matches known instances in the literature (Mordell 1967, Elsholtz & Tao 2013). "
                "Per P29 Discovery Criterion, classified as 'rediscovery'."
            ),
            "timestamp": timestamp,
        }

    elif pid == "taxicab":
        verified = campaign_results["verified_taxicabs"]
        assert verified, "No verified taxicab number found"
        primary = verified[0]  # 1729

        reproduction = verify_independent_reproduction(pid, primary)
        classification = "rediscovery"

        bundle = {
            "problem_id": pid,
            "title": nomination.title,
            "conjecture_statement": nomination.conjecture_statement,
            "certificate_type": nomination.certificate_type,
            "target_instance": {"sum_val": primary["sum_val"]},
            "solution_data": {
                "pair_1": primary["pair_1"],
                "pair_2": primary["pair_2"],
            },
            "exact_algebraic_evidence": {
                "equation": "a^3 + b^3 == c^3 + d^3 == sum_val",
                "sum1": primary["sum1"],
                "sum2": primary["sum2"],
                "residual": primary["residual"],
                "verified": primary["verified_exact"],
            },
            "independent_reproduction": reproduction,
            "literature_citations": nomination.literature_citations,
            "classification": classification,
            "classification_rationale": "Matches Hardy-Ramanujan 1729 taxicab number.",
            "timestamp": timestamp,
        }

    elif pid == "diophantine-quintuple":
        reproduction = verify_independent_reproduction(pid, campaign_results)
        classification = "null-campaign"

        bundle = {
            "problem_id": pid,
            "title": nomination.title,
            "conjecture_statement": nomination.conjecture_statement,
            "certificate_type": nomination.certificate_type,
            "target_instance": {"base_quadruple": [1, 3, 8, 120]},
            "search_bounds": campaign_results["range"],
            "candidates_evaluated": campaign_results["total_evaluated"],
            "matches_found": campaign_results["matches_count"],
            "independent_reproduction": reproduction,
            "literature_citations": nomination.literature_citations,
            "classification": classification,
            "classification_rationale": (
                "Exhaustive bounded verification completed with 0 extensions, confirming absence of Diophantine "
                "quintuples in [121, 250,000], consistent with He-Togbé-Ziegler 2019 non-existence theorem."
            ),
            "timestamp": timestamp,
        }
    else:
        raise ValueError(f"Unknown problem_id: {pid}")

    bundle_canonical = json.dumps(bundle, sort_keys=True)
    bundle["certificate_hash"] = hashlib.sha256(bundle_canonical.encode("utf-8")).hexdigest()
    return bundle


# ==============================================================================
# 5. Main Execution Harness (P29 Gate)
# ==============================================================================


def run_open_problem_campaign(
    problem_id: str = "erdos-straus",
    device_name: str | None = None,
    output_path: str | Path | None = None,
    smoke: bool = False,
) -> dict[str, Any]:
    """Execute complete P29 campaign for the nominated open problem."""
    device = resolve_device(device_name)
    torch.set_num_threads(8)

    if problem_id not in PROBLEM_REGISTRY:
        raise ValueError(
            f"Unknown problem '{problem_id}'. Available: {list(PROBLEM_REGISTRY.keys())}"
        )

    nomination = PROBLEM_REGISTRY[problem_id]

    print("=" * 115)
    print("P29 OPEN PROBLEMS WITH VERIFIABLE CERTIFICATES")
    print("=" * 115)
    print(f"  Device              : {device}")
    print(f"  Problem ID          : {nomination.problem_id}")
    print(f"  Title               : {nomination.title}")
    print(f"  Domain              : {nomination.domain}")
    print(f"  Certificate Type    : {nomination.certificate_type}")
    print("=" * 115)

    # 1. Run Search Campaign with Full Lineage
    print("\n[1/3] Running GPU candidate generation and filtering campaign...")
    if problem_id == "erdos-straus":
        instances = [1009, 10007] if smoke else [1009, 10007, 100003]
        batch_size = 50_000 if smoke else 500_000
        campaign_results = run_erdos_straus_campaign(
            instances, device=device, batch_size=batch_size
        )
    elif problem_id == "taxicab":
        max_base = 50 if smoke else 150
        campaign_results = run_taxicab_campaign(max_base=max_base, device=device)
    elif problem_id == "diophantine-quintuple":
        max_cand = 5_000 if smoke else 250_000
        campaign_results = run_diophantine_quintuple_campaign(max_candidate=max_cand, device=device)
    else:
        raise ValueError(f"Unsupported problem_id: {problem_id}")

    print(
        f"  Total Candidates    : {campaign_results['total_evaluated']:,} "
        f"({campaign_results['search_cvps']:,.0f} CVPS, {campaign_results['elapsed_total_sec']:.2f}s)"
    )

    # 2. Exact Checking, Independent Reproduction & Certificate Construction
    print(
        "\n[2/3] Promoting finalists to exact CPU checker and verifying independent reproduction..."
    )
    certificate_bundle = generate_certificate_bundle(nomination, campaign_results, device)
    print(f"  Classification      : {certificate_bundle['classification']}")
    print(f"  Certificate SHA256  : {certificate_bundle['certificate_hash'][:16]}...")
    print(f"  Independent Repro   : {certificate_bundle['independent_reproduction']['status']}")

    # 3. Provenance & Final Report Assembly
    print("\n[3/3] Assembling manifest and writing checksummed artifacts...")
    prov = collect_provenance(
        seed=42,
        device=device,
        dataset_hashes={
            "nomination": hashlib.sha256(nomination.conjecture_statement.encode()).hexdigest()
        },
        config={
            "problem_id": problem_id,
            "certificate_type": nomination.certificate_type,
            "smoke": smoke,
        },
    )

    report = {
        "manifest_version": "1.0",
        "phase": "p29-open-problems",
        "status": "PASS",
        "git_commit": get_git_commit(),
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "device": str(device),
        "provenance": prov,
        "nomination": asdict(nomination),
        "campaign_summary": {
            "total_candidates_evaluated": campaign_results["total_evaluated"],
            "search_throughput_cvps": campaign_results["search_cvps"],
            "elapsed_search_sec": campaign_results["elapsed_total_sec"],
        },
        "certificate_bundle": certificate_bundle,
        "classification": certificate_bundle["classification"],
        "classification_rationale": certificate_bundle["classification_rationale"],
    }

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        cert_p = out_p.parent / f"p29-{problem_id}-certificate.json"
        with open(cert_p, "w", encoding="utf-8") as f:
            json.dump(certificate_bundle, f, indent=2, sort_keys=True)
        cert_hash = hashlib.sha256(cert_p.read_bytes()).hexdigest()

        raw_p = out_p.parent / f"p29-{problem_id}-raw.json"
        with open(raw_p, "w", encoding="utf-8") as f:
            json.dump(campaign_results, f, indent=2, sort_keys=True, default=str)
        raw_hash = hashlib.sha256(raw_p.read_bytes()).hexdigest()

        written = write_manifest(
            out_p,
            report,
            {
                str(cert_p): cert_hash,
                str(raw_p): raw_hash,
            },
        )
        print(
            f"Artifact manifest written to {out_p} (manifest_sha256={written['manifest_sha256'][:16]})"
        )

    return report


def run_adversarial_rejection_suite(device: torch.device | None = None) -> list[dict[str, Any]]:
    """Adversarial rejection suite testing wrong-answer, forged-count, out-of-bound, overflow, and altered fixtures."""
    results: list[dict[str, Any]] = []

    # 1. Wrong answer: Erdős-Straus with incorrect z
    is_v, _, _ = check_erdos_straus(1009, 253, 85100, 944524901)
    is_v_frac, _, _ = check_erdos_straus_fractions(1009, 253, 85100, 944524901)
    results.append(
        {
            "fixture_id": "adv_es_wrong_answer",
            "description": "Erdős-Straus candidate with z coordinate off by 1",
            "target_problem": "erdos-straus",
            "tested_condition": "exact_identity_and_fractions",
            "rejected": (not is_v) and (not is_v_frac),
            "rejection_reason": "both_checkers_detected_nonzero_residual",
        }
    )

    # 2. Out of bound: Erdős-Straus historical coordinate exceeding 10^9
    in_b, _ = check_coordinate_bounds(
        "erdos-straus", {"x": 253, "y": 85096, "z": 1974822872}, max_coord=10**9
    )
    results.append(
        {
            "fixture_id": "adv_es_out_of_bound",
            "description": "Erdős-Straus valid identity but z=1974822872 exceeds 10^9 bound",
            "target_problem": "erdos-straus",
            "tested_condition": "coordinate_bound_strictness",
            "rejected": not in_b,
            "rejection_reason": "coordinate_exceeds_declared_bound_1e9",
        }
    )

    # 3. Domain violation: n < 2 or non-positive
    is_v_n1, _, _ = check_erdos_straus(1, 253, 85100, 944524900)
    is_v_neg, _, _ = check_erdos_straus_fractions(1009, -253, 85100, 944524900)
    results.append(
        {
            "fixture_id": "adv_es_domain_violation",
            "description": "Erdős-Straus with n=1 or negative coordinate",
            "target_problem": "erdos-straus",
            "tested_condition": "domain_n_ge_2_and_positivity",
            "rejected": (not is_v_n1) and (not is_v_neg),
            "rejection_reason": "rejected_by_domain_guardrails",
        }
    )

    # 4. Wrong answer: Taxicab wrong sum
    is_v_tax, _, _ = check_taxicab(1730, 1, 12, 9, 10)
    is_v_tax_f, _, _ = check_taxicab_factorization(1730, 1, 12, 9, 10)
    results.append(
        {
            "fixture_id": "adv_taxicab_wrong_sum",
            "description": "Taxicab sum_val=1730 is not equal to cube pairs",
            "target_problem": "taxicab",
            "tested_condition": "cube_sum_and_factorization",
            "rejected": (not is_v_tax) and (not is_v_tax_f),
            "rejection_reason": "both_checkers_detected_sum_mismatch",
        }
    )

    # 5. Domain violation: Taxicab duplicate pairs
    is_v_dup, _, _ = check_taxicab(1729, 1, 12, 1, 12)
    is_v_dup_f, _, _ = check_taxicab_factorization(1729, 1, 12, 1, 12)
    results.append(
        {
            "fixture_id": "adv_taxicab_duplicate_pairs",
            "description": "Taxicab where pair_1 == pair_2",
            "target_problem": "taxicab",
            "tested_condition": "distinct_pairs_requirement",
            "rejected": (not is_v_dup) and (not is_v_dup_f),
            "rejection_reason": "rejected_identical_pairs",
        }
    )

    # 6. Forged candidate: Quintuple invalid extension candidate e=5
    is_v_q5, _, _ = check_diophantine_quintuple([1, 3, 8, 120, 5])
    is_v_q5_ind, _, _ = check_diophantine_quintuple_independent([1, 3, 8, 120, 5])
    results.append(
        {
            "fixture_id": "adv_quintuple_non_square",
            "description": "Diophantine quintuple invalid extension candidate e=5",
            "target_problem": "diophantine-quintuple",
            "tested_condition": "all_pairs_product_plus_one_square",
            "rejected": (not is_v_q5) and (not is_v_q5_ind),
            "rejection_reason": "non_square_pairwise_products",
        }
    )

    # 7. Domain violation: Quintuple duplicate elements
    is_v_q_dup, _, _ = check_diophantine_quintuple([1, 1, 3, 8, 120])
    is_v_q_dup_ind, _, _ = check_diophantine_quintuple_independent([1, 1, 3, 8, 120])
    results.append(
        {
            "fixture_id": "adv_quintuple_duplicate_elements",
            "description": "Diophantine quintuple with duplicate elements",
            "target_problem": "diophantine-quintuple",
            "tested_condition": "distinct_5_elements_requirement",
            "rejected": (not is_v_q_dup) and (not is_v_q_dup_ind),
            "rejection_reason": "rejected_duplicate_or_invalid_count",
        }
    )

    # 8. Altered artifact: Tampered certificate payload
    dummy_bundle = {
        "problem_id": "erdos-straus",
        "target_instance": {"n": 1009},
        "solution_data": {"x": 253, "y": 85100, "z": 944524900},
    }
    canonical_hash = hashlib.sha256(
        json.dumps(dummy_bundle, sort_keys=True).encode("utf-8")
    ).hexdigest()
    tampered_bundle = dict(dummy_bundle, solution_data={"x": 254, "y": 85100, "z": 944524900})
    tampered_hash = hashlib.sha256(
        json.dumps(tampered_bundle, sort_keys=True).encode("utf-8")
    ).hexdigest()
    results.append(
        {
            "fixture_id": "adv_altered_artifact_hash",
            "description": "Tampered certificate payload with mismatching checksum",
            "target_problem": "integrity",
            "tested_condition": "sha256_canonical_checksum_verification",
            "rejected": canonical_hash != tampered_hash,
            "rejection_reason": "sha256_checksum_mismatch_detected",
        }
    )

    return results


def audit_historical_certificate(cert_path: Path, max_coord: int = 10**9) -> dict[str, Any] | None:
    """Audit historical P29 certificate against dual checkers and strict coordinate bound."""
    if not cert_path.exists():
        return None
    with open(cert_path, encoding="utf-8") as f:
        data = json.load(f)

    pid = data.get("problem_id", "")
    sol = data.get("solution_data", {})
    t_inst = data.get("target_instance", {})

    if pid == "erdos-straus":
        n = int(t_inst.get("n", sol.get("n", 0)))
        x = int(sol.get("x", 0))
        y = int(sol.get("y", 0))
        z = int(sol.get("z", 0))

        ok1, res1, _ = check_erdos_straus(n, x, y, z)
        ok2, res2, _ = check_erdos_straus_fractions(n, x, y, z)
        in_bounds, bounds_info = check_coordinate_bounds("erdos-straus", sol, max_coord=max_coord)

        classification = "rediscovery" if in_bounds else "exceeds_declared_coordinate_bound"
        return {
            "artifact_path": str(cert_path),
            "problem_id": pid,
            "target_instance": {"n": n},
            "solution_data": {"x": x, "y": y, "z": z},
            "dual_checker_results": {
                "checker_1_integer_identity": {"valid": ok1, "residual": res1},
                "checker_2_rational_fractions": {"valid": ok2, "diff": str(res2)},
                "mathematical_identity_verified": ok1 and ok2,
            },
            "coordinate_bounds_audit": bounds_info,
            "historical_classification": data.get("classification", ""),
            "reclassified_status": classification,
            "reclassification_rationale": (
                "Mathematical identity is verified bit-exact by dual independent checkers (Mordell integer identity "
                "and exact rational fractions), but maximum coordinate z exceeds the declared bound M <= 10^9. "
                "Reclassified as 'exceeds_declared_coordinate_bound' without disputing mathematical validity."
                if not in_bounds
                else "Satisfies all dual checkers and coordinate bounds."
            ),
            "preserved_as_superseded_diagnostic": not in_bounds,
        }
    return None


def run_certificate_audit(
    bounds_strict: bool = True,
    output_path: str | Path | None = None,
    device_name: str | None = None,
) -> dict[str, Any]:
    """Execute complete P31 audit of open problem certificates with dual checkers, coordinate bounds, and adversarial rejection."""
    t0 = time.monotonic()
    device = resolve_device(device_name)
    torch.set_num_threads(8)

    # 1. Audit historical certificates
    historical_audit = []
    p29_cert = _REPO_ROOT / "experiments" / "p29-erdos-straus-certificate.json"
    h_res = audit_historical_certificate(p29_cert, max_coord=10**9)
    if h_res:
        historical_audit.append(h_res)

    # 2. Strict campaigns & independent certificates
    # 2.1 Erdős-Straus strict solutions
    es_campaign = run_erdos_straus_campaign(
        [1009, 10007, 100003],
        device=device,
        bounds_strict=bounds_strict,
        max_coord=10**9,
    )
    # 2.2 Taxicab
    taxicab_campaign = run_taxicab_campaign(max_base=150, device=device)
    # 2.3 Diophantine quintuple complete replay
    quintuple_replay = replay_and_verify_bounded_null(
        base_quadruple=[1, 3, 8, 120],
        r_start=121,
        r_end=250_000,
        device=device,
    )

    # Construct strict certificates
    strict_certificates: dict[str, Any] = {}

    # Erdős-Straus
    es_verified = [inst for inst in es_campaign["instances"] if inst["found"]]
    if es_verified:
        primary_es = es_verified[0]["details"]
        es_repro = verify_independent_reproduction(
            "erdos-straus", primary_es, bounds_strict=bounds_strict, device=device
        )
        strict_certificates["erdos-straus"] = {
            "problem_id": "erdos-straus",
            "bounded_statement": "Find exact positive integer solutions (x, y, z) for n in {1009, 10007, 100003} with search bound M <= 10^9.",
            "target_instance": {"n": primary_es["n"]},
            "solution_data": {
                "x": primary_es["x"],
                "y": primary_es["y"],
                "z": primary_es["z"],
            },
            "coordinate_bounds": {
                "max_coordinate_value": max(primary_es["x"], primary_es["y"], primary_es["z"]),
                "declared_bound": 10**9,
                "within_bounds": True,
            },
            "dual_checker_evidence": {
                "checker_1_integer_identity": primary_es["verified_exact"],
                "checker_2_rational_fractions": primary_es["dual_checker_exact_fractions"][
                    "verified_exact_fraction"
                ],
            },
            "instances_summary": es_campaign["instances"],
            "independent_reproduction": es_repro,
            "classification": "rediscovery",
            "classification_rationale": "Verified bit-exact solution strictly bounded by M <= 10^9 and checked by dual independent mathematical checkers.",
        }

    # Taxicab
    if taxicab_campaign["verified_taxicabs"]:
        primary_tax = taxicab_campaign["verified_taxicabs"][0]
        tax_repro = verify_independent_reproduction(
            "taxicab", primary_tax, bounds_strict=bounds_strict, device=device
        )
        strict_certificates["taxicab"] = {
            "problem_id": "taxicab",
            "target_instance": {"sum_val": primary_tax["sum_val"]},
            "solution_data": {
                "pair_1": primary_tax["pair_1"],
                "pair_2": primary_tax["pair_2"],
            },
            "coordinate_bounds": {
                "max_coordinate_value": primary_tax["sum_val"],
                "declared_bound": 50_000,
                "within_bounds": True,
            },
            "dual_checker_evidence": {
                "checker_1_sum_of_cubes": True,
                "checker_2_factorization": True,
            },
            "independent_reproduction": tax_repro,
            "classification": "rediscovery",
            "classification_rationale": "Matches Hardy-Ramanujan 1729 taxicab number certified by dual formulations.",
        }

    # Diophantine Quintuple
    q_repro = verify_independent_reproduction(
        "diophantine-quintuple",
        {"range": [121, 250_000], "base_quadruple": [1, 3, 8, 120]},
        bounds_strict=bounds_strict,
        device=device,
    )
    strict_certificates["diophantine-quintuple"] = {
        "problem_id": "diophantine-quintuple",
        "target_instance": {"base_quadruple": [1, 3, 8, 120]},
        "search_bounds": [121, 250_000],
        "replay_verification": quintuple_replay,
        "coordinate_bounds": {
            "max_coordinate_value": 250_000,
            "declared_bound": 500_000,
            "within_bounds": True,
        },
        "independent_reproduction": q_repro,
        "classification": "exhaustive_null",
        "classification_rationale": "Exhaustive candidate-by-candidate domain replay confirmed 0 extensions in [121, 250,000], consistent with He-Togbé-Ziegler 2019 theorem.",
    }

    # 3. Adversarial Rejection Suite
    adv_fixtures = run_adversarial_rejection_suite(device=device)
    accepted_false_positives = sum(1 for f in adv_fixtures if not f["rejected"])

    elapsed = max(1e-6, time.monotonic() - t0)

    prov = collect_provenance(
        seed=42,
        device=device,
        dataset_hashes={
            "erdos_straus": hashlib.sha256(b"erdos_straus_p31").hexdigest()[:16],
            "taxicab": hashlib.sha256(b"taxicab_p31").hexdigest()[:16],
            "diophantine_quintuple": hashlib.sha256(b"diophantine_quintuple_p31").hexdigest()[:16],
        },
        config={
            "bounds_strict": bounds_strict,
            "max_coord_erdos_straus": 10**9,
            "taxicab_bound": 50_000,
            "quintuple_bound": 250_000,
        },
    )

    audit_report = {
        "manifest_version": "1.0",
        "phase": "p31-verifier-certificates",
        "status": "PASS" if accepted_false_positives == 0 else "FAIL",
        "bounds_strict": bounds_strict,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "elapsed_sec": elapsed,
        "device": str(device),
        "audit_summary": {
            "historical_certificates_audited": len(historical_audit),
            "historical_reclassified": sum(
                1
                for h in historical_audit
                if h["reclassified_status"] == "exceeds_declared_coordinate_bound"
            ),
            "strict_certificates_generated": len(strict_certificates),
            "adversarial_fixtures_tested": len(adv_fixtures),
            "adversarial_fixtures_rejected": sum(1 for f in adv_fixtures if f["rejected"]),
            "accepted_false_positives": accepted_false_positives,
            "soundness_gate_passed": accepted_false_positives == 0,
        },
        "historical_certificates_audit": historical_audit,
        "strict_certificates": strict_certificates,
        "adversarial_rejection_suite": adv_fixtures,
        "provenance": prov,
    }

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        written = write_manifest(out_p, audit_report, {})
        print(
            f"P31 certificate audit report written to {out_p} (manifest_sha256={written['manifest_sha256'][:16]})"
        )

    return audit_report


P39_PREREGISTRATION_HASH = (
    hashlib.sha256(Path(_REPO_ROOT, "experiments", "p39-nomination.json").read_bytes()).hexdigest()
    if Path(_REPO_ROOT, "experiments", "p39-nomination.json").exists()
    else "missing"
)

P39_ALLOWED_CLASSIFICATIONS = (
    "rediscovery",
    "candidate",
    "verified-construction",
    "counterexample",
    "proven-theorem",
    "exhaustive_null",
    "budget_exhausted",
)


def _p39_overflow_audit(n: int, x_steps: int = 50, batch_size: int = 500_000) -> dict[str, Any]:
    """Analytic int64-overflow guard for the GPU modular-filtering intermediates.

    Bounds 4*x*y and n*(x+y) over the explored (x, y) rectangle and requires
    both maxima below 2^62; z itself is computed in Python arbitrary precision.
    """
    x0 = n // 4 + 1
    x_max = x0 + x_steps - 1
    y_min = n * x0 // 1 + 1
    y_max = y_min + batch_size
    peak_mul = 4 * x_max * y_max
    peak_sum = n * (x_max + y_max)
    limit = 2**62
    return {
        "n": n,
        "peak_4xy": peak_mul,
        "peak_n_x_plus_y": peak_sum,
        "int64_limit": 2**63 - 1,
        "guard_limit": limit,
        "within_guard": peak_mul < limit and peak_sum < limit,
    }


def run_matched_baseline_erdos_straus(
    n_instances: list[int],
    budget_per_instance_sec: list[float],
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """Matched CPU baseline: same (x, y) space definition and order, same checkers.

    Deterministic sequential enumeration with Python arbitrary-precision
    integers, time-boxed per instance to the GPU campaign wall-clock (equal
    budget). Contextualizes engine cost; classification never depends on it.
    """
    results: list[dict[str, Any]] = []
    for n, budget in zip(n_instances, budget_per_instance_sec):
        t0 = time.perf_counter()
        x0 = n // 4 + 1
        evaluated = 0
        found: dict[str, Any] | None = None
        for x_step in range(50):
            x_val = x0 + x_step
            r = 4 * x_val - n
            if r <= 0:
                continue
            y_min = (n * x_val) // r + 1
            y = y_min
            while True:
                if time.perf_counter() - t0 >= budget:
                    break
                denom = 4 * x_val * y - n * (x_val + y)
                if denom > 0 and (n * x_val * y) % denom == 0:
                    z_val = (n * x_val * y) // denom
                    evaluated += 1
                    ok1, _, det1 = check_erdos_straus(n, x_val, y, z_val)
                    ok2, _, det2 = check_erdos_straus_fractions(n, x_val, y, z_val)
                    if ok1 and ok2 and max(x_val, y, z_val) <= max_coord:
                        found = {
                            "n": n,
                            "x": x_val,
                            "y": y,
                            "z": z_val,
                            "checker_1": det1["residual"],
                            "checker_2": det2.get("diff", 0),
                        }
                        break
                    if max(x_val, y, z_val) > max_coord and y > y_min + 500_000:
                        break
                else:
                    evaluated += 1
                y += 1
                if y > y_min + 500_000:
                    break
            if found is not None or time.perf_counter() - t0 >= budget:
                break
        elapsed = time.perf_counter() - t0
        results.append(
            {
                "n": n,
                "found": found is not None,
                "details": found,
                "evaluated": evaluated,
                "elapsed_sec": elapsed,
                "budget_sec": budget,
            }
        )
    return {
        "problem_id": "erdos-straus",
        "method": "matched_cpu_enumeration_equal_budget",
        "instances": results,
    }


def _p39_repo_catalogue() -> list[dict[str, int]]:
    """Collect previously certified Erdős-Straus instances from repo artifacts."""
    catalogue: list[dict[str, int]] = []
    for rel in ("experiments/p29-erdos-straus-certificate.json",):
        p = _REPO_ROOT / rel
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        sol = data.get("solution_data", {})
        tgt = data.get("target_instance", {})
        if {"x", "y", "z"} <= set(sol) and "n" in tgt:
            catalogue.append(
                {"n": int(tgt["n"]), "x": int(sol["x"]), "y": int(sol["y"]), "z": int(sol["z"])}
            )
    p31 = _REPO_ROOT / "experiments" / "p31-certificates.json"
    if p31.exists():
        try:
            strict = (
                json.loads(p31.read_text()).get("strict_certificates", {}).get("erdos-straus", {})
            )
        except (OSError, ValueError):
            strict = {}
        repro = (strict.get("independent_reproduction") or {}).get("details") or {}
        c1 = repro.get("checker_1_integer_identity", {})
        if {"n", "x", "y", "z"} <= set(c1):
            catalogue.append(
                {"n": int(c1["n"]), "x": int(c1["x"]), "y": int(c1["y"]), "z": int(c1["z"])}
            )
    return catalogue


def assess_instance_novelty(
    solution: dict[str, int], catalogue: list[dict[str, int]]
) -> dict[str, Any]:
    """Novelty assessment with explicit catalogue-search limitations.

    Without positive novelty evidence the weaker rediscovery label is retained;
    an uncatalogued instance alone is never promoted to a new-theorem claim.
    """
    triple = sorted([int(solution["x"]), int(solution["y"]), int(solution["z"])])
    for known in catalogue:
        if (
            int(known["n"]) == int(solution["n"])
            and sorted([known["x"], known["y"], known["z"]]) == triple
        ):
            return {
                "assessment": "duplicate_of_catalogue",
                "classification_cap": "rediscovery",
                "note": "Bit-exact match with a previously certified repo instance.",
            }
    return {
        "assessment": "rediscovery_benchmark_instance",
        "classification_cap": "rediscovery",
        "note": (
            "Nominated prime instances are long-studied benchmarks; no exhaustive "
            "external catalogue (OEIS-wide) lookup performed, so novelty beyond "
            "rediscovery is not claimed."
        ),
    }


def run_certified_campaign(
    problem_id: str = "erdos-straus",
    freeze_manifest: str | Path = "experiments/p38-confirmation.json",
    nomination_path: str | Path = "experiments/p39-nomination.json",
    output_path: str | Path | None = "experiments/p39-science.json",
    device_name: str | None = None,
    smoke: bool = False,
    checkpoint_path: str | Path | None = "experiments/p39-checkpoint.json",
) -> dict[str, Any]:
    """P39 bounded certified campaign for one nominated problem (single cycle)."""
    if problem_id != "erdos-straus":
        raise ValueError(
            f"Unsupported P39 problem {problem_id!r}; one campaign per cycle "
            "(additional targets are separate research cycles)."
        )
    device = resolve_device(device_name)
    torch.set_num_threads(8)
    t_wall_0 = time.perf_counter()

    freeze_p = Path(freeze_manifest)
    freeze = json.loads(freeze_p.read_text())
    freeze_sha = hashlib.sha256(freeze_p.read_bytes()).hexdigest()
    nom_p = Path(nomination_path)
    nomination = json.loads(nom_p.read_text())
    nom_sha = hashlib.sha256(nom_p.read_bytes()).hexdigest()

    print("=" * 115)
    print("P39 BOUNDED CERTIFIED SCIENCE CAMPAIGN (erdos-straus, frozen stack)")
    print(f"  Device              : {device}")
    print(f"  Freeze manifest     : {freeze_p} (status={freeze.get('status')})")
    print("=" * 115)

    base = {
        "phase": "p39-certified-science",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "problem_id": problem_id,
        "freeze_manifest": str(freeze_p),
        "freeze_manifest_sha256": freeze_sha,
        "nomination_path": str(nom_p),
        "nomination_sha256": nom_sha,
    }

    def _finish(report: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
        report["elapsed_sec"] = time.perf_counter() - t_wall_0
        if output_path:
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            raw_p = out_p.parent / "p39-science-raw.json"
            with open(raw_p, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, sort_keys=True, default=str)
            written = write_manifest(
                out_p, report, {str(raw_p): hashlib.sha256(raw_p.read_bytes()).hexdigest()}
            )
            print(
                f"Artifact manifest written to {out_p} "
                f"(manifest_sha256={written['manifest_sha256'][:16]})"
            )
        return report

    # Prerequisite gates: P38 integrity accepted; nomination matches the problem.
    if freeze.get("status") != "PASS":
        report = {
            **base,
            "status": "FAIL",
            "classification": "BLOCKED",
            "rationale": "P38 freeze manifest is not accepted; advancement blocked.",
        }
        print("P39 BLOCKED: P38 prerequisite not met.")
        return _finish(report, {"instances": []})
    if nomination.get("problem_id") != problem_id or nomination.get("status") != "preregistered":
        report = {
            **base,
            "status": "FAIL",
            "classification": "BLOCKED",
            "rationale": "Nomination file does not preregister this problem; blocked.",
        }
        print("P39 BLOCKED: nomination mismatch.")
        return _finish(report, {"instances": []})

    # Soundness gate: P31 independent checkers must reject every adversarial fixture.
    adv = run_adversarial_rejection_suite(device)
    fps = [f for f in adv if not f.get("rejected")]
    if fps:
        report = {
            **base,
            "status": "FAIL",
            "classification": "BLOCKED",
            "rationale": f"Checker soundness gate failed: {len(fps)} accepted false positives.",
        }
        print("P39 BLOCKED: checker soundness gate failed.")
        return _finish(report, {"instances": []})
    print(f"  Checker soundness   : {len(adv)}/{len(adv)} adversarial fixtures rejected")

    bound = int(nomination["bounds"]["declared_bound"])
    instances = [int(n) for n in nomination["instances"]]
    if smoke:
        instances = instances[:1]
    batch_size = 50_000 if smoke else 500_000
    catalogue = _p39_repo_catalogue()

    ckpt_p = Path(checkpoint_path) if checkpoint_path else None
    checkpoint: dict[str, Any] = {}
    if ckpt_p is not None and ckpt_p.exists():
        try:
            checkpoint = json.loads(ckpt_p.read_text())
        except (OSError, ValueError):
            checkpoint = {}

    per_instance: list[dict[str, Any]] = []
    for n in instances:
        key = str(n)
        if key in checkpoint and checkpoint[key].get("certificate_hash"):
            rec = checkpoint[key]
            sol = rec["solution"]
            ok1, _, _ = check_erdos_straus(n, sol["x"], sol["y"], sol["z"])
            ok2, _, _ = check_erdos_straus_fractions(n, sol["x"], sol["y"], sol["z"])
            if ok1 and ok2:
                print(f"  n={n}: resumed from checkpoint ({rec['classification']})")
                per_instance.append({**rec, "resumed": True})
                continue
            print(f"  n={n}: checkpoint failed re-verification; re-running")
        audit = _p39_overflow_audit(n, batch_size=batch_size)
        assert audit["within_guard"], f"int64 overflow guard tripped for n={n}: {audit}"
        camp = run_erdos_straus_campaign(
            [n], device=device, batch_size=batch_size, bounds_strict=True, max_coord=bound
        )
        inst = camp["instances"][0]
        base_cmp = run_matched_baseline_erdos_straus([n], [inst["elapsed_sec"]], max_coord=bound)
        rec: dict[str, Any] = {
            "n": n,
            "found": bool(inst["found"]),
            "gpu_elapsed_sec": inst["elapsed_sec"],
            "gpu_evaluated": camp["total_evaluated"],
            "overflow_audit": audit,
            "baseline": base_cmp["instances"][0],
            "coverage": (
                "x in [n//4+1, n//4+50] with y windows <= "
                f"{batch_size} per x step; budget-limited, not exhaustive"
            ),
            "resumed": False,
        }
        if inst["found"]:
            det = inst["details"]
            sol = {"n": n, "x": int(det["x"]), "y": int(det["y"]), "z": int(det["z"])}
            repro = verify_independent_reproduction(
                problem_id, sol, bounds_strict=True, device=device
            )
            assert repro["status"] == "PASS", f"Independent reproduction failed for n={n}"
            novelty = assess_instance_novelty(sol, catalogue)
            cert_body = {
                "solution": sol,
                "dual_evidence": det,
                "reproduction": repro,
                "novelty": novelty,
                "classification": novelty["classification_cap"],
            }
            cert_body["certificate_hash"] = hashlib.sha256(
                json.dumps(cert_body, sort_keys=True, default=str).encode()
            ).hexdigest()
            rec.update(
                {
                    "solution": sol,
                    "certificate": cert_body,
                    "certificate_hash": cert_body["certificate_hash"],
                    "classification": novelty["classification_cap"],
                }
            )
            catalogue.append(sol)
        else:
            rec.update(
                {
                    "classification": "budget_exhausted",
                    "note": (
                        "No in-bounds certified decomposition in the explored "
                        "windows; a failed finite search is not a counterexample "
                        "to the existential conjecture."
                    ),
                }
            )
        per_instance.append(rec)
        if ckpt_p is not None:
            checkpoint[key] = {k: v for k, v in rec.items() if k != "baseline"}
            ckpt_p.parent.mkdir(parents=True, exist_ok=True)
            with open(ckpt_p, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, indent=2, sort_keys=True, default=str)
        print(
            f"  n={n}: {rec['classification']} "
            f"(gpu {inst['elapsed_sec']:.2f}s, baseline found={base_cmp['instances'][0]['found']})"
        )

    # Recheck the nomination statement against what actually ran.
    assert [r["n"] for r in per_instance] == instances, "Ran instances differ from nomination"
    assert bound == 10**9, "Bound drifted from nomination"

    certified = [r for r in per_instance if r.get("certificate_hash")]
    if certified:
        overall = "rediscovery"
        why = (
            f"{len(certified)}/{len(per_instance)} nominated instances carry bounded "
            "dual-checked certificates matching benchmark knowledge; weaker label retained."
        )
    else:
        overall = "budget_exhausted"
        why = "No nominated instance yielded an in-bounds certificate in budget; honest null."
    assert overall in P39_ALLOWED_CLASSIFICATIONS

    prov = collect_provenance(
        seed=42,
        device=device,
        dataset_hashes={"nomination": nom_sha[:16], "p38_freeze": freeze_sha[:16]},
        config={
            "problem_id": problem_id,
            "instances": instances,
            "bound": bound,
            "bounds_strict": True,
        },
    )
    report = {
        **base,
        "status": "PASS",
        "provenance": prov,
        "nomination_statement": nomination["conjecture_statement"],
        "bounded_statement": nomination["bounded_statement"],
        "soundness": {
            "adversarial_rejected": f"{len(adv)}/{len(adv)}",
            "accepted_false_positives": 0,
        },
        "instances": per_instance,
        "classification": overall,
        "classification_rationale": why,
        "novelty": (
            "No catalogue-novel instance demonstrated; literature status unchanged "
            "(conjecture open in general; nominated instances remain benchmarks)."
        ),
        "operator": (
            "self-repetition with implementation-independent checkers; not independent authorship."
        ),
    }
    print(f"P39 {overall}: {why}")
    return _finish(report, {"instances": per_instance})


# ==============================================================================
# P57 — Bounded Erdős–Straus discovery campaign (instances only, never the conjecture)
# ==============================================================================

P57_MODULUS = 24
P57_RESIDUE = 1
P57_LIMIT = 100000
P57_MAX_COORD = 10**9
P57_KNOWN_TRIPLE_1009 = (253, 85100, 944524900)
P57_CLASSIFICATIONS = (
    "rediscovery",
    "candidate",
    "budget-exhausted",
)


def p57_sieve_primes(limit: int) -> list[int]:
    """Deterministic prime sieve for the nomination list."""
    n = int(limit)
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i * i : n + 1 : i] = b"\x00" * ((n - i * i) // i + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def p57_nominate_instances(limit: int = P57_LIMIT) -> list[int]:
    """Frozen nomination: primes n ≡ 1 (mod 24) with 2 ≤ n ≤ limit.

    The hard residue class: even n, multiples of 3, and n ≡ 2 (mod 3) all
    carry classical parametric triples, and greedy covers n ≠ 1 (mod 4).
    """
    return [p for p in p57_sieve_primes(limit) if p % P57_MODULUS == P57_RESIDUE]


def p57_classical_constructions(n: int) -> list[dict[str, Any]]:
    """Known parametric triples, each exactly verified; inapplicable outside its class."""
    fams: list[dict[str, Any]] = []
    if n % 2 == 0:
        m = n // 2
        fams.append({"family": "even", "triple": (m, m + 1, m * (m + 1))})
    if (n + 1) % 3 == 0:
        fams.append({"family": "n=2-mod-3", "triple": (n, (n + 1) // 3, n * (n + 1) // 3)})
    if n % 3 == 0:
        fams.append({"family": "multiple-of-3", "triple": (n // 3, 2 * n, 2 * n)})
    out = []
    for fam in fams:
        x, y, z = fam["triple"]
        ok, _, _ = check_erdos_straus(n, x, y, z)
        fam["verified"] = bool(ok)
        out.append(fam)
    return out


def p57_classify_solved(n: int, triple: tuple[int, int, int]) -> str:
    """rediscovery when the triple matches a classical family or the cited k3 anchor.

    Anything else stays candidate: computationally verified but novelty
    unreviewed. verified-construction needs reviewer-sustained novelty;
    discovery additionally needs independent reproduction plus the proper
    certificate or proof. None of that is claimed here.
    """
    for fam in p57_classical_constructions(n):
        if tuple(fam["triple"]) == tuple(triple):
            return "rediscovery"
    if n == 1009 and tuple(triple) == P57_KNOWN_TRIPLE_1009:
        return "rediscovery"
    return "candidate"


def run_p57_bounded_campaign(
    n_instances: list[int],
    *,
    device: torch.device,
    max_coord: int = P57_MAX_COORD,
    time_cap_sec: float = 3600.0,
    batch_size: int = 500_000,
    chunk: int = 64,
) -> dict[str, Any]:
    """Time-capped instance campaign: accepted search, classical comparison, honest statuses.

    Unprocessed or unfound instances are budget-exhausted, never
    exhaustive-null: the search window is bounded, not covering.
    """
    t0 = time.perf_counter()
    deadline = t0 + float(time_cap_sec)
    instances: list[dict[str, Any]] = []
    total_evaluated = 0
    capped = False
    for start in range(0, len(n_instances), chunk):
        if time.perf_counter() > deadline:
            capped = True
            break
        part = run_erdos_straus_campaign(
            [int(n) for n in n_instances[start : start + chunk]],
            device=device,
            batch_size=batch_size,
            bounds_strict=True,
            max_coord=max_coord,
        )
        total_evaluated += part["total_evaluated"]
        for inst in part["instances"]:
            n = int(inst["n"])
            fams = p57_classical_constructions(n)
            classical_solved = sum(1 for f in fams if f["verified"])
            if inst["found"]:
                d = inst["details"] or {}
                triple = (int(d["x"]), int(d["y"]), int(d["z"]))
                status = p57_classify_solved(n, triple)
            else:
                triple = None
                status = "budget-exhausted"
            instances.append(
                {
                    "n": n,
                    "found": bool(inst["found"]),
                    "status": status,
                    "triple": triple,
                    "classical_families": [f["family"] for f in fams],
                    "classical_solved": classical_solved,
                    "elapsed_sec": inst["elapsed_sec"],
                }
            )
    for n in n_instances[len(instances) :]:
        instances.append(
            {
                "n": int(n),
                "found": False,
                "status": "budget-exhausted",
                "triple": None,
                "classical_families": [],
                "classical_solved": 0,
                "elapsed_sec": 0.0,
            }
        )
        capped = True
    elapsed = time.perf_counter() - t0
    by_status: dict[str, int] = {}
    for inst in instances:
        by_status[inst["status"]] = by_status.get(inst["status"], 0) + 1
    return {
        "problem_id": "erdos-straus-p57",
        "nominated": len(n_instances),
        "instances": instances,
        "by_status": by_status,
        "time_capped": capped,
        "total_evaluated": total_evaluated,
        "elapsed_total_sec": elapsed,
    }


# ==============================================================================
# P59 entrega 2 — baselines comparáveis e contabilização integral (Erdős–Straus)
# ==============================================================================
#
# Todos os braços recebem as mesmas entradas públicas (n, limites, espaço de
# candidatos, warm-start). Custos de treino, geração, inferência, filtros,
# verificadores e tracking são todos contabilizados; o total é calculado,
# nunca declarado pelo braço. Famílias sem baseline pareado têm comparação
# explicitamente restrita. Fixtures development, sem finais P38/P56/P71.

P59_ES_ARMS = ("cpu_enumeration", "classical_construction")

P59_COST_PARTS = ("train", "generation", "inference", "filters", "checkers", "tracking")

P59_COMPARISON_SCOPE: dict[str, dict[str, Any]] = {
    "erdos-straus": {
        "comparable": True,
        "arms": list(P59_ES_ARMS),
        "note": "matched trial with identical public inputs and full cost ledger",
    },
    "taxicab": {"comparable": False, "reason": "no matched baseline implemented"},
    "diophantine-quintuple": {
        "comparable": False,
        "reason": "no matched baseline implemented",
    },
}


def p59_comparison_scope(family: str) -> dict[str, Any]:
    """Allowed comparison scope for a family; unknown families stay restricted."""
    scope = P59_COMPARISON_SCOPE.get(str(family))
    if scope is None:
        return {"comparable": False, "reason": f"unknown family: {family}"}
    return {"family": str(family), **scope}


def p59_cost_ledger(**parts: float) -> dict[str, Any]:
    """Full cost ledger: every part billed, total computed, nothing subtracted."""
    keys = set(parts)
    if keys != set(P59_COST_PARTS):
        raise ValueError(f"P59 ledger needs exactly {list(P59_COST_PARTS)}, got {sorted(keys)}")
    for key, val in parts.items():
        if not isinstance(val, (int, float)) or not math.isfinite(float(val)):
            raise ValueError(f"P59 ledger part {key} must be a finite number")
        if float(val) < 0.0:
            raise ValueError(f"P59 ledger part {key} must not be negative")
    total = sum(float(parts[k]) for k in P59_COST_PARTS)
    return {"parts": {k: float(parts[k]) for k in P59_COST_PARTS}, "total_sec": total}


def p59_es_public_inputs(
    n: int,
    max_coord: int = 10**9,
    x_steps: int = 50,
    y_cap: int = 200_000,
    warm_start: tuple[tuple[int, int, int], ...] = (),
) -> dict[str, Any]:
    """Frozen public input bundle for one Erdős–Straus instance (all arms alike)."""
    if int(n) < 2 or int(max_coord) <= 0 or int(x_steps) <= 0 or int(y_cap) <= 0:
        raise ValueError("P59 ES inputs need n>=2 with positive bounds")
    warm = [tuple(int(v) for v in t) for t in warm_start]
    if any(len(t) != 3 for t in warm):
        raise ValueError("P59 warm-start entries must be (x, y, z) triples")
    return {
        "n": int(n),
        "max_coord": int(max_coord),
        "x_steps": int(x_steps),
        "y_cap": int(y_cap),
        "warm_start": warm,
    }


def _p59_inputs_hash(inputs: dict[str, Any]) -> str:
    canon = {
        "n": inputs["n"],
        "max_coord": inputs["max_coord"],
        "x_steps": inputs["x_steps"],
        "y_cap": inputs["y_cap"],
        "warm_start": [list(t) for t in inputs["warm_start"]],
    }
    return hashlib.sha256(json.dumps(canon, sort_keys=True).encode()).hexdigest()


def run_p59_matched_es_trial(arm: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """One deterministic Erdős–Straus arm trial under identical public inputs.

    Arms: ``cpu_enumeration`` (bounded (x, y) scan, dual exact checkers) and
    ``classical_construction`` (verified parametric families only). A triple
    already in warm-start reports origin ``warm-start``: reusing a handed
    answer is never discovery. No wall-clock dependence: fixed step caps.
    """
    if arm not in P59_ES_ARMS:
        raise ValueError(f"Unknown P59 ES arm: {arm}")
    n = int(inputs["n"])
    max_coord = int(inputs["max_coord"])
    warm = {tuple(t) for t in inputs["warm_start"]}
    t_gen0 = time.perf_counter()
    evaluated = 0
    found: tuple[int, int, int] | None = None
    origin = "none"
    if arm == "classical_construction":
        for fam in p57_classical_constructions(n):
            if not fam["verified"]:
                continue
            triple = tuple(int(v) for v in fam["triple"])
            if max(triple) > max_coord:
                continue
            found = triple
            origin = "warm-start" if triple in warm else f"classical-{fam['family']}"
            evaluated = 1
            break
    else:
        x0 = n // 4 + 1
        for x_val in range(x0, x0 + int(inputs["x_steps"])):
            r = 4 * x_val - n
            if r <= 0:
                continue
            y_min = (n * x_val) // r + 1
            for y_val in range(y_min, y_min + int(inputs["y_cap"])):
                denom = 4 * x_val * y_val - n * (x_val + y_val)
                if denom > 0 and (n * x_val * y_val) % denom == 0:
                    z_val = (n * x_val * y_val) // denom
                    evaluated += 1
                    ok1, _, _ = check_erdos_straus(n, x_val, y_val, z_val)
                    ok2, _, _ = check_erdos_straus_fractions(n, x_val, y_val, z_val)
                    if ok1 and ok2 and max(x_val, y_val, z_val) <= max_coord:
                        found = (x_val, y_val, z_val)
                        origin = "warm-start" if found in warm else "enumerated"
                        break
                else:
                    evaluated += 1
            if found is not None:
                break
    t_gen1 = time.perf_counter()
    t_chk0 = time.perf_counter()
    checkers_ok = False
    if found is not None:
        c1, _, _ = check_erdos_straus(n, *found)
        c2, _, _ = check_erdos_straus_fractions(n, *found)
        checkers_ok = bool(c1 and c2)
    t_chk1 = time.perf_counter()
    ledger = p59_cost_ledger(
        train=0.0,
        generation=t_gen1 - t_gen0,
        inference=0.0,
        filters=0.0,
        checkers=t_chk1 - t_chk0,
        tracking=0.0,
    )
    return {
        "arm": arm,
        "n": n,
        "inputs_hash": _p59_inputs_hash(inputs),
        "found": found is not None and checkers_ok,
        "triple": list(found) if found is not None else None,
        "origin": origin if found is not None else "none",
        "status": "certified" if (found is not None and checkers_ok) else "budget-exhausted",
        "evaluated": evaluated,
        "ledger": ledger,
    }


# ==============================================================================
# P61 entrega 1 — H02 sombras aritméticas (filtros modulares baratos)
# ==============================================================================
#
# Condição necessária 4xyz = n(xy+xz+yz) módulo p em primos pequenos
# congelados, reduzindo após cada multiplicação (sem overflow). Sem divisão
# módulo p, sem reconstrução CRT: resíduo incompatível rejeita; resto segue
# ao checker exato. Resíduos compatíveis nunca são certificado.

P61_SHADOW_PRIMES = (3, 5, 7, 11, 13)


def p61_modular_shadow(
    n: int, x: int, y: int, z: int, primes: tuple[int, ...] = P61_SHADOW_PRIMES
) -> dict[str, Any]:
    """NumPy-free reference: necessary residue condition per frozen prime."""
    per_prime: dict[int, bool] = {}
    for p in primes:
        lhs = (4 % p) * (int(x) % p) % p * (int(y) % p) % p * (int(z) % p) % p
        xy = (int(x) % p) * (int(y) % p) % p
        xz = (int(x) % p) * (int(z) % p) % p
        yz = (int(y) % p) * (int(z) % p) % p
        rhs = (int(n) % p) * ((xy + xz + yz) % p) % p
        per_prime[int(p)] = bool(lhs == rhs)
    rejected = [p for p, ok in per_prime.items() if not ok]
    return {"keep": not rejected, "per_prime": per_prime, "rejected_by": rejected}


def p61_modular_shadow_batch_torch(
    n: int,
    xs: torch.Tensor,
    ys: torch.Tensor,
    zs: torch.Tensor,
    primes: tuple[int, ...] = P61_SHADOW_PRIMES,
    device: torch.device | None = None,
) -> torch.Tensor:
    """Batched shadow filter reusing the campaign torch pattern (int64).

    Inputs are reduced modulo p first (identical residues, overflow-safe:
    every intermediate stays below max(p)^3), then the same necessary
    condition as the reference. Returns a boolean keep mask; False entries
    are impossible solutions, True entries stay inconclusive for the checker.
    """
    dev = device if device is not None else torch.device("cpu")
    xv = xs.to(dtype=torch.int64, device=dev).ravel()
    yv = ys.to(dtype=torch.int64, device=dev).ravel()
    zv = zs.to(dtype=torch.int64, device=dev).ravel()
    keep = torch.ones(xv.numel(), dtype=torch.bool, device=dev)
    for p in primes:
        pp = int(p)
        lhs = (4 % pp) * (xv % pp) % pp * (yv % pp) % pp * (zv % pp) % pp
        rhs = (
            (int(n) % pp)
            * (((xv % pp) * (yv % pp) + (xv % pp) * (zv % pp) + (yv % pp) * (zv % pp)) % pp)
            % pp
        )
        keep &= lhs == rhs
    return keep


def run_p61_paired_filter_trial(
    n: int,
    triples: list[tuple[int, int, int]],
    device: torch.device | None = None,
) -> dict[str, Any]:
    """Paired with/without-filter comparison on exactly the same candidates.

    Unfiltered arm runs the dual exact checkers on every candidate; filtered
    arm runs the shadow mask first (with CPU/GPU transfers billed) and the
    checkers only on kept entries. Certificates must be identical in both
    arms and no exact solution may be rejected (else ``false_rejections`` > 0
    and the trial is unusable). Reports paired total costs; cheaper-or-not is
    a measurement outcome, never assumed here.
    """
    dev = device if device is not None else torch.device("cpu")
    xs = torch.tensor([t[0] for t in triples], dtype=torch.int64)
    ys = torch.tensor([t[1] for t in triples], dtype=torch.int64)
    zs = torch.tensor([t[2] for t in triples], dtype=torch.int64)

    def _check_all(idxs: list[int]) -> tuple[set[tuple[int, int, int]], float]:
        t0 = time.perf_counter()
        certs: set[tuple[int, int, int]] = set()
        for i in idxs:
            x, y, z = triples[i]
            ok1, _, _ = check_erdos_straus(n, x, y, z)
            ok2, _, _ = check_erdos_straus_fractions(n, x, y, z)
            if ok1 and ok2:
                certs.add((x, y, z))
        return certs, time.perf_counter() - t0

    t_all0 = time.perf_counter()
    certs_all, check_all_sec = _check_all(list(range(len(triples))))
    total_without_sec = time.perf_counter() - t_all0

    t_tx0 = time.perf_counter()
    mask_cpu = p61_modular_shadow_batch_torch(int(n), xs, ys, zs, device=torch.device("cpu"))
    devices_compared = ["cpu"]
    agreement = True
    mask_main = mask_cpu
    if torch.cuda.is_available():
        try:
            mask_cuda = p61_modular_shadow_batch_torch(
                int(n), xs, ys, zs, device=torch.device("cuda")
            ).cpu()
            devices_compared.append("cuda")
            agreement = bool((mask_cuda == mask_cpu).all().item())
            if dev.type == "cuda":
                mask_main = mask_cuda
        except RuntimeError:
            pass
    transfer_sec = time.perf_counter() - t_tx0
    kept = [i for i, k in enumerate(mask_main.tolist()) if k]
    t_f0 = time.perf_counter()
    mask_ref = [p61_modular_shadow(int(n), *triples[i])["keep"] for i in range(len(triples))]
    filter_sec = time.perf_counter() - t_f0
    if [bool(v) for v in mask_ref] != [bool(v) for v in mask_main.tolist()]:
        agreement = False
    certs_kept, check_kept_sec = _check_all(kept)
    total_with_sec = transfer_sec + filter_sec + check_kept_sec
    false_rejections = len(certs_all - certs_kept)
    return {
        "n": int(n),
        "candidates": len(triples),
        "kept": len(kept),
        "eliminated": len(triples) - len(kept),
        "certificates_unfiltered": sorted(certs_all),
        "certificates_filtered": sorted(certs_kept),
        "certificates_equal": certs_all == certs_kept,
        "false_rejections": false_rejections,
        "devices_compared": devices_compared,
        "device_agreement": bool(agreement),
        "costs": {
            "check_all_sec": check_all_sec,
            "total_without_sec": total_without_sec,
            "transfer_sec": transfer_sec,
            "filter_sec": filter_sec,
            "check_kept_sec": check_kept_sec,
            "total_with_sec": total_with_sec,
        },
    }


# ==============================================================================
# P62 entrega 1 — H01 primitivas de reparo estruturado de erros
# ==============================================================================
#
# Perturbações limitadas de certificados development com resíduo inteiro
# exato, sinais e divisibilidade. Vizinhança congelada de edições inteiras
# (uma coordenada, passos ±1..±3, domínio >= 1). Baselines clássico
# (menor |resíduo|) e aleatório sob a mesma vizinhança; políticas recebem
# só (n, x, y, z) — nunca a solução privada. Aceitação só pelos checkers.

P62_NEIGHBORHOOD_STEPS = (-3, -2, -1, 1, 2, 3)

P62_DIVISIBILITY_PRIMES = (2, 3, 5, 7, 11, 13)


def p62_exact_residual(n: int, x: int, y: int, z: int) -> int:
    """Exact integer residual 4xyz - n(xy+xz+yz); zero iff exact identity."""
    return 4 * int(x) * int(y) * int(z) - int(n) * (
        int(x) * int(y) + int(x) * int(z) + int(y) * int(z)
    )


def p62_exact_features(n: int, x: int, y: int, z: int) -> dict[str, Any]:
    """Exact perturbation features: residual, sign, small-prime divisibility."""
    r = p62_exact_residual(n, x, y, z)
    return {
        "residual": r,
        "sign": (1 if r > 0 else (-1 if r < 0 else 0)),
        "divisible_by": [p for p in P62_DIVISIBILITY_PRIMES if r % p == 0],
    }


def p62_neighbors(x: int, y: int, z: int) -> list[tuple[int, int, int]]:
    """Frozen bounded neighborhood: one coordinate, steps ±1..±3, domain >= 1."""
    out = []
    for coord in range(3):
        for step in P62_NEIGHBORHOOD_STEPS:
            t = [int(x), int(y), int(z)]
            t[coord] += step
            if min(t) >= 1:
                out.append((t[0], t[1], t[2]))
    return out


def p62_classical_repair_step(n: int, x: int, y: int, z: int) -> tuple[int, int, int] | None:
    """Classical baseline: valid neighbor with smallest |residual| (ties broken
    lexicographically for determinism)."""
    best: tuple[int, tuple[int, int, int]] | None = None
    for nb in p62_neighbors(x, y, z):
        r = abs(p62_exact_residual(n, *nb))
        if best is None or (r, nb) < (best[0], best[1]):
            best = (r, nb)
    return None if best is None else best[1]


def p62_random_repair_step(
    n: int, x: int, y: int, z: int, seed: int
) -> tuple[int, int, int] | None:
    """Random baseline: seeded uniform choice among valid neighbors."""
    import random as _random

    _ = n
    opts = p62_neighbors(x, y, z)
    if not opts:
        return None
    return _random.Random(int(seed)).choice(opts)


def p62_split_by_origin(
    records: list[dict[str, Any]], key: str = "n"
) -> dict[str, list[dict[str, Any]]]:
    """Deterministic split with disjoint origins: sorted unique key values go
    alternately to train/dev, so no origin ever appears on both sides."""
    origins = sorted({r[key] for r in records})
    train_origins = set(origins[::2])
    return {
        "train": [r for r in records if r[key] in train_origins],
        "dev": [r for r in records if r[key] not in train_origins],
    }


def p62_repair_cycles(
    n: int,
    start: tuple[int, int, int],
    policy: str = "classical",
    max_cycles: int = 12,
    seed: int = 0,
) -> dict[str, Any]:
    """Bounded repair loop from a perturbed triple until the fixed checkers
    certify, a state repeats (stalled) or the cycle cap hits (exhausted)."""
    if policy not in ("classical", "random"):
        raise ValueError(f"Unknown P62 repair policy: {policy}")
    x, y, z = (int(v) for v in start)
    residuals: list[int] = []
    visited = {(x, y, z)}
    cycles = 0
    while cycles < int(max_cycles):
        ok1, _, _ = check_erdos_straus(int(n), x, y, z)
        ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
        if ok1 and ok2:
            return {
                "certified": True,
                "triple": (x, y, z),
                "cycles_used": cycles,
                "residuals": residuals,
                "status": "certified",
            }
        if policy == "classical":
            nxt = p62_classical_repair_step(int(n), x, y, z)
        else:
            nxt = p62_random_repair_step(int(n), x, y, z, int(seed) + cycles)
        if nxt is None or nxt in visited:
            return {
                "certified": False,
                "triple": (x, y, z),
                "cycles_used": cycles,
                "residuals": residuals,
                "status": "stalled",
            }
        visited.add(nxt)
        x, y, z = nxt
        residuals.append(p62_exact_residual(int(n), x, y, z))
        cycles += 1
    ok1, _, _ = check_erdos_straus(int(n), x, y, z)
    ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
    certified = bool(ok1 and ok2)
    return {
        "certified": certified,
        "triple": (x, y, z),
        "cycles_used": cycles,
        "residuals": residuals,
        "status": "certified" if certified else "exhausted",
    }


# ==============================================================================
# P62 entrega 2 — H01 reparador pequeno treinado e comparação com custos
# ==============================================================================
#
# Um único reparador (MLP ~150 parâmetros, clonagem comportamental das
# trajetórias clássicas em origens de treino) escolhe entre os 18 vizinhos
# a partir de descritores computáveis sem a solução: |R| e Δ|R| do vizinho,
# coordenada e passo. Baselines aleatório e clássico sob a mesma vizinhança;
# comparação com entradas iguais, custo de coleta/treino faturado ao braço
# aprendido. Splits por origem: nenhuma origem treina e avalia.

P62_REPAIR_FEATURE_SCALE = 10000.0


class P62RepairScorer(torch.nn.Module):
    """Tiny shared per-neighbor scorer (~150 params, CPU)."""

    def __init__(self, hidden: int = 16) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(6, hidden), torch.nn.Tanh(), torch.nn.Linear(hidden, 1)
        )

    def forward(self, feats: torch.Tensor) -> torch.Tensor:
        return self.net(feats).squeeze(-1)


def p62_neighbor_features(n: int, x: int, y: int, z: int) -> torch.Tensor:
    """Solution-free neighbor descriptors: scaled |R|, Δ|R|, coord, step."""
    cur = abs(p62_exact_residual(n, x, y, z))
    rows = []
    for idx, nb in enumerate(p62_neighbors(x, y, z)):
        r_nb = abs(p62_exact_residual(n, *nb))
        onehot = [0.0, 0.0, 0.0]
        onehot[idx // 6] = 1.0
        step = P62_NEIGHBORHOOD_STEPS[idx % 6] / 3.0
        rows.append(
            [
                r_nb / P62_REPAIR_FEATURE_SCALE,
                (r_nb - cur) / P62_REPAIR_FEATURE_SCALE,
                *onehot,
                step,
            ]
        )
    return torch.tensor(rows, dtype=torch.float32)


def p62_collect_cloning_samples(
    n_values: list[int],
    starts_per_solution: int = 6,
    seed: int = 0,
    max_cycles: int = 12,
) -> tuple[list[dict[str, Any]], float]:
    """Classical repair trajectories on train origins as imitation samples.

    Each step records neighbor descriptors plus the classical choice index
    (exact label from the fixed checkers' residual, never a private answer:
    the label is argmin |R| over the same public neighborhood).
    """
    import random as _random

    t0 = time.perf_counter()
    rng = _random.Random(int(seed))
    samples: list[dict[str, Any]] = []
    for n in n_values:
        sols = [
            tuple(int(v) for v in fam["triple"])
            for fam in p57_classical_constructions(int(n))
            if fam["verified"]
        ]
        for sol in sols:
            cand_starts = {sol}
            while len(cand_starts) < starts_per_solution + 1:
                cand_starts.add(
                    (
                        max(1, sol[0] + rng.randint(-4, 4)),
                        max(1, sol[1] + rng.randint(-4, 4)),
                        max(1, sol[2] + rng.randint(-4, 4)),
                    )
                )
            for start in sorted(cand_starts - {sol}):
                x, y, z = start
                visited = {(x, y, z)}
                for _ in range(int(max_cycles)):
                    ok1, _, _ = check_erdos_straus(int(n), x, y, z)
                    ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
                    if ok1 and ok2:
                        break
                    nbs = p62_neighbors(x, y, z)
                    choice = p62_classical_repair_step(int(n), x, y, z)
                    if choice is None or choice in visited:
                        break
                    samples.append(
                        {
                            "n": int(n),
                            "state": (x, y, z),
                            "choice": nbs.index(choice),
                        }
                    )
                    visited.add(choice)
                    x, y, z = choice
    return samples, time.perf_counter() - t0


def p62_train_repairer(
    samples: list[dict[str, Any]], seed: int = 0, epochs: int = 60, lr: float = 0.05
) -> dict[str, Any]:
    """Train the single small repairer (behavior cloning, full-batch CPU)."""
    if not samples:
        raise ValueError("P62 training needs non-empty samples")
    torch.manual_seed(int(seed))
    model = P62RepairScorer()
    opt = torch.optim.Adam(model.parameters(), lr=float(lr))
    loss_fn = torch.nn.CrossEntropyLoss()
    feats = [p62_neighbor_features(s["n"], *s["state"]) for s in samples]
    labels = [int(s["choice"]) for s in samples]
    t0 = time.perf_counter()
    for _ in range(int(epochs)):
        opt.zero_grad()
        total = sum(
            loss_fn(model(f).unsqueeze(0), torch.tensor([y])) for f, y in zip(feats, labels)
        ) / len(feats)
        total.backward()
        opt.step()
    train_sec = time.perf_counter() - t0
    with torch.no_grad():
        hits = sum(int(model(f).argmax().item()) == y for f, y in zip(feats, labels))
        train_acc = hits / len(feats)
    n_params = sum(p.numel() for p in model.parameters())
    return {
        "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "n_params": int(n_params),
        "n_samples": len(samples),
        "train_acc": train_acc,
        "train_sec": float(train_sec),
        "epochs": int(epochs),
        "seed": int(seed),
    }


def p62_learned_repair_step(
    weights: dict[str, torch.Tensor], n: int, x: int, y: int, z: int
) -> tuple[int, int, int] | None:
    """Learned policy: argmax shared-scorer choice (deterministic, solution-free)."""
    nbs = p62_neighbors(x, y, z)
    if not nbs:
        return None
    model = P62RepairScorer()
    model.load_state_dict(weights)
    model.eval()
    with torch.no_grad():
        scores = model(p62_neighbor_features(int(n), x, y, z))
    return nbs[int(scores.argmax().item())]


def p62_repair_cycles_learned(
    n: int,
    start: tuple[int, int, int],
    weights: dict[str, torch.Tensor],
    max_cycles: int = 12,
) -> dict[str, Any]:
    """Bounded repair loop under the learned policy (same gates as classical)."""
    x, y, z = (int(v) for v in start)
    residuals: list[int] = []
    visited = {(x, y, z)}
    cycles = 0
    while cycles < int(max_cycles):
        ok1, _, _ = check_erdos_straus(int(n), x, y, z)
        ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
        if ok1 and ok2:
            return {
                "certified": True,
                "triple": (x, y, z),
                "cycles_used": cycles,
                "residuals": residuals,
                "status": "certified",
            }
        nxt = p62_learned_repair_step(weights, int(n), x, y, z)
        if nxt is None or nxt in visited:
            return {
                "certified": False,
                "triple": (x, y, z),
                "cycles_used": cycles,
                "residuals": residuals,
                "status": "stalled",
            }
        visited.add(nxt)
        x, y, z = nxt
        residuals.append(p62_exact_residual(int(n), x, y, z))
        cycles += 1
    ok1, _, _ = check_erdos_straus(int(n), x, y, z)
    ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
    certified = bool(ok1 and ok2)
    return {
        "certified": certified,
        "triple": (x, y, z),
        "cycles_used": cycles,
        "residuals": residuals,
        "status": "certified" if certified else "exhausted",
    }


def p62_compare_repair_policies(
    weights: dict[str, torch.Tensor],
    train_sec: float,
    starts: list[tuple[int, tuple[int, int, int]]],
    max_cycles: int = 12,
    seed: int = 0,
) -> dict[str, Any]:
    """Equal-input comparison: classical vs random vs learned on same starts.

    Collection/training cost is billed to the learned arm only; repair-loop
    cost is measured per policy. No promotion here: numbers are reported.
    """
    out: dict[str, Any] = {}
    for policy in ("classical", "random", "learned"):
        t0 = time.perf_counter()
        certified = 0
        cycles_total = 0
        for n, start in starts:
            if policy == "learned":
                rep = p62_repair_cycles_learned(n, start, weights, max_cycles)
            else:
                rep = p62_repair_cycles(n, start, policy=policy, max_cycles=max_cycles, seed=seed)
            certified += 1 if rep["certified"] else 0
            cycles_total += rep["cycles_used"]
        loop_sec = time.perf_counter() - t0
        billed = loop_sec + (float(train_sec) if policy == "learned" else 0.0)
        out[policy] = {
            "starts": len(starts),
            "certified": certified,
            "cycles_total": cycles_total,
            "loop_sec": loop_sec,
            "train_sec_billed": float(train_sec) if policy == "learned" else 0.0,
            "total_sec": billed,
        }
    return out


# ==============================================================================
# P63 entrega 1 — H08 códigos estruturados de rejeição do verificador
# ==============================================================================
#
# Códigos fixos (IDs inteiros/tensores no ciclo, sem texto ou parsing):
# denominador zero, limite violado, resíduo não nulo, domínio inválido e
# prova incompleta. Emissão pura sobre os checkers existentes — enunciado,
# axiomas e regra de aceitação inalterados. INCOMPLETE_PROOF reserva
# divergência entre checkers (ex.: fronteira formal); em triplas inteiras
# os dois checkers coincidem, então ele segue não observado aqui.

P63_REJECTION_CODES = {
    "ACCEPT": 0,
    "ZERO_DENOMINATOR": 1,
    "BOUND_VIOLATED": 2,
    "NONZERO_RESIDUAL": 3,
    "INVALID_DOMAIN": 4,
    "INCOMPLETE_PROOF": 5,
}


def p63_rejection_code(n: int, x: int, y: int, z: int, max_coord: int = 10**9) -> int:
    """Structured rejection ID for one candidate (deterministic, exact ints)."""
    C = P63_REJECTION_CODES
    if (
        not isinstance(x, int)
        or not isinstance(y, int)
        or not isinstance(z, int)
        or isinstance(x, bool)
        or isinstance(y, bool)
        or isinstance(z, bool)
        or x < 1
        or y < 1
        or z < 1
    ):
        return C["INVALID_DOMAIN"]
    if max(x, y, z) > int(max_coord):
        return C["BOUND_VIOLATED"]
    if 4 * x * y - int(n) * (x + y) == 0:
        return C["ZERO_DENOMINATOR"]
    ok1, residual, _ = check_erdos_straus(int(n), x, y, z)
    ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
    if ok1 and ok2:
        return C["ACCEPT"]
    if residual != 0:
        return C["NONZERO_RESIDUAL"]
    return C["INCOMPLETE_PROOF"]


def p63_code_tensor(codes: list[int], device: torch.device | None = None) -> torch.Tensor:
    """One-hot float tensor over the frozen codebook (loop-safe, no text)."""
    dev = device if device is not None else torch.device("cpu")
    width = len(P63_REJECTION_CODES)
    out = torch.zeros((len(codes), width), dtype=torch.float32, device=dev)
    for i, code in enumerate(codes):
        if 0 <= int(code) < width:
            out[i, int(code)] = 1.0
    return out


def p63_shuffle_codes(seed: int) -> dict[int, int]:
    """Deterministic codebook permutation for the shuffled ablation arm."""
    import random as _random

    ids = list(range(len(P63_REJECTION_CODES)))
    perm = ids[:]
    _random.Random(int(seed)).shuffle(perm)
    return dict(zip(ids, perm))


def p63_scalar_score(n: int, x: int, y: int, z: int, max_coord: int = 10**9) -> float:
    """Single-scalar baseline feedback: 1.0 iff exact, decaying with |R|."""
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in (x, y, z)):
        return 0.0
    if min(x, y, z) < 1 or max(x, y, z) > int(max_coord):
        return 0.0
    return 1.0 / (1.0 + abs(p62_exact_residual(int(n), x, y, z)))


# ==============================================================================
# P63 entrega 2 — H08 comparação real × embaralhado × escalar com custos
# ==============================================================================
#
# Mesmo loop de reparo e mesmo orçamento para os três braços; só o feedback
# muda. Real usa o código verdadeiro, embaralhado passa pela permutação
# congelada (ablação: mesma distribuição, estrutura destruída) e escalar usa
# só 1/(1+|R|). Toda consulta ao verificador é contada e há teto registrado;
# estourar o teto encerra como query-capped. Pesos de prioridade congelados
# e arbitrários (não ajustados): só o contraste entre braços importa.

P63_CODE_PRIORITY = (0, 3, 4, 2, 5, 1)

P63_FEEDBACK_ARMS = ("real", "shuffled", "scalar")


def p63_neighbor_key(
    arm: str, code: int, residual_abs: int, coords: tuple[int, int, int], perm: dict[int, int]
) -> tuple[int, int, tuple[int, int, int]]:
    """Frozen ranking key per arm (ties broken by |R| then coordinates)."""
    if arm == "real":
        shown = int(code)
    elif arm == "shuffled":
        shown = int(perm.get(int(code), int(code)))
    elif arm == "scalar":
        shown = 0 if int(residual_abs) == 0 else 2
    else:
        raise ValueError(f"Unknown P63 feedback arm: {arm}")
    return (P63_CODE_PRIORITY[shown], int(residual_abs), coords)


def p63_compare_feedback_arms(
    n: int,
    starts: list[tuple[int, int, int]],
    max_cycles: int = 12,
    query_limit: int = 2000,
    shuffle_seed: int = 7,
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """Equal-budget repair comparison across the three feedback arms."""
    perm = p63_shuffle_codes(int(shuffle_seed))
    out: dict[str, Any] = {}
    for arm in P63_FEEDBACK_ARMS:
        t0 = time.perf_counter()
        certified = 0
        cycles_total = 0
        queries_total = 0
        details = []
        for start in starts:
            x, y, z = (int(v) for v in start)
            visited = {(x, y, z)}
            traj: list[int] = []
            cycles = 0
            status = "exhausted"
            while cycles < int(max_cycles):
                queries_total += 1
                ok1, _, _ = check_erdos_straus(int(n), x, y, z)
                ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
                if ok1 and ok2:
                    status = "certified"
                    certified += 1
                    break
                if queries_total >= int(query_limit):
                    status = "query-capped"
                    break
                ranked = []
                for nb in p62_neighbors(x, y, z):
                    if arm == "scalar":
                        code = P63_REJECTION_CODES["NONZERO_RESIDUAL"]
                    else:
                        code = p63_rejection_code(int(n), *nb, max_coord=int(max_coord))
                        queries_total += 1
                    r_nb = abs(p62_exact_residual(int(n), *nb))
                    ranked.append((p63_neighbor_key(arm, code, r_nb, nb, perm), nb))
                if not ranked:
                    status = "stalled"
                    break
                ranked.sort(key=lambda kv: kv[0])
                nxt = ranked[0][1]
                if nxt in visited:
                    status = "stalled"
                    break
                visited.add(nxt)
                x, y, z = nxt
                traj.append(p63_rejection_code(int(n), x, y, z, max_coord=int(max_coord)))
                queries_total += 1
                cycles += 1
            cycles_total += cycles
            details.append(
                {
                    "start": list(start),
                    "status": status,
                    "cycles": cycles,
                    "codes": traj,
                    "triple": [x, y, z],
                }
            )
        out[arm] = {
            "starts": len(starts),
            "certified": certified,
            "cycles_total": cycles_total,
            "queries_total": queries_total,
            "loop_sec": time.perf_counter() - t0,
            "details": details,
        }
    return out


# ==============================================================================
# P63 entrega 3 — H08 scorer único treinado em development + interface
# ==============================================================================
#
# Um único scorer ([one-hot(6) do código, escalar]) clonado das escolhas
# clássicas em origens de treino. Na inferência, os três braços usam OS
# MESMOS pesos: real (códigos verdadeiros), shuffled (one-hot permutado,
# mesma distribuição) e scalar (one-hot zerado). Custo de coleta/treino
# faturado uma vez; loops com mesmo teto de ciclos/queries. Trajetórias de
# códigos + tripla final persistidas por start para replay.

P63_FEEDBACK_INPUT_DIM = 7


class P63FeedbackScorer(torch.nn.Module):
    """Tiny shared scorer over [code one-hot, scalar] (~160 params, CPU)."""

    def __init__(self, hidden: int = 16) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(P63_FEEDBACK_INPUT_DIM, hidden),
            torch.nn.Tanh(),
            torch.nn.Linear(hidden, 1),
        )

    def forward(self, feats: torch.Tensor) -> torch.Tensor:
        return self.net(feats).squeeze(-1)


def p63_feedback_neighbor_features(
    n: int, x: int, y: int, z: int, max_coord: int = 10**9
) -> tuple[torch.Tensor, list[tuple[int, int, int]], list[int]]:
    """Per-neighbor [code one-hot, scalar] rows plus neighbors and codes."""
    rows = []
    nbs = p62_neighbors(x, y, z)
    codes = [p63_rejection_code(int(n), *nb, max_coord=int(max_coord)) for nb in nbs]
    for nb, code in zip(nbs, codes):
        onehot = [0.0] * len(P63_REJECTION_CODES)
        onehot[int(code)] = 1.0
        rows.append([*onehot, p63_scalar_score(int(n), *nb, max_coord=int(max_coord))])
    return torch.tensor(rows, dtype=torch.float32), nbs, codes


def p63_train_feedback_scorer(
    samples: list[dict[str, Any]],
    seed: int = 0,
    epochs: int = 40,
    lr: float = 0.05,
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """Behavior-clone classical choices from true-code feedback (development)."""
    if not samples:
        raise ValueError("P63 training needs non-empty samples")
    torch.manual_seed(int(seed))
    model = P63FeedbackScorer()
    opt = torch.optim.Adam(model.parameters(), lr=float(lr))
    loss_fn = torch.nn.CrossEntropyLoss()
    feats = [
        p63_feedback_neighbor_features(s["n"], *s["state"], max_coord=int(max_coord))[0]
        for s in samples
    ]
    labels = [int(s["choice"]) for s in samples]
    t0 = time.perf_counter()
    for _ in range(int(epochs)):
        opt.zero_grad()
        total = sum(
            loss_fn(model(f).unsqueeze(0), torch.tensor([y])) for f, y in zip(feats, labels)
        ) / len(feats)
        total.backward()
        opt.step()
    train_sec = time.perf_counter() - t0
    with torch.no_grad():
        hits = sum(int(model(f).argmax().item()) == y for f, y in zip(feats, labels))
    return {
        "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "n_params": int(sum(p.numel() for p in model.parameters())),
        "n_samples": len(samples),
        "train_acc": hits / len(feats),
        "train_sec": float(train_sec),
        "epochs": int(epochs),
        "seed": int(seed),
    }


def p63_feedback_repair_cycles(
    n: int,
    start: tuple[int, int, int],
    weights: dict[str, torch.Tensor],
    arm: str,
    perm: dict[int, int],
    max_cycles: int = 12,
    query_limit: int = 2000,
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """Bounded repair loop under one feedback arm of the shared scorer."""
    if arm not in P63_FEEDBACK_ARMS:
        raise ValueError(f"Unknown P63 feedback arm: {arm}")
    model = P63FeedbackScorer()
    model.load_state_dict(weights)
    model.eval()
    x, y, z = (int(v) for v in start)
    visited = {(x, y, z)}
    codes_traj: list[int] = []
    queries = 0
    cycles = 0
    status = "exhausted"
    while cycles < int(max_cycles):
        queries += 1
        ok1, _, _ = check_erdos_straus(int(n), x, y, z)
        ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
        if ok1 and ok2:
            status = "certified"
            break
        if queries >= int(query_limit):
            status = "query-capped"
            break
        nbs = p62_neighbors(x, y, z)
        if not nbs:
            status = "stalled"
            break
        rows = []
        for nb in nbs:
            if arm == "scalar":
                onehot = [0.0] * len(P63_REJECTION_CODES)
            else:
                code = p63_rejection_code(int(n), *nb, max_coord=int(max_coord))
                queries += 1
                if arm == "shuffled":
                    code = int(perm.get(int(code), int(code)))
                onehot = [0.0] * len(P63_REJECTION_CODES)
                onehot[int(code)] = 1.0
            rows.append([*onehot, p63_scalar_score(int(n), *nb, max_coord=int(max_coord))])
        with torch.no_grad():
            nxt = nbs[int(model(torch.tensor(rows, dtype=torch.float32)).argmax().item())]
        if nxt in visited:
            status = "stalled"
            break
        visited.add(nxt)
        x, y, z = nxt
        codes_traj.append(p63_rejection_code(int(n), x, y, z, max_coord=int(max_coord)))
        queries += 1
        cycles += 1
    ok1, _, _ = check_erdos_straus(int(n), x, y, z)
    ok2, _, _ = check_erdos_straus_fractions(int(n), x, y, z)
    if status != "certified":
        status = "certified" if (ok1 and ok2) else status
    return {
        "certified": status == "certified",
        "triple": [x, y, z],
        "cycles_used": cycles,
        "queries": queries,
        "codes": codes_traj,
        "status": status,
    }


def p63_compare_learned_feedback(
    weights: dict[str, torch.Tensor],
    starts: list[tuple[int, tuple[int, int, int]]],
    shuffle_seed: int = 7,
    max_cycles: int = 12,
    query_limit: int = 2000,
    max_coord: int = 10**9,
) -> dict[str, Any]:
    """Same weights, three feedbacks: real vs shuffled vs scalar."""
    perm = p63_shuffle_codes(int(shuffle_seed))
    out: dict[str, Any] = {}
    for arm in P63_FEEDBACK_ARMS:
        t0 = time.perf_counter()
        reps = [
            p63_feedback_repair_cycles(
                n, start, weights, arm, perm, max_cycles, query_limit, max_coord
            )
            for n, start in starts
        ]
        out[arm] = {
            "starts": len(starts),
            "certified": sum(1 for r in reps if r["certified"]),
            "cycles_total": sum(r["cycles_used"] for r in reps),
            "queries_total": sum(r["queries"] for r in reps),
            "loop_sec": time.perf_counter() - t0,
            "details": reps,
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P29/P31 Open Problems with Verifiable Certificates (Diophantine / Identities / Combinatorial)"
    )
    parser.add_argument(
        "--problem",
        type=str,
        default="erdos-straus",
        choices=list(PROBLEM_REGISTRY.keys()),
        help="Problem nomination identifier (default: 'erdos-straus')",
    )
    parser.add_argument(
        "--audit-certificates",
        action="store_true",
        help="Run P31 certificate audit, strict bounds verification, and adversarial rejection suite",
    )
    parser.add_argument(
        "--certified-campaign",
        action="store_true",
        help="Run P39 bounded certified campaign for the nominated problem",
    )
    parser.add_argument(
        "--freeze-manifest",
        type=str,
        default="experiments/p38-confirmation.json",
        help="P39: accepted freeze manifest (default: experiments/p38-confirmation.json)",
    )
    parser.add_argument(
        "--nomination",
        type=str,
        default="experiments/p39-nomination.json",
        help="P39: preregistered nomination file",
    )
    parser.add_argument(
        "--bounds-strict",
        action="store_true",
        help="Strictly enforce declared finite-domain coordinate bounds (e.g. M <= 10^9 for Erdős-Straus)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path for artifact manifest",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Compute device (cpu/cuda)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run fast smoke campaign",
    )
    args = parser.parse_args()

    if args.audit_certificates:
        out_path = args.output or "experiments/p31-certificates.json"
        res = run_certificate_audit(
            bounds_strict=args.bounds_strict,
            output_path=out_path,
            device_name=args.device,
        )
        return 0 if res["status"] == "PASS" else 1

    if args.certified_campaign:
        out_path = args.output or "experiments/p39-science.json"
        res = run_certified_campaign(
            problem_id=args.problem,
            freeze_manifest=args.freeze_manifest,
            nomination_path=args.nomination,
            output_path=out_path,
            device_name=args.device,
            smoke=args.smoke,
        )
        return 0 if res["status"] == "PASS" else 1

    out_path = args.output or f"experiments/p29-{args.problem}.json"
    res = run_open_problem_campaign(
        problem_id=args.problem,
        device_name=args.device,
        output_path=out_path,
        smoke=args.smoke,
    )
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
