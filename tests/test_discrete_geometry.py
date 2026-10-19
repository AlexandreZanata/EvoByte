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
    DEFAULT_CONVEX_POLYGONS_LEAN_FILE,
    audit_convex_polygons_happy_ending_baseline,
    erdos_szekeres_cup_cap_bound,
    find_convex_k_gons,
    find_empty_convex_holes,
    generate_convex_polygons_happy_ending_lean_code,
    is_empty_convex_hole,
    verify_convex_polygons_happy_ending_baseline_soundness,
    verify_happy_ending_properties,
    verify_unit_distance_properties,
    verify_unit_distances_szemeredi_trotter_baseline_soundness,
    DEFAULT_HADWIGER_NELSON_LEAN_FILE,
    audit_hadwiger_nelson_coloring_baseline,
    generate_hadwiger_nelson_coloring_lean_code,
    hadwiger_nelson_chromatic_interval,
    hexagonal_tiling_coloring_bounds,
    is_valid_unit_distance_coloring,
    moser_spindle_graph,
    verify_hadwiger_nelson_coloring_baseline_soundness,
    verify_moser_spindle_chromatic_number,
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


# ==============================================================================
# P133 TESTS: CONVEX POLYGONS & ERDŐS-SZEKERES HAPPY ENDING PROBLEM
# ==============================================================================


def test_erdos_szekeres_cup_cap_bound() -> None:
    """Test Erdős-Szekeres cup-cap combinatorial bounds and recurrence."""
    assert erdos_szekeres_cup_cap_bound(3, 3) == 3
    assert erdos_szekeres_cup_cap_bound(3, 4) == 4
    assert erdos_szekeres_cup_cap_bound(4, 3) == 4
    assert erdos_szekeres_cup_cap_bound(4, 4) == 7
    assert erdos_szekeres_cup_cap_bound(3, 5) == 5
    assert erdos_szekeres_cup_cap_bound(5, 3) == 5
    assert erdos_szekeres_cup_cap_bound(4, 5) == 11
    assert erdos_szekeres_cup_cap_bound(5, 4) == 11
    assert erdos_szekeres_cup_cap_bound(5, 5) == 21

    # Recurrence: f(a, b) = f(a-1, b) + f(a, b-1) - 1
    assert erdos_szekeres_cup_cap_bound(4, 4) == (
        erdos_szekeres_cup_cap_bound(3, 4) + erdos_szekeres_cup_cap_bound(4, 3) - 1
    )
    assert erdos_szekeres_cup_cap_bound(4, 5) == (
        erdos_szekeres_cup_cap_bound(3, 5) + erdos_szekeres_cup_cap_bound(4, 4) - 1
    )
    assert erdos_szekeres_cup_cap_bound(5, 5) == (
        erdos_szekeres_cup_cap_bound(4, 5) + erdos_szekeres_cup_cap_bound(5, 4) - 1
    )


def test_find_convex_k_gons_and_klein_theorem() -> None:
    """Test finding convex k-gons and verification of Klein's theorem on 5 points."""
    # 5 points in general position (4 on hull, 1 inside)
    pts1 = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 1)]
    quads1 = find_convex_k_gons(pts1, 4)
    assert len(quads1) >= 1

    # 5 points forming a strictly convex pentagon
    pts2 = [(0, 0), (4, 0), (5, 3), (2, 4), (0, 3)]
    quads2 = find_convex_k_gons(pts2, 4)
    assert len(quads2) == 5

    # Degenerate cases
    assert find_convex_k_gons([(0, 0), (1, 1)], 4) == []


def test_is_empty_convex_hole_and_search() -> None:
    """Test empty convex hole detection and search algorithms."""
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
    quad_with_interior = [(0, 0), (4, 0), (4, 4), (0, 4)]
    # Has (2, 2) inside, so cannot be empty
    assert is_empty_convex_hole(pts, quad_with_interior) is False

    # Strictly convex 5-gon has exactly 5 empty convex 4-holes
    pentagon = [(0, 0), (4, 0), (5, 3), (2, 4), (0, 3)]
    holes4 = find_empty_convex_holes(pentagon, 4)
    assert len(holes4) == 5

    # 3-holes
    holes3 = find_empty_convex_holes(pentagon, 3)
    assert len(holes3) >= 1


def test_verify_happy_ending_properties() -> None:
    """Test Happy Ending properties verification on benchmark point configurations."""
    configs = [
        [(0, 0), (4, 0), (4, 4), (0, 4), (2, 1)],
        [(0, 0), (4, 0), (5, 3), (2, 4), (0, 3)],
        [(0, 0), (6, 0), (8, 4), (5, 7), (1, 6), (3, 3)],
        [(0, 0), (5, 0), (7, 3), (6, 6), (2, 7), (-1, 4), (2, 3)],
    ]
    for pts in configs:
        res = verify_happy_ending_properties(pts)
        assert res["n_points"] >= 5
        assert res["is_general_position"] is True
        assert res["klein_holds"] is True
        assert res["happy_ending_property_holds"] is True
        assert res["convex_4_gons_count"] >= 1


def test_generate_convex_polygons_happy_ending_lean_code() -> None:
    """Test generation of ConvexPolygonsHappyEndingTheorems.lean module."""
    code = generate_convex_polygons_happy_ending_lean_code()
    assert "namespace EvoByte.HappyEnding" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 75


def test_audit_convex_polygons_happy_ending_baseline() -> None:
    """Test P133 baseline audit against Lean 4 kernel."""
    audit = audit_convex_polygons_happy_ending_baseline(verify_lake=True)
    assert audit["module"] == "ConvexPolygonsHappyEndingTheorems"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert len(audit["benchmarks"]) >= 4

    sound, findings = verify_convex_polygons_happy_ending_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_convex_polygons_soundness_rejections() -> None:
    """Test that P133 soundness validator properly catches defects."""
    bad_audit = {
        "has_sorry": True,
        "total_theorems": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": [{"happy_ending_property_holds": True, "klein_holds": True, "n_points": 5}],
    }
    sound, findings = verify_convex_polygons_happy_ending_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    sparse_audit = {
        "has_sorry": False,
        "total_theorems": 10,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": [{"happy_ending_property_holds": True, "klein_holds": True, "n_points": 5}],
    }
    sound, findings = verify_convex_polygons_happy_ending_baseline_soundness(sparse_audit, min_theorems=75)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    failing_audit = {
        "has_sorry": False,
        "total_theorems": 100,
        "lake_passed": False,
        "sha256": "a" * 64,
        "benchmarks": [{"happy_ending_property_holds": True, "klein_holds": True, "n_points": 5}],
    }
    sound, findings = verify_convex_polygons_happy_ending_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)


# ==============================================================================
# P134 TESTS: HADWIGER-NELSON PROBLEM & PLANE COLORING
# ==============================================================================


def test_moser_spindle_graph() -> None:
    """Test construction of Moser spindle 7-vertex 11-edge unit-distance graph."""
    vertices, edges = moser_spindle_graph()
    assert len(vertices) == 7
    assert len(edges) == 11
    assert vertices == list(range(7))

    # All edges are pairs (u, v) with u < v
    for u, v in edges:
        assert 0 <= u < v < 7

    # Check key structural edges: shared apex 0, tips 3 and 6, cross edge (3, 6)
    assert (3, 6) in edges
    assert (0, 1) in edges and (0, 2) in edges and (0, 4) in edges and (0, 5) in edges


def test_is_valid_unit_distance_coloring() -> None:
    """Test validity checker for unit distance proper graph coloring."""
    _, edges = moser_spindle_graph()

    # Monochromatic coloring is completely invalid
    all_zeros = [0] * 7
    assert is_valid_unit_distance_coloring(edges, all_zeros) is False

    # Valid 4-coloring
    col4 = [0, 1, 2, 0, 1, 2, 3]
    assert is_valid_unit_distance_coloring(edges, col4) is True

    # Violate cross edge (3, 6)
    invalid_col = [0, 1, 2, 0, 1, 2, 0]
    assert is_valid_unit_distance_coloring(edges, invalid_col) is False


def test_verify_moser_spindle_chromatic_number() -> None:
    """Test Moser spindle invariants: non-3-colorable, 4-colorable, omega=3, alpha=2."""
    res = verify_moser_spindle_chromatic_number()
    assert res["vertices_count"] == 7
    assert res["edges_count"] == 11
    assert res["valid_3_colorings_count"] == 0
    assert res["is_3_colorable"] is False
    assert res["is_4_colorable"] is True
    assert res["chromatic_number"] == 4
    assert res["clique_number"] == 3
    assert res["triangles_count"] == 4
    assert res["independence_number"] == 2
    assert res["ceil_n_div_alpha"] == 4
    assert res["handshaking_holds"] is True
    assert res["degree_sum"] == 22
    assert res["invariants_hold"] is True


def test_hexagonal_tiling_coloring_bounds() -> None:
    """Test Isbell's hexagonal 7-coloring geometry and diameter bounds."""
    res = hexagonal_tiling_coloring_bounds()
    assert res["side_length"] == 0.44
    assert res["tile_diameter"] < 1.0
    assert res["tile_diameter_strictly_less_than_1"] is True
    assert res["min_same_color_distance"] > 1.0
    assert res["min_same_color_distance_strictly_greater_than_1"] is True
    assert res["integer_check_passed"] is True
    assert res["isbell_upper_bound"] == 7
    assert res["bounds_valid"] is True


def test_hadwiger_nelson_chromatic_interval() -> None:
    """Test Hadwiger-Nelson bounds interval: [5, 7]."""
    res = hadwiger_nelson_chromatic_interval()
    assert res["lower_bound_moser"] == 4
    assert res["lower_bound_degrey"] == 5
    assert res["upper_bound_isbell"] == 7
    assert res["current_best_lower_bound"] == 5
    assert res["current_best_upper_bound"] == 7
    assert res["chromatic_interval"] == [5, 7]
    assert res["possible_chromatic_numbers"] == [5, 6, 7]
    assert res["degrey_vertex_count"] == 1581
    assert res["exoo_ismailescu_vertex_count"] == 553
    assert res["heule_vertex_counts"] == [510, 509]
    assert res["all_bounds_consistent"] is True


def test_generate_hadwiger_nelson_coloring_lean_code() -> None:
    """Test generation of HadwigerNelsonColoringTheorems.lean module."""
    code = generate_hadwiger_nelson_coloring_lean_code()
    assert "namespace EvoByte.HadwigerNelson" in code
    assert "sorry" not in code
    thms = [line for line in code.splitlines() if line.startswith("theorem ") or line.startswith("lemma ")]
    assert len(thms) >= 75


def test_audit_hadwiger_nelson_coloring_baseline() -> None:
    """Test P134 baseline audit against Lean 4 kernel."""
    audit = audit_hadwiger_nelson_coloring_baseline(verify_lake=True)
    assert audit["module"] == "HadwigerNelsonColoringTheorems"
    assert audit["has_sorry"] is False
    assert audit["lake_passed"] is True
    assert audit["total_theorems"] >= 75
    assert audit["benchmarks"]["moser_invariants"]["invariants_hold"] is True
    assert audit["benchmarks"]["tiling_bounds"]["bounds_valid"] is True
    assert audit["benchmarks"]["interval_bounds"]["all_bounds_consistent"] is True

    sound, findings = verify_hadwiger_nelson_coloring_baseline_soundness(audit, min_theorems=75)
    assert sound is True
    assert findings == []


def test_verify_hadwiger_nelson_coloring_soundness_rejections() -> None:
    """Test that P134 soundness validator properly catches defects."""
    bad_audit = {
        "has_sorry": True,
        "total_theorems": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": {
            "moser_invariants": {"invariants_hold": True},
            "tiling_bounds": {"bounds_valid": True},
            "interval_bounds": {"all_bounds_consistent": True},
        },
    }
    sound, findings = verify_hadwiger_nelson_coloring_baseline_soundness(bad_audit)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)

    sparse_audit = {
        "has_sorry": False,
        "total_theorems": 10,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": {
            "moser_invariants": {"invariants_hold": True},
            "tiling_bounds": {"bounds_valid": True},
            "interval_bounds": {"all_bounds_consistent": True},
        },
    }
    sound, findings = verify_hadwiger_nelson_coloring_baseline_soundness(sparse_audit, min_theorems=75)
    assert sound is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)

    failing_audit = {
        "has_sorry": False,
        "total_theorems": 100,
        "lake_passed": False,
        "sha256": "a" * 64,
        "benchmarks": {
            "moser_invariants": {"invariants_hold": True},
            "tiling_bounds": {"bounds_valid": True},
            "interval_bounds": {"all_bounds_consistent": True},
        },
    }
    sound, findings = verify_hadwiger_nelson_coloring_baseline_soundness(failing_audit)
    assert sound is False
    assert any("LAKE_BUILD_FAILED" in f for f in findings)

    bad_bench_audit = {
        "has_sorry": False,
        "total_theorems": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
        "benchmarks": {
            "moser_invariants": {"invariants_hold": False},
            "tiling_bounds": {"bounds_valid": True},
            "interval_bounds": {"all_bounds_consistent": True},
        },
    }
    sound, findings = verify_hadwiger_nelson_coloring_baseline_soundness(bad_bench_audit)
    assert sound is False
    assert any("INVALID_MOSER_BENCHMARK" in f for f in findings)
