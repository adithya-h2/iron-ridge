import { apiRequest } from "@/services/api";
import type { Order } from "@/types/domain";
import type { PaginatedResponse } from "@/types/api";

export async function list(page = 1, pageSize = 20): Promise<PaginatedResponse<Order>> {
  return apiRequest({
    method: "GET",
    url: "/orders",
    params: { page, page_size: pageSize },
  });
}

export async function getById(orderId: string): Promise<Order> {
  return apiRequest({ method: "GET", url: `/orders/${orderId}` });
}
