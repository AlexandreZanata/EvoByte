"""Pre-registered Hamiltonian anomaly search protocol (P183).

Executes strict dual-track search (conserved operators + variational ground states)
over frustrated quantum spin chains (J1-J2 at Majumdar-Ghosh point and frustrated spiral regime).
Enforces zero manual solution seeds and requires independent exact verification
for any claimed invariant before promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from evobyte.quantum.evolution_q import evolve_conserved_operator
from evobyte.quantum.ground import evolve_ground_state
from evobyte.quantum.hamiltonians import PauliTerm, decode_term, ising, j1j2, total_sz
from evobyte.quantum.oracle import exact


def independent_pauli_matrix(x_mask: int, z_mask: int, phase: int, n_qubits: int) -> np.ndarray:
    """Build independent dense 2^N matrix via Kronecker products without repo oracle."""
    i2 = np.eye(2, dtype=np.complex128)
    x2 = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    xz = np.array([[0, -1], [1, 0]], dtype=np.complex128)
    z2 = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    phases = (1.0 + 0.0j, 0.0 + 1.0j, -1.0 + 0.0j, 0.0 - 1.0j)

    mat = np.array([[1.0]], dtype=np.complex128)
    for q in reversed(range(n_qubits)):
        bx = (x_mask >> q) & 1
        bz = (z_mask >> q) & 1
        if bx == 0 and bz == 0:
            s = i2
        elif bx == 1 and bz == 0:
            s = x2
        elif bx == 0 and bz == 1:
            s = z2
        else:
            s = xz
        mat = np.kron(mat, s)
    return mat * phases[phase % 4]


def independent_operator_matrix(terms: list[PauliTerm], n_qubits: int) -> np.ndarray:
    """Assemble dense operator matrix independently from term list."""
    dim = 1 << n_qubits
    mat = np.zeros((dim, dim), dtype=np.complex128)
    for t in terms:
        mat += t.coeff * independent_pauli_matrix(t.x_mask, t.z_mask, t.phase, n_qubits)
    return mat


def independent_commutator_norm(
    h_terms: list[PauliTerm], o_terms: list[PauliTerm], n_qubits: int
) -> float:
    """Compute Frobenius norm ||H*O - O*H||_F independently."""
    h_mat = independent_operator_matrix(h_terms, n_qubits)
    o_mat = independent_operator_matrix(o_terms, n_qubits)
    comm = h_mat @ o_mat - o_mat @ h_mat
    return float(np.linalg.norm(comm, ord="fro"))


def verify_non_trivial_invariant(
    h_terms: list[PauliTerm], o_terms: list[PauliTerm], n_qubits: int
) -> dict[str, Any]:
    """Strictly verify whether candidate is a non-trivial, non-cancelling conserved operator."""
    dim = 1 << n_qubits
    o_mat = independent_operator_matrix(o_terms, n_qubits)
    fro_norm = float(np.linalg.norm(o_mat, ord="fro"))

    if fro_norm < 1e-6:
        return {
            "verified": False,
            "reason": "TRIVIAL_ZERO_OPERATOR",
            "frobenius_norm": fro_norm,
            "distance_from_identity": 0.0,
            "commutator_error": 0.0,
        }

    # Check non-identity (distance from scalar identity)
    trace_val = np.trace(o_mat)
    ident_comp = (trace_val / dim) * np.eye(dim, dtype=np.complex128)
    dist_ident = float(np.linalg.norm(o_mat - ident_comp, ord="fro"))

    if dist_ident < 1e-6:
        return {
            "verified": False,
            "reason": "TRIVIAL_SCALAR_IDENTITY",
            "frobenius_norm": fro_norm,
            "distance_from_identity": dist_ident,
            "commutator_error": 0.0,
        }

    comm_err = independent_commutator_norm(h_terms, o_terms, n_qubits)
    is_conserved = bool(comm_err < 1e-7)

    # Check against known total Sz invariant
    sz_mat = independent_operator_matrix(total_sz(n_qubits), n_qubits)
    sz_norm = float(np.linalg.norm(sz_mat, ord="fro"))
    overlap_sz = abs(np.trace(o_mat.conj().T @ sz_mat)) / (fro_norm * sz_norm + 1e-12)
    is_known_sz = bool(overlap_sz >= 0.999)

    return {
        "verified": bool(is_conserved and not is_known_sz),
        "is_conserved": is_conserved,
        "is_known_sz": is_known_sz,
        "frobenius_norm": fro_norm,
        "distance_from_identity": dist_ident,
        "commutator_error": comm_err,
        "overlap_with_total_sz": float(overlap_sz),
        "reason": "KNOWN_SZ" if is_known_sz else ("CONSERVED" if is_conserved else "NON_COMMUTING"),
    }


def run_calibrations(manifest: dict[str, Any]) -> dict[str, Any]:
    """Phase 1: Calibrate pipeline against known exactly soluble instances."""
    results: list[dict[str, Any]] = []
    all_passed = True

    for cal in manifest.get("calibration_targets", []):
        cal_id = cal["id"]
        model = cal["model"]
        n = cal["n_qubits"]

        if model == "ising":
            h_terms = ising(n, j=cal["params"]["j"], h=cal["params"]["h"])
            # Discover 1-term parity operator
            res = evolve_conserved_operator(h_terms, n, pop_size=40, generations=25, n_terms=1, seed=42)
            passed = res["success"] and res["commutator_error"] < 1e-7
            if passed:
                indep_comm = independent_commutator_norm(h_terms, res["best_candidate"], n)
                passed = indep_comm < 1e-7
            results.append({
                "target_id": cal_id,
                "model": model,
                "n_qubits": n,
                "passed": passed,
                "evaluations": res["evaluations"],
                "elapsed_s": res["elapsed_s"],
                "best_candidate": [decode_term(t, n) for t in res["best_candidate"]],
                "commutator_error": res["commutator_error"],
            })
            if not passed:
                all_passed = False

        elif model == "j1j2":
            h_terms = j1j2(n, j1=cal["params"]["j1"], j2=cal["params"]["j2"])
            ex = exact(h_terms, n)
            res = evolve_ground_state(h_terms, n, pop_size=30, generations=25, n_terms=4, seed=42, oracle_truth=ex)
            e_err = abs(res["energy_candidate"] - cal["known_e0"])
            passed = e_err < 1e-3 and (res["fidelity"] or 0.0) >= 0.99
            results.append({
                "target_id": cal_id,
                "model": model,
                "n_qubits": n,
                "passed": passed,
                "evaluations": res["evaluations"],
                "elapsed_s": res["elapsed_s"],
                "energy_discovered": res["energy_candidate"],
                "energy_exact": cal["known_e0"],
                "energy_error": e_err,
                "fidelity": res["fidelity"],
            })
            if not passed:
                all_passed = False

    return {
        "status": "ALL_CALIBRATIONS_PASSED" if all_passed else "CALIBRATION_FAILED",
        "results": results,
    }


def build_lattice_hamiltonian(lattice_cfg: dict[str, Any], n_qubits: int) -> list[PauliTerm]:
    """Instantiate Hamiltonian term list for target frustrated lattice."""
    params = lattice_cfg.get("params", {})
    if lattice_cfg["model"] == "j1j2":
        return j1j2(n_qubits, j1=float(params.get("j1", 1.0)), j2=float(params.get("j2", 0.5)))
    raise ValueError(f"Unsupported lattice model: {lattice_cfg['model']}")


def execute_campaign(
    manifest_path: str | Path,
    output_path: str | Path,
    checkpoint_path: str | Path,
) -> dict[str, Any]:
    """Execute pre-registered Hamiltonian anomaly search campaign."""
    manifest_path = Path(manifest_path)
    output_path = Path(output_path)
    checkpoint_path = Path(checkpoint_path)

    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = json.loads(manifest_bytes.decode("utf-8"))

    # Phase 1: Calibration
    calib_out = run_calibrations(manifest)
    if calib_out["status"] != "ALL_CALIBRATIONS_PASSED":
        raise RuntimeError(f"Calibration failed: {calib_out}")

    # Load existing checkpoint if valid
    trials: list[dict[str, Any]] = []
    completed_keys: set[str] = set()

    if checkpoint_path.exists():
        try:
            ckpt_data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            if ckpt_data.get("manifest_hash") == manifest_hash:
                trials = ckpt_data.get("trials", [])
                completed_keys = {
                    f"{t['lattice_id']}_N{t['n_qubits']}_seed{t['seed']}" for t in trials
                }
        except Exception:
            trials = []
            completed_keys = set()

    lattices = manifest.get("lattices", [])
    sizes = manifest.get("sizes", [])
    seeds = manifest.get("seeds", [42, 101, 202])

    t_start = time.perf_counter()
    has_confirmed_anomaly = False

    for lat in lattices:
        lat_id = lat["id"]
        for sz in sizes:
            n = sz["n_qubits"]
            size_label = sz["label"]

            for seed in seeds:
                trial_key = f"{lat_id}_N{n}_seed{seed}"
                if trial_key in completed_keys:
                    continue

                h_terms = build_lattice_hamiltonian(lat, n)
                ex = exact(h_terms, n)
                e_exact = float(ex["E_exact"])

                # 1. Conserved Operator Search (2 terms)
                res_cons = evolve_conserved_operator(
                    h_terms,
                    n,
                    pop_size=30,
                    generations=20,
                    n_terms=2,
                    seed=seed,
                )

                # Strict independent check
                verif_out = verify_non_trivial_invariant(
                    h_terms, res_cons["best_candidate"], n
                )

                # 2. Variational Ground State Search (without manual dimer seeds)
                res_ground = evolve_ground_state(
                    h_terms,
                    n,
                    pop_size=30,
                    generations=20,
                    n_terms=min(6, 1 << (n - 1)),
                    seed=seed,
                    oracle_truth=ex,
                )

                e_cand = float(res_ground["energy_candidate"])
                e_err = abs(e_cand - e_exact)
                fid = float(res_ground["fidelity"] or 0.0)

                # Anomaly check: energy strictly below exact bound or uncataloged conserved operator
                is_anomaly = verif_out["verified"] or (e_cand < e_exact - 1e-3)
                if is_anomaly:
                    has_confirmed_anomaly = True

                trial_record = {
                    "lattice_id": lat_id,
                    "size_label": size_label,
                    "n_qubits": n,
                    "seed": seed,
                    "conserved_search": {
                        "evaluations": res_cons["evaluations"],
                        "elapsed_s": res_cons["elapsed_s"],
                        "candidate": [decode_term(t, n) for t in res_cons["best_candidate"]],
                        "commutator_error": res_cons["commutator_error"],
                        "verification": verif_out,
                    },
                    "ground_search": {
                        "evaluations": res_ground["evaluations"],
                        "elapsed_s": res_ground["elapsed_s"],
                        "energy_discovered": e_cand,
                        "energy_exact": e_exact,
                        "energy_error": e_err,
                        "fidelity": fid,
                        "success": res_ground["success"],
                    },
                    "anomaly_detected": is_anomaly,
                }

                trials.append(trial_record)
                completed_keys.add(trial_key)

                # Write incremental checkpoint
                ckpt_payload = {
                    "phase": "P183",
                    "manifest_hash": manifest_hash,
                    "trials_completed": len(trials),
                    "trials": trials,
                    "updated_at": time.time(),
                }
                checkpoint_path.write_text(json.dumps(ckpt_payload, indent=2), encoding="utf-8")

    total_wall_clock = time.perf_counter() - t_start
    total_evaluations = sum(
        t["conserved_search"]["evaluations"] + t["ground_search"]["evaluations"]
        for t in trials
    )

    campaign_status = "ANOMALY_CONFIRMED" if has_confirmed_anomaly else "NULL_RESULT"

    final_payload = {
        "phase": "P183",
        "manifest_hash": manifest_hash,
        "calibration_status": calib_out["status"],
        "calibration_details": calib_out["results"],
        "campaign_status": campaign_status,
        "total_trials": len(trials),
        "total_evaluations": total_evaluations,
        "wall_clock_sec": total_wall_clock,
        "trials": trials,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")
    return final_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="P183 Hamiltonian Anomaly Search")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--output", required=True, help="Path to output results JSON")
    parser.add_argument("--checkpoint", required=True, help="Path to checkpoint JSON")
    args = parser.parse_args()

    results = execute_campaign(args.manifest, args.output, args.checkpoint)
    print(f"P183 Hamiltonian Anomaly Search: {results['campaign_status']}")
    print(f"Calibration: {results['calibration_status']}")
    print(f"Trials: {results['total_trials']}, Evaluations: {results['total_evaluations']}, Wall Clock: {results['wall_clock_sec']:.2f}s")


if __name__ == "__main__":
    main()
