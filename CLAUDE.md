# Catalysis Kinetic Model Search

You are a computational scientist searching for the kinetic model with the
highest evidence (ELBO) for a closed catalysis experiment. Follow this file.

## Files

- `prepare.py` — fixed. Never edit (it owns the data and computes the score).
- `train.py` — you may change anything here: the reaction network, the priors,
  and the noise model.
- `results.tsv` — the experiment ledger; one row per run.
- `MEMORY.md`, `TODO.md` — durable notes and the running list of ideas.

## Objective

Maximise the ELBO printed by `train.py`. Keep any change that raises it.

## How models are compared (evidence odds)

`train.py` reports an `elbo`. For a proposed model vs the current best,

    odds = exp(elbo_proposed - elbo_best)

- `odds > 1`  → accept (keep it).
- `odds <= 1` → reject (revert to the previous best).

## Running the model

    uv sync                          # once, creates the local environment
    uv run train.py > run.log 2>&1
    grep "^elbo:" run.log

Each run also writes a fit plot to `.dash/fit.png` (used by the optional
dashboard).

## Setup

1. Create a branch `run/<tag>` (tag = today's date) from the current state.
2. Read `prepare.py` and `train.py`.
3. Confirm `results.tsv` has only its header row.
4. Run the current model once and log it to `results.tsv` as the first row; its
   ELBO is the current best to beat.

## Experiment loop

Run a fixed budget of up to 8 iterations (stop early if two successive
iterations fail to beat the best):

1. Make ONE change to `train.py` — the reaction network, the priors, or the
   noise model, whatever you think will raise the ELBO. Commit it.
2. Run `uv run train.py > run.log 2>&1`.
3. Read `grep "^elbo:" run.log`. If there is no summary block, the run crashed —
   read `tail -n 40 run.log`, then fix or revert.
4. Compute `odds = exp(elbo_proposed - elbo_best)`; if `odds > 1` → accept (this
   run is the new best), else reject and revert.
5. Append a row to `results.tsv` with the columns of its header row.
6. Update `MEMORY.md` and `TODO.md`, then continue.

**Timeout:** kill any run over 5 minutes and treat it as a crash.

## Relay note

If resumed, read `MEMORY.md` and `results.tsv`, check out the best kept commit,
and continue from there — do not restart from the baseline.
