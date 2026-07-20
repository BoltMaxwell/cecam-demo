# TODO / Ideas queue

Loop stopped early after 6 iterations (two successive discards). Best kept
model: commit 4318e24, elbo=67.26305. Ideas for a future session, if resumed:

1. Untested variants of the NO branch point: e.g. NH3 sourced from NO2 in
   *addition to* NO (two sources), or non-first-order kinetics for one edge.
2. A hidden pool other than NOH in series (e.g. branching before NO2 itself,
   between NO3 and NO2) — not yet tried.
3. Any change must still route every outflow into a tracked species (mass
   conservation is structural, not fit) and must not touch
   LOG_RATE_LOC/LOG_RATE_SCALE or the sigma prior.
