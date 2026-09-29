"""Unit tests for elite archive, checkpointing, and Hall of Fame (P07)."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pytest

from evobyte.archive import (
    EliteArchive,
    compute_program_hash,
    is_memorizer,
    load_checkpoint,
    run_resume_selftest,
    save_checkpoint,
    write_hall_of_fame_entry,
)
from evobyte.bytecode import OPCODE_VERSION, encode_instr, nop_program


def test_archive_add_and_retrieve_by_hash(tmp_path: Path) -> None:
    db_file = tmp_path / "elites.db"
    archive = EliteArchive(db_file)

    prog = np.zeros(16, dtype=np.uint32)
    prog[0] = encode_instr(0x01, 7, 0, 1)  # ADD r7 = r0 + r1
    sha = compute_program_hash(prog)

    inserted = archive.add_elite(
        program=prog,
        generation=12,
        fitness=0.045,
        train_error=0.04,
        validation_error=0.042,
        test_error=0.043,
        complexity=2.5,
        parents=["p1_sha", "p2_sha"],
        mutation_history="single_point_cross+point_mut",
        novelty_score=0.88,
    )
    assert inserted is True
    assert archive.count() == 1

    row = archive.get_by_hash(sha)
    assert row is not None
    assert row["sha256"] == sha
    assert row["generation"] == 12
    assert row["opcode_version"] == OPCODE_VERSION
    assert row["fitness"] == pytest.approx(0.045)
    assert row["train_error"] == pytest.approx(0.04)
    assert row["validation_error"] == pytest.approx(0.042)
    assert row["test_error"] == pytest.approx(0.043)
    assert row["complexity"] == pytest.approx(2.5)
    assert json.loads(row["parents"]) == ["p1_sha", "p2_sha"]
    assert row["mutation_history"] == "single_point_cross+point_mut"
    assert row["novelty_score"] == pytest.approx(0.88)
    assert row["timestamp"] > 0

    restored_prog = np.frombuffer(row["candidate_binary"], dtype=np.uint32)
    assert np.array_equal(restored_prog, prog)
    archive.close()


def test_archive_dedup(tmp_path: Path) -> None:
    archive = EliteArchive(tmp_path / "dedup.db")
    prog = nop_program()

    ins1 = archive.add_elite(prog, generation=1, fitness=1.0, train_error=1.0)
    assert ins1 is True
    assert archive.count() == 1

    # Re-inserting the same binary should be deduplicated (return False, count stays 1)
    ins2 = archive.add_elite(prog, generation=2, fitness=0.5, train_error=0.5)
    assert ins2 is False
    assert archive.count() == 1
    archive.close()


def test_archive_get_elites_ordering(tmp_path: Path) -> None:
    archive = EliteArchive()  # in-memory SQLite

    p1 = np.zeros(16, dtype=np.uint32)
    p1[0] = encode_instr(0x01, 7, 0, 1)

    p2 = np.zeros(16, dtype=np.uint32)
    p2[0] = encode_instr(0x02, 7, 0, 1)

    p3 = np.zeros(16, dtype=np.uint32)
    p3[0] = encode_instr(0x03, 7, 0, 1)

    archive.add_elite(p1, generation=10, fitness=0.5, train_error=0.5, novelty_score=0.1)
    archive.add_elite(p2, generation=5, fitness=0.1, train_error=0.1, novelty_score=0.9)
    archive.add_elite(p3, generation=20, fitness=0.3, train_error=0.3, novelty_score=0.5)

    # Order by fitness ASC
    by_fit = archive.get_elites(limit=3, order_by="fitness")
    assert [r["fitness"] for r in by_fit] == pytest.approx([0.1, 0.3, 0.5])

    # Order by novelty DESC
    by_nov = archive.get_elites(limit=3, order_by="novelty")
    assert [r["novelty_score"] for r in by_nov] == pytest.approx([0.9, 0.5, 0.1])

    # Order by generation DESC
    by_gen = archive.get_elites(limit=3, order_by="generation")
    assert [r["generation"] for r in by_gen] == [20, 10, 5]

    archive.close()


def test_archive_context_manager(tmp_path: Path) -> None:
    db_file = tmp_path / "ctx.db"
    prog = nop_program()
    with EliteArchive(db_file) as arch:
        arch.add_elite(prog, generation=1, fitness=0.1, train_error=0.1)
        assert arch.count() == 1


def test_checkpoint_save_and_load(tmp_path: Path) -> None:
    ckpt_file = tmp_path / "checkpoint.pkl"
    rng = np.random.default_rng(999)
    pop = np.stack([nop_program() for _ in range(5)])

    state = {
        "generation": 42,
        "rng_state": rng.bit_generator.state,
        "population": pop,
    }
    save_checkpoint(ckpt_file, state)
    assert ckpt_file.exists()

    loaded = load_checkpoint(ckpt_file)
    assert loaded["generation"] == 42
    assert loaded["opcode_version"] == OPCODE_VERSION
    assert loaded["timestamp"] > 0
    assert np.array_equal(loaded["population"], pop)
    assert loaded["rng_state"]["state"]["state"] == rng.bit_generator.state["state"]["state"]


def test_checkpoint_version_mismatch(tmp_path: Path) -> None:
    ckpt_file = tmp_path / "invalid_ver.pkl"
    bad_state = {
        "generation": 1,
        "opcode_version": 9999,  # Incompatible version
    }
    with open(ckpt_file, "wb") as f:
        pickle.dump(bad_state, f)

    with pytest.raises(ValueError, match="Checkpoint opcode version mismatch"):
        load_checkpoint(ckpt_file)


def test_hall_of_fame_writer_non_memorizer(tmp_path: Path) -> None:
    fame_file = tmp_path / "fame.jsonl"
    entry = {
        "rank": 1,
        "fitness": 0.0075,
        "expression": "CSEL r2, r7, 0x0b ; ADD r7, r6, 0x03",
        "generation": 50,
        "discovered_after_N_candidates": 15000,
        "train_error": 0.0,
        "validation_error": 0.001,
        "val_gap": 0.001,
        "complexity": 7.5,
        "parents": ["pA", "pB"],
        "hash": "b09aafbf1c7e4820",
    }
    written = write_hall_of_fame_entry(fame_file, entry)
    assert written is True
    assert fame_file.exists()

    with open(fame_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["rank"] == 1
    assert record["hash"] == "b09aafbf1c7e4820"
    assert record["fitness"] == pytest.approx(0.0075)
    assert record["val_gap"] == pytest.approx(0.001)


def test_hall_of_fame_writer_rejects_memorizer(tmp_path: Path) -> None:
    fame_file = tmp_path / "fame_reject.jsonl"

    # Memorizer due to val_error > 2*train_err + 0.05
    mem1 = {
        "rank": 1,
        "fitness": 0.01,
        "expression": "overfit",
        "generation": 10,
        "train_error": 0.01,
        "validation_error": 0.20,
        "val_gap": 0.19,
    }
    assert write_hall_of_fame_entry(fame_file, mem1) is False

    # Memorizer due to val_gap > 0.05
    mem2 = {
        "rank": 1,
        "fitness": 0.01,
        "expression": "overfit_gap",
        "generation": 10,
        "train_error": 0.1,
        "validation_error": 0.18,
        "val_gap": 0.08,
    }
    assert write_hall_of_fame_entry(fame_file, mem2) is False

    # Memorizer due to extrapolation_error
    mem3 = {
        "rank": 1,
        "fitness": 0.01,
        "expression": "overfit_extrap",
        "generation": 10,
        "train_error": 0.01,
        "validation_error": 0.02,
        "val_gap": 0.01,
        "extrapolation_error": 0.8,
    }
    assert write_hall_of_fame_entry(fame_file, mem3) is False

    # File should not exist or be empty
    if fame_file.exists():
        with open(fame_file, "r", encoding="utf-8") as f:
            assert len(f.readlines()) == 0


def test_resume_equivalence(tmp_path: Path) -> None:
    success = run_resume_selftest(seed=42, checkpoint_dir=tmp_path)
    assert success is True
