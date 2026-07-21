import { useEffect, useState } from "react"
import type { LedgerResponse, StateResponse } from "@/lib/types"

const POLL_MS = 4000

export interface LiveData {
  state: StateResponse | null   // null until the first successful poll
  ledger: LedgerResponse | null
  error: boolean                // last poll failed; previous data is retained
  updatedAt: number | null      // ms epoch of the last successful poll
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`)
  return res.json() as Promise<T>
}

export function useLiveData(): LiveData {
  const [data, setData] = useState<LiveData>({
    state: null, ledger: null, error: false, updatedAt: null,
  })

  useEffect(() => {
    let alive = true
    const tick = async () => {
      try {
        const [state, ledger] = await Promise.all([
          getJson<StateResponse>("/api/state"),
          getJson<LedgerResponse>("/api/ledger"),
        ])
        if (alive) setData({ state, ledger, error: false, updatedAt: Date.now() })
      } catch {
        if (alive) setData((d) => ({ ...d, error: true }))
      }
    }
    tick()
    const id = setInterval(tick, POLL_MS)
    return () => { alive = false; clearInterval(id) }
  }, [])

  return data
}
