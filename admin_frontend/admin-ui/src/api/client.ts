import { createApiClient } from "@shared/api-client";

/*
  Zentraler API Client.
  Admin Key niemals loggen.
*/

export function apiClient(adminKey: string, actor?: string) {
  return createApiClient({
    timeout: 15000,
    extraHeaders: {
      "X-Admin-Key": adminKey,
      ...(actor ? { "X-Admin-Actor": actor } : {})
    }
  });
}
