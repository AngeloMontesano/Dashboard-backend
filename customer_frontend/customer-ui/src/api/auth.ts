import axios from 'axios';
import { getBaseURL, getTenantHeaders, getTenantSlug } from './base';

type LoginResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  role?: string;
  user_id?: string;
  tenant_id?: string;
};

export async function authLogin(email: string, password: string) {
  const baseURL = getBaseURL();
  const tenantSlug = getTenantSlug();
  const client = axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
      ...getTenantHeaders()
    }
  });
  try {
    const res = await client.post<LoginResponse>('/auth/login', { email, password });
    return res.data;
  } catch (err: any) {
    if (err?.code === 'ECONNABORTED') {
      err.message = `Login Timeout (API ${baseURL})`;
    } else if (err?.message === 'Network Error') {
      err.message = `Network Error (API ${baseURL})`;
    }
    throw err;
  }
}
