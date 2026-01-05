import { api, authHeaders } from "./client";
import type { components, paths } from "./gen/openapi";

export type Category = components["schemas"]["CategoryOut"];
export type Item = components["schemas"]["ItemOut"];
export type ItemsPage = components["schemas"]["ItemsPage"];
type ItemsQuery = NonNullable<paths["/inventory/items"]["get"]["parameters"]["query"]>;
type ItemCreatePayload = components["schemas"]["ItemCreate"];
type ItemUpdatePayload = components["schemas"]["ItemUpdate"];
export type MovementPayload = components["schemas"]["MovementPayload"];
type SkuExistsResponse = components["schemas"]["SKUExistsResponse"];
type ImportItemsResponse =
  paths["/inventory/items/import"]["post"]["responses"]["200"]["content"]["application/json"];
type SettingsOut = components["schemas"]["TenantSettingsOut"];
type SettingsUpdate = components["schemas"]["TenantSettingsUpdate"];
type MassImportResult = components["schemas"]["MassImportResult"];
type OrderOut = components["schemas"]["OrderOut"];
type OrderCreate = components["schemas"]["OrderCreate"];
type OrderEmailRequest = components["schemas"]["OrderEmailRequest"];
type ReorderResponse = components["schemas"]["ReorderResponse"];
export type OrderCreateItem = components["schemas"]["OrderItemInput"];

export type ImportItemsResult = {
  imported: number;
  updated: number;
  errors: { row: string; error: string }[];
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
  const data = (res.data || {}) as Partial<ImportItemsResult>;
  return {
    imported: data.imported ?? 0,
    updated: data.updated ?? 0,
    errors: data.errors ?? [],
  };
}

export async function exportItems(token: string) {
  const res = await api.get<{ csv: string }>("/inventory/items/export", { headers: authHeaders(token) });
  return res.data.csv;
}

export async function postInventoryMovement(token: string, payload: MovementPayload) {
  const res = await api.post("/inventory/movements", payload, { headers: authHeaders(token) });
  return res.data;
}

export async function fetchSettings(token: string) {
  const res = await api.get<SettingsOut>("/inventory/settings", { headers: authHeaders(token) });
  return res.data;
}

export async function updateSettings(token: string, payload: SettingsUpdate) {
  const res = await api.put<SettingsOut>("/inventory/settings", payload, { headers: authHeaders(token) });
  return res.data;
}

export async function exportSettings(token: string) {
  const res = await api.get<Blob>("/inventory/settings/export", {
    headers: authHeaders(token),
    responseType: "blob",
  });
  return res.data;
}

export async function importSettings(token: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post<MassImportResult>("/inventory/settings/import", form, {
    headers: {
      ...authHeaders(token),
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
}

export async function sendTestEmail(token: string, email: string) {
  const res = await api.post("/inventory/settings/test-email", { email }, { headers: authHeaders(token) });
  return res.data as { ok: boolean; error?: string | null };
}

export async function listOrders(token: string, status?: "OPEN" | "COMPLETED" | "CANCELED") {
  const res = await api.get<OrderOut[]>("/inventory/orders", {
    params: status ? { status } : undefined,
    headers: authHeaders(token),
  });
  return res.data;
}

export async function createOrder(token: string, payload: OrderCreate) {
  const res = await api.post<OrderOut>("/inventory/orders", payload, { headers: authHeaders(token) });
  return res.data;
}

export async function completeOrder(token: string, orderId: string) {
  const res = await api.post<OrderOut>(`/inventory/orders/${orderId}/complete`, null, { headers: authHeaders(token) });
  return res.data;
}

export async function cancelOrder(token: string, orderId: string) {
  const res = await api.post<OrderOut>(`/inventory/orders/${orderId}/cancel`, null, { headers: authHeaders(token) });
  return res.data;
}

export async function sendOrderEmail(token: string, orderId: string, payload: OrderEmailRequest) {
  const res = await api.post(`/inventory/orders/${orderId}/email`, payload, { headers: authHeaders(token) });
  return res.data as { ok: boolean; error?: string | null };
}

export async function downloadOrderPdf(token: string, orderId: string) {
  const res = await api.get<Blob>(`/inventory/orders/${orderId}/pdf`, {
    headers: authHeaders(token),
    responseType: "blob",
  });
  return res.data;
}

export async function fetchReorderRecommendations(token: string) {
  const res = await api.get<ReorderResponse>("/inventory/orders/recommended", { headers: authHeaders(token) });
  return res.data;
}
