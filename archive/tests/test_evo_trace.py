"""Tests for P26 Reproducible Lineage Tracing, Audit Replay & Exploration Map."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.evo_trace import (
    build_exploration_map,
    classify_quality,
    classify_structure,
    compute_behavioral_signature,
    extract_candidate_metrics,
    generate_claims_audit,
    measure_tracing_overhead,
    run_acceptance_audit,
    run_evo_trace_pipeline,
    run_lineage_evolution,
    validate_parent_ordering,
    verify_config_sensitivity,
    verify_honest_counters,
    verify_manifest_integrity,
    verify_replay_bit_exact,
    verify_resume_bit_exact,
)
from evobyte.bytecode import encode_instr
from evobyte.provenance import write_manifest


def test_extract_candidate_metrics() -> None:
    # 2 active instructions (ADD r7, r0, r1 and MUL r7, r7, r2), rest NOPs
    words = [0] * 16
    words[0] = encode_instr(0x01, 7, 0, 1)  # ADD r7, r0, 1
    words[1] = encode_instr(0x03, 7, 7, 2)  # MUL r7, r7, 2
    arr = np.array(words, dtype=np.uint32)

    m = extract_candidate_metrics(arr)
    assert m["length_total"] == 16
    assert m["length_active"] == 2
    assert m["n_nops"] == 14
    assert m["nop_fraction"] == 14 / 16
    assert "ADD" in m["ops"]
    assert "MUL" in m["ops"]


def test_compute_behavioral_signature() -> None:
    # Program that writes constant 0 to r7: SUB r7, r0, r0 (x - x = 0.0)
    words = [0] * 16
    words[0] = encode_instr(0x02, 7, 0, 0)
    tensor_prog = torch.tensor(words, dtype=torch.int64)

    probe_xs = torch.tensor([-2.0, 0.0, 2.0], dtype=torch.float32)
    sig, beh = compute_behavioral_signature(tensor_prog, probe_xs, device=torch.device("cpu"))
    assert beh == "constant_output"
    assert len(sig) == 16


def test_classify_structure_and_quality() -> None:
    assert classify_quality(0.00005) == "tier_0_discovery"
    assert classify_quality(0.005) == "tier_1_near"
    assert classify_quality(0.5) == "tier_2_coarse"
    assert classify_quality(10.0) == "tier_3_poor"
    assert classify_quality(float("inf")) == "tier_invalid"

    m_nop = {"nop_fraction": 0.6, "length_active": 4, "ops": ["ADD"]}
    assert classify_structure(m_nop) == "nop_heavy"

    m_dense = {"nop_fraction": 0.1, "length_active": 14, "ops": ["ADD", "MUL"]}
    assert classify_structure(m_dense) == "dense"

    m_branch = {"nop_fraction": 0.3, "length_active": 8, "ops": ["ADD", "CSEL"]}
    assert classify_structure(m_branch) == "branching_ops"


def test_run_lineage_evolution_and_ancestry() -> None:
    record = run_lineage_evolution(
        seed=42,
        pop_size=50,
        n_generations=5,
        n_points=64,
        formula="x_plus_1",
        audit_mode=True,
        device_name="cpu",
    )
    assert record.run_id == "run_seed_42"
    assert len(record.generations) == 5
    assert record.audit_store is not None
    assert len(record.audit_store) == 50 * 5

    # Check ancestry tracking
    assert len(record.promoted_ancestry) >= 1
    best_anc = record.promoted_ancestry[0]
    assert len(best_anc.ancestry_chain) >= 1
    assert best_anc.ancestry_chain[0] == best_anc.candidate_id


def test_verify_replay_bit_exact() -> None:
    record = run_lineage_evolution(
        seed=100,
        pop_size=40,
        n_generations=4,
        n_points=32,
        formula="x2_3x_7",
        audit_mode=True,
        device_name="cpu",
    )
    replay_res = verify_replay_bit_exact(record, device_name="cpu")
    assert replay_res["bit_exact_reproducible"] is True
    assert replay_res["generations_replayed"] == 4
    assert replay_res["mismatches_count"] == 0
    assert replay_res["promoted_ancestry_matched"] is True


def test_build_exploration_map() -> None:
    record = run_lineage_evolution(
        seed=7,
        pop_size=40,
        n_generations=3,
        n_points=32,
        audit_mode=False,
        device_name="cpu",
    )
    exp_map = build_exploration_map([record], device_name="cpu")
    assert exp_map["distinct_byte_programs"] >= 1
    assert exp_map["distinct_mathematical_expressions"] >= 1
    assert exp_map["syntactic_redundancy_ratio"] >= 1.0
    assert len(exp_map["structure_distribution"]) > 0
    assert len(exp_map["quality_distribution"]) > 0


def test_measure_tracing_overhead() -> None:
    oh = measure_tracing_overhead(
        pop_size=30,
        n_generations=3,
        n_points=32,
        device_name="cpu",
        repeats=1,
    )
    assert oh["baseline_sec"] > 0
    assert oh["aggregate_sec"] > 0
    assert oh["cvps_baseline"] > 0
    assert "aggregate_overhead_pct" in oh
    assert "audit_overhead_pct" in oh


def test_full_pipeline(tmp_path: Path) -> None:
    out_file = tmp_path / "test-p26.json"
    manifest = run_evo_trace_pipeline(
        seeds_count=2,
        audit=True,
        output_path=out_file,
        device_name="cpu",
        pop_size=30,
        n_generations=3,
        n_points=32,
    )
    assert out_file.exists()
    assert manifest["phase"] == "p26-lineage-map"
    assert manifest["status"] == "complete"
    assert manifest["all_bit_exact_reproduced"] is True
    assert len(manifest["seeds"]) == 2
    assert "exploration_map" in manifest
    assert "overhead_benchmark" in manifest
    assert "manifest_sha256" in manifest


def test_checkpoint_resume_bit_exact(tmp_path: Path) -> None:
    res = verify_resume_bit_exact(
        seed=101,
        pop_size=40,
        n_generations=6,
        split_at=3,
        n_points=32,
        device_name="cpu",
        checkpoint_dir=tmp_path,
    )
    assert res["bit_exact_resumed"] is True
    assert res["mismatches_count"] == 0
    assert res["generations_verified"] == 6
    assert res["split_generation"] == 3


def test_parent_ordering_symmetry() -> None:
    record = run_lineage_evolution(
        seed=42,
        pop_size=40,
        n_generations=4,
        n_points=32,
        formula="x2_3x_7",
        audit_mode=True,
        device_name="cpu",
        crossover_p=0.8,
    )
    val = validate_parent_ordering(record)
    assert val["valid"] is True
    assert len(val["violations"]) == 0
    assert val["n_offspring"] > 0


def test_honest_counters_consistency() -> None:
    record = run_lineage_evolution(
        seed=77,
        pop_size=50,
        n_generations=5,
        n_points=32,
        audit_mode=False,
        device_name="cpu",
    )
    res = verify_honest_counters(record)
    assert res["consistent"] is True
    assert len(res["issues"]) == 0

    # Verify per-generation invariants directly
    cum = 0
    for g in record.generations:
        cum += 50
        assert g.total_generated_cumulative == cum
        assert g.executed_scored_count == 50
        assert g.s0_valid_count == g.valid_count
        assert g.distinct_bytes_window + g.repeated_bytes_window == 50
        assert g.duplicate_count_status == "exact"
        assert g.validity_sampled_estimated is False


def test_manifest_integrity_fail_closed(tmp_path: Path) -> None:
    manifest_path = tmp_path / "test_manifest.json"
    art_path = tmp_path / "test_art.bin"
    art_path.write_bytes(b"honest content")
    import hashlib

    art_sha = hashlib.sha256(b"honest content").hexdigest()

    write_manifest(
        manifest_path,
        {"phase": "test-p32", "status": "PASS"},
        {
            str(
                art_path.relative_to(_REPO_ROOT)
                if art_path.is_relative_to(_REPO_ROOT)
                else art_path
            ): art_sha
        },
    )

    # 1. Valid passes
    v_pass = verify_manifest_integrity(manifest_path)
    assert v_pass["passed"] is True
    assert v_pass["raw_artifacts_verified"] == 1

    # 2. Tampered content fails closed
    art_path.write_bytes(b"tampered content")
    v_tamper = verify_manifest_integrity(manifest_path)
    assert v_tamper["passed"] is False
    assert v_tamper["reason"] == "artifact_tampered"

    # 3. Missing artifact fails closed
    art_path.unlink()
    v_miss = verify_manifest_integrity(manifest_path)
    assert v_miss["passed"] is False
    assert v_miss["reason"] == "artifact_missing"

    # 4. Missing manifest fails closed
    v_nonexistent = verify_manifest_integrity(tmp_path / "missing.json")
    assert v_nonexistent["passed"] is False
    assert v_nonexistent["reason"] == "manifest_not_found"


def test_config_sensitivity() -> None:
    res = verify_config_sensitivity(seed=42, device_name="cpu")
    assert res["diverged"] is True
    assert res["first_diverged_generation"] >= 0


def test_manifest_requires_checksum_and_raw_evidence(tmp_path: Path) -> None:
    manifest_path = tmp_path / "empty.json"
    manifest_path.write_text('{"status":"PASS"}')
    assert verify_manifest_integrity(manifest_path)["reason"] == "missing_manifest_hash"
    write_manifest(manifest_path, {"status": "PASS"}, {})
    assert verify_manifest_integrity(manifest_path)["reason"] == "missing_raw_artifacts"
    manifest_path.write_text("[]")
    assert verify_manifest_integrity(manifest_path)["passed"] is False


def test_generate_claims_audit() -> None:
    audit = generate_claims_audit()
    assert audit["audit_complete"] is True
    phases = audit["p13_p29_classifications"]
    assert set(phases) == {f"P{i}" for i in range(13, 32)}
    assert "Population-parallel GPU" in phases["P16"]["claim"]
    assert "Streaming GPU cascade" in phases["P18"]["claim"]
    assert "Quantum-inspired randomness" in phases["P27"]["claim"]
    assert phases["P14"]["classification"] == "not_run"
    assert phases["P22"]["classification"] == "provisional"
    assert phases["P25"]["classification"] == "superseded"
    assert phases["P29"]["classification"] == "superseded"
    quantum = audit["quantum_classifications"]
    assert set(quantum) == {f"Q{i:02}" for i in range(7, 14)}
    assert "known ground-state" in quantum["Q10"]["rationale"]
    assert "not a trained" in quantum["Q12"]["rationale"]
    assert "oracle" in quantum["Q13"]["rationale"]
    for entry in [*phases.values(), *quantum.values()]:
        assert entry["classification"] != "accepted"
        assert entry["classification_scope"] == "scientific_acceptance"
        assert entry["evidence"][0]["present"] is True
        assert len(entry["evidence"][0]["sha256"]) == 64
        assert entry["independent_confirmation"] == "not_run"
    h1 = audit["hypothesis_h1_evaluation"]
    assert h1["overall_h1_verdict"] == "provisional"
    assert set(h1["criteria_status"].values()) == {"provisional"}
    assert len(h1["criterion_definitions"]) == 5
    assert "ablation 8–9" in h1["criterion_definitions"]["criterion_2_speed"]
    assert "1,000,000 distinct" in h1["engineering_goal"]


def test_claims_audit_missing_or_forged_evidence_cannot_accept(tmp_path: Path) -> None:
    missing = generate_claims_audit(repo_root=tmp_path)
    assert missing["audit_complete"] is False
    assert all(
        e["classification"] == "not_run" for e in missing["p13_p29_classifications"].values()
    )
    doc = tmp_path / "docs/phases/P16-population-gpu-vm.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# P16 — Population-parallel GPU interpreter\n")
    artifact = tmp_path / "experiments/p16-vm.json"
    artifact.parent.mkdir()
    artifact.write_text('{"status":"PASS","classification":"accepted"}')
    forged = generate_claims_audit(repo_root=tmp_path)
    p16 = forged["p13_p29_classifications"]["P16"]
    assert p16["classification"] == "provisional"
    assert p16["independent_confirmation"] == "not_run"
    assert forged["audit_complete"] is False
    previous_sha = p16["evidence"][1]["sha256"]
    artifact.write_text('{"status":"PASS","throughput":1000000000}')
    altered = generate_claims_audit(repo_root=tmp_path)
    assert altered["p13_p29_classifications"]["P16"]["classification"] != "accepted"
    assert altered["p13_p29_classifications"]["P16"]["evidence"][1]["sha256"] != previous_sha


def test_run_acceptance_audit_smoke(tmp_path: Path) -> None:
    out_file = tmp_path / "p32-smoke.json"
    manifest = run_acceptance_audit(
        seeds_count=2,
        resume=True,
        output_path=out_file,
        device_name="cpu",
        pop_size=30,
        n_generations=4,
        split_at=2,
        n_points=32,
    )
    assert out_file.exists()
    assert manifest["phase"] == "p32-replay-acceptance"
    assert manifest["status"] == "PASS"
    assert all(manifest["mandatory_checks"].values()) is True
    assert len(manifest["seeds"]) == 2
    assert len(manifest["resume_verification"]) == 2
    assert all(r["bit_exact_resumed"] for r in manifest["resume_verification"]) is True
    trace_path = out_file.with_suffix(".trace.json")
    trace = json.loads(trace_path.read_text())
    assert len(trace["lineage_runs"]) == 2
    for run in trace["lineage_runs"]:
        assert len(run["audit_store"]) == run["audit_store_count"]
        assert len(run["audit_store"]) > 10
    assert verify_manifest_integrity(out_file)["passed"] is True
    trace_path.write_text('{"lineage_runs":[]}')
    assert verify_manifest_integrity(out_file)["reason"] == "artifact_tampered"
    trace_path.unlink()
    assert verify_manifest_integrity(out_file)["reason"] == "artifact_missing"


def test_acceptance_cannot_pass_without_resume(tmp_path: Path) -> None:
    manifest = run_acceptance_audit(
        seeds_count=1,
        resume=False,
        output_path=tmp_path / "no-resume.json",
        device_name="cpu",
        pop_size=30,
        n_generations=4,
        split_at=2,
        n_points=32,
    )
    assert manifest["status"] == "FAIL"
    assert manifest["mandatory_checks"]["all_resumed_bit_exact"] is False
    with pytest.raises(ValueError, match="positive"):
        run_acceptance_audit(seeds_count=0, output_path=tmp_path / "empty.json")


def test_p51_bounded_map_caps_and_partial_coverage() -> None:
    from benchmarks.evo_trace import build_bounded_replay_map, run_lineage_evolution
    from evobyte.archive import validate_bounded_replay_map

    record = run_lineage_evolution(
        seed=7,
        pop_size=16,
        n_generations=3,
        n_points=32,
        formula="x2_3x_7",
        audit_mode=True,
        device_name="cpu",
    )
    full = build_bounded_replay_map(record, max_nodes=100_000, checkpoint_ref="ckpt")
    assert full.coverage == "full"
    assert full.sampling_rate == 1.0
    assert full.dropped_samples == 0

    small = build_bounded_replay_map(record, max_nodes=20, checkpoint_ref="ckpt")
    assert small.coverage == "partial_sampled"
    assert len(small.nodes) <= 20
    assert small.io_bytes <= small.io_queue_bytes
    assert small.raw_bytes < small.raw_disk_bytes
    expected = [a.bytecode_sha256 for a in record.promoted_ancestry]
    assert validate_bounded_replay_map(small, expected_certificates=expected)["ok"] is True


def test_p51_bounded_map_replay_and_validation() -> None:
    from benchmarks.evo_trace import (
        build_bounded_replay_map,
        replay_bounded_map_segments,
        run_lineage_evolution,
        run_p51_bounded_replay,
    )
    from evobyte.archive import (
        new_bounded_replay_map,
        replay_map_add_sample,
        validate_bounded_replay_map,
    )

    exp = run_p51_bounded_replay(
        seed=7, pop_size=16, n_generations=3, device_name="cpu", max_nodes=20
    )
    assert exp["replay"]["segments_match"] is True
    assert exp["validation"]["ok"] is True
    assert exp["parent_ordering_valid"] is True
    assert exp["counters_consistent"] is True
    assert exp["overhead"]["audit_sec"] > 0

    record = run_lineage_evolution(
        seed=7,
        pop_size=16,
        n_generations=3,
        n_points=32,
        formula="x2_3x_7",
        audit_mode=True,
        device_name="cpu",
    )
    replay_map = build_bounded_replay_map(record, max_nodes=20, checkpoint_ref="ckpt")
    replay = replay_bounded_map_segments(record, replay_map, device_name="cpu")
    assert replay["segments_match"] is True
    assert replay["nodes_compared"] == len(replay_map.nodes)

    broken = new_bounded_replay_map(7, "ckpt")
    assert replay_map_add_sample(broken, 1, "c_g1_o0", "b" * 64, ["c_g9_nope"], "elite") is True
    assert validate_bounded_replay_map(broken)["ok"] is False
    assert validate_bounded_replay_map(replay_map, expected_certificates=["0" * 64])["ok"] is False
