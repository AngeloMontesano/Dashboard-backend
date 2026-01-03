// src/api/admin.ts
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
} from "../types";

import { apiClient } from "./client";

/*
  Admin API Wrapper
  - alle Calls setzen X-Admin-Key und optional X-Admin-Actor
*/

export async function adminPing(adminKey: string, actor?: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get("/admin/ping");
  return res.data as Record<string, unknown>;
}

/* Tenants */
export async function adminListTenants(
  adminKey: string,
  actor?: string,
  params?: { q?: string; limit?: number; offset?: number }
) {
  const api = apiClient(adminKey, actor);
  const res = await api.get("/admin/tenants", { params });
  return res.data as TenantOut[];
}

export async function adminCreateTenant(adminKey: string, actor?: string, payload: TenantCreate) {
  const api = apiClient(adminKey, actor);
  const res = await api.post("/admin/tenants", payload);
  return res.data as TenantOut;
}

export async function adminUpdateTenant(adminKey: string, actor?: string, tenantId: string, payload: TenantUpdate) {
  const api = apiClient(adminKey, actor);
  const res = await api.patch(`/admin/tenants/${tenantId}`, payload);
  return res.data as TenantOut;
}

export async function adminDeleteTenant(adminKey: string, actor?: string, tenantId: string) {
  const api = apiClient(adminKey, actor);
  await api.delete(`/admin/tenants/${tenantId}`);
  return true;
}

/* Users */
export async function adminListUsers(adminKey: string, actor?: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get("/admin/users");
  return res.data as UserOut[];
}

export async function adminCreateUser(adminKey: string, actor?: string, payload: UserCreate) {
  const api = apiClient(adminKey, actor);
  const res = await api.post("/admin/users", payload);
  return res.data as UserOut;
}

export async function adminUpdateUser(adminKey: string, actor?: string, userId: string, payload: UserUpdate) {
  const api = apiClient(adminKey, actor);
  const res = await api.patch(`/admin/users/${userId}`, payload);
  return res.data as UserOut;
}

/* Memberships */
export async function adminMembershipsByTenant(adminKey: string, actor?: string, tenantId: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get(`/admin/memberships/tenant/${tenantId}`);
  return res.data as MembershipOut[];
}

export async function adminMembershipsByUser(adminKey: string, actor?: string, userId: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get(`/admin/memberships/user/${userId}`);
  return res.data as MembershipOut[];
}

export async function adminCreateMembership(adminKey: string, actor?: string, payload: MembershipCreate) {
  const api = apiClient(adminKey, actor);
  const res = await api.post("/admin/memberships", payload);
  return res.data as MembershipOut;
}

export async function adminUpdateMembership(adminKey: string, actor?: string, membershipId: string, payload: MembershipUpdate) {
  const api = apiClient(adminKey, actor);
  const res = await api.patch(`/admin/memberships/${membershipId}`, payload);
  return res.data as MembershipOut;
}

/* Roles */
export async function adminRoles(adminKey: string, actor?: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get("/admin/roles");
  return res.data as string[];
}

/* Diagnostics */
export async function adminDiagnostics(adminKey: string, actor?: string) {
  const api = apiClient(adminKey, actor);
  const res = await api.get("/admin/diagnostics");
  return res.data as DiagnosticsOut;
}

/* Audit */
export async function adminGetAudit(adminKey: string, actor?: string, filters: AuditFilters = {}) {
  const api = apiClient(adminKey, actor);

  // backend erwartet query params, null vermeiden
  const params: Record<string, unknown> = {};
  if (filters.actor) params.actor = filters.actor;
  if (filters.action) params.action = filters.action;
  if (filters.entity_type) params.entity_type = filters.entity_type;
  if (filters.entity_id) params.entity_id = filters.entity_id;
  if (filters.created_from) params.created_from = filters.created_from;
  if (filters.created_to) params.created_to = filters.created_to;

  params.limit = typeof filters.limit === "number" ? filters.limit : 100;
  params.offset = typeof filters.offset === "number" ? filters.offset : 0;

  const res = await api.get("/admin/audit", { params });
  return res.data as AuditOut[];
}
