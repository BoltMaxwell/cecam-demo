import {
  CartesianGrid, ComposedChart, Line, ReferenceLine, Scatter, XAxis, YAxis,
} from "recharts"
import {
  ChartContainer, ChartLegend, ChartLegendContent, ChartTooltip, ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { STATUS } from "@/lib/palette"
import type { LedgerRow } from "@/lib/types"

export function ProgressChart({ rows }: { rows: LedgerRow[] }) {
  const pts = rows.filter((r): r is LedgerRow & { elbo: number } => r.elbo !== null)
  if (pts.length === 0) {
    return <p className="py-6 text-center text-sm italic text-muted-foreground">No runs logged yet.</p>
  }
  const config = {
    elbo: { label: "ELBO", color: STATUS.neutral },
    keep: { label: "keep", color: STATUS.good },
    discard: { label: "discard", color: STATUS.critical },
    crash: { label: "crash", color: STATUS.neutral },
  } satisfies ChartConfig
  const byStatus = (s: string) => pts.filter((r) => r.status === s)
  const baseline = pts[0].elbo

  return (
    <ChartContainer config={config} className="aspect-[2/1] w-full">
      <ComposedChart data={pts} margin={{ top: 8, right: 8 }}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="iter" type="number" allowDecimals={false}
          domain={[0, "dataMax"]}
          label={{ value: "iteration", position: "insideBottomRight", offset: -4 }}
        />
        <YAxis width={48} domain={["auto", "auto"]}
               label={{ value: "ELBO", angle: -90, position: "insideLeft" }} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <ReferenceLine y={baseline} stroke={STATUS.neutral} strokeDasharray="4 4"
                       label={{ value: "baseline", position: "insideBottomLeft", fontSize: 11 }} />
        <Line dataKey="elbo" stroke="var(--muted-foreground)" strokeWidth={1}
              dot={false} legendType="none" isAnimationActive={false} />
        <Scatter data={byStatus("keep")} dataKey="elbo" name="keep"
                 fill="var(--color-keep)" isAnimationActive={false} />
        <Scatter data={byStatus("discard")} dataKey="elbo" name="discard" shape="cross"
                 fill="var(--color-discard)" isAnimationActive={false} />
        <Scatter data={byStatus("crash")} dataKey="elbo" name="crash" shape="triangle"
                 fill="var(--color-crash)" isAnimationActive={false} />
      </ComposedChart>
    </ChartContainer>
  )
}
