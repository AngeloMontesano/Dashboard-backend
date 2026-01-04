const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";
const apiSubdomain = import.meta.env.VITE_API_SUBDOMAIN || "api";
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || "https";
const apiHost = import.meta.env.VITE_API_HOST || "";
const apiPort = import.meta.env.VITE_API_PORT || "";
const tenantSlug = import.meta.env.VITE_TENANT_SLUG || "";
const explicitApiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE;

const runtimeHost = typeof window !== "undefined" ? window.location.hostname : "";
const runtimeProtocol = typeof window !== "undefined" ? window.location.protocol.replace(":", "") : "";
const runtimePort = typeof window !== "undefined" ? window.location.port : "";

export function getBaseURL(): string {
  if (explicitApiBase) return explicitApiBase;
  if (apiHost) {
    const portPart = apiPort ? `:${apiPort}` : "";
    return `${apiProtocol}://${apiHost}${portPart}`;
  }
  // Prefer the current host if it already matches the base domain (keeps tenant slug)
  if (baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
    const portPart = runtimePort ? `:${runtimePort}` : "";
    const protocol = runtimeProtocol || apiProtocol;
    return `${protocol}://${runtimeHost}${portPart}`;
  }

  // If a tenant slug is provided via env, build `<slug>.<baseDomain>`
  if (tenantSlug && baseDomain) {
    return `${apiProtocol}://${tenantSlug}.${baseDomain}`;
  }

  // Fallback: shared api subdomain
  return `${apiProtocol}://${apiSubdomain}.${baseDomain}`;
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
    }
  );
}
