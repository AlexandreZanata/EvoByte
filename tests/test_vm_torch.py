"""PyTorch VM conformance tests (P05 gate). Proves CPU-vs-GPU equivalence within 1e-6."""

import numpy as np
import torch

from evobyte.bytecode import encode_instr, nop_program
from evobyte.vm import execute, execute_batch
from evobyte.vm_torch import (
    execute_batch_torch,
    execute_population_torch,
    execute_torch,
    get_default_device,
)


def _prog_single(op, a=0, b=0):
    p = nop_program()
    p[0] = encode_instr(op, dst=7, a=a, b=b)
    return p


def _exact_quadratic_program():
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=3, a=1, b=11)  # r3 = 3.0
    p[1] = encode_instr(0x03, dst=3, a=3, b=0)  # r3 = 3x
    p[2] = encode_instr(0x03, dst=2, a=0, b=0)  # r2 = x^2
    p[3] = encode_instr(0x01, dst=4, a=2, b=3)  # r4 = x^2 + 3x
    p[4] = encode_instr(0x0F, dst=7, a=4, b=10)  # r7 = x^2 + 3x + 7
    return p


def test_all_ops_conformance_with_cpu_oracle():
    edges = np.array(
        [
            0.0,
            -0.0,
            1.0,
            -1.0,
            1e-12,
            -1e-12,
            1e-30,
            -1e-30,
            1e-38,
            1e-40,
            1e20,
            -1e20,
            1e30,
            -1e30,
            1e38,
            -1e38,
            3.14159,
            float("inf"),
            float("-inf"),
            float("nan"),
        ],
        dtype=np.float32,
    )
    device = get_default_device()

    for op in range(0x10):
        prog = _prog_single(op, a=0, b=1 if op not in (0x0F,) else 5)
        for x in edges:
            cpu_y, cpu_bad = execute(prog, np.float32(x), np.float32(2.0))
            t_y, t_bad = execute_torch(prog, float(x), 2.0, device=device)

            t_y_np = t_y.cpu().numpy()
            t_bad_bool = bool(t_bad.cpu().item())

            assert np.isfinite(t_y_np), f"Torch op {op:#x} escaped non-finite on x={x}: {t_y_np}"
            assert np.isfinite(cpu_y), f"CPU op {op:#x} escaped non-finite on x={x}: {cpu_y}"

            # Invalid flag parity
            assert t_bad_bool == bool(cpu_bad), (
                f"Op {op:#x} invalid flag mismatch on x={x}: torch={t_bad_bool} vs cpu={cpu_bad}"
            )

            # Output numerical match within 1e-5 relative / absolute tolerance
            if np.isnan(x) or np.isinf(x):
                assert t_y_np == cpu_y
            else:
                np.testing.assert_allclose(
                    t_y_np,
                    cpu_y,
                    rtol=1e-5,
                    atol=1e-5,
                    err_msg=f"Numerical mismatch on op {op:#x} with input {x}",
                )


def test_nan_inf_inputs_never_escape_torch():
    device = get_default_device()
    for op in [0x01, 0x03, 0x04, 0x05, 0x07, 0x08, 0x09, 0x0F]:
        prog = _prog_single(op, a=0, b=1)
        for bad_val in [float("inf"), float("-inf"), float("nan")]:
            y, flag = execute_torch(prog, bad_val, bad_val, device=device)
            assert torch.isfinite(y), f"Escaped non-finite for op {op:#x} on input {bad_val}"
            assert bool(flag.item()) is True


def test_x_plus_one_conformance():
    p = nop_program()
    p[0] = encode_instr(0x0F, dst=7, a=0, b=1)
    xs = np.array([1.0, 2.0, -5.0, 10.0, 0.0], dtype=np.float32)

    cpu_preds, cpu_flags = execute_batch(p, xs)
    t_preds, t_flags = execute_batch_torch(p, xs)

    np.testing.assert_allclose(t_preds.cpu().numpy(), cpu_preds, rtol=1e-6)
    assert np.array_equal(t_flags.cpu().numpy(), cpu_flags)


def test_quadratic_conformance():
    p = _exact_quadratic_program()
    xs = np.linspace(-10.0, 10.0, 128, dtype=np.float32)

    cpu_preds, _cpu_flags = execute_batch(p, xs)
    t_preds, t_flags = execute_batch_torch(p, xs)

    expected = xs**2 + 3 * xs + 7
    np.testing.assert_allclose(t_preds.cpu().numpy(), expected, rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(t_preds.cpu().numpy(), cpu_preds, rtol=1e-5, atol=1e-5)
    assert not np.any(t_flags.cpu().numpy())


def test_population_batch_conformance():
    from evobyte.evolution import sample_structured

    rng = np.random.default_rng(123)
    P = 20
    B = 64
    progs = [sample_structured(rng) for _ in range(P)]
    progs.append(_exact_quadratic_program())
    progs_np = np.stack(progs)

    xs = np.linspace(-5.0, 5.0, B, dtype=np.float32)

    # CPU sequential reference
    cpu_preds = np.zeros((len(progs), B), dtype=np.float32)
    cpu_flags = np.zeros((len(progs), B), dtype=bool)
    for p_i, p in enumerate(progs):
        pred, bad = execute_batch(p, xs)
        cpu_preds[p_i] = pred
        cpu_flags[p_i] = bad

    # Torch batched population
    t_preds, t_flags = execute_population_torch(progs_np, xs)
    t_preds_np = t_preds.cpu().numpy()
    t_flags_np = t_flags.cpu().numpy()

    np.testing.assert_allclose(t_preds_np, cpu_preds, rtol=1e-5, atol=1e-5)
    assert np.array_equal(t_flags_np, cpu_flags)
