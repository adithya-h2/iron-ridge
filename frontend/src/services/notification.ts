import { apiRequest } from "@/services/api";
import type { NotificationPayload, NotificationResult } from "@/types/domain";

export async function send(payload: NotificationPayload): Promise<NotificationResult> {
  return apiRequest({ method: "POST", url: "/api/v1/notifications", data: payload });
}
