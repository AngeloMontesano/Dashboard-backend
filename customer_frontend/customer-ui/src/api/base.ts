const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";
const apiSubdomain = import.meta.env.VITE_API_SUBDOMAIN || "api";
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || "https";
const apiHost = import.meta.env.VITE_API_HOST || "";
const apiPort = import.meta.env.VITE_API_PORT || "";
const tenantSlug = import.meta.env.VITE_TENANT_SLUG || "";
const explicitApiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE;
// Default to the dedicated API host (api.<baseDomain>). Opt-in to the runtime host via VITE_ALLOW_RUNTIME_HOST=true.
const allowRuntimeHost = (import.meta.env.VITE_ALLOW_RUNTIME_HOST || "false").toLowerCase() === "true";
// Backend serves routes at the root (e.g. /auth/login, /inventory/items). Prefix can still be added via env if needed.
const apiPrefix = normalizePrefix(import.meta.env.VITE_API_PREFIX ?? "");

const runtimeHost = typeof window !== "undefined" ? window.location.hostname : "";
const runtimeProtocol = typeof window !== "undefined" ? window.location.protocol.replace(":", "") : "";
const runtimePort = typeof window !== "undefined" ? window.location.port : "";

function normalizePrefix(prefix: string | undefined | null): string {
  if (!prefix) return "";
  const trimmed = prefix.trim();
  if (!trimmed || trimmed === "/") return "";
  const withLeading = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
  return withLeading.replace(/\/+$/, "");
}

function replaceHost(url: string, host: string): string | null {
  try {
    const parsed = new URL(url);
    parsed.host = host;
    return parsed.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

function applyPrefix(url: string): string {
  const sanitized = url.replace(/\/+$/, "");
  if (!apiPrefix) return sanitized;
  return `${sanitized}${apiPrefix}`;
}

export function getBaseURL(): string {
  // If an explicit base is set, use it unless runtime-host overriding is explicitly allowed.
  if (explicitApiBase) {
    if (allowRuntimeHost && baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
      const adjusted = replaceHost(explicitApiBase, runtimeHost + (runtimePort ? `:${runtimePort}` : ""));
      if (adjusted) return applyPrefix(adjusted);
    }
    return applyPrefix(explicitApiBase);
  }
  if (apiHost) {
    const portPart = apiPort ? `:${apiPort}` : "";
    return applyPrefix(`${apiProtocol}://${apiHost}${portPart}`);
  }
  // Prefer the current host if it already matches the base domain (keeps tenant slug)
  if (allowRuntimeHost && baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
    const portPart = runtimePort ? `:${runtimePort}` : "";
    const protocol = runtimeProtocol || apiProtocol;
    return applyPrefix(`${protocol}://${runtimeHost}${portPart}`);
  }

  // If a tenant slug is provided via env, build `<slug>.<baseDomain>`
  if (tenantSlug && baseDomain) {
    return applyPrefix(`${apiProtocol}://${tenantSlug}.${baseDomain}`);
  }

  // Fallback: shared api subdomain
  return applyPrefix(`${apiProtocol}://${apiSubdomain}.${baseDomain}`);
}

export function getTenantHost(): string | null {
  // Prefer the runtime host when it already contains the tenant slug.
  if (baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
    return runtimeHost + (runtimePort ? `:${runtimePort}` : "");
  }
  // Fallback: build host from env slug
  if (tenantSlug && baseDomain) {
    const portPart = apiPort ? `:${apiPort}` : "";
    return `${tenantSlug}.${baseDomain}${portPart}`;
  }
  return null;
}

export function getTenantSlug(): string {
  const tenantHost = getTenantHost();
  const slugFromHost = tenantHost ? tenantHost.split(":")[0]?.split(".")[0] : "";
  return slugFromHost || tenantSlug || "";
}

export function getTenantHeaders(): Record<string, string> {
  const tenantHost = getTenantHost();
  const slug = getTenantSlug();

  const headers: Record<string, string> = {};
  if (tenantHost) headers["X-Forwarded-Host"] = tenantHost;
  if (slug) headers["X-Tenant-Slug"] = slug;
  return headers;
}

// Helpful console output for debugging connectivity
if (typeof console !== "undefined") {
  console.info(
    "[api] resolved base URL",
    getBaseURL(),
    {
      explicitApiBase,
      apiHost,
      apiPort,
      apiProtocol,
      apiSubdomain,
      baseDomain,
      tenantSlug,
      runtimeHost,
      runtimeProtocol,
      runtimePort,
      allowRuntimeHost,
      apiPrefix,
    }
  );
}
