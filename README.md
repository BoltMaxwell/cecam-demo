# Catalysis kinetic model search (ungated variant)

A looser variant of the AutoResearch harness on `main`. It keeps the same
evidence-odds loop and ledger, but the agent may change **anything** in
`train.py` — the reaction network, the priors, and the noise model — to maximise
the ELBO. See the full harness on
[`main`](https://github.com/BoltMaxwell/cecam-demo) and the bare version on
[`no-harness`](https://github.com/BoltMaxwell/cecam-demo/tree/no-harness).

## Run it

```bash
git clone -b ungated https://github.com/BoltMaxwell/cecam-demo.git cecam-ungated
cd cecam-ungated
uv sync
```

Open the folder in Codex or Claude (so it reads `AGENTS.md` / `CLAUDE.md`) and
paste this prompt:

```text
Read AGENTS.md and follow it exactly. Maximise the ELBO printed by train.py.
Run the experiment loop for up to 8 iterations, logging every run to results.tsv.
```

## Watch it live (optional dashboard)

In a second terminal, start the dashboard to watch the current model fit and the
ELBO progress update as the search runs:

```bash
uv run dashboard.py      # then open http://localhost:8000
```
