import { NavLink } from 'react-router-dom'
import { LayoutDashboard, GitBranch, ShieldCheck, ActivitySquare, Settings, Flame } from 'lucide-react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/pipeline', label: 'Pipeline', icon: GitBranch },
  { to: '/approvals', label: 'Approvals', icon: ShieldCheck },
  { to: '/system-health', label: 'System Health', icon: ActivitySquare },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-line bg-base-raised/40 flex flex-col">
      <div className="h-16 flex items-center gap-2.5 px-5 border-b border-line">
        <div className="h-8 w-8 rounded-md bg-signal-bg border border-signal-dim flex items-center justify-center">
          <Flame size={16} className="text-signal" strokeWidth={2.5} />
        </div>
        <div className="leading-tight">
          <div className="font-display font-semibold text-sm text-ink">Iron Ridge</div>
          <div className="text-[10px] font-mono text-ink-faint tracking-wide">SALES OPS</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-signal-bg text-signal'
                  : 'text-ink-muted hover:text-ink hover:bg-base-inset',
              ].join(' ')
            }
          >
            <Icon size={16} strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-line">
        <div className="rounded-md border border-line bg-base-inset px-3 py-2.5">
          <div className="text-[10px] font-mono text-ink-faint uppercase tracking-wide mb-1">Pipeline</div>
          <div className="text-xs text-ink-muted leading-relaxed">
            Marty → Lisa → Neil → Paul → Victor → Sally → Adam
          </div>
        </div>
      </div>
    </aside>
  )
}
