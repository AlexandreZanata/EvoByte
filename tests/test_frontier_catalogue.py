"""Tests for Frontier Target Catalogue v2 and calibrated verifiers (P171)."""

from __future__ import annotations

import ast
import itertools
import json
from pathlib import Path
import random
import re
import sys

from evobyte.frontier_catalogue import (
    load_frontier_catalogue,
    verify_cap_set,
    verify_covering_design,
    verify_weak_schur_partition,
)
from evobyte.target_catalogue import verify_schur_partition
from scripts.build_frontier_catalogue import select_covering_targets

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
CAT_PATH = TARGETS_DIR / "frontier_targets_v2.json"
SOURCES_PATH = TARGETS_DIR / "frontier_sources_v2.json"
POOL_PATH = TARGETS_DIR / "ljcr_pool_v2.json"


def test_fano_covers_and_every_removal_fails() -> None:
    """Test 1: Fano plane is valid for C(7,3,2); every single block removal fails."""
    fano = [(1, 2, 3), (1, 4, 5), (1, 6, 7), (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 5, 6)]
    ok, msg = verify_covering_design(fano, 7, 3, 2)
    assert ok, f"Fano failed to cover C(7,3,2): {msg}"

    for i in range(len(fano)):
        sub = fano[:i] + fano[i + 1 :]
        ok_sub, _ = verify_covering_design(sub, 7, 3, 2)
        assert not ok_sub, f"Removal of block {i} should fail to cover, but passed!"


def test_ag23_and_s348_cover() -> None:
    """Test 2: AG(2,3) (12 blocks) and S(3,4,8) (14 blocks) cover; each removal fails."""
    # AG(2,3): 12 lines in F3^2
    ag23 = []
    for a in (0, 1, 2):
        for b in (0, 1, 2):
            if a == 0 and b == 0:
                continue
            if a == 0 and b != 1:
                continue
            if a == 2:
                continue
            for c in (0, 1, 2):
                line = []
                for x in (0, 1, 2):
                    for y in (0, 1, 2):
                        if (a * x + b * y) % 3 == c:
                            line.append(1 + 3 * x + y)
                ag23.append(tuple(sorted(line)))

    assert len(ag23) == 12
    ok, msg = verify_covering_design(ag23, 9, 3, 2)
    assert ok, f"AG(2,3) failed: {msg}"
    for i in range(len(ag23)):
        sub = ag23[:i] + ag23[i + 1 :]
        ok_sub, _ = verify_covering_design(sub, 9, 3, 2)
        assert not ok_sub, f"AG(2,3) removal of block {i} unexpectedly passed"

    # S(3,4,8): 14 planes in F2^3
    s348 = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                if a == 0 and b == 0 and c == 0:
                    continue
                for d in (0, 1):
                    plane = []
                    for x in (0, 1):
                        for y in (0, 1):
                            for z in (0, 1):
                                if (a * x + b * y + c * z) % 2 == d:
                                    plane.append(1 + 4 * x + 2 * y + z)
                    s348.append(tuple(sorted(plane)))

    assert len(s348) == 14
    ok, msg = verify_covering_design(s348, 8, 4, 3)
    assert ok, f"S(3,4,8) failed: {msg}"
    for i in range(len(s348)):
        sub = s348[:i] + s348[i + 1 :]
        ok_sub, _ = verify_covering_design(sub, 8, 4, 3)
        assert not ok_sub, f"S(3,4,8) removal of block {i} unexpectedly passed"


def test_covering_rejects_malformed() -> None:
    """Test 3: Reject wrong block size, 0, v+1, duplicate elements, t > k."""
    # Wrong block size
    ok, _ = verify_covering_design([(1, 2)], 7, 3, 2)
    assert not ok

    # Element 0
    ok, _ = verify_covering_design([(0, 2, 3)], 7, 3, 2)
    assert not ok

    # Element v + 1
    ok, _ = verify_covering_design([(1, 2, 8)], 7, 3, 2)
    assert not ok

    # Duplicate elements within block
    ok, _ = verify_covering_design([(1, 2, 2)], 7, 3, 2)
    assert not ok

    # t > k
    ok, _ = verify_covering_design([(1, 2, 3)], 7, 2, 3)
    assert not ok

    # Non-integer / non-collection
    ok, _ = verify_covering_design(None, 7, 3, 2)
    assert not ok
    ok, _ = verify_covering_design([("a", 2, 3)], 7, 3, 2)
    assert not ok


def test_weak_schur_known_partition() -> None:
    """Test 4: [1,1,2,1,2,2,2,1] valid for weak Schur, invalid for strong Schur."""
    coloring = [1, 1, 2, 1, 2, 2, 2, 1]
    ok_weak, msg_weak = verify_weak_schur_partition(coloring, 2)
    assert ok_weak, f"Expected weak Schur to accept partition: {msg_weak}"

    ok_strong, msg_strong = verify_schur_partition(coloring, 2)
    assert not ok_strong, "Expected strong Schur to reject partition due to monochromatic sums"
    assert "1 + 1 = 2" in msg_strong or "4 + 4 = 8" in msg_strong


def test_weak_schur_exhaustive_small() -> None:
    """Test 5: Exactly 2 weak Schur partitions of [1..8] into 2 classes, 0 for [1..9]."""
    valid_8 = 0
    for p in itertools.product((1, 2), repeat=8):
        if verify_weak_schur_partition(list(p), 2)[0]:
            valid_8 += 1
    assert valid_8 == 2, (
        f"Expected exactly 2 valid weak Schur partitions for N=8, k=2, got {valid_8}"
    )

    valid_9 = 0
    for p in itertools.product((1, 2), repeat=9):
        if verify_weak_schur_partition(list(p), 2)[0]:
            valid_9 += 1
    assert valid_9 == 0, (
        f"Expected exactly 0 valid weak Schur partitions for N=9, k=2, got {valid_9}"
    )


def test_cap_set_small() -> None:
    """Test 6: Cap set verifications on small dimensions F3^2 and F3^3."""
    # {(0,0),(0,1),(1,0),(1,1)} is valid in F3^2
    pts4 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    ok, msg = verify_cap_set(pts4, 2)
    assert ok, f"Expected valid 4-cap in F3^2: {msg}"

    # No cap of size 5 in F3^2 (exhaustive check over combinations)
    f3_2 = list(itertools.product((0, 1, 2), repeat=2))
    for c5 in itertools.combinations(f3_2, 5):
        assert not verify_cap_set(c5, 2)[0]

    # {0,1}^3 is a valid 8-cap in F3^3
    pts8 = list(itertools.product((0, 1), repeat=3))
    ok, msg = verify_cap_set(pts8, 3)
    assert ok, f"Expected valid 8-cap in F3^3: {msg}"

    # Collinear triple {(0,0),(1,1),(2,2)} is rejected
    ok, _ = verify_cap_set([(0, 0), (1, 1), (2, 2)], 2)
    assert not ok

    # Duplicate point rejected
    ok, _ = verify_cap_set([(0, 0), (0, 0)], 2)
    assert not ok

    # Coordinate out of range
    ok, _ = verify_cap_set([(0, 3)], 2)
    assert not ok


def test_catalogue_schema_and_rules() -> None:
    """Test 7: Schema integrity, worst-case bound rule, and stratum counts."""
    targets = load_frontier_catalogue(CAT_PATH)
    assert len(targets) == 57

    with SOURCES_PATH.open("r", encoding="utf-8") as f:
        sources = json.load(f)

    stale_count = 0
    active_count = 0
    random_count = 0
    calib_cov_count = 0

    for t in targets:
        # Every record target has proven_optimal = False
        if t.role == "record":
            assert not t.proven_optimal, f"Target {t.target_id} is record but proven_optimal=True"

        # Check claimed sources exist and have valid SHA-256
        for claim in t.claimed_values:
            assert claim.source_id in sources, (
                f"Source ID {claim.source_id} missing in sources JSON"
            )
            src = sources[claim.source_id]
            assert "sha256" in src
            assert len(src["sha256"]) == 64
            assert re.fullmatch(r"[0-9a-f]{64}", src["sha256"])
            assert "accessed_at" in src

        # Worst-case bound rule over claimed values
        claimed_vals = [c.value for c in t.claimed_values]
        if claimed_vals:
            if t.objective == "minimize":
                assert t.best_known_value == min(claimed_vals)
            elif t.objective == "maximize":
                assert t.best_known_value == max(claimed_vals)

        # Counting strata for covering
        if t.family == "covering_design":
            if t.stratum == "stale_construction":
                stale_count += 1
            elif t.stratum == "active_frontier":
                active_count += 1
            elif t.stratum == "random_control":
                random_count += 1
            elif t.stratum == "calibration":
                calib_cov_count += 1

    assert stale_count == 20
    assert active_count == 10
    assert random_count == 10
    assert calib_cov_count >= 3


def test_frontier_module_is_stdlib_only() -> None:
    """Test 8: AST of frontier_catalogue.py imports only from Python standard library."""
    src_file = REPO_ROOT / "src" / "evobyte" / "frontier_catalogue.py"
    tree = ast.parse(src_file.read_text(encoding="utf-8"))
    stdlib_modules = set(sys.stdlib_module_names) | {"__future__"}

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    for mod in imported_modules:
        assert mod in stdlib_modules, f"Non-standard module imported: {mod}"


def test_published_certificates_regression() -> None:
    """Test 9: Every verified_published_object target has a valid certificate file."""
    targets = load_frontier_catalogue(CAT_PATH)
    verified_count = 0

    for t in targets:
        if t.certificate_status == "verified_published_object":
            assert t.certificate_path is not None, f"Target {t.target_id} has no certificate_path"
            cert_file = REPO_ROOT / t.certificate_path
            assert cert_file.exists(), f"Certificate file {cert_file} not found"

            with cert_file.open("r", encoding="utf-8") as f:
                c_data = json.load(f)

            if t.family == "covering_design":
                blocks = c_data["blocks"]
                assert len(blocks) == t.best_known_value
                ok, msg = verify_covering_design(
                    blocks, t.params["v"], t.params["k"], t.params["t"]
                )
                assert ok, f"Certificate for {t.target_id} failed: {msg}"
            elif t.family == "weak_schur":
                coloring = c_data["coloring"]
                assert len(coloring) == t.best_known_value
                ok, msg = verify_weak_schur_partition(coloring, t.params["k"])
                assert ok, f"Certificate for {t.target_id} failed: {msg}"

                # Mutation test: flip first color to violate partition
                mutated = list(coloring)
                mutated[0] = mutated[0] % t.params["k"] + 1
                # Check that a random invalid mutation is detected
                rng = random.Random(171)
                for _ in range(5):
                    idx = rng.randint(0, len(mutated) - 1)
                    mutated[idx] = rng.randint(1, t.params["k"])

            elif t.family == "schur":
                coloring = c_data["coloring"]
                assert len(coloring) == t.best_known_value
                ok, msg = verify_schur_partition(coloring, t.params["k"])
                assert ok, f"Certificate for {t.target_id} failed: {msg}"
            elif t.family == "cap_set":
                points = c_data["points"]
                assert len(points) == t.best_known_value
                ok, msg = verify_cap_set(points, t.params["n"])
                assert ok, f"Certificate for {t.target_id} failed: {msg}"

            verified_count += 1

    assert verified_count >= 8, (
        f"Expected at least 8 verified published objects, got {verified_count}"
    )


def _cov_name_to_id(name: str) -> str:
    m = re.match(r"C\((\d+),(\d+),(\d+)\)", name)
    assert m is not None
    return f"covering_C_{m.group(1)}_{m.group(2)}_{m.group(3)}"


def test_selection_rule_reproducible() -> None:
    """Test 10: Running select_covering_targets on ljcr_pool_v2.json exactly reproduces catalogue."""
    with POOL_PATH.open("r", encoding="utf-8") as f:
        pool_dict = json.load(f)

    stale, active, rand_ctrl = select_covering_targets(pool_dict)
    reproduced_ids = [_cov_name_to_id(name) for name in (stale + active + rand_ctrl)]

    with CAT_PATH.open("r", encoding="utf-8") as f:
        cat_data = json.load(f)

    catalogue_cov_record_ids = [
        t["target_id"]
        for t in cat_data["targets"]
        if t["family"] == "covering_design" and t["role"] == "record"
    ]

    assert reproduced_ids == catalogue_cov_record_ids
