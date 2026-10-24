"""Tests for constructive bytecode priority engine and greedy constructor (P173)."""

from __future__ import annotations

import itertools
import pickle
import time
from typing import Any

import numpy as np
import pytest

from evobyte.archive import load_checkpoint
from evobyte.bytecode import (
    OPCODE_VERSION,
    encode_instr,
    is_valid,
    nop_program,
)
from evobyte.constructive import evaluate_priority, greedy_construct
from evobyte.vm import execute


def test_opcode_version_bumped_and_v0_compatible(tmp_path: Any) -> None:
    """Test 1: OPCODE_VERSION == 1; v0 golden program bit-identical; v0 passes is_valid; load_checkpoint accepts 0 and 1."""
    assert OPCODE_VERSION == 1

    # Golden v0 program: ADD r7, r0, r1
    prog_v0 = nop_program()
    prog_v0[0] = encode_instr(0x01, dst=7, a=0, b=1)  # ADD r7, r0, r1

    assert is_valid(prog_v0)

    # Execute on fixed input points (x0=3.5, x1=2.25)
    out, invalid = execute(prog_v0, np.float32(3.5), np.float32(2.25))
    assert not invalid
    # Expected output: exactly 5.75
    assert float(out) == 5.75

    # Test load_checkpoint accepts both version 0 and version 1
    ckpt_v0 = tmp_path / "ckpt_v0.pkl"
    with open(ckpt_v0, "wb") as f:
        pickle.dump({"opcode_version": 0, "generation": 10}, f)

    loaded_v0 = load_checkpoint(ckpt_v0)
    assert loaded_v0["opcode_version"] == 0
    assert loaded_v0["generation"] == 10

    ckpt_v1 = tmp_path / "ckpt_v1.pkl"
    with open(ckpt_v1, "wb") as f:
        pickle.dump({"opcode_version": 1, "generation": 20}, f)

    loaded_v1 = load_checkpoint(ckpt_v1)
    assert loaded_v1["opcode_version"] == 1
    assert loaded_v1["generation"] == 20

    # Version 2 must be rejected
    ckpt_v2 = tmp_path / "ckpt_v2.pkl"
    with open(ckpt_v2, "wb") as f:
        pickle.dump({"opcode_version": 2, "generation": 30}, f)

    with pytest.raises(ValueError, match="Checkpoint opcode version mismatch"):
        load_checkpoint(ckpt_v2)


def test_ctx_feat_opcodes_execute() -> None:
    """Test 2: CTX reads ctx[b & 0x0F] (0.0 if out of range); FEAT analogous; 0x12 rejected by is_valid."""
    prog = nop_program()
    # CTX: r2 = ctx[3]
    prog[0] = encode_instr(0x10, dst=2, a=0, b=3)
    # FEAT: r3 = feat[1]
    prog[1] = encode_instr(0x11, dst=3, a=0, b=1)
    # CTX out of range: r4 = ctx[15] (ctx has 4 elements -> out of range -> 0.0)
    prog[2] = encode_instr(0x10, dst=4, a=0, b=15)
    # FEAT out of range: r5 = feat[10] (feat has 3 elements -> out of range -> 0.0)
    prog[3] = encode_instr(0x11, dst=5, a=0, b=10)
    # ADD r7, r2, r3
    prog[4] = encode_instr(0x01, dst=7, a=2, b=3)

    assert is_valid(prog)

    ctx_data = [10.0, 20.0, 30.0, 42.5]
    feat_data = [1.0, 7.5, 3.0]

    out, invalid = execute(prog, np.float32(0.0), ctx=ctx_data, feat=feat_data)
    assert not invalid
    # r2 = 42.5, r3 = 7.5, r7 = 42.5 + 7.5 = 50.0
    assert float(out) == 50.0

    # Also test evaluate_priority executes CTX and FEAT
    res_prio = evaluate_priority(prog, feat_data, ctx_data)
    assert res_prio == 50.0

    # Verify that an invalid opcode 0x12 is rejected by is_valid
    prog_invalid = nop_program()
    # Construct word with opcode 0x12 manually
    prog_invalid[0] = np.uint32(0x12 | (7 << 8))
    assert not is_valid(prog_invalid)


def test_priority_scores_cube_statically() -> None:
    """Test 3: Python priority scores 0/1 vectors above others; equivalent bytecode reproduces exact same ordering."""
    # Bytecode program computing -(x0^2 + x1^2 + x2^2)
    # r0=x0, r1=x1, r2=x2
    prog = nop_program()
    # MUL r3, r0, r0
    prog[0] = encode_instr(0x03, dst=3, a=0, b=0)
    # MUL r4, r1, r1
    prog[1] = encode_instr(0x03, dst=4, a=1, b=1)
    # MUL r5, r2, r2
    prog[2] = encode_instr(0x03, dst=5, a=2, b=2)
    # ADD r6, r3, r4
    prog[3] = encode_instr(0x01, dst=6, a=3, b=4)
    # ADD r7, r6, r5
    prog[4] = encode_instr(0x01, dst=7, a=6, b=5)
    # NEG r7, r7, 0
    prog[5] = encode_instr(0x0C, dst=7, a=7, b=0)

    assert is_valid(prog)

    pts27 = list(itertools.product((0, 1, 2), repeat=3))

    def py_priority(p: tuple[int, int, int]) -> float:
        return -float(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)

    py_scores = [(py_priority(p), idx, p) for idx, p in enumerate(pts27)]
    bc_scores = [(evaluate_priority(prog, list(p), []), idx, p) for idx, p in enumerate(pts27)]

    # Sort both by score descending, tie break by index
    py_sorted = sorted(py_scores, key=lambda item: (-item[0], item[1]))
    bc_sorted = sorted(bc_scores, key=lambda item: (-item[0], item[1]))

    py_points_order = [item[2] for item in py_sorted]
    bc_points_order = [item[2] for item in bc_sorted]

    assert py_points_order == bc_points_order

    # The top 8 points must be the cube {0, 1}^3
    top_8 = set(py_points_order[:8])
    expected_cube = set(itertools.product((0, 1), repeat=3))
    assert top_8 == expected_cube


def test_greedy_builds_cube_instant() -> None:
    """Test 4: Greedy constructor + static priority builds {0,1}^3 in < 0.1s."""
    pts27 = list(itertools.product((0, 1, 2), repeat=3))

    def static_priority(pt: tuple[int, int, int], ctx: dict[str, Any]) -> float:
        # Score higher if coordinates are in {0, 1}
        return -float(pt[0] ** 2 + pt[1] ** 2 + pt[2] ** 2)

    def is_feasible(
        cand: tuple[int, int, int], built: list[tuple[int, int, int]], ctx: dict[str, Any]
    ) -> bool:
        # Candidate cannot form a line (collinear triple) with any pair in built
        for i in range(len(built)):
            p1 = built[i]
            for j in range(i + 1, len(built)):
                p2 = built[j]
                if (
                    (p1[0] + p2[0] + cand[0]) % 3 == 0
                    and (p1[1] + p2[1] + cand[1]) % 3 == 0
                    and (p1[2] + p2[2] + cand[2]) % 3 == 0
                ):
                    return False
        return True

    def is_complete(built: list[tuple[int, int, int]], ctx: dict[str, Any]) -> bool:
        return len(built) == 8

    t0 = time.perf_counter()
    built, steps, evals = greedy_construct(
        pts27,
        priority_fn=static_priority,
        is_feasible_fn=is_feasible,
        is_complete_fn=is_complete,
    )
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.1, f"Greedy cube construction exceeded 0.1s: {elapsed:.4f}s"
    expected_cube = set(itertools.product((0, 1), repeat=3))
    assert len(built) == 8
    assert set(built) == expected_cube
    assert evals > 0
    assert steps == 8


def test_greedy_never_adds_infeasible() -> None:
    """Test 5: is_feasible rejecting a specific point ensures it is never added."""
    candidates = ["A", "B", "C", "D"]
    forbidden = "C"

    def priority_fn(cand: str, ctx: dict[str, Any]) -> float:
        # Highest priority to the forbidden candidate
        if cand == forbidden:
            return 1000.0
        return 1.0

    def is_feasible(cand: str, built: list[str]) -> bool:
        return cand != forbidden

    def is_complete(built: list[str]) -> bool:
        return len(built) >= 3

    built, steps, evals = greedy_construct(
        candidates,
        priority_fn=priority_fn,
        is_feasible_fn=is_feasible,
        is_complete_fn=is_complete,
    )

    assert forbidden not in built
    assert "A" in built
    assert "B" in built
    assert "D" in built
