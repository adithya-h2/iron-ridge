import { apiRequest } from "@/services/api";
import type { LoginCredentials, RegisterPayload, TokenResponse, User } from "@/types/auth";

export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append("username", credentials.username);
  form.append("password", credentials.password);
  const response = await apiRequest<TokenResponse>({
    method: "POST",
    url: "/auth/login",
    data: form,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response;
}

export async function getMe(): Promise<User> {
  return apiRequest<User>({ method: "GET", url: "/auth/me" });
}

export async function register(payload: RegisterPayload): Promise<User> {
  return apiRequest<User>({ method: "POST", url: "/auth/register", data: payload });
}
