// src/types.ts
import type { components, paths } from "./api/gen/openapi";

type TenantListResponse =
  paths["/admin/tenants"]["get"]["responses"]["200"]["content"]["application/json"];

export type TenantOut = TenantListResponse[number];
export type TenantCreate = components["schemas"]["TenantCreate"];
export type TenantUpdate = components["schemas"]["TenantUpdate"];
export type TenantSettingsOut = components["schemas"]["TenantSettingsOut"];
export type TenantSettingsUpdate = components["schemas"]["TenantSettingsUpdate"];

export type UserOut = components["schemas"]["UserOut"];
export type UserCreate = components["schemas"]["UserCreate"];
export type UserUpdate = components["schemas"]["UserUpdate"];

export type MembershipOut = components["schemas"]["MembershipOut"];
export type MembershipCreate = components["schemas"]["MembershipCreate"];
export type MembershipUpdate = components["schemas"]["MembershipUpdate"];

export type DiagnosticsOut = Record<string, unknown>;
export type AuditOut = components["schemas"]["AuditOut"];
export type AuditFilters = NonNullable<paths["/admin/audit"]["get"]["parameters"]["query"]>;

export type TenantUserApiOut = components["schemas"]["TenantUserOut"];
export type TenantUserCreate = {
  email: string;
  role: string;
  password?: string | null;
  is_active?: boolean;
};
export type TenantUserUpdate = {
  role?: string | null;
  password?: string | null;
  is_active?: boolean | null;
};
export type TenantUserOut = {
  id: string;
  tenant_id?: string;
  user_id?: string;
  email: string;
  role: string;
  is_active: boolean;
  has_password?: boolean;
  updated_at?: string;
};
