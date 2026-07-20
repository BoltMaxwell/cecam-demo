"""Fixed benchmark for the catalysis AutoResearch activity.

DO NOT EDIT during experiments. This file owns the dataset, the mass-conservation
gate, and the evidence-based model-comparison rule. The reaction model and the
inference live in `train.py`, the only file an experiment may change.
"""

from __future__ import annotations

import html
import math
import os
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


# =============================================================================
# Dashboard rendering (FIXED). Used by train.py (fit plot) and dashboard.py.
# These are display-only helpers; they never affect the gate or the ledger.
# =============================================================================
DASH_DIR = HERE / ".dash"


def _atomic_savefig(fig, path):
    import matplotlib.pyplot as plt
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fig.savefig(tmp, dpi=110, format="png")
    plt.close(fig)
    os.replace(tmp, path)


def _read_ledger(results_tsv):
    """Parse results.tsv into a list of dict rows (elbo coerced to float)."""
    p = pathlib.Path(results_tsv)
    if not p.exists():
        return []
    lines = [ln for ln in p.read_text().splitlines() if ln.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        row = dict(zip(header, line.split("\t")))
        try:
            row["elbo"] = float(row.get("elbo", "nan"))
        except ValueError:
            row["elbo"] = float("nan")
        rows.append(row)
    return rows


def save_fit_plot(species, traj_grid, dt, metrics, path):
    """Render the current model: species curves vs observed data + total mass.

    traj_grid: [G, nsp] normalised trajectory on the fixed grid. Observed species
    are solid, hidden species dashed. `metrics` provides elbo and mass_gate (bool).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = load()
    times, obs = data["times"], data["obs"]
    traj = np.asarray(traj_grid) * TOTAL0
    gt = np.arange(traj.shape[0]) * dt
    colors = plt.cm.tab10.colors

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7),
                                   gridspec_kw={"height_ratios": [3, 1]})
    for j, name in enumerate(species):
        hidden = name not in OBSERVED
        ax1.plot(gt, traj[:, j], color=colors[j % 10],
                 ls="--" if hidden else "-",
                 label=name + (" (hidden)" if hidden else ""))
    for k, name in enumerate(OBSERVED):
        ax1.scatter(times, obs[:, k], s=30, zorder=5, edgecolor="k",
                    linewidth=0.4, color=colors[species.index(name) % 10])
    gate = "PASS" if metrics.get("mass_gate") else "FAIL"
    ax1.set_ylabel("concentration (mmol/L)")
    ax1.set_title(f"Model fit — ELBO={metrics.get('elbo', float('nan')):.2f}"
                  f"  |  mass gate {gate}")
    ax1.legend(fontsize=8, ncol=2, loc="upper right")

    ax2.plot(gt, traj.sum(axis=1), color="k")
    ax2.axhline(TOTAL0, color="tab:red", ls=":", label=f"target {TOTAL0:.0f}")
    ax2.set_ylabel("total mass"); ax2.set_xlabel("time")
    ax2.legend(fontsize=8, loc="lower left")

    fig.tight_layout()
    _atomic_savefig(fig, path)


def save_progress_plot(results_tsv, path):
    """ELBO vs iteration from the ledger; green o = keep, red x = discard."""
    rows = _read_ledger(results_tsv)
    if not rows:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 3.2))
    elbos = [r["elbo"] for r in rows]
    ax.plot(range(len(rows)), elbos, color="0.6", lw=1, zorder=1)
    for x, r in enumerate(rows):
        keep = r.get("status") == "keep"
        ax.scatter(x, r["elbo"], s=60, zorder=3,
                   marker="o" if keep else "x",
                   color="tab:green" if keep else "tab:red")
        if r.get("mass_gate") != "PASS":
            ax.annotate("mass FAIL", (x, r["elbo"]), fontsize=7, color="tab:red",
                        textcoords="offset points", xytext=(0, 6))
    ax.axhline(elbos[0], color="0.8", ls=":", label="baseline")
    ax.legend(fontsize=8)
    ax.set_xlabel("iteration"); ax.set_ylabel("ELBO")
    ax.set_title("AutoResearch progress")
    fig.tight_layout()
    _atomic_savefig(fig, path)


def results_table_html(results_tsv):
    """Return an HTML table for the ledger, or a placeholder if empty."""
    p = pathlib.Path(results_tsv)
    if not p.exists():
        return "<p>No runs logged yet.</p>"
    lines = [ln for ln in p.read_text().splitlines() if ln.strip()]
    if len(lines) < 2:
        return "<p>No runs logged yet.</p>"
    header = lines[0].split("\t")
    out = ["<table border='1' cellpadding='4' cellspacing='0'><tr>"]
    out += [f"<th>{html.escape(h)}</th>" for h in header]
    out.append("</tr>")
    for line in lines[1:]:
        out.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in line.split("\t")) + "</tr>")
    out.append("</table>")
    return "\n".join(out)
