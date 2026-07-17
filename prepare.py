"""Fixed benchmark for the catalysis AutoResearch activity.

DO NOT EDIT during experiments. This file owns the dataset, the mass-conservation
gate, and the evidence-based model-comparison rule. The reaction model and the
inference live in `train.py`, the only file an experiment may change.
"""

from __future__ import annotations

import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
DATA_PATH = HERE / "catalysis.csv"

# The five measured species (column order). Concentrations are in mmol/L.
OBSERVED = ["NO3", "NO2", "N2", "NH3", "N2O"]

# All nitrogen starts as NO3. The vessel is closed, so a valid model conserves
# this total for all time.
TOTAL0 = 500.0

# Hard gate: if the total modelled mass drifts from TOTAL0 by more than this
# relative tolerance at any measured time, the model is unphysical and rejected.
MASS_TOL = 0.02

SUMMARY_FIELDS = [
    "elbo",
    "mass_residual",
    "mass_gate",
    "num_species",
    "hidden_species",
    "inference_seconds",
]

RESULTS_HEADER = "commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription"


def load():
    """Return the measured `times` [T] and observed concentrations `obs` [T, 5]."""
    raw = np.genfromtxt(DATA_PATH, delimiter=",", names=True)
    times = np.asarray(raw["Time"], dtype=float)
    obs = np.stack([np.asarray(raw[name], dtype=float) for name in OBSERVED], axis=1)
    return {"times": times, "obs": obs}


def mass_residual(total_over_time):
    """Largest relative deviation of total modelled mass from TOTAL0."""
    total = np.asarray(total_over_time, dtype=float)
    return float(np.max(np.abs(total - TOTAL0)) / TOTAL0)


def mass_gate(total_over_time):
    """True if the model conserves mass within MASS_TOL at every measured time."""
    return mass_residual(total_over_time) <= MASS_TOL


def odds(elbo_proposed, elbo_best):
    """Posterior odds in favour of the proposed model over the current best.

    We treat exp(ELBO) as a stand-in for the model evidence and assume the two
    models are equally probable a priori. With equal priors the posterior odds
    equal the evidence ratio, exp(ELBO_proposed - ELBO_best). Odds > 1 means the
    data favour the proposed model.
    """
    diff = float(elbo_proposed) - float(elbo_best)
    try:
        return math.exp(diff)
    except OverflowError:
        return float("inf")


def accept(elbo_proposed, elbo_best):
    """Accept the proposed model iff the evidence odds exceed 1."""
    return odds(elbo_proposed, elbo_best) > 1.0


def print_summary(metrics):
    """Print the fixed-format summary block the loop greps for."""
    lines = ["---"]
    for field in SUMMARY_FIELDS:
        value = metrics[field]
        if field == "mass_gate":
            value = "PASS" if value else "FAIL"
        elif isinstance(value, float):
            value = f"{value:.6e}"
        lines.append(f"{field}: {value}")
    lines.append("---")
    print("\n".join(lines))
