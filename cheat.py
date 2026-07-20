"""Ungated 'cheat' demo for the workshop — NOT shipped on main.

Fits the same closed-vessel catalysis data with NO mass gate and a mass-LEAK
network: a sink term lets nitrogen disappear, so the observed species can match
the data's decline and the ELBO rises -- but total mass falls below 500, which
the real harness rejects. Prints the inflated ELBO and mass_gate=FAIL and saves
/tmp/cheat_mass.png.

Run from inside a clone of the harness repo (needs ./catalysis.csv):
    uv run python /tmp/cheat.py
"""
from __future__ import annotations

import pathlib
import time

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from jax import lax
from numpyro.infer import SVI, Trace_ELBO
from numpyro.infer.autoguide import AutoNormal

numpyro.set_platform("cpu")

OBSERVED = ["NO3", "NO2", "N2", "NH3", "N2O"]
TOTAL0 = 500.0
LOG_RATE_LOC = jnp.log(0.02)
LOG_RATE_SCALE = 1.0
N_RATES = 5  # baseline 4 + one leak
T_FINAL, N_STEPS = 180.0, 360
DT = T_FINAL / N_STEPS
Y0 = jnp.array([1.0, 0.0, 0.0, 0.0, 0.0])


def rhs(y, t, k):
    NO3, NO2, N2, NH3, N2O = y
    k1, k2, k4, k5, k6 = k
    dNO3 = -k1 * NO3
    dNO2 = k1 * NO3 - (k2 + k4 + k5 + k6) * NO2   # k6 = leak: mass leaves the system
    dN2 = k2 * NO2
    dNH3 = k4 * NO2
    dN2O = k5 * NO2
    return jnp.array([dNO3, dNO2, dN2, dNH3, dN2O])


def integrate_grid(k):
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


def main():
    raw = np.genfromtxt(pathlib.Path.cwd() / "catalysis.csv", delimiter=",", names=True)
    times = np.asarray(raw["Time"], dtype=float)
    obs = np.stack([np.asarray(raw[n], dtype=float) for n in OBSERVED], axis=1)
    meas_idx = jnp.array([int(round(float(t) / DT)) for t in times])
    y_obs = jnp.array(obs / TOTAL0)

    def model(y):
        log_k = numpyro.sample("log_k", dist.Normal(LOG_RATE_LOC * jnp.ones(N_RATES), LOG_RATE_SCALE))
        k = jnp.exp(log_k)
        sigma = numpyro.sample("sigma", dist.HalfNormal(0.1))
        pred = integrate_grid(k)[meas_idx][:, :5]
        numpyro.sample("y", dist.Normal(pred, sigma), obs=y)

    guide = AutoNormal(model)
    svi = SVI(model, guide, numpyro.optim.Adam(5e-3), Trace_ELBO())
    res = svi.run(jax.random.PRNGKey(0), 4000, y_obs, progress_bar=False)
    elbo = float(-Trace_ELBO(num_particles=512).loss(jax.random.PRNGKey(1), res.params, model, guide, y_obs))
    k_hat = jnp.exp(guide.median(res.params)["log_k"])
    traj = np.asarray(integrate_grid(k_hat))
    total = traj[np.asarray(meas_idx)].sum(axis=1) * TOTAL0
    residual = float(np.max(np.abs(total - TOTAL0)) / TOTAL0)
    gate = residual <= 0.02

    print("--- UNGATED CHEAT ---")
    print(f"elbo: {elbo:.3f}   (honest baseline is ~44.2)")
    print(f"mass_residual: {residual:.4f}   (tolerance 0.02)")
    print(f"mass_gate: {'PASS' if gate else 'FAIL'}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    gt = np.arange(traj.shape[0]) * DT
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(gt, (traj * TOTAL0).sum(axis=1), color="k", label="total modelled mass")
    ax.axhline(TOTAL0, color="tab:red", ls=":", label="target 500 (closed vessel)")
    ax.set_title(f"Cheat: mass leaks away  (ELBO {elbo:.1f}, gate FAIL)")
    ax.set_xlabel("time"); ax.set_ylabel("total mass (mmol/L)"); ax.legend()
    fig.tight_layout(); fig.savefig("/tmp/cheat_mass.png", dpi=110)
    print("saved /tmp/cheat_mass.png")


if __name__ == "__main__":
    main()
