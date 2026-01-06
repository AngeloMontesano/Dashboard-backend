import { api } from "./client";
import type { components, paths } from "./gen/openapi";

export type GlobalCategory = components["schemas"]["CategoryOut"];
export type CategoryCreatePayload = components["schemas"]["CategoryCreate"];
export type CategoryUpdatePayload = components["schemas"]["CategoryUpdate"];

export type GlobalItem = components["schemas"]["ItemOut"];
export type ItemCreatePayload = components["schemas"]["ItemCreate"];
export type ItemUpdatePayload = components["schemas"]["ItemUpdate"];

type ItemsPage = components["schemas"]["ItemsPage"];
type ItemsQuery = NonNullable<paths["/inventory/items"]["get"]["parameters"]["query"]>;
type ImportItemsResponse =
  paths["/inventory/items/import"]["post"]["responses"]["200"]["content"]["application/json"];
type ExportItemsResponse =
  paths["/inventory/items/export"]["get"]["responses"]["200"]["content"]["application/json"];

function bearer(token?: string) {
  if (!token) {
    throw new Error("Authorization Token erforderlich");
  }
  return { Authorization: `Bearer ${token}` };
}

export async function fetchGlobalCategories(token: string) {
  const res = await api.get<GlobalCategory[]>("/inventory/categories", { headers: bearer(token) });
  return res.data;
}

export async function createGlobalCategory(token: string, payload: CategoryCreatePayload) {
  const res = await api.post<GlobalCategory>("/inventory/categories", payload, { headers: bearer(token) });
  return res.data;
}

export async function updateGlobalCategory(token: string, id: string, payload: CategoryUpdatePayload) {
  const res = await api.patch<GlobalCategory>(`/inventory/categories/${id}`, payload, { headers: bearer(token) });
  return res.data;
}

export async function fetchGlobalItems(token: string, params?: ItemsQuery) {
  const res = await api.get<ItemsPage>("/inventory/items", { headers: bearer(token), params });
  return res.data;
}

export async function createGlobalItem(token: string, payload: ItemCreatePayload) {
  const res = await api.post<GlobalItem>("/inventory/items", payload, { headers: bearer(token) });
  return res.data;
}

export async function updateGlobalItem(token: string, id: string, payload: ItemUpdatePayload) {
  const res = await api.patch<GlobalItem>(`/inventory/items/${id}`, payload, { headers: bearer(token) });
  return res.data;
}

export async function importGlobalItems(token: string, file: File, mapping?: Record<string, string>) {
  const form = new FormData();
  form.append("file", file);
  if (mapping) {
    form.append("mapping", JSON.stringify(mapping));
  }

  const res = await api.post<ImportItemsResponse>("/inventory/items/import", form, {
    headers: {
      ...bearer(token),
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
}

export async function exportGlobalItems(token: string) {
  const res = await api.get<ExportItemsResponse>("/inventory/items/export", {
    headers: bearer(token),
  });
  return res.data;
}
