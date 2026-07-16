import { apiRequest } from "@/services/api";
import type { AuditLog, WorkflowTimeline } from "@/types/domain";
import type { PaginatedResponse } from "@/types/api";

export async function getAuditLogs(
  dealId: string,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<AuditLog>> {
  return apiRequest({
    method: "GET",
    url: "/audit",
    params: { deal_id: dealId, page, page_size: pageSize },
  });
}

export async function getWorkflowTimeline(
  dealId: string,
  page = 1,
  pageSize = 20
): Promise<WorkflowTimeline> {
  return apiRequest({
    method: "GET",
    url: `/api/v1/workflows/${dealId}/timeline`,
    params: { page, page_size: pageSize },
  });
}
