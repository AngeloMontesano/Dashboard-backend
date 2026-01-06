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

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      sessionStorage.removeItem("customer_auth");
      delete api.defaults.headers.common.Authorization;
      const redirect = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/login?redirect=${redirect}`;
      return;
    }
    return Promise.reject(error);
  }
);

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
