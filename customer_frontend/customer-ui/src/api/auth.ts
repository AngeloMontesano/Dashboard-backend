import { api } from './client';
import { getBaseURL, getTenantHeaders } from './base';

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
  try {
    const res = await api.post<LoginResponse>(
      '/auth/login',
      { email, password },
      {
        timeout: 15000,
        headers: getTenantHeaders()
      }
    );
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
