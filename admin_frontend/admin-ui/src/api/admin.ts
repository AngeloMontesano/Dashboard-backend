import type { components, paths } from "./gen/openapi";
import type {
  TenantOut,
  TenantCreate,
  TenantUpdate,
  UserOut,
  UserCreate,
  UserUpdate,
  MembershipOut,
  MembershipCreate,
  MembershipUpdate,
  AuditOut,
  AuditFilters,
  DiagnosticsOut,
  TenantUserCreate,
  TenantUserUpdate,
  TenantUserOut,
  TenantUserApiOut,
} from "../types";
import { adminHeaders, api } from "./client";

/*
  Admin API Wrapper
  - alle Calls setzen X-Admin-Key und optional X-Admin-Actor
*/

type TenantListResponse = paths["/admin/tenants"]["get"]["responses"]["200"]["content"]["application/json"];
type UserListResponse = paths["/admin/users"]["get"]["responses"]["200"]["content"]["application/json"];
type MembershipsByTenantResponse =
  paths["/admin/memberships/tenant/{tenant_id}"]["get"]["responses"]["200"]["content"]["application/json"];
type MembershipsByUserResponse =
  paths["/admin/memberships/user/{user_id}"]["get"]["responses"]["200"]["content"]["application/json"];
type RolesResponse = paths["/admin/roles"]["get"]["responses"]["200"]["content"]["application/json"];
type AuditResponse = paths["/admin/audit"]["get"]["responses"]["200"]["content"]["application/json"];
type DiagnosticsResponse = paths["/admin/diagnostics"]["get"]["responses"]["200"]["content"]["application/json"];
type TenantUserListResponse =
  paths["/admin/tenants/{tenant_id}/users"]["get"]["responses"]["200"]["content"]["application/json"];

type AdminLoginPayload = components["schemas"]["AdminCredentialLogin"];
type TenantUserCreatePayload = components["schemas"]["TenantUserCreate"];
type TenantUserUpdatePayload = components["schemas"]["TenantUserUpdate"];

type AdminLoginResponse = { admin_key: string; actor?: string };

function withAdmin(adminKey: string, actor?: string) {
  return { headers: adminHeaders(adminKey, actor) };
}

function mapTenantUser(tenantId: string, user: TenantUserApiOut): TenantUserOut {
  return {
    id: user.membership_id || user.user_id,
    tenant_id: tenantId,
    user_id: user.user_id,
    email: user.email,
    role: user.role,
    is_active: user.membership_is_active ?? user.user_is_active ?? false,
  };
}

export async function adminPing(adminKey: string, actor?: string) {
  const res = await api.get<Record<string, unknown>>("/admin/ping", withAdmin(adminKey, actor));
  return res.data;
}

export async function adminLoginWithCredentials(email: string, password: string) {
  const payload: AdminLoginPayload = { email, password };
  const res = await api.post<AdminLoginResponse>("/admin/login", payload, { timeout: 15000 });
  return res.data;
}

/* Tenants */
export async function adminListTenants(
  adminKey: string,
  actor?: string,
  params?: { q?: string; limit?: number; offset?: number }
) {
  const res = await api.get<TenantListResponse>("/admin/tenants", { ...withAdmin(adminKey, actor), params });
  return res.data as TenantOut[];
}

export async function adminCreateTenant(adminKey: string, actor?: string, payload: TenantCreate) {
  const res = await api.post<TenantOut>("/admin/tenants", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminUpdateTenant(adminKey: string, actor: string | undefined, tenantId: string, payload: TenantUpdate) {
  const res = await api.patch<TenantOut>(`/admin/tenants/${tenantId}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminDeleteTenant(adminKey: string, actor: string | undefined, tenantId: string) {
  await api.delete(`/admin/tenants/${tenantId}`, { ...withAdmin(adminKey, actor), params: { confirm: true } });
  return true;
}

/* Users */
export async function adminListUsers(adminKey: string, actor?: string) {
  const res = await api.get<UserListResponse>("/admin/users", withAdmin(adminKey, actor));
  return res.data as UserOut[];
}

export async function adminCreateUser(adminKey: string, actor: string | undefined, payload: UserCreate) {
  const res = await api.post<UserOut>("/admin/users", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminUpdateUser(adminKey: string, actor: string | undefined, userId: string, payload: UserUpdate) {
  const res = await api.patch<UserOut>(`/admin/users/${userId}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

/* Tenant Users (combined user + membership for a tenant) */
export async function adminListTenantUsers(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  params?: { q?: string; limit?: number; offset?: number }
) {
  const res = await api.get<TenantUserListResponse>(`/admin/tenants/${tenantId}/users`, {
    ...withAdmin(adminKey, actor),
    params,
  });
  const data = res.data || [];
  return (data as TenantUserApiOut[]).map((u) => mapTenantUser(tenantId, u));
}

export async function adminCreateTenantUser(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  payload: TenantUserCreate
) {
  const body: TenantUserCreatePayload = {
    email: payload.email,
    role: payload.role,
    password: payload.password ?? null,
    user_is_active: payload.is_active ?? true,
    membership_is_active: payload.is_active ?? true,
  };
  const res = await api.post<TenantUserApiOut>(`/admin/tenants/${tenantId}/users`, body, withAdmin(adminKey, actor));
  return mapTenantUser(tenantId, res.data);
}

export async function adminUpdateTenantUser(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  membershipId: string,
  payload: TenantUserUpdate
) {
  const body: TenantUserUpdatePayload = {
    role: payload.role ?? null,
    password: payload.password ?? null,
    user_is_active: payload.is_active ?? null,
    membership_is_active: payload.is_active ?? null,
  };
  const res = await api.patch<TenantUserApiOut>(
    `/admin/tenants/${tenantId}/users/${membershipId}`,
    body,
    withAdmin(adminKey, actor)
  );
  return mapTenantUser(tenantId, res.data);
}

export async function adminDeleteTenantUser(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  membershipId: string
) {
  await api.delete(`/admin/tenants/${tenantId}/users/${membershipId}`, withAdmin(adminKey, actor));
  return true;
}

export async function adminSetTenantUserPassword(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  userId: string,
  password: string
) {
  const res = await api.post<TenantUserApiOut>(
    `/admin/tenants/${tenantId}/users/${userId}/set-password`,
    { password },
    withAdmin(adminKey, actor)
  );
  return mapTenantUser(tenantId, res.data);
}

/* Memberships */
export async function adminMembershipsByTenant(adminKey: string, actor: string | undefined, tenantId: string) {
  const res = await api.get<MembershipsByTenantResponse>(
    `/admin/memberships/tenant/${tenantId}`,
    withAdmin(adminKey, actor)
  );
  return res.data as MembershipOut[];
}

export async function adminMembershipsByUser(adminKey: string, actor: string | undefined, userId: string) {
  const res = await api.get<MembershipsByUserResponse>(`/admin/memberships/user/${userId}`, withAdmin(adminKey, actor));
  return res.data as MembershipOut[];
}

export async function adminCreateMembership(adminKey: string, actor: string | undefined, payload: MembershipCreate) {
  const res = await api.post<MembershipOut>("/admin/memberships", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminUpdateMembership(
  adminKey: string,
  actor: string | undefined,
  membershipId: string,
  payload: MembershipUpdate
) {
  const res = await api.patch<MembershipOut>(`/admin/memberships/${membershipId}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

/* Roles */
export async function adminRoles(adminKey: string, actor?: string) {
  const res = await api.get<RolesResponse>("/admin/roles", withAdmin(adminKey, actor));
  return res.data as string[];
}

/* Diagnostics */
export async function adminDiagnostics(adminKey: string, actor?: string) {
  const res = await api.get<DiagnosticsResponse>("/admin/diagnostics", withAdmin(adminKey, actor));
  return (res.data as DiagnosticsOut) || {};
}

/* Audit */
export async function adminGetAudit(adminKey: string, actor: string | undefined, filters: AuditFilters = {}) {
  const params: Record<string, unknown> = {};
  if (filters.actor) params.actor = filters.actor;
  if (filters.action) params.action = filters.action;
  if (filters.entity_type) params.entity_type = filters.entity_type;
  if (filters.entity_id) params.entity_id = filters.entity_id;
  if (filters.created_from) params.created_from = filters.created_from;
  if (filters.created_to) params.created_to = filters.created_to;

  params.limit = typeof filters.limit === "number" ? filters.limit : 100;
  params.offset = typeof filters.offset === "number" ? filters.offset : 0;

  const res = await api.get<AuditResponse>("/admin/audit", { ...withAdmin(adminKey, actor), params });
  return res.data as AuditOut[];
}
