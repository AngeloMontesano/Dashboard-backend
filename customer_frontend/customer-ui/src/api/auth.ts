import { api } from "./client";
import { getBaseURL, getTenantHeaders } from "./base";
import type { components } from "./gen/openapi";

type LoginResponse = components["schemas"]["TokenResponse"];
type RefreshRequest = components["schemas"]["RefreshRequest"];

export async function authLogin(email: string, password: string) {
  const baseURL = getBaseURL();
  try {
    const res = await api.post<LoginResponse>(
      "/auth/login",
      { email, password },
      {
        timeout: 15000,
        headers: getTenantHeaders(),
      }
    );
    return res.data;
  } catch (err: any) {
    if (err?.code === "ECONNABORTED") {
      err.message = `Login Timeout (API ${baseURL})`;
    } else if (err?.message === "Network Error") {
      err.message = `Network Error (API ${baseURL})`;
    }
    throw err;
  }
}

export async function authRefresh(body: RefreshRequest) {
  const res = await api.post<LoginResponse>(
    "/auth/refresh",
    body,
    {
      timeout: 12000,
      headers: getTenantHeaders(),
      // avoid interceptor re-trigger for refresh
      skipAuthRefresh: true,
    } as any
  );
  return res.data;
}
