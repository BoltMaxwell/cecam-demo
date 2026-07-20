# CECAM demo — an AutoResearch harness that forces an honest model

A tiny, self-contained harness for calibrating a kinetic model of a **closed**
catalysis experiment. All nitrogen starts as NO3 at 500 mmol/L, yet the five
**observed** species sum to *less than* 500 at intermediate times. The missing
mass is the whole puzzle — and the reason a harness matters.

## What you need (from the earlier activities)

- A coding agent: **Codex** (uses `AGENTS.md`) or **Claude** (uses `CLAUDE.md`).
- A paid agent/API plan for that agent.
- [`uv`](https://docs.astral.sh/uv/) installed.
- No local setup? Use the Colab fallback: **[Open in Colab](https://colab.research.google.com/github/BoltMaxwell/cecam-demo/blob/main/colab/cecam_demo.ipynb)**.

## 1. Get the repo and confirm the baseline

```bash
git clone https://github.com/BoltMaxwell/cecam-demo.git
cd cecam-demo
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

## Watch it live (optional dashboard)

In a **second terminal**, start the dashboard and open it in a browser:

```bash
uv run dashboard.py      # then open http://localhost:8000
```

It refreshes every 2 seconds and shows two things as the agent works:

- **Current model fit** — the species concentration curves vs. the measured
  data, plus total mass against the 500 mmol/L target. When the agent adds an
  unobserved species you'll see a new dashed curve appear.
- **AutoResearch progress** — the ELBO at each iteration (green = kept,
  red = discarded) and the full `results.tsv` ledger.

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

## Optional: see what "cheating" looks like

Curious what an *ungated* agent does? This one-liner pulls a throwaway script
(kept off this branch on purpose, so your agent never sees it) and runs it from
`/tmp`:

```bash
curl -s https://raw.githubusercontent.com/BoltMaxwell/cecam-demo/extras/cheat.py -o /tmp/cheat.py && uv run python /tmp/cheat.py
```

It fits the same data with a mass **leak** — the ELBO goes *up* while total mass
falls below 500, so `mass_gate: FAIL`. It saves `/tmp/cheat_mass.png` showing the
mass draining away. That's exactly the shortcut the harness exists to reject.
