import type { LucideIcon } from 'lucide-react'

export function EmptyState({ icon: Icon, title, body }: { icon: LucideIcon; title: string; body: string }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6 border border-dashed border-line rounded-lg">
      <Icon size={22} className="text-ink-faint mb-3" />
      <div className="font-medium text-sm text-ink mb-1">{title}</div>
      <p className="text-xs text-ink-muted max-w-xs">{body}</p>
    </div>
  )
}
