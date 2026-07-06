import { useEffect, useState } from 'react'
import { Topbar } from '../components/Topbar'
import { DealCard } from '../components/DealCard'
import { EmptyState } from '../components/EmptyState'
import { api } from '../api/client'
import type { Deal, DealStage } from '../types/deal'
import { Inbox } from 'lucide-react'

const COLUMNS: { stage: DealStage; label: string }[] = [
  { stage: 'LEAD', label: 'Lead' },
  { stage: 'QUALIFICATION', label: 'Qualification' },
  { stage: 'REQUIREMENTS', label: 'Requirements' },
  { stage: 'PRICING', label: 'Pricing' },
  { stage: 'APPROVAL', label: 'Approval' },
  { stage: 'ORDER', label: 'Order' },
  { stage: 'DELIVERY', label: 'Delivery' },
]

export function Pipeline() {
  const [deals, setDeals] = useState<Deal[]>([])

  useEffect(() => {
    api.getDeals().then(setDeals)
  }, [])

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title="Pipeline" subtitle="Every deal, grouped by its current stage" />
      <div className="flex-1 overflow-x-auto scrollbar-thin p-6">
        <div className="flex gap-4 min-w-max h-full">
          {COLUMNS.map((col) => {
            const colDeals = deals.filter((d) => d.stage === col.stage)
            return (
              <div key={col.stage} className="w-72 shrink-0 flex flex-col">
                <div className="flex items-center justify-between mb-3 px-1">
                  <span className="font-mono text-xs uppercase tracking-wide text-ink-muted">{col.label}</span>
                  <span className="font-mono text-xs text-ink-faint">{colDeals.length}</span>
                </div>
                <div className="space-y-3">
                  {colDeals.length === 0 ? (
                    <div className="text-xs text-ink-faint border border-dashed border-line rounded-lg py-6 text-center">
                      No deals
                    </div>
                  ) : (
                    colDeals.map((d) => <DealCard key={d.id} deal={d} />)
                  )}
                </div>
              </div>
            )
          })}
        </div>
        {deals.length === 0 && (
          <EmptyState icon={Inbox} title="No deals yet" body="New leads submitted through the webhook will appear here." />
        )}
      </div>
    </div>
  )
}
