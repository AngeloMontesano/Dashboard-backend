import axios from "axios";
import { getBaseURL } from "./base";

/*
  Zentraler API Client.
  Admin Key niemals loggen.
*/

export function apiClient(adminKey: string, actor?: string) {
  const baseURL = getBaseURL();

  return axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      "X-Admin-Key": adminKey,
      ...(actor ? { "X-Admin-Actor": actor } : {}),
      "Content-Type": "application/json",
    },
  });
}
