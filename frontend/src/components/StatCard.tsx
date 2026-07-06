import type { LucideIcon } from 'lucide-react'

export function StatCard({
  label,
  value,
  icon: Icon,
  tone = 'neutral',
}: {
  label: string
  value: string | number
  icon: LucideIcon
  tone?: 'neutral' | 'signal' | 'alarm' | 'clear'
}) {
  const toneText = {
    neutral: 'text-ink',
    signal: 'text-signal',
    alarm: 'text-alarm',
    clear: 'text-clear',
  }[tone]

  return (
    <div className="rounded-lg border border-line bg-base-raised p-4 shadow-panel">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono uppercase tracking-wide text-ink-faint">{label}</span>
        <Icon size={15} className="text-ink-faint" />
      </div>
      <div className={`font-display text-2xl font-semibold ${toneText}`}>{value}</div>
    </div>
  )
}
