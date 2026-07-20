# Sample AutoResearch run (reference only)

A real, unedited run of this harness on the finished repo, driven by a coding
agent (Claude **Sonnet**). It lives on the `extras` branch, **not on `main`** —
so a participant's agent (which clones `main`) never sees the answer.

## What happened

The agent was told only: *maximise the ELBO, mass gate must pass.* With no hint
about the missing mass, it discovered a single unobserved intermediate —
**NO (nitric oxide)** — and raised the evidence from the baseline to a
well-supported model:

- **ELBO 44.16 → 67.26**, mass gate **PASS** at every step (residuals ~1e-7).
- Final network (6 species, mass-conserving by construction):
  `NO3 → NO2 → NO(hidden) → {N2, NH3, N2O}` (NO branches three ways).
- 6 hypotheses tried: **4 kept, 3 discarded** by the evidence-odds rule.
  It even tested a *second* hidden species and correctly rejected it
  (odds 0.40 < 1) — the data support exactly one.

This matches real denitrification chemistry (NO₃→NO₂→NO→N₂O/N₂).

## It did not cheat (audited)

- `prepare.py` (gate + benchmark): untouched.
- Priors and noise model: untouched — no metric-gaming.
- Only the reaction-network block of `train.py` was edited; the fixed section is
  byte-identical to baseline.
- Every accept/reject in the ledger matches `odds = exp(elbo - elbo_best) > 1`.

## Files

- `results.tsv` — the experiment ledger (one row per run).
- `progress.png` — ELBO trajectory (green = kept, red = discarded).
- `MEMORY.md` / `TODO.md` — the agent's own durable notes and reasoning.
- `train.py` — the final winning network (the hidden-NO model).

## Note

Different agents/models reach different valid answers: an earlier Fable run found
*two* justified hidden species (ELBO ~72). Same data, both honest — there is no
single "right" answer, only models the evidence supports.
