// src/types.ts
import type { components, paths } from "./api/gen/openapi";

type TenantListResponse =
  paths["/admin/tenants"]["get"]["responses"]["200"]["content"]["application/json"];

export type TenantOut = TenantListResponse[number];
export type TenantCreate = components["schemas"]["TenantCreate"];
export type TenantUpdate = components["schemas"]["TenantUpdate"];
export type TenantSettingsOut = components["schemas"]["TenantSettingsOut"];
export type TenantSettingsUpdate = components["schemas"]["TenantSettingsUpdate"];
export type GlobalCustomerSettingsOut = components["schemas"]["GlobalCustomerSettingsOut"];
export type GlobalCustomerSettingsUpdate = components["schemas"]["GlobalCustomerSettingsUpdate"];

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

export type AdminSystemInfo = {
  app_version: string;
  environment: string;
  build_timestamp: string;
  build_branch: string;
  image_tag?: string | null;
  git_commit?: string | null;
  db: string;
  db_error?: string;
  timestamp: string;
};

export type AdminSystemActionResponse = {
  action: string;
  supported: boolean;
  performed: boolean;
  detail: string;
  timestamp: string;
};

export type SmtpSettingsOut = {
  host: string;
  port: number;
  from_email: string;
  user?: string | null;
  use_tls: boolean;
  has_password: boolean;
};

export type SmtpSettingsIn = {
  host: string;
  port: number;
  from_email: string;
  user?: string | null;
  password?: string | null;
  use_tls: boolean;
};

export type SmtpTestResponse = {
  ok: boolean;
  detail?: string | null;
  request_id?: string | null;
};

export type SystemEmailSettings = {
  host: string | null;
  port: number | null;
  user: string | null;
  from_email: string | null;
  has_password: boolean;
};

export type SystemEmailSettingsUpdate = {
  host: string | null;
  port: number | null;
  user: string | null;
  password: string | null;
  from_email: string | null;
};

export type DemoInventoryImportResponse = {
  ok: boolean;
  tenant_slug: string;
  tenant_created: boolean;
  categories_created: number;
  categories_updated: number;
  items_created: number;
  items_updated: number;
};
