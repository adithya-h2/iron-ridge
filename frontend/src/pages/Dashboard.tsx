import { useEffect, useState } from 'react'
import { Flame, ShieldAlert, Truck, CheckCircle2 } from 'lucide-react'
import { Topbar } from '../components/Topbar'
import { StatCard } from '../components/StatCard'
import { DealCard } from '../components/DealCard'
import { api } from '../api/client'
import type { Deal, StageCount } from '../types/deal'

export function Dashboard() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [counts, setCounts] = useState<StageCount[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getDeals(), api.getStageCounts()]).then(([d, c]) => {
      setDeals(d)
      setCounts(c)
      setLoading(false)
    })
  }, [])

  const activeDeals = deals.filter((d) => d.stage !== 'REJECTED' && d.stage !== 'DELIVERY')
  const awaitingApproval = counts.find((c) => c.stage === 'APPROVAL')?.count ?? 0
  const delivered = counts.find((c) => c.stage === 'DELIVERY')?.count ?? 0
  const rejected = counts.find((c) => c.stage === 'REJECTED')?.count ?? 0

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title="Dashboard" subtitle="Live status across the Iron Ridge sales pipeline" />

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <StatCard label="Active deals" value={activeDeals.length} icon={Flame} tone="signal" />
          <StatCard label="Awaiting Victor" value={awaitingApproval} icon={ShieldAlert} tone="signal" />
          <StatCard label="Delivered" value={delivered} icon={CheckCircle2} tone="clear" />
          <StatCard label="Rejected" value={rejected} icon={Truck} tone="alarm" />
        </div>

        <div>
          <h2 className="font-display text-sm font-semibold text-ink mb-3">In progress</h2>
          {loading ? (
            <p className="text-sm text-ink-muted">Loading deals…</p>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {activeDeals.map((d) => (
                <DealCard key={d.id} deal={d} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
