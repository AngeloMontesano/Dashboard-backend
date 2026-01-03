// src/types.ts

export type TenantOut = { id: string; slug: string; name: string; is_active: boolean };
export type TenantCreate = { slug: string; name: string };
export type TenantUpdate = { name?: string; is_active?: boolean };

export type UserOut = { id: string; email: string; is_active: boolean; has_password: boolean };
export type UserCreate = { email: string; password?: string | null };
export type UserUpdate = { is_active?: boolean | null; password?: string | null };

export type MembershipOut = {
  id: string;
  user_id: string;
  tenant_id: string;
  role: string;
  is_active: boolean;
};
export type MembershipCreate = { user_id: string; tenant_id: string; role: string };
export type MembershipUpdate = { role?: string | null; is_active?: boolean | null };

export type DiagnosticsOut = {
  duplicate_memberships: unknown[];
  memberships_without_user: unknown[];
  memberships_without_tenant: unknown[];
  inactive_tenant_with_active_memberships: unknown[];
};

export type AuditOut = {
  id: string;
  actor: string;
  action: string;
  entity_type: string;
  entity_id: string;
  payload: Record<string, unknown>;
  created_at: string; // ISO date-time
};

export type AuditFilters = {
  actor?: string;
  action?: string;
  entity_type?: string;
  entity_id?: string;
  created_from?: string; // ISO date-time
  created_to?: string;   // ISO date-time
  limit?: number;
  offset?: number;
};
