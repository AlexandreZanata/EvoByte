"""Belief Propagation with Ordered Statistics Decoding (BP-OSD) Engine (P214).

Implements modern quantum error-correcting decoders combining iterative belief
propagation over Tanner factor graphs with algebraic Ordered Statistics Decoding (OSD)
post-processing:
1. BP Phase: Normalized Min-Sum or Sum-Product message passing on check-to-variable
   and variable-to-check Tanner edges.
2. OSD Phase: High-order reliability sorting gamma_j = |L_j|, Most Reliable Basis (MRB)
   identification via GF(2) Gaussian elimination, and exact syndrome inversion.
3. Quantum CSS Integration: Decoupled X-Z decoding against stabilizer check matrices
   (HX, HZ) with exact logical error detection (testing whether residual e + e_hat lies
   in the stabilizer space or represents a logical fault).
4. Physical Error Simulation: Monte Carlo estimation of Block Error Rate (BLER) and
   Bit Error Rate (BER) across depolarizing channels, and fast heuristic distance upper bounding.

Part of the Bivariate Bicycle & Projective Geometries Program (P211-P220, D047).
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Any, Sequence

import numpy as np

from evobyte.quasi_cyclic_qecc import (
    gf2_basis_and_indices,
    in_gf2_span,
)


@dataclass(frozen=True)
class BPOSDResult:
    """Outcome of a BP-OSD decoding operation."""

    converged_bp: bool
    iterations: int
    error_estimate: np.ndarray
    syndrome_valid: bool
    method_used: str
    weight: int
    posterior_llrs: np.ndarray

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            "converged_bp": self.converged_bp,
            "iterations": self.iterations,
            "error_weight": self.weight,
            "syndrome_valid": self.syndrome_valid,
            "method_used": self.method_used,
        }


class BPOSDDecoder:
    """Belief Propagation with Ordered Statistics Decoding (BP-OSD) Decoder.

    Supports Min-Sum and Sum-Product belief propagation with OSD-0 / OSD-W fallback.
    """

    def __init__(
        self,
        H: np.ndarray,
        error_rate: float = 0.05,
        max_iter: int = 30,
        osd_order: int = 0,
        bp_method: str = "min_sum",
        ms_scaling: float = 0.75,
    ) -> None:
        self.H: np.ndarray = np.asarray(H, dtype=np.uint8)
        self.m, self.n = self.H.shape
        self.error_rate: float = float(error_rate)
        self.max_iter: int = int(max_iter)
        self.osd_order: int = int(osd_order)
        self.bp_method: str = bp_method.lower()
        self.ms_scaling: float = float(ms_scaling)

        # Precompute Tanner graph adjacency lists
        self.checks_of_var: list[np.ndarray] = [
            np.where(self.H[:, j] == 1)[0] for j in range(self.n)
        ]
        self.vars_of_check: list[np.ndarray] = [
            np.where(self.H[i, :] == 1)[0] for i in range(self.m)
        ]

        # Prior log-likelihood ratio L_0 = ln((1 - p) / p)
        safe_p = max(1e-6, min(1.0 - 1e-6, self.error_rate))
        self.prior_llr: float = float(np.log((1.0 - safe_p) / safe_p))

    def decode(self, syndrome: Sequence[int] | np.ndarray) -> BPOSDResult:
        """Decode a binary syndrome vector s into an estimated error pattern e_hat."""
        s = np.asarray(syndrome, dtype=np.uint8) % 2
        if np.all(s == 0):
            return BPOSDResult(
                converged_bp=True,
                iterations=0,
                error_estimate=np.zeros(self.n, dtype=np.uint8),
                syndrome_valid=True,
                method_used="zero_syndrome",
                weight=0,
                posterior_llrs=np.full(self.n, self.prior_llr, dtype=float),
            )

        # -------------------------------------------------------------
        # Phase 1: Belief Propagation
        # -------------------------------------------------------------
        # v2c[i, j]: message from variable j to check i
        v2c = np.zeros((self.m, self.n), dtype=float)
        for j in range(self.n):
            for i in self.checks_of_var[j]:
                v2c[i, j] = self.prior_llr

        c2v = np.zeros((self.m, self.n), dtype=float)
        posterior_llr = np.full(self.n, self.prior_llr, dtype=float)
        converged = False
        bp_iters = 0
        bp_candidate: np.ndarray | None = None

        for it in range(self.max_iter):
            bp_iters = it + 1

            # Check-to-Variable update
            for i in range(self.m):
                v_nodes = self.vars_of_check[i]
                if len(v_nodes) == 0:
                    continue

                if self.bp_method == "sum_product":
                    # Tanh rule for sum-product
                    prod = float((-1) ** int(s[i]))
                    for j in v_nodes:
                        val = np.clip(v2c[i, j], -35.0, 35.0)
                        prod *= float(np.tanh(val / 2.0))
                    for j in v_nodes:
                        val = np.clip(v2c[i, j], -35.0, 35.0)
                        th = float(np.tanh(val / 2.0))
                        div = prod / th if abs(th) > 1e-12 else 0.0
                        div = max(-0.9999999, min(0.9999999, div))
                        c2v[i, j] = 2.0 * float(np.arctanh(div))
                else:
                    # Normalized Min-Sum
                    sgn_prod = int((-1) ** int(s[i]))
                    for j in v_nodes:
                        sgn_prod *= 1 if v2c[i, j] >= 0 else -1

                    magnitudes = [abs(v2c[i, j]) for j in v_nodes]
                    for idx_j, j in enumerate(v_nodes):
                        s_ex = sgn_prod * (1 if v2c[i, j] >= 0 else -1)
                        # Min magnitude excluding j
                        sub_mags = [m for k, m in enumerate(magnitudes) if k != idx_j]
                        min_m = min(sub_mags) if sub_mags else 0.0
                        c2v[i, j] = self.ms_scaling * s_ex * min_m

            # Variable-to-Check update & posterior LLR
            posterior_llr = np.full(self.n, self.prior_llr, dtype=float)
            for j in range(self.n):
                for i in self.checks_of_var[j]:
                    posterior_llr[j] += c2v[i, j]

            hard_decision = (posterior_llr < 0).astype(np.uint8)
            check_syn = (self.H @ hard_decision) % 2
            if np.array_equal(check_syn, s):
                # Verify that hard decision weight is low (<= n // 2)
                if int(np.sum(hard_decision)) <= self.n // 2:
                    converged = True
                    return BPOSDResult(
                        converged_bp=True,
                        iterations=bp_iters,
                        error_estimate=hard_decision,
                        syndrome_valid=True,
                        method_used="bp",
                        weight=int(np.sum(hard_decision)),
                        posterior_llrs=posterior_llr,
                    )
                else:
                    bp_candidate = hard_decision.copy()

            # Update messages for next iteration
            for j in range(self.n):
                for i in self.checks_of_var[j]:
                    v2c[i, j] = posterior_llr[j] - c2v[i, j]

        # -------------------------------------------------------------
        # Phase 2: Ordered Statistics Decoding (OSD)
        # -------------------------------------------------------------
        e_hat, method_str = self._osd_solve(s, posterior_llr)
        syn_valid = bool(np.array_equal((self.H @ e_hat) % 2, s))

        # If BP found a candidate with weight > n//2, compare with OSD
        if bp_candidate is not None:
            w_bp = int(np.sum(bp_candidate))
            w_osd = int(np.sum(e_hat)) if syn_valid else w_bp + 1
            if syn_valid and w_osd < w_bp:
                return BPOSDResult(
                    converged_bp=False,
                    iterations=bp_iters,
                    error_estimate=e_hat,
                    syndrome_valid=True,
                    method_used=method_str,
                    weight=w_osd,
                    posterior_llrs=posterior_llr,
                )
            elif not syn_valid:
                return BPOSDResult(
                    converged_bp=True,
                    iterations=bp_iters,
                    error_estimate=bp_candidate,
                    syndrome_valid=True,
                    method_used="bp",
                    weight=w_bp,
                    posterior_llrs=posterior_llr,
                )

        return BPOSDResult(
            converged_bp=converged,
            iterations=bp_iters,
            error_estimate=e_hat,
            syndrome_valid=syn_valid,
            method_used=method_str,
            weight=int(np.sum(e_hat)),
            posterior_llrs=posterior_llr,
        )

    def _osd_solve(self, syndrome: np.ndarray, posterior_llr: np.ndarray) -> tuple[np.ndarray, str]:
        """Perform Ordered Statistics Decoding (OSD-0 / OSD-W) using soft reliabilities."""
        # Order bits by reliability |posterior_llr| in descending order
        perm = np.argsort(-np.abs(posterior_llr))
        H_perm = self.H[:, perm].copy()

        # Gaussian elimination to select most reliable basis (MRB)
        echelon_track = np.hstack([H_perm, np.eye(self.m, dtype=np.uint8)])
        rank = 0
        basis_cols: list[int] = []

        for col in range(self.n):
            piv = None
            for row in range(rank, self.m):
                if echelon_track[row, col] == 1:
                    piv = row
                    break
            if piv is not None:
                if piv != rank:
                    echelon_track[[rank, piv]] = echelon_track[[piv, rank]]
                for row in range(self.m):
                    if row != rank and echelon_track[row, col] == 1:
                        echelon_track[row] ^= echelon_track[rank]
                basis_cols.append(col)
                rank += 1
                if rank == self.m:
                    break

        T = echelon_track[:, self.n :]  # Elimination transform matrix
        s_rref = (T @ syndrome) % 2

        # Check if syndrome lies in span of H
        if np.any(s_rref[rank:] != 0):
            # Inconsistent syndrome
            return np.zeros(self.n, dtype=np.uint8), "osd_failed"

        # Baseline OSD-0 solution (non-basis bits set to 0)
        best_e_perm = np.zeros(self.n, dtype=np.uint8)
        for row_idx, col_idx in enumerate(basis_cols):
            best_e_perm[col_idx] = s_rref[row_idx]

        best_cost = float(np.sum(np.abs(posterior_llr[perm][best_e_perm == 1])))
        best_method = "osd_0"

        # OSD-W: Test candidate error flips on least reliable basis bits if requested
        if self.osd_order > 0 and len(basis_cols) > 0:
            order_w = min(self.osd_order, min(4, len(basis_cols)))
            # The least reliable basis bits are at the end of basis_cols
            lrb_indices = basis_cols[-order_w:]

            for num_flips in range(1, order_w + 1):
                for flip_subset in itertools.combinations(lrb_indices, num_flips):
                    cand_e = np.zeros(self.n, dtype=np.uint8)
                    for col in flip_subset:
                        cand_e[col] = 1

                    # Compute modified syndrome to be absorbed by remaining basis bits
                    s_mod = (syndrome ^ (H_perm @ cand_e)) % 2
                    s_mod_rref = (T @ s_mod) % 2

                    for row_idx, col_idx in enumerate(basis_cols):
                        cand_e[col_idx] = (cand_e[col_idx] + s_mod_rref[row_idx]) % 2

                    # Evaluate log-likelihood cost
                    cost = float(np.sum(np.abs(posterior_llr[perm][cand_e == 1])))
                    if cost < best_cost:
                        best_cost = cost
                        best_e_perm = cand_e.copy()
                        best_method = f"osd_{num_flips}"

        # Invert permutation back to original qubit ordering
        e_hat = np.zeros(self.n, dtype=np.uint8)
        e_hat[perm] = best_e_perm
        return e_hat, best_method

    @staticmethod
    def decode_css(
        decoder_x: BPOSDDecoder,
        decoder_z: BPOSDDecoder,
        syndrome_z: np.ndarray,
        syndrome_x: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        """Decode CSS quantum code by solving X errors with HZ and Z errors with HX."""
        res_x = decoder_x.decode(syndrome_z)
        res_z = decoder_z.decode(syndrome_x)
        all_valid = res_x.syndrome_valid and res_z.syndrome_valid
        return res_x.error_estimate, res_z.error_estimate, all_valid

    def evaluate_channel_bler(
        self,
        num_trials: int = 500,
        error_rate: float | None = None,
        rng: np.random.Generator | None = None,
        is_css: bool = False,
        H_stabilizers: np.ndarray | None = None,
    ) -> dict[str, Any]:
        """Evaluate Block Error Rate (BLER) and Bit Error Rate (BER) across random channel errors.

        For quantum codes: decoding is considered successful if residual error e + e_hat
        belongs to the row span of H_stabilizers (stabilizer degeneracy).
        """
        if rng is None:
            rng = np.random.default_rng(seed=42)

        p = self.error_rate if error_rate is None else float(error_rate)
        basis_stab, _ = (
            gf2_basis_and_indices(H_stabilizers) if H_stabilizers is not None else ([], [])
        )

        block_errors = 0
        bit_errors = 0
        bp_convergences = 0
        total_iterations = 0

        for _ in range(num_trials):
            # Sample independent Bernoulli error vector
            err = (rng.random(self.n) < p).astype(np.uint8)
            syn = (self.H @ err) % 2

            res = self.decode(syn)
            total_iterations += res.iterations
            if res.converged_bp:
                bp_convergences += 1

            residual = (err ^ res.error_estimate) % 2
            bit_errors += int(np.sum(residual))

            if is_css and H_stabilizers is not None:
                # Success if residual is in stabilizer group
                res_int = int(sum(int(b) << i for i, b in enumerate(residual)))
                if not in_gf2_span(res_int, basis_stab):
                    block_errors += 1
            else:
                # Classical success: exact error reconstruction
                if np.any(residual != 0):
                    block_errors += 1

        return {
            "num_trials": num_trials,
            "error_rate": p,
            "bler": float(block_errors / num_trials),
            "ber": float(bit_errors / (num_trials * self.n)),
            "bp_convergence_rate": float(bp_convergences / num_trials),
            "avg_iterations": float(total_iterations / num_trials),
        }

    @staticmethod
    def find_distance_upper_bound(
        HX: np.ndarray,
        HZ: np.ndarray,
        num_samples: int = 50,
        rng: np.random.Generator | None = None,
    ) -> int:
        """Find a fast upper bound on CSS code distance d <= d_upper using BP-OSD.

        Generates random logical vectors in ker(HZ) and ker(HX) and reduces them
        to minimal weight representatives via stabilizer coset decoding.
        """
        if rng is None:
            rng = np.random.default_rng(seed=42)

        _mx, n = HX.shape
        decoder_x = BPOSDDecoder(HZ, error_rate=0.1, max_iter=20, osd_order=1)
        decoder_z = BPOSDDecoder(HX, error_rate=0.1, max_iter=20, osd_order=1)

        basis_x, _ = gf2_basis_and_indices(HX)
        basis_z, _ = gf2_basis_and_indices(HZ)

        min_found_weight = n

        # Sample random weight-w vectors and check if they produce non-trivial logicals
        for _ in range(num_samples):
            w = rng.integers(1, min(6, n))
            indices = rng.choice(n, size=w, replace=False)
            rand_v = np.zeros(n, dtype=np.uint8)
            rand_v[indices] = 1

            # Decode syndrome of rand_v against HZ to find X logical
            s_z = (HZ @ rand_v) % 2
            res_x = decoder_x.decode(s_z)
            cand_x = (rand_v ^ res_x.error_estimate) % 2
            if np.any((HZ @ cand_x) % 2 != 0):
                continue
            cand_x_int = int(sum(int(b) << i for i, b in enumerate(cand_x)))
            if cand_x_int > 0 and not in_gf2_span(cand_x_int, basis_x):
                wt = int(np.sum(cand_x))
                if 0 < wt < min_found_weight:
                    min_found_weight = wt

            # Decode syndrome against HX to find Z logical
            s_x = (HX @ rand_v) % 2
            res_z = decoder_z.decode(s_x)
            cand_z = (rand_v ^ res_z.error_estimate) % 2
            if np.any((HX @ cand_z) % 2 != 0):
                continue
            cand_z_int = int(sum(int(b) << i for i, b in enumerate(cand_z)))
            if cand_z_int > 0 and not in_gf2_span(cand_z_int, basis_z):
                wt = int(np.sum(cand_z))
                if 0 < wt < min_found_weight:
                    min_found_weight = wt

        return min_found_weight
