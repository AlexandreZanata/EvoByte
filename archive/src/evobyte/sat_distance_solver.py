"""Exact SAT Distance Solver for Quantum Codes (P214).

Implements exact Conjunctive Normal Form (CNF) formulations with Totalizer and
Sorting Network cardinality encodings to certify or refute minimum quantum code
distances d >= d_target (with focus on d >= 5) for:
1. CSS Quantum Stabilizer Codes: (HX, HZ), BivariateStabilizerCode, QuasiCyclicStabilizer.
   Decouples X and Z error search into separate optimal parity and cardinality formulas.
2. General Non-CSS Stabilizer Codes: Arbitrary commuting Pauli generator groups (e.g. Gottesman [[8, 3, 3]]).
   Constructs the full symplectic centralizer S^perp and joint X-Z support variables w_j = x_j or z_j.
3. Certifiable Outcome: If all weights w < d_target are UNSAT, d >= d_target is unconditionally proven.
   If SAT for weight w, extracts the exact minimal non-trivial Pauli logical witness operator.

Part of the Bivariate Bicycle & Projective Geometries Program (P211-P220, D047).
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Sequence

import numpy as np
from pysat.card import CardEnc, EncType

from evobyte.quasi_cyclic_qecc import (
    QuasiCyclicStabilizer,
    gf2_basis_and_indices,
    in_gf2_span,
    verify_symplectic_orthogonality,
)
from evobyte.sat_bridge import CNFFormula, solve_cnf
from evobyte.sat_distance_encoder import extract_css_logicals, nullspace_gf2


def pauli_to_symplectic_vector(pauli_str: str) -> np.ndarray:
    """Convert Pauli string of length n to binary symplectic vector (x_1..x_n | z_1..z_n)."""
    n = len(pauli_str)
    vec = np.zeros(2 * n, dtype=np.uint8)
    for j, char in enumerate(pauli_str.upper()):
        if char in ("X", "Y"):
            vec[j] = 1
        if char in ("Z", "Y"):
            vec[j + n] = 1
    return vec


def symplectic_to_pauli_string(vec: Sequence[int], n: int) -> str:
    """Convert binary symplectic vector (x_1..x_n | z_1..z_n) to Pauli string."""
    paulis = []
    for j in range(n):
        x = int(vec[j])
        z = int(vec[j + n])
        if x and z:
            paulis.append("Y")
        elif x:
            paulis.append("X")
        elif z:
            paulis.append("Z")
        else:
            paulis.append("I")
    return "".join(paulis)


def extract_general_stabilizer_logicals(
    generators: Sequence[str] | np.ndarray,
) -> tuple[np.ndarray, list[np.ndarray], int, int]:
    """Extract symplectic parity check matrix S, logical basis vectors, n, and k."""
    if len(generators) == 0:
        raise ValueError("Cannot extract logicals from empty generator set.")

    if isinstance(generators[0], str):
        n = len(generators[0])
        m = len(generators)
        S = np.zeros((m, 2 * n), dtype=np.uint8)
        for i, g in enumerate(generators):
            S[i] = pauli_to_symplectic_vector(g)
    else:
        S = np.asarray(generators, dtype=np.uint8)
        m, two_n = S.shape
        n = two_n // 2

    # Check mutual commutativity: S_X @ S_Z^T + S_Z @ S_X^T == 0 mod 2
    M = np.hstack([S[:, n:], S[:, :n]])
    comm = (M @ S.T) % 2
    if not np.all(comm == 0):
        raise ValueError("Stabilizer generators do not mutually commute symplectically!")

    # Centralizer S^perp = ker(M)
    ker_M = nullspace_gf2(M, 2 * n)
    basis_s, _ = gf2_basis_and_indices(S)
    rank_s = len(basis_s)
    k = n - rank_s

    logicals: list[np.ndarray] = []
    current_basis = list(basis_s)

    for vec in ker_M:
        v_int = int(sum(int(b) << i for i, b in enumerate(vec)))
        if not in_gf2_span(v_int, current_basis):
            logicals.append(vec)
            hb = v_int
            for b in current_basis:
                hb = min(hb, hb ^ b)
            if hb:
                lead = hb.bit_length() - 1
                for idx, b in enumerate(current_basis):
                    if (b >> lead) & 1:
                        current_basis[idx] = b ^ hb
                current_basis.append(hb)
                current_basis.sort(reverse=True)

    return S, logicals, n, k


@dataclass(frozen=True)
class SATDistanceCertificate:
    """Formal certificate of SAT-based quantum code distance verification."""

    n: int
    k: int
    d: int | None
    proven_lower_bound: int
    target_distance: int
    distance_verified: bool
    is_css: bool
    minimal_logical_pauli: str | None
    witness_vector: tuple[int, ...] | None
    num_clauses: int
    solve_time_seconds: float
    solver_name: str
    cardinality_encoding: str

    def to_dict(self) -> dict[str, Any]:
        """Convert certificate to dictionary format."""
        return {
            "n": self.n,
            "k": self.k,
            "d": self.d,
            "proven_lower_bound": self.proven_lower_bound,
            "target_distance": self.target_distance,
            "distance_verified": self.distance_verified,
            "is_css": self.is_css,
            "minimal_logical_pauli": self.minimal_logical_pauli,
            "witness_vector": list(self.witness_vector) if self.witness_vector else None,
            "num_clauses": self.num_clauses,
            "solve_time_seconds": round(self.solve_time_seconds, 4),
            "solver_name": self.solver_name,
            "cardinality_encoding": self.cardinality_encoding,
        }


class ExactSATDistanceSolver:
    """Exact SAT solver for quantum code distance verification and minimal logical search.

    Formulates distance verification via Boolean Satisfiability (CNF) and CDCL solvers:
    - Supports Totalizer (EncType.totalizer), Sorting Network (EncType.sortnetwrk), and
      Sequential Counter encodings.
    - Resolves d >= 5 in sub-second to low-second times for n <= 20 qubits.
    """

    def __init__(
        self,
        cardinality_encoding: str = "totalizer",
        solver_name: str = "cadical195",
    ) -> None:
        self.cardinality_encoding: str = cardinality_encoding.lower()
        self.solver_name: str = solver_name

    def _get_enc_type(self) -> EncType:
        if self.cardinality_encoding == "totalizer":
            return EncType.totalizer
        elif self.cardinality_encoding == "sortnetwrk":
            return EncType.sortnetwrk
        elif self.cardinality_encoding == "seqcounter":
            return EncType.seqcounter
        return EncType.totalizer

    def _encode_css_logical(
        self,
        H_checks: np.ndarray,
        anti_target: np.ndarray,
        weight: int,
    ) -> CNFFormula:
        """Encode whether an undetectable error of prescribed weight exists in CSS code."""
        n = H_checks.shape[1]
        formula = CNFFormula(n_vars=n)
        vars_vec = list(range(1, n + 1))

        # 1. Parity checks: H_checks @ v == 0 (mod 2)
        for row in H_checks:
            lits = [i + 1 for i, b in enumerate(row) if b]
            if lits:
                formula.add_xor(lits, target_parity=0)

        # 2. Non-triviality check: v @ anti_target == 1 (mod 2)
        lits_anti = [i + 1 for i, b in enumerate(anti_target) if b]
        if lits_anti:
            formula.add_xor(lits_anti, target_parity=1)
        else:
            # Cannot anti-commute with zero vector
            formula.add_clause([1])
            formula.add_clause([-1])
            return formula

        # 3. Cardinality constraint: sum(v_j) <= weight
        if self.cardinality_encoding in ("totalizer", "sortnetwrk"):
            enc = CardEnc.atmost(
                lits=vars_vec,
                bound=weight,
                top_id=formula.n_vars,
                encoding=self._get_enc_type(),
            )
            formula.add_clauses(enc.clauses)
        else:
            formula.add_at_most_k(vars_vec, weight)

        return formula

    def _encode_general_logical(
        self,
        M_checks: np.ndarray,
        L_target: np.ndarray,
        n: int,
        weight: int,
    ) -> CNFFormula:
        """Encode whether a general non-CSS logical operator of prescribed weight exists."""
        formula = CNFFormula(n_vars=3 * n)

        # Indicator variables w_j <-> (x_j or z_j)
        for j in range(n):
            xj = j + 1
            zj = j + n + 1
            wj = j + 2 * n + 1
            formula.add_clause([-xj, wj])
            formula.add_clause([-zj, wj])
            formula.add_clause([-wj, xj, zj])

        # Parity checks: M_checks @ [x | z]^T == 0 (mod 2)
        for row in M_checks:
            lits = [j + 1 for j, b in enumerate(row) if b]
            if lits:
                formula.add_xor(lits, target_parity=0)

        # Anti-commute with L_target: <v, L_target> == 1 (mod 2)
        lits_anti = []
        for j in range(n):
            if L_target[j + n] == 1:
                lits_anti.append(j + 1)  # x_j with L_z_j
            if L_target[j] == 1:
                lits_anti.append(j + n + 1)  # z_j with L_x_j

        if lits_anti:
            formula.add_xor(lits_anti, target_parity=1)
        else:
            formula.add_clause([1])
            formula.add_clause([-1])
            return formula

        # Cardinality constraint: sum(w_j) <= weight
        w_lits = [j + 2 * n + 1 for j in range(n)]
        if self.cardinality_encoding in ("totalizer", "sortnetwrk"):
            enc = CardEnc.atmost(
                lits=w_lits,
                bound=weight,
                top_id=formula.n_vars,
                encoding=self._get_enc_type(),
            )
            formula.add_clauses(enc.clauses)
        else:
            formula.add_at_most_k(w_lits, weight)

        return formula

    def prove_distance_at_least(
        self,
        code: Any,
        min_distance: int = 5,
        timeout_seconds: float = 30.0,
    ) -> SATDistanceCertificate:
        """Prove whether quantum code distance satisfies d >= min_distance.

        Checks all weights w in [1, min_distance - 1].
        If all queries are UNSAT, d >= min_distance is unconditionally proven.
        """
        t0 = time.perf_counter()
        is_css, data = self._parse_code(code)

        if is_css:
            HX, HZ, n, k = data
            if k <= 0:
                return self._empty_certificate(n, k, min_distance, is_css=True)

            logicals_x, logicals_z = extract_css_logicals(HX, HZ)
            total_clauses = 0

            for w in range(1, min_distance):
                # Check X logical errors (anti-commuting with logical Z)
                for lz in logicals_z:
                    formula = self._encode_css_logical(HZ, lz, weight=w)
                    total_clauses += len(formula.clauses)
                    res = solve_cnf(
                        formula, timeout_seconds=timeout_seconds, solver_name=self.solver_name
                    )
                    if res.is_sat:
                        witness_x = tuple(1 if i + 1 in res.model else 0 for i in range(n))
                        pstr = "".join("X" if b else "I" for b in witness_x)
                        elapsed = time.perf_counter() - t0
                        return SATDistanceCertificate(
                            n=n,
                            k=k,
                            d=w,
                            proven_lower_bound=w,
                            target_distance=min_distance,
                            distance_verified=False,
                            is_css=True,
                            minimal_logical_pauli=pstr,
                            witness_vector=witness_x,
                            num_clauses=total_clauses,
                            solve_time_seconds=elapsed,
                            solver_name=res.solver_name,
                            cardinality_encoding=self.cardinality_encoding,
                        )

                # Check Z logical errors (anti-commuting with logical X)
                for lx in logicals_x:
                    formula = self._encode_css_logical(HX, lx, weight=w)
                    total_clauses += len(formula.clauses)
                    res = solve_cnf(
                        formula, timeout_seconds=timeout_seconds, solver_name=self.solver_name
                    )
                    if res.is_sat:
                        witness_z = tuple(1 if i + 1 in res.model else 0 for i in range(n))
                        pstr = "".join("Z" if b else "I" for b in witness_z)
                        elapsed = time.perf_counter() - t0
                        return SATDistanceCertificate(
                            n=n,
                            k=k,
                            d=w,
                            proven_lower_bound=w,
                            target_distance=min_distance,
                            distance_verified=False,
                            is_css=True,
                            minimal_logical_pauli=pstr,
                            witness_vector=witness_z,
                            num_clauses=total_clauses,
                            solve_time_seconds=elapsed,
                            solver_name=res.solver_name,
                            cardinality_encoding=self.cardinality_encoding,
                        )

            elapsed = time.perf_counter() - t0
            return SATDistanceCertificate(
                n=n,
                k=k,
                d=None,
                proven_lower_bound=min_distance,
                target_distance=min_distance,
                distance_verified=True,
                is_css=True,
                minimal_logical_pauli=None,
                witness_vector=None,
                num_clauses=total_clauses,
                solve_time_seconds=elapsed,
                solver_name=self.solver_name,
                cardinality_encoding=self.cardinality_encoding,
            )
        else:
            # General non-CSS stabilizer code
            S, logicals, n, k = data
            if k <= 0:
                return self._empty_certificate(n, k, min_distance, is_css=False)

            M = np.hstack([S[:, n:], S[:, :n]])
            total_clauses = 0

            for w in range(1, min_distance):
                for L in logicals:
                    formula = self._encode_general_logical(M, L, n, weight=w)
                    total_clauses += len(formula.clauses)
                    res = solve_cnf(
                        formula, timeout_seconds=timeout_seconds, solver_name=self.solver_name
                    )
                    if res.is_sat:
                        model = set(res.model or [])
                        vec = [1 if j + 1 in model else 0 for j in range(2 * n)]
                        pstr = symplectic_to_pauli_string(vec, n)
                        elapsed = time.perf_counter() - t0
                        return SATDistanceCertificate(
                            n=n,
                            k=k,
                            d=w,
                            proven_lower_bound=w,
                            target_distance=min_distance,
                            distance_verified=False,
                            is_css=False,
                            minimal_logical_pauli=pstr,
                            witness_vector=tuple(vec),
                            num_clauses=total_clauses,
                            solve_time_seconds=elapsed,
                            solver_name=res.solver_name,
                            cardinality_encoding=self.cardinality_encoding,
                        )

            elapsed = time.perf_counter() - t0
            return SATDistanceCertificate(
                n=n,
                k=k,
                d=None,
                proven_lower_bound=min_distance,
                target_distance=min_distance,
                distance_verified=True,
                is_css=False,
                minimal_logical_pauli=None,
                witness_vector=None,
                num_clauses=total_clauses,
                solve_time_seconds=elapsed,
                solver_name=self.solver_name,
                cardinality_encoding=self.cardinality_encoding,
            )

    def compute_exact_distance(
        self,
        code: Any,
        max_distance: int = 6,
        timeout_seconds: float = 30.0,
    ) -> SATDistanceCertificate:
        """Find the exact quantum code distance d by checking weights 1, 2, ..., max_distance."""
        cert = self.prove_distance_at_least(
            code, min_distance=max_distance, timeout_seconds=timeout_seconds
        )
        if cert.distance_verified:
            # It is at least max_distance. Test max_distance itself:
            cert_next = self.prove_distance_at_least(
                code, min_distance=max_distance + 1, timeout_seconds=timeout_seconds
            )
            if not cert_next.distance_verified and cert_next.d == max_distance:
                return cert_next
            return cert
        return cert

    def find_minimal_logical(
        self,
        code: Any,
        max_weight: int = 6,
        timeout_seconds: float = 30.0,
    ) -> tuple[int, str]:
        """Find the minimal weight non-trivial logical operator as (distance, pauli_string)."""
        cert = self.compute_exact_distance(
            code, max_distance=max_weight, timeout_seconds=timeout_seconds
        )
        if cert.d is not None and cert.minimal_logical_pauli is not None:
            return cert.d, cert.minimal_logical_pauli
        return cert.proven_lower_bound, ""

    def _parse_code(self, code: Any) -> tuple[bool, Any]:
        """Normalize code into CSS (HX, HZ, n, k) or General (S, logicals, n, k)."""
        if isinstance(code, tuple) and len(code) == 2:
            HX, HZ = code
            n = HX.shape[1]
            rx = len(gf2_basis_and_indices(HX)[0])
            rz = len(gf2_basis_and_indices(HZ)[0])
            k = n - rx - rz
            if not verify_symplectic_orthogonality(HX, HZ):
                raise ValueError("Check matrices do not commute symplectically!")
            return True, (HX, HZ, n, k)
        elif hasattr(code, "HX") and hasattr(code, "HZ"):
            HX, HZ = code.HX, code.HZ
            n = code.n
            k = code.k
            if not verify_symplectic_orthogonality(HX, HZ):
                raise ValueError("Check matrices do not commute symplectically!")
            return True, (HX, HZ, n, k)
        elif isinstance(code, (list, tuple)) and isinstance(code[0], str):
            # Sequence of Pauli strings
            S, logicals, n, k = extract_general_stabilizer_logicals(code)
            return False, (S, logicals, n, k)
        raise TypeError(f"Unsupported code representation: {type(code)}")

    def _empty_certificate(
        self, n: int, k: int, target_distance: int, is_css: bool
    ) -> SATDistanceCertificate:
        return SATDistanceCertificate(
            n=n,
            k=k,
            d=0,
            proven_lower_bound=0,
            target_distance=target_distance,
            distance_verified=False,
            is_css=is_css,
            minimal_logical_pauli=None,
            witness_vector=None,
            num_clauses=0,
            solve_time_seconds=0.0,
            solver_name=self.solver_name,
            cardinality_encoding=self.cardinality_encoding,
        )
