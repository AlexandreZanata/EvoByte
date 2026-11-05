"""Unit tests for Diophantine obstruction graphs and negative search space data engine (P106)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.science_matrix import run_p106_obstruction_graphs_audit
from evobyte.algebraic import (
    ObstructionNode,
    build_diophantine_obstruction_graph,
    evaluate_obstruction_graph_pruning,
)
from evobyte.formal_bridge import (
    audit_obstruction_graphs_data_engine,
    export_obstruction_theorems_lean,
    generate_obstruction_theorems_lean_code,
    verify_obstruction_graphs_soundness,
)


def test_diophantine_obstruction_graph_build():
    graph = build_diophantine_obstruction_graph(a=4, primes=[2, 3, 5, 7])
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0

    # Distinct residues on same variable and modulus are incompatible
    n_r0 = ObstructionNode("n", 4, 0)
    n_r1 = ObstructionNode("n", 4, 1)
    assert graph.is_incompatible(n_r0, n_r1) is True
    assert graph.is_incompatible(n_r0, n_r0) is False

    # Parity obstruction: even a=4, odd n forces odd d
    n_odd = ObstructionNode("n", 2, 1)
    d_even = ObstructionNode("d", 2, 0)
    assert graph.is_incompatible(n_odd, d_even) is True


def test_prune_divisor_candidates_soundness():
    graph = build_diophantine_obstruction_graph(a=4)
    # For n=101 (prime), n^2 = 10201. Real divisors in range [1, 202] are 1, 101.
    candidates = list(range(1, 203))
    survived, pruned = graph.prune_divisor_candidates(101, candidates)

    assert pruned > 0
    assert len(survived) + pruned == len(candidates)
    # Real divisors must not be pruned
    assert 1 in survived
    assert 101 in survived
    assert not graph.is_candidate_obstructed(101, 1)
    assert not graph.is_candidate_obstructed(101, 101)


def test_evaluate_obstruction_graph_pruning():
    res = evaluate_obstruction_graph_pruning(instances=[101, 103, 107], a=4)
    assert res["is_sound"] is True
    assert res["false_negatives"] == 0
    assert res["pruning_ratio"] >= 0.50
    assert res["total_pruned"] > 0


def test_generate_and_export_obstruction_theorems_lean(tmp_path: Path):
    code = generate_obstruction_theorems_lean_code()
    assert "namespace EvoByte.Obstructions" in code
    assert "structure ModState" in code
    assert "theorem incompatible_states_exclusive" in code
    assert "theorem incompatible_symm" in code
    assert "theorem incompatible_irreflexive" in code
    assert "theorem mod_obstruction_m2_r1" in code
    assert "theorem pillai_catalan_diff_9_8" in code
    assert "sorry" not in code

    out_p = tmp_path / "ObstructionTheorems.lean"
    exported = export_obstruction_theorems_lean(out_p)
    assert exported.exists()
    assert exported.read_text(encoding="utf-8") == code


def test_audit_obstruction_graphs_data_engine_smoke():
    res = audit_obstruction_graphs_data_engine(verify_lake=False)
    assert res["phase"] == "P106"
    assert res["theorem_count"] >= 60
    assert res["has_sorry"] is False
    assert res["is_sound"] is True
    assert res["false_negatives"] == 0
    assert res["pruning_ratio"] >= 0.50


def test_verify_obstruction_graphs_soundness():
    good = {
        "theorem_count": 92,
        "has_sorry": False,
        "is_sound": True,
        "false_negatives": 0,
        "pruning_ratio": 0.75,
        "lake_passed": True,
    }
    sound, findings = verify_obstruction_graphs_soundness(good)
    assert sound is True
    assert len(findings) == 0

    bad = {
        "theorem_count": 20,
        "has_sorry": True,
        "is_sound": False,
        "false_negatives": 3,
        "pruning_ratio": 0.20,
        "lake_passed": False,
        "lake_reasons": ["build failed"],
    }
    sound, findings = verify_obstruction_graphs_soundness(bad)
    assert sound is False
    assert any("SORRY_DETECTED" in f for f in findings)
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)
    assert any("LAKE_BUILD_FAILED" in f for f in findings)
    assert any("FALSE_NEGATIVES_DETECTED" in f for f in findings)
    assert any("INSUFFICIENT_PRUNING" in f for f in findings)


def test_p106_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P106 configuration"):
        run_p106_obstruction_graphs_audit(cfg_p, tmp_path / "out.json")


def test_p106_acceptance_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P106",
        "acceptance_phase": "P106",
        "min_theorems": 60,
        "min_pruning_ratio": 0.50,
        "a": 4,
        "budget_sec": 3600.0,
        "generated_path": "lean_proofs/Generated/ObstructionGraphTheorems.lean",
        "project_dir": "lean_proofs",
        "allow_dirty": True,
        "require_clean_tree": False,
        "verify_lake": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p106-smoke.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p106-out.json"

    report = run_p106_obstruction_graphs_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P106"
    assert report["verdict"] == "ACCEPTED"
    assert report["theorem_count"] >= 60
    assert report["has_sorry"] is False
    assert report["is_sound"] is True
    assert report["false_negatives"] == 0
