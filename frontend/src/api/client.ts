import type { AgentJob, Deal, DealEvent, StageCount } from '../types/deal'
import { mockDeals, mockEvents, mockJobs } from './mockData'

// ─────────────────────────────────────────────────────────────────────────
// HOW TO CONNECT THIS TO THE REAL BACKEND
//
// 1. Set VITE_API_BASE_URL and VITE_USE_MOCKS=false in a .env file
//    (see .env.example).
// 2. Confirm the real endpoint paths against app/api/routes/ and update
//    the ENDPOINTS map below if they differ.
// 3. Confirm the real response shapes against the Pydantic schemas and
//    update src/types/deal.ts to match — this file does not need to
//    change beyond the ENDPOINTS map.
//
// Every function below has a real fetch() call already written, gated
// behind USE_MOCKS, so switching over is a one-line env change once the
// backend is confirmed to return matching shapes.
// ─────────────────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const USE_MOCKS = (import.meta.env.VITE_USE_MOCKS ?? 'true') === 'true'

const ENDPOINTS = {
  deals: '/deals',
  deal: (id: string) => `/deals/${id}`,
  dealEvents: (id: string) => `/deals/${id}/events`,
  approve: (id: string) => `/deals/${id}/approve`,
  reject: (id: string) => `/deals/${id}/reject`,
  stageCounts: '/deals/stats/by-stage',
  jobs: '/jobs',
  health: '/health',
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status} on ${path}`)
  }
  return res.json() as Promise<T>
}

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

export const api = {
  async getDeals(): Promise<Deal[]> {
    if (USE_MOCKS) {
      await delay(250)
      return mockDeals
    }
    return request<Deal[]>(ENDPOINTS.deals)
  },

  async getDeal(id: string): Promise<Deal | undefined> {
    if (USE_MOCKS) {
      await delay(150)
      return mockDeals.find((d) => d.id === id)
    }
    return request<Deal>(ENDPOINTS.deal(id))
  },

  async getDealEvents(id: string): Promise<DealEvent[]> {
    if (USE_MOCKS) {
      await delay(150)
      return mockEvents[id] ?? []
    }
    return request<DealEvent[]>(ENDPOINTS.dealEvents(id))
  },

  async getStageCounts(): Promise<StageCount[]> {
    if (USE_MOCKS) {
      await delay(150)
      const counts = new Map<string, number>()
      for (const d of mockDeals) counts.set(d.stage, (counts.get(d.stage) ?? 0) + 1)
      return Array.from(counts.entries()).map(([stage, count]) => ({
        stage: stage as StageCount['stage'],
        count,
      }))
    }
    return request<StageCount[]>(ENDPOINTS.stageCounts)
  },

  async getJobs(): Promise<AgentJob[]> {
    if (USE_MOCKS) {
      await delay(150)
      return mockJobs
    }
    return request<AgentJob[]>(ENDPOINTS.jobs)
  },

  async approveDeal(id: string): Promise<void> {
    if (USE_MOCKS) {
      await delay(300)
      const d = mockDeals.find((x) => x.id === id)
      if (d) {
        d.status = 'APPROVED'
        d.stage = 'ORDER'
      }
      return
    }
    await request(ENDPOINTS.approve(id), { method: 'POST' })
  },

  async rejectDeal(id: string, reason: string): Promise<void> {
    if (USE_MOCKS) {
      await delay(300)
      const d = mockDeals.find((x) => x.id === id)
      if (d) {
        d.status = 'REJECTED'
        d.stage = 'REJECTED'
        d.rejection_reason = reason
      }
      return
    }
    await request(ENDPOINTS.reject(id), {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
  },
}
