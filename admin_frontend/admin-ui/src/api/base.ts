// src/api/base.ts
// Zentrale Definitionen für API und Domains (Env-gesteuert)

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";
const apiSubdomain = import.meta.env.VITE_API_SUBDOMAIN || "api";
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || "https";
const explicitApiBase = import.meta.env.VITE_API_BASE;

export function getBaseURL() {
  if (explicitApiBase) return explicitApiBase;
  return `${apiProtocol}://${apiSubdomain}.${baseDomain}`;
}

export function getBaseDomain() {
  return baseDomain;
}
