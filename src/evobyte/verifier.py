"""Level-1 scoring + cascade + early stop (spec: docs/VERIFIER.md)."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from evobyte.bytecode import CONST_BANK, OPCODE_VERSION, decode_human, decode_instr, is_valid
from evobyte.vm import execute_batch, execute_batch_f64

try:
    import sympy

    _HAS_SYMPY = True
except ImportError:
    sympy = None  # type: ignore
    _HAS_SYMPY = False

W_ERR = 1.0
W_COMPLEXITY = 1e-3
W_INVALID = 1.0
W_VAL_GAP = 0.5
PENALTY_INVALID = 1e9


def complexity(program: np.ndarray) -> float:
    """Cheap parsimony: non-NOP count + 0.5 * distinct ops."""
    ops = set()
    count = 0
    for word in program:
        op = int(word) & 0xFF
        if op == 0x00:
            continue
        count += 1
        ops.add(op)
    return float(count) + 0.5 * float(len(ops))


def score_predictions(
    pred: np.ndarray,
    target: np.ndarray,
    invalid: np.ndarray,
    comp: float,
    val_pred: np.ndarray | None = None,
    val_target: np.ndarray | None = None,
) -> float:
    """Scalar fitness (lower is better). All inputs finite by VM contract."""
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    mse = float(np.mean((pred - target) ** 2))
    mae = float(np.mean(np.abs(pred - target)))
    norm_err = mse + 0.1 * mae
    invalid_rate = float(np.mean(invalid)) if invalid.size else 0.0

    val_gap = 0.0
    if val_pred is not None and val_target is not None:
        val_pred = np.asarray(val_pred, dtype=np.float64)
        val_target = np.asarray(val_target, dtype=np.float64)
        val_mse = float(np.mean((val_pred - val_target) ** 2))
        val_mae = float(np.mean(np.abs(val_pred - val_target)))
        val_err = val_mse + 0.1 * val_mae
        val_gap = max(0.0, val_err - norm_err)

    return W_ERR * norm_err + W_COMPLEXITY * comp + W_INVALID * invalid_rate + W_VAL_GAP * val_gap


def evaluate(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    val_xs: np.ndarray | None = None,
    val_ys: np.ndarray | None = None,
) -> dict:
    """Full S3-style evaluation of one program on (xs, ys) with optional validation set."""
    pred, invalid = execute_batch(program, xs)
    comp = complexity(program)

    val_pred = None
    if val_xs is not None and val_ys is not None:
        val_pred, _ = execute_batch(program, val_xs)

    fitness = score_predictions(pred, ys, invalid, comp, val_pred=val_pred, val_target=val_ys)
    mse = float(np.mean((np.asarray(pred, float) - np.asarray(ys, float)) ** 2))
    mae = float(np.mean(np.abs(np.asarray(pred, float) - np.asarray(ys, float))))
    norm_err = mse + 0.1 * mae

    val_gap = 0.0
    if val_pred is not None and val_ys is not None:
        val_mse = float(np.mean((np.asarray(val_pred, float) - np.asarray(val_ys, float)) ** 2))
        val_mae = float(np.mean(np.abs(np.asarray(val_pred, float) - np.asarray(val_ys, float))))
        val_gap = max(0.0, (val_mse + 0.1 * val_mae) - norm_err)

    return {
        "fitness": fitness,
        "mse": mse,
        "mae": mae,
        "norm_err": norm_err,
        "complexity": comp,
        "invalid_rate": float(np.mean(invalid)) if invalid.size else 0.0,
        "val_gap": val_gap,
    }


def cascade_evaluate(
    program: np.ndarray,
    xs: np.ndarray,
    ys: np.ndarray,
    elite_err: float = 1.0,
    k: float = 4.0,
    val_xs: np.ndarray | None = None,
    val_ys: np.ndarray | None = None,
) -> dict:
    """S0(validity) -> S1(32) -> S2(256) -> S3(up to 4096) with early termination.

    Returns dict with stage reached, fitness, and kill flag.
    """
    comp = complexity(program)
    if not is_valid(program):
        return {
            "stage": 0,
            "fitness": PENALTY_INVALID,
            "mse": float("inf"),
            "mae": float("inf"),
            "norm_err": float("inf"),
            "killed": True,
            "complexity": comp,
            "invalid_rate": 1.0,
            "val_gap": 0.0,
        }

    n = len(xs)
    stage_sizes = [min(32, n), min(256, n), min(4096, n)]
    stages = []
    for s in stage_sizes:
        if not stages or s > stages[-1]:
            stages.append(s)

    last_sub = None
    for stage_i, m in enumerate(stages):
        sub = evaluate(program, xs[:m], ys[:m])
        last_sub = sub
        if m >= 8 and sub["norm_err"] > k * max(elite_err, 1e-12):
            return {
                "stage": stage_i + 1,
                "fitness": sub["fitness"],
                "mse": sub["mse"],
                "mae": sub["mae"],
                "norm_err": sub["norm_err"],
                "killed": True,
                "complexity": comp,
                "invalid_rate": sub["invalid_rate"],
                "val_gap": sub["val_gap"],
            }

    if val_xs is not None and val_ys is not None:
        last_sub = evaluate(program, xs[: stages[-1]], ys[: stages[-1]], val_xs, val_ys)

    return {
        "stage": len(stages),
        "fitness": last_sub["fitness"],
        "mse": last_sub["mse"],
        "mae": last_sub["mae"],
        "norm_err": last_sub["norm_err"],
        "killed": False,
        "complexity": comp,
        "invalid_rate": last_sub["invalid_rate"],
        "val_gap": last_sub["val_gap"],
    }


def cascade_evaluate_population(
    programs: list[np.ndarray],
    xs: np.ndarray,
    ys: np.ndarray,
    elite_err: float = 1.0,
    k: float = 4.0,
) -> dict:
    """Evaluate a population of candidates through the cascade and report stage accounting."""
    results = []
    total = len(programs)
    stage_kills = {0: 0, 1: 0, 2: 0, 3: 0}

    for prog in programs:
        res = cascade_evaluate(prog, xs, ys, elite_err=elite_err, k=k)
        results.append(res)
        if res["killed"]:
            st = res["stage"]
            stage_kills[st] = stage_kills.get(st, 0) + 1

    stage_survivors = {}
    current = total
    for s in range(4):
        stage_survivors[s] = current
        current = max(0, current - stage_kills.get(s, 0))

    final_survivors = sum(1 for r in results if not r["killed"])
    kill_rates = {s: (stage_kills.get(s, 0) / total) if total else 0.0 for s in range(4)}

    return {
        "results": results,
        "total": total,
        "stage_survivors": stage_survivors,
        "stage_kills": stage_kills,
        "kill_rates": kill_rates,
        "survivors": final_survivors,
        "survival_rate": final_survivors / total if total else 0.0,
    }


# --- Level-2 Strict Verification & Discovery Evidence (P19 Scope) ---


@dataclass
class L2VerificationResult:
    """Outcome of Level-2 strict evaluation."""

    passed: bool
    decision: str
    reasons: list[str]
    f64_test_mse: float
    f32_test_mse: float
    f64_f32_divergence: float
    train_mse: float
    val_mse: float | None
    extrap_mse: float | None
    adversarial_invalid_rate: float
    ordinary_math_valid: bool
    ordinary_math_error: str | None
    symbolic_equivalent: bool
    symbolic_expression: str
    symbolic_notes: str
    proof_type: str
    tolerance: float
    domain: str
    exported_candidate: dict[str, Any]


def _exact_constant(value: float) -> Any:
    """Map a float constant to its exact symbolic value (P42).

    Integral floats become Integers and finite decimals become exact Rationals
    of their decimal expansion. Non-representable values (NaN/inf) and
    transcendental approximations (pi/e slots) stay Float, which confines any
    identity involving them to numerical evidence, never an exact certificate.
    """
    if not _HAS_SYMPY:
        return None
    v = float(value)
    if not math.isfinite(v):
        return sympy.Float(v)
    if v.is_integer():
        return sympy.Integer(int(v))
    return sympy.Rational(str(v))


def _unified_symbol(var_name: str) -> Any:
    """Single assumed symbol shared by program and target expressions."""
    return sympy.Symbol(var_name, real=True)


def _unify_symbols(expr: Any, var_name: str) -> Any:
    """Rewrite every same-named free symbol to the single assumed symbol."""
    if expr is None:
        return None
    x = _unified_symbol(var_name)
    try:
        mapping = {s: x for s in expr.free_symbols if s.name == var_name}
    except AttributeError:
        return expr
    return expr.xreplace(mapping) if mapping else expr


def program_to_sympy(
    program: np.ndarray,
    const_bank: np.ndarray | None = None,
    linear_head: tuple[float, float] = (1.0, 0.0),
    var_name: str = "x",
) -> Any:
    """Build a simplified SymPy expression from bytecode, constants, and linear head."""
    if not _HAS_SYMPY:
        return None
    x = _unified_symbol(var_name)
    regs = [sympy.Integer(0)] * 8
    regs[0] = x
    bank = const_bank if const_bank is not None else CONST_BANK

    for word in program:
        op, dst, a, b_raw = decode_instr(word)
        if op == 0x00:
            continue
        if dst >= 8 or a >= 8:
            continue

        ra = regs[a]
        if op == 0x0F:  # CSEL: ra + const[b & 0xF]
            b_idx = int(b_raw) & 0x0F
            c_val = bank[b_idx] if b_idx < len(bank) else 0.0
            regs[dst] = ra + _exact_constant(float(c_val))
            continue

        b = int(b_raw)
        rb = regs[b % 8]

        try:
            if op == 0x01:  # ADD
                regs[dst] = ra + rb
            elif op == 0x02:  # SUB
                regs[dst] = ra - rb
            elif op == 0x03:  # MUL
                regs[dst] = ra * rb
            elif op == 0x04:  # DIV
                regs[dst] = ra / rb if rb != 0 else sympy.nan
            elif op == 0x05:  # SIN
                regs[dst] = sympy.sin(ra)
            elif op == 0x06:  # COS
                regs[dst] = sympy.cos(ra)
            elif op == 0x07:  # EXP
                regs[dst] = sympy.exp(ra)
            elif op == 0x08:  # LOG
                regs[dst] = sympy.log(sympy.Abs(ra))
            elif op == 0x09:  # POW
                regs[dst] = sympy.Pow(ra, rb)
            elif op == 0x0A:  # ABS
                regs[dst] = sympy.Abs(ra)
            elif op == 0x0B:  # SQRT
                regs[dst] = sympy.sqrt(sympy.Abs(ra))
            elif op == 0x0C:  # NEG
                regs[dst] = -ra
            elif op == 0x0D:  # MIN
                regs[dst] = sympy.Min(ra, rb)
            elif op == 0x0E:  # MAX
                regs[dst] = sympy.Max(ra, rb)
        except (TypeError, ValueError, AttributeError, ArithmeticError):
            regs[dst] = sympy.nan

    out = regs[7]
    if linear_head != (1.0, 0.0):
        w1, w0 = linear_head
        out = _exact_constant(float(w1)) * out + _exact_constant(float(w0))

    try:
        return sympy.simplify(out)
    except (TypeError, ValueError, AttributeError, ArithmeticError):
        return out


try:
    _POLY_ERRORS: tuple[type, ...] = (
        TypeError,
        ValueError,
        AttributeError,
        ArithmeticError,
        sympy.PolificationFailed,
    )
except AttributeError:
    _POLY_ERRORS = (TypeError, ValueError, AttributeError, ArithmeticError)


def check_exact_identity(
    candidate_expr: Any,
    ground_truth: str | Any,
    var_name: str = "x",
    domain: tuple[float, float] | None = None,
) -> tuple[bool, str]:
    """Prove or reject exact identity with unified symbols and an explicit domain.

    Exactness requires exact integer/rational arithmetic (no Float coefficients,
    no transcendental operators) with an identically zero numerator, plus no
    poles inside the declared domain (or anywhere real when domain is None).
    Low numeric error never promotes to exact: failures return reasons that
    keep the caller on numerical evidence.
    """
    if not _HAS_SYMPY or candidate_expr is None:
        return False, "sympy_unavailable"
    x = _unified_symbol(var_name)
    cand = _unify_symbols(candidate_expr, var_name)
    if isinstance(ground_truth, str):
        if ground_truth == "x2_3x_7":
            target = x**2 + 3 * x + 7
        elif ground_truth == "sin_x2":
            target = sympy.sin(x) + x**2
        elif ground_truth == "x_plus_1":
            target = x + 1
        else:
            try:
                target = sympy.sympify(ground_truth, locals={var_name: x})
            except (TypeError, ValueError, AttributeError, sympy.SympifyError) as e:
                return False, f"cannot_parse_ground_truth: {e}"
    else:
        target = _unify_symbols(ground_truth, var_name)
    try:
        cand = sympy.sympify(cand)
        target = sympy.sympify(target)
    except (TypeError, ValueError, AttributeError, sympy.SympifyError) as e:
        return False, f"cannot_normalize_expressions: {e}"
    for side in (cand, target):
        if side.has(sympy.nan, sympy.zoo, sympy.oo, -sympy.oo):
            return False, "undefined_expression: zero denominator, invalid domain or overflow"
    try:
        if cand.has(sympy.Float) or target.has(sympy.Float):
            return False, "inexact_coefficients: Float present; numerical evidence only"
        non_rational = (sympy.sin, sympy.cos, sympy.exp, sympy.log, sympy.Abs, sympy.Min, sympy.Max)
        if cand.has(*non_rational) or target.has(*non_rational):
            return False, "non_rational_operators: exact identity not decidable here"
        diff = sympy.together(sympy.expand(cand - target))
        num, den = sympy.fraction(diff)
        if not sympy.Poly(num, x).is_zero:
            return False, f"nonzero_numerator: {sympy.simplify(diff)}"
        poles: list[float] = []
        try:
            for root in sympy.Poly(den, x).all_roots():
                if root.is_real:
                    poles.append(float(root.evalf()))
        except _POLY_ERRORS:
            return False, "denominator_not_polynomial: cannot certify pole freedom"
        if domain is None:
            if poles:
                return (
                    False,
                    f"poles_on_real_line: {sorted(poles)}; declare an explicit pole-free domain",
                )
            return True, "exact_identity_unconditional"
        lo, hi = domain
        inside = sorted(p for p in poles if lo <= p <= hi)
        if inside:
            return False, f"pole_in_domain: {inside} inside [{lo}, {hi}]"
        return True, f"exact_identity_on_domain [{lo}, {hi}]"
    except (TypeError, ValueError, AttributeError, ArithmeticError) as e:
        return False, f"exact_check_failed: {e}"


def check_symbolic_equivalence(
    candidate_expr: Any,
    ground_truth: str | Any,
    var_name: str = "x",
    domain: tuple[float, float] | None = None,
) -> tuple[bool, str]:
    """Test exact symbolic identity between candidate expression and ground truth."""
    return check_exact_identity(candidate_expr, ground_truth, var_name=var_name, domain=domain)


def check_ordinary_math(
    program: np.ndarray,
    xs: np.ndarray,
    const_bank: np.ndarray | None = None,
    linear_head: tuple[float, float] = (1.0, 0.0),
) -> tuple[bool, str | None]:
    """Check if candidate executes without singularity or domain violations under ordinary mathematical rules."""
    bank = (
        const_bank.astype(np.float64) if const_bank is not None else CONST_BANK.astype(np.float64)
    )
    for x in xs:
        regs = np.zeros(8, dtype=np.float64)
        regs[0] = float(x)
        for word in program:
            op, dst, a, b_raw = decode_instr(word)
            if op == 0x00:
                continue
            if dst >= 8 or a >= 8:
                return False, f"Invalid register index dst={dst}, a={a}"
            ra = regs[a]
            if op == 0x0F:  # CSEL
                b_idx = int(b_raw) & 0x0F
                c_val = bank[b_idx] if b_idx < len(bank) else 0.0
                regs[dst] = ra + c_val
                continue

            b = int(b_raw)
            rb = regs[b % 8]

            if op == 0x01:  # ADD
                regs[dst] = ra + rb
            elif op == 0x02:  # SUB
                regs[dst] = ra - rb
            elif op == 0x03:  # MUL
                regs[dst] = ra * rb
            elif op == 0x04:  # DIV
                if abs(rb) < 1e-12:
                    return False, f"Singularity: division by near-zero ({rb:.3e}) near x={x:.6g}"
                regs[dst] = ra / rb
            elif op == 0x05:  # SIN
                regs[dst] = np.sin(ra)
            elif op == 0x06:  # COS
                regs[dst] = np.cos(ra)
            elif op == 0x07:  # EXP
                if abs(ra) > 700.0:
                    return False, f"Overflow: exp magnitude exceeds 700 ({ra:.3e}) near x={x:.6g}"
                regs[dst] = np.exp(ra)
            elif op == 0x08:  # LOG
                if ra <= 0.0:
                    return False, f"Domain violation: log of non-positive ({ra:.3e}) near x={x:.6g}"
                regs[dst] = np.log(ra)
            elif op == 0x09:  # POW
                if abs(ra) < 1e-12 and rb < 0.0:
                    return False, f"Singularity: 0**negative near x={x:.6g}"
                try:
                    regs[dst] = float(np.power(ra, rb))
                except (FloatingPointError, OverflowError, ValueError, ZeroDivisionError):
                    return False, f"Domain violation: pow({ra}, {rb}) near x={x:.6g}"
            elif op == 0x0A:  # ABS
                regs[dst] = abs(ra)
            elif op == 0x0B:  # SQRT
                if ra < 0.0:
                    return False, f"Domain violation: sqrt of negative ({ra:.3e}) near x={x:.6g}"
                regs[dst] = np.sqrt(ra)
            elif op == 0x0C:  # NEG
                regs[dst] = -ra
            elif op == 0x0D:  # MIN
                regs[dst] = min(ra, rb)
            elif op == 0x0E:  # MAX
                regs[dst] = max(ra, rb)
            else:
                return False, f"Unknown opcode {op:#x}"

            if not np.isfinite(regs[dst]):
                return False, f"Non-finite output ({regs[dst]}) near x={x:.6g}"
    return True, None


def export_reproducible_candidate(
    program: np.ndarray,
    const_bank: np.ndarray | None = None,
    linear_head: tuple[float, float] = (1.0, 0.0),
    domain: str = "[-10, 10]",
    recorded_predictions: np.ndarray | None = None,
    recorded_mse: float = 0.0,
    verifier_outcome: str = "unverified",
) -> dict[str, Any]:
    """Export complete bytecode, fitted constants, linear head, and recorded predictions."""
    prog_bytes = np.ascontiguousarray(program, dtype=np.uint32).tobytes()
    sha = hashlib.sha256(prog_bytes).hexdigest()[:16]
    bank = (
        const_bank.astype(np.float64) if const_bank is not None else CONST_BANK.astype(np.float64)
    )
    return {
        "sha256": sha,
        "program": [int(w) for w in program],
        "opcode_version": OPCODE_VERSION,
        "constants": [float(c) for c in bank],
        "linear_head": [float(linear_head[0]), float(linear_head[1])],
        "domain": domain,
        "recorded_predictions": (
            [float(p) for p in recorded_predictions] if recorded_predictions is not None else []
        ),
        "recorded_mse": float(recorded_mse),
        "verifier_outcome": verifier_outcome,
    }


def reproduce_candidate(
    export_dict: dict[str, Any],
    xs: np.ndarray,
) -> np.ndarray:
    """Execute exported candidate-plus-constants to reproduce its recorded predictions."""
    prog = np.array(export_dict["program"], dtype=np.uint32)
    bank = np.array(export_dict["constants"], dtype=np.float64)
    lhead = tuple(export_dict["linear_head"])
    preds, _ = execute_batch_f64(prog, xs, const_bank=bank)
    if lhead != (1.0, 0.0):
        preds = np.float64(lhead[0]) * preds + np.float64(lhead[1])
    return preds


def verify_l2(
    program: np.ndarray,
    train_xs: np.ndarray,
    train_ys: np.ndarray,
    test_xs: np.ndarray,
    test_ys: np.ndarray,
    val_xs: np.ndarray | None = None,
    val_ys: np.ndarray | None = None,
    extrap_xs: np.ndarray | None = None,
    extrap_ys: np.ndarray | None = None,
    adversarial_xs: np.ndarray | None = None,
    constants: np.ndarray | list[float] | None = None,
    linear_head: tuple[float, float] = (1.0, 0.0),
    ground_truth_formula: str | None = None,
    ground_truth_sympy: Any = None,
    error_threshold: float = 1e-4,
    extrap_threshold: float = 1.0,
    divergence_threshold: float = 1e-3,
    domain_str: str = "[-10, 10]",
    domain: tuple[float, float] | None = None,
) -> L2VerificationResult:
    """Level-2 strict verification protocol on frozen candidate programs.

    Numeric checks (MSE, extrapolation, adversarial) only ever yield
    numerical evidence. The exact_certificate label additionally requires a
    unified-symbol exact identity over integers/rationals with no poles in
    the explicit domain. No training positive is born from tolerance alone.
    """
    reasons: list[str] = []

    bank_f64 = (
        np.asarray(constants, dtype=np.float64)
        if constants is not None
        else CONST_BANK.astype(np.float64)
    )
    bank_f32 = bank_f64.astype(np.float32)

    # 1. Ordinary mathematical domain check (comparing protected VM with ordinary math)
    math_test_points = (
        np.concatenate([test_xs[:32], adversarial_xs])
        if adversarial_xs is not None
        else test_xs[:32]
    )
    math_valid, math_err = check_ordinary_math(
        program, math_test_points, const_bank=bank_f64, linear_head=linear_head
    )
    if not math_valid:
        reasons.append("protected_domain_exploit")

    # 2. True Float64 vs Float32 execution on held-out test split
    f64_preds, _f64_flags = execute_batch_f64(program, test_xs, const_bank=bank_f64)
    if linear_head != (1.0, 0.0):
        f64_preds = np.float64(linear_head[0]) * f64_preds + np.float64(linear_head[1])
    f64_test_mse = float(np.mean((f64_preds - np.asarray(test_ys, dtype=np.float64)) ** 2))

    f32_preds, _ = execute_batch(program, test_xs.astype(np.float32), const_bank=bank_f32)
    if linear_head != (1.0, 0.0):
        f32_preds = np.float32(linear_head[0]) * f32_preds + np.float32(linear_head[1])
    f32_test_mse = float(np.mean((f32_preds - np.asarray(test_ys, dtype=np.float32)) ** 2))

    f64_f32_div = abs(f64_test_mse - f32_test_mse)

    # Precision sensitivity check
    if (f64_test_mse > error_threshold and f32_test_mse <= error_threshold) or (
        f64_f32_div > divergence_threshold and f64_test_mse > error_threshold
    ):
        reasons.append("float_precision_divergence")

    if f64_test_mse > error_threshold and "float_precision_divergence" not in reasons:
        reasons.append("test_error_exceeds_threshold")

    # 3. Train error and validation error
    train_preds, _ = execute_batch_f64(program, train_xs, const_bank=bank_f64)
    if linear_head != (1.0, 0.0):
        train_preds = np.float64(linear_head[0]) * train_preds + np.float64(linear_head[1])
    train_mse = float(np.mean((train_preds - np.asarray(train_ys, dtype=np.float64)) ** 2))

    val_mse: float | None = None
    if val_xs is not None and val_ys is not None:
        val_preds, _ = execute_batch_f64(program, val_xs, const_bank=bank_f64)
        if linear_head != (1.0, 0.0):
            val_preds = np.float64(linear_head[0]) * val_preds + np.float64(linear_head[1])
        val_mse = float(np.mean((val_preds - np.asarray(val_ys, dtype=np.float64)) ** 2))

    # 4. Extrapolation test on both domain sides
    extrap_mse: float | None = None
    if extrap_xs is not None and extrap_ys is not None:
        extrap_preds, _ = execute_batch_f64(program, extrap_xs, const_bank=bank_f64)
        if linear_head != (1.0, 0.0):
            extrap_preds = np.float64(linear_head[0]) * extrap_preds + np.float64(linear_head[1])
        extrap_mse = float(np.mean((extrap_preds - np.asarray(extrap_ys, dtype=np.float64)) ** 2))
        if extrap_mse > extrap_threshold:
            reasons.append("extrapolation_divergence")

    # Overfitting / Memorization signature
    eval_val = val_mse if val_mse is not None else f64_test_mse
    val_gap = max(0.0, eval_val - train_mse)
    from evobyte.archive import is_memorizer

    if (
        is_memorizer(train_mse, eval_val, val_gap, extrap_mse)
        and "extrapolation_divergence" not in reasons
    ):
        reasons.append("overfit_memorization")

    # 5. Adversarial points check
    adv_invalid_rate = 0.0
    if adversarial_xs is not None:
        _, adv_flags = execute_batch_f64(program, adversarial_xs, const_bank=bank_f64)
        adv_invalid_rate = float(np.mean(adv_flags)) if len(adv_flags) else 0.0
        if adv_invalid_rate > 0.0:
            reasons.append("adversarial_invalid_flag")

    # 6. Exact identity check (unified symbols, explicit domain)
    sym_expr = program_to_sympy(program, const_bank=bank_f64, linear_head=linear_head)
    sym_str = str(sym_expr) if sym_expr is not None else decode_human(program)
    sym_equiv = False
    proof_type = "numerical_evidence"
    sym_notes = ""

    gt_target = ground_truth_sympy if ground_truth_sympy is not None else ground_truth_formula
    if gt_target is not None and _HAS_SYMPY and sym_expr is not None:
        eq, detail = check_symbolic_equivalence(sym_expr, gt_target, domain=domain)
        if eq:
            sym_equiv = True
            sym_notes = f"Proved exact identity ({detail})"
        else:
            sym_equiv = False
            sym_notes = f"No exact identity: {detail}"
    else:
        sym_notes = "Numerical evidence only (symbolic ground truth not verified)"

    passed = len(reasons) == 0
    # An exact label additionally requires full acceptance: an invalid program
    # (e.g. rejected by ordinary mathematics) never carries a certificate.
    if sym_equiv and passed:
        proof_type = "exact_certificate"
    else:
        sym_equiv = sym_equiv and passed
        proof_type = "numerical_evidence"

    decision = "VERIFIED_DISCOVERY" if passed else f"REJECTED: {', '.join(reasons)}"

    exported = export_reproducible_candidate(
        program=program,
        const_bank=bank_f64,
        linear_head=linear_head,
        domain=domain_str,
        recorded_predictions=f64_preds,
        recorded_mse=f64_test_mse,
        verifier_outcome=decision,
    )

    return L2VerificationResult(
        passed=passed,
        decision=decision,
        reasons=reasons,
        f64_test_mse=f64_test_mse,
        f32_test_mse=f32_test_mse,
        f64_f32_divergence=f64_f32_div,
        train_mse=train_mse,
        val_mse=val_mse,
        extrap_mse=extrap_mse,
        adversarial_invalid_rate=adv_invalid_rate,
        ordinary_math_valid=math_valid,
        ordinary_math_error=math_err,
        symbolic_equivalent=sym_equiv,
        symbolic_expression=sym_str,
        symbolic_notes=sym_notes,
        proof_type=proof_type,
        tolerance=error_threshold,
        domain=domain_str,
        exported_candidate=exported,
    )
