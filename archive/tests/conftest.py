import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))


@pytest.fixture
def p30_split_manifest(tmp_path: Path) -> Path:
    """Hermetic polynomial corpus; never read or replace historical datasets."""
    from benchmarks.math_corpus import (
        generate_symbolic_task,
        run_corpus_isolation_and_audit,
    )
    from benchmarks.math_specialist import _try_exact_horner_program

    items = []
    for idx in range(256):
        item, rejected = generate_symbolic_task("polynomial_arithmetic", idx, seed=42)
        assert item is not None and rejected is None
        # Supported constant-bank polynomials exercise exact positives reliably.
        if _try_exact_horner_program(item.metadata["ground_truth_expr"]) is not None:
            items.append(item)
        if len(items) == 16:
            break
    assert len(items) == 16
    snapshot = tmp_path / "controlled-polynomials.jsonl"
    snapshot.write_text(
        "".join(json.dumps(item.to_dict()) + "\n" for item in items), encoding="utf-8"
    )
    manifest = tmp_path / "controlled-p30-splits.json"
    report = run_corpus_isolation_and_audit(
        snapshot_path=snapshot,
        output_path=manifest,
        device_name="cpu",
        seed=42,
    )
    assert report["contamination_audit"]["after_audit"]["zero_leakage_verified"]
    for split in ("train", "val", "final_test"):
        assert report["splits"][split]
    assert report["held_out_seal"]["access_count"] == 0
    return manifest
