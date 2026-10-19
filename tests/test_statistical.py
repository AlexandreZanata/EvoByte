"""Unit and integration tests for P111 statistical selection control and multi-problem blind confirmation."""

from __future__ import annotations

from evobyte.statistical import (
    compute_holm_bonferroni,
    evaluate_multiproblem_blind_confirmation,
    generate_multiproblem_blind_partition,
    verify_multiproblem_confirmation_soundness,
)


def test_compute_holm_bonferroni():
    # Synthetic p-values: 3 hypotheses
    raw_p = {
        "H1": 0.001,
        "H2": 0.004,
        "H3": 0.02,
    }
    res = compute_holm_bonferroni(raw_p, alpha=0.01)
    assert res["m_hypotheses"] == 3
    assert res["ordered_tracks"] == ["H1", "H2", "H3"]
    # H1 factor=3 -> 0.003 < 0.01
    # H2 factor=2 -> 0.008 < 0.01
    # H3 factor=1 -> 0.02 >= 0.01
    assert "H1" in res["significant_tracks"]
    assert "H2" in res["significant_tracks"]
    assert "H3" not in res["significant_tracks"]
    assert res["fwer_controlled"] is False

    # All significant
    raw_p_all = {"H1": 1e-5, "H2": 2e-5, "H3": 1e-4}
    res_all = compute_holm_bonferroni(raw_p_all, alpha=0.01)
    assert res_all["all_significant"] is True
    assert res_all["fwer_controlled"] is True


def test_generate_multiproblem_blind_partition():
    dev_pool = {"DEV_01", "DEV_02", "P105_001"}
    part = generate_multiproblem_blind_partition(seed=42, count_per_track=25, dev_pool=dev_pool)
    assert part["total_instances"] == 100
    assert part["count_per_track"] == 25
    assert len(part["tracks"]) == 4
    assert set(part["tracks"].keys()) == {"erdos_graham", "pillai", "schinzel", "giuga"}
    assert part["leakage_detected"] is False
    assert part["zero_leakage_verified"] is True
    assert len(part["checksum"]) == 64

    # Test leakage detection
    leaky_pool = {"P111_EG_01"}
    part_leaky = generate_multiproblem_blind_partition(
        seed=42, count_per_track=25, dev_pool=leaky_pool
    )
    assert part_leaky["leakage_detected"] is True
    assert part_leaky["zero_leakage_verified"] is False


def test_evaluate_multiproblem_blind_confirmation():
    part = generate_multiproblem_blind_partition(seed=42, count_per_track=25)
    eval_res = evaluate_multiproblem_blind_confirmation(part, alpha=0.01)

    assert eval_res["total_instances"] == 100
    assert eval_res["total_wins"] >= 95
    assert eval_res["all_verified"] is True
    assert eval_res["fwer_controlled"] is True
    assert eval_res["max_holm_p_value"] < 0.01

    for t_info in eval_res["tracks"].values():
        assert t_info["outcome"] == "CONFIRMED"
        assert t_info["wins"] >= 20
        assert t_info["all_verified"] is True
        assert t_info["holm_adjusted_p_value"] < 0.01


def test_verify_multiproblem_confirmation_soundness():
    part = generate_multiproblem_blind_partition(seed=42, count_per_track=25)
    eval_res = evaluate_multiproblem_blind_confirmation(part, alpha=0.01)

    sound, findings = verify_multiproblem_confirmation_soundness(
        eval_res,
        min_total_instances=100,
        min_wins=80,
        alpha=0.01,
    )
    assert sound is True
    assert len(findings) == 0

    # Test rejection on leakage
    leaky_res = dict(eval_res)
    leaky_res["leakage_detected"] = True
    sound_leaky, findings_leaky = verify_multiproblem_confirmation_soundness(leaky_res)
    assert sound_leaky is False
    assert any("LEAKAGE" in f for f in findings_leaky)
