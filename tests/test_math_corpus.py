"""Tests for P25 Math Corpus Consolidation & Leak-Free Benchmark Harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.math_corpus import (
    CorpusItem,
    HeldOutSeal,
    IsolatedCorpusLoader,
    ProblemGroup,
    audit_splits_contamination,
    build_and_verify_corpus,
    convert_gsm8k_row,
    convert_numinamath_row,
    extract_problem_template,
    generate_coverage_report,
    generate_symbolic_task,
    get_source_problem_id,
    group_items_by_source_and_template,
    isolate_and_split_groups,
    normalize_text_for_dedup,
    parse_boxed_or_scalar,
    reproduce_p25_contamination,
    run_corpus_isolation_and_audit,
    run_parallel_verification,
    safe_eval_arithmetic,
    stratify_and_seal,
)


@pytest.fixture
def local_corpus_snapshot(tmp_path: Path) -> Path:
    """Controlled inputs for pipeline tests, independent of research caches."""
    items = [
        CorpusItem(
            id=f"fixture_exec_{idx}",
            source="ci_fixture",
            source_id=chr(97 + idx),
            track="EXECUTE",
            family="arithmetic_chain",
            difficulty=1,
            problem_text=f"Arithmetic case {chr(97 + idx)}",
            expression=f"{idx} + 3",
            inputs=[],
            constraints={},
            allowed_ops=["ADD"],
            target_answer=float(idx + 3),
            verifier={"method": "guarded_arithmetic", "tolerance": 1e-6},
            metadata={},
        )
        for idx in range(20)
    ]
    for idx in range(4):
        item, rejected = generate_symbolic_task("polynomial_arithmetic", idx, seed=42)
        assert item is not None and rejected is None
        items.append(item)
    unsupported, rejected = convert_gsm8k_row(
        {"question": "How many candles were counted?", "answer": "#### 7"},
        idx=999,
    )
    assert len(unsupported) == 1 and not rejected
    items.extend(unsupported)
    snapshot = tmp_path / "controlled-corpus.jsonl"
    snapshot.write_text(
        "".join(json.dumps(item.to_dict()) + "\n" for item in items), encoding="utf-8"
    )
    return snapshot


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
    gsm8k_path = tmp_path / "gsm8k.jsonl"
    numina_path = tmp_path / "numina.jsonl"
    gsm8k_path.write_text(
        json.dumps(
            {
                "question": "How many apples remain after giving two away?",
                "answer": "5 - 2 = <<5-2=3>>3. #### 3",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    numina_path.write_text(
        json.dumps(
            {
                "problem": "Evaluate 4 times 5.",
                "solution": r"\boxed{20}",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = build_and_verify_corpus(
        gsm8k_path=gsm8k_path,
        numina_path=numina_path,
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


# ==============================================================================
# P30 Corpus Isolation Unit Tests
# ==============================================================================


def test_normalize_and_template_extraction() -> None:
    text = "Janet sells 3 eggs for $2 each. Compute \\boxed{6}."
    norm = normalize_text_for_dedup(text)
    assert "$" not in norm
    assert "janet sells 3 eggs for 2 each. compute 6" in norm

    tpl_text, tpl_id = extract_problem_template(text)
    assert "{N}" in tpl_text
    assert "3" not in tpl_text
    assert tpl_id.startswith("tpl_")
    assert len(tpl_id) == 20  # tpl_ + 16 hex chars


def test_reused_source_ids_disambiguation() -> None:
    it_diff = CorpusItem(
        id="sym_diff_0000",
        source="symbolic_math",
        source_id="0",
        track="FIND",
        family="symbolic_differentiation",
        difficulty=1,
        problem_text="diff x",
        expression=None,
        inputs=[],
        constraints={},
        allowed_ops=["ADD"],
        target_answer=0.0,
        verifier={"method": "target_scalar_float"},
        metadata={},
    )
    it_inte = CorpusItem(
        id="sym_inte_0000",
        source="symbolic_math",
        source_id="0",
        track="FIND",
        family="symbolic_integration",
        difficulty=1,
        problem_text="inte x",
        expression=None,
        inputs=[],
        constraints={},
        allowed_ops=["ADD"],
        target_answer=0.0,
        verifier={"method": "target_scalar_float"},
        metadata={},
    )
    id_diff = get_source_problem_id(it_diff)
    id_inte = get_source_problem_id(it_inte)
    assert id_diff != id_inte
    assert id_diff == "symbolic_math:symbolic_differentiation:0"
    assert id_inte == "symbolic_math:symbolic_integration:0"


def test_group_by_source_problem_and_sibling_chains() -> None:
    row = {
        "question": "A farmer has 10 sheep and buys 5 more.",
        "answer": "10 + 5 = <<10+5=15>>15 sheep. #### 15",
    }
    items, rejected = convert_gsm8k_row(row, idx=42)
    assert len(rejected) == 0
    assert len(items) == 2  # 1 exec + 1 find

    groups, ungroupable = group_items_by_source_and_template(items)
    assert len(ungroupable) == 0
    assert len(groups) == 1

    group = groups[0]
    assert isinstance(group, ProblemGroup)
    assert len(group.items) == 2
    assert group.group_id == "gsm8k:42"
    assert group.is_exposed is True

    # Sibling items share group_id and template_id and have reference_only status
    assert items[0].group_id == group.group_id
    assert items[1].group_id == group.group_id
    assert items[0].template_id == group.template_id
    assert items[1].template_id == group.template_id
    assert items[0].verification_status == "reference_only"
    assert items[1].verification_status == "reference_only"


def test_duplicate_text_clustering() -> None:
    it1 = CorpusItem(
        id="it1",
        source="symbolic_math",
        source_id="1",
        track="FIND",
        family="symbolic_differentiation",
        difficulty=1,
        problem_text="Differentiate with respect to x: 2*x + 1",
        expression="2*x + 1",
        inputs=[],
        constraints={},
        allowed_ops=["ADD"],
        target_answer=2.0,
        verifier={"method": "target_scalar_float"},
        metadata={},
    )
    it2 = CorpusItem(
        id="it2",
        source="symbolic_math",
        source_id="19",
        track="FIND",
        family="symbolic_differentiation",
        difficulty=1,
        problem_text="differentiate with respect to x:  2*x + 1 ",
        expression="2*x + 1",
        inputs=[],
        constraints={},
        allowed_ops=["ADD"],
        target_answer=2.0,
        verifier={"method": "target_scalar_float"},
        metadata={},
    )
    groups, ungroupable = group_items_by_source_and_template([it1, it2])
    assert len(ungroupable) == 0
    # Clustered into 1 group because normalized problem text is identical
    assert len(groups) == 1
    assert len(groups[0].items) == 2
    assert it1.group_id == it2.group_id


def test_ungroupable_records_reporting() -> None:
    bad_item = CorpusItem(
        id="bad_01",
        source="",
        source_id="",
        track="FIND",
        family="unknown",
        difficulty=1,
        problem_text="",
        expression=None,
        inputs=[],
        constraints={},
        allowed_ops=[],
        target_answer=0.0,
        verifier={},
        metadata={},
    )
    groups, ungroupable = group_items_by_source_and_template([bad_item])
    assert len(groups) == 0
    assert len(ungroupable) == 1
    assert ungroupable[0] == "bad_01"


def test_p25_contamination_reproduction_640() -> None:
    snapshot = _REPO_ROOT / "data" / "processed" / "p25_corpus.jsonl"
    if not snapshot.exists():
        pytest.skip("p25_corpus.jsonl snapshot not found")

    import json

    with open(snapshot, encoding="utf-8") as f:
        items = [CorpusItem.from_dict(json.loads(line)) for line in f if line.strip()]

    report = reproduce_p25_contamination(items, seed=42)
    assert report["reproduced_defect"] == "p25_item_stratification_leakage"
    assert report["gsm8k_shared_source_problems"] == 640
    assert report["total_gsm8k_source_problems"] == 1319
    assert report["status"] == "reproduced_as_reported"


def test_isolated_splits_zero_leakage() -> None:
    # Build synthetic groups: exposed and unexposed
    items: list[CorpusItem] = []
    # 20 exposed problems with 2 chain steps each (total 60 items)
    for i in range(20):
        items.append(
            CorpusItem(
                id=f"gsm_{i}_exec_0",
                source="gsm8k",
                source_id=str(i),
                track="EXECUTE",
                family="arithmetic_chain",
                difficulty=1,
                problem_text=f"compute {i} + 1",
                expression=f"{i} + 1",
                inputs=[],
                constraints={},
                allowed_ops=["ADD"],
                target_answer=float(i + 1),
                verifier={"method": "guarded_arithmetic"},
                metadata={"internal_exposure_prior": True},
            )
        )
        items.append(
            CorpusItem(
                id=f"gsm_{i}_exec_1",
                source="gsm8k",
                source_id=str(i),
                track="EXECUTE",
                family="arithmetic_chain",
                difficulty=1,
                problem_text=f"compute {i} * 2",
                expression=f"{i} * 2",
                inputs=[],
                constraints={},
                allowed_ops=["MUL"],
                target_answer=float(i * 2),
                verifier={"method": "guarded_arithmetic"},
                metadata={"internal_exposure_prior": True},
            )
        )
        items.append(
            CorpusItem(
                id=f"gsm_{i}_find",
                source="gsm8k",
                source_id=str(i),
                track="FIND",
                family="arithmetic_word_problem",
                difficulty=2,
                problem_text=f"Problem {i} question",
                expression=None,
                inputs=[float(i)],
                constraints={},
                allowed_ops=["ADD", "MUL"],
                target_answer=float(i * 2),
                verifier={"method": "target_scalar_float"},
                metadata={"internal_exposure_prior": True},
            )
        )

    # 30 unexposed problems (single item each)
    for i in range(30):
        items.append(
            CorpusItem(
                id=f"numina_{i}_find",
                source="numinamath",
                source_id=str(i),
                track="FIND",
                family="algebra_numeric",
                difficulty=2,
                problem_text=f"Find x such that x + {i} = 100",
                expression=None,
                inputs=[float(i)],
                constraints={},
                allowed_ops=["SUB"],
                target_answer=float(100 - i),
                verifier={"method": "target_scalar_float"},
                metadata={"internal_exposure_prior": False},
            )
        )

    groups, ungroupable = group_items_by_source_and_template(items)
    assert len(ungroupable) == 0
    assert len(groups) == 50

    splits, split_groups, seal = isolate_and_split_groups(groups, seed=123)
    audit = audit_splits_contamination(splits, split_groups, items, seed=123)

    after = audit["after_audit"]
    assert after["zero_leakage_verified"] is True
    assert after["source_overlap_train_val"] == 0
    assert after["source_overlap_train_final_test"] == 0
    assert after["source_overlap_val_final_test"] == 0
    assert after["group_overlap_train_val"] == 0
    assert after["group_overlap_train_final_test"] == 0
    assert after["group_overlap_val_final_test"] == 0
    assert after["exposed_items_in_final_test"] == 0
    assert after["exposed_groups_in_final_test"] == 0
    assert after["all_pristine_test_unexposed"] is True

    # Check total items conservation
    total_split_items = len(splits["train"]) + len(splits["val"]) + len(splits["final_test"])
    assert total_split_items == len(items)

    # Check seal
    assert seal.sealed is True
    assert seal.n_items == len(splits["final_test"])
    assert seal.access_count == 0


def test_isolated_corpus_loader_access_control() -> None:
    item_tr = CorpusItem(
        id="tr_1",
        source="test",
        source_id="1",
        track="FIND",
        family="test_fam",
        difficulty=1,
        problem_text="train prob",
        expression=None,
        inputs=[],
        constraints={},
        allowed_ops=[],
        target_answer=1.0,
        verifier={},
        metadata={},
    )
    item_te = CorpusItem(
        id="te_1",
        source="test",
        source_id="2",
        track="FIND",
        family="test_fam",
        difficulty=1,
        problem_text="test prob",
        expression=None,
        inputs=[],
        constraints={},
        allowed_ops=[],
        target_answer=2.0,
        verifier={},
        metadata={},
    )
    seal = HeldOutSeal(sealed=True, n_items=1)
    loader = IsolatedCorpusLoader(
        splits={"train": [item_tr], "val": [], "final_test": [item_te], "held_out": [item_te]},
        seal=seal,
    )

    # Train and val accessible without restrictions
    assert len(loader.get_train_items()) == 1
    assert len(loader.get_val_items()) == 0
    assert len(loader.load_split("train")) == 1

    # Unauthorized access to final test raises PermissionError
    import pytest

    with pytest.raises(PermissionError, match="Unauthorized access"):
        loader.get_final_test_items(caller="researcher", reason="tuning", authorized=False)

    with pytest.raises(PermissionError, match="Unauthorized access"):
        loader.load_split("final_test")

    with pytest.raises(PermissionError, match="Unauthorized access"):
        loader.load_split("held_out")

    # Missing caller or reason raises ValueError
    with pytest.raises(ValueError, match="caller"):
        loader.get_final_test_items(caller="", reason="eval", authorized=True)

    with pytest.raises(ValueError, match="reason"):
        loader.get_final_test_items(caller="eval_agent", reason="  ", authorized=True)

    # Authorized access succeeds and logs
    test_items = loader.get_final_test_items(
        caller="frozen_eval_runner",
        reason="p38_independent_reproduction",
        authorized=True,
    )
    assert len(test_items) == 1
    assert test_items[0].id == "te_1"
    assert loader.seal.access_count == 1
    assert len(loader.seal.access_log) == 1
    assert loader.seal.access_log[0]["caller"] == "frozen_eval_runner"

    # Invalid split name
    with pytest.raises(ValueError, match="Unknown split name"):
        loader.load_split("nonexistent_split")


def test_isolated_splits_determinism() -> None:
    items = [
        CorpusItem(
            id=f"item_{i}",
            source="numinamath",
            source_id=str(i),
            track="FIND",
            family="algebra_numeric",
            difficulty=(i % 3) + 1,
            problem_text=f"problem {i}",
            expression=None,
            inputs=[],
            constraints={},
            allowed_ops=[],
            target_answer=float(i),
            verifier={"method": "target_scalar_float"},
            metadata={"internal_exposure_prior": False},
        )
        for i in range(25)
    ]
    groups, _ = group_items_by_source_and_template(items)

    splits1, _, seal1 = isolate_and_split_groups(groups, seed=999)
    splits2, _, seal2 = isolate_and_split_groups(groups, seed=999)

    assert [it.id for it in splits1["train"]] == [it.id for it in splits2["train"]]
    assert [it.id for it in splits1["val"]] == [it.id for it in splits2["val"]]
    assert [it.id for it in splits1["final_test"]] == [it.id for it in splits2["final_test"]]
    assert seal1.item_ids_sha256 == seal2.item_ids_sha256
    assert seal1.content_sha256 == seal2.content_sha256


def test_run_corpus_isolation_and_audit_manifest(
    tmp_path: Path,
    local_corpus_snapshot: Path,
) -> None:
    manifest_p = tmp_path / "p30-splits.json"
    manifest = run_corpus_isolation_and_audit(
        snapshot_path=local_corpus_snapshot,
        output_path=manifest_p,
        device_name="cpu",
        seed=42,
    )

    assert manifest_p.exists()
    assert manifest["phase"] == "p30-corpus-isolation"
    assert manifest["status"] == "complete"
    assert manifest["contamination_audit"]["after_audit"]["zero_leakage_verified"] is True
    assert manifest["held_out_seal"]["sealed"] is True
    assert manifest["held_out_seal"]["access_count"] == 0

    loader = IsolatedCorpusLoader.from_manifest(manifest_p)
    assert len(loader.get_train_items()) > 0
    assert len(loader.get_val_items()) > 0
    with pytest.raises(PermissionError):
        loader.load_split("final_test")

    test_items = loader.load_split(
        "final_test", caller="test_agent", reason="unit_test", authorized=True
    )
    assert len(test_items) > 0
    assert loader.seal.access_count == 1
