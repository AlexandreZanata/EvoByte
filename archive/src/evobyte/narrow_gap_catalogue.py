"""Narrow Gap Frontier Target Catalogue (P191).

Catalogue of exactly 5 open frontier targets with narrow gaps (gap <= 2)
in Covering Designs (LJCR) and Quantum Error-Correcting Codes (Grassl codetables),
together with calibrated zero-dependency verifiers, snapshot provenance,
and candidate cyclic/circulant symmetry groups.

Part of the Structured Discovery and Functional Synthesis Program (P191-P200, D043).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.qecc_verifier import check_stabilizer, code_distance


@dataclass(frozen=True)
class NarrowGapTarget:
    """An immutable record representing a narrow-gap frontier target."""

    target_id: str
    family: str
    name: str
    params: Mapping[str, int]
    role: str
    objective: str
    best_known_value: int
    theoretical_bound: int
    gap: int
    proven_optimal: bool
    record_condition: str
    tie_condition: str
    candidate_symmetry_group: str
    symmetry_order: int
    source_id: str
    snapshot_sha256: str
    source_url: str
    verifier_name: str
    certificate_status: str
    reference_object: Any
    description: str


@dataclass(frozen=True)
class CalibrationTarget:
    """An immutable calibration target with a known exact solution."""

    target_id: str
    family: str
    name: str
    params: Mapping[str, int]
    role: str
    expected_value: int
    proven_optimal: bool
    verifier_name: str
    certificate_object: Any
    description: str


# Reference generator strings for QECC open record targets from verified Markus Grassl snapshots
_QECC_14_3_GENERATORS: tuple[str, ...] = (
    "XIIIYIIXZZYZII",
    "ZIIZXYIZYIYZII",
    "IXIIZXIXIIIXII",
    "IZIZYXIZIYZYII",
    "IIXIXYIIXYYXII",
    "IIZZZZIIZZYYII",
    "IIIXIZIIIZXYII",
    "IIIIIIXXXXXXII",
    "IIIIIIZZZZZZII",
    "IIIIIIIIIIIIXI",
    "IIIIIIIIIIIIIX",
)

_QECC_16_5_GENERATORS: tuple[str, ...] = (
    "XIIIYZIXYYXXIXII",
    "ZIIZXYIZXYZIYXII",
    "IXIIZYIXZZIIIXII",
    "IZIZYXIZYXIZYXII",
    "IIXIXXIIIXXIYYII",
    "IIZZZZIIIIZZZZII",
    "IIIXIIIIIXIXZZII",
    "IIIIIIXXXXXXXXII",
    "IIIIIIZZZZZZZZII",
    "IIIIIIIIIIIIIIXI",
    "IIIIIIIIIIIIIIIX",
)

# Reference generators for calibration targets
_STEANE_GENERATORS: tuple[str, ...] = (
    "IIIXXXX",
    "IXXIIXX",
    "XIXIXIX",
    "IIIZZZZ",
    "IZZIIZZ",
    "ZIZIZIZ",
)

_SHOR_GENERATORS: tuple[str, ...] = (
    "ZZIIIIIII",
    "IZZIIIIII",
    "IIIZZIIII",
    "IIIIZZIII",
    "IIIIIIZZI",
    "IIIIIIIZZ",
    "XXXXXXIII",
    "IIIXXXXXX",
)

_FIVE_QUBIT_GENERATORS: tuple[str, ...] = (
    "XZZXI",
    "IXZZX",
    "XIXZZ",
    "ZXIXZ",
)

_C_7_3_2_BLOCKS: tuple[tuple[int, ...], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (1, 6, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 5, 6),
)

_C_8_4_3_BLOCKS: tuple[tuple[int, ...], ...] = (
    (1, 3, 5, 7),
    (2, 4, 6, 8),
    (1, 2, 5, 6),
    (3, 4, 7, 8),
    (1, 4, 5, 8),
    (2, 3, 6, 7),
    (1, 2, 3, 4),
    (5, 6, 7, 8),
    (1, 3, 6, 8),
    (2, 4, 5, 7),
    (1, 2, 7, 8),
    (3, 4, 5, 6),
    (1, 4, 6, 7),
    (2, 3, 5, 8),
)


# Frozen tuple of exactly 5 narrow-gap frontier targets
NARROW_GAP_TARGETS: tuple[NarrowGapTarget, ...] = (
    NarrowGapTarget(
        target_id="covering_C_13_6_3",
        family="covering_design",
        name="C(13,6,3)",
        params={"v": 13, "k": 6, "t": 3},
        role="record",
        objective="minimize",
        best_known_value=21,
        theoretical_bound=20,
        gap=1,
        proven_optimal=False,
        record_condition="size <= 20",
        tie_condition="size == 21 non-isomorphic",
        candidate_symmetry_group="Z_13",
        symmetry_order=13,
        source_id="ljcr-coverdata-459bcaf",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        verifier_name="verify_covering_design",
        certificate_status="site_unreachable",
        reference_object=None,
        description=(
            "Covering design C(13,6,3): 286 3-subsets of 13 points covered by 6-element blocks. "
            "Stale record of 21 blocks since 1996; theoretical lower bound 20. Gap=1. "
            "Automorphism candidates: Z_13 cyclic orbits."
        ),
    ),
    NarrowGapTarget(
        target_id="covering_C_14_6_3",
        family="covering_design",
        name="C(14,6,3)",
        params={"v": 14, "k": 6, "t": 3},
        role="record",
        objective="minimize",
        best_known_value=25,
        theoretical_bound=24,
        gap=1,
        proven_optimal=False,
        record_condition="size <= 24",
        tie_condition="size == 25 non-isomorphic",
        candidate_symmetry_group="Z_14",
        symmetry_order=14,
        source_id="ljcr-coverdata-459bcaf",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        verifier_name="verify_covering_design",
        certificate_status="site_unreachable",
        reference_object=None,
        description=(
            "Covering design C(14,6,3): 364 3-subsets of 14 points covered by 6-element blocks. "
            "Stale record of 25 blocks since 1996; theoretical lower bound 24. Gap=1. "
            "Automorphism candidates: Z_14 cyclic or Z_13 + fixed point."
        ),
    ),
    NarrowGapTarget(
        target_id="covering_C_15_8_4",
        family="covering_design",
        name="C(15,8,4)",
        params={"v": 15, "k": 8, "t": 4},
        role="record",
        objective="minimize",
        best_known_value=30,
        theoretical_bound=29,
        gap=1,
        proven_optimal=False,
        record_condition="size <= 29",
        tie_condition="size == 30 non-isomorphic",
        candidate_symmetry_group="Z_15",
        symmetry_order=15,
        source_id="ljcr-coverdata-459bcaf",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        verifier_name="verify_covering_design",
        certificate_status="site_unreachable",
        reference_object=None,
        description=(
            "Covering design C(15,8,4): 1365 4-subsets of 15 points covered by 8-element blocks. "
            "Stale record of 30 blocks since 1996; theoretical lower bound 29. Gap=1. "
            "Automorphism candidates: Z_15 cyclic or Z_5 x Z_3 factorization."
        ),
    ),
    NarrowGapTarget(
        target_id="qecc_14_3_open",
        family="qecc_stabilizer",
        name="[[14,3,4-5]]",
        params={"n": 14, "k": 3},
        role="record",
        objective="maximize",
        best_known_value=4,
        theoretical_bound=5,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 5",
        tie_condition="distance == 4 non-isomorphic",
        candidate_symmetry_group="circulant_Z_14",
        symmetry_order=14,
        source_id="grassl-codetables-14-3",
        snapshot_sha256="47188e2033fbd0227efdaa1d7a2d424109702fbec7389a2e4bd9b25a8bedd714",
        source_url="https://codetables.de/QECC.php?q=4&n=14&k=3",
        verifier_name="code_distance",
        certificate_status="verified_snapshot",
        reference_object=_QECC_14_3_GENERATORS,
        description=(
            "Quantum stabilizer code [[14,3,d]]: n=14 qubits, k=3 encoded qubits. "
            "Markus Grassl tables document d_lo=4, d_hi=5. Gap=1. "
            "Automorphism candidates: circulant block generators over Z_14."
        ),
    ),
    NarrowGapTarget(
        target_id="qecc_16_5_open",
        family="qecc_stabilizer",
        name="[[16,5,4-5]]",
        params={"n": 16, "k": 5},
        role="record",
        objective="maximize",
        best_known_value=4,
        theoretical_bound=5,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 5",
        tie_condition="distance == 4 non-isomorphic",
        candidate_symmetry_group="circulant_Z_16",
        symmetry_order=16,
        source_id="grassl-codetables-16-5",
        snapshot_sha256="2a74240fb793bb88e3edfedd2b34d737595ba1080af2972498d1c0fee221316e",
        source_url="https://codetables.de/QECC.php?q=4&n=16&k=5",
        verifier_name="code_distance",
        certificate_status="verified_snapshot",
        reference_object=_QECC_16_5_GENERATORS,
        description=(
            "Quantum stabilizer code [[16,5,d]]: n=16 qubits, k=5 encoded qubits. "
            "Markus Grassl tables document d_lo=4, d_hi=5. Gap=1. "
            "Automorphism candidates: circulant block generators over Z_16."
        ),
    ),
)


CALIBRATION_TARGETS: tuple[CalibrationTarget, ...] = (
    CalibrationTarget(
        target_id="covering_C_7_3_2",
        family="covering_design",
        name="C(7,3,2)",
        params={"v": 7, "k": 3, "t": 2},
        role="calibration",
        expected_value=7,
        proven_optimal=True,
        verifier_name="verify_covering_design",
        certificate_object=_C_7_3_2_BLOCKS,
        description="Fano plane 2-(7,3,1) Steiner system: exactly 7 blocks covering all 21 pairs.",
    ),
    CalibrationTarget(
        target_id="covering_C_8_4_3",
        family="covering_design",
        name="C(8,4,3)",
        params={"v": 8, "k": 4, "t": 3},
        role="calibration",
        expected_value=14,
        proven_optimal=True,
        verifier_name="verify_covering_design",
        certificate_object=_C_8_4_3_BLOCKS,
        description="Affine geometry AG(3,2) 3-(8,4,1) design: exactly 14 blocks covering all 56 triples.",
    ),
    CalibrationTarget(
        target_id="steane_7_1_3",
        family="qecc_stabilizer",
        name="[[7,1,3]]",
        params={"n": 7, "k": 1},
        role="calibration",
        expected_value=3,
        proven_optimal=True,
        verifier_name="code_distance",
        certificate_object=_STEANE_GENERATORS,
        description="Steane 7-qubit CSS code [[7,1,3]]: distance 3.",
    ),
    CalibrationTarget(
        target_id="shor_9_1_3",
        family="qecc_stabilizer",
        name="[[9,1,3]]",
        params={"n": 9, "k": 1},
        role="calibration",
        expected_value=3,
        proven_optimal=True,
        verifier_name="code_distance",
        certificate_object=_SHOR_GENERATORS,
        description="Shor 9-qubit code [[9,1,3]]: distance 3.",
    ),
    CalibrationTarget(
        target_id="five_qubit_5_1_3",
        family="qecc_stabilizer",
        name="[[5,1,3]]",
        params={"n": 5, "k": 1},
        role="calibration",
        expected_value=3,
        proven_optimal=True,
        verifier_name="code_distance",
        certificate_object=_FIVE_QUBIT_GENERATORS,
        description="Perfect 5-qubit code [[5,1,3]]: distance 3.",
    ),
)


def get_narrow_gap_catalogue() -> list[NarrowGapTarget]:
    """Return a list of all frozen narrow-gap frontier targets."""
    return list(NARROW_GAP_TARGETS)


def get_calibration_catalogue() -> list[CalibrationTarget]:
    """Return a list of all calibration targets."""
    return list(CALIBRATION_TARGETS)


def get_target_by_id(target_id: str) -> NarrowGapTarget:
    """Lookup a narrow-gap target by its identifier.

    Raises KeyError if target_id is not found.
    """
    for t in NARROW_GAP_TARGETS:
        if t.target_id == target_id:
            return t
    raise KeyError(f"Target ID {target_id!r} not found in narrow-gap catalogue")


def get_calibration_by_id(target_id: str) -> CalibrationTarget:
    """Lookup a calibration target by its identifier.

    Raises KeyError if target_id is not found.
    """
    for c in CALIBRATION_TARGETS:
        if c.target_id == target_id:
            return c
    raise KeyError(f"Calibration ID {target_id!r} not found in calibration catalogue")


def verify_target_candidate(target_id: str, candidate_object: Any) -> tuple[bool, Any]:
    """Verify a candidate object against the target specification.

    Dispatches to verify_covering_design for covering designs and code_distance for QECC.
    Returns (ok, payload_or_reason).
    """
    try:
        target = get_target_by_id(target_id)
    except KeyError:
        return False, f"Unknown target_id: {target_id}"

    if target.family == "covering_design":
        v = target.params["v"]
        k = target.params["k"]
        t = target.params["t"]
        return verify_covering_design(candidate_object, v, k, t)

    if target.family == "qecc_stabilizer":
        n = target.params["n"]
        k = target.params["k"]
        ok_stab, stab_res = check_stabilizer(candidate_object)
        if not ok_stab:
            return False, f"Stabilizer check failed: {stab_res}"
        if not isinstance(stab_res, dict):
            return False, "Malformed stabilizer result"
        if stab_res.get("n") != n or stab_res.get("k") != k:
            return (
                False,
                f"Dimension mismatch: expected [[{n},{k}]], got [[{stab_res.get('n')},{stab_res.get('k')}]]",
            )
        ok_dist, dist_res = code_distance(candidate_object)
        if not ok_dist:
            return False, f"Code distance calculation failed: {dist_res}"
        return True, dist_res

    return False, f"Unsupported family: {target.family}"


def export_narrow_gap_catalogue_json(output_path: Path | str) -> None:
    """Export the narrow-gap catalogue and calibrations to a structured JSON file."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0",
        "program": "P191-P200 Structured Discovery (D043)",
        "freeze_date": "2026-10-26",
        "num_record_targets": len(NARROW_GAP_TARGETS),
        "num_calibration_targets": len(CALIBRATION_TARGETS),
        "targets": [asdict(t) for t in NARROW_GAP_TARGETS],
        "calibrations": [asdict(c) for c in CALIBRATION_TARGETS],
    }
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
