import {
  CartesianGrid, ComposedChart, Line, Scatter, XAxis, YAxis,
} from "recharts"
import {
  ChartContainer, ChartLegend, ChartLegendContent, ChartTooltip, ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { speciesTheme } from "@/lib/palette"
import type { FitState } from "@/lib/types"

export function FitChart({ state }: { state: FitState }) {
  const config = Object.fromEntries(
    state.species.map((s) => [s, {
      label: state.hidden.includes(s) ? `${s} (hidden)` : s,
      theme: speciesTheme(s, state.species),
    }]),
  ) satisfies ChartConfig

  const tMax = state.grid_times[state.grid_times.length - 1]
  const dt = state.grid_times.length > 1
    ? state.grid_times[1] - state.grid_times[0]
    : 1
  const observedSpecies = state.species.filter((s) => s in state.observed)

  // One data array: predicted lines on the full grid, with the measured points
  // merged into the SAME rows at each measurement's grid index (the seven
  // measured times land exactly on the RK4 grid by construction). The
  // observation scatters therefore share the exact numeric x-axis as the lines,
  // with no second data array to reconcile — robust across Recharts versions.
  const rows: Record<string, number>[] = state.grid_times.map((t, i) => {
    const row: Record<string, number> = { t }
    for (const s of state.species) row[s] = state.predicted[s][i]
    return row
  })
  state.obs_times.forEach((ot, oi) => {
    const gi = Math.round(ot / dt)
    if (gi >= 0 && gi < rows.length) {
      for (const s of observedSpecies) rows[gi][`${s}__obs`] = state.observed[s][oi]
    }
  })

  return (
    <ChartContainer config={config} className="aspect-[2/1] w-full">
      <ComposedChart data={rows} margin={{ top: 8, right: 8 }}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="t" type="number" domain={[0, tMax]} tickCount={7}
          label={{ value: "time", position: "insideBottomRight", offset: -4 }}
        />
        <YAxis
          width={48}
          label={{ value: "mmol/L", angle: -90, position: "insideLeft" }}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        {state.species.map((s) => (
          <Line
            key={s} dataKey={s} type="monotone" dot={false} strokeWidth={2}
            stroke={`var(--color-${s})`} isAnimationActive={false}
            strokeDasharray={state.hidden.includes(s) ? "6 4" : undefined}
          />
        ))}
        {observedSpecies.map((s) => (
          <Scatter
            key={`obs-${s}`} dataKey={`${s}__obs`} name={s}
            legendType="none" fill={`var(--color-${s})`}
            stroke="var(--background)" strokeWidth={1} isAnimationActive={false}
          />
        ))}
      </ComposedChart>
    </ChartContainer>
  )
}
