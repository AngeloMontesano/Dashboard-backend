// src/api/base.ts
// Zentrale Definitionen für API und Domains (Env-gesteuert)

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";

export function getBaseURL() {
  return baseURL;
}

export function getBaseDomain() {
  return baseDomain;
}
