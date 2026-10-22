"""Frontier Target Catalogue v2 - Verifiers and Loaders.

Calibrated independent verifiers for covering designs, weak Schur numbers,
strong Schur numbers, and cap sets in F_3^n.

Standard library only (no external dependencies).
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ClaimedValue:
    """A claimed value from a primary or secondary source."""

    value: int
    source_id: str
    verified_object: bool


@dataclass(frozen=True)
class FrontierTarget:
    """An immutable record representing a frontier target in Catalogue v2."""

    target_id: str
    family: str
    params: Mapping[str, Any]
    objective: str
    role: str
    stratum: str
    best_known_value: int
    source_convention: str
    claimed_values: tuple[ClaimedValue, ...]
    lower_bound: int | float | None
    proven_optimal: bool
    last_improvement: str | None
    last_method: str | None
    certificate_status: str
    certificate_path: str | None
    verifier: str
    verifier_runtime_s: float


REQUIRED_TARGET_FIELDS = (
    "target_id",
    "family",
    "params",
    "objective",
    "role",
    "stratum",
    "best_known_value",
    "source_convention",
    "claimed_values",
    "lower_bound",
    "proven_optimal",
    "last_improvement",
    "last_method",
    "certificate_status",
    "certificate_path",
    "verifier",
    "verifier_runtime_s",
)

VALID_FAMILIES = {"covering_design", "weak_schur", "schur", "cap_set"}
VALID_OBJECTIVES = {"minimize", "maximize"}
VALID_ROLES = {"record", "calibration"}
VALID_STRATA = {
    "stale_construction",
    "active_frontier",
    "random_control",
    "named_open",
    "calibration",
}
VALID_CERT_STATUSES = {
    "verified_published_object",
    "not_obtained",
    "site_unreachable",
    "constructed_calibration",
}


def verify_covering_design(
    blocks: Any, v: Any, k: Any, t: Any
) -> tuple[bool, str]:
    """Verify that blocks form a valid C(v, k, t) covering design.

    Every t-subset of {1..v} must be contained in at least one block of size k.
    Uses colexicographical ranking (combinatorial number system) and bitset.
    """
    if not isinstance(v, int) or isinstance(v, bool):
        return False, "v must be an integer"
    if not isinstance(k, int) or isinstance(k, bool):
        return False, "k must be an integer"
    if not isinstance(t, int) or isinstance(t, bool):
        return False, "t must be an integer"

    if t < 1 or k < t or v < k:
        return False, f"invalid parameters: require 1 <= t ({t}) <= k ({k}) <= v ({v})"

    num_subsets = math.comb(v, t)
    if num_subsets > 10_000_000:
        return False, "too large"

    if not isinstance(blocks, (list, tuple)):
        return False, "blocks must be a list or tuple"
    if len(blocks) == 0:
        return False, "empty blocks collection"

    # Precompute binomial coefficients up to v for rank calculation
    binom = [[math.comb(n, r) for r in range(t + 1)] for n in range(v + 1)]

    arr = bytearray((num_subsets + 7) // 8)
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

        # Colexicographical rank for each t-subset
        for sub in itertools.combinations(sorted_b, t):
            r = 0
            for i, c in enumerate(sub):
                r += binom[c][i + 1]
            byte_idx = r >> 3
            bit_mask = 1 << (r & 7)
            if not (arr[byte_idx] & bit_mask):
                arr[byte_idx] |= bit_mask
                covered += 1

    if covered == num_subsets:
        return True, f"all {num_subsets} {t}-subsets covered"
    return False, f"only {covered}/{num_subsets} {t}-subsets covered"


def verify_weak_schur_partition(
    coloring: Any, k: Any
) -> tuple[bool, str]:
    """Verify that coloring is a valid weak sum-free k-partition of {1..N}.

    coloring[i-1] is the color of integer i.
    No monochromatic distinct triple x < y with x + y = z <= N is permitted.
    x + x = 2x is allowed (weak Schur rule).
    """
    if not isinstance(coloring, (list, tuple)):
        return False, "coloring must be a list or tuple"
    if len(coloring) == 0:
        return False, "empty coloring list"
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        return False, f"invalid number of colors k: {k}"

    n = len(coloring)
    color_sets: list[set[int]] = [set() for _ in range(k + 1)]

    for i, c in enumerate(coloring, start=1):
        if not isinstance(c, int) or isinstance(c, bool):
            return False, f"non-integer color at index {i}: {c}"
        if c < 1 or c > k:
            return False, f"color {c} at index {i} out of range 1..{k}"
        color_sets[c].add(i)

    for c in range(1, k + 1):
        s = color_sets[c]
        sorted_s = sorted(s)
        for idx_x, x in enumerate(sorted_s):
            for y in sorted_s[idx_x + 1:]:
                z = x + y
                if z in s:
                    return (
                        False,
                        f"weak Schur violation in color {c}: {x} + {y} = {z}",
                    )

    return (
        True,
        f"valid weak sum-free partition of 1..{n} into {k} classes",
    )


def verify_cap_set(points: Any, n: Any) -> tuple[bool, str]:
    """Verify that points form a valid cap set in F_3^n.

    All points must be distinct elements of {0, 1, 2}^n.
    No three distinct points may sum to 0 mod 3 (i.e. form an affine line).
    """
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
            return False, f"point {p_idx} dimension != {n} (got {len(pt)})"
        tup_coords = []
        for coord in pt:
            if not isinstance(coord, int) or isinstance(coord, bool):
                return False, f"non-integer coordinate in point {p_idx}: {coord}"
            if coord not in (0, 1, 2):
                return False, f"coordinate {coord} out of range {0, 1, 2}"
            tup_coords.append(coord)
        p_tup = tuple(tup_coords)
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

    return True, f"valid cap set of size {num_pts} in F3^{n}"


def load_frontier_catalogue(path: str | Path) -> tuple[FrontierTarget, ...]:
    """Load and strictly validate the Frontier Target Catalogue v2 JSON file.

    Returns an immutable tuple of FrontierTarget instances.
    Raises ValueError or FileNotFoundError if invalid.
    """
    resolved_path = Path(path).resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Catalogue file not found: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        raw_targets = data.get("targets")
        if raw_targets is None:
            raise ValueError("Catalogue JSON dict must contain 'targets' key")
    elif isinstance(data, list):
        raw_targets = data
    else:
        raise ValueError("Catalogue JSON root must be a list or dict")

    targets: list[FrontierTarget] = []
    seen_ids: set[str] = set()

    for idx, item in enumerate(raw_targets):
        if not isinstance(item, dict):
            raise ValueError(f"Target at index {idx} must be a dict")

        for req in REQUIRED_TARGET_FIELDS:
            if req not in item:
                raise ValueError(f"Target at index {idx} missing required field: {req}")

        tid = item["target_id"]
        if tid in seen_ids:
            raise ValueError(f"Duplicate target_id in catalogue: {tid}")
        seen_ids.add(tid)

        role = item["role"]
        if role not in VALID_ROLES:
            raise ValueError(f"Target {tid} has invalid role: {role}")

        family = item["family"]
        if family not in VALID_FAMILIES:
            raise ValueError(f"Target {tid} has invalid family: {family}")

        objective = item["objective"]
        if objective not in VALID_OBJECTIVES:
            raise ValueError(f"Target {tid} has invalid objective: {objective}")

        stratum = item["stratum"]
        if stratum not in VALID_STRATA:
            raise ValueError(f"Target {tid} has invalid stratum: {stratum}")

        proven_optimal = item["proven_optimal"]
        if not isinstance(proven_optimal, bool):
            raise ValueError(f"Target {tid} proven_optimal must be bool")

        if role == "record" and proven_optimal:
            raise ValueError(
                f"Target {tid} is a record target but has proven_optimal=True (forbidden)"
            )

        cert_status = item["certificate_status"]
        if cert_status not in VALID_CERT_STATUSES:
            raise ValueError(f"Target {tid} has invalid certificate_status: {cert_status}")

        raw_claims = item["claimed_values"]
        if not isinstance(raw_claims, list):
            raise ValueError(f"Target {tid} claimed_values must be a list")

        claimed_values: list[ClaimedValue] = []
        for c in raw_claims:
            if not isinstance(c, dict) or "value" not in c or "source_id" not in c:
                raise ValueError(f"Target {tid} has malformed claimed_value: {c}")
            claimed_values.append(
                ClaimedValue(
                    value=int(c["value"]),
                    source_id=str(c["source_id"]),
                    verified_object=bool(c.get("verified_object", False)),
                )
            )

        targets.append(
            FrontierTarget(
                target_id=tid,
                family=family,
                params=dict(item["params"]),
                objective=objective,
                role=role,
                stratum=stratum,
                best_known_value=int(item["best_known_value"]),
                source_convention=str(item["source_convention"]),
                claimed_values=tuple(claimed_values),
                lower_bound=item["lower_bound"],
                proven_optimal=proven_optimal,
                last_improvement=item["last_improvement"],
                last_method=item["last_method"],
                certificate_status=cert_status,
                certificate_path=item["certificate_path"],
                verifier=str(item["verifier"]),
                verifier_runtime_s=float(item["verifier_runtime_s"]),
            )
        )

    return tuple(targets)
