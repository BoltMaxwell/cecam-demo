import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GOLD, STATUS } from "@/lib/palette"

interface Props {
  updatedAt: number | null
  error: boolean
  dark: boolean
  onToggleTheme: () => void
}

export function Header({ updatedAt, error, dark, onToggleTheme }: Props) {
  const [, forceTick] = useState(0)
  useEffect(() => {
    const id = setInterval(() => forceTick((n) => n + 1), 1000)
    return () => clearInterval(id)
  }, [])
  const ago = updatedAt === null ? null : Math.max(0, Math.round((Date.now() - updatedAt) / 1000))

  return (
    <header
      className="flex items-center gap-3 border-b bg-card px-6 py-3"
      style={{ borderTop: `6px solid ${GOLD}` }}
    >
      <h1 className="text-lg font-semibold tracking-tight">Catalysis AutoResearch</h1>
      {error ? (
        <Badge style={{ background: STATUS.critical }} className="text-white">reconnecting…</Badge>
      ) : (
        <Badge style={{ background: STATUS.good }} className="text-white">LIVE</Badge>
      )}
      <span className="ml-auto text-sm text-muted-foreground">
        {ago === null ? "waiting for data…" : `updated ${ago}s ago`}
      </span>
      <Button variant="ghost" size="sm" onClick={onToggleTheme} aria-label="toggle theme">
        {dark ? "light" : "dark"}
      </Button>
    </header>
  )
}
