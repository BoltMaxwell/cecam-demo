import json

import numpy as np
import pytest

import prepare


def _traj(G, nsp):
    return np.linspace(1.0, 0.0, G)[:, None] * np.ones((1, nsp)) / nsp


METRICS = {"elbo": 50.0, "mass_residual": 2.4e-7, "mass_gate": True,
           "inference_seconds": 3.9}


def test_save_fit_state_shape(tmp_path):
    species = ["NO3", "NO2", "N2", "NH3", "N2O", "X"]
    out = tmp_path / "state.json"
    prepare.save_fit_state(species, _traj(361, 6), 0.5, METRICS, out)
    state = json.loads(out.read_text())
    assert state["species"] == species
    assert state["hidden"] == ["X"]
    assert state["total0"] == prepare.TOTAL0
    assert len(state["grid_times"]) == 361 == len(state["predicted"]["X"])
    assert state["grid_times"][1] == 0.5
    assert len(state["obs_times"]) == len(state["observed"]["NO3"])
    assert len(state["total_mass"]) == 361
    assert state["mass_gate"] is True
    assert state["generated_at"] > 0
    # atomic write leaves no temp file behind
    assert list(tmp_path.iterdir()) == [out]


def test_save_fit_state_non_finite_metric_becomes_null(tmp_path):
    out = tmp_path / "state.json"
    prepare.save_fit_state(["NO3", "NO2", "N2", "NH3", "N2O"], _traj(11, 5), 0.5,
                           {**METRICS, "elbo": float("nan")}, out)
    assert json.loads(out.read_text())["elbo"] is None


def test_save_fit_state_rejects_nan_trajectory(tmp_path):
    traj = _traj(11, 5)
    traj[3, 2] = float("nan")
    with pytest.raises(ValueError):
        prepare.save_fit_state(["NO3", "NO2", "N2", "NH3", "N2O"], traj, 0.5,
                               METRICS, tmp_path / "state.json")
