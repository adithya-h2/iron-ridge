import { Link } from 'react-router-dom'
import { AlertTriangle, Clock } from 'lucide-react'
import type { Deal } from '../types/deal'
import { Badge } from './Badge'

function hoursSince(iso: string) {
  return (Date.now() - new Date(iso).getTime()) / 3_600_000
}

export function DealCard({ deal }: { deal: Deal }) {
  const overdue =
    deal.stage === 'APPROVAL' &&
    deal.approval_requested_at !== undefined &&
    hoursSince(deal.approval_requested_at) > deal.approval_sla_hours

  const flagged = deal.confidence !== undefined && deal.confidence < 0.6 && deal.stage !== 'REJECTED'

  return (
    <Link
      to={`/deals/${deal.id}`}
      className="block rounded-lg border border-line bg-base-raised p-4 hover:border-signal-dim transition-colors group"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <div className="font-medium text-sm text-ink group-hover:text-signal transition-colors">
            {deal.org_name}
          </div>
          <div className="text-xs font-mono text-ink-faint mt-0.5">{deal.id}</div>
        </div>
        {overdue && (
          <Badge tone="alarm">
            <Clock size={11} /> Overdue
          </Badge>
        )}
        {flagged && !overdue && (
          <Badge tone="signal">
            <AlertTriangle size={11} /> Flagged
          </Badge>
        )}
      </div>

      <div className="text-xs text-ink-muted mb-3">
        {deal.required_quantity}× {deal.vehicle_type} — {deal.city}, {deal.country}
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="font-mono text-ink-faint uppercase tracking-wide">{deal.status.replace(/_/g, ' ')}</span>
        {deal.lead_score !== undefined && (
          <span className="font-mono text-ink-muted">Score {deal.lead_score}</span>
        )}
      </div>
    </Link>
  )
}
