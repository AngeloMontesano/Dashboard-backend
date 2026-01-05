// Zentrale URL-Helfer für das Admin-Frontend.
const runtimeHostname = typeof window !== "undefined" ? window.location.hostname : "";
const API_BASE_PATH = "/api";

export function getBaseURL() {
  return API_BASE_PATH;
}

export function getBaseDomain() {
  return runtimeHostname;
}
