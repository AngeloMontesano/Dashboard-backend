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
  const client = buildClient(token);
  const res = await client.get<Category[]>('/inventory/categories');
  return res.data;
}

export async function createCategory(token: string, payload: { name: string; is_active?: boolean }) {
  const client = buildClient(token);
  const res = await client.post<Category>('/inventory/categories', payload);
  return res.data;
}

export async function updateCategory(token: string, id: string, payload: { name?: string; is_active?: boolean }) {
  const client = buildClient(token);
  const res = await client.patch<Category>(`/inventory/categories/${id}`, payload);
  return res.data;
}

export async function fetchItems(params: {
  token: string;
  q?: string;
  category_id?: string | null;
  active?: boolean | null;
  page?: number;
  page_size?: number;
}) {
  const { token, ...query } = params;
  const client = buildClient(token);
  const res = await client.get<ItemsPage>('/inventory/items', { params: query });
  return res.data;
}

export async function checkSkuExists(token: string, sku: string) {
  const client = buildClient(token);
  const res = await client.get<{ exists: boolean; normalized_sku: string }>(
    `/inventory/items/sku/${encodeURIComponent(sku)}/exists`
  );
  return res.data;
}

export type ItemCreatePayload = {
  sku: string;
  barcode: string;
  name: string;
  description?: string;
  quantity?: number;
  unit?: string;
  is_active?: boolean;
  category_id?: string | null;
  min_stock?: number;
  max_stock?: number;
  target_stock?: number;
  recommended_stock?: number;
  order_mode?: number;
};

export async function createItem(token: string, payload: ItemCreatePayload) {
  const client = buildClient(token);
  const res = await client.post<Item>('/inventory/items', payload);
  return res.data;
}

export async function updateItem(token: string, id: string, payload: Partial<ItemCreatePayload>) {
  const client = buildClient(token);
  const res = await client.patch<Item>(`/inventory/items/${id}`, payload);
  return res.data;
}

export async function importItems(token: string, file: File) {
  const client = buildClient(token);
  const form = new FormData();
  form.append('file', file);
  const res = await client.post<{ imported: number; updated: number; errors: Array<{ row: string; error: string }> }>(
    '/inventory/items/import',
    form,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  );
  return res.data;
}

export async function exportItems(token: string) {
  const client = buildClient(token);
  const res = await client.get<{ csv: string }>('/inventory/items/export');
  return res.data.csv;
}

export async function postInventoryMovement(token: string, payload: MovementPayload) {
  const client = buildClient(token);
  const res = await client.post('/inventory/movements', payload);
  return res.data;
}
