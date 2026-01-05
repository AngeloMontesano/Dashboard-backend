import { api, authHeaders } from "./client";
import type { components, paths } from "./gen/openapi";

type ItemsQuery = NonNullable<paths["/inventory/items"]["get"]["parameters"]["query"]>;

export type Category = components["schemas"]["CategoryOut"];
export type Item = components["schemas"]["ItemOut"];
export type ItemsPage = components["schemas"]["ItemsPage"];
export type ItemCreatePayload = components["schemas"]["ItemCreate"];
export type ItemUpdatePayload = components["schemas"]["ItemUpdate"];
export type MovementPayload = components["schemas"]["MovementPayload"];
export type SkuExistsResponse = components["schemas"]["SKUExistsResponse"];

type ImportItemsResponse = {
  imported: number;
  updated: number;
  errors: Array<{ row: string; error: string }>;
};

export async function fetchCategories(token: string) {
  const res = await api.get<Category[]>("/inventory/categories", { headers: authHeaders(token) });
  return res.data;
}

export async function createCategory(token: string, payload: components["schemas"]["CategoryCreate"]) {
  const res = await api.post<Category>("/inventory/categories", payload, { headers: authHeaders(token) });
  return res.data;
}

export async function updateCategory(token: string, id: string, payload: components["schemas"]["CategoryUpdate"]) {
  const res = await api.patch<Category>(`/inventory/categories/${id}`, payload, { headers: authHeaders(token) });
  return res.data;
}

export async function fetchItems(params: ItemsQuery & { token: string }) {
  const { token, ...query } = params;
  const res = await api.get<ItemsPage>("/inventory/items", { params: query, headers: authHeaders(token) });
  return res.data;
}

export async function checkSkuExists(token: string, sku: string) {
  const res = await api.get<SkuExistsResponse>(`/inventory/items/sku/${encodeURIComponent(sku)}/exists`, {
    headers: authHeaders(token),
  });
  return res.data;
}

export async function createItem(token: string, payload: ItemCreatePayload) {
  const res = await api.post<Item>("/inventory/items", payload, { headers: authHeaders(token) });
  return res.data;
}

export async function updateItem(token: string, id: string, payload: ItemUpdatePayload) {
  const res = await api.patch<Item>(`/inventory/items/${id}`, payload, { headers: authHeaders(token) });
  return res.data;
}

export async function importItems(token: string, file: File, mapping?: Record<string, string>) {
  const form = new FormData();
  form.append("file", file);
  if (mapping) {
    form.append("mapping", JSON.stringify(mapping));
  }

  const res = await api.post<ImportItemsResponse>("/inventory/items/import", form, {
    headers: {
      ...authHeaders(token),
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
}

export async function exportItems(token: string) {
  const res = await api.get<{ csv: string }>("/inventory/items/export", { headers: authHeaders(token) });
  return res.data.csv;
}

export async function postInventoryMovement(token: string, payload: MovementPayload) {
  const res = await api.post("/inventory/movements", payload, { headers: authHeaders(token) });
  return res.data;
}
