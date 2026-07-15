import { axiosInstance } from "./axios";
import type { AuthToken, User } from "@/lib/types";
import type { UserRole } from "@/lib/constants";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  username: string;
  password: string;
  role: UserRole;
  assigned_village?: string | null;
}

export async function login(payload: LoginPayload): Promise<AuthToken> {
  const form = new URLSearchParams({ username: payload.username, password: payload.password });
  const response = await axiosInstance.post<AuthToken>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<User> {
  const response = await axiosInstance.post<User>("/auth/register", payload);
  return response.data;
}
