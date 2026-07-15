import axios, { AxiosError } from "axios";

// Configurable via VITE_API_BASE_URL (e.g. in a deployed .env or Vercel's
// environment variable settings). Falls back to the local backend's default
// address so `npm run dev` works out of the box with no setup required.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export const axiosInstance = axios.create({
  baseURL: API_BASE,
});

/**
 * There's no direct import from hooks/useAuth.tsx here on purpose — axios.ts
 * has no business importing React context. Instead, AuthProvider registers
 * a callback on mount via setUnauthorizedHandler; the interceptor calls it
 * if present. This keeps the API layer framework-agnostic and avoids a
 * circular import between api/axios.ts and hooks/useAuth.tsx.
 */
let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  unauthorizedHandler = handler;
}

export function setAuthToken(token: string | null) {
  if (token) {
    axiosInstance.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete axiosInstance.defaults.headers.common.Authorization;
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      // Belt-and-suspenders: useAuth also proactively logs out at the
      // token's own exp claim, but a 401 means the SERVER considers the
      // session invalid right now (revoked, clock skew, etc.) — always
      // trust that over client-side expiry tracking.
      unauthorizedHandler?.();
    }

    const status = error.response?.status ?? 0;
    const detail = error.response?.data?.detail ?? error.message ?? "Network error — please check your connection.";
    return Promise.reject(new ApiError(status, detail));
  }
);
