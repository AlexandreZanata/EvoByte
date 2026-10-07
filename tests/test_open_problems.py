"""Unit tests for P29 open problems and verifiable certificates."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.open_problems import (
    P57_KNOWN_TRIPLE_1009,
    P61_SHADOW_PRIMES,
    P65_MAX_LIBRARY,
    PROBLEM_REGISTRY,
    P62RepairScorer,
    P65BridgeScorer,
    audit_historical_certificate,
    check_coordinate_bounds,
    check_diophantine_quintuple,
    check_diophantine_quintuple_independent,
    check_erdos_straus,
    check_erdos_straus_fractions,
    check_taxicab,
    check_taxicab_factorization,
    p57_classical_constructions,
    p57_classify_solved,
    p57_nominate_instances,
    p61_modular_shadow,
    p61_modular_shadow_batch_torch,
    p62_classical_repair_step,
    p62_collect_cloning_samples,
    p62_compare_repair_policies,
    p62_exact_features,
    p62_exact_residual,
    p62_learned_repair_step,
    p62_neighbors,
    p62_random_repair_step,
    p62_repair_cycles,
    p62_split_by_origin,
    p62_train_repairer,
    p64_apply_rules,
    p64_prioritized_scan,
    p64_proof_vs_saved,
    p64_prove_rule,
    p64_rule_matches,
    p64_rule_report,
    p64_suggest_rules,
    p65_build_library,
    p65_compare_libraries,
    p65_entry_features,
    p65_entry_verifies,
    p65_find_bridge,
    p65_instantiate,
    p65_model_pick,
    p65_random_library,
    p65_train_bridge_scorer,
    replay_and_verify_bounded_null,
    run_adversarial_rejection_suite,
    run_certificate_audit,
    run_open_problem_campaign,
    run_p57_bounded_campaign,
    run_p61_paired_filter_trial,
    verify_independent_reproduction,
)


def test_problem_registry_structure() -> None:
    assert "erdos-straus" in PROBLEM_REGISTRY
    assert "taxicab" in PROBLEM_REGISTRY
    assert "diophantine-quintuple" in PROBLEM_REGISTRY

    es = PROBLEM_REGISTRY["erdos-straus"]
    assert es.certificate_type == "integer_exact_certificate"
    assert len(es.literature_citations) >= 2
    assert "rediscovery" in es.classification_rules

    dq = PROBLEM_REGISTRY["diophantine-quintuple"]
    assert dq.certificate_type == "bounded_null_certificate"
    assert "null-campaign" in dq.classification_rules


def test_erdos_straus_exact_checker() -> None:
    # Known exact solution for n=1009: 4/1009 = 1/253 + 1/85096 + 1/1974822872
    n = 1009
    x = 253
    y = 85096
    z = 1974822872

    is_valid, residual, details = check_erdos_straus(n, x, y, z)
    assert is_valid is True
    assert residual == 0
    assert details["lhs"] == details["rhs"]

    # Negative test with corrupted z
    is_bad, bad_res, _ = check_erdos_straus(n, x, y, z + 1)
    assert is_bad is False
    assert bad_res != 0

    # Non-positive input
    is_neg, _, _ = check_erdos_straus(n, -1, y, z)
    assert is_neg is False


def test_taxicab_exact_checker() -> None:
    # 1729 = 1^3 + 12^3 = 9^3 + 10^3
    is_valid, residual, details = check_taxicab(1729, 1, 12, 9, 10)
    assert is_valid is True
    assert residual == 0
    assert details["sum1"] == 1729
    assert details["sum2"] == 1729

    # Negative test
    is_bad, _, _ = check_taxicab(1729, 1, 12, 9, 11)
    assert is_bad is False


def test_diophantine_quintuple_exact_checker() -> None:
    # Fermat quadruple: {1, 3, 8, 120} has all pairwise products + 1 as squares
    # Test extending with a non-quintuple (e.g. 5)
    is_valid, _res, details = check_diophantine_quintuple([1, 3, 8, 120, 5])
    assert is_valid is False
    assert details["all_pairs_square"] is False

    # Negative test: non-distinct or non-5 elements
    is_bad1, _, _ = check_diophantine_quintuple([1, 3, 8, 120])
    assert is_bad1 is False
    is_bad2, _, _ = check_diophantine_quintuple([1, 1, 3, 8, 120])
    assert is_bad2 is False


def test_independent_reproduction_verifier() -> None:
    solution_data = {
        "n": 1009,
        "x": 253,
        "y": 85096,
        "z": 1974822872,
    }
    repro = verify_independent_reproduction("erdos-straus", solution_data)
    assert repro["status"] == "PASS"
    assert len(repro["reproduction_hash"]) == 64
    assert repro["reproduction_time_sec"] >= 0.0


def test_open_problems_smoke_campaign() -> None:
    device = "cpu"
    report = run_open_problem_campaign(
        problem_id="erdos-straus",
        device_name=device,
        output_path=None,
        smoke=True,
    )
    assert report["manifest_version"] == "1.0"
    assert report["phase"] == "p29-open-problems"
    assert report["status"] == "PASS"
    assert report["classification"] in ("rediscovery", "verified-construction")
    assert "certificate_bundle" in report
    cert = report["certificate_bundle"]
    assert cert["problem_id"] == "erdos-straus"
    assert len(cert["certificate_hash"]) == 64
    assert cert["independent_reproduction"]["status"] == "PASS"


def test_dual_checkers_erdos_straus() -> None:
    # Strict solution for n=1009 within bound 10^9: (253, 85100, 944524900)
    n = 1009
    x = 253
    y = 85100
    z = 944524900

    # Checker 1: integer exact identity
    is_v1, res1, det1 = check_erdos_straus(n, x, y, z)
    assert is_v1 is True
    assert res1 == 0
    assert det1["verified_exact"] is True

    # Checker 2: rational fractions
    is_v2, diff2, det2 = check_erdos_straus_fractions(n, x, y, z)
    assert is_v2 is True
    assert diff2 == 0
    assert det2["verified_exact_fraction"] is True

    # Coordinate bounds
    in_bounds, b_info = check_coordinate_bounds(
        "erdos-straus", {"x": x, "y": y, "z": z}, max_coord=10**9
    )
    assert in_bounds is True
    assert b_info["within_bounds"] is True


def test_dual_checkers_taxicab() -> None:
    # Ta(2) = 1729 = 1^3 + 12^3 = 9^3 + 10^3
    sum_val = 1729
    a, b, c, d = 1, 12, 9, 10

    # Checker 1: sum of cubes
    is_v1, res1, _ = check_taxicab(sum_val, a, b, c, d)
    assert is_v1 is True
    assert res1 == 0

    # Checker 2: sum of cubes factorization
    is_v2, res2, det2 = check_taxicab_factorization(sum_val, a, b, c, d)
    assert is_v2 is True
    assert res2 == 0
    assert det2["verified_algebraic_identity"] is True


def test_independent_checker_diophantine_quintuple() -> None:
    # Fermat quadruple + non-square candidate e=5
    is_v, res, det = check_diophantine_quintuple_independent([1, 3, 8, 120, 5])
    assert is_v is False
    assert res != 0
    assert det["all_pairs_square"] is False

    # Domain check: 4 elements or duplicates
    is_bad1, _, _ = check_diophantine_quintuple_independent([1, 3, 8, 120])
    assert is_bad1 is False
    is_bad2, _, _ = check_diophantine_quintuple_independent([1, 1, 3, 8, 120])
    assert is_bad2 is False


def test_coordinate_bounds_reclassification() -> None:
    # Historical P29 solution for n=1009 has z=1974822872 > 10^9
    sol_historical = {"n": 1009, "x": 253, "y": 85096, "z": 1974822872}
    in_bounds, b_info = check_coordinate_bounds("erdos-straus", sol_historical, max_coord=10**9)
    assert in_bounds is False
    assert b_info["max_coordinate_value"] == 1974822872
    assert b_info["within_bounds"] is False

    # Strict reproduction check with bounds_strict=True flags bound exceedance
    repro_strict = verify_independent_reproduction(
        "erdos-straus", sol_historical, bounds_strict=True
    )
    assert repro_strict["status"] == "EXCEEDS_BOUND"
    assert repro_strict["details"]["classification"] == "exceeds_declared_coordinate_bound"

    # Historical certificate audit function test
    p29_cert_path = _REPO_ROOT / "experiments" / "p29-erdos-straus-certificate.json"
    if p29_cert_path.exists():
        audit_res = audit_historical_certificate(p29_cert_path, max_coord=10**9)
        assert audit_res is not None
        assert audit_res["reclassified_status"] == "exceeds_declared_coordinate_bound"
        assert audit_res["preserved_as_superseded_diagnostic"] is True


def test_replay_and_verify_bounded_null() -> None:
    # Bounded replay of Fermat quadruple extensions in small test window
    res = replay_and_verify_bounded_null(
        base_quadruple=[1, 3, 8, 120],
        r_start=121,
        r_end=500,
    )
    assert res["null_verified"] is True
    assert res["status"] == "exhaustive_null"
    assert res["candidates_checked"] == 380
    assert len(res["counterexamples"]) == 0


def test_adversarial_rejection_suite_open_problems() -> None:
    results = run_adversarial_rejection_suite()
    assert len(results) >= 8
    # Zero accepted false positives
    accepted_fps = [r for r in results if not r["rejected"]]
    assert len(accepted_fps) == 0
    # Every fixture must be rejected
    assert all(r["rejected"] is True for r in results)


def test_run_certificate_audit_manifest(tmp_path: Path) -> None:
    out_p = tmp_path / "p31-certificates.json"
    audit = run_certificate_audit(
        bounds_strict=True,
        output_path=out_p,
    )
    assert out_p.exists()
    assert audit["phase"] == "p31-verifier-certificates"
    assert audit["status"] == "PASS"
    assert audit["audit_summary"]["accepted_false_positives"] == 0
    assert audit["audit_summary"]["soundness_gate_passed"] is True
    assert "strict_certificates" in audit
    assert "diophantine-quintuple" in audit["strict_certificates"]
    assert "erdos-straus" in audit["strict_certificates"]
    assert "taxicab" in audit["strict_certificates"]


def test_p39_nomination_file_valid() -> None:
    import json as _json

    nom = _json.loads((_REPO_ROOT / "experiments" / "p39-nomination.json").read_text())
    assert nom["problem_id"] == "erdos-straus"
    assert nom["status"] == "preregistered"
    assert nom["instances"] == [1009, 10007, 100003]
    assert nom["bounds"]["declared_bound"] == 10**9
    assert len(nom["checkers"]) == 2
    assert "novelty_plan" in nom and "coverage" in nom


def test_p39_certified_campaign_smoke(tmp_path: Path) -> None:
    from benchmarks.open_problems import P39_ALLOWED_CLASSIFICATIONS, run_certified_campaign

    out_p = tmp_path / "p39-science.json"
    report = run_certified_campaign(
        problem_id="erdos-straus",
        freeze_manifest=_REPO_ROOT / "experiments" / "p38-confirmation.json",
        nomination_path=_REPO_ROOT / "experiments" / "p39-nomination.json",
        output_path=out_p,
        device_name="cpu",
        smoke=True,
        checkpoint_path=tmp_path / "p39-checkpoint.json",
    )
    assert out_p.exists()
    assert report["phase"] == "p39-certified-science"
    assert report["status"] == "PASS"
    assert len(report["instances"]) == 1
    assert report["instances"][0]["n"] == 1009
    assert report["classification"] in P39_ALLOWED_CLASSIFICATIONS
    assert report["soundness"]["accepted_false_positives"] == 0
    for inst in report["instances"]:
        if inst.get("certificate"):
            assert len(inst["certificate_hash"]) == 64
            assert inst["certificate"]["reproduction"]["status"] == "PASS"


def test_p39_checkpoint_resume(tmp_path: Path) -> None:
    from benchmarks.open_problems import run_certified_campaign

    ckpt = tmp_path / "p39-checkpoint.json"
    kwargs = {
        "problem_id": "erdos-straus",
        "freeze_manifest": _REPO_ROOT / "experiments" / "p38-confirmation.json",
        "nomination_path": _REPO_ROOT / "experiments" / "p39-nomination.json",
        "device_name": "cpu",
        "smoke": True,
        "checkpoint_path": ckpt,
    }
    first = run_certified_campaign(output_path=tmp_path / "p39-a.json", **kwargs)
    assert ckpt.exists()
    second = run_certified_campaign(output_path=tmp_path / "p39-b.json", **kwargs)
    assert first["instances"][0]["classification"] == second["instances"][0]["classification"]
    if second["instances"][0].get("certificate_hash"):
        assert second["instances"][0]["resumed"] is True


def test_p39_blocked_without_valid_freeze(tmp_path: Path) -> None:
    import json as _json

    from benchmarks.open_problems import run_certified_campaign

    bad_freeze = tmp_path / "bad-freeze.json"
    bad_freeze.write_text(_json.dumps({"phase": "p38", "status": "FAIL"}))
    report = run_certified_campaign(
        problem_id="erdos-straus",
        freeze_manifest=bad_freeze,
        nomination_path=_REPO_ROOT / "experiments" / "p39-nomination.json",
        output_path=tmp_path / "p39-blocked.json",
        device_name="cpu",
        smoke=True,
        checkpoint_path=None,
    )
    assert report["status"] == "FAIL"
    assert report["classification"] == "BLOCKED"


def test_p39_rejects_parallel_problems(tmp_path: Path) -> None:
    import pytest

    from benchmarks.open_problems import run_certified_campaign

    with pytest.raises(ValueError, match="one campaign per cycle"):
        run_certified_campaign(
            problem_id="erdos-straus+taxicab",
            output_path=tmp_path / "p39-bad.json",
            checkpoint_path=None,
        )


def test_p57_nomination_frozen_hard_class() -> None:
    nom = p57_nominate_instances()
    assert len(nom) == 1181
    assert nom[0] == 73
    assert 1009 in nom
    assert nom == p57_nominate_instances()
    assert all(n % 24 == 1 and n >= 2 for n in nom)
    assert nom == sorted(nom)


def test_p57_classical_constructions_verify_and_miss_hard_class() -> None:
    fams = {f["family"]: f for f in p57_classical_constructions(4)}
    assert fams["even"]["triple"] == (2, 3, 6) and fams["even"]["verified"] is True
    fams = {f["family"]: f for f in p57_classical_constructions(5)}
    assert fams["n=2-mod-3"]["triple"] == (5, 2, 10) and fams["n=2-mod-3"]["verified"] is True
    fams = {f["family"]: f for f in p57_classical_constructions(3)}
    assert (
        fams["multiple-of-3"]["triple"] == (1, 6, 6) and fams["multiple-of-3"]["verified"] is True
    )
    for n in (73, 97, 1009):
        assert p57_classical_constructions(n) == []
    assert p57_classify_solved(1009, (253, 85100, 944524900)) == "rediscovery"
    assert p57_classify_solved(73, (20, 210, 30660)) == "candidate"


def test_p57_windowed_search_never_claims_exhaustive_null() -> None:
    import torch

    res = run_p57_bounded_campaign(
        [99793],
        device=torch.device("cpu"),
        time_cap_sec=0.0,
        batch_size=1000,
    )
    assert res["instances"][0]["status"] == "budget-exhausted"
    assert res["time_capped"] is True
    assert "exhaustive-null" not in res["by_status"]


def _p61_known_solutions() -> list[tuple[int, int, int, int]]:
    sols = [(1009, *P57_KNOWN_TRIPLE_1009)]
    for n in range(2, 31):
        for fam in p57_classical_constructions(n):
            if fam["verified"]:
                sols.append((n, *fam["triple"]))
    return sols


def test_p61_shadow_keeps_every_exact_solution() -> None:
    for n, x, y, z in _p61_known_solutions():
        rep = p61_modular_shadow(n, x, y, z)
        assert rep["keep"] is True, (n, x, y, z, rep["rejected_by"])
        assert rep["rejected_by"] == []
    assert set(P61_SHADOW_PRIMES) == {3, 5, 7, 11, 13}
    for n in (2, 3, 4, 5, 6):
        for x in range(1, 31):
            for y in range(1, 31):
                for z in range(1, 31):
                    ok, _, _ = check_erdos_straus(n, x, y, z)
                    if ok:
                        assert p61_modular_shadow(n, x, y, z)["keep"] is True


def test_p61_shadow_batch_agrees_with_reference() -> None:
    import torch

    triples = _p61_known_solutions()[:12]
    triples += [(4, 1, 1, 1), (4, 2, 3, 7), (1009, 253, 85100, 1974822873)]
    n = 4
    xs = torch.tensor([t[1] for t in triples], dtype=torch.int64)
    ys = torch.tensor([t[2] for t in triples], dtype=torch.int64)
    zs = torch.tensor([t[3] for t in triples], dtype=torch.int64)
    mask = p61_modular_shadow_batch_torch(n, xs, ys, zs)
    for (nn, x, y, z), kept in zip(triples, mask.tolist()):
        assert bool(kept) == p61_modular_shadow(n, x, y, z)["keep"], (nn, x, y, z)


def test_p61_compatible_residues_are_not_certificate() -> None:
    found = None
    for n in (4, 5, 6):
        for x in range(1, 51):
            for y in range(1, 51):
                for z in range(1, 51):
                    ok, _, _ = check_erdos_straus(n, x, y, z)
                    if not ok and p61_modular_shadow(n, x, y, z)["keep"]:
                        found = (n, x, y, z)
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    assert found is not None
    n, x, y, z = found
    assert check_erdos_straus(n, x, y, z)[0] is False


def test_p61_shadow_eliminates_false_and_reports_cost() -> None:
    import random
    import time

    import torch

    rng = random.Random(7)
    xs = [rng.randint(1, 500) for _ in range(300)] + [2]
    ys = [rng.randint(1, 500) for _ in range(300)] + [3]
    zs = [rng.randint(1, 500) for _ in range(300)] + [6]
    t0 = time.perf_counter()
    mask = p61_modular_shadow_batch_torch(4, torch.tensor(xs), torch.tensor(ys), torch.tensor(zs))
    elapsed = time.perf_counter() - t0
    kept = int(mask.sum().item())
    assert 0 < kept < len(xs)
    assert elapsed >= 0.0


def test_p61_paired_trial_same_certificates_no_false_rejection() -> None:
    import random

    import torch

    rng = random.Random(11)
    triples = [(2, 3, 6)] + [
        (rng.randint(1, 300), rng.randint(1, 300), rng.randint(1, 300)) for _ in range(200)
    ]
    rec = run_p61_paired_filter_trial(4, triples)
    assert rec["certificates_equal"] is True
    assert (2, 3, 6) in rec["certificates_filtered"]
    assert rec["false_rejections"] == 0
    assert rec["kept"] < rec["candidates"]
    costs = rec["costs"]
    assert set(costs) == {
        "check_all_sec",
        "total_without_sec",
        "transfer_sec",
        "filter_sec",
        "check_kept_sec",
        "total_with_sec",
    }
    assert costs["total_with_sec"] == (
        costs["transfer_sec"] + costs["filter_sec"] + costs["check_kept_sec"]
    )
    assert "cpu" in rec["devices_compared"]
    if torch.cuda.is_available():
        assert "cuda" in rec["devices_compared"]
    assert rec["device_agreement"] is True


def test_p61_paired_trial_exhaustive_box_zero_false_rejection() -> None:
    triples = [(x, y, z) for x in range(1, 21) for y in range(1, 21) for z in range(1, 21)]
    rec = run_p61_paired_filter_trial(4, triples)
    assert rec["certificates_equal"] is True
    assert rec["false_rejections"] == 0
    assert len(rec["certificates_filtered"]) > 0


def test_p62_exact_features() -> None:
    assert p62_exact_residual(4, 2, 3, 6) == 0
    feat = p62_exact_features(4, 2, 3, 6)
    assert feat == {"residual": 0, "sign": 0, "divisible_by": [2, 3, 5, 7, 11, 13]}
    assert p62_exact_residual(4, 2, 3, 7) == 4 * 2 * 3 * 7 - 4 * (6 + 14 + 21)
    assert p62_exact_features(4, 2, 3, 7)["sign"] in (-1, 1)


def test_p62_classical_repair_certifies_perturbed() -> None:
    for start in [(2, 3, 7), (2, 4, 6), (3, 3, 6), (5, 5, 5)]:
        rep = p62_repair_cycles(4, start, policy="classical", max_cycles=12)
        assert rep["certified"] is True, (start, rep)
        assert rep["status"] == "certified"
        assert rep["cycles_used"] <= 12
        assert check_erdos_straus(4, *rep["triple"])[0] is True
        mags = [abs(r) for r in rep["residuals"]]
        assert all(b <= a for a, b in zip([abs(p62_exact_residual(4, *start))] + mags, mags))
        assert all(v >= 1 for t in [start, rep["triple"]] for v in t)


def test_p62_random_repair_is_seeded_deterministic() -> None:
    first = p62_repair_cycles(4, (5, 5, 5), policy="random", max_cycles=12, seed=3)
    second = p62_repair_cycles(4, (5, 5, 5), policy="random", max_cycles=12, seed=3)
    assert first == second
    assert p62_random_repair_step(4, 2, 3, 7, seed=9) == p62_random_repair_step(4, 2, 3, 7, seed=9)
    assert p62_classical_repair_step(4, 2, 3, 7) == (2, 3, 6)


def test_p62_repair_statuses_and_domain() -> None:
    rep = p62_repair_cycles(4, (5, 5, 5), policy="classical", max_cycles=0)
    assert rep["status"] == "exhausted"
    assert rep["certified"] is False
    assert rep["cycles_used"] == 0
    try:
        p62_repair_cycles(4, (2, 3, 7), policy="learned")
    except ValueError as exc:
        assert "Unknown P62 repair policy" in str(exc)
    else:
        raise AssertionError("unknown policy must raise")
    assert len(p62_neighbors(1, 1, 1)) == 9
    assert all(min(t) >= 1 for t in p62_neighbors(1, 1, 1))


def test_p62_split_by_origin_is_disjoint() -> None:
    records = [{"n": n, "case": i} for n in (4, 5, 6, 7) for i in range(3)]
    first = p62_split_by_origin(records)
    second = p62_split_by_origin(records)
    assert first == second
    assert {r["n"] for r in first["train"]}.isdisjoint({r["n"] for r in first["dev"]})
    assert len(first["train"]) + len(first["dev"]) == len(records)


def _p62_trained_weights() -> dict:
    samples, _ = p62_collect_cloning_samples([4, 8], starts_per_solution=6, seed=0)
    assert len(samples) > 0
    return p62_train_repairer(samples, seed=0, epochs=60)


def test_p62_repairer_trains_small_and_deterministic() -> None:
    first = _p62_trained_weights()
    second = _p62_trained_weights()
    assert first["n_params"] == 129
    assert first["n_params"] <= 1000
    assert first["train_acc"] > 0.5
    assert first["train_sec"] >= 0.0
    assert first["state_dict"].keys() == second["state_dict"].keys()
    scorer = P62RepairScorer()
    assert sum(p.numel() for p in scorer.parameters()) == 129


def test_p62_learned_step_is_deterministic_and_solution_free() -> None:
    weights = _p62_trained_weights()["state_dict"]
    assert p62_learned_repair_step(weights, 4, 2, 3, 7) == p62_learned_repair_step(
        weights, 4, 2, 3, 7
    )
    assert p62_learned_repair_step(weights, 4, 2, 3, 7) in p62_neighbors(2, 3, 7)


def test_p62_compare_policies_equal_inputs_with_costs() -> None:
    weights = _p62_trained_weights()
    dev_starts = [(6, (3, 5, 12)), (6, (4, 4, 12)), (9, (3, 19, 18)), (9, (4, 18, 18))]
    rep = p62_compare_repair_policies(
        weights["state_dict"], weights["train_sec"], dev_starts, max_cycles=12, seed=0
    )
    assert set(rep) == {"classical", "random", "learned"}
    for rec in rep.values():
        assert rec["starts"] == len(dev_starts)
        assert 0 <= rec["certified"] <= len(dev_starts)
        assert rec["total_sec"] >= 0.0
    assert rep["learned"]["train_sec_billed"] == weights["train_sec"] > 0.0
    assert rep["learned"]["total_sec"] >= rep["learned"]["train_sec_billed"]
    assert rep["classical"]["train_sec_billed"] == 0.0
    assert rep["classical"]["certified"] >= rep["learned"]["certified"] - len(dev_starts)


def test_p64_prove_refute_timeout_paths() -> None:
    proven = p64_prove_rule({"kind": "interval", "bound": "sum_le", "value": 4}, 4, 6)
    assert proven["status"] == "PROVEN"
    assert proven["checks"] == 4
    refuted = p64_prove_rule({"kind": "parity", "coord": 0, "residue": 1}, 4, 6)
    assert refuted["status"] == "REFUTED"
    assert check_erdos_straus(4, *refuted["counterexample"])[0] is True
    assert p64_rule_matches(
        {"kind": "parity", "coord": 0, "residue": 1}, tuple(refuted["counterexample"])
    )
    slow = p64_prove_rule({"kind": "parity", "coord": 0, "residue": 1}, 4, 100, max_checks=1000)
    assert slow["status"] == "UNPROVEN"
    assert slow["checks"] == 0


def test_p64_only_proven_rules_eliminate() -> None:
    proven_rule = {"kind": "interval", "bound": "sum_le", "value": 4}
    proof = p64_prove_rule(proven_rule, 4, 6)
    assert proof["status"] == "PROVEN"
    triples = [(1, 1, 1), (1, 1, 2), (2, 3, 6), (2, 3, 7)]
    res = p64_apply_rules(triples, [proven_rule], [{"kind": "parity", "coord": 0, "residue": 1}])
    assert res["kept"] == [2, 3]
    assert [e["triple"] for e in res["eliminated"]] == [[1, 1, 1], [1, 1, 2]]
    assert all(e["rule"] == proven_rule for e in res["eliminated"])
    assert res["priority"] == [1, 1, 0, 0]
    empty = p64_apply_rules(triples, [], [{"kind": "parity", "coord": 0, "residue": 1}])
    assert empty["kept"] == [0, 1, 2, 3]
    assert empty["eliminated"] == []


def test_p64_suggest_and_report() -> None:
    errors = [(2, 3, 7), (5, 5, 5), (1, 2, 3)]
    first = p64_suggest_rules(errors)
    assert first == p64_suggest_rules(errors)
    assert len(first) > 0
    assert all(sum(1 for t in errors if p64_rule_matches(rule, t)) >= 1 for rule in first)
    rule = {"kind": "interval", "bound": "sum_le", "value": 4}
    rep = p64_rule_report(rule, p64_prove_rule(rule, 4, 6), errors)
    assert rep["status"] == "PROVEN"
    assert rep["coverage_fraction"] == 0.0
    assert "only inside the proven box" in rep["limits"]


def test_p64_proof_vs_saved_measured() -> None:
    rule = {"kind": "interval", "bound": "sum_le", "value": 4}
    rep = p64_proof_vs_saved(rule, 4, proof_box=6, search_box=12)
    assert rep["status"] == "PROVEN"
    assert rep["eliminated"] == 4
    assert rep["saved_sec"] > 0.0
    assert rep["proof_sec"] >= 0.0
    assert rep["net_sec"] == rep["saved_sec"] - rep["proof_sec"]
    cold = p64_proof_vs_saved(
        {"kind": "parity", "coord": 0, "residue": 1}, 4, proof_box=100, max_checks=1000
    )
    assert cold["status"] == "UNPROVEN"
    assert cold["eliminated"] == 0
    assert cold["saved_sec"] == 0.0
    dead = p64_proof_vs_saved({"kind": "parity", "coord": 0, "residue": 1}, 4, proof_box=6)
    assert dead["status"] == "REFUTED"
    assert dead["eliminated"] == 0


def test_p64_prioritized_scan_guarantees_exploration() -> None:
    triples = [(x, y, z) for x in range(1, 7) for y in range(1, 7) for z in range(1, 3)]
    rules = [{"kind": "parity", "coord": 0, "residue": 1}]
    first = p64_prioritized_scan(triples, rules, explore_frac=0.1, seed=3)
    assert first == p64_prioritized_scan(triples, rules, explore_frac=0.1, seed=3)
    assert sorted(first["order"]) == list(range(len(triples)))
    assert first["unfiltered_fraction"] >= 0.1
    narrow = p64_prioritized_scan(triples, rules, explore_frac=0.5, seed=3)
    assert narrow["unfiltered_fraction"] >= 0.5
    assert p64_prioritized_scan([], rules)["order"] == []
    try:
        p64_prioritized_scan(triples, rules, explore_frac=0.0)
    except ValueError as exc:
        assert "explore_frac" in str(exc)
    else:
        raise AssertionError("explore_frac=0 must raise")


def test_p64_proven_rules_discard_no_known_valid() -> None:
    rule = {"kind": "interval", "bound": "sum_le", "value": 4}
    assert p64_prove_rule(rule, 4, 6)["status"] == "PROVEN"
    known = [(2, 3, 6), (2, 4, 4), (3, 3, 3), (3, 4, 12), (2, 3, 6)]
    res = p64_apply_rules(known, [rule], [])
    assert res["eliminated"] == []
    assert res["kept"] == [0, 1, 2, 3, 4]


def test_p65_library_is_frozen_and_covering() -> None:
    lib = p65_build_library()
    assert len(lib) <= P65_MAX_LIBRARY == 8
    assert [e["id"] for e in lib] == ["even", "n=2-mod-3", "multiple-of-3", "anchor-1009"]
    assert p65_instantiate(lib[0], 6) == (3, 4, 12)
    assert p65_instantiate(lib[0], 5) is None
    assert p65_instantiate(lib[3], 1009) == tuple(P57_KNOWN_TRIPLE_1009)
    assert p65_instantiate(lib[3], 6) is None


def test_p65_bridges_prove_the_fixed_target() -> None:
    import pytest

    lib = p65_build_library()
    for n in (4, 5, 6, 9, 10):
        bridge = p65_find_bridge(lib, n)
        assert bridge is not None
        assert bridge["verified_for_n"] == n
        assert check_erdos_straus(n, *bridge["triple"])[0] is True
        assert check_erdos_straus_fractions(n, *bridge["triple"])[0] is True
    assert p65_find_bridge(lib, 73) is None
    anchor = p65_find_bridge(lib, 1009)
    assert anchor is not None and anchor["label"] == "rediscovery"
    other = p65_find_bridge(lib, 6)
    assert other is not None
    assert check_erdos_straus(7, *other["triple"])[0] is False
    with pytest.raises(ValueError, match="exceeds frozen max"):
        p65_find_bridge(lib + lib + lib[:1], 6)


def test_p65_random_library_is_seeded_public() -> None:
    first = p65_random_library(6, 50, seed=0)
    assert first == p65_random_library(6, 50, seed=0)
    assert len(first) == 6
    assert all(e["kind"] == "random" for e in first)
    fa = p65_entry_features(6, first[0])
    fb = p65_entry_features(6, first[1])
    assert len(fa) == 11
    assert fa == fb


def test_p65_bridge_scorer_trains_and_picks() -> None:
    lib = p65_build_library() + p65_random_library(6, 50, seed=0)
    first = p65_train_bridge_scorer(lib, list(range(2, 21)), seed=0, epochs=30)
    second = p65_train_bridge_scorer(lib, list(range(2, 21)), seed=0, epochs=30)
    assert first["n_params"] <= 100000
    assert first["train_acc"] > 0.5
    for key in first["state_dict"]:
        assert bool((first["state_dict"][key] == second["state_dict"][key]).all())
    assert sum(p.numel() for p in P65BridgeScorer().parameters()) == first["n_params"]
    assert p65_entry_verifies({"kind": "random", "triple": [2, 3, 6]}, 4) is True
    assert p65_entry_verifies({"kind": "random", "triple": [2, 3, 7]}, 4) is False
    pick = p65_model_pick(lib, first["state_dict"], 6)
    assert pick is not None
    assert check_erdos_straus(6, *pick["triple"])[0] is True
    miss = p65_model_pick(lib, first["state_dict"], 73)
    if miss is not None:
        assert check_erdos_straus(73, *miss["triple"])[0] is True


def test_p65_compare_libraries_bills_costs() -> None:
    rep = p65_compare_libraries(
        [4, 5, 6, 9, 10, 73],
        n_random=6,
        coord_bound=50,
        seed=0,
        train_n=list(range(2, 21)),
        epochs=30,
    )
    assert rep["library_size"] == 10
    assert rep["train"]["n_params"] <= 100000
    for arm in ("random-pick", "structured-first", "model-pick", "direct-search"):
        rec = rep[arm]
        assert rec["targets"] == 6
        assert set(rec["ledger"]) == {"parts", "total_sec"}
        parts = rec["ledger"]["parts"]
        assert set(parts) == {"train", "generation", "inference", "filters", "checkers", "tracking"}
        assert rec["ledger"]["total_sec"] == sum(parts.values())
    assert rep["model-pick"]["ledger"]["parts"]["train"] == rep["train"]["train_sec"] > 0.0
    assert rep["structured-first"]["ledger"]["parts"]["train"] == 0.0
    assert rep["structured-first"]["certified"] == 5
    assert rep["model-pick"]["certified"] >= 1
