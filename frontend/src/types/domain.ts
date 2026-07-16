export interface WorkflowCustomerSummary {
  customer_id?: string | null;
  company_name?: string | null;
  contact_person?: string | null;
  email?: string | null;
}

export interface WorkflowRetryState {
  attempt_count: number;
  last_attempt?: string | null;
  last_error?: string | null;
  retryable: boolean;
}

export interface WorkflowStatus {
  deal_id: string;
  customer?: WorkflowCustomerSummary | null;
  workflow_id?: string | null;
  current_agent?: string | null;
  current_status?: string | null;
  progress_percentage: number;
  created_at?: string | null;
  updated_at?: string | null;
  estimated_completion?: string | null;
  retry?: WorkflowRetryState | null;
}

export interface WorkflowTimelineEvent {
  timestamp?: string | null;
  agent?: string | null;
  status?: string | null;
  action?: string | null;
  message?: string | null;
}

export interface WorkflowTimeline {
  deal_id: string;
  events: WorkflowTimelineEvent[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LeadIntakePayload {
  source: string;
  submission_channel: string;
  org_name?: string;
  company_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  city?: string;
  state?: string;
  country?: string;
  industry?: string;
  vehicle_type?: string;
  required_quantity?: number | string;
  contact_person?: string;
  notes?: string;
  department?: string;
  expected_timeline?: string;
  budget_range?: string;
}

export interface LeadIntakeResult {
  deal_id: string;
  customer_id: string;
  workflow_id: string;
  lead_source: string;
  submission_channel: string;
  status: string;
  company_name?: string | null;
  is_duplicate: boolean;
  matched_customer_id?: string | null;
  lead_score?: number | null;
}

export interface DashboardSummary {
  total_deals: number;
  deals_by_status: { status: string; count: number }[];
  total_revenue: number | string;
  pending_approvals: number;
  active_orders: number;
}

export interface Approval {
  approval_id: string;
  quotation_id?: string | null;
  approved_by?: string | null;
  decision?: string | null;
  remarks?: string | null;
  approved_at?: string | null;
}

export interface Order {
  order_id: string;
  deal_id?: string | null;
  quotation_id?: string | null;
  order_status?: string | null;
  erp_reference?: string | null;
  created_at?: string | null;
}

export interface AuditLog {
  audit_id: string;
  deal_id?: string | null;
  agent_name?: string | null;
  action?: string | null;
  previous_status?: string | null;
  new_status?: string | null;
  reason?: string | null;
  created_at?: string | null;
}

export interface NotificationPayload {
  template: string;
  channels: string[];
  deal_id?: string | null;
  workflow_id?: string | null;
  context?: Record<string, unknown>;
}

export interface NotificationResult {
  template: string;
  deliveries: { channel: string; success: boolean; detail?: string | null }[];
}
