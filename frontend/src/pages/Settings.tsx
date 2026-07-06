import { Topbar } from '../components/Topbar'

export function Settings() {
  const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
  const usingMocks = (import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true'

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title="Settings" subtitle="Backend connection and workflow configuration" />

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6 max-w-2xl">
        <section className="rounded-lg border border-line bg-base-raised p-5">
          <h2 className="font-display text-sm font-semibold text-ink mb-1">Backend connection</h2>
          <p className="text-xs text-ink-muted mb-4">
            Set in <code className="font-mono text-signal">.env</code> as <code className="font-mono">VITE_API_BASE_URL</code> and{' '}
            <code className="font-mono">VITE_USE_MOCKS</code>. Restart the dev server after changing.
          </p>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between border-b border-line pb-3">
              <dt className="text-ink-faint font-mono text-xs uppercase">API base URL</dt>
              <dd className="font-mono text-ink">{apiBase}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-ink-faint font-mono text-xs uppercase">Data source</dt>
              <dd className="font-mono text-ink">{usingMocks ? 'Mock data (no backend required)' : 'Live FastAPI backend'}</dd>
            </div>
          </dl>
        </section>

        <section className="rounded-lg border border-line bg-base-raised p-5">
          <h2 className="font-display text-sm font-semibold text-ink mb-1">Approval SLA</h2>
          <p className="text-xs text-ink-muted mb-4">
            Deals sitting in the Approval stage longer than this are flagged as overdue on the Approvals page.
            Currently defined per-deal by the backend (<code className="font-mono">approval_sla_hours</code>) —
            a global default can be added here once the backend exposes a settings endpoint.
          </p>
          <div className="flex items-center gap-2 text-sm text-ink">
            <span className="font-mono text-signal text-lg font-semibold">24</span>
            <span className="text-ink-muted text-xs">hours (current default)</span>
          </div>
        </section>

        <section className="rounded-lg border border-line bg-base-raised p-5">
          <h2 className="font-display text-sm font-semibold text-ink mb-1">Pipeline reference</h2>
          <p className="text-xs text-ink-muted">
            Marty (Lead Capture) → Lisa (Validation) → Neil (Requirements) → Paul (Pricing) → Victor (Human
            Approval via Slack) → Sally (Order Management) → Adam (Customer Updates)
          </p>
        </section>
      </div>
    </div>
  )
}
