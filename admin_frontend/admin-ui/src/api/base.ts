// src/api/base.ts
// Zentrale Definition der Base URL für alle APIs

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export function getBaseURL() {
  return baseURL;
}
