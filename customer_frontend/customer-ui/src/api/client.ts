import axios from "axios";
import { getBaseURL, getTenantHeaders } from "./base";

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 20000,
});

api.defaults.headers.common = {
  ...api.defaults.headers.common,
  "Content-Type": "application/json",
  ...getTenantHeaders(),
};

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export function authHeaders(token?: string) {
  return token ? { Authorization: `Bearer ${token}` } : undefined;
}
