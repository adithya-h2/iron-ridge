import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, RotateCw, XCircle, ActivitySquare } from 'lucide-react'
import { Topbar } from '../components/Topbar'
import { Badge } from '../components/Badge'
import { EmptyState } from '../components/EmptyState'
import { api } from '../api/client'
import type { AgentJob, JobStatus } from '../types/deal'

const statusMeta: Record<JobStatus, { tone: 'alarm' | 'signal' | 'clear'; icon: typeof XCircle; label: string }> = {
  FAILED: { tone: 'alarm', icon: XCircle, label: 'Failed' },
  RETRYING: { tone: 'signal', icon: RotateCw, label: 'Retrying' },
  SUCCESS: { tone: 'clear', icon: CheckCircle2, label: 'Succeeded' },
}

export function SystemHealth() {
  const [jobs, setJobs] = useState<AgentJob[]>([])

  useEffect(() => {
    api.getJobs().then(setJobs)
  }, [])

  const issues = jobs.filter((j) => j.status !== 'SUCCESS')

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Topbar title="System Health" subtitle="Agent call reliability — failures, retries, and their outcomes" />

      <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6">
        <div className="grid grid-cols-3 gap-4 max-w-2xl">
          <div className="rounded-lg border border-line bg-base-raised p-4">
            <div className="text-xs font-mono uppercase text-ink-faint mb-1">Failed</div>
            <div className="font-display text-xl font-semibold text-alarm">
              {jobs.filter((j) => j.status === 'FAILED').length}
            </div>
          </div>
          <div className="rounded-lg border border-line bg-base-raised p-4">
            <div className="text-xs font-mono uppercase text-ink-faint mb-1">Retrying</div>
            <div className="font-display text-xl font-semibold text-signal">
              {jobs.filter((j) => j.status === 'RETRYING').length}
            </div>
          </div>
          <div className="rounded-lg border border-line bg-base-raised p-4">
            <div className="text-xs font-mono uppercase text-ink-faint mb-1">Succeeded</div>
            <div className="font-display text-xl font-semibold text-clear">
              {jobs.filter((j) => j.status === 'SUCCESS').length}
            </div>
          </div>
        </div>

        <div>
          <h2 className="font-display text-sm font-semibold text-ink mb-3">Attention needed</h2>
          {issues.length === 0 ? (
            <EmptyState icon={ActivitySquare} title="All clear" body="No agent calls have failed or are retrying right now." />
          ) : (
            <div className="space-y-3 max-w-3xl">
              {issues.map((job) => {
                const meta = statusMeta[job.status]
                const Icon = meta.icon
                return (
                  <div key={job.id} className="rounded-lg border border-line bg-base-raised p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono text-xs uppercase text-signal">{job.agent}</span>
                          <span className="font-mono text-xs text-ink-faint">{job.endpoint}</span>
                        </div>
                        <Link to={`/deals/${job.deal_id}`} className="text-sm text-ink hover:text-signal">
                          {job.deal_id}
                        </Link>
                        {job.error_message && (
                          <p className="text-xs text-ink-muted mt-2 font-mono bg-base-inset rounded px-2 py-1.5 border border-line">
                            {job.error_message}
                          </p>
                        )}
                      </div>
                      <Badge tone={meta.tone}>
                        <Icon size={11} /> {meta.label}
                      </Badge>
                    </div>
                    <div className="text-[11px] font-mono text-ink-faint mt-3">
                      Attempt {job.attempt} of {job.max_attempts} · {new Date(job.created_at).toLocaleString()}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
