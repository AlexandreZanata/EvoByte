"""Generalized Symmetry and Non-Circulant Target Catalogue (P201).

Catalogue of exactly 5 open frontier targets with narrow gaps (gap <= 2)
in Quantum Error-Correcting Codes (Grassl codetables) and Covering Designs (LJCR),
requiring generalized non-circulant symmetries (quasi-cyclic / lifted product)
or affine / dihedral automorphism groups (AGL(1, q), D_m).

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.qecc_verifier import check_stabilizer, code_distance


@dataclass(frozen=True)
class GeneralizedTarget:
    """An immutable record representing an open target requiring generalized symmetry."""

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
class GeneralizedCalibrationTarget:
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

_QECC_18_3_GENERATORS: tuple[str, ...] = (
    "XIIIIIIIIXIXIXIIII",
    "IXIIIIIIIIYXZZZXII",
    "IIXIIIIIIXZYYXZYII",
    "IIIXIIIIIYXYXZIZII",
    "IIIIXIIIIZXYZIYIII",
    "IIIIIXIIIYYZZXYIII",
    "IIIIIIXIIIIIIIIIII",
    "IIIIIIIXZZZZZZZZII",
    "IIIIIIIIXXXXXXXXII",
    "IIIIIIIIZZZZZZZZII",
    "IIIIIIIIIIIIIIIIXI",
    "IIIIIIIIIIIIIIIIIX",
    "IIIIIIIIIIIIIIIIXZ",
    "IIIIIIIIIIIIIIIIZX",
    "IIIIIIIIIIIIIIIIYY",
)

# Reference generators and blocks for calibration targets
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

_STEANE_GENERATORS: tuple[str, ...] = (
    "IIIXXXX",
    "IXXIIXX",
    "XIXIXIX",
    "IIIZZZZ",
    "IZZIIZZ",
    "ZIZIZIZ",
)

_C_9_3_2_BLOCKS: tuple[tuple[int, ...], ...] = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    (1, 4, 7),
    (2, 5, 8),
    (3, 6, 9),
    (1, 5, 9),
    (2, 6, 7),
    (3, 4, 8),
    (1, 6, 8),
    (2, 4, 9),
    (3, 5, 7),
)


# Frozen tuple of exactly 5 generalized symmetry / non-circulant frontier targets
GENERALIZED_TARGETS: tuple[GeneralizedTarget, ...] = (
    GeneralizedTarget(
        target_id="qecc_14_3_noncirculant",
        family="qecc_stabilizer",
        name="[[14,3,d]]",
        params={"n": 14, "k": 3},
        role="record",
        objective="maximize",
        best_known_value=4,
        theoretical_bound=5,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 5",
        tie_condition="distance == 4 with CSS quasi-cyclic structure",
        candidate_symmetry_group="Bicirculant_QC_14",
        symmetry_order=28,
        source_id="grassl-codetables-qecc-14-3",
        snapshot_sha256="47188e2033fbd0227efdaa1d7a2d424109702fbec7389a2e4bd9b25a8bedd714",
        source_url="http://www.codetables.de/QECC.php?q=2&n=14&k=3",
        verifier_name="check_stabilizer_and_distance",
        certificate_status="active_frontier",
        reference_object=_QECC_14_3_GENERATORS,
        description=(
            "Grassl additive quantum code [[14,3,d]]: n=14 qubits, k=3 encoded qubits. "
            "Grassl lower bound d=4, upper bound d=5. Gap=1. "
            "Proposition 4.1 in P198 proved circulant CSS cannot exceed d=3. "
            "Target: quasi-cyclic bicirculant / lifted product structure breaking circulant symmetry to achieve d >= 4."
        ),
    ),
    GeneralizedTarget(
        target_id="qecc_16_5_noncirculant",
        family="qecc_stabilizer",
        name="[[16,5,d]]",
        params={"n": 16, "k": 5},
        role="record",
        objective="maximize",
        best_known_value=4,
        theoretical_bound=5,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 5",
        tie_condition="distance == 4 with CSS quasi-cyclic structure",
        candidate_symmetry_group="Bicirculant_QC_16",
        symmetry_order=32,
        source_id="grassl-codetables-qecc-16-5",
        snapshot_sha256="2a74240fb793bb88e3edfedd2b34d737595ba1080af2972498d1c0fee221316e",
        source_url="http://www.codetables.de/QECC.php?q=2&n=16&k=5",
        verifier_name="check_stabilizer_and_distance",
        certificate_status="active_frontier",
        reference_object=_QECC_16_5_GENERATORS,
        description=(
            "Grassl additive quantum code [[16,5,d]]: n=16 qubits, k=5 encoded qubits. "
            "Grassl lower bound d=4, upper bound d=5. Gap=1. "
            "Proposition 4.1 in P198 proved circulant CSS cannot exceed d=3. "
            "Target: quasi-cyclic bicirculant / lifted product structure breaking circulant symmetry to achieve d >= 4."
        ),
    ),
    GeneralizedTarget(
        target_id="qecc_18_3_noncirculant",
        family="qecc_stabilizer",
        name="[[18,3,d]]",
        params={"n": 18, "k": 3},
        role="record",
        objective="maximize",
        best_known_value=5,
        theoretical_bound=6,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 6",
        tie_condition="distance == 5 with CSS quasi-cyclic structure",
        candidate_symmetry_group="Bicirculant_QC_18",
        symmetry_order=36,
        source_id="grassl-codetables-qecc-18-3",
        snapshot_sha256="b7a370e26b83eedfab4bc73e75aa5f102e3ddebc1f2cc9de78e391b2b9b6560d",
        source_url="http://www.codetables.de/QECC.php?q=2&n=18&k=3",
        verifier_name="check_stabilizer_and_distance",
        certificate_status="active_frontier",
        reference_object=_QECC_18_3_GENERATORS,
        description=(
            "Grassl additive quantum code [[18,3,d]]: n=18 qubits, k=3 encoded qubits. "
            "Grassl lower bound d=5, upper bound d=6. Gap=1. "
            "Target: quasi-cyclic / bicirculant structure breaking single circulant block symmetry to seek d >= 5 or 6."
        ),
    ),
    GeneralizedTarget(
        target_id="covering_C_13_5_3_affine",
        family="covering_design",
        name="C(13,5,3)",
        params={"v": 13, "k": 5, "t": 3},
        role="record",
        objective="minimize",
        best_known_value=34,
        theoretical_bound=32,
        gap=2,
        proven_optimal=False,
        record_condition="size <= 33",
        tie_condition="size == 34 with affine symmetry AGL(1,13)",
        candidate_symmetry_group="AGL_1_13",
        symmetry_order=156,
        source_id="ljcr-coverdata-459bcaf",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        verifier_name="verify_covering_design",
        certificate_status="active_frontier",
        reference_object=None,
        description=(
            "Covering design C(13,5,3): 286 3-subsets of 13 points covered by 5-element blocks. "
            "World record 34 blocks (LJCR); theoretical lower bound 32. Gap=2. "
            "Resisted pure cyclic Z_13 symmetry in P196 (yielded 19 on C(13,5,3) sub-orbits). "
            "Target: 1-dimensional affine group AGL(1, 13) of order 156."
        ),
    ),
    GeneralizedTarget(
        target_id="covering_C_15_10_4_affine",
        family="covering_design",
        name="C(15,10,4)",
        params={"v": 15, "k": 10, "t": 4},
        role="record",
        objective="minimize",
        best_known_value=14,
        theoretical_bound=12,
        gap=2,
        proven_optimal=False,
        record_condition="size <= 13",
        tie_condition="size == 14 with dihedral symmetry D_15",
        candidate_symmetry_group="Dihedral_D15",
        symmetry_order=30,
        source_id="ljcr-coverdata-459bcaf",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://raw.githubusercontent.com/dmgordo/LJCR/459bcaf247bd8d34610d946b0465864f7d4dfa37/coverings/coverdata.json",
        verifier_name="verify_covering_design",
        certificate_status="active_frontier",
        reference_object=None,
        description=(
            "Covering design C(15,10,4): 1365 4-subsets of 15 points covered by 10-element blocks. "
            "World record 14 blocks (LJCR); theoretical lower bound 12. Gap=2. "
            "Target: dihedral group D_15 of order 30 (rotations + reflections modulo 15)."
        ),
    ),
)


# Frozen tuple of calibration targets with verified solutions
CALIBRATION_TARGETS: tuple[GeneralizedCalibrationTarget, ...] = (
    GeneralizedCalibrationTarget(
        target_id="calib_shor_9_1_3",
        family="qecc_stabilizer",
        name="[[9,1,3]]",
        params={"n": 9, "k": 1, "d": 3},
        role="calibration",
        expected_value=3,
        proven_optimal=True,
        verifier_name="check_stabilizer_and_distance",
        certificate_object=_SHOR_GENERATORS,
        description=(
            "Shor 9-qubit code [[9,1,3]]: non-circulant concatenation of 3-qubit phase and bit flip codes. "
            "Calibrates non-circulant stabilizer verification and distance evaluation."
        ),
    ),
    GeneralizedCalibrationTarget(
        target_id="calib_steane_7_1_3",
        family="qecc_stabilizer",
        name="[[7,1,3]]",
        params={"n": 7, "k": 1, "d": 3},
        role="calibration",
        expected_value=3,
        proven_optimal=True,
        verifier_name="check_stabilizer_and_distance",
        certificate_object=_STEANE_GENERATORS,
        description=(
            "Steane 7-qubit CSS code [[7,1,3]]: Fano plane parity check matrix under AGL(1, 7). "
            "Calibrates affine CSS stabilizer verification."
        ),
    ),
    GeneralizedCalibrationTarget(
        target_id="calib_covering_C_9_3_2",
        family="covering_design",
        name="C(9,3,2)",
        params={"v": 9, "k": 3, "t": 2},
        role="calibration",
        expected_value=12,
        proven_optimal=True,
        verifier_name="verify_covering_design",
        certificate_object=_C_9_3_2_BLOCKS,
        description=(
            "Affine plane AG(2, 3) covering design C(9,3,2)=12: 12 lines over GF(3)^2 covering all 36 pairs. "
            "Calibrates affine group block generation and verification."
        ),
    ),
)


def get_generalized_target_catalogue() -> tuple[GeneralizedTarget, ...]:
    """Return immutable tuple of the 5 generalized frontier targets."""
    return GENERALIZED_TARGETS


def get_target_by_id(target_id: str) -> GeneralizedTarget:
    """Lookup a generalized frontier target by target_id."""
    for t in GENERALIZED_TARGETS:
        if t.target_id == target_id:
            return t
    raise KeyError(f"Target '{target_id}' not found in generalized catalogue")


def get_generalized_calibration_catalogue() -> tuple[GeneralizedCalibrationTarget, ...]:
    """Return immutable tuple of the calibration targets."""
    return CALIBRATION_TARGETS


def get_calibration_by_id(target_id: str) -> GeneralizedCalibrationTarget:
    """Lookup a calibration target by target_id."""
    for c in CALIBRATION_TARGETS:
        if c.target_id == target_id:
            return c
    raise KeyError(f"Calibration target '{target_id}' not found")


def verify_target_candidate(target_id: str, candidate_object: Any) -> tuple[bool, Any]:
    """Verify a candidate solution against target rules."""
    target = get_target_by_id(target_id)
    if target.family == "covering_design":
        v = target.params["v"]
        k = target.params["k"]
        t = target.params["t"]
        return verify_covering_design(candidate_object, v, k, t)
    elif target.family == "qecc_stabilizer":
        chk_ok, chk_payload = check_stabilizer(candidate_object)
        if not chk_ok:
            return False, chk_payload
        dist_ok, dist_payload = code_distance(candidate_object)
        if not dist_ok:
            return False, dist_payload
        return True, {"check": chk_payload, "distance": dist_payload}
    raise ValueError(f"Unknown family: {target.family}")


def verify_calibration_candidate(target_id: str, candidate_object: Any) -> tuple[bool, Any]:
    """Verify a calibration candidate object."""
    calib = get_calibration_by_id(target_id)
    if calib.family == "covering_design":
        v = calib.params["v"]
        k = calib.params["k"]
        t = calib.params["t"]
        return verify_covering_design(candidate_object, v, k, t)
    elif calib.family == "qecc_stabilizer":
        chk_ok, chk_payload = check_stabilizer(candidate_object)
        if not chk_ok:
            return False, chk_payload
        dist_ok, dist_payload = code_distance(candidate_object)
        if not dist_ok:
            return False, dist_payload
        return True, {"check": chk_payload, "distance": dist_payload}
    raise ValueError(f"Unknown calibration family: {calib.family}")


def export_catalogue_to_json(out_path: Path | str) -> None:
    """Serialize the catalogue to JSON format for durable snapshotting."""
    path = Path(out_path)
    data = {
        "version": "1.0.0",
        "program": "Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045)",
        "phase": "P201",
        "target_count": len(GENERALIZED_TARGETS),
        "calibration_count": len(CALIBRATION_TARGETS),
        "targets": [asdict(t) for t in GENERALIZED_TARGETS],
        "calibrations": [asdict(c) for c in CALIBRATION_TARGETS],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
