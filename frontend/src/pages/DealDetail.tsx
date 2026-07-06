import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, History } from 'lucide-react'
import { Topbar } from '../components/Topbar'
import { StageRail } from '../components/StageRail'
import { TimelineItem } from '../components/TimelineItem'
import { Badge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { api } from '../api/client'
import type { Deal, DealEvent } from '../types/deal'

export function DealDetail() {
  const { id } = useParams<{ id: string }>()
  const [deal, setDeal] = useState<Deal | undefined>()
  const [events, setEvents] = useState<DealEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.all([api.getDeal(id), api.getDealEvents(id)]).then(([d, e]) => {
      setDeal(d)
      setEvents(e)
      setLoading(false)
    })
  }, [id])

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Topbar title="Deal" />
        <div className="p-6 text-sm text-ink-muted">Loading…</div>
      </div>
    )
  }

  if (!deal) {
    return (
      <div className="flex-1 flex flex-col">
        <Topbar title="Deal not found" />
        <div className="p-6">
          <Link to="/pipeline" className="text-signal text-sm inline-flex items-center gap-1.5">
            <ArrowLeft size={14} /> Back to pipeline
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title={deal.org_name} subtitle={deal.id} />

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6">
        <Link to="/pipeline" className="text-ink-muted hover:text-signal text-xs inline-flex items-center gap-1.5">
          <ArrowLeft size={13} /> Back to pipeline
        </Link>

        <div className="rounded-lg border border-line bg-base-raised p-5">
          <StageRail current={deal.stage} />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2 rounded-lg border border-line bg-base-raised p-5">
            <h2 className="font-display text-sm font-semibold text-ink mb-4">Deal details</h2>
            <dl className="grid grid-cols-2 gap-y-3 text-sm">
              <dt className="text-ink-faint font-mono text-xs uppercase">Vehicle</dt>
              <dd className="text-ink">{deal.required_quantity}× {deal.vehicle_type}</dd>

              <dt className="text-ink-faint font-mono text-xs uppercase">Location</dt>
              <dd className="text-ink">{deal.city}, {deal.country}</dd>

              <dt className="text-ink-faint font-mono text-xs uppercase">Status</dt>
              <dd><Badge tone="signal">{deal.status.replace(/_/g, ' ')}</Badge></dd>

              <dt className="text-ink-faint font-mono text-xs uppercase">Current agent</dt>
              <dd className="text-ink font-mono text-xs">{deal.current_agent}</dd>

              {deal.lead_score !== undefined && (
                <>
                  <dt className="text-ink-faint font-mono text-xs uppercase">Lead score</dt>
                  <dd className="text-ink">{deal.lead_score} / 100</dd>
                </>
              )}

              {deal.confidence !== undefined && (
                <>
                  <dt className="text-ink-faint font-mono text-xs uppercase">Validation confidence</dt>
                  <dd className="text-ink">
                    {(deal.confidence * 100).toFixed(0)}%
                    {deal.confidence < 0.6 && <span className="text-signal ml-2 text-xs">Flagged for review</span>}
                  </dd>
                </>
              )}

              {deal.quotation_id && (
                <>
                  <dt className="text-ink-faint font-mono text-xs uppercase">Quotation</dt>
                  <dd className="text-ink font-mono text-xs">{deal.quotation_id} · {deal.discount}% discount</dd>
                </>
              )}

              {deal.order_id && (
                <>
                  <dt className="text-ink-faint font-mono text-xs uppercase">Order</dt>
                  <dd className="text-ink font-mono text-xs">{deal.order_id}</dd>
                </>
              )}

              {deal.rejection_reason && (
                <>
                  <dt className="text-ink-faint font-mono text-xs uppercase">Rejection reason</dt>
                  <dd className="text-alarm text-sm">{deal.rejection_reason}</dd>
                </>
              )}
            </dl>
          </div>

          <div className="rounded-lg border border-line bg-base-raised p-5">
            <h2 className="font-display text-sm font-semibold text-ink mb-4">Timestamps</h2>
            <dl className="space-y-3 text-xs">
              <div>
                <dt className="text-ink-faint font-mono uppercase mb-0.5">Created</dt>
                <dd className="text-ink">{new Date(deal.created_at).toLocaleString()}</dd>
              </div>
              <div>
                <dt className="text-ink-faint font-mono uppercase mb-0.5">Last updated</dt>
                <dd className="text-ink">{new Date(deal.updated_at).toLocaleString()}</dd>
              </div>
              {deal.approval_requested_at && (
                <div>
                  <dt className="text-ink-faint font-mono uppercase mb-0.5">Approval requested</dt>
                  <dd className="text-ink">{new Date(deal.approval_requested_at).toLocaleString()}</dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        <div className="rounded-lg border border-line bg-base-raised p-5">
          <h2 className="font-display text-sm font-semibold text-ink mb-5 flex items-center gap-2">
            <History size={15} className="text-ink-faint" /> Audit trail
          </h2>
          {events.length === 0 ? (
            <EmptyState icon={History} title="No events logged" body="Stage transitions for this deal will appear here as agents run." />
          ) : (
            <div>
              {events.map((e, i) => (
                <TimelineItem key={e.id} event={e} isLast={i === events.length - 1} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
