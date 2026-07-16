export interface User {
  user_id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  role?: string;
}

export type UserRole = "admin" | "sales" | "manager" | "agent";
