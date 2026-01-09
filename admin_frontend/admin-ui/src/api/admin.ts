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
  TenantSettingsOut,
  TenantSettingsUpdate,
  AdminSystemInfo,
  AdminSystemActionResponse,
  SmtpSettingsOut,
  SmtpSettingsIn,
  SmtpTestResponse,
  SystemEmailSettings,
  SystemEmailSettingsUpdate,
} from "../types";

import { api, adminHeaders } from "./client";

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
type TenantSettingsResponse =
  paths["/admin/tenants/{tenant_id}/settings"]["get"]["responses"]["200"]["content"]["application/json"];

type AdminCategoriesResponse =
  paths["/admin/inventory/categories"]["get"]["responses"]["200"]["content"]["application/json"];
type AdminCategoryCreate = components["schemas"]["CategoryCreate"];
type AdminCategoryUpdate = components["schemas"]["CategoryUpdate"];

type AdminUnitsResponse = paths["/admin/inventory/units"]["get"]["responses"]["200"]["content"]["application/json"];
type AdminUnitPayload = components["schemas"]["ItemUnitOut"];

type AdminItemsResponse =
  paths["/admin/inventory/items"]["get"]["responses"]["200"]["content"]["application/json"];
type AdminItemsQuery = NonNullable<paths["/admin/inventory/items"]["get"]["parameters"]["query"]>;
type AdminItemCreate = components["schemas"]["ItemCreate"];
type AdminItemUpdate = components["schemas"]["ItemUpdate"];
type AdminImportResponse =
  paths["/admin/inventory/items/import"]["post"]["responses"]["200"]["content"]["application/json"];
type AdminExportResponse =
  paths["/admin/inventory/items/export"]["get"]["responses"]["200"]["content"]["application/json"];

type AdminIndustriesResponse =
  paths["/admin/inventory/industries"]["get"]["responses"]["200"]["content"]["application/json"];
type AdminIndustryCreate = components["schemas"]["IndustryCreate"];
type AdminIndustryUpdate = components["schemas"]["IndustryUpdate"];
type AdminIndustryItemsResponse =
  paths["/admin/inventory/industries/{industry_id}/items"]["get"]["responses"]["200"]["content"]["application/json"];
type AdminIndustryItemsUpdate =
  components["schemas"]["IndustryArticlesUpdate"];

type AdminLoginPayload = components["schemas"]["AdminCredentialLogin"];
type TenantUserCreatePayload = components["schemas"]["TenantUserCreate"];
type TenantUserUpdatePayload = components["schemas"]["TenantUserUpdate"];

type AdminLoginResponse = { admin_key: string; actor?: string };
type AdminSystemInfoResponse = AdminSystemInfo;
type AdminSystemActionResponseRaw = AdminSystemActionResponse;
type AdminSystemEmailSettingsResponse = SystemEmailSettings;
type AdminSmtpSettingsResponse = SmtpSettingsOut;
type AdminSmtpTestResponse = SmtpTestResponse;
type BackupEntry = {
  id: string;
  scope: string;
  tenant_id: string | null;
  tenant_slug: string | null;
  created_at: string;
  status: string;
  restored_at?: string | null;
  files: { name: string; size_bytes: number; size_label: string }[];
};

type BackupListResponse = { items: BackupEntry[] };
type BackupActionResponse = { backup: BackupEntry; message: string };

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
  const res = await api.post<AdminLoginResponse>(
    "/admin/login",
    { email, password },
    { timeout: 15000 }
  );
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

/* Tenant Settings */
export async function adminGetTenantSettings(adminKey: string, actor: string | undefined, tenantId: string) {
  const res = await api.get<TenantSettingsResponse>(`/admin/tenants/${tenantId}/settings`, withAdmin(adminKey, actor));
  return res.data as TenantSettingsOut;
}

export async function adminUpdateTenantSettings(
  adminKey: string,
  actor: string | undefined,
  tenantId: string,
  payload: TenantSettingsUpdate
) {
  const res = await api.put<TenantSettingsOut>(
    `/admin/tenants/${tenantId}/settings`,
    payload,
    withAdmin(adminKey, actor)
  );
  return res.data;
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

/* System */
export async function adminGetSystemInfo(adminKey: string, actor?: string) {
  const res = await api.get<AdminSystemInfoResponse>("/admin/system/info", withAdmin(adminKey, actor));
  return res.data;
}

export async function adminGetEmailSettings(adminKey: string, actor?: string) {
  const res = await api.get<AdminSystemEmailSettingsResponse>("/admin/system/email", withAdmin(adminKey, actor));
  return res.data;
}

export async function adminUpdateEmailSettings(adminKey: string, actor: string | undefined, payload: SystemEmailSettingsUpdate) {
  const res = await api.put<AdminSystemEmailSettingsResponse>("/admin/system/email", payload, withAdmin(adminKey, actor));
  return res.data;
}

/* Backups */
export async function adminListBackups(adminKey: string, actor?: string) {
  const res = await api.get<BackupListResponse>("/admin/backups", withAdmin(adminKey, actor));
  return res.data.items;
}

export async function adminCreateTenantBackup(adminKey: string, actor: string | undefined, tenantId: string) {
  const res = await api.post<BackupActionResponse>(`/admin/backups/tenants/${tenantId}`, null, withAdmin(adminKey, actor));
  return res.data.backup;
}

export async function adminCreateAllBackups(adminKey: string, actor?: string) {
  const res = await api.post<BackupActionResponse>("/admin/backups/all", null, withAdmin(adminKey, actor));
  return res.data.backup;
}

export async function adminRestoreBackup(adminKey: string, actor: string | undefined, backupId: string) {
  const res = await api.post<BackupActionResponse>(`/admin/backups/${backupId}/restore`, null, withAdmin(adminKey, actor));
  return res.data.backup;
}

export async function adminDownloadBackup(adminKey: string, actor: string | undefined, backupId: string) {
  const res = await api.get(`/admin/backups/${backupId}/download`, {
    ...withAdmin(adminKey, actor),
    responseType: "blob",
  });
  return res.data as Blob;
}

export async function adminDownloadBackupFile(
  adminKey: string,
  actor: string | undefined,
  backupId: string,
  filename: string
) {
  const res = await api.get(`/admin/backups/${backupId}/files/${filename}`, {
    ...withAdmin(adminKey, actor),
    responseType: "blob",
  });
  return res.data as Blob;
}

/* SMTP */
export async function adminGetSmtpSettings(adminKey: string, actor?: string) {
  const res = await api.get<AdminSmtpSettingsResponse>("/admin/smtp/settings", withAdmin(adminKey, actor));
  return res.data;
}

export async function adminUpdateSmtpSettings(adminKey: string, actor: string | undefined, payload: SmtpSettingsIn) {
  const res = await api.put<AdminSmtpSettingsResponse>("/admin/smtp/settings", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminTestSmtpSettings(adminKey: string, actor: string | undefined, email: string) {
  const res = await api.post<AdminSmtpTestResponse>(
    "/admin/smtp/settings/test",
    { email },
    withAdmin(adminKey, actor)
  );
  return res.data;
}

export async function adminTestEmail(adminKey: string, actor: string | undefined, email: string) {
  const res = await api.post<AdminSystemActionResponseRaw>(
    "/admin/system/email/test",
    { email },
    withAdmin(adminKey, actor)
  );
  return res.data;
}

export async function adminSystemCacheReset(adminKey: string, actor?: string) {
  const res = await api.post<AdminSystemActionResponseRaw>("/admin/system/actions/cache-reset", null, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminSystemReindex(adminKey: string, actor?: string) {
  const res = await api.post<AdminSystemActionResponseRaw>("/admin/system/actions/reindex", null, withAdmin(adminKey, actor));
  return res.data;
}

export async function adminSystemRestart(adminKey: string, actor?: string) {
  const res = await api.post<AdminSystemActionResponseRaw>("/admin/system/actions/restart", null, withAdmin(adminKey, actor));
  return res.data;
}

/* SMTP Settings */
export interface SmtpSettings {
  host: string;
  port: number;
  from_email: string;
  user?: string | null;
  use_tls: boolean;
  has_password: boolean;
}

export interface SmtpSettingsInput {
  host: string;
  port: number;
  from_email: string;
  user?: string | null;
  password?: string | null;
  use_tls: boolean;
}

export async function adminTestSmtp(adminKey: string, actor: string | undefined, email: string) {
  const res = await api.post<{ ok: boolean }>("/admin/smtp/settings/test", { email }, withAdmin(adminKey, actor));
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

/* Admin Inventory: Categories */
export async function adminListGlobalCategories(adminKey: string, actor?: string) {
  const res = await api.get<AdminCategoriesResponse>("/admin/inventory/categories", withAdmin(adminKey, actor));
  return res.data as components["schemas"]["CategoryOut"][];
}

export async function adminCreateGlobalCategory(adminKey: string, actor: string | undefined, payload: AdminCategoryCreate) {
  const res = await api.post("/admin/inventory/categories", payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["CategoryOut"];
}

export async function adminUpdateGlobalCategory(
  adminKey: string,
  actor: string | undefined,
  id: string,
  payload: AdminCategoryUpdate
) {
  const res = await api.patch(`/admin/inventory/categories/${id}`, payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["CategoryOut"];
}

/* Admin Inventory: Units */
export async function adminListUnits(adminKey: string, actor?: string) {
  const res = await api.get<AdminUnitsResponse>("/admin/inventory/units", withAdmin(adminKey, actor));
  return res.data as components["schemas"]["ItemUnitOut"][];
}

export async function adminUpsertUnit(adminKey: string, actor: string | undefined, payload: AdminUnitPayload) {
  const res = await api.post<AdminUnitPayload>("/admin/inventory/units", payload, withAdmin(adminKey, actor));
  return res.data;
}

/* Admin Inventory: Items */
export async function adminListGlobalItems(adminKey: string, actor: string | undefined, params?: AdminItemsQuery) {
  const res = await api.get<AdminItemsResponse>("/admin/inventory/items", { ...withAdmin(adminKey, actor), params });
  return res.data as components["schemas"]["ItemsPage"];
}

export async function adminCreateGlobalItem(adminKey: string, actor: string | undefined, payload: AdminItemCreate) {
  const res = await api.post("/admin/inventory/items", payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["ItemOut"];
}

export async function adminUpdateGlobalItem(
  adminKey: string,
  actor: string | undefined,
  id: string,
  payload: AdminItemUpdate
) {
  const res = await api.patch(`/admin/inventory/items/${id}`, payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["ItemOut"];
}

export async function adminImportGlobalItems(adminKey: string, actor: string | undefined, file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post<AdminImportResponse>("/admin/inventory/items/import", form, {
    headers: { ...withAdmin(adminKey, actor).headers, "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function adminExportGlobalItems(adminKey: string, actor: string | undefined) {
  const res = await api.get<AdminExportResponse>("/admin/inventory/items/export", withAdmin(adminKey, actor));
  return res.data;
}

/* Admin Inventory: Industries */
export async function adminListIndustries(adminKey: string, actor?: string) {
  const res = await api.get<AdminIndustriesResponse>("/admin/inventory/industries", withAdmin(adminKey, actor));
  return res.data;
}

export async function adminCreateIndustry(adminKey: string, actor: string | undefined, payload: AdminIndustryCreate) {
  const res = await api.post("/admin/inventory/industries", payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["IndustryOut"];
}

export async function adminUpdateIndustry(
  adminKey: string,
  actor: string | undefined,
  id: string,
  payload: AdminIndustryUpdate
) {
  const res = await api.patch(`/admin/inventory/industries/${id}`, payload, withAdmin(adminKey, actor));
  return res.data as components["schemas"]["IndustryOut"];
}

export async function adminGetIndustryItems(adminKey: string, actor: string | undefined, industryId: string) {
  const res = await api.get<AdminIndustryItemsResponse>(
    `/admin/inventory/industries/${industryId}/items`,
    withAdmin(adminKey, actor)
  );
  return res.data;
}

export async function adminSetIndustryItems(
  adminKey: string,
  actor: string | undefined,
  industryId: string,
  payload: AdminIndustryItemsUpdate
) {
  const res = await api.put(`/admin/inventory/industries/${industryId}/items`, payload, withAdmin(adminKey, actor));
  return res.data as { ok: boolean; count: number };
}
