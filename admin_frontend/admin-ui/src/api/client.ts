import { createApiClient } from "@shared/api-client";

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
});

export function apiClient(adminKey: string, actor?: string) {
  return createApiClient({
    timeout: 15000,
    extraHeaders: {
      "X-Admin-Key": adminKey,
      ...(actor ? { "X-Admin-Actor": actor } : {})
    }
  });
}
