"""Tests for P121: Extremal graph theory, Mantel-Turán, and Ramsey invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from evobyte.graph_ramsey import (
    audit_extremal_graph_ramsey_baseline,
    clique_number,
    erdos_szekeres_ramsey_bound,
    generate_extremal_graph_ramsey_lean_code,
    has_k_clique,
    independence_number,
    mantel_edge_bound,
    turan_edge_count,
    turan_graph_adjacency,
    turan_part_sizes,
    verify_extremal_graph_ramsey_baseline_soundness,
    verify_handshaking_lemma,
    verify_turan_extremal_properties,
)


def test_turan_part_sizes_and_edge_count():
    for n in range(1, 15):
        for r in range(2, 6):
            sizes = turan_part_sizes(n, r)
            assert len(sizes) == r
            assert sum(sizes) == n
            assert max(sizes) - min(sizes) <= 1
            adj = turan_graph_adjacency(n, r)
            num_edges = sum(sum(row) for row in adj) // 2
            assert num_edges == turan_edge_count(n, r)
            assert verify_handshaking_lemma(adj)


def test_mantel_theorem_and_turan_properties():
    for n in range(2, 12):
        assert turan_edge_count(n, 2) == mantel_edge_bound(n)
        props = verify_turan_extremal_properties(n, 2)
        assert props["is_kr_plus_1_free"] is True
        assert props["handshaking_holds"] is True
        assert props["density_bound_holds"] is True
        assert props["clique_matches_min_n_r"] is True
        assert props["independence_matches_max_part"] is True
        if n >= 2:
            assert props["clique_number"] == 2
        assert props["independence_number"] == (n + 1) // 2


def test_clique_and_independence_number():
    adj_t6_3 = turan_graph_adjacency(6, 3)
    assert has_k_clique(adj_t6_3, 3) is True
    assert has_k_clique(adj_t6_3, 4) is False
    assert clique_number(adj_t6_3) == 3
    assert independence_number(adj_t6_3) == 2


def test_erdos_szekeres_ramsey_bounds():
    assert erdos_szekeres_ramsey_bound(3, 3) == 6
    assert erdos_szekeres_ramsey_bound(3, 4) == 10
    assert erdos_szekeres_ramsey_bound(4, 4) == 20
    for s in range(3, 7):
        for t in range(3, 7):
            assert erdos_szekeres_ramsey_bound(s, t) == (
                erdos_szekeres_ramsey_bound(s - 1, t) + erdos_szekeres_ramsey_bound(s, t - 1)
            )


def test_generate_and_audit_p121_baseline(tmp_path: Path):
    code = generate_extremal_graph_ramsey_lean_code()
    assert "namespace EvoByte.ExtremalGraphRamsey" in code
    assert "sorry" not in code
    assert code.count("theorem ") >= 60

    audit = audit_extremal_graph_ramsey_baseline(
        project_dir="lean_proofs",
        lean_file="lean_proofs/Generated/ExtremalGraphRamseySignatures.lean",
        verify_lake=False,
    )
    sound, findings = verify_extremal_graph_ramsey_baseline_soundness(audit, min_theorems=60)
    assert sound is True, f"Unexpected soundness findings: {findings}"
    assert audit["total_theorems"] >= 60
    assert audit["has_sorry"] is False

    # Also test science_matrix runner with verify_lake=False and allow_dirty=True
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from science_matrix import run_p121_extremal_graph_ramsey_baseline_audit

    cfg_path = tmp_path / "p121-test-config.json"
    out_path = tmp_path / "p121-test-out.json"
    cfg_path.write_text(
        json.dumps(
            {
                "phase": "P121",
                "seed": 42,
                "device": "cpu",
                "project_dir": "lean_proofs",
                "lean_file": "lean_proofs/Generated/ExtremalGraphRamseySignatures.lean",
                "min_theorems": 60,
                "verify_lake": False,
                "require_clean_tree": False,
                "allow_dirty": True,
            }
        ),
        encoding="utf-8",
    )
    report = run_p121_extremal_graph_ramsey_baseline_audit(cfg_path, out_path)
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert out_path.exists()


def test_p122_paley_srg_and_ramsey_witnesses(tmp_path: Path):
    from evobyte.graph_ramsey import (
        audit_paley_ramsey_constructions,
        certify_ramsey_lower_bound,
        circulant_graph_adjacency,
        generate_ramsey_paley_lean_code,
        paley_graph_adjacency,
        quadratic_residues_mod_p,
        verify_paley_ramsey_soundness,
        verify_srg_parameters,
    )

    assert quadratic_residues_mod_p(5) == [1, 4]
    assert quadratic_residues_mod_p(13) == [1, 3, 4, 9, 10, 12]
    assert quadratic_residues_mod_p(17) == [1, 2, 4, 8, 9, 13, 15, 16]

    for p in (5, 13, 17, 29):
        adj_p = paley_graph_adjacency(p)
        srg = verify_srg_parameters(adj_p)
        assert srg["is_srg"] is True
        assert srg["v"] == p
        assert srg["k"] == (p - 1) // 2
        assert srg["lambda"] == (p - 5) // 4
        assert srg["mu"] == (p - 1) // 4

    w_r33 = certify_ramsey_lower_bound(paley_graph_adjacency(5), 3, 3)
    assert w_r33["valid_witness"] is True
    assert w_r33["certified_ramsey_lower_bound"] == 6

    w_r34 = certify_ramsey_lower_bound(circulant_graph_adjacency(8, [1, 4]), 3, 4)
    assert w_r34["valid_witness"] is True
    assert w_r34["certified_ramsey_lower_bound"] == 9

    w_r35 = certify_ramsey_lower_bound(circulant_graph_adjacency(13, [1, 5, 8, 12]), 3, 5)
    assert w_r35["valid_witness"] is True
    assert w_r35["certified_ramsey_lower_bound"] == 14

    w_r44 = certify_ramsey_lower_bound(paley_graph_adjacency(17), 4, 4)
    assert w_r44["valid_witness"] is True
    assert w_r44["certified_ramsey_lower_bound"] == 18

    code = generate_ramsey_paley_lean_code()
    assert "namespace EvoByte.RamseyPaley" in code
    assert "sorry" not in code
    assert code.count("theorem ") >= 60

    audit = audit_paley_ramsey_constructions(
        project_dir="lean_proofs",
        lean_file="lean_proofs/Generated/RamseyPaleyTheorems.lean",
        verify_lake=False,
    )
    sound, findings = verify_paley_ramsey_soundness(audit, min_theorems=60)
    assert sound is True, f"Unexpected P122 soundness findings: {findings}"
    assert audit["total_theorems"] >= 60
    assert audit["has_sorry"] is False

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root / "benchmarks") not in sys.path:
        sys.path.insert(0, str(repo_root / "benchmarks"))
    from science_matrix import run_p122_paley_ramsey_audit

    cfg_path = tmp_path / "p122-test-config.json"
    out_path = tmp_path / "p122-test-out.json"
    cfg_path.write_text(
        json.dumps(
            {
                "phase": "P122",
                "seed": 42,
                "device": "cpu",
                "project_dir": "lean_proofs",
                "lean_file": "lean_proofs/Generated/RamseyPaleyTheorems.lean",
                "min_theorems": 60,
                "verify_lake": False,
                "require_clean_tree": False,
                "allow_dirty": True,
            }
        ),
        encoding="utf-8",
    )
    report = run_p122_paley_ramsey_audit(cfg_path, out_path)
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert out_path.exists()
