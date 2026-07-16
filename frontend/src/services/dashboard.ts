import { apiRequest } from "@/services/api";
import type { DashboardSummary } from "@/types/domain";

export async function getSummary(): Promise<DashboardSummary> {
  return apiRequest({ method: "GET", url: "/dashboard/summary" });
}

export async function getPipeline(): Promise<{ stages: { status: string; count: number }[] }> {
  return apiRequest({ method: "GET", url: "/dashboard/pipeline" });
}

export async function getAgents(): Promise<{ agents: { agent: string; count: number }[] }> {
  return apiRequest({ method: "GET", url: "/dashboard/agents" });
}

export async function getRevenue(): Promise<{
  monthly: { month: string; total: number | string }[];
  total: number | string;
}> {
  return apiRequest({ method: "GET", url: "/dashboard/revenue" });
}

export async function getOrders(): Promise<{
  by_status: { status: string; count: number }[];
  recent: { order_id: string; deal_id?: string | null; order_status?: string | null; created_at?: string | null }[];
}> {
  return apiRequest({ method: "GET", url: "/dashboard/orders" });
}

export async function getApprovals(): Promise<{
  by_decision: { status: string; count: number }[];
  pending: { approval_id: string; quotation_id?: string | null; decision?: string | null; approved_at?: string | null }[];
}> {
  return apiRequest({ method: "GET", url: "/dashboard/approvals" });
}
