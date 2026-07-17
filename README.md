# CECAM demo — an AutoResearch harness that forces an honest model

A tiny, self-contained harness for calibrating a kinetic model of a **closed**
catalysis experiment. All nitrogen starts as NO3 at 500 mmol/L, yet the five
**observed** species sum to *less than* 500 at intermediate times. The missing
mass is the whole puzzle — and the reason a harness matters.

## What you need (from the earlier activities)

- A coding agent: **Codex** (uses `AGENTS.md`) or **Claude** (uses `CLAUDE.md`).
- A paid agent/API plan for that agent.
- [`uv`](https://docs.astral.sh/uv/) installed.
- No local setup? Use the Colab fallback: **[Open in Colab](colab/cecam_demo.ipynb)**.

## 1. Get the repo and confirm the baseline

```bash
git clone https://github.com/<your-org>/cecam_demo.git
cd cecam_demo
uv sync
uv run train.py | grep '^elbo:\|^mass_gate:'
```

You should see `mass_gate: PASS` and `elbo:` around 44. This is the closed
five-species baseline: it conserves mass but fits poorly.

## 2. Point your agent at the harness

Open the repo in Codex or Claude (so it reads `AGENTS.md` / `CLAUDE.md`), then
paste this **exact** prompt:

```text
Read AGENTS.md and follow it exactly. Your objective is to maximise the ELBO
reported by train.py, subject to the mass gate passing. Run the experiment loop
for up to 8 iterations, logging every run to results.tsv. Do not edit prepare.py,
the data, the priors, or the noise model — only the reaction network in train.py.
```

## 3. Watch the ledger

While the agent works (~10 minutes), watch the experiment ledger fill in:

```bash
# re-run this to see new rows as the agent logs them:
cat results.tsv
# optional live view (Linux, or macOS with Homebrew `watch`+`column`):
#   watch -n 5 column -t -s $'\t' results.tsv
```

You will see rows rejected — `mass_gate FAIL`, or `odds <= 1` — until the agent
realises the only honest way to raise the ELBO is to **add an unobserved
intermediate species** that carries the missing mass. That run passes the gate
*and* beats the evidence, and is kept.

## Why this is the point

Before the workshop we ran the same task **without** the harness (see
[`cheat-reveal/`](cheat-reveal/)). Free to "just maximise the ELBO," the agent
raised the score by letting mass leak away — a great fit to unphysical chemistry.
The harness is the only reason the science comes out honest.
