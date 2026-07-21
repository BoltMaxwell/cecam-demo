import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import { STATUS } from "@/lib/palette"
import type { LedgerRow } from "@/lib/types"

function StatusBadge({ status }: { status: string }) {
  const bg =
    status === "keep" ? STATUS.good :
    status === "discard" ? STATUS.critical : STATUS.neutral
  return <Badge style={{ background: bg }} className="text-white">{status}</Badge>
}

export function LedgerTable({ rows }: { rows: LedgerRow[] }) {
  if (rows.length === 0) {
    return <p className="py-6 text-center text-sm italic text-muted-foreground">No runs logged yet.</p>
  }
  const hasGate = rows.some((r) => r.mass_gate !== null)
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-8">#</TableHead>
          <TableHead>commit</TableHead>
          <TableHead className="text-right">ELBO</TableHead>
          {hasGate && <TableHead>gate</TableHead>}
          <TableHead>status</TableHead>
          <TableHead>description</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.iter}>
            <TableCell className="text-muted-foreground">{r.iter}</TableCell>
            <TableCell className="font-mono text-xs">{r.commit}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">
              {r.elbo?.toFixed(2) ?? "—"}
            </TableCell>
            {hasGate && (
              <TableCell>
                {r.mass_gate === "PASS" ? "✓ PASS" : r.mass_gate === "FAIL" ? "✗ FAIL" : "—"}
              </TableCell>
            )}
            <TableCell><StatusBadge status={r.status} /></TableCell>
            <TableCell className="max-w-[30ch] truncate" title={r.description}>
              {r.description}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
