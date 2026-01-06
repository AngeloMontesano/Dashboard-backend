import { api, adminHeaders } from "./client";
import type { components, paths } from "./gen/openapi";

export type GlobalCategory = components["schemas"]["CategoryOut"];
export type CategoryCreatePayload = components["schemas"]["CategoryCreate"];
export type CategoryUpdatePayload = components["schemas"]["CategoryUpdate"];

export type GlobalItem = components["schemas"]["ItemOut"];
export type ItemCreatePayload = components["schemas"]["ItemCreate"];
export type ItemUpdatePayload = components["schemas"]["ItemUpdate"];

export type GlobalUnit = components["schemas"]["ItemUnitOut"];
export type GlobalIndustry = components["schemas"]["IndustryOut"];
export type IndustryAssignRequest = components["schemas"]["IndustryAssignRequest"];
export type IndustryAssignResponse = components["schemas"]["IndustryAssignResponse"];
export type IndustryMappingImportResult = components["schemas"]["IndustryMappingImportResult"];
export type IndustryOverlapCounts = components["schemas"]["IndustryOverlapCounts"];

type ItemsPage = components["schemas"]["ItemsPage"];
type ItemsQuery = NonNullable<paths["/admin/inventory/items"]["get"]["parameters"]["query"]>;
type ImportItemsResponse =
  paths["/admin/inventory/items/import"]["post"]["responses"]["200"]["content"]["application/json"];
type IndustryAssignRequest = components["schemas"]["IndustryAssignTenantsRequest"];
type IndustryAssignResponse =
  paths["/admin/inventory/industries/{industry_id}/assign/tenants"]["post"]["responses"]["200"]["content"]["application/json"];

function withAdmin(adminKey: string, actor?: string) {
  return { headers: adminHeaders(adminKey, actor) };
}

/* Kategorien */
export async function fetchGlobalCategories(adminKey: string, actor?: string) {
  const res = await api.get<GlobalCategory[]>("/admin/inventory/categories", withAdmin(adminKey, actor));
  return res.data;
}

export async function createGlobalCategory(adminKey: string, payload: CategoryCreatePayload, actor?: string) {
  const res = await api.post<GlobalCategory>("/admin/inventory/categories", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function updateGlobalCategory(adminKey: string, id: string, payload: CategoryUpdatePayload, actor?: string) {
  const res = await api.patch<GlobalCategory>(`/admin/inventory/categories/${id}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function deleteGlobalCategory(adminKey: string, id: string, actor?: string) {
  await api.delete(`/admin/inventory/categories/${id}`, withAdmin(adminKey, actor));
}

export async function importGlobalCategories(adminKey: string, file: File, actor?: string) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/admin/inventory/categories/import", form, {
    headers: { ...withAdmin(adminKey, actor).headers, "Content-Type": "multipart/form-data" },
  });
  return res.data as ImportItemsResponse;
}

export async function exportGlobalCategories(adminKey: string, format: "csv" | "xlsx" = "csv", actor?: string) {
  const res = await api.get(`/admin/inventory/categories/export`, {
    ...withAdmin(adminKey, actor),
    params: { format },
    responseType: "blob",
  });
  return res.data as Blob;
}

/* Einheiten */
export async function fetchGlobalUnits(adminKey: string, actor?: string) {
  const res = await api.get<GlobalUnit[]>("/admin/inventory/units", withAdmin(adminKey, actor));
  return res.data;
}

export async function upsertGlobalUnit(adminKey: string, payload: GlobalUnit, actor?: string) {
  const res = await api.post<GlobalUnit>("/admin/inventory/units", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function deleteGlobalUnit(adminKey: string, code: string, actor?: string) {
  await api.delete(`/admin/inventory/units/${code}`, withAdmin(adminKey, actor));
}

export async function importGlobalUnits(adminKey: string, file: File, actor?: string) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/admin/inventory/units/import", form, {
    headers: { ...withAdmin(adminKey, actor).headers, "Content-Type": "multipart/form-data" },
  });
  return res.data as ImportItemsResponse;
}

export async function exportGlobalUnits(adminKey: string, format: "csv" | "xlsx" = "csv", actor?: string) {
  const res = await api.get(`/admin/inventory/units/export`, {
    ...withAdmin(adminKey, actor),
    params: { format },
    responseType: "blob",
  });
  return res.data as Blob;
}

/* Artikel */
export async function fetchGlobalItems(adminKey: string, actor: string | undefined, params?: ItemsQuery) {
  const res = await api.get<ItemsPage>("/admin/inventory/items", { ...withAdmin(adminKey, actor), params });
  return res.data;
}

export async function createGlobalItem(adminKey: string, payload: ItemCreatePayload, actor?: string) {
  const res = await api.post<GlobalItem>("/admin/inventory/items", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function updateGlobalItem(adminKey: string, id: string, payload: ItemUpdatePayload, actor?: string) {
  const res = await api.patch<GlobalItem>(`/admin/inventory/items/${id}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function deleteGlobalItem(adminKey: string, id: string, actor?: string) {
  await api.delete(`/admin/inventory/items/${id}`, withAdmin(adminKey, actor));
}

export async function importGlobalItems(adminKey: string, file: File, actor?: string) {
  const form = new FormData();
  form.append("file", file);

  const res = await api.post<ImportItemsResponse>("/admin/inventory/items/import", form, {
    headers: {
      ...withAdmin(adminKey, actor).headers,
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
}

export async function exportGlobalItems(adminKey: string, format: "csv" | "xlsx" = "csv", actor?: string) {
  const res = await api.get(`/admin/inventory/items/export`, {
    ...withAdmin(adminKey, actor),
    params: { format },
    responseType: "blob",
  });
  return res.data as Blob;
}

/* Branchen */
export async function fetchGlobalIndustries(adminKey: string, actor?: string) {
  const res = await api.get<GlobalIndustry[]>("/admin/inventory/industries", withAdmin(adminKey, actor));
  return res.data;
}

export async function createGlobalIndustry(adminKey: string, payload: components["schemas"]["IndustryCreate"], actor?: string) {
  const res = await api.post<GlobalIndustry>("/admin/inventory/industries", payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function updateGlobalIndustry(
  adminKey: string,
  id: string,
  payload: components["schemas"]["IndustryUpdate"],
  actor?: string
) {
  const res = await api.patch<GlobalIndustry>(`/admin/inventory/industries/${id}`, payload, withAdmin(adminKey, actor));
  return res.data;
}

export async function deleteGlobalIndustry(adminKey: string, id: string, actor?: string) {
  await api.delete(`/admin/inventory/industries/${id}`, withAdmin(adminKey, actor));
}

export async function fetchIndustryItems(adminKey: string, industryId: string, actor?: string) {
  const res = await api.get<GlobalItem[]>(`/admin/inventory/industries/${industryId}/items`, withAdmin(adminKey, actor));
  return res.data;
}

export async function setIndustryItems(
  adminKey: string,
  industryId: string,
  payload: components["schemas"]["IndustryArticlesUpdate"],
  actor?: string
) {
  const res = await api.put<{ ok: boolean; count: number }>(
    `/admin/inventory/industries/${industryId}/items`,
    payload,
    withAdmin(adminKey, actor)
  );
  return res.data;
}

export async function exportIndustryMapping(
  adminKey: string,
  industryId: string,
  format: "csv" | "xlsx" = "csv",
  actor?: string
) {
  const res = await api.get(`/admin/inventory/industries/${industryId}/items/export`, {
    ...withAdmin(adminKey, actor),
    params: { format },
    responseType: "blob",
  });
  return res.data as Blob;
}

export async function importIndustryMapping(
  adminKey: string,
  industryId: string,
  file: File,
  actor?: string
) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post<IndustryMappingImportResult>(
    `/admin/inventory/industries/${industryId}/items/import`,
    form,
    {
      headers: {
        ...withAdmin(adminKey, actor).headers,
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return res.data;
}

export async function fetchIndustryOverlapCounts(adminKey: string, itemIds: string[], actor?: string) {
  const res = await api.get<IndustryOverlapCounts>(`/admin/inventory/industries/overlap-counts`, {
    ...withAdmin(adminKey, actor),
    params: { item_ids: itemIds },
  });
  return res.data;
}

export async function assignIndustryItemsToTenants(
  adminKey: string,
  industryId: string,
  payload: IndustryAssignRequest,
  actor?: string
) {
  const res = await api.post<IndustryAssignResponse>(
    `/admin/inventory/industries/${industryId}/assign-to-tenants`,
    payload,
    withAdmin(adminKey, actor)
  );
  return res.data;
}
