"""PyTorch batched reference interpreter with exact safe-math semantics (spec: docs/VM.md)."""

from __future__ import annotations

import numpy as np
import torch

from evobyte.bytecode import CONST_BANK, N_INSTR, N_REGS, decode_instr

CLAMP_VAL = 1e30
TWO_PI = 2.0 * float(np.pi)
BINARY_OPS = frozenset({0x01, 0x02, 0x03, 0x04, 0x09, 0x0D, 0x0E})


def get_default_device() -> torch.device:
    """Return cuda if available, else cpu."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_const_bank_tensor(device: torch.device | None = None) -> torch.Tensor:
    """Return constant bank as a 1D float32 PyTorch tensor on target device."""
    return torch.tensor(CONST_BANK, dtype=torch.float32, device=device)


def _safe_apply_torch(
    op: int,
    ra: torch.Tensor,
    rb: torch.Tensor,
    b_raw: int,
    const_bank: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Vectorized safe-math application of one opcode on PyTorch tensors."""
    invalid = torch.zeros_like(ra, dtype=torch.bool)
    a = ra
    b = rb

    # Input sanitization
    not_finite_a = ~torch.isfinite(a)
    invalid = invalid | not_finite_a
    a = torch.where(not_finite_a, torch.zeros_like(a), a)

    if op in BINARY_OPS:
        not_finite_b = ~torch.isfinite(b)
        invalid = invalid | not_finite_b
        b = torch.where(not_finite_b, torch.zeros_like(b), b)

    if op == 0x01:  # ADD
        out = a + b
    elif op == 0x02:  # SUB
        out = a - b
    elif op == 0x03:  # MUL
        out = a * b
    elif op == 0x04:  # DIV
        near_zero = torch.abs(b.double()) < 1e-12
        invalid = invalid | near_zero
        safe_b = torch.where(near_zero, torch.ones_like(b), b)
        out = torch.where(near_zero, torch.zeros_like(a), a / safe_b)
    elif op == 0x05:  # SIN
        red_a = torch.remainder(a, TWO_PI)
        out = torch.sin(red_a)
    elif op == 0x06:  # COS
        red_a = torch.remainder(a, TWO_PI)
        out = torch.cos(red_a)
    elif op == 0x07:  # EXP
        a_d = a.double()
        out_of_range = (a_d > 20.0) | (a_d < -20.0)
        invalid = invalid | out_of_range
        safe_a = torch.clamp(a, -20.0, 20.0)
        out = torch.where(out_of_range, torch.zeros_like(a), torch.exp(safe_a))
    elif op == 0x08:  # LOG
        abs_a = torch.abs(a)
        near_zero = abs_a.double() < 1e-12
        invalid = invalid | near_zero
        safe_a = torch.where(near_zero, torch.ones_like(abs_a), abs_a)
        out = torch.where(near_zero, torch.zeros_like(a), torch.log(safe_a))
    elif op == 0x09:  # POW
        abs_a = torch.abs(a)
        clamped_b = torch.clamp(b, -6.0, 6.0)
        zero_div = (abs_a.double() < 1e-12) & (clamped_b < 0.0)
        invalid = invalid | zero_div
        safe_base = torch.where(zero_div, torch.ones_like(abs_a), abs_a)
        out = torch.where(zero_div, torch.zeros_like(abs_a), torch.pow(safe_base, clamped_b))
    elif op == 0x0A:  # ABS
        out = torch.abs(a)
    elif op == 0x0B:  # SQRT
        out = torch.sqrt(torch.abs(a))
    elif op == 0x0C:  # NEG
        out = -a
    elif op == 0x0D:  # MIN
        out = torch.minimum(a, b)
    elif op == 0x0E:  # MAX
        out = torch.maximum(a, b)
    elif op == 0x0F:  # CSEL: ra + const[b & 0xF]
        idx = int(b_raw) & 0x0F
        c_val = const_bank[idx]
        out = a + c_val
    else:
        out = torch.zeros_like(a)
        invalid = invalid | True

    # Output guards
    not_finite_out = ~torch.isfinite(out)
    invalid = invalid | not_finite_out
    out = torch.where(not_finite_out, torch.zeros_like(out), out)

    too_large = torch.abs(out) > CLAMP_VAL
    invalid = invalid | too_large
    out = torch.clamp(out, -CLAMP_VAL, CLAMP_VAL)

    subnormal = (out != 0.0) & (torch.abs(out) < 1e-38)
    out = torch.where(subnormal, torch.zeros_like(out), out)

    return out, invalid


def execute_batch_torch(
    program: np.ndarray | torch.Tensor,
    xs: np.ndarray | torch.Tensor,
    x1s: np.ndarray | torch.Tensor | None = None,
    device: torch.device | str | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Execute one program over a batch of input points fully in PyTorch."""
    if device is None:
        device = get_default_device()
    else:
        device = torch.device(device)

    const_bank = get_const_bank_tensor(device)

    if isinstance(xs, np.ndarray):
        xs_t = torch.from_numpy(xs.astype(np.float32)).to(device)
    else:
        xs_t = xs.to(dtype=torch.float32, device=device)
    xs_t = xs_t.ravel()
    b_size = xs_t.shape[0]

    if x1s is not None:
        if isinstance(x1s, np.ndarray):
            x1s_t = torch.from_numpy(x1s.astype(np.float32)).to(device)
        else:
            x1s_t = x1s.to(dtype=torch.float32, device=device)
        x1s_t = x1s_t.ravel()
    else:
        x1s_t = torch.zeros_like(xs_t)

    regs = torch.zeros((N_REGS, b_size), dtype=torch.float32, device=device)
    regs[0] = xs_t
    regs[1] = x1s_t

    overall_invalid = torch.zeros(b_size, dtype=torch.bool, device=device)
    bad_x0 = ~torch.isfinite(regs[0])
    bad_x1 = ~torch.isfinite(regs[1])
    overall_invalid = overall_invalid | bad_x0 | bad_x1
    regs[0] = torch.where(bad_x0, torch.zeros_like(regs[0]), regs[0])
    regs[1] = torch.where(bad_x1, torch.zeros_like(regs[1]), regs[1])

    if isinstance(program, torch.Tensor):
        prog_np = program.cpu().numpy().astype(np.uint32)
    else:
        prog_np = np.asarray(program, dtype=np.uint32)

    for i in range(N_INSTR):
        op, dst, a, b = decode_instr(prog_np[i])
        if op == 0x00:
            continue
        if dst >= N_REGS or a >= N_REGS:
            overall_invalid = overall_invalid | True
            continue
        if op in BINARY_OPS and b >= N_REGS:
            overall_invalid = overall_invalid | True

        rb = regs[b % N_REGS]
        out, flag = _safe_apply_torch(op, regs[a], rb, b, const_bank)
        regs[dst] = out
        overall_invalid = overall_invalid | flag

    final = regs[7]
    bad_final = ~torch.isfinite(final)
    overall_invalid = overall_invalid | bad_final
    final = torch.where(bad_final, torch.zeros_like(final), final)
    return final, overall_invalid


def execute_torch(
    program: np.ndarray | torch.Tensor,
    x0: float | torch.Tensor,
    x1: float | torch.Tensor = 0.0,
    device: torch.device | str | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Execute one program on a single input point in PyTorch."""
    if not isinstance(x0, torch.Tensor):
        xs = torch.tensor([float(x0)], dtype=torch.float32)
    else:
        xs = x0.view(1)
    if not isinstance(x1, torch.Tensor):
        x1s = torch.tensor([float(x1)], dtype=torch.float32)
    else:
        x1s = x1.view(1)
    out, flag = execute_batch_torch(program, xs, x1s, device=device)
    return out[0], flag[0]


def execute_population_torch(
    programs: np.ndarray | torch.Tensor,
    xs: np.ndarray | torch.Tensor,
    x1s: np.ndarray | torch.Tensor | None = None,
    device: torch.device | str | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Execute a population of P programs across B data points in parallel on device."""
    if device is None:
        device = get_default_device()
    else:
        device = torch.device(device)

    const_bank = get_const_bank_tensor(device)

    if isinstance(programs, torch.Tensor):
        progs_np = programs.cpu().numpy().astype(np.uint32)
    else:
        progs_np = np.asarray(programs, dtype=np.uint32)

    P = progs_np.shape[0]

    if isinstance(xs, np.ndarray):
        xs_t = torch.from_numpy(xs.astype(np.float32)).to(device)
    else:
        xs_t = xs.to(dtype=torch.float32, device=device)
    xs_t = xs_t.ravel()
    B = xs_t.shape[0]

    if x1s is not None:
        if isinstance(x1s, np.ndarray):
            x1s_t = torch.from_numpy(x1s.astype(np.float32)).to(device)
        else:
            x1s_t = x1s.to(dtype=torch.float32, device=device)
        x1s_t = x1s_t.ravel()
    else:
        x1s_t = torch.zeros_like(xs_t)

    # Initialize registers tensor: shape (P, N_REGS, B)
    regs = torch.zeros((P, N_REGS, B), dtype=torch.float32, device=device)
    regs[:, 0, :] = xs_t.unsqueeze(0).expand(P, -1)
    regs[:, 1, :] = x1s_t.unsqueeze(0).expand(P, -1)

    overall_invalid = torch.zeros((P, B), dtype=torch.bool, device=device)
    bad_x0 = (~torch.isfinite(regs[:, 0, :])).any(dim=1, keepdim=True)
    bad_x1 = (~torch.isfinite(regs[:, 1, :])).any(dim=1, keepdim=True)
    overall_invalid = overall_invalid | bad_x0 | bad_x1

    for step in range(N_INSTR):
        words = progs_np[:, step]
        ops = words & 0xFF
        dsts = (words >> 8) & 0xFF
        as_ = (words >> 16) & 0xFF
        bs = (words >> 24) & 0xFF

        unique_ops = np.unique(ops)
        for op in unique_ops:
            if op == 0x00:
                continue
            idx_p = np.where(ops == op)[0]
            if len(idx_p) == 0:
                continue

            for p_idx in idx_p:
                dst = int(dsts[p_idx])
                a = int(as_[p_idx])
                b = int(bs[p_idx])

                if dst >= N_REGS or a >= N_REGS:
                    overall_invalid[p_idx, :] = True
                    continue

                if op in BINARY_OPS and b >= N_REGS:
                    overall_invalid[p_idx, :] = True

                rb = regs[p_idx, b % N_REGS, :]
                out, flag = _safe_apply_torch(int(op), regs[p_idx, a, :], rb, b, const_bank)
                regs[p_idx, dst, :] = out
                overall_invalid[p_idx, :] = overall_invalid[p_idx, :] | flag

    final = regs[:, 7, :]
    bad_final = ~torch.isfinite(final)
    overall_invalid = overall_invalid | bad_final
    final = torch.where(bad_final, torch.zeros_like(final), final)
    return final, overall_invalid
