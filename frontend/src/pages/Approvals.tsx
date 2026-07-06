import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Clock, ShieldCheck, X } from 'lucide-react'
import { Topbar } from '../components/Topbar'
import { Badge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { api } from '../api/client'
import type { Deal } from '../types/deal'

function hoursSince(iso: string) {
  return (Date.now() - new Date(iso).getTime()) / 3_600_000
}

export function Approvals() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [rejectingId, setRejectingId] = useState<string | null>(null)
  const [reason, setReason] = useState('')

  const load = () => api.getDeals().then((all) => setDeals(all.filter((d) => d.stage === 'APPROVAL')))

  useEffect(() => {
    load()
  }, [])

  const approve = async (id: string) => {
    await api.approveDeal(id)
    load()
  }

  const submitReject = async () => {
    if (!rejectingId) return
    await api.rejectDeal(rejectingId, reason || 'Rejected by Victor via dashboard')
    setRejectingId(null)
    setReason('')
    load()
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title="Approvals" subtitle="Deals waiting on Victor's sign-off before moving to Order" />

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
        {deals.length === 0 ? (
          <EmptyState icon={ShieldCheck} title="Nothing waiting" body="No deals are currently sitting in the approval gate." />
        ) : (
          <div className="space-y-3 max-w-3xl">
            {deals.map((d) => {
              const overdue = d.approval_requested_at ? hoursSince(d.approval_requested_at) > d.approval_sla_hours : false
              const waitedHours = d.approval_requested_at ? Math.round(hoursSince(d.approval_requested_at)) : 0

              return (
                <div key={d.id} className="rounded-lg border border-line bg-base-raised p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <Link to={`/deals/${d.id}`} className="font-medium text-sm text-ink hover:text-signal">
                        {d.org_name}
                      </Link>
                      <div className="text-xs font-mono text-ink-faint mt-0.5">{d.id} · {d.quotation_id}</div>
                      <div className="text-xs text-ink-muted mt-2">
                        {d.required_quantity}× {d.vehicle_type} — quote at {d.discount}% discount
                      </div>
                    </div>
                    {overdue ? (
                      <Badge tone="alarm">
                        <Clock size={11} /> {waitedHours}h — SLA breached ({d.approval_sla_hours}h)
                      </Badge>
                    ) : (
                      <Badge tone="neutral">
                        <Clock size={11} /> Waiting {waitedHours}h of {d.approval_sla_hours}h
                      </Badge>
                    )}
                  </div>

                  <div className="flex items-center gap-2 mt-4">
                    <button
                      onClick={() => approve(d.id)}
                      className="rounded-md bg-signal text-base px-3 py-1.5 text-xs font-medium hover:brightness-110 transition-all"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => setRejectingId(d.id)}
                      className="rounded-md border border-line px-3 py-1.5 text-xs font-medium text-ink-muted hover:text-alarm hover:border-alarm/40 transition-colors"
                    >
                      Reject
                    </button>
                  </div>

                  {rejectingId === d.id && (
                    <div className="mt-4 pt-4 border-t border-line">
                      <label className="text-xs font-mono uppercase text-ink-faint mb-2 block">Rejection reason</label>
                      <div className="flex gap-2">
                        <input
                          autoFocus
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                          placeholder="Why is this deal being rejected?"
                          className="flex-1 rounded-md bg-base-inset border border-line px-3 py-1.5 text-sm text-ink placeholder:text-ink-faint focus:border-signal-dim outline-none"
                        />
                        <button
                          onClick={submitReject}
                          className="rounded-md bg-alarm text-white px-3 py-1.5 text-xs font-medium hover:brightness-110"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setRejectingId(null)}
                          className="rounded-md border border-line px-2 py-1.5 text-ink-muted hover:text-ink"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
