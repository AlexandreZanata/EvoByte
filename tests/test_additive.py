"""Unit tests for additive combinatorics, Sidon sets, and P113 baseline formal audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.science_matrix import (
    run_p113_additive_combinatorics_baseline_audit,
    run_p114_sidon_sets_audit,
    run_p115_additive_energy_audit,
    run_p116_additive_norm_audit,
    run_p117_erdos_turan_bases_audit,
    run_p118_sum_free_density_audit,
    run_p119_additive_blind_confirmation_audit,
    run_p120_additive_grand_campaign_audit,
    run_p149_constructive_certificates_audit,
)
from evobyte.additive import (
    DEFAULT_ADDITIVE_ENERGY_LEAN_FILE,
    DEFAULT_ADDITIVE_TACTIC_LEAN_FILE,
    DEFAULT_ERDOS_TURAN_BASES_LEAN_FILE,
    DEFAULT_EXTREMAL_CONSTRUCTIVE_CERTIFICATES_LEAN_FILE,
    DEFAULT_LEAN_FILE,
    DEFAULT_SIDON_THEOREMS_LEAN_FILE,
    DEFAULT_SUM_FREE_THEOREMS_LEAN_FILE,
    additive_energy,
    audit_additive_combinatorics_baseline,
    audit_additive_energy_balog_szemeredi,
    audit_additive_norm_metatactic,
    audit_erdos_turan_additive_bases,
    audit_extremal_constructive_certificates_baseline,
    audit_sidon_sets_extremal_search,
    audit_sum_free_schnirelmann_density,
    bose_chowla_sidon_set,
    compile_extremal_constructive_certificates_lean,
    doubling_constant,
    erdos_turan_sidon_upper_bound,
    extract_bsg_popular_difference_subset,
    generate_additive_combinatorics_lean_code,
    generate_additive_energy_theorems_lean_code,
    generate_additive_tactic_theorems_lean_code,
    generate_erdos_turan_bases_theorems_lean_code,
    generate_extremal_sidon_certificates,
    generate_sidon_sets_theorems_lean_code,
    generate_sum_free_theorems_lean_code,
    is_b2g_set,
    is_finite_additive_basis_of_order_2,
    is_sidon_set,
    is_sum_free,
    iterated_sum_diff_set,
    mian_chowla_sequence,
    minkowski_diff,
    minkowski_sum,
    representation_count,
    representation_profile,
    ruzsa_sidon_construction,
    schnirelmann_density,
    search_extremal_sidon_set,
    search_extremal_sum_free_subset,
    search_minimal_additive_basis_order_2,
    singer_difference_set,
    verify_additive_combinatorics_baseline_soundness,
    verify_additive_energy_soundness,
    verify_additive_norm_soundness,
    verify_cauchy_schwarz_additive_bound,
    verify_erdos_turan_bases_soundness,
    verify_extremal_constructive_certificates_baseline_soundness,
    verify_minkowski_monotonicity_and_algebra,
    verify_plunnecke_ruzsa_bound,
    verify_schnirelmann_mann_inequality,
    verify_sidon_difference_property,
    verify_sidon_sets_soundness,
    verify_sum_free_density_soundness,
)
from evobyte.formal_bridge import (
    audit_additive_combinatorics_grand_campaign,
    verify_additive_combinatorics_grand_campaign_soundness,
)
from evobyte.statistical import (
    evaluate_additive_blind_confirmation,
    generate_additive_blind_partition,
    verify_additive_blind_confirmation_soundness,
)
from evobyte.verifier import is_lean_available

needs_lean = pytest.mark.skipif(not is_lean_available(), reason="requires Lean 4 toolchain")


def test_is_sidon_set():
    assert is_sidon_set([]) is True
    assert is_sidon_set([1]) is True
    assert is_sidon_set([1, 2]) is True
    assert is_sidon_set([1, 2, 4]) is True
    assert is_sidon_set([1, 2, 5, 10]) is True
    assert is_sidon_set([1, 3, 7, 12, 20]) is True

    # Non-Sidon sets
    assert is_sidon_set([1, 2, 3, 4]) is False  # 1+4 = 2+3 = 5
    assert is_sidon_set([1, 3, 4, 6]) is False  # 1+6 = 3+4 = 7


def test_is_b2g_set():
    assert is_b2g_set([1, 2, 4], g=1) is True
    assert is_b2g_set([1, 2, 3, 4], g=1) is False
    assert is_b2g_set([1, 2, 3, 4], g=2) is True
    assert is_b2g_set([1, 2, 3, 4], g=0) is False


def test_mian_chowla_sequence():
    seq = mian_chowla_sequence(8)
    assert len(seq) == 8
    assert seq == [1, 2, 4, 8, 13, 21, 31, 45]
    assert is_sidon_set(seq) is True


def test_ruzsa_sidon_construction():
    s5 = ruzsa_sidon_construction(5)
    assert len(s5) == 4
    assert is_sidon_set(s5) is True

    s7 = ruzsa_sidon_construction(7)
    assert len(s7) == 6
    assert is_sidon_set(s7) is True


def test_singer_difference_set():
    s2 = singer_difference_set(2)
    assert is_sidon_set(s2) is True
    s3 = singer_difference_set(3)
    assert is_sidon_set(s3) is True


def test_minkowski_sum_and_diff():
    a = [1, 2]
    b = [10, 20]
    assert minkowski_sum(a, b) == [11, 12, 21, 22]
    assert minkowski_diff(a, b) == [-19, -18, -9, -8]


def test_additive_energy():
    # For Sidon set of size k, pairwise sums are distinct, so energy is 2*k^2 - k
    s = [1, 2, 4]  # size 3
    # 2*(3^2) - 3 = 18 - 3 = 15
    assert additive_energy(s) == 15

    s4 = [1, 2, 4, 8]  # size 4
    # 2*(4^2) - 4 = 32 - 4 = 28
    assert additive_energy(s4) == 28


def test_doubling_constant():
    a = [1, 2, 3]
    # A+A = {2, 3, 4, 5, 6}, len=5
    assert doubling_constant(a) == pytest.approx(5 / 3)


def test_is_sum_free():
    assert is_sum_free([1, 3, 5, 7]) is True
    assert is_sum_free([1, 2, 3]) is False  # 1+2 = 3
    assert is_sum_free([5, 6, 7, 8, 9]) is True  # elements in (N/2, N] are sum-free


def test_representation_count():
    a = [1, 2, 4]
    assert representation_count(a, 3) == 1  # 1 + 2
    assert representation_count(a, 5) == 1  # 1 + 4
    assert representation_count(a, 2) == 1  # 1 + 1
    assert representation_count(a, 7) == 0


def test_audit_additive_combinatorics_baseline():
    res = audit_additive_combinatorics_baseline(verify_lake=False)
    assert res["module"] == "AdditiveCombinatoricsSignatures"
    assert res["total_theorems"] >= 50
    assert res["has_sorry"] is False
    assert len(res["sha256"]) == 64

    # Soundness verification with mocked lake_passed=True
    res_copy = dict(res, lake_passed=True)
    sound, findings = verify_additive_combinatorics_baseline_soundness(res_copy, min_theorems=50)
    assert sound is True
    assert len(findings) == 0


def test_verify_additive_combinatorics_baseline_soundness_rejections():
    bad_summary_1 = {
        "has_sorry": True,
        "total_theorems": 100,
        "lake_passed": True,
        "sha256": "a" * 64,
    }
    sound_1, f_1 = verify_additive_combinatorics_baseline_soundness(bad_summary_1)
    assert sound_1 is False
    assert any("SORRY_DETECTED" in f for f in f_1)

    bad_summary_2 = {
        "has_sorry": False,
        "total_theorems": 10,
        "lake_passed": True,
        "sha256": "a" * 64,
    }
    sound_2, f_2 = verify_additive_combinatorics_baseline_soundness(bad_summary_2, min_theorems=50)
    assert sound_2 is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in f_2)

    bad_summary_3 = {
        "has_sorry": False,
        "total_theorems": 100,
        "lake_passed": False,
        "lake_reasons": ["error"],
        "sha256": "a" * 64,
    }
    sound_3, f_3 = verify_additive_combinatorics_baseline_soundness(bad_summary_3)
    assert sound_3 is False
    assert any("LAKE_BUILD_FAILED" in f for f in f_3)


def test_p113_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P113 configuration"):
        run_p113_additive_combinatorics_baseline_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p113_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P113",
        "min_theorems": 50,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/AdditiveCombinatoricsSignatures.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p113-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p113-out.json"

    report = run_p113_additive_combinatorics_baseline_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P113"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 50
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


def test_code_generation():
    assert DEFAULT_LEAN_FILE.name == "AdditiveCombinatoricsSignatures.lean"
    code = generate_additive_combinatorics_lean_code()
    assert "namespace EvoByte.AdditiveCombinatorics" in code
    assert "def PairwiseNonCollision" in code
    assert "sorry" not in code


# ==============================================================================
# P114 TESTS: SIDON SETS EXTREMAL SEARCH & DIFFERENCE NON-COLLISION
# ==============================================================================


def test_verify_sidon_difference_property():
    assert verify_sidon_difference_property([]) is True
    assert verify_sidon_difference_property([1]) is True
    assert verify_sidon_difference_property([1, 2, 5, 7]) is True
    assert verify_sidon_difference_property([1, 2, 5, 10, 12]) is True
    assert verify_sidon_difference_property([1, 2, 3, 4]) is False


def test_bose_chowla_and_extremal_sidon_search():
    for q in (2, 3, 5, 7):
        bc = bose_chowla_sidon_set(q)
        assert len(bc) == q
        assert is_sidon_set(bc) is True
        assert verify_sidon_difference_property(bc) is True

    res7 = search_extremal_sidon_set(7, time_budget_sec=0.1)
    assert res7["cardinality"] == 4
    assert res7["is_sidon"] is True
    assert res7["diff_property_holds"] is True
    assert res7["cardinality"] <= erdos_turan_sidon_upper_bound(7)

    res12 = search_extremal_sidon_set(12, time_budget_sec=0.1)
    assert res12["cardinality"] == 5
    assert res12["is_sidon"] is True
    assert res12["diff_property_holds"] is True
    assert res12["additive_energy"] == 2 * 25 - 5


def test_p114_sidon_sets_theorems_generation_and_soundness():
    assert DEFAULT_SIDON_THEOREMS_LEAN_FILE.name == "SidonSetsTheorems.lean"
    code = generate_sidon_sets_theorems_lean_code()
    assert "import Generated.AdditiveCombinatoricsSignatures" in code
    assert "theorem sidon_diff_to_sum_eq" in code
    assert "sorry" not in code

    summary = audit_sidon_sets_extremal_search(verify_lake=False)
    assert summary["module"] == "SidonSetsTheorems"
    assert summary["total_theorems"] >= 60
    assert summary["has_sorry"] is False
    ok, findings = verify_sidon_sets_soundness(dict(summary, lake_passed=True), min_theorems=60)
    assert ok is True
    assert findings == []


def test_p114_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p114.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P114 configuration"):
        run_p114_sidon_sets_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p114_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P114",
        "min_theorems": 60,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/SidonSetsTheorems.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p114-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p114-out.json"

    report = run_p114_sidon_sets_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P114"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


# ==============================================================================
# P115 TESTS: ADDITIVE ENERGY, PLÜNNECKE-RUZSA & BALOG-SZEMERÉDI-GOWERS
# ==============================================================================


def test_cauchy_schwarz_and_plunnecke_ruzsa_bounds():
    for sample in ([1, 2, 3, 4], [1, 2, 5, 7], [1, 2, 4, 8], [1, 2, 3, 7, 8, 9]):
        cs = verify_cauchy_schwarz_additive_bound(sample)
        assert cs["cauchy_schwarz_holds"] is True
        assert cs["lhs_sum"] >= cs["rhs"]
        assert cs["lhs_diff"] >= cs["rhs"]

        pr = verify_plunnecke_ruzsa_bound(sample, k_plus=2, l_minus=1)
        assert pr["plunnecke_ruzsa_holds"] is True
        assert pr["lhs_cleared"] <= pr["rhs_cleared"]

        bsg = extract_bsg_popular_difference_subset(sample)
        assert bsg["energy_upper_bound_holds"] is True
        assert 1 <= bsg["subset_size"] <= len(sample)

    iter_ap = iterated_sum_diff_set([1, 2, 3], k_plus=2, l_minus=1)
    assert min(iter_ap) == 1 + 1 - 3
    assert max(iter_ap) == 3 + 3 - 1


def test_p115_additive_energy_theorems_generation_and_soundness():
    assert DEFAULT_ADDITIVE_ENERGY_LEAN_FILE.name == "AdditiveEnergyTheorems.lean"
    code = generate_additive_energy_theorems_lean_code()
    assert "import Generated.SidonSetsTheorems" in code
    assert "theorem additive_cauchy_schwarz_mono" in code
    assert "sorry" not in code

    summary = audit_additive_energy_balog_szemeredi(verify_lake=False)
    assert summary["module"] == "AdditiveEnergyTheorems"
    assert summary["total_theorems"] >= 60
    assert summary["has_sorry"] is False
    ok, findings = verify_additive_energy_soundness(
        dict(summary, lake_passed=True), min_theorems=60
    )
    assert ok is True
    assert findings == []


def test_p115_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p115.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P115 configuration"):
        run_p115_additive_energy_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p115_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P115",
        "min_theorems": 60,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/AdditiveEnergyTheorems.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p115-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p115-out.json"

    report = run_p115_additive_energy_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P115"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


# ==============================================================================
# P116 TESTS: CUSTOM METATACTIC `additive_norm` & MINKOWSKI NORMALIZATION
# ==============================================================================


def test_verify_minkowski_monotonicity_and_algebra():
    ver = verify_minkowski_monotonicity_and_algebra([1, 2, 5, 7], [1, 2, 5, 7, 11], [2, 4])
    assert ver["commutativity_holds"] is True
    assert ver["associativity_holds"] is True
    assert ver["inclusion_monotonicity_holds"] is True
    assert ver["translation_cancellation_holds"] is True
    assert ver["freiman_bounds_hold"] is True
    assert ver["all_laws_hold"] is True


def test_p116_additive_norm_generation_and_soundness():
    assert DEFAULT_ADDITIVE_TACTIC_LEAN_FILE.name == "AdditiveTacticTheorems.lean"
    code = generate_additive_tactic_theorems_lean_code()
    assert 'syntax "additive_norm" : tactic' in code
    assert "theorem minkowski_elem_comm" in code
    assert "sorry" not in code

    summary = audit_additive_norm_metatactic(verify_lake=False)
    assert summary["module"] == "AdditiveTacticTheorems"
    assert summary["total_theorems"] >= 60
    assert summary["has_tactic_syntax"] is True
    assert summary["tactic_invocations"] >= 60
    assert summary["has_sorry"] is False
    ok, findings = verify_additive_norm_soundness(dict(summary, lake_passed=True), min_theorems=60)
    assert ok is True
    assert findings == []


def test_p116_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p116.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P116 configuration"):
        run_p116_additive_norm_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p116_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P116",
        "min_theorems": 60,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/AdditiveTacticTheorems.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p116-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p116-out.json"

    report = run_p116_additive_norm_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P116"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_tactic_syntax"] is True
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


# ==============================================================================
# P117 TESTS: ERDŐS-TURÁN ADDITIVE BASES & REPRESENTATION MULTIPLICITY
# ==============================================================================


def test_erdos_turan_additive_bases_and_profile():
    assert is_finite_additive_basis_of_order_2([0, 1, 3, 4], 6) is True
    assert is_finite_additive_basis_of_order_2([0, 1, 4], 6) is False

    for n_val in (6, 10, 16):
        res = search_minimal_additive_basis_order_2(n_val, time_budget_sec=0.05)
        prof = res["profile"]
        assert prof["is_basis"] is True
        assert prof["rohrbach_bound_holds"] is True
        assert prof["pigeonhole_multiplicity_holds"] is True
        assert representation_profile(res["best_basis"], n_val)["is_basis"] is True


def test_p117_erdos_turan_bases_generation_and_soundness():
    assert DEFAULT_ERDOS_TURAN_BASES_LEAN_FILE.name == "ErdosTuranBasesTheorems.lean"
    code = generate_erdos_turan_bases_theorems_lean_code()
    assert "import Generated.AdditiveTacticTheorems" in code
    assert "theorem rohrbach_pair_capacity" in code
    assert "sorry" not in code

    summary = audit_erdos_turan_additive_bases(verify_lake=False)
    assert summary["module"] == "ErdosTuranBasesTheorems"
    assert summary["total_theorems"] >= 60
    assert summary["has_sorry"] is False
    ok, findings = verify_erdos_turan_bases_soundness(
        dict(summary, lake_passed=True), min_theorems=60
    )
    assert ok is True
    assert findings == []


def test_p117_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p117.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P117 configuration"):
        run_p117_erdos_turan_bases_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p117_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P117",
        "min_theorems": 60,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/ErdosTuranBasesTheorems.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p117-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p117-out.json"

    report = run_p117_erdos_turan_bases_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P117"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


# ==============================================================================
# P118 TESTS: SUM-FREE SETS & SCHNIRELMANN-MANN DENSITY
# ==============================================================================


def test_sum_free_extremal_and_schnirelmann_mann_density():
    for n_val in (9, 15, 24):
        sf = search_extremal_sum_free_subset(n_val, dilation=4)
        assert sf["is_sum_free"] is True
        assert sf["dilation_invariant"] is True
        assert sf["erdos_third_bound_holds"] is True
        assert sf["cardinality"] == (n_val + 1) // 2

    assert schnirelmann_density([1, 3, 5, 7, 9], 10) == pytest.approx(0.5)
    mann = verify_schnirelmann_mann_inequality([1, 3, 5, 7, 9], [1, 3, 5, 7, 9], 10)
    assert mann["schnirelmann_holds"] is True
    assert mann["mann_holds"] is True
    assert mann["sigma_sum"] == pytest.approx(1.0)


def test_p118_sum_free_theorems_generation_and_soundness():
    assert DEFAULT_SUM_FREE_THEOREMS_LEAN_FILE.name == "SumFreeTheorems.lean"
    code = generate_sum_free_theorems_lean_code()
    assert "import Generated.ErdosTuranBasesTheorems" in code
    assert "theorem sum_free_dilation_invariance" in code
    assert "sorry" not in code

    summary = audit_sum_free_schnirelmann_density(verify_lake=False)
    assert summary["module"] == "SumFreeTheorems"
    assert summary["total_theorems"] >= 60
    assert summary["has_sorry"] is False
    ok, findings = verify_sum_free_density_soundness(
        dict(summary, lake_passed=True), min_theorems=60
    )
    assert ok is True
    assert findings == []


def test_p118_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p118.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P118 configuration"):
        run_p118_sum_free_density_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p118_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P118",
        "min_theorems": 60,
        "project_dir": "lean_proofs",
        "lean_file": "lean_proofs/Generated/SumFreeTheorems.lean",
        "allow_dirty": True,
        "require_clean_tree": False,
        "seed": 42,
    }
    cfg_p = tmp_path / "p118-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p118-out.json"

    report = run_p118_sum_free_density_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P118"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] >= 60
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


# ==============================================================================
# P119 TESTS: ADDITIVE COMBINATORICS BLIND CONFIRMATION (FWER HOLM-BONFERRONI)
# ==============================================================================


def test_p119_additive_blind_partition_and_fwer_evaluation():
    part = generate_additive_blind_partition(seed=119, count_per_track=25, alpha=0.01)
    assert part["split_id"] == "p119-additive-blind-partition-v1"
    assert part["total_instances"] == 100
    assert part["zero_leakage_verified"] is True
    assert len(part["checksum"]) == 64

    eval_res = evaluate_additive_blind_confirmation(part, alpha=0.01)
    assert eval_res["phase"] == "P119"
    assert eval_res["total_instances"] == 100
    assert eval_res["total_wins"] == 100
    assert eval_res["total_losses"] == 0
    assert eval_res["fwer_controlled"] is True
    assert eval_res["max_holm_p_value"] < 0.01
    assert eval_res["all_confirmed"] is True

    sound, findings = verify_additive_blind_confirmation_soundness(eval_res)
    assert sound is True
    assert findings == []

    # Verify leakage detection
    contaminated = generate_additive_blind_partition(
        seed=119, count_per_track=5, dev_pool={"P119_SID_01"}, alpha=0.01
    )
    assert contaminated["leakage_detected"] is True
    assert contaminated["zero_leakage_verified"] is False


def test_p119_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p119.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P119 configuration"):
        run_p119_additive_blind_confirmation_audit(cfg_p, tmp_path / "out.json")


def test_p119_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P119",
        "acceptance_phase": "P119",
        "seed": 119,
        "device": "cpu",
        "alpha": 0.01,
        "count_per_track": 25,
        "min_total_instances": 100,
        "min_wins": 80,
        "split_path": "experiments/p119-blind-split.json",
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p119-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p119-out.json"

    report = run_p119_additive_blind_confirmation_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P119"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_instances"] == 100
    assert report["total_wins"] == 100
    assert report["fwer_controlled"] is True


# ==============================================================================
# P120 TESTS: ADDITIVE COMBINATORICS GRAND CAMPAIGN & CERTIFIED DOSSIER
# ==============================================================================


def test_p120_additive_grand_campaign_and_hash_chain():
    summary = audit_additive_combinatorics_grand_campaign(verify_lake=False)
    assert summary["total_modules"] == 32
    assert summary["total_theorems"] == 2392
    assert summary["additive_theorems"] == 463
    assert summary["has_sorry"] is False
    assert (
        summary["final_chain_hash"]
        == "8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3"
    )
    ok, findings = verify_additive_combinatorics_grand_campaign_soundness(
        dict(summary, lake_passed=True), min_theorems=2000, min_modules=32
    )
    assert ok is True
    assert findings == []


def test_p120_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p120.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P120 configuration"):
        run_p120_additive_grand_campaign_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p120_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P120",
        "seed": 42,
        "device": "cpu",
        "project_dir": "lean_proofs",
        "generated_dir": "lean_proofs/Generated",
        "min_theorems": 2000,
        "min_modules": 32,
        "expected_chain_hash": "8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3",
        "dossier_path": "docs/research/p120-additive-combinatorics-dossier.md",
        "verify_lake": True,
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p120-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p120-out.json"

    report = run_p120_additive_grand_campaign_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P120"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_modules"] == 32
    assert report["total_theorems"] == 2392
    assert report["additive_theorems"] == 463
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True


def test_p149_sidon_generator_and_certificates():
    certs_data = generate_extremal_sidon_certificates()
    assert certs_data["total_certificates"] == 50
    assert certs_data["all_valid"] is True
    assert (
        certs_data["checksum"] == "b95c5d8541c08cce8f646de35bf05febf42d280369b39962c64254bf56d19a64"
    )
    families = {c["family"] for c in certs_data["certificates"]}
    assert {"ruzsa", "mian_chowla", "singer", "bnb_dense"} <= families
    for c in certs_data["certificates"]:
        assert c["is_sidon"] is True
        assert c["max_element"] <= 2000


def test_p149_constructive_soundness():
    audit_data = audit_extremal_constructive_certificates_baseline(verify_lake=False)
    assert audit_data["total_theorems"] == 114
    assert audit_data["has_sorry"] is False
    assert audit_data["certificates_summary"]["all_valid"] is True

    valid, findings = verify_extremal_constructive_certificates_baseline_soundness(audit_data)
    assert valid is True
    assert findings == []

    # Test tampering detection on sorry
    corrupted_sorry = dict(audit_data, has_sorry=True)
    valid, findings = verify_extremal_constructive_certificates_baseline_soundness(corrupted_sorry)
    assert valid is False
    assert any("SORRY_DETECTED" in f for f in findings)

    # Test tampering detection on invalid certificates
    corrupted_certs = dict(audit_data, certificates_summary={"all_valid": False})
    valid, findings = verify_extremal_constructive_certificates_baseline_soundness(corrupted_certs)
    assert valid is False
    assert any("INVALID_SIDON_CERTIFICATES" in f for f in findings)

    # Test insufficient theorems
    corrupted_thms = dict(audit_data, total_theorems=10)
    valid, findings = verify_extremal_constructive_certificates_baseline_soundness(corrupted_thms)
    assert valid is False
    assert any("INSUFFICIENT_THEOREMS" in f for f in findings)


def test_p149_acceptance_rejects_wrong_phase(tmp_path: Path):
    cfg_p = tmp_path / "bad-p149-cfg.json"
    cfg_p.write_text(json.dumps({"phase": "INVALID"}))
    with pytest.raises(ValueError, match="not a P149 configuration"):
        run_p149_constructive_certificates_audit(cfg_p, tmp_path / "out.json")


@needs_lean
def test_p149_audit_smoke(tmp_path: Path):
    cfg = {
        "phase": "P149",
        "seed": 42,
        "device": "cpu",
        "project_dir": "lean_proofs",
        "generated_dir": "lean_proofs/Generated",
        "min_theorems": 100,
        "verify_lake": True,
        "allow_dirty": True,
        "require_clean_tree": False,
    }
    cfg_p = tmp_path / "p149-smoke-config.json"
    cfg_p.write_text(json.dumps(cfg))
    out_p = tmp_path / "p149-out.json"

    report = run_p149_constructive_certificates_audit(cfg_p, out_p)
    assert out_p.exists()
    assert report["phase"] == "P149"
    assert report["verdict"] == "ACCEPTED"
    assert report["total_theorems"] == 114
    assert report["has_sorry"] is False
    assert report["lake_passed"] is True
