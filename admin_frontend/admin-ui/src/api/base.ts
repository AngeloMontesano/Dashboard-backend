// Zentrale URL-Helfer für das Admin-Frontend.
const runtimeHostname = typeof window !== "undefined" ? window.location.hostname : "";
const API_BASE_PATH = "/api";
const DEFAULT_BACKUP_BASE_PATH = "/admin/backups";

export function getBaseURL() {
  return API_BASE_PATH;
}

export function getBaseDomain() {
  return runtimeHostname;
}

export function getBackupBasePath() {
  const envPath = import.meta.env?.VITE_ADMIN_BACKUP_BASE_PATH as string | undefined;
  if (!envPath) return DEFAULT_BACKUP_BASE_PATH;
  const normalized = envPath.startsWith("/") ? envPath : `/${envPath}`;
  return normalized.replace(/^\/api/, "");
}
