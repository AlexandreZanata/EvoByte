"""Tests for P184 Standalone Frontier Certificate Verifier.

Strict constraints:
- Zero external dependencies in scripts/verify_frontier_certificate.py (enforced by AST).
- All tests execute in < 0.2s each; total suite < 3s.
- Subprocess verification of exit codes (0 for valid, 1 for corrupted/rejected, 2 for usage error).
- Dual verification consistency across standalone CLI and EvoByte internal verifiers.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from evobyte.frontier_catalogue import (
    verify_cap_set as internal_verify_cap,
    verify_covering_design as internal_verify_covering,
    verify_weak_schur_partition as internal_verify_weak_schur,
)
from evobyte.qecc_verifier import code_distance as internal_code_distance
from scripts.verify_certificate_standalone import verify_schur_pure as internal_verify_schur


SCRIPT_PATH = Path("scripts/verify_frontier_certificate.py")


def _run_cli(cert_path: Path | str) -> subprocess.CompletedProcess[str]:
    """Helper to run standalone verifier CLI via subprocess."""
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(cert_path)],
        capture_output=True,
        text=True,
    )


def test_standalone_accepts_valid_covering(tmp_path: Path) -> None:
    """Valid Fano plane C(7, 3, 2) covering certificate returns exit code 0."""
    cert = {
        "certificate_type": "covering",
        "target_id": "fano_c7_3_2",
        "v": 7,
        "k": 3,
        "t": 2,
        "blocks": [[1, 2, 3], [1, 4, 5], [1, 6, 7], [2, 4, 6], [2, 5, 7], [3, 4, 7], [3, 5, 6]],
    }
    p = tmp_path / "valid_covering.json"
    p.write_text(json.dumps(cert), encoding="utf-8")

    res = _run_cli(p)
    assert res.returncode == 0
    assert "[SUCCESS]" in res.stdout
    assert "covered by 7 blocks" in res.stdout


def test_standalone_rejects_corrupted_covering(tmp_path: Path) -> None:
    """Corrupted covering (missing block or invalid block size) returns exit code 1."""
    # 1. Missing block (only 6 blocks -> uncovered pair {3, 5})
    cert_missing = {
        "certificate_type": "covering",
        "target_id": "fano_missing_block",
        "v": 7,
        "k": 3,
        "t": 2,
        "blocks": [
            [1, 2, 3],
            [1, 4, 5],
            [1, 6, 7],
            [2, 4, 6],
            [2, 5, 7],
            [3, 4, 7],
            # missing [3, 5, 6]
        ],
    }
    p1 = tmp_path / "corrupted_missing.json"
    p1.write_text(json.dumps(cert_missing), encoding="utf-8")
    res1 = _run_cli(p1)
    assert res1.returncode == 1
    assert "[FAILED]" in res1.stderr

    # 2. Invalid block size
    cert_bad_size = {
        "certificate_type": "covering",
        "target_id": "fano_bad_size",
        "v": 7,
        "k": 3,
        "t": 2,
        "blocks": [[1, 2], [1, 4, 5]],
    }
    p2 = tmp_path / "corrupted_size.json"
    p2.write_text(json.dumps(cert_bad_size), encoding="utf-8")
    res2 = _run_cli(p2)
    assert res2.returncode == 1
    assert "size !=" in res2.stderr


def test_standalone_accepts_weak_schur_and_rejects_strong_claim(tmp_path: Path) -> None:
    """Weak Schur partition of 1..8 passes as weak_schur and fails as schur."""
    ws_partition = [1, 1, 2, 1, 2, 2, 2, 1]

    # Valid as weak_schur
    cert_weak = {
        "certificate_type": "weak_schur",
        "target_id": "ws_k2_n8",
        "k": 2,
        "partition": ws_partition,
    }
    p_weak = tmp_path / "cert_weak.json"
    p_weak.write_text(json.dumps(cert_weak), encoding="utf-8")
    res_weak = _run_cli(p_weak)
    assert res_weak.returncode == 0
    assert "[SUCCESS]" in res_weak.stdout
    assert "valid weak sum-free partition" in res_weak.stdout

    # Fails when claimed as strong schur (because 1 + 1 = 2 is monochromatic in class 1)
    cert_strong = {
        "certificate_type": "schur",
        "target_id": "ws_as_strong_fail",
        "k": 2,
        "partition": ws_partition,
    }
    p_strong = tmp_path / "cert_strong.json"
    p_strong.write_text(json.dumps(cert_strong), encoding="utf-8")
    res_strong = _run_cli(p_strong)
    assert res_strong.returncode == 1
    assert "[FAILED]" in res_strong.stderr
    assert "monochromatic Schur violation: 1 + 1 = 2" in res_strong.stderr


def test_standalone_accepts_cap_cube_and_rejects_line(tmp_path: Path) -> None:
    """Affine hypercube in F3^3 passes; collinear triple fails with exit code 1."""
    # 1. Valid hypercube {0, 1}^3
    valid_pts = [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [1, 0, 0],
        [1, 0, 1],
        [1, 1, 0],
        [1, 1, 1],
    ]
    cert_valid = {
        "certificate_type": "cap_set",
        "target_id": "cap_cube_valid",
        "n": 3,
        "points": valid_pts,
    }
    p_valid = tmp_path / "cap_valid.json"
    p_valid.write_text(json.dumps(cert_valid), encoding="utf-8")
    res_valid = _run_cli(p_valid)
    assert res_valid.returncode == 0
    assert "[SUCCESS]" in res_valid.stdout

    # 2. Collinear triple [(0,0,0), (1,1,1), (2,2,2)] (sums to (0,0,0) mod 3)
    cert_line = {
        "certificate_type": "cap_set",
        "target_id": "cap_line_fail",
        "n": 3,
        "points": [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
    }
    p_line = tmp_path / "cap_line.json"
    p_line.write_text(json.dumps(cert_line), encoding="utf-8")
    res_line = _run_cli(p_line)
    assert res_line.returncode == 1
    assert "[FAILED]" in res_line.stderr
    assert "collinear triple" in res_line.stderr


def test_standalone_accepts_steane_and_rejects_broken(tmp_path: Path) -> None:
    """Steane [[7, 1, 3]] code passes; non-commuting generator fails with exit code 1."""
    steane_gens = [
        "IIIXXXX",
        "IXXIIXX",
        "XIXIXIX",
        "IIIZZZZ",
        "IZZIIZZ",
        "ZIZIZIZ",
    ]
    cert_valid = {
        "certificate_type": "qecc_stabilizer",
        "target_id": "steane_valid",
        "n": 7,
        "k_claimed": 1,
        "d_claimed": 3,
        "stabilizers": steane_gens,
    }
    p_valid = tmp_path / "steane_valid.json"
    p_valid.write_text(json.dumps(cert_valid), encoding="utf-8")
    res_valid = _run_cli(p_valid)
    assert res_valid.returncode == 0
    assert "[SUCCESS]" in res_valid.stdout
    assert "[[7,1,3]]" in res_valid.stdout

    # 1. Non-commuting generator: replace first generator with 'IIIXXXZ'
    broken_comm = list(steane_gens)
    broken_comm[0] = "IIIXXXZ"
    cert_comm_fail = {
        "certificate_type": "qecc_stabilizer",
        "target_id": "steane_comm_fail",
        "n": 7,
        "k_claimed": 1,
        "d_claimed": 3,
        "stabilizers": broken_comm,
    }
    p_comm = tmp_path / "steane_comm_fail.json"
    p_comm.write_text(json.dumps(cert_comm_fail), encoding="utf-8")
    res_comm = _run_cli(p_comm)
    assert res_comm.returncode == 1
    assert "[FAILED]" in res_comm.stderr
    assert "do not commute" in res_comm.stderr

    # 2. Overclaimed distance d=4
    cert_d_fail = dict(cert_valid)
    cert_d_fail["d_claimed"] = 4
    p_d = tmp_path / "steane_d_fail.json"
    p_d.write_text(json.dumps(cert_d_fail), encoding="utf-8")
    res_d = _run_cli(p_d)
    assert res_d.returncode == 1
    assert "[FAILED]" in res_d.stderr
    assert "code distance mismatch" in res_d.stderr


def test_standalone_imports_only_stdlib() -> None:
    """AST check: scripts/verify_frontier_certificate.py imports ONLY Python standard library."""
    assert SCRIPT_PATH.exists()
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))

    # Determine standard library module names
    stdlib_names = (
        set(sys.stdlib_module_names)
        if hasattr(sys, "stdlib_module_names")
        else {
            "argparse",
            "hashlib",
            "json",
            "sys",
            "math",
            "itertools",
            "dataclasses",
            "collections",
            "typing",
            "pathlib",
            "os",
            "re",
            "time",
            "functools",
        }
    )

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    assert imported_modules.issubset(stdlib_names), (
        f"Disallowed non-stdlib imports in standalone verifier: {imported_modules - stdlib_names}"
    )
    assert "numpy" not in imported_modules
    assert "evobyte" not in imported_modules


def test_sample_certificates_verify_both_implementations() -> None:
    """Each sample certificate in dist/external-validation/ passes standalone CLI and internal verifiers."""
    sample_dir = Path("dist/external-validation")
    sample_files = sorted(sample_dir.glob("frontier_sample_*.json"))
    assert len(sample_files) == 5, f"Expected 5 sample certificates, found {len(sample_files)}"

    for f in sample_files:
        # 1. Standalone CLI verifier
        res_cli = _run_cli(f)
        assert res_cli.returncode == 0, f"Standalone CLI failed on {f.name}: {res_cli.stderr}"
        assert "[SUCCESS]" in res_cli.stdout

        # 2. Internal EvoByte verifier
        data = json.loads(f.read_text(encoding="utf-8"))
        cert_type = data["certificate_type"]

        if cert_type == "covering":
            ok, msg = internal_verify_covering(data["blocks"], data["v"], data["k"], data["t"])
        elif cert_type == "schur":
            ok, msg = internal_verify_schur(data["partition"], data["k"])
        elif cert_type == "weak_schur":
            ok, msg = internal_verify_weak_schur(data["partition"], data["k"])
        elif cert_type == "cap_set":
            ok, msg = internal_verify_cap(data["points"], data["n"])
        elif cert_type == "qecc_stabilizer":
            ok, res_payload = internal_code_distance(data["stabilizers"])
            if ok:
                ok = (res_payload["k"] == data["k_claimed"]) and (
                    res_payload["d"] == data["d_claimed"]
                )
                msg = f"QECC verified: {res_payload}"
            else:
                msg = str(res_payload)
        else:
            raise AssertionError(f"Unknown certificate type: {cert_type}")

        assert ok, f"Internal verifier failed on {f.name}: {msg}"
