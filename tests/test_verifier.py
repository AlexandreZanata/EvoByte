"""Verifier tests (P04 gate, runnable already on the skeleton)."""

import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "benchmarks"))

from benchmarks.open_problems import (
    P63_REJECTION_CODES,
    check_erdos_straus,
    check_erdos_straus_fractions,
    p63_code_tensor,
    p63_rejection_code,
    p63_scalar_score,
    p63_shuffle_codes,
)
from evobyte.bytecode import encode_instr, nop_program
from evobyte.verifier import (
    cascade_evaluate,
    cascade_evaluate_population,
    complexity,
    evaluate,
    score_predictions,
)


def _x2_program():
    # r2 = r0*r0 ; r7 = r2 + 0  (shape check only; not exact target)
    p = nop_program()
    p[0] = encode_instr(0x03, dst=2, a=0, b=0)
    p[1] = encode_instr(0x01, dst=7, a=2, b=2)
    return p


def test_complexity_counts():
    p = nop_program()
    assert complexity(p) == 0.0
    assert complexity(_x2_program()) > 0.0


def test_evaluate_finite():
    xs = np.linspace(-2, 2, 64, dtype=np.float32)
    ys = xs * xs
    out = evaluate(_x2_program(), xs, ys)
    assert np.isfinite(out["fitness"])
    assert "norm_err" in out
    assert "mae" in out


def test_invalid_program_dies_at_s0():
    # NOP-only program is invalid
    bad_p = nop_program()
    out = cascade_evaluate(
        bad_p, np.linspace(-2, 2, 32, dtype=np.float32), np.zeros(32, dtype=np.float32)
    )
    assert out["stage"] == 0
    assert out["killed"] is True
    assert out["fitness"] >= 1e9


def test_cascade_kills_bad_fast():
    xs = np.linspace(-10, 10, 512, dtype=np.float32)
    ys = xs * xs + 3 * xs + 7
    bad = nop_program()
    bad[0] = encode_instr(0x05, dst=7, a=0, b=0)  # sin(x) vs quadratic
    out = cascade_evaluate(bad, xs, ys, elite_err=1e-6, k=4.0)
    assert out["killed"] is True
    assert out["stage"] == 1


def _exact_quadratic_program():
    # y = x^2 + 3x + 7
    # CONST_BANK[11] == 3.0, CONST_BANK[10] == 7.0
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = r1 + 3.0 = 3.0
    p[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = r3 * r0 = 3x
    p[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = r0 * r0 = x^2
    p[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = r2 + r3 = x^2 + 3x
    p[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = r4 + 7.0 = x^2 + 3x + 7
    return p


def test_elite_survives_all_stages():
    xs = np.linspace(-10, 10, 1024, dtype=np.float32)
    ys = xs * xs + 3 * xs + 7
    elite = _exact_quadratic_program()
    out = cascade_evaluate(elite, xs, ys, elite_err=1e-6, k=4.0)
    assert out["killed"] is False
    assert out["stage"] == 3
    assert out["mse"] < 1e-6


def test_anti_memorization_val_gap():
    # Model that fits training perfectly but diverges on validation
    train_pred = np.array([1.0, 2.0, 3.0])
    train_target = np.array([1.0, 2.0, 3.0])
    val_pred = np.array([10.0, 20.0, 30.0])
    val_target = np.array([1.0, 2.0, 3.0])
    invalid = np.array([False, False, False])

    score_without_val = score_predictions(train_pred, train_target, invalid, comp=1.0)
    score_with_val = score_predictions(
        train_pred, train_target, invalid, comp=1.0, val_pred=val_pred, val_target=val_target
    )
    # score_with_val should be higher (worse) due to validation gap penalty
    assert score_with_val > score_without_val


def test_cascade_evaluate_population_accounting():
    xs = np.linspace(-10, 10, 512, dtype=np.float32)
    ys = xs * xs + 3 * xs + 7

    # Population of:
    # 2 invalid programs (should die at S0)
    # 2 poor fits (sin(x), cos(x), should die at S1)
    # 1 exact program (should survive)
    p_sin = nop_program()
    p_sin[0] = encode_instr(0x05, dst=7, a=0, b=0)
    p_cos = nop_program()
    p_cos[0] = encode_instr(0x06, dst=7, a=0, b=0)
    pop = [nop_program(), nop_program(), p_sin, p_cos, _exact_quadratic_program()]

    stats = cascade_evaluate_population(pop, xs, ys, elite_err=1e-6, k=4.0)
    assert stats["total"] == 5
    assert stats["stage_kills"][0] == 2  # 2 killed at S0
    assert stats["stage_kills"][1] == 2  # 2 killed at S1
    assert stats["survivors"] == 1  # 1 exact survived
    assert (
        stats["stage_kills"][0]
        + stats["stage_kills"][1]
        + stats["stage_kills"][2]
        + stats["stage_kills"][3]
        + stats["survivors"]
        == 5
    )


def test_hidden_never_imported_in_src():
    import subprocess

    result = subprocess.run(
        ["grep", "-rn", "hidden", "src/"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, f"Found forbidden 'hidden' reference in src/:\n{result.stdout}"


def test_p63_rejection_codebook_frozen() -> None:
    assert P63_REJECTION_CODES == {
        "ACCEPT": 0,
        "ZERO_DENOMINATOR": 1,
        "BOUND_VIOLATED": 2,
        "NONZERO_RESIDUAL": 3,
        "INVALID_DOMAIN": 4,
        "INCOMPLETE_PROOF": 5,
    }


def test_p63_rejection_codes_cover_cases() -> None:
    C = P63_REJECTION_CODES
    assert p63_rejection_code(4, 2, 3, 6) == C["ACCEPT"]
    assert p63_rejection_code(4, 2, 3, 7) == C["NONZERO_RESIDUAL"]
    assert p63_rejection_code(4, 0, 3, 6) == C["INVALID_DOMAIN"]
    assert p63_rejection_code(4, -1, 3, 6) == C["INVALID_DOMAIN"]
    assert p63_rejection_code(4, 1, 1, 10**9 + 1) == C["BOUND_VIOLATED"]
    assert p63_rejection_code(4, 2, 2, 5) == C["ZERO_DENOMINATOR"]


def test_p63_false_stays_false_and_accept_matches_checkers() -> None:
    C = P63_REJECTION_CODES
    for n in (4, 5, 6):
        for x in range(1, 16):
            for y in range(1, 16):
                for z in range(1, 16):
                    code = p63_rejection_code(n, x, y, z)
                    ok1, _, _ = check_erdos_straus(n, x, y, z)
                    ok2 = code == C["ACCEPT"]
                    ok3, _, _ = check_erdos_straus_fractions(n, x, y, z)
                    assert ok2 == (ok1 and ok3)
                    if not (ok1 and ok3):
                        assert code != C["ACCEPT"]


def test_p63_tensor_shuffle_scalar() -> None:

    C = P63_REJECTION_CODES
    t = p63_code_tensor([0, 3, 5])
    assert t.shape == (3, 6)
    assert t[0, C["ACCEPT"]].item() == 1.0
    assert t[1].sum().item() == 1.0
    assert p63_shuffle_codes(7) == p63_shuffle_codes(7)
    perm = p63_shuffle_codes(7)
    assert sorted(perm.values()) == list(range(6))
    assert p63_scalar_score(4, 2, 3, 6) == 1.0
    s = p63_scalar_score(4, 2, 3, 7)
    assert 0.0 < s < 1.0
    assert p63_scalar_score(4, 0, 3, 6) == 0.0
    assert p63_scalar_score(4, 2, 3, 6) > p63_scalar_score(4, 2, 3, 7)


def _p63_strip(rec):
    return {
        arm: {k: v for k, v in arm_rec.items() if k != "loop_sec"} for arm, arm_rec in rec.items()
    }


def test_p63_compare_arms_deterministic_and_counted() -> None:
    from benchmarks.open_problems import p63_compare_feedback_arms

    starts = [(2, 3, 7), (5, 5, 5)]
    first = p63_compare_feedback_arms(4, starts, max_cycles=6)
    second = p63_compare_feedback_arms(4, starts, max_cycles=6)
    assert _p63_strip(first) == _p63_strip(second)
    assert set(first) == {"real", "shuffled", "scalar"}
    for rec in first.values():
        assert rec["starts"] == len(starts)
        assert rec["queries_total"] > 0
        assert rec["loop_sec"] >= 0.0
        for det in rec["details"]:
            assert det["status"] in ("certified", "stalled", "exhausted", "query-capped")
            if det["status"] == "certified":
                assert check_erdos_straus(4, *det["triple"])[0] is True
    assert first["real"]["queries_total"] >= first["scalar"]["queries_total"]


def test_p63_query_cap_and_unknown_arm() -> None:
    import pytest

    from benchmarks.open_problems import (
        P63_CODE_PRIORITY,
        p63_compare_feedback_arms,
        p63_neighbor_key,
    )

    assert P63_CODE_PRIORITY == (0, 3, 4, 2, 5, 1)
    rec = p63_compare_feedback_arms(4, [(5, 5, 5)], max_cycles=12, query_limit=1)
    for arm_rec in rec.values():
        assert [d["status"] for d in arm_rec["details"]] == ["query-capped"]
    with pytest.raises(ValueError, match="Unknown P63 feedback arm"):
        p63_neighbor_key("oracle", 0, 0, (1, 1, 1), {})
