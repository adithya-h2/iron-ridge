import axios, { type AxiosInstance, type AxiosRequestConfig } from "axios";

import { getAuthToken } from "@/lib/auth-storage";
import { ApiRequestError, type ApiResponse } from "@/types/api";

function resolveBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    if (typeof window !== "undefined") {
      console.warn(
        "Warning: NEXT_PUBLIC_API_URL is not configured. Set it in Vercel or .env.local. Falling back to http://localhost:8000 for local development."
      );
    }
    return "http://localhost:8000";
  }
  return url.replace(/\/$/, "");
}

export const apiClient: AxiosInstance = axios.create({
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  if (!config.baseURL) {
    config.baseURL = resolveBaseUrl();
  }
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function apiRequest<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.request<ApiResponse<T>>({
    ...config,
    baseURL: config.baseURL ?? resolveBaseUrl(),
  });
  const payload = response.data;
  if (!payload.success || payload.error) {
    throw new ApiRequestError(
      payload.error ?? { code: "UNKNOWN", message: "Request failed" }
    );
  }
  if (payload.data === null) {
    throw new ApiRequestError({ code: "NO_DATA", message: "Empty response data" });
  }
  return payload.data;
}

export function getApiBaseUrl(): string {
  return resolveBaseUrl();
}
