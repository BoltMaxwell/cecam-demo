"""Editable experiment surface: the catalysis reaction model + inference.

This is the ONLY file you change during an experiment. Modify only the reaction
network here (species, pathways, stoichiometry). The priors and noise model are
FIXED — do not change them to inflate the ELBO. Never edit `prepare.py`, the
data, or the mass gate.

BASELINE (what ships): a closed five-species network with NO unobserved
intermediate. It conserves mass (passes the gate) but fits poorly, so its
evidence (ELBO) is low. Raising the ELBO without breaking the mass gate is the
whole game.

Run it:

    uv run train.py
"""

from __future__ import annotations

import time

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from jax import lax
from numpyro.infer import SVI, Trace_ELBO
from numpyro.infer.autoguide import AutoNormal

import prepare

numpyro.set_platform("cpu")

# =============================================================================
# Reaction network  --  EDIT THIS BLOCK
# =============================================================================
# List every species the model tracks. Observed species must keep these exact
# names: NO3, NO2, N2, NH3, N2O. You may ADD unobserved species (any new name).
SPECIES = ["NO3", "NO2", "N2", "NH3", "N2O"]

# Initial fraction of each species at t=0 (concentrations are normalised by the
# initial total of 500 mmol/L, so all mass starts as NO3 = 1.0).
Y0 = jnp.array([1.0, 0.0, 0.0, 0.0, 0.0])

# Number of rate constants the network uses.
N_RATES = 4


def rhs(y, t, k):
    """dy/dt = f(y, t, k) for the first-order reaction network.

    Baseline:
        NO3 --k1--> NO2
        NO2 --k2--> N2      (direct; no intermediate)
        NO2 --k4--> NH3
        NO2 --k5--> N2O
    Every term that leaves one species enters another, so total mass is
    conserved by construction.
    """
    NO3, NO2, N2, NH3, N2O = y
    k1, k2, k4, k5 = k
    dNO3 = -k1 * NO3
    dNO2 = k1 * NO3 - (k2 + k4 + k5) * NO2
    dN2 = k2 * NO2
    dNH3 = k4 * NO2
    dN2O = k5 * NO2
    return jnp.array([dNO3, dNO2, dN2, dNH3, dN2O])


# =============================================================================
# End of editable block. Everything below is FIXED — do not edit it.
# =============================================================================

# FIXED prior on each log-rate. Do NOT change LOG_RATE_LOC / LOG_RATE_SCALE (or
# the noise model) to raise the ELBO: tightening a prior shrinks the ELBO's
# penalty term and inflates the score without improving the model, and it makes
# runs incomparable. Only the reaction network above may change.
LOG_RATE_LOC = jnp.log(0.02)
LOG_RATE_SCALE = 1.0

OBS_COLS = jnp.array([SPECIES.index(name) for name in prepare.OBSERVED])
HIDDEN = [name for name in SPECIES if name not in prepare.OBSERVED]

# Fixed RK4 grid over [0, 180]. The seven measured times land exactly on it.
T_FINAL = 180.0
N_STEPS = 360
DT = T_FINAL / N_STEPS


def _grid_index(t):
    return int(round(t / DT))


def integrate_grid(k):
    """Integrate the normalised ODE on the fixed RK4 grid. Returns [N+1, nsp]."""

    def step(c, i):
        t = i * DT
        a = rhs(c, t, k)
        b = rhs(c + 0.5 * DT * a, t + 0.5 * DT, k)
        d = rhs(c + 0.5 * DT * b, t + 0.5 * DT, k)
        e = rhs(c + DT * d, t + DT, k)
        c_next = c + (DT / 6.0) * (a + 2.0 * b + 2.0 * d + e)
        return c_next, c_next

    _, traj = lax.scan(step, Y0, jnp.arange(N_STEPS))
    return jnp.concatenate([Y0[None, :], traj], axis=0)


_DATA = prepare.load()
MEAS_IDX = jnp.array([_grid_index(float(t)) for t in _DATA["times"]])
Y_OBS_NORM = jnp.array(_DATA["obs"] / prepare.TOTAL0)


def numpyro_model(y_obs_norm):
    log_k = numpyro.sample(
        "log_k", dist.Normal(LOG_RATE_LOC * jnp.ones(N_RATES), LOG_RATE_SCALE)
    )
    k = numpyro.deterministic("k", jnp.exp(log_k))
    sigma = numpyro.sample("sigma", dist.HalfNormal(0.1))  # normalised-concentration noise
    pred = integrate_grid(k)[MEAS_IDX][:, OBS_COLS]
    numpyro.sample("y", dist.Normal(pred, sigma), obs=y_obs_norm)


def main():
    start = time.time()
    guide = AutoNormal(numpyro_model)
    svi = SVI(numpyro_model, guide, numpyro.optim.Adam(5e-3), Trace_ELBO())
    result = svi.run(jax.random.PRNGKey(0), 4000, Y_OBS_NORM, progress_bar=False)

    # Stable ELBO estimate (many particles) = approximate log-evidence.
    neg_elbo = Trace_ELBO(num_particles=512).loss(
        jax.random.PRNGKey(1), result.params, numpyro_model, guide, Y_OBS_NORM
    )
    elbo = float(-neg_elbo)

    # Mass gate from posterior-median rates.
    k_hat = jnp.exp(guide.median(result.params)["log_k"])
    traj = np.asarray(integrate_grid(k_hat))
    total_mass = traj[np.asarray(MEAS_IDX)].sum(axis=1) * prepare.TOTAL0

    metrics = {
        "elbo": elbo,
        "mass_residual": prepare.mass_residual(total_mass),
        "mass_gate": prepare.mass_gate(total_mass),
        "num_species": len(SPECIES),
        "hidden_species": ",".join(HIDDEN) if HIDDEN else "none",
        "inference_seconds": round(time.time() - start, 1),
    }
    prepare.print_summary(metrics)


if __name__ == "__main__":
    main()
