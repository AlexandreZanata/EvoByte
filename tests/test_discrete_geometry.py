"""Tests for discrete geometry, metric embedding, and distinct distance formal baseline (P129)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from evobyte.discrete_geometry import (
    are_points_colinear,
    audit_discrete_geometry_baseline,
    audit_erdos_distinct_distances_baseline,
    audit_unit_distances_szemeredi_trotter_baseline,
    circular_points,
    convex_hull_2d,
    count_point_line_incidences,
    cross_product_2d,
    distinct_distance_count,
    distinct_squared_distances,
    distance_quadruples_energy,
    erdos_elementary_distance_bound,
    erdos_szekeres_happy_ending_bound,
    erdos_unit_distance_kst_bound,
    erdos_unit_distance_lower_bound,
    generate_discrete_geometry_signatures_lean_code,
    generate_erdos_distinct_distances_lean_code,
    generate_grid_lines,
    generate_unit_distances_szemeredi_trotter_lean_code,
    grid_distinct_distance_count,
    grid_points,
    guth_katz_lower_estimate,
    historical_distinct_distance_bounds,
    is_convex_polygon,
    is_in_general_position,
    landau_ramanujan_grid_estimate,
    linear_points,
    moser_spindle_points,
    pairwise_squared_distances,
    point_line_incidence,
    spencer_szemeredi_trotter_bound,
    sq_euclidean_distance,
    triangular_grid_points,
    unit_distance_count,
    unit_distance_graph_degrees,
    verify_discrete_geometry_baseline_soundness,
    verify_discrete_geometry_properties,
    verify_erdos_distinct_distances_baseline_soundness,
    verify_erdos_distinct_distances_properties,
    DEFAULT_DISCRETE_GEOMETRY_TACTIC_LEAN_FILE,
    audit_discrete_geometry_tactic_baseline,
    discrete_geometry_tactic_benchmarks,
    generate_discrete_geometry_tactic_lean_code,
    normalize_squared_distance_expression,
    verify_discrete_geometry_tactic_baseline_soundness,
    verify_unit_distance_properties,
    verify_unit_distances_szemeredi_trotter_baseline_soundness,
)


def test_sq_euclidean_distance_and_identities() -> None:
    """Test metric distance properties and algebraic symmetries."""
    assert sq_euclidean_distance((0, 0), (0, 0)) == 0
    assert sq_euclidean_distance((3, 4), (0, 0)) == 25
    assert sq_euclidean_distance((1, 2), (4, 6)) == 25
    # Symmetry
    assert sq_euclidean_distance((1, 2), (4, 6)) == sq_euclidean_distance((4, 6), (1, 2))
    # Translation invariance
    assert sq_euclidean_distance((1 + 10, 2 - 5), (4 + 10, 6 - 5)) == sq_euclidean_distance((1, 2), (4, 6))


def test_pairwise_and_distinct_distances() -> None:
    """Test pairwise squared distance calculations and distinct counts."""
    pts = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Unit square
    pairs = pairwise_squared_distances(pts)
    assert len(pairs) == 6  # C(4, 2) = 6
    dists = distinct_squared_distances(pts)
    assert dists == {1, 2}  # Side 1 (sq=1), Diagonal sqrt(2) (sq=2)
    assert distinct_distance_count(pts) == 2


def test_linear_and_grid_distance_bounds() -> None:
    """Test Erdős distinct distance elementary bounds for colinear and grid points."""
    colinear = linear_points(5)
    assert len(colinear) == 5
    # n colinear points have exactly n-1 distinct distances
    assert distinct_distance_count(colinear) == 4

    for n in (4, 9, 16, 25):
        bound = erdos_elementary_distance_bound(n)
        # bound ~ sqrt(2n) - 1
        assert bound <= n - 1

    grid4 = grid_points(4)
    assert len(grid4) == 16
    n_distinct = distinct_distance_count(grid4)
    elem_bound = erdos_elementary_distance_bound(16)
    assert n_distinct >= elem_bound
    assert grid_distinct_distance_count(4) == n_distinct


def test_cross_product_and_colinearity() -> None:
    """Test 2D determinant and orientation predicates."""
    # Colinear horizontal
    assert cross_product_2d((0, 0), (2, 0), (5, 0)) == 0
    assert are_points_colinear((0, 0), (2, 0), (5, 0)) is True
    # Non-colinear triangle
    assert cross_product_2d((0, 0), (1, 0), (0, 1)) == 1
    assert are_points_colinear((0, 0), (1, 0), (0, 1)) is False


def test_general_position_and_convex_hull() -> None:
    """Test general position detector and 2D convex hull Graham scan."""
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert is_in_general_position(square) is True
    square_with_midpoint = [(0, 0), (1, 0), (2, 0), (2, 2), (0, 2)]
    assert is_in_general_position(square_with_midpoint) is False

    hull = convex_hull_2d(square_with_midpoint)
    assert len(hull) == 4
    assert is_convex_polygon(hull) is True


def test_erdos_szekeres_and_moser_spindle() -> None:
    """Test Erdős-Szekeres bound and Moser spindle unit distance graph."""
    assert erdos_szekeres_happy_ending_bound(3) == 3
    assert erdos_szekeres_happy_ending_bound(4) == math.comb(4, 2) + 1  # 7
    assert erdos_szekeres_happy_ending_bound(5) == math.comb(6, 3) + 1  # 21

    spindle = moser_spindle_points()
    assert len(spindle) == 7
    u_count = unit_distance_count(spindle, unit_sq=4)
    assert u_count >= 1


def test_verify_discrete_geometry_properties() -> None:
    """Test property verification dictionary on grid point sets."""
    props = verify_discrete_geometry_properties(grid_points(3))
    assert props["n_points"] == 9
    assert props["total_pairs"] == 36
    assert props["elementary_bound_holds"] is True
    assert props["distinct_distances"] > 0
    assert props["convex_hull_size"] == 4


def test_generate_discrete_geometry_signatures_lean_code() -> None:
    """Test that generated Lean 4 file is syntactically sound, sorry-free, and has >= 75 theorems."""
    code = generate_discrete_geometry_signatures_lean_code()
    assert "namespace EvoByte.DiscreteGeometry" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 75


def test_audit_discrete_geometry_baseline() -> None:
    """Test baseline audit against live project Lean 4 code."""
    audit = audit_discrete_geometry_baseline(verify_lake=True)
    assert audit["module"] == "DiscreteGeometrySignatures"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert len(audit["geometry_benchmarks"]) == 4

    sound, findings = verify_discrete_geometry_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_soundness_rejections() -> None:
    """Test that soundness validator properly catches defects."""
    # Sorry detection
    bad_audit = {"has_sorry": True, "total_theorems": 100, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_discrete_geometry_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    # Insufficient theorems
    sparse_audit = {"has_sorry": False, "total_theorems": 10, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_discrete_geometry_baseline_soundness(sparse_audit, min_theorems=75)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    # Lake failure
    failing_audit = {"has_sorry": False, "total_theorems": 100, "lake_passed": False, "sha256": "a" * 64}
    sound, findings = verify_discrete_geometry_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)


def test_triangular_and_circular_point_generators() -> None:
    """Test triangular Eisenstein lattice and circular point set generation."""
    tri3 = triangular_grid_points(3)
    assert len(tri3) == 9
    circ8 = circular_points(8, radius=500)
    assert len(circ8) == 8
    # All points lie within roughly radius distance from origin
    for x, y in circ8:
        dist_sq = x * x + y * y
        assert abs(math.sqrt(dist_sq) - 500) <= 2.0


def test_distance_energy_and_cauchy_schwarz() -> None:
    """Test distance energy E(P) calculation and Cauchy-Schwarz inequality D * E >= pairs^2."""
    pts = grid_points(3)  # 3x3 grid, 9 points, 36 pairs
    props = verify_erdos_distinct_distances_properties(pts)
    assert props["n_points"] == 9
    assert props["total_pairs"] == 36
    assert props["distinct_distances"] == 5
    assert props["distance_energy"] > 0
    assert props["cs_inequality_holds"] is True
    # D * E >= pairs^2
    assert props["product_d_e"] >= props["pairs_squared"]


def test_theoretical_bounds_estimates() -> None:
    """Test Landau-Ramanujan and Guth-Katz theoretical estimates and historical chain."""
    n = 100
    lr = landau_ramanujan_grid_estimate(n)
    gk = guth_katz_lower_estimate(n)
    assert lr > 0
    assert gk > 0

    hist = historical_distinct_distance_bounds(n)
    # Check monotonicity of historical bounds: 1946 <= 1952 <= 1984 <= 1997 <= 2001
    assert hist["erdos_1946"] <= hist["moser_1952"]
    assert hist["moser_1952"] <= hist["chung_1984"]
    assert hist["chung_1984"] <= hist["szekely_1997"]
    assert hist["szekely_1997"] <= hist["solymosi_toth_2001"]


def test_generate_erdos_distinct_distances_lean_code() -> None:
    """Test generation of ErdosDistinctDistancesTheorems.lean module."""
    code = generate_erdos_distinct_distances_lean_code()
    assert "namespace EvoByte.ErdosDistinctDistances" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 75


def test_audit_erdos_distinct_distances_baseline() -> None:
    """Test P130 baseline audit against Lean 4 kernel."""
    audit = audit_erdos_distinct_distances_baseline(verify_lake=True)
    assert audit["module"] == "ErdosDistinctDistancesTheorems"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert len(audit["benchmarks"]) >= 5

    sound, findings = verify_erdos_distinct_distances_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_erdos_soundness_rejections() -> None:
    """Test that P130 soundness validator properly catches defects."""
    bad_audit = {"has_sorry": True, "total_theorems": 100, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_erdos_distinct_distances_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    sparse_audit = {"has_sorry": False, "total_theorems": 10, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_erdos_distinct_distances_baseline_soundness(sparse_audit, min_theorems=75)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    failing_audit = {"has_sorry": False, "total_theorems": 100, "lake_passed": False, "sha256": "a" * 64}
    sound, findings = verify_erdos_distinct_distances_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)


def test_point_line_incidences_and_grid_lines() -> None:
    """Test point-line incidence detector and grid line generation."""
    # Line x - y = 0
    line_diag = (1, -1, 0)
    assert point_line_incidence((0, 0), line_diag) is True
    assert point_line_incidence((2, 2), line_diag) is True
    assert point_line_incidence((1, 2), line_diag) is False

    pts = grid_points(3)  # 9 points
    lines = generate_grid_lines(3)  # 3 horizontal + 3 vertical = 6 lines
    assert len(lines) == 6
    # Each point belongs to exactly 1 horizontal and 1 vertical line, so total incidences = 2 * 9 = 18
    incidences = count_point_line_incidences(pts, lines)
    assert incidences == 18


def test_unit_distance_properties_and_handshaking() -> None:
    """Test unit distance graph invariants and handshaking theorem sum deg(v) = 2*u."""
    pts = grid_points(3)  # 9 points, 12 unit edges (4 horizontal pairs per row * 3? No: 2 per row * 3 + 2 per col * 3 = 12)
    props = verify_unit_distance_properties(pts, unit_sq=1)
    assert props["n_points"] == 9
    assert props["unit_distances"] == 12
    assert props["sum_degrees"] == 24
    assert props["handshaking_holds"] is True
    assert props["sst_cubic_holds"] is True

    # Moser spindle: 7 vertices, 11 edges (with unit_sq=4)
    spindle = moser_spindle_points()
    s_props = verify_unit_distance_properties(spindle, unit_sq=4)
    assert s_props["n_points"] == 7
    assert s_props["handshaking_holds"] is True
    assert s_props["sum_degrees"] == 2 * s_props["unit_distances"]


def test_unit_distance_theoretical_bounds() -> None:
    """Test Spencer-Szemerédi-Trotter and Erdős unit distance bounds."""
    for n in (10, 50, 100):
        sst = spencer_szemeredi_trotter_bound(n)
        kst = erdos_unit_distance_kst_bound(n)
        lower = erdos_unit_distance_lower_bound(n)
        assert sst > 0
        assert kst > 0
        assert lower > 0
        # SST exponent 4/3 is strictly lower than KST exponent 3/2 for large n
        if n >= 100:
            assert sst < kst * 8


def test_generate_unit_distances_szemeredi_trotter_lean_code() -> None:
    """Test generation of UnitDistancesSzemerediTrotterTheorems.lean module."""
    code = generate_unit_distances_szemeredi_trotter_lean_code()
    assert "namespace EvoByte.UnitDistances" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 75


def test_audit_unit_distances_szemeredi_trotter_baseline() -> None:
    """Test P131 baseline audit against Lean 4 kernel."""
    audit = audit_unit_distances_szemeredi_trotter_baseline(verify_lake=True)
    assert audit["module"] == "UnitDistancesSzemerediTrotterTheorems"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert len(audit["benchmarks"]) >= 4

    sound, findings = verify_unit_distances_szemeredi_trotter_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_unit_distances_soundness_rejections() -> None:
    """Test that P131 soundness validator properly catches defects."""
    bad_audit = {"has_sorry": True, "total_theorems": 100, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_unit_distances_szemeredi_trotter_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    sparse_audit = {"has_sorry": False, "total_theorems": 10, "lake_passed": True, "sha256": "a" * 64}
    sound, findings = verify_unit_distances_szemeredi_trotter_baseline_soundness(sparse_audit, min_theorems=75)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    failing_audit = {"has_sorry": False, "total_theorems": 100, "lake_passed": False, "sha256": "a" * 64}
    sound, findings = verify_unit_distances_szemeredi_trotter_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)


# ==============================================================================
# P132 TESTS: GEOM_DISTANCE_NORM METATACTIC & GEOMETRIC AUTOMATION
# ==============================================================================


def test_normalize_squared_distance_expression() -> None:
    """Test algebraic normalization of squared distance expression."""
    res = normalize_squared_distance_expression((1, 2), (4, 6))
    assert res["dx"] == 3
    assert res["dy"] == 4
    assert res["dx_sq"] == 9
    assert res["dy_sq"] == 16
    assert res["total_sq"] == 25
    assert res["is_zero"] is False
    assert res["is_axial"] is False
    assert res["is_diagonal"] is False

    diag = normalize_squared_distance_expression((0, 0), (5, 5))
    assert diag["is_diagonal"] is True
    assert diag["total_sq"] == 50


def test_discrete_geometry_tactic_benchmarks() -> None:
    """Test algebraic Euclidean metric and tactic property benchmarks."""
    benchmarks = discrete_geometry_tactic_benchmarks()
    assert len(benchmarks) >= 1
    for b in benchmarks:
        assert b["parallelogram_holds"] is True
        assert b["apollonius_holds"] is True
        assert b["leibniz_holds"] is True
        assert b["lagrange_holds"] is True
        assert b["eisenstein_holds"] is True
        assert b["all_properties_hold"] is True


def test_generate_discrete_geometry_tactic_lean_code() -> None:
    """Test generation of DiscreteGeometryTacticTheorems.lean module."""
    code = generate_discrete_geometry_tactic_lean_code()
    assert "namespace EvoByte.DiscreteGeometryTactic" in code
    assert 'syntax "geom_distance_norm" : tactic' in code
    assert 'syntax "geom_distance_intro" : tactic' in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 80


def test_audit_discrete_geometry_tactic_baseline() -> None:
    """Test P132 baseline audit against Lean 4 kernel."""
    audit = audit_discrete_geometry_tactic_baseline(verify_lake=True)
    assert audit["module"] == "DiscreteGeometryTacticTheorems"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["has_syntax_def"] is True
    assert audit["total_theorems"] >= 80
    assert audit["tactic_uses"] >= 80
    assert len(audit["benchmarks"]) >= 1

    sound, findings = verify_discrete_geometry_tactic_baseline_soundness(audit, min_theorems=80)
    assert sound is True
    assert findings == []


def test_verify_discrete_geometry_tactic_soundness_rejections() -> None:
    """Test that P132 soundness validator properly catches defects."""
    bad_audit = {
        "has_sorry": True,
        "has_syntax_def": True,
        "total_theorems": 100,
        "tactic_uses": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": [{"all_properties_hold": True}],
    }
    sound, findings = verify_discrete_geometry_tactic_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    no_syntax = {
        "has_sorry": False,
        "has_syntax_def": False,
        "total_theorems": 100,
        "tactic_uses": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": [{"all_properties_hold": True}],
    }
    sound, findings = verify_discrete_geometry_tactic_baseline_soundness(no_syntax)
    assert sound is False
    assert any("MISSING_SYNTAX_DEF" in f for f in findings)

    sparse_audit = {
        "has_sorry": False,
        "has_syntax_def": True,
        "total_theorems": 10,
        "tactic_uses": 10,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": [{"all_properties_hold": True}],
    }
    sound, findings = verify_discrete_geometry_tactic_baseline_soundness(sparse_audit, min_theorems=80)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    failing_audit = {
        "has_sorry": False,
        "has_syntax_def": True,
        "total_theorems": 100,
        "tactic_uses": 100,
        "lake_passed": False,
        "sha256": "a" * 64,
        "benchmarks": [{"all_properties_hold": True}],
    }
    sound, findings = verify_discrete_geometry_tactic_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)
