import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'

export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  const { theme, toggle } = useTheme()

  return (
    <header className="h-16 shrink-0 border-b border-line flex items-center justify-between px-6">
      <div>
        <h1 className="font-display font-semibold text-lg text-ink leading-tight">{title}</h1>
        {subtitle && <p className="text-xs text-ink-muted mt-0.5">{subtitle}</p>}
      </div>
      <button
        onClick={toggle}
        aria-label="Toggle color theme"
        className="h-9 w-9 rounded-md border border-line flex items-center justify-center text-ink-muted hover:text-signal hover:border-signal-dim transition-colors"
      >
        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
      </button>
    </header>
  )
}
