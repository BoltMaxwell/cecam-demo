# Catalysis kinetic fit — no harness

The bare version: just the data and a task. There is **no harness** here — no
mass-conservation gate, no evidence-odds loop, no ledger, no fixed benchmark, no
`AGENTS.md`. You hand a coding agent the dataset and a thin prompt and see what it
does when nothing keeps it honest or reproducible. Compare it with the harnessed
version on [`main`](https://github.com/BoltMaxwell/cecam-demo).

## Run it

Clone this branch and open the folder in your coding agent (Codex or Claude):

```bash
git clone -b no-harness https://github.com/BoltMaxwell/cecam-demo.git cecam-no-harness
cd cecam-no-harness
uv sync
```

Then paste this prompt:

```text
I have a catalysis dataset in catalysis.csv: five species (NO3, NO2, N2, NH3,
N2O) in mmol/L measured over time, all starting as 500 mmol/L of NO3. Fit a
kinetic reaction model to the data as well as you can. Report the reaction
network and the fitted rate constants, and make a plot of your best model's
predicted concentration curves over time with the measured data points
overlaid — save it as fit.png.
```

## What to watch for

There is no harness, so nothing enforces discipline or honesty. As the agent works:

- **Does it stay physical?** The five observed species sum to *less than* 500 at
  intermediate times — some mass is temporarily held in a species the experiment
  never measured. Does the agent notice, and introduce that unobserved
  intermediate? Or does it "fit the data" with a model that quietly leaks or
  manufactures mass?
- **Can you trust it?** Could you rerun its result and get the same thing? Is
  there any record of what it tried — or just a final answer?
- **You still get a picture.** The prompt asks for `fit.png`, so you get a visual
  of the fit — but you had to ask, and there is no ledger of how it got there.

Then open the harnessed version on `main`: the mass gate forces honesty, the
evidence ratchet keeps only real improvements, and every trial is logged as a row
in `results.tsv` and a Git commit — a reproducible record you can watch live on
the dashboard. That difference is what the harness buys you.
