import { createContext, useContext, useState, useCallback, useMemo, useEffect, useRef, type ReactNode } from "react";
import { jwtDecode } from "jwt-decode";
import * as authApi from "@/api/auth";
import { setAuthToken, setUnauthorizedHandler } from "@/api/axios";
import type { User } from "@/lib/types";

const STORAGE_KEY = "arogent_session";

interface StoredSession {
  token: string;
  user: User;
}

interface DecodedToken {
  sub: string;
  exp: number; // seconds since epoch
}

interface AuthContextValue {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean; // true only while restoring a session on first mount
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readStoredSession(): StoredSession | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as StoredSession;
  } catch {
    return null;
  }
}

function isTokenExpired(token: string): boolean {
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    return decoded.exp * 1000 <= Date.now();
  } catch {
    return true; // an undecodable token is treated as expired, not trusted
  }
}

function msUntilExpiry(token: string): number {
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    return Math.max(decoded.exp * 1000 - Date.now(), 0);
  } catch {
    return 0;
  }
}

/**
 * Session is persisted to localStorage as {token, user} together. On page
 * load, the token's own exp claim is decoded and checked BEFORE trusting
 * the stored user — an expired token never restores a session, even if
 * the stored user object looks fine.
 *
 * Known limitation, stated plainly rather than glossed over: restoring a
 * session trusts the locally stored user object without re-validating
 * against the server (there's no GET /auth/me endpoint yet — Module 7 is
 * scoped to the existing API, and adding one is a backend change outside
 * that scope). If a user's role changed server-side, a stale local session
 * wouldn't reflect that until next login. Production roadmap: add
 * GET /auth/me and call it on restore instead of trusting local storage.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const logoutTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearLogoutTimer = useCallback(() => {
    if (logoutTimerRef.current) {
      clearTimeout(logoutTimerRef.current);
      logoutTimerRef.current = null;
    }
  }, []);

  const logout = useCallback(() => {
    clearLogoutTimer();
    localStorage.removeItem(STORAGE_KEY);
    setAuthToken(null);
    setUser(null);
  }, [clearLogoutTimer]);

  const scheduleAutoLogout = useCallback(
    (token: string) => {
      clearLogoutTimer();
      const delay = msUntilExpiry(token);
      logoutTimerRef.current = setTimeout(() => {
        logout();
      }, delay);
    },
    [clearLogoutTimer, logout]
  );

  const login = useCallback(
    async (username: string, password: string) => {
      const result = await authApi.login({ username, password });
      const session: StoredSession = { token: result.access_token, user: result.user };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
      setAuthToken(result.access_token);
      setUser(result.user);
      scheduleAutoLogout(result.access_token);
    },
    [scheduleAutoLogout]
  );

  // Restore session on first mount
  useEffect(() => {
    const stored = readStoredSession();
    if (stored && !isTokenExpired(stored.token)) {
      setAuthToken(stored.token);
      setUser(stored.user);
      scheduleAutoLogout(stored.token);
    } else if (stored) {
      // Stale/expired session left over from a previous visit — clear it
      // rather than leaving dead data in storage.
      localStorage.removeItem(STORAGE_KEY);
    }
    setIsLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Register the 401 handler once — axios.ts calls this on any 401 response,
  // independent of the client-side expiry timer above (see axios.ts's comment).
  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, [logout]);

  useEffect(() => clearLogoutTimer, [clearLogoutTimer]);

  const value = useMemo<AuthContextValue>(
    () => ({ user, login, logout, isAuthenticated: user !== null, isLoading }),
    [user, login, logout, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
