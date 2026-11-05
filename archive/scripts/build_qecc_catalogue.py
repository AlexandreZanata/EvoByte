#!/usr/bin/env python3
"""Build and verify QECC Frontier Catalogue v1 (P180).

Deterministic builder and validator for:
- docs/research/targets/qecc_frontier_v1.json
- docs/research/targets/qecc_sources_v1.json

Usage:
    python3 scripts/build_qecc_catalogue.py          # builds both JSON files
    python3 scripts/build_qecc_catalogue.py --check  # verifies committed files match reconstruction
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "quantum"
TARGETS_DIR = REPO_ROOT / "docs" / "research" / "targets"
CATALOGUE_PATH = TARGETS_DIR / "qecc_frontier_v1.json"
SOURCES_PATH = TARGETS_DIR / "qecc_sources_v1.json"

SOURCES_META: dict[str, dict[str, Any]] = {
    "grassl-codetables-bounds": {
        "source_id": "grassl-codetables-bounds",
        "url": "https://codetables.de/QECC/Tables_color.php?q=4&n0=1&n1=30&k0=0&k1=10",
        "sha256": "52c8a9c9c41ad8faa3f953cf689ae73b0454a74d0d485caeb5a5ec1cb7c98f3e",
        "accessed_at": "2026-10-25T16:23:37Z",
        "status": "verified_snapshot",
        "notes": (
            "Markus Grassl's table of bounds on the minimum distance of qubit "
            "quantum codes [[n,k,d]]_2 for length 1<=n<=30 and dimension 0<=k<=10."
        ),
    },
    "grassl-codetables-20-2": {
        "source_id": "grassl-codetables-20-2",
        "url": "https://codetables.de/QECC.php?q=4&n=20&k=2",
        "sha256": "85a30663ec80ac6f7f46f2f3dd79b31ad066ba4f1b2ae4c43cebde10ed1d1c02",
        "accessed_at": "2026-10-25T16:23:24Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[20,2]] qubit code with d_lo=6, d_hi=7 and stabilizer matrix."),
    },
    "grassl-codetables-20-3": {
        "source_id": "grassl-codetables-20-3",
        "url": "https://codetables.de/QECC.php?q=4&n=20&k=3",
        "sha256": "df71b4f69a085f4e7daa566c2b2cd145b238d8409599e86ffa42938f5aa29fe4",
        "accessed_at": "2026-10-25T16:25:14Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[20,3]] qubit code with d_lo=6, d_hi=7 and stabilizer matrix."),
    },
    "grassl-codetables-14-3": {
        "source_id": "grassl-codetables-14-3",
        "url": "https://codetables.de/QECC.php?q=4&n=14&k=3",
        "sha256": "47188e2033fbd0227efdaa1d7a2d424109702fbec7389a2e4bd9b25a8bedd714",
        "accessed_at": "2026-10-25T16:24:00Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[14,3]] qubit code with d_lo=4, d_hi=5 and stabilizer matrix."),
    },
    "grassl-codetables-16-5": {
        "source_id": "grassl-codetables-16-5",
        "url": "https://codetables.de/QECC.php?q=4&n=16&k=5",
        "sha256": "2a74240fb793bb88e3edfedd2b34d737595ba1080af2972498d1c0fee221316e",
        "accessed_at": "2026-10-25T16:24:00Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[16,5]] qubit code with d_lo=4, d_hi=5 and stabilizer matrix."),
    },
    "grassl-codetables-17-3": {
        "source_id": "grassl-codetables-17-3",
        "url": "https://codetables.de/QECC.php?q=4&n=17&k=3",
        "sha256": "fa62cfe2fed23e1380fb7408ec1e0d61720190daac7bd6ea329669362e5cfcbe",
        "accessed_at": "2026-10-25T16:25:14Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[17,3]] qubit code with d_lo=5, d_hi=6 and stabilizer matrix."),
    },
    "grassl-codetables-18-3": {
        "source_id": "grassl-codetables-18-3",
        "url": "https://codetables.de/QECC.php?q=4&n=18&k=3",
        "sha256": "b7a370e26b83eedfab4bc73e75aa5f102e3ddebc1f2cc9de78e391b2b9b6560d",
        "accessed_at": "2026-10-25T16:25:14Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[18,3]] qubit code with d_lo=5, d_hi=6 and stabilizer matrix."),
    },
    "grassl-codetables-19-10": {
        "source_id": "grassl-codetables-19-10",
        "url": "https://codetables.de/QECC.php?q=4&n=19&k=10",
        "sha256": "88c7d050a1cce6fbe150f742383f2413c00d7c5ae37e55ae73f746b7475bf427",
        "accessed_at": "2026-10-25T16:25:14Z",
        "status": "verified_snapshot",
        "notes": ("Markus Grassl: [[19,10]] qubit code with d_lo=3, d_hi=4 and stabilizer matrix."),
    },
    "steane-1996": {
        "source_id": "steane-1996",
        "url": "https://doi.org/10.1098/rspa.1996.0136",
        "sha256": "bf4553229b47e804fce571a067ff5067a9cf608304e226a31c57e84cbef51ce8",
        "accessed_at": "2026-10-24T10:33:00Z",
        "status": "peer_reviewed_literature",
        "notes": (
            "A. M. Steane (1996): Error Correcting Codes in Quantum Theory. "
            "Steane [[7,1,3]] CSS code based on Hamming [7,4,3]."
        ),
    },
    "shor-1995": {
        "source_id": "shor-1995",
        "url": "https://doi.org/10.1103/PhysRevA.52.R2493",
        "sha256": "d9a33bb7f525bf4e397ba3d0ec422171ecba3a8b4ecbfb2e23035be48cbcf124",
        "accessed_at": "2026-10-24T10:33:00Z",
        "status": "peer_reviewed_literature",
        "notes": (
            "P. W. Shor (1995): Scheme for reducing decoherence in quantum computer memory. "
            "Shor [[9,1,3]] code."
        ),
    },
    "laflamme-1996": {
        "source_id": "laflamme-1996",
        "url": "https://doi.org/10.1103/PhysRevLett.77.198",
        "sha256": "e25f6e8ccae700444565eb63567d26da5381fbc036329a27c0062a4b8682a033",
        "accessed_at": "2026-10-25T16:24:00Z",
        "status": "peer_reviewed_literature",
        "notes": (
            "R. Laflamme, C. Miquel, J. P. Paz, W. H. Zurek (1996): Perfect Quantum Error "
            "Correcting Code. Perfect 5-qubit code [[5,1,3]]."
        ),
    },
}

CALIBRATION_TARGETS: list[dict[str, Any]] = [
    {
        "target_id": "steane_7_1_3",
        "family": "qecc_stabilizer",
        "n": 7,
        "k": 1,
        "d_lo": 3,
        "d_hi": 3,
        "objective": "exact verification of canonical Steane [[7,1,3]] code",
        "role": "calibration",
        "best_known_value": 3,
        "source_convention": "exact known code [[7,1,3]] (Steane 1996)",
        "claimed_values": [{"value": 3, "source_id": "steane-1996"}],
        "verifier": "qecc_verifier.code_distance",
        "certificate_status": "constructed_calibration",
        "certificate_object": [
            "IIIXXXX",
            "IXXIIXX",
            "XIXIXIX",
            "IIIZZZZ",
            "IZZIIZZ",
            "ZIZIZIZ",
        ],
    },
    {
        "target_id": "shor_9_1_3",
        "family": "qecc_stabilizer",
        "n": 9,
        "k": 1,
        "d_lo": 3,
        "d_hi": 3,
        "objective": "exact verification of canonical Shor [[9,1,3]] code",
        "role": "calibration",
        "best_known_value": 3,
        "source_convention": "exact known code [[9,1,3]] (Shor 1995)",
        "claimed_values": [{"value": 3, "source_id": "shor-1995"}],
        "verifier": "qecc_verifier.code_distance",
        "certificate_status": "constructed_calibration",
        "certificate_object": [
            "ZZIIIIIII",
            "IZZIIIIII",
            "IIIZZIIII",
            "IIIIZZIII",
            "IIIIIIZZI",
            "IIIIIIIZZ",
            "XXXXXXIII",
            "IIIXXXXXX",
        ],
    },
    {
        "target_id": "five_qubit_5_1_3",
        "family": "qecc_stabilizer",
        "n": 5,
        "k": 1,
        "d_lo": 3,
        "d_hi": 3,
        "objective": "exact verification of 5-qubit perfect code [[5,1,3]]",
        "role": "calibration",
        "best_known_value": 3,
        "source_convention": "exact known code [[5,1,3]] (Laflamme et al. 1996)",
        "claimed_values": [{"value": 3, "source_id": "laflamme-1996"}],
        "verifier": "qecc_verifier.code_distance",
        "certificate_status": "constructed_calibration",
        "certificate_object": [
            "XZZXI",
            "IXZZX",
            "XIXZZ",
            "ZXIXZ",
        ],
    },
    {
        "target_id": "error_detect_4_2_2",
        "family": "qecc_stabilizer",
        "n": 4,
        "k": 2,
        "d_lo": 2,
        "d_hi": 2,
        "objective": "exact verification of error detection code [[4,2,2]]",
        "role": "calibration",
        "best_known_value": 2,
        "source_convention": "exact known code [[4,2,2]]",
        "claimed_values": [{"value": 2, "source_id": "grassl-codetables-bounds"}],
        "verifier": "qecc_verifier.code_distance",
        "certificate_status": "constructed_calibration",
        "certificate_object": [
            "XXXX",
            "ZZZZ",
        ],
    },
    {
        "target_id": "repetition_3_1_1",
        "family": "qecc_stabilizer",
        "n": 3,
        "k": 1,
        "d_lo": 1,
        "d_hi": 1,
        "objective": "exact verification of 3-qubit bit-flip code [[3,1,1]]",
        "role": "calibration",
        "best_known_value": 1,
        "source_convention": "bit-flip code [[3,1,1]]",
        "claimed_values": [{"value": 1, "source_id": "grassl-codetables-bounds"}],
        "verifier": "qecc_verifier.code_distance",
        "certificate_status": "constructed_calibration",
        "certificate_object": [
            "ZZI",
            "IZZ",
        ],
    },
]

RECORD_TARGET_SPECS: list[dict[str, Any]] = [
    {
        "target_id": "qecc_14_3_open",
        "n": 14,
        "k": 3,
        "d_lo": 4,
        "d_hi": 5,
        "source_id": "grassl-codetables-14-3",
        "snapshot_filename": "codetables_qecc_14_3.html",
    },
    {
        "target_id": "qecc_16_5_open",
        "n": 16,
        "k": 5,
        "d_lo": 4,
        "d_hi": 5,
        "source_id": "grassl-codetables-16-5",
        "snapshot_filename": "codetables_qecc_16_5.html",
    },
    {
        "target_id": "qecc_17_3_open",
        "n": 17,
        "k": 3,
        "d_lo": 5,
        "d_hi": 6,
        "source_id": "grassl-codetables-17-3",
        "snapshot_filename": "codetables_qecc_17_3.html",
    },
    {
        "target_id": "qecc_18_3_open",
        "n": 18,
        "k": 3,
        "d_lo": 5,
        "d_hi": 6,
        "source_id": "grassl-codetables-18-3",
        "snapshot_filename": "codetables_qecc_18_3.html",
    },
    {
        "target_id": "qecc_19_10_open",
        "n": 19,
        "k": 10,
        "d_lo": 3,
        "d_hi": 4,
        "source_id": "grassl-codetables-19-10",
        "snapshot_filename": "codetables_qecc_19_10.html",
    },
    {
        "target_id": "qecc_20_2_open",
        "n": 20,
        "k": 2,
        "d_lo": 6,
        "d_hi": 7,
        "source_id": "grassl-codetables-20-2",
        "snapshot_filename": "codetables_qecc_20_2.html",
    },
    {
        "target_id": "qecc_20_3_open",
        "n": 20,
        "k": 3,
        "d_lo": 6,
        "d_hi": 7,
        "source_id": "grassl-codetables-20-3",
        "snapshot_filename": "codetables_qecc_20_3.html",
    },
]


def _parse_stabilizer_matrix(html_text: str, n_expected: int) -> list[str]:
    mapping = {("0", "0"): "I", ("1", "0"): "X", ("0", "1"): "Z", ("1", "1"): "Y"}
    rows = re.findall(r"\[([0-1 ]+)\|([0-1 ]+)\]", html_text)
    paulis: list[str] = []
    for xr, zr in rows:
        xs = xr.split()
        zs = zr.split()
        if len(xs) != n_expected or len(zs) != n_expected:
            raise ValueError(f"Row dimension mismatch: {len(xs)}, expected {n_expected}")
        paulis.append("".join(mapping[(x, z)] for x, z in zip(xs, zs)))
    return paulis


def build_catalogue() -> dict[str, Any]:
    """Deterministically construct catalogue and verify snapshot checksums."""
    targets: list[dict[str, Any]] = []

    # 1. Add calibrations
    for cal in CALIBRATION_TARGETS:
        targets.append(dict(cal))

    # 2. Add record targets parsed from snapshot files
    for spec in RECORD_TARGET_SPECS:
        target_id = spec["target_id"]
        n = spec["n"]
        k = spec["k"]
        d_lo = spec["d_lo"]
        d_hi = spec["d_hi"]
        source_id = spec["source_id"]
        snapshot_file = RAW_DIR / spec["snapshot_filename"]

        if not snapshot_file.exists():
            raise FileNotFoundError(
                f"Missing required snapshot file: {snapshot_file}. "
                "Download snapshots before building catalogue."
            )

        content_bytes = snapshot_file.read_bytes()
        actual_sha = hashlib.sha256(content_bytes).hexdigest()
        expected_sha = SOURCES_META[source_id]["sha256"]
        if actual_sha != expected_sha:
            raise ValueError(
                f"SHA256 mismatch for {snapshot_file.name}: "
                f"got {actual_sha}, expected {expected_sha}"
            )

        html_text = content_bytes.decode("utf-8")
        lb_m = re.search(r"lower bound:</TD><TD>(\d+)", html_text)
        ub_m = re.search(r"upper bound:</TD><TD>(\d+)", html_text)
        if not lb_m or not ub_m:
            raise ValueError(f"Bounds not found in {snapshot_file.name}")
        parsed_d_lo = int(lb_m.group(1))
        parsed_d_hi = int(ub_m.group(1))
        if parsed_d_lo != d_lo or parsed_d_hi != d_hi:
            raise ValueError(
                f"Bounds mismatch in {snapshot_file.name}: "
                f"found [{parsed_d_lo}, {parsed_d_hi}], expected [{d_lo}, {d_hi}]"
            )

        paulis = _parse_stabilizer_matrix(html_text, n)
        if len(paulis) != n - k:
            raise ValueError(f"Stabilizer row count {len(paulis)} != n-k ({n - k}) for {target_id}")

        target_entry: dict[str, Any] = {
            "target_id": target_id,
            "family": "qecc_stabilizer",
            "n": n,
            "k": k,
            "d_lo": d_lo,
            "d_hi": d_hi,
            "objective": f"achieve d >= {d_hi} via explicit stabilizer set, or prove d >= {d_lo + 1}",
            "role": "record",
            "best_known_value": d_lo,
            "source_convention": "lower bound = maior d com construção explícita publicada nas tabelas de Grassl",
            "claimed_values": [{"value": d_lo, "source_id": source_id}],
            "verifier": "qecc_verifier.code_distance",
            "certificate_status": "verified_published_object",
            "certificate_object": paulis,
        }
        targets.append(target_entry)

    catalogue: dict[str, Any] = {
        "version": "1.0.0",
        "catalogue_date": "2026-10-25",
        "description": "QECC Frontier Target Catalogue based on Markus Grassl bounds (P180)",
        "targets": targets,
    }
    return catalogue


def write_all() -> None:
    TARGETS_DIR.mkdir(parents=True, exist_ok=True)
    catalogue = build_catalogue()

    cat_json = json.dumps(catalogue, indent=2, sort_keys=True) + "\n"
    CATALOGUE_PATH.write_text(cat_json, encoding="utf-8")

    sources_json = json.dumps(SOURCES_META, indent=2, sort_keys=True) + "\n"
    SOURCES_PATH.write_text(sources_json, encoding="utf-8")
    print(f"Wrote catalogue ({len(catalogue['targets'])} targets) -> {CATALOGUE_PATH}")
    print(f"Wrote sources ({len(SOURCES_META)} sources) -> {SOURCES_PATH}")


def check_all() -> bool:
    if not CATALOGUE_PATH.exists():
        print(f"ERROR: Catalogue file {CATALOGUE_PATH} does not exist.")
        return False
    if not SOURCES_PATH.exists():
        print(f"ERROR: Sources file {SOURCES_PATH} does not exist.")
        return False

    committed_cat_text = CATALOGUE_PATH.read_text(encoding="utf-8")
    committed_src_text = SOURCES_PATH.read_text(encoding="utf-8")

    rebuilt_cat = build_catalogue()
    rebuilt_cat_text = json.dumps(rebuilt_cat, indent=2, sort_keys=True) + "\n"
    rebuilt_src_text = json.dumps(SOURCES_META, indent=2, sort_keys=True) + "\n"

    if committed_cat_text != rebuilt_cat_text:
        print("ERROR: Committed catalogue does not match deterministic reconstruction!")
        return False
    if committed_src_text != rebuilt_src_text:
        print("ERROR: Committed sources do not match deterministic reconstruction!")
        return False

    print("ALL QECC CATALOGUE CHECK GATES PASSED DETERMINISTICALLY!")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="QECC Frontier Target Catalogue v1 builder")
    parser.add_argument(
        "--check", action="store_true", help="Verify committed files match reconstruction"
    )
    args = parser.parse_args()

    if args.check:
        if not check_all():
            sys.exit(1)
    else:
        write_all()
        if not check_all():
            sys.exit(1)


if __name__ == "__main__":
    main()
