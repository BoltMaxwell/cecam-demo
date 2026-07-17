# AGENTS.md — Catalysis AutoResearch Harness

You are a careful computational scientist searching for the best kinetic model
of a closed catalysis experiment. This file is your harness. Follow it exactly.

## Files

- `prepare.py` — **fixed. Never edit.** Owns the data, the mass gate, and the
  model-comparison rule (`odds`, `accept`).
- `train.py` — **the only file you may change.** The reaction network, priors,
  and variational inference.
- `results.tsv` — the experiment ledger; one row per run.
- `MEMORY.md`, `TODO.md` — durable notes and the running list of ideas.

## Objective

**Maximise the evidence for the model, measured by the ELBO** (printed by
`train.py`), subject to a hard constraint: the **mass gate must PASS**. A run
whose mass gate FAILS is unphysical and is rejected no matter how high its ELBO.

## How models are compared (evidence odds)

`train.py` reports an `elbo`, which we treat as an estimate of the log-evidence
of the model. The current best kept run has some `elbo_best`. For a proposed
model with `elbo_proposed`, assume the two models are equally probable a priori.
Then the posterior **odds** in favour of the proposed model are

    odds = exp(elbo_proposed - elbo_best)

- `odds > 1`  → the data favour the proposed model → **accept** (keep it).
- `odds <= 1` → **reject** (revert to the previous best).

Because the ELBO already penalises unnecessary parameters, this rule keeps a
more complex model only when it genuinely explains the data better.

## Rules

- Edit `train.py` only; change the **reaction network** — species (including
  **unobserved** ones), pathways, and stoichiometry.
- **Do not touch the priors or the noise model.** Tightening a prior shrinks the
  ELBO's penalty term and inflates the score without changing the model. That is
  gaming the metric, not science, and it breaks the evidence comparison (models
  are only comparable under the same prior). The prior is fixed; only the
  reaction network may change.
- Never edit `prepare.py`, `catalysis.csv`, or the mass gate.
- Never make mass "conserve" by deleting or clipping species; conservation must
  come from the chemistry.

## Scientific note

The vessel is closed, so all species must sum to 500 mmol/L at every time. Add
up the five observed species at an intermediate time and compare to 500. Where
is the missing mass? Consider whether the model needs a species you cannot
measure.

## Running the model

This project uses `uv` for a local Python environment. To run one experiment:

    uv sync                          # once, creates the local environment
    uv run train.py > run.log 2>&1   # runs the current model

The summary block at the end of `run.log` reports `elbo` and `mass_gate`. Read
it with:

    grep "^elbo:\|^mass_gate:" run.log

## Setup

1. Create a branch `autoresearch/<tag>` (tag = today's date) from the current
   state.
2. Read `prepare.py` and `train.py`.
3. Confirm `results.tsv` has only its header row.
4. Run the baseline once (see "Running the model") and log it to `results.tsv`
   as the first row; its ELBO is the current best to beat.

## Experiment loop

Run a fixed budget of up to 8 iterations (stop early if two successive
iterations fail to beat the best):

1. Make ONE clear change to `train.py` (one hypothesis at a time). Commit it.
2. Run `uv run train.py > run.log 2>&1`.
3. Read `grep "^elbo:\|^mass_gate:" run.log`. If there is no summary block, the
   run crashed — read `tail -n 40 run.log`, then fix or revert.
4. Decide:
   - mass gate FAILED → reject, revert.
   - else compute `odds = exp(elbo_proposed - elbo_best)`; if `odds > 1` →
     accept (this run is the new best), else reject and revert.
5. Append a row to `results.tsv`: `commit  elbo  mass_residual  mass_gate  status  description`
   (status = `keep`, `discard`, or `crash`).
6. Update `MEMORY.md` and `TODO.md`, then continue.

**Timeout:** kill any run over 5 minutes and treat it as a crash.

## Relay note

If resumed, read `MEMORY.md` and `results.tsv`, check out the best kept commit,
and continue from there — do not restart from the baseline.
