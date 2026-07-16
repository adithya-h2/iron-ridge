import { apiRequest } from "@/services/api";
import type { Approval } from "@/types/domain";

export async function requestApproval(quotationId: string): Promise<Approval> {
  return apiRequest({ method: "POST", url: "/approvals/request", data: { quotation_id: quotationId } });
}

export async function approve(approvalId: string): Promise<Approval> {
  return apiRequest({ method: "POST", url: `/approvals/${approvalId}/approve` });
}

export async function reject(approvalId: string): Promise<Approval> {
  return apiRequest({ method: "POST", url: `/approvals/${approvalId}/reject` });
}

export async function decide(
  approvalId: string,
  payload: { decision: string; approved_by?: string; remarks?: string }
): Promise<Approval> {
  return apiRequest({ method: "POST", url: `/approvals/${approvalId}/decide`, data: payload });
}

export async function getById(approvalId: string): Promise<Approval> {
  return apiRequest({ method: "GET", url: `/approvals/${approvalId}` });
}
