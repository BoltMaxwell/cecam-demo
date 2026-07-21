import {
  CartesianGrid, ComposedChart, Line, ReferenceArea, ReferenceLine, XAxis, YAxis,
} from "recharts"
import {
  ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig,
} from "@/components/ui/chart"
import { STATUS } from "@/lib/palette"
import type { FitState } from "@/lib/types"

export function MassChart({ state }: { state: FitState }) {
  const config = {
    total: { label: "total mass", color: STATUS.neutral },
  } satisfies ChartConfig
  const rows = state.grid_times.map((t, i) => ({ t, total: state.total_mass[i] }))
  const t0 = state.total0
  const tMax = state.grid_times[state.grid_times.length - 1]

  return (
    <ChartContainer config={config} className="aspect-[4/1] w-full">
      <ComposedChart data={rows} margin={{ top: 4, right: 8 }}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey="t" type="number" domain={[0, tMax]} tickCount={7} />
        <YAxis width={48} domain={[t0 * 0.9, t0 * 1.1]} tickCount={3} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ReferenceArea
          y1={t0 * 0.98} y2={t0 * 1.02}
          fill="var(--muted)" fillOpacity={0.5}
          label={{ value: "gate ±2%", position: "insideTopRight", fontSize: 11 }}
        />
        <ReferenceLine y={t0} stroke={STATUS.neutral} strokeDasharray="4 4" />
        <Line
          dataKey="total" dot={false} strokeWidth={2} isAnimationActive={false}
          stroke={state.mass_gate ? "var(--foreground)" : STATUS.critical}
        />
      </ComposedChart>
    </ChartContainer>
  )
}
