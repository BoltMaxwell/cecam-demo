import { Badge } from "@/components/ui/badge"
import { STATUS } from "@/lib/palette"
import type { FitState } from "@/lib/types"

export function MetricBar({ state }: { state: FitState }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="secondary" className="font-mono text-sm">
        ELBO {state.elbo?.toFixed(2) ?? "—"}
      </Badge>
      <Badge
        style={{ background: state.mass_gate ? STATUS.good : STATUS.critical }}
        className="text-white"
      >
        {state.mass_gate ? "✓ mass gate PASS" : "✗ mass gate FAIL"}
      </Badge>
      <Badge variant="outline">{state.species.length} species</Badge>
      <Badge variant="outline">
        hidden: {state.hidden.length ? state.hidden.join(", ") : "none"}
      </Badge>
      <Badge variant="outline">
        inference {state.inference_seconds?.toFixed(1) ?? "—"}s
      </Badge>
    </div>
  )
}
