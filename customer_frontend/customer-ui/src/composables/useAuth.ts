import { reactive } from 'vue';
import { authLogin } from '@/api/auth';

type AuthState = {
  accessToken: string;
  refreshToken: string;
  role: string;
  email: string;
  tenantId: string;
  userId: string;
  loading: boolean;
};

const state = reactive<AuthState>({
  accessToken: '',
  refreshToken: '',
  role: '',
  email: '',
  tenantId: '',
  userId: '',
  loading: false
});

const STORAGE_KEY = 'customer_auth';

function persist() {
  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      accessToken: state.accessToken,
      refreshToken: state.refreshToken,
      role: state.role,
      email: state.email,
      tenantId: state.tenantId,
      userId: state.userId
    })
  );
}

function restore() {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    const parsed = JSON.parse(raw);
    state.accessToken = parsed.accessToken || '';
    state.refreshToken = parsed.refreshToken || '';
    state.role = parsed.role || '';
    state.email = parsed.email || '';
    state.tenantId = parsed.tenantId || '';
    state.userId = parsed.userId || '';
  } catch {
    // ignore parse errors
  }
}

restore();

export function useAuth() {
  async function login(email: string, password: string) {
    state.loading = true;
    try {
      const res = await authLogin(email, password);
      state.accessToken = res.access_token;
      state.refreshToken = res.refresh_token;
      state.role = res.role || '';
      state.email = email;
      state.tenantId = res.tenant_id || '';
      state.userId = res.user_id || '';
      persist();
    } finally {
      state.loading = false;
    }
  }

  function logout() {
    state.accessToken = '';
    state.refreshToken = '';
    state.role = '';
    state.email = '';
    state.tenantId = '';
    state.userId = '';
    sessionStorage.removeItem(STORAGE_KEY);
  }

  function isAuthenticated() {
    return Boolean(state.accessToken);
  }

  return {
    state,
    login,
    logout,
    isAuthenticated
  };
}
