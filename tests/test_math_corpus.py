"""Tests for P25 Math Corpus Consolidation & Leak-Free Benchmark Harness."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.math_corpus import (
    CorpusItem,
    build_and_verify_corpus,
    convert_gsm8k_row,
    convert_numinamath_row,
    generate_coverage_report,
    generate_symbolic_task,
    parse_boxed_or_scalar,
    run_parallel_verification,
    safe_eval_arithmetic,
    stratify_and_seal,
)


def test_safe_eval_arithmetic_valid() -> None:
    assert safe_eval_arithmetic("2 + 3 * 4") == 14.0
    assert safe_eval_arithmetic("(10 - 4) / 2") == 3.0
    assert safe_eval_arithmetic("2 ** 3") == 8.0
    assert safe_eval_arithmetic("-5.5 + 1.5") == -4.0
    assert safe_eval_arithmetic("100 % 7") == 2.0


def test_safe_eval_arithmetic_guards() -> None:
    # Malicious or non-arithmetic syntax must return None
    assert safe_eval_arithmetic("__import__('os').system('ls')") is None
    assert safe_eval_arithmetic("eval('2+2')") is None
    assert safe_eval_arithmetic("open('/tmp/test')") is None
    assert safe_eval_arithmetic("x + 1") is None
    # Division by zero
    assert safe_eval_arithmetic("1 / 0") is None
    # Empty string
    assert safe_eval_arithmetic("") is None
    assert safe_eval_arithmetic("   ") is None


def test_parse_boxed_or_scalar() -> None:
    assert parse_boxed_or_scalar("42") == 42.0
    assert parse_boxed_or_scalar("  -3.14  ") == -3.14
    assert parse_boxed_or_scalar(r"\boxed{17}") == 17.0
    assert parse_boxed_or_scalar(r"\frac{1}{4}") == 0.25
    assert parse_boxed_or_scalar("3/2") == 1.5
    assert parse_boxed_or_scalar("proof") is None
    assert parse_boxed_or_scalar("invalid latex text") is None


def test_convert_gsm8k_row_valid() -> None:
    row = {
        "question": "Janet has 16 eggs. She sells 3 to Tom and 4 to Alice, each egg for 2 dollars.",
        "answer": (
            "Janet sells 3 + 4 = <<3+4=7>>7 eggs. "
            "Remaining eggs: 16 - 7 = <<16-7=9>>9 eggs. "
            "Income: 7 * 2 = <<7*2=14>>14 dollars. #### 14"
        ),
    }
    items, rejected = convert_gsm8k_row(row, idx=1)
    assert len(rejected) == 0
    # 3 calculation chains (EXECUTE) + 1 final answer (FIND)
    assert len(items) == 4

    exec_items = [it for it in items if it.track == "EXECUTE"]
    find_items = [it for it in items if it.track == "FIND"]
    assert len(exec_items) == 3
    assert len(find_items) == 1

    assert exec_items[0].target_answer == 7.0
    assert exec_items[1].target_answer == 9.0
    assert exec_items[2].target_answer == 14.0
    assert find_items[0].target_answer == 14.0
    assert find_items[0].metadata["internal_exposure_prior"] is True


def test_convert_gsm8k_row_out_of_scope() -> None:
    bad_row = {
        "question": "A problem with a div0 chain.",
        "answer": "Compute <<1/0=0>>. No final answer marker.",
    }
    _items, rejected = convert_gsm8k_row(bad_row, idx=2)
    assert len(rejected) >= 1
    reasons = [r.reason for r in rejected]
    assert "division_by_zero_or_arithmetic_error" in reasons
    assert "missing_or_ambiguous_answer" in reasons


def test_convert_numinamath_row_filtering() -> None:
    # 1. Valid row
    valid_row = {
        "problem": "Find the value of 5x + 3 when x = 2.",
        "solution": "Substitute x = 2: 5(2) + 3 = 13. \\boxed{13}",
        "answer": "13",
        "problem_type": "Algebra",
        "problem_is_valid": "Yes",
        "solution_is_valid": "Yes",
    }
    items, rejected = convert_numinamath_row(valid_row, idx=10)
    assert len(items) == 1
    assert len(rejected) == 0
    assert items[0].target_answer == 13.0
    assert items[0].family == "algebra_numeric"
    assert items[0].track == "FIND"

    # 2. Invalid problem flag
    p_invalid_row = dict(valid_row, problem_is_valid="No")
    _, rej_p = convert_numinamath_row(p_invalid_row, idx=11)
    assert len(rej_p) == 1
    assert rej_p[0].reason == "invalid_problem_flag"

    # 3. Invalid solution flag
    s_invalid_row = dict(valid_row, solution_is_valid="Incomplete")
    _, rej_s = convert_numinamath_row(s_invalid_row, idx=12)
    assert len(rej_s) == 1
    assert rej_s[0].reason == "invalid_solution_flag"

    # 4. Proof-based problem
    proof_row = dict(valid_row, answer="proof")
    _, rej_proof = convert_numinamath_row(proof_row, idx=13)
    assert len(rej_proof) == 1
    assert rej_proof[0].reason == "proof_based_non_numeric"


def test_generate_symbolic_tasks() -> None:
    families = [
        "symbolic_differentiation",
        "symbolic_integration",
        "polynomial_arithmetic",
        "first_order_ode",
    ]
    for fam in families:
        it, rej = generate_symbolic_task(fam, task_idx=0, seed=42)
        assert rej is None
        assert it is not None
        assert it.family == fam
        assert it.track == "FIND"
        assert len(it.verifier["target_values"]) > 0


def test_stratify_and_seal() -> None:
    # Create mock items across families and difficulties
    items = []
    for f_idx, fam in enumerate(["family_a", "family_b"]):
        for diff in [1, 2, 3]:
            for i in range(10):
                items.append(
                    CorpusItem(
                        id=f"item_{fam}_d{diff}_{i:02d}",
                        source="test",
                        source_id=str(i),
                        track="FIND",
                        family=fam,
                        difficulty=diff,
                        problem_text="mock",
                        expression=None,
                        inputs=[1.0, 2.0],
                        constraints={},
                        allowed_ops=["ADD"],
                        target_answer=float(i),
                        verifier={"method": "target_scalar_float", "tolerance": 1e-5},
                        metadata={},
                    )
                )

    splits, seal = stratify_and_seal(items, seed=123, train_ratio=0.70, val_ratio=0.15)
    train_ids = {it.id for it in splits["train"]}
    val_ids = {it.id for it in splits["val"]}
    held_out_ids = {it.id for it in splits["held_out"]}

    # Zero overlap
    assert len(train_ids & val_ids) == 0
    assert len(train_ids & held_out_ids) == 0
    assert len(val_ids & held_out_ids) == 0
    assert len(train_ids | val_ids | held_out_ids) == len(items)

    # Check seal integrity
    assert seal.sealed is True
    assert seal.n_items == len(splits["held_out"])
    assert len(seal.item_ids_sha256) == 64
    assert len(seal.content_sha256) == 64
    assert seal.access_count == 0
    assert len(seal.access_log) == 0

    # Test seal access auditor
    seal.log_access("audit_agent", "post_training_eval")
    assert seal.access_count == 1
    assert len(seal.access_log) == 1
    assert seal.access_log[0]["caller"] == "audit_agent"


def test_parallel_verification_and_gpu_parity() -> None:
    items = [
        CorpusItem(
            id="test_01",
            source="test",
            source_id="1",
            track="EXECUTE",
            family="arithmetic_chain",
            difficulty=1,
            problem_text="2 + 3",
            expression="2 + 3",
            inputs=[],
            constraints={},
            allowed_ops=["ADD"],
            target_answer=5.0,
            verifier={"method": "guarded_arithmetic", "tolerance": 1e-6},
            metadata={},
        ),
        CorpusItem(
            id="test_02",
            source="test",
            source_id="2",
            track="FIND",
            family="algebra_numeric",
            difficulty=2,
            problem_text="Find x",
            expression=None,
            inputs=[10.0],
            constraints={},
            allowed_ops=["ADD"],
            target_answer=10.0,
            verifier={"method": "target_scalar_float", "tolerance": 1e-6},
            metadata={},
        ),
    ]

    report = run_parallel_verification(items, device_name="cpu")
    assert report["n_items_checked"] == 2
    assert report["failures"] == 0
    assert report["all_passed"] is True
    assert report["parity_sum_ok"] is True
    assert report["parity_l2_ok"] is True
    assert abs(report["gpu_sum"] - report["cpu_oracle_sum"]) < 1e-4


def test_generate_coverage_report() -> None:
    items = [
        CorpusItem(
            id="test_01",
            source="gsm8k",
            source_id="1",
            track="EXECUTE",
            family="arithmetic_chain",
            difficulty=1,
            problem_text="2 + 3",
            expression="2 + 3",
            inputs=[],
            constraints={},
            allowed_ops=["ADD"],
            target_answer=5.0,
            verifier={"method": "guarded_arithmetic", "tolerance": 1e-6},
            metadata={},
        ),
    ]
    cov = generate_coverage_report(items, rejected=[])
    assert cov["total_convertible"] == 1
    assert cov["total_out_of_scope"] == 0
    assert cov["by_family"]["arithmetic_chain"] == 1
    assert cov["by_difficulty"][1] == 1
    assert cov["by_track"]["EXECUTE"] == 1


def test_full_pipeline_fast(tmp_path: Path) -> None:
    out_manifest = tmp_path / "test-manifest.json"
    snapshot_path = tmp_path / "test-snapshot.jsonl"

    manifest = build_and_verify_corpus(
        output_manifest=out_manifest,
        snapshot_path=snapshot_path,
        device_name="cpu",
        seed=42,
        numina_limit=5,
        symbolic_n=8,
        gsm8k_limit=5,
    )

    assert out_manifest.exists()
    assert snapshot_path.exists()
    assert manifest["phase"] == "p25-math-corpus"
    assert manifest["status"] == "complete"
    assert manifest["items_total"] > 0
    assert manifest["verification"]["failures"] == 0
    assert manifest["verification"]["parity_sum_ok"] is True
    assert manifest["held_out_seal"]["sealed"] is True
    assert manifest["held_out_seal"]["access_count"] == 0
    assert "internal_exposure_disclosure" in manifest
