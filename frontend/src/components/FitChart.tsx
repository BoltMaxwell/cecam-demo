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

  const gridRows = state.grid_times.map((t, i) => ({
    t,
    ...Object.fromEntries(state.species.map((s) => [s, state.predicted[s][i]])),
  }))
  const obsRows = (s: string) =>
    state.obs_times.map((t, i) => ({ t, y: state.observed[s][i] }))
  const tMax = state.grid_times[state.grid_times.length - 1]

  return (
    <ChartContainer config={config} className="aspect-[2/1] w-full">
      <ComposedChart data={gridRows} margin={{ top: 8, right: 8 }}>
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
        {state.species.filter((s) => s in state.observed).map((s) => (
          <Scatter
            key={`obs-${s}`} data={obsRows(s)} dataKey="y" name={s}
            legendType="none" fill={`var(--color-${s})`}
            stroke="var(--background)" strokeWidth={1} isAnimationActive={false}
          />
        ))}
      </ComposedChart>
    </ChartContainer>
  )
}
