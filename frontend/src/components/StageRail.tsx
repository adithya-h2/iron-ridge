import type { DealStage } from '../types/deal'

const ROUTE: { stage: DealStage; label: string }[] = [
  { stage: 'LEAD', label: 'Lead' },
  { stage: 'QUALIFICATION', label: 'Qualification' },
  { stage: 'REQUIREMENTS', label: 'Requirements' },
  { stage: 'PRICING', label: 'Pricing' },
  { stage: 'APPROVAL', label: 'Approval' },
  { stage: 'ORDER', label: 'Order' },
  { stage: 'PRODUCTION', label: 'Production' },
  { stage: 'DELIVERY', label: 'Delivery' },
]

export function StageRail({ current, compact = false }: { current: DealStage; compact?: boolean }) {
  if (current === 'REJECTED') {
    return (
      <div className="flex items-center gap-2 font-mono text-xs text-alarm">
        <span className="h-2 w-2 rounded-full bg-alarm" />
        ROUTE TERMINATED — REJECTED
      </div>
    )
  }

  const currentIndex = ROUTE.findIndex((r) => r.stage === current)

  return (
    <div className="flex items-center w-full">
      {ROUTE.map((r, i) => {
        const done = i < currentIndex
        const active = i === currentIndex
        return (
          <div key={r.stage} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center gap-1.5 shrink-0">
              <div
                className={[
                  'rounded-full flex items-center justify-center transition-colors',
                  compact ? 'h-2.5 w-2.5' : 'h-3.5 w-3.5 border-2',
                  active
                    ? 'bg-signal border-signal shadow-[0_0_0_4px_rgba(255,149,0,0.15)]'
                    : done
                      ? 'bg-clear border-clear'
                      : 'bg-transparent border-line',
                ].join(' ')}
              />
              {!compact && (
                <span
                  className={[
                    'font-mono text-[10px] uppercase tracking-wide whitespace-nowrap',
                    active ? 'text-signal' : done ? 'text-clear' : 'text-ink-faint',
                  ].join(' ')}
                >
                  {r.label}
                </span>
              )}
            </div>
            {i < ROUTE.length - 1 && (
              <div
                className={[
                  'flex-1 mx-1',
                  compact ? 'h-px' : 'h-0.5',
                  i < currentIndex ? 'bg-clear' : 'bg-line',
                ].join(' ')}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
