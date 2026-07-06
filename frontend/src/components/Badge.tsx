import type { ReactNode } from 'react'

type Tone = 'neutral' | 'signal' | 'alarm' | 'clear'

const toneClasses: Record<Tone, string> = {
  neutral: 'bg-line/60 text-ink-muted border-line',
  signal: 'bg-signal-bg text-signal border-signal-dim',
  alarm: 'bg-alarm-bg text-alarm border-alarm/40',
  clear: 'bg-clear-bg text-clear border-clear/30',
}

export function Badge({ tone = 'neutral', children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-mono uppercase tracking-wide ${toneClasses[tone]}`}
    >
      {children}
    </span>
  )
}
