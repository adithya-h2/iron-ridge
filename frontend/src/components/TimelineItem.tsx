import type { DealEvent } from '../types/deal'

export function TimelineItem({ event, isLast }: { event: DealEvent; isLast: boolean }) {
  const time = new Date(event.created_at)

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="h-2.5 w-2.5 rounded-full bg-signal shrink-0 mt-1" />
        {!isLast && <div className="w-px flex-1 bg-line mt-1" />}
      </div>
      <div className="pb-6">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="font-mono text-xs uppercase tracking-wide text-signal">{event.agent}</span>
          <span className="text-[11px] font-mono text-ink-faint">
            {time.toLocaleDateString()} · {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <p className="text-sm text-ink-muted">{event.message}</p>
        <div className="text-[11px] font-mono text-ink-faint mt-1">
          {event.from_status ?? '—'} → {event.to_status}
        </div>
      </div>
    </div>
  )
}
