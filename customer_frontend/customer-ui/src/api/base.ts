const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";
const apiSubdomain = import.meta.env.VITE_API_SUBDOMAIN || "api";
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || "https";
const apiHost = import.meta.env.VITE_API_HOST || "";
const apiPort = import.meta.env.VITE_API_PORT || "";
const explicitApiBase = import.meta.env.VITE_API_BASE_URL;

export function getBaseURL(): string {
  if (explicitApiBase) return explicitApiBase;
  if (apiHost) {
    const portPart = apiPort ? `:${apiPort}` : "";
    return `${apiProtocol}://${apiHost}${portPart}`;
  }
  return `${apiProtocol}://${apiSubdomain}.${baseDomain}`;
}
