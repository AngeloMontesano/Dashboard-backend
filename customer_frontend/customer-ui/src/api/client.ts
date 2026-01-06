import axios from "axios";
import { getBaseURL, getTenantHeaders } from "./base";

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 20000,
});

api.defaults.headers.common = {
  ...api.defaults.headers.common,
  "Content-Type": "application/json",
  ...getTenantHeaders(),
};

const STORAGE_KEY = "customer_auth";
type StoredAuth = {
  accessToken?: string;
  refreshToken?: string;
  role?: string;
  email?: string;
  tenantId?: string;
  userId?: string;
};

let refreshPromise: Promise<string | null> | null = null;
type RefreshEvent = {
  status: "success" | "failed";
  reason?: string;
  at: string;
};

function readRefreshLog(): RefreshEvent[] {
  if (typeof sessionStorage === "undefined") return [];
  try {
    const raw = sessionStorage.getItem("customer_auth_refresh_log");
    if (!raw) return [];
    return JSON.parse(raw) as RefreshEvent[];
  } catch {
    return [];
  }
}

function recordRefreshEvent(event: Omit<RefreshEvent, "at">) {
  if (typeof sessionStorage === "undefined") return;
  const next: RefreshEvent = { ...event, at: new Date().toISOString() };
  const log = [...readRefreshLog(), next].slice(-10);
  try {
    sessionStorage.setItem("customer_auth_refresh_log", JSON.stringify(log));
  } catch {
    // ignore storage issues
  }
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("customer-auth-refresh", { detail: next }));
  }
}

function readStoredAuth(): StoredAuth | null {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
}

function persistAuth(update: StoredAuth) {
  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      accessToken: update.accessToken || "",
      refreshToken: update.refreshToken || "",
      role: update.role || "",
      email: update.email || "",
      tenantId: update.tenantId || "",
      userId: update.userId || ""
    })
  );
  window.dispatchEvent(new Event("customer-auth-updated"));
}

function clearAuthAndRedirect() {
  sessionStorage.removeItem(STORAGE_KEY);
  delete api.defaults.headers.common.Authorization;
  const redirect = encodeURIComponent(window.location.pathname + window.location.search);
  window.location.href = `/login?redirect=${redirect}`;
}

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  const stored = readStoredAuth();
  if (!stored?.refreshToken) return null;

  refreshPromise = (async () => {
    try {
      const res = await axios.post(
        `${getBaseURL()}/auth/refresh`,
        { refresh_token: stored.refreshToken },
        {
          timeout: 12000,
          headers: {
            "Content-Type": "application/json",
            ...getTenantHeaders()
          }
        }
      );
      const data = res.data as { access_token: string; refresh_token?: string; role?: string; tenant_id?: string; user_id?: string };
      const accessToken = data.access_token;
      const refreshToken = data.refresh_token || stored.refreshToken;
      persistAuth({
        accessToken,
        refreshToken,
        role: data.role || stored.role,
        email: stored.email,
        tenantId: data.tenant_id || stored.tenantId,
        userId: data.user_id || stored.userId
      });
      setAuthToken(accessToken);
      recordRefreshEvent({ status: "success" });
      return accessToken;
    } catch (err: any) {
      recordRefreshEvent({ status: "failed", reason: err?.message || "refresh_failed" });
      clearAuthAndRedirect();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const originalConfig = error?.config || {};
    const shouldRefresh = (status === 401 || status === 403) && !originalConfig._retry && !originalConfig.skipAuthRefresh;

    if (shouldRefresh) {
      originalConfig._retry = true;
      const newToken = await refreshAccessToken();
      if (newToken) {
        originalConfig.headers = {
          ...originalConfig.headers,
          Authorization: `Bearer ${newToken}`
        };
        return api(originalConfig);
      }
    }

    if (status === 401 && !originalConfig.skipAuthRefresh) {
      recordRefreshEvent({ status: "failed", reason: "unauthorized_after_retry" });
      clearAuthAndRedirect();
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export function authHeaders(token?: string) {
  return token ? { Authorization: `Bearer ${token}` } : undefined;
}

export function getAuthRefreshLog(): RefreshEvent[] {
  return readRefreshLog();
}
