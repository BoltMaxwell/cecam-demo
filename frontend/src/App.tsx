import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { FitChart } from "@/components/FitChart"
import { Header } from "@/components/Header"
import { LedgerTable } from "@/components/LedgerTable"
import { MassChart } from "@/components/MassChart"
import { MetricBar } from "@/components/MetricBar"
import { ProgressChart } from "@/components/ProgressChart"
import { useLiveData } from "@/lib/useLiveData"

function Waiting({ msg }: { msg: string }) {
  return <p className="py-10 text-center text-sm italic text-muted-foreground">{msg}</p>
}

export default function App() {
  const { state, ledger, error, updatedAt } = useLiveData()
  const [dark, setDark] = useState(false)  // default light: projector legibility
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark)
  }, [dark])

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header updatedAt={updatedAt} error={error} dark={dark}
              onToggleTheme={() => setDark((d) => !d)} />
      <main className="mx-auto grid max-w-[1400px] items-start gap-5 p-6 lg:grid-cols-[1.05fr_1fr]">
        <Card>
          <CardHeader><CardTitle>Current model fit</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {state === null ? (
              <Skeleton className="h-[420px] w-full" />
            ) : !state.ready ? (
              <Waiting msg="waiting for the first run…" />
            ) : (
              <>
                <MetricBar state={state} />
                <FitChart state={state} />
                <Separator />
                <MassChart state={state} />
              </>
            )}
          </CardContent>
        </Card>
        <div className="flex flex-col gap-5">
          <Card>
            <CardHeader><CardTitle>AutoResearch progress</CardTitle></CardHeader>
            <CardContent>
              {ledger === null
                ? <Skeleton className="h-[220px] w-full" />
                : <ProgressChart rows={ledger.rows} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Experiment ledger</CardTitle></CardHeader>
            <CardContent>
              {ledger === null
                ? <Skeleton className="h-[160px] w-full" />
                : <LedgerTable rows={ledger.rows} />}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
