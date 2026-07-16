import { apiRequest } from "@/services/api";
import type { LeadIntakePayload, LeadIntakeResult } from "@/types/domain";

export async function createLead(payload: LeadIntakePayload): Promise<LeadIntakeResult> {
  return apiRequest({ method: "POST", url: "/api/v1/leads", data: payload });
}
