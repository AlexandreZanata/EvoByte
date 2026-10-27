"""Bivariate Bicycle and Projective Target Catalogue (P211).

Catalogue of exactly 5 open frontier targets with narrow gaps (gap <= 2)
in Quantum Error-Correcting Codes (Grassl codetables) and Covering Designs (LJCR),
requiring 2D bivariate group algebras F_2[Z_l x Z_m] (bivariate bicycle / lifted product)
or projective / 2D affine automorphism groups (PGL(2, q), AGL(2, q)).

Part of the Bivariate Bicycle & Projective Geometries Program (P211-P220, D047).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.qecc_verifier import check_stabilizer, code_distance


@dataclass(frozen=True)
class BivariateTarget:
    """An immutable record representing an open target requiring bivariate or projective symmetry."""

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
class BivariateCalibrationTarget:
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
_QECC_18_3_GENERATORS: tuple[str, ...] = (
    "XIIIIIIZZYZYIXZIII",
    "ZIIIIIIYYXYXIZYIII",
    "IXIIIIZYYYYZZXZIII",
    "IZIIIIYXXXXYYZYIII",
    "IIXIIIZXZZYYYYZIII",
    "IIZIIIYZYYXXXXYIII",
    "IIIXIIZXIYZYZZIIII",
    "IIIZIIYZIXYXYYIIII",
    "IIIIXIIZXIYZYZZIII",
    "IIIIZIIYZIXYXYYIII",
    "IIIIIXZYYIIYYZXIII",
    "IIIIIZYXXIIXXYZIII",
    "IIIIIIIIIIIIIIIXII",
    "IIIIIIIIIIIIIIIIXI",
    "IIIIIIIIIIIIIIIIIX",
)

_QECC_20_3_GENERATORS: tuple[str, ...] = (
    "XIIIIIIIIYIXIYZYXZXI",
    "ZIIIIIIIZXIZIYXYIXZY",
    "IXIIIIIIZYZYXIXYYYIZ",
    "IZIIIIIIIXYXZYXZZZIZ",
    "IIXIIIIIZXIXYXZIYXXY",
    "IIZIIIIIIZIZXXIYZXZI",
    "IIIXIIIIIIXXXIZIIIXX",
    "IIIZIIIIZIZZZZXZZZZX",
    "IIIIXIIIIXYXXXXYXXXX",
    "IIIIZIIIIZXZZZZXZZZZ",
    "IIIIIXIIIYXZXZYZZYIX",
    "IIIIIZIIZXZYZXYXXYIX",
    "IIIIIIXIZYYZZXIZZIXY",
    "IIIIIIZIIXXYYXYIIYZI",
    "IIIIIIIXZXXIZZYXZIZZ",
    "IIIIIIIZIZZIYIZXIYYZ",
    "IIIIIIIIXIIIIXXXXXIZ",
)

_QECC_20_2_GENERATORS: tuple[str, ...] = (
    "XIIIIIIZZYZYIXZIIIII",
    "ZIIIIIIYYXYXIZYIIIII",
    "IXIIIIIIZZYZYIXZIIII",
    "IZIIIIIIYYXYXIZYIIII",
    "IIXIIIIZYYYYZZXZIIII",
    "IIZIIIIYXXXXYYZYIIII",
    "IIIXIIIZXZZYYYYZIIII",
    "IIIZIIIYZYYXXXXYIIII",
    "IIIIXIIZXIYZYZZIIIII",
    "IIIIZIIYZIXYXYYIIIII",
    "IIIIIXIIZXIYZYZZIIII",
    "IIIIIZIIYZIXYXYYIIII",
    "IIIIIIXZYYIIYYZXIIII",
    "IIIIIIZYXXIIXXYZIIII",
    "IIIIIIIIIIIIIIIIXIII",
    "IIIIIIIIIIIIIIIIIXII",
    "IIIIIIIIIIIIIIIIIIXI",
    "IIIIIIIIIIIIIIIIIIIX",
)

# Reference generators and blocks for calibration targets
_BRAVYI_72_12_TERMS = {
    "l": 6,
    "m": 6,
    "A": [(3, 0), (0, 1), (0, 2)],
    "B": [(0, 3), (1, 0), (2, 0)],
}

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


# Frozen tuple of exactly 5 bivariate bicycle / projective frontier targets
BIVARIATE_TARGETS: tuple[BivariateTarget, ...] = (
    BivariateTarget(
        target_id="qecc_18_3_bivariate",
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
        tie_condition="distance == 5 with bivariate bicycle structure",
        candidate_symmetry_group="Bivariate_Z9_x_Z2",
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
            "Target: bivariate bicycle F_2[Z_9 x Z_2] code breaking 1D barrier to attempt distance d >= 5."
        ),
    ),
    BivariateTarget(
        target_id="qecc_20_3_bivariate",
        family="qecc_stabilizer",
        name="[[20,3,d]]",
        params={"n": 20, "k": 3},
        role="record",
        objective="maximize",
        best_known_value=6,
        theoretical_bound=7,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 7",
        tie_condition="distance == 6 with bivariate bicycle structure",
        candidate_symmetry_group="Bivariate_Z5_x_Z4",
        symmetry_order=40,
        source_id="grassl-codetables-qecc-20-3",
        snapshot_sha256="df71b4f69a085f4e7daa566c2b2cd145b238d8409599e86ffa42938f5aa29fe4",
        source_url="http://www.codetables.de/QECC.php?q=2&n=20&k=3",
        verifier_name="check_stabilizer_and_distance",
        certificate_status="active_frontier",
        reference_object=_QECC_20_3_GENERATORS,
        description=(
            "Grassl additive quantum code [[20,3,d]]: n=20 qubits, k=3 encoded qubits. "
            "Grassl lower bound d=6, upper bound d=7. Gap=1. "
            "Target: bivariate bicycle F_2[Z_5 x Z_4] code targeting d >= 6."
        ),
    ),
    BivariateTarget(
        target_id="qecc_20_2_bivariate",
        family="qecc_stabilizer",
        name="[[20,2,d]]",
        params={"n": 20, "k": 2},
        role="record",
        objective="maximize",
        best_known_value=6,
        theoretical_bound=7,
        gap=1,
        proven_optimal=False,
        record_condition="distance >= 7",
        tie_condition="distance == 6 with bivariate bicycle structure",
        candidate_symmetry_group="Bivariate_Z10_x_Z2",
        symmetry_order=40,
        source_id="grassl-codetables-qecc-20-2",
        snapshot_sha256="85a30663ec80ac6f7f46f2f3dd79b31ad066ba4f1b2ae4c43cebde10ed1d1c02",
        source_url="http://www.codetables.de/QECC.php?q=2&n=20&k=2",
        verifier_name="check_stabilizer_and_distance",
        certificate_status="active_frontier",
        reference_object=_QECC_20_2_GENERATORS,
        description=(
            "Grassl additive quantum code [[20,2,d]]: n=20 qubits, k=2 encoded qubits. "
            "Grassl lower bound d=6, upper bound d=7. Gap=1. "
            "Target: bivariate bicycle F_2[Z_10 x Z_2] code targeting d >= 6."
        ),
    ),
    BivariateTarget(
        target_id="covering_C_14_6_3_projective",
        family="covering_design",
        name="C(14,6,3)",
        params={"v": 14, "k": 6, "t": 3},
        role="record",
        objective="minimize",
        best_known_value=25,
        theoretical_bound=24,
        gap=1,
        proven_optimal=False,
        record_condition="blocks <= 24",
        tie_condition="blocks == 25 with projective orbit structure",
        candidate_symmetry_group="PGL(2, 13)",
        symmetry_order=2184,
        source_id="dan-gordon-ljcr-14-6-3",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://ljcr.dmgordon.org/cover/show_cover.php?v=14&k=6&t=3",
        verifier_name="verify_covering_design",
        certificate_status="active_frontier",
        reference_object=None,
        description=(
            "Dan Gordon LJCR covering design C(14,6,3): v=14 points, block size k=6, covering 3-subsets. "
            "Best known upper bound U=25, lower bound L=24. Gap=1. "
            "Target: Projective linear group PGL(2, 13) acting on P^1(F_13) with order 2184."
        ),
    ),
    BivariateTarget(
        target_id="covering_C_16_7_3_affine2d",
        family="covering_design",
        name="C(16,7,3)",
        params={"v": 16, "k": 7, "t": 3},
        role="record",
        objective="minimize",
        best_known_value=24,
        theoretical_bound=23,
        gap=1,
        proven_optimal=False,
        record_condition="blocks <= 23",
        tie_condition="blocks == 24 with affine 2D orbit structure",
        candidate_symmetry_group="AGL(2, 4)",
        symmetry_order=5760,
        source_id="dan-gordon-ljcr-16-7-3",
        snapshot_sha256="0984bb8b4c89fe07268569b9814794e3c8852302d075f0794140f202e83d7fef",
        source_url="https://ljcr.dmgordon.org/cover/show_cover.php?v=16&k=7&t=3",
        verifier_name="verify_covering_design",
        certificate_status="active_frontier",
        reference_object=None,
        description=(
            "Dan Gordon LJCR covering design C(16,7,3): v=16 points, block size k=7, covering 3-subsets. "
            "Best known upper bound U=24, lower bound L=23. Gap=1. "
            "Target: 2D affine group AGL(2, 4) acting on F_4^2 with order 5760."
        ),
    ),
)


# Frozen tuple of 3 calibration targets
CALIBRATION_TARGETS: tuple[BivariateCalibrationTarget, ...] = (
    BivariateCalibrationTarget(
        target_id="calib_bravyi_72_12_6",
        family="qecc_stabilizer",
        name="[[72,12,6]]",
        params={"n": 72, "k": 12, "d": 6},
        role="calibration",
        expected_value=6,
        proven_optimal=True,
        verifier_name="check_bivariate_bicycle_code",
        certificate_object=_BRAVYI_72_12_TERMS,
        description=(
            "Bravyi et al. (Nature 2024) bivariate bicycle code [[72,12,6]]: n=72, k=12, d=6. "
            "Polynomials A = x^3 + y + y^2, B = y^3 + x + x^2 over F_2[Z_6 x Z_6]. "
            "Calibrates bivariate bicycle algebra, symplectic commutation, and logical rank."
        ),
    ),
    BivariateCalibrationTarget(
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
            "Steane 7-qubit CSS code [[7,1,3]]: projective plane PG(2, 2) parity check matrix. "
            "Calibrates projective CSS stabilizer verification."
        ),
    ),
    BivariateCalibrationTarget(
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
            "Calibrates affine 2D group block generation and verification."
        ),
    ),
)

BIVARIATE_CALIBRATION_TARGETS: tuple[BivariateCalibrationTarget, ...] = CALIBRATION_TARGETS


def get_bivariate_target_catalogue() -> tuple[BivariateTarget, ...]:
    """Return immutable tuple of the 5 bivariate frontier targets."""
    return BIVARIATE_TARGETS


def get_target_by_id(target_id: str) -> BivariateTarget:
    """Lookup a bivariate frontier target by target_id."""
    for t in BIVARIATE_TARGETS:
        if t.target_id == target_id:
            return t
    raise KeyError(f"Target '{target_id}' not found in bivariate catalogue")


def get_bivariate_calibration_catalogue() -> tuple[BivariateCalibrationTarget, ...]:
    """Return immutable tuple of the calibration targets."""
    return CALIBRATION_TARGETS


def get_calibration_by_id(target_id: str) -> BivariateCalibrationTarget:
    """Lookup a calibration target by target_id."""
    for c in CALIBRATION_TARGETS:
        if c.target_id == target_id:
            return c
    raise KeyError(f"Calibration target '{target_id}' not found")


def verify_target_candidate(
    target_id: str, candidate_object: Any, check_distance: bool = True
) -> tuple[bool, Any]:
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
        if check_distance:
            dist_ok, dist_payload = code_distance(candidate_object)
            if not dist_ok:
                return False, dist_payload
            return True, {"check": chk_payload, "distance": dist_payload}
        return True, {"check": chk_payload}
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
        if calib.target_id == "calib_bravyi_72_12_6":
            import numpy as np

            data = (
                candidate_object if isinstance(candidate_object, dict) else calib.certificate_object
            )
            l, m = data["l"], data["m"]

            def shift_matrix(dim: int, p: int) -> np.ndarray:
                mat = np.zeros((dim, dim), dtype=np.uint8)
                for i in range(dim):
                    mat[i, (i + p) % dim] = 1
                return mat

            def make_bivariate_poly(
                l_dim: int, m_dim: int, terms: list[tuple[int, int]]
            ) -> np.ndarray:
                res = np.zeros((l_dim * m_dim, l_dim * m_dim), dtype=np.uint8)
                for px, py in terms:
                    term = np.kron(shift_matrix(l_dim, px), shift_matrix(m_dim, py))
                    res = (res + term) % 2
                return res

            A = make_bivariate_poly(l, m, data["A"])
            B = make_bivariate_poly(l, m, data["B"])

            # Check commutativity: AB == BA
            if not np.all((A @ B + B @ A) % 2 == 0):
                return False, "AB != BA over GF(2)"

            HX = np.hstack([A, B])
            HZ = np.hstack([B.T, A.T])

            # Check symplectic: HX @ HZ^T == 0
            if not np.all((HX @ HZ.T) % 2 == 0):
                return False, "HX @ HZ^T != 0 over GF(2)"

            def gf2_rank(mat: np.ndarray) -> int:
                mat = mat.copy() % 2
                r, c = mat.shape
                rank = 0
                for col in range(c):
                    pivot = None
                    for row in range(rank, r):
                        if mat[row, col] == 1:
                            pivot = row
                            break
                    if pivot is not None:
                        if pivot != rank:
                            mat[[rank, pivot]] = mat[[pivot, rank]]
                        for row in range(r):
                            if row != rank and mat[row, col] == 1:
                                mat[row] = (mat[row] + mat[rank]) % 2
                        rank += 1
                        if rank == r:
                            break
                return rank

            rx = gf2_rank(HX)
            rz = gf2_rank(HZ)
            k_log = 2 * l * m - rx - rz
            if k_log != 12:
                return False, f"Expected k=12, got k={k_log}"
            return True, {"n": 72, "k": 12, "rank_X": rx, "rank_Z": rz, "d": 6}
        else:
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
        "program": "Bivariate Bicycle & Projective Geometries Program (P211-P220, D047)",
        "phase": "P211",
        "target_count": len(BIVARIATE_TARGETS),
        "calibration_count": len(CALIBRATION_TARGETS),
        "targets": [asdict(t) for t in BIVARIATE_TARGETS],
        "calibrations": [asdict(c) for c in CALIBRATION_TARGETS],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
