import axios from "axios";
import { getBaseURL } from "./base";

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
});

api.defaults.headers.common["Content-Type"] = "application/json";

export function adminHeaders(adminKey: string, actor?: string) {
  return {
    "X-Admin-Key": adminKey,
    ...(actor ? { "X-Admin-Actor": actor } : {}),
  };
}
