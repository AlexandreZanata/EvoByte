"""P165 guard tests: blind rediscovery calibration protocol."""

from __future__ import annotations

import numpy as np

from evobyte.rediscovery import (
    RediscoveryTrial,
    make_vdw_evaluator,
    run_single_calibration_trial,
)
from evobyte.target_catalogue import verify_vanderwaerden_coloring

# A valid 3-coloring of [1..26] with no monochromatic 3-term AP, i.e. a
# certificate that W(3,3) >= 27. Independently confirmed by the P163 oracle and
# by an exhaustive backtracking search (no valid coloring of [1..27] exists).
KNOWN_W_3_3_CERTIFICATE = np.array(
    [1, 1, 2, 2, 1, 1, 2, 3, 2, 3, 3, 1, 3, 1, 1, 2, 1, 2, 2, 3, 1, 3, 3, 2, 3, 2],
    dtype=int,
)


def test_make_vdw_evaluator_validates_known_optimum():
    assert verify_vanderwaerden_coloring(KNOWN_W_3_3_CERTIFICATE, r=3, k=3)[0] is True
    _, _, _, eval_fn = make_vdw_evaluator(n=26, r=3, k=3)
    score, solved = eval_fn(KNOWN_W_3_3_CERTIFICATE)
    assert score == 0.0
    assert solved is True


def test_single_calibration_trial_random():
    trial = run_single_calibration_trial("vdw_3_3_26", "RandomSearch", 0.1, 42)
    assert isinstance(trial, RediscoveryTrial)
    assert trial.instance_id == "vdw_3_3_26"
    assert trial.method == "RandomSearch"
    assert trial.seed == 42
    assert isinstance(trial.success, bool)
    assert trial.total_evals >= 0
    assert trial.elapsed_sec >= 0.0
    assert trial.time_to_hit_sec is None or trial.success


def test_single_calibration_trial_sa():
    trial = run_single_calibration_trial("vdw_3_3_26", "SimulatedAnnealing", 0.1, 42)
    assert isinstance(trial, RediscoveryTrial)
    assert trial.method == "SimulatedAnnealing"
    assert trial.total_evals > 0
    assert trial.elapsed_sec >= 0.0
