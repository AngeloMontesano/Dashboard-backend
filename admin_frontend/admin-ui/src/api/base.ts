// Zentrale URL-Helfer für das Admin-Frontend.
import { getBaseURL as sharedGetBaseURL } from "@shared/api-client";

const runtimeHostname = typeof window !== "undefined" ? window.location.hostname : "";

export function getBaseURL() {
  return sharedGetBaseURL();
}

export function getBaseDomain() {
  return runtimeHostname;
}
