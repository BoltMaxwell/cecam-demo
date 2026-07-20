# AutoResearch Memory

## FINAL best: commit 4318e24, elbo_best = 67.26305 (PASS) — checked out on this branch

Network: `NO3 -k1-> NO2`, `NO2 -k2-> NO(hidden)`, then NO branches three ways
in parallel: `NO -k4-> NH3`, `NO -k5-> N2`, `NO -k6-> N2O`. N_RATES=5.

## Full history

| commit  | elbo     | mass_gate | status  | change |
|---------|----------|-----------|---------|--------|
| 2946bce | 44.15623 | PASS      | keep    | baseline: NO3->NO2->{N2,NH3,N2O} direct, no hidden species |
| ed75586 | 52.44389 | PASS      | keep    | + hidden NO intermediate, series NO2->NO->N2O->N2 |
| ab680ff | 66.87736 | PASS      | keep    | NO branches in parallel to N2 and N2O (drop N2O->N2) |
| 54cec6f | 63.75864 | PASS      | discard | hybrid: add N2O->N2 back onto parallel NO; odds=0.044 |
| 4318e24 | 67.26305 | PASS      | keep    | NH3 moved from NO2 branch to NO branch; odds=1.47 — **FINAL BEST** |
| 2569a8f | 63.70810 | PASS      | discard | add direct NO2->N2 shortcut bypassing NO; odds=0.029 |
| 565c0fc | 66.35847 | PASS      | discard | second hidden species NOH in series before NO; odds=0.40 |

Stopped after 6 iterations: two successive discards (2569a8f, 565c0fc) per the
harness's early-stop rule. `train.py` on this branch is checked out at the
4318e24 network (verified via `git checkout 4318e24 -- train.py`).

## Scientific finding

The vessel's apparent missing mass (up to ~28% at t=60, summing only the 5
observed species) is fully explained by a single unobserved intermediate:
nitric oxide (NO), sitting between NO2 and the three end products. The
best-supported topology has NO2 reduced to hidden NO, which then splits three
ways in parallel to N2, NH3, and N2O — i.e. NO is a true branch point, not a
step in a longer chain. Both tested elaborations of this topology (routing
N2O back into N2, giving NO2 a direct shortcut to N2, or inserting a second
hidden species upstream of NO) reduced the evidence — the data support exactly
one hidden species and exactly three outgoing edges from it, no more.

## Rules reminder

- Only `train.py`'s `SPECIES`, `Y0`, `N_RATES`, `rhs()` may change.
- Priors (`LOG_RATE_LOC`, `LOG_RATE_SCALE`) and noise model (`sigma` prior) are
  fixed — never touch them.
- `odds = exp(elbo_proposed - elbo_best)`; accept iff `odds > 1`.
