const API_BASE_URL = "/api";
const runtimeHostname = typeof window !== "undefined" ? window.location.hostname : "";

export function getBaseURL() {
  return API_BASE_URL;
}

export function getBaseDomain() {
  return runtimeHostname;
}
