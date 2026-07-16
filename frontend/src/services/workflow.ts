import { apiRequest } from "@/services/api";
import type { WorkflowStatus, WorkflowTimeline } from "@/types/domain";

export async function getStatus(dealId: string): Promise<WorkflowStatus> {
  return apiRequest({ method: "GET", url: `/api/v1/workflows/${dealId}` });
}

export async function getTimeline(
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

export async function recordRetry(dealId: string): Promise<{ deal_id: string; recorded: boolean }> {
  return apiRequest({ method: "POST", url: `/api/v1/workflows/${dealId}/retry` });
}
