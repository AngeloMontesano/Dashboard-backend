import axios from 'axios';
import { getBaseURL } from './base';

type LoginResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  role?: string;
  user_id?: string;
  tenant_id?: string;
};

export async function authLogin(email: string, password: string) {
  const client = axios.create({
    baseURL: getBaseURL(),
    timeout: 15000,
    headers: { 'Content-Type': 'application/json' }
  });
  const res = await client.post<LoginResponse>('/auth/login', { email, password });
  return res.data;
}
