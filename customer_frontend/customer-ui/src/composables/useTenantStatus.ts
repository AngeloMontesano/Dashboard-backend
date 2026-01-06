import { ref, readonly, type Ref } from 'vue';
import { api } from '@/api/client';
import { getTenantHeaders } from '@/api/base';

export type TenantStatusValue = {
  status: 'ok' | 'not_found' | 'inactive' | 'unavailable';
  slug?: string | null;
  host?: string | null;
  tenant_id?: string | null;
  is_active?: boolean | null;
  reason?: string | null;
};

const tenantStatus: Ref<TenantStatusValue | null> = ref(null);

export function useTenantStatus() {
  return readonly(tenantStatus);
}

export async function initTenantStatus(): Promise<TenantStatusValue> {
  if (tenantStatus.value) return tenantStatus.value;

  try {
    const res = await api.get<TenantStatusValue>('/public/tenant-status', {
      headers: getTenantHeaders(),
      timeout: 8000,
      // keine Auth-Refresh-Versuche für public Endpoint
      // @ts-expect-error - Axios Config Erkennung für Custom Flag
      skipAuthRefresh: true
    });
    tenantStatus.value = res.data;
  } catch (err: any) {
    tenantStatus.value = {
      status: 'unavailable',
      reason: err?.message || 'unavailable'
    };
  }

  return tenantStatus.value!;
}
