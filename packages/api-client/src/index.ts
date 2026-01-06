// Gemeinsame API-Helfer ohne eigene Axios-Instanz.

const API_BASE_PATH = "/api";

function resolveRuntimeHost() {
  if (typeof window === "undefined") return "";
  return window.location.host || "";
}

function resolveRuntimeHostname() {
  if (typeof window === "undefined") return "";
  return window.location.hostname || "";
}

export function getBaseURL(): string {
  return API_BASE_PATH;
}

export function getTenantSlug(): string {
  const envSlug = (import.meta.env.VITE_TENANT_SLUG || "").trim();
  if (envSlug) return envSlug;

  const hostname = resolveRuntimeHostname();
  const parts = hostname.split(".");
  if (parts.length > 2) return parts[0] || "";

  return "";
}

export function getTenantHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  const runtimeHost = resolveRuntimeHost();
  const slug = getTenantSlug();

  if (runtimeHost) headers["X-Forwarded-Host"] = runtimeHost;
  if (slug) headers["X-Tenant-Slug"] = slug;

  return headers;
}
