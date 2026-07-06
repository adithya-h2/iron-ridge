// These types mirror the backend's Deal / WorkflowEvent entities as described
// in the Iron Ridge README. Field names are best-guess based on the documented
// pipeline stages and agent outputs — confirm against the real Pydantic
// schemas in app/api/routes/ and adjust here once known. This file is the
// ONE place to edit if the real backend shapes differ.

export type DealStage =
  | 'LEAD'
  | 'QUALIFICATION'
  | 'REQUIREMENTS'
  | 'PRICING'
  | 'APPROVAL'
  | 'ORDER'
  | 'PRODUCTION'
  | 'DELIVERY'
  | 'REJECTED'

export type DealStatus =
  | 'NEW_LEAD'
  | 'VALIDATED'
  | 'REQUIREMENTS_COLLECTED'
  | 'PRICED'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'REJECTED'
  | 'ORDER_CREATED'
  | 'IN_PRODUCTION'
  | 'DELIVERED'

export type AgentName = 'MARTY' | 'LISA' | 'NEIL' | 'PAUL' | 'VICTOR' | 'SALLY' | 'ADAM'

export interface Deal {
  id: string
  org_name: string
  vehicle_type: string
  required_quantity: number
  city: string
  country: string
  status: DealStatus
  stage: DealStage
  current_agent: AgentName
  lead_score?: number
  confidence?: number
  quotation_id?: string
  discount?: number
  order_id?: string
  delivery_status?: string
  rejection_reason?: string
  created_at: string
  updated_at: string
  approval_requested_at?: string
  approval_sla_hours: number
}

export interface DealEvent {
  id: string
  deal_id: string
  agent: AgentName | 'SYSTEM'
  from_status: DealStatus | null
  to_status: DealStatus
  message: string
  created_at: string
}

export type JobStatus = 'SUCCESS' | 'FAILED' | 'RETRYING'

export interface AgentJob {
  id: string
  deal_id: string
  agent: AgentName
  endpoint: string
  status: JobStatus
  attempt: number
  max_attempts: number
  error_message?: string
  created_at: string
}

export interface StageCount {
  stage: DealStage
  count: number
}
