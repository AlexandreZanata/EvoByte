"""P163 guard tests: independent verifiers for the frozen record-target catalogue."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from evobyte import target_catalogue
from evobyte.target_catalogue import (
    load_catalogue,
    verify_graph_spectral_conjecture,
    verify_schur_partition,
    verify_vanderwaerden_coloring,
)

REPO = Path(__file__).resolve().parents[1]
CATALOGUE = REPO / "docs" / "research" / "targets" / "open_targets.json"

# Valid 2-coloring of [1..8] with zero monochromatic 3-term APs (W(2,3) = 9).
VALID_W23_COLORING = [1, 1, 2, 2, 1, 1, 2, 2]

# The example given in the phase specification. It is NOT a valid coloring: positions
# 1, 4 and 7 carry the same color and form a monochromatic 3-term AP.
SPEC_EXAMPLE_W23_COLORING = [1, 1, 2, 1, 2, 2, 1, 2]

VALID_SCHUR_PARTITION = [1, 2, 2, 1]
SCHUR_VIOLATION_PARTITION = [1, 1, 1, 2]

PATH_P4 = [
    [0, 1, 0, 0],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [0, 0, 1, 0],
]


def test_vanderwaerden_valid_sample():
    ok, message = verify_vanderwaerden_coloring(VALID_W23_COLORING, r=2, k=3)
    assert ok is True
    assert "valid" in message


def test_vanderwaerden_violation_detected():
    ok, message = verify_vanderwaerden_coloring([1, 1, 1, 2, 2, 2], r=2, k=3)
    assert ok is False
    assert "monochromatic AP" in message


def test_vanderwaerden_specification_example_is_rejected():
    """The coloring proposed in the phase spec is invalid and must not certify anything."""
    ok, message = verify_vanderwaerden_coloring(SPEC_EXAMPLE_W23_COLORING, r=2, k=3)
    assert ok is False
    assert "monochromatic AP" in message


def test_schur_valid_sample():
    ok, message = verify_schur_partition(VALID_SCHUR_PARTITION, k=2)
    assert ok is True
    assert "valid sum-free" in message


def test_schur_violation_detected():
    ok, message = verify_schur_partition(SCHUR_VIOLATION_PARTITION, k=2)
    assert ok is False
    assert "Schur violation" in message


def test_graph_spectral_properties():
    is_counterexample, metrics = verify_graph_spectral_conjecture(PATH_P4, "AH_diam_mu2")
    assert is_counterexample is False
    assert metrics["n"] == 4
    assert metrics["diameter"] == 3.0
    assert metrics["connected"] is True
    # Laplacian of P4: eigenvalues 0, 2 - sqrt(2), 2, 2 + sqrt(2).
    assert abs(metrics["mu_2"] - (2.0 - np.sqrt(2.0))) < 1e-9
    # Adjacency eigenvalues of P4: 2*cos(k*pi/5) for k = 1..4, so lambda_1 = 2*cos(pi/5).
    assert abs(metrics["lambda_1"] - 2.0 * np.cos(np.pi / 5.0)) < 1e-9
    assert abs(metrics["lhs_value"] - (3.0 + 2.0 - np.sqrt(2.0))) < 1e-9


def test_graph_rejects_malformed_inputs():
    assert verify_graph_spectral_conjecture([[0, 1], [0, 0]], "AH_diam_mu2")[0] is False
    assert verify_graph_spectral_conjecture([[0]], "AH_diam_mu2")[0] is False
    assert verify_graph_spectral_conjecture([], "AH_diam_mu2")[0] is False
    assert verify_graph_spectral_conjecture([[0, 1], [1, 0]], "unknown_conjecture")[0] is False


def test_catalogue_schema():
    raw = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    assert raw["version"] == "1.0.0"
    assert len(raw["targets"]) == 4

    targets = load_catalogue(CATALOGUE)
    assert len(targets) == 4
    for spec in targets:
        assert spec.target_id
        assert spec.family
        assert spec.description
        assert spec.reference
        assert isinstance(spec.published_bound, float)
        assert spec.bound_type in {"lower_bound", "upper_bound", "counterexample_threshold"}
        assert callable(getattr(target_catalogue, spec.verification_fn))

    ids = {spec.target_id for spec in targets}
    assert ids == {
        "vanderwaerden_w3_3",
        "vanderwaerden_w2_6",
        "schur_s5",
        "spectral_graph_diam_mu2",
    }
