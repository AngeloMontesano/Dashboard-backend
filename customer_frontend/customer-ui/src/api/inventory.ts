import { createApiClient } from './base';

function buildClient(token?: string) {
  return createApiClient({ token });
}

export type Category = {
  id: string;
  name: string;
  is_system: boolean;
  is_active: boolean;
};

export type Item = {
  id: string;
  sku: string;
  barcode: string;
  name: string;
  description: string;
  quantity: number;
  unit: string;
  is_active: boolean;
  category_id?: string | null;
  category_name?: string | null;
  min_stock: number;
  max_stock: number;
  target_stock: number;
  recommended_stock: number;
  order_mode: number;
};

export type ItemsPage = {
  items: Item[];
  total: number;
  page: number;
  page_size: number;
};

export type MovementPayload = {
  client_tx_id: string;
  type: 'IN' | 'OUT';
  barcode: string;
  qty: number;
  note?: string;
  created_at?: string;
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
