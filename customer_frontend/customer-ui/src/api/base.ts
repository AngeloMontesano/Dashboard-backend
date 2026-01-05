const API_BASE_URL = "/api";
const runtimeHost = typeof window !== "undefined" ? window.location.host : "";
const runtimeHostname = typeof window !== "undefined" ? window.location.hostname : "";

const envTenantSlug = (import.meta.env.VITE_TENANT_SLUG || "").trim();
const envTenantHost = (import.meta.env.VITE_TENANT_HOST || "").trim();
const allowRuntimeTenant = (import.meta.env.VITE_ALLOW_RUNTIME_TENANT || "true").toLowerCase() === "true";

export function getBaseURL(): string {
  return API_BASE_URL;
}

export function getTenantHost(): string | null {
  if (allowRuntimeTenant && runtimeHost) return runtimeHost;
  if (envTenantHost) return envTenantHost;
  return null;
}

export function getTenantSlug(): string {
  if (allowRuntimeTenant && runtimeHostname) {
    const slug = runtimeHostname.split(":")[0]?.split(".")[0];
    if (slug) return slug;
  }
  return envTenantSlug;
}

export function getTenantHeaders(): Record<string, string> {
  const tenantHost = getTenantHost();
  const slug = getTenantSlug();

  const headers: Record<string, string> = {};
  if (tenantHost) headers["X-Forwarded-Host"] = tenantHost;
  if (slug) headers["X-Tenant-Slug"] = slug;
  return headers;
}
