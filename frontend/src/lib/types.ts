// Mirrors .dash/state.json via GET /api/state (see server.py / prepare.save_fit_state).
export interface FitState {
  ready: true
  generated_at: number
  elbo: number | null
  mass_residual: number | null
  mass_gate: boolean
  inference_seconds: number | null
  total0: number
  species: string[]
  hidden: string[]
  grid_times: number[]
  predicted: Record<string, number[]>
  obs_times: number[]
  observed: Record<string, number[]>
  total_mass: number[]
}

export type StateResponse = { ready: false } | FitState

// One results.tsv row via GET /api/ledger. mass columns are absent on the
// ungated branch; elbo is null for crash rows.
export interface LedgerRow {
  iter: number
  commit: string
  elbo: number | null
  mass_residual: number | null
  mass_gate: "PASS" | "FAIL" | null
  status: "keep" | "discard" | "crash" | string
  description: string
}

export interface LedgerResponse {
  rows: LedgerRow[]
}
