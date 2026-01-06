<script setup lang="ts">
import { onMounted, reactive, computed } from 'vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import { useAuth } from '@/composables/useAuth';
import {
  listOrders,
  completeOrder,
  cancelOrder,
  sendOrderEmail,
  downloadOrderPdf,
  fetchReorderRecommendations,
  fetchItems,
  createOrder
} from '@/api/inventory';

const { state: authState } = useAuth();

type Order = Awaited<ReturnType<typeof listOrders>>[number];
type ReorderItem = Awaited<ReturnType<typeof fetchReorderRecommendations>>['items'][number];
type ItemOption = Awaited<ReturnType<typeof fetchItems>>['items'][number];
type OrderRow = { id: string; itemId: string; quantity: number; note: string };

const state = reactive<{
  orders: Order[];
  loading: boolean;
  error: string | null;
  emailing: Record<string, boolean>;
  recommended: ReorderItem[];
  downloading: Record<string, boolean>;
  completing: Record<string, boolean>;
  canceling: Record<string, boolean>;
  items: ItemOption[];
  creating: boolean;
  createRows: OrderRow[];
  orderNote: string;
  filters: { status: 'ALL' | 'OPEN' | 'COMPLETED' | 'CANCELED'; search: string };
}>({
  orders: [],
  loading: false,
  error: null,
  emailing: {},
  recommended: [],
  downloading: {},
  completing: {},
  canceling: {},
  items: [],
  creating: false,
  createRows: [],
  orderNote: '',
  filters: { status: 'ALL', search: '' }
});

let rowId = 0;
const nextRowId = () => `row-${Date.now()}-${rowId++}`;

const selectableItems = computed(() => {
  const map = new Map<string, { value: string; label: string }>();
  const pushItem = (item: { id: string; name: string; quantity?: number | null; sku?: string | null }) => {
    if (!item?.id || map.has(item.id)) return;
    const parts = [item.name];
    if (typeof item.quantity === 'number') parts.push(`Bestand ${item.quantity}`);
    if (item.sku) parts.push(`SKU ${item.sku}`);
    map.set(item.id, { value: item.id, label: parts.join(' • ') });
  };
  state.items.forEach(pushItem);
  state.recommended.forEach(pushItem);
  return Array.from(map.values());
});

const openOrders = computed(() => state.orders.filter((o) => o.status === 'OPEN'));
const completedOrders = computed(() => state.orders.filter((o) => o.status === 'COMPLETED'));
const canceledOrders = computed(() => state.orders.filter((o) => o.status === 'CANCELED'));

const matchesSearch = (order: Order) => {
  const term = state.filters.search.trim().toLowerCase();
  if (!term) return true;
  return (
    order.number.toLowerCase().includes(term) ||
    (order.note && order.note.toLowerCase().includes(term)) ||
    order.items.some((item) => item.item_name?.toLowerCase().includes(term))
  );
};

const filteredOrders = computed(() =>
  state.orders.filter(
    (o) => (state.filters.status === 'ALL' || o.status === state.filters.status) && matchesSearch(o)
  )
);
const filteredOpenOrders = computed(() => filteredOrders.value.filter((o) => o.status === 'OPEN'));
const filteredCompletedOrders = computed(() => filteredOrders.value.filter((o) => o.status === 'COMPLETED'));
const filteredCanceledOrders = computed(() => filteredOrders.value.filter((o) => o.status === 'CANCELED'));

async function loadOrders() {
  if (!authState.accessToken) return;
  state.loading = true;
  state.error = null;
  try {
    state.orders = await listOrders(authState.accessToken);
  } catch (err: any) {
    state.error = err?.message || 'Bestellungen konnten nicht geladen werden';
  } finally {
    state.loading = false;
  }
}

async function loadRecommendations() {
  if (!authState.accessToken) return;
  try {
    const res = await fetchReorderRecommendations(authState.accessToken);
    state.recommended = res.items || [];
    prefillRowsFromRecommended();
  } catch {
    // Fallback auf lokale Items, falls Endpoint (z.B. wegen Migration) fehlt
    if (state.items.length) {
      state.recommended = state.items
        .filter(
          (item) =>
            item.is_active &&
            item.order_mode !== 0 &&
            item.target_stock > 0 &&
            item.quantity < item.target_stock
        )
        .map((item) => ({
          id: item.id,
          name: item.name,
          sku: item.sku,
          barcode: item.barcode,
          category_id: item.category_id || null,
          quantity: item.quantity,
          target_stock: item.target_stock,
          min_stock: item.min_stock,
          recommended_qty: Math.max(
            item.target_stock - item.quantity,
            item.min_stock - item.quantity,
            1
          )
        }));
    } else {
      state.recommended = [];
    }
  }

  if (!state.createRows.length) {
    prefillRowsFromRecommended();
  }
}

async function loadItems() {
  if (!authState.accessToken) return;
  try {
    const res = await fetchItems({ token: authState.accessToken, page: 1, page_size: 200, active: true });
    state.items = res.items;
    if (!state.recommended.length) {
      state.recommended = res.items
        .filter(
          (item) =>
            item.is_active &&
            item.order_mode !== 0 &&
            item.target_stock > 0 &&
            item.quantity < item.target_stock
        )
        .map((item) => ({
          id: item.id,
          name: item.name,
          sku: item.sku,
          barcode: item.barcode,
          category_id: item.category_id || null,
          quantity: item.quantity,
          target_stock: item.target_stock,
          min_stock: item.min_stock,
          recommended_qty: Math.max(
            item.target_stock - item.quantity,
            item.min_stock - item.quantity,
            1
          )
        }));
    }
  } catch {
    state.items = [];
  }

  if (!state.createRows.length) {
    prefillRowsFromRecommended();
  }
}

function prefillRowsFromRecommended(force = false) {
  if (!state.recommended.length) return;
  if (state.createRows.length && !force) return;
  const existingIds = new Set(state.createRows.map((row) => row.itemId));
  const additions = state.recommended
    .filter((item) => !existingIds.has(item.id))
    .map((item) => ({
      id: nextRowId(),
      itemId: item.id,
      quantity: Math.max(item.recommended_qty || item.quantity || 1, 1),
      note: ''
    }));
  if (additions.length) {
    state.createRows = [...state.createRows, ...additions];
  }
}

function addEmptyRow() {
  state.createRows = [...state.createRows, { id: nextRowId(), itemId: '', quantity: 1, note: '' }];
}

function removeRow(rowId: string) {
  state.createRows = state.createRows.filter((row) => row.id !== rowId);
}

async function markComplete(orderId: string) {
  if (!authState.accessToken) return;
  state.completing[orderId] = true;
  try {
    const updated = await completeOrder(authState.accessToken, orderId);
    state.orders = state.orders.map((o) => (o.id === updated.id ? updated : o));
  } catch (err: any) {
    state.error = err?.message || 'Erledigen fehlgeschlagen';
  } finally {
    state.completing[orderId] = false;
  }
}

async function markCanceled(orderId: string) {
  if (!authState.accessToken) return;
  state.canceling[orderId] = true;
  try {
    const updated = await cancelOrder(authState.accessToken, orderId);
    state.orders = state.orders.map((o) => (o.id === updated.id ? updated : o));
  } catch (err: any) {
    state.error = err?.message || 'Stornieren fehlgeschlagen';
  } finally {
    state.canceling[orderId] = false;
  }
}

async function sendEmail(orderId: string) {
  if (!authState.accessToken) return;
  state.emailing[orderId] = true;
  try {
    const res = await sendOrderEmail(authState.accessToken, orderId, {});
    if (!res.ok) {
      state.error = res.error || 'E-Mail-Versand fehlgeschlagen';
    }
  } catch (err: any) {
    state.error = err?.message || 'E-Mail-Versand fehlgeschlagen';
  } finally {
    state.emailing[orderId] = false;
  }
}

async function downloadPdf(orderId: string) {
  if (!authState.accessToken) return;
  state.downloading[orderId] = true;
  try {
    const order = state.orders.find((o) => o.id === orderId);
    const blob = await downloadOrderPdf(authState.accessToken, orderId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `order-${order?.number || orderId}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    state.error = err?.message || 'PDF konnte nicht geladen werden';
  } finally {
    state.downloading[orderId] = false;
  }
}

async function createNewOrder() {
  if (!authState.accessToken) return;
  if (!state.createRows.length && state.recommended.length) {
    prefillRowsFromRecommended(true);
  }
  const validRows = state.createRows.filter((row) => row.itemId && row.quantity > 0);
  if (!validRows.length) {
    state.error = 'Bitte mindestens einen Artikel und eine Menge hinterlegen';
    return;
  }
  state.creating = true;
  state.error = null;
  try {
    const payload = {
      note: state.orderNote || undefined,
      items: validRows.map((row) => ({
        item_id: row.itemId,
        quantity: row.quantity,
        note: row.note || undefined
      }))
    };
    const created = await createOrder(authState.accessToken, payload);
    state.orders = [created, ...state.orders];
    state.createRows = [];
    state.orderNote = '';
    await loadRecommendations();
  } catch (err: any) {
    state.error = err?.message || 'Bestellung konnte nicht angelegt werden';
  } finally {
    state.creating = false;
  }
}

onMounted(async () => {
  await loadOrders();
  await loadRecommendations();
  await loadItems();
});
</script>

<template>
  <UiPage>
    <UiSection title="Bestellungen" subtitle="Überwache Eingänge und Ausgänge, priorisiere kritische Lieferungen.">
      <UiToolbar>
        <template #start>
          <p class="eyebrow">Einkauf & Ausgang</p>
        </template>
        <template #end>
          <div class="action-row">
            <button class="btnGhost small" type="button" @click="loadOrders" :disabled="state.loading">
              Neu laden
            </button>
            <button class="btnPrimary small" type="button" @click="createNewOrder" :disabled="state.creating">
              Bestellung anlegen
            </button>
          </div>
        </template>
      </UiToolbar>

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
      </div>

      <div class="filter-card two-column mt-md">
        <div class="stack">
          <label class="field-label">Status-Filter</label>
          <select v-model="state.filters.status" class="input">
            <option value="ALL">Alle</option>
            <option value="OPEN">Offen</option>
            <option value="COMPLETED">Erledigt</option>
            <option value="CANCELED">Storniert</option>
          </select>
        </div>
        <div class="stack">
          <label class="field-label">Suche</label>
          <input
            v-model="state.filters.search"
            type="text"
            class="input"
            placeholder="Nummer, Notiz oder Artikel suchen"
          />
          <span class="hint">Filtert alle Tabellen. Groß/Kleinschreibung egal.</span>
        </div>
      </div>

      <div class="cards-grid mt-md">
        <article class="card">
          <h3 class="card__title">Offene Bestellungen</h3>
          <p class="card__value">{{ openOrders.length }}</p>
          <p class="card__hint">Summe aller offenen Bestellungen</p>
        </article>
        <article class="card">
          <h3 class="card__title">Erledigt</h3>
          <p class="card__value">{{ completedOrders.length }}</p>
          <p class="card__hint">abgeschlossene Bestellungen</p>
        </article>
        <article class="card">
          <h3 class="card__title">Bestellwürdig</h3>
          <p class="card__value">{{ state.recommended.length }}</p>
          <p class="card__hint">Artikel unter Sollbestand</p>
        </article>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Neue Bestellung</h3>
        <p class="section-subtitle">Bestellwürdige Artikel werden automatisch vorausgewählt.</p>

        <div class="tableWrap" v-if="state.createRows.length">
          <table class="table">
            <thead>
              <tr>
                <th>Artikel</th>
                <th>Menge</th>
                <th>Notiz</th>
                <th>Aktion</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in state.createRows" :key="row.id">
                <td>
                  <select v-model="row.itemId" class="input">
                    <option value="">Bitte wählen</option>
                    <option v-for="option in selectableItems" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                </td>
                <td>
                  <input v-model.number="row.quantity" type="number" min="1" class="input" />
                </td>
                <td>
                  <input v-model="row.note" type="text" class="input" placeholder="optional" />
                </td>
                <td>
                  <button class="btnGhost small" type="button" @click="removeRow(row.id)">
                    Entfernen
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine Zeilen vorhanden. Bestellwürdige Artikel werden beim Anlegen übernommen.</p>

        <div class="action-row mt-sm">
          <button
            class="btnGhost small"
            type="button"
            @click="prefillRowsFromRecommended(true)"
            :disabled="!state.recommended.length"
          >
            Bestellwürdig übernehmen
          </button>
          <button class="btnGhost small" type="button" @click="addEmptyRow">
            + Zeile
          </button>
        </div>

        <div class="form-grid mt-sm">
          <label class="form-field span-2">
            <span class="form-label">Notiz zur Bestellung</span>
            <input v-model="state.orderNote" type="text" class="input" placeholder="optional" />
          </label>
        </div>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Offene Bestellungen</h3>
        <div class="tableWrap" v-if="filteredOpenOrders.length">
          <table class="table">
            <thead>
              <tr>
                <th>Nummer</th>
                <th>Positionen</th>
                <th>Status</th>
                <th class="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOpenOrders" :key="order.id">
                <td>{{ order.number }}</td>
                <td>{{ order.items.length }}</td>
                <td>{{ order.status }}</td>
                <td class="table-actions text-right">
                  <button class="btnGhost small" type="button" @click="downloadPdf(order.id)" :disabled="state.downloading[order.id]">
                    PDF
                  </button>
                  <button class="btnGhost small" type="button" @click="sendEmail(order.id)" :disabled="state.emailing[order.id]">
                    E-Mail
                  </button>
                  <button
                    class="btnPrimary small"
                    type="button"
                    @click="markComplete(order.id)"
                    :disabled="state.completing[order.id] || state.canceling[order.id]"
                  >
                    Erledigt
                  </button>
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="markCanceled(order.id)"
                    :disabled="state.canceling[order.id] || state.completing[order.id]"
                  >
                    Stornieren
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine offenen Bestellungen vorhanden (Filter berücksichtigen).</p>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Erledigte Bestellungen</h3>
        <div class="tableWrap" v-if="filteredCompletedOrders.length">
          <table class="table">
            <thead>
              <tr>
                <th>Nummer</th>
                <th>Positionen</th>
                <th>Status</th>
                <th class="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredCompletedOrders" :key="order.id">
                <td>{{ order.number }}</td>
                <td>{{ order.items.length }}</td>
                <td>{{ order.status }}</td>
                <td class="table-actions text-right">
                  <button class="btnGhost small" type="button" @click="downloadPdf(order.id)" :disabled="state.downloading[order.id]">
                    PDF
                  </button>
                  <button class="btnGhost small" type="button" @click="sendEmail(order.id)" :disabled="state.emailing[order.id]">
                    E-Mail
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine erledigten Bestellungen (Filter berücksichtigen).</p>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Stornierte Bestellungen</h3>
        <div class="tableWrap" v-if="filteredCanceledOrders.length">
          <table class="table">
            <thead>
              <tr>
                <th>Nummer</th>
                <th>Positionen</th>
                <th>Status</th>
                <th class="text-right">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredCanceledOrders" :key="order.id">
                <td>{{ order.number }}</td>
                <td>{{ order.items.length }}</td>
                <td>{{ order.status }}</td>
                <td class="table-actions text-right">
                  <button class="btnGhost small" type="button" @click="downloadPdf(order.id)" :disabled="state.downloading[order.id]">
                    PDF
                  </button>
                  <button class="btnGhost small" type="button" @click="sendEmail(order.id)" :disabled="state.emailing[order.id]">
                    E-Mail
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine stornierten Bestellungen (Filter berücksichtigen).</p>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Bestellwürdig</h3>
        <div class="tableWrap" v-if="state.recommended.length">
          <table class="table">
            <thead>
              <tr>
                <th>Artikel</th>
                <th>Barcode</th>
                <th>Bestand</th>
                <th>Soll</th>
                <th>Empfohlen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in state.recommended" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.barcode }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.target_stock }}</td>
                <td>{{ item.recommended_qty }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine bestellwürdigen Artikel.</p>
      </div>
    </UiSection>
  </UiPage>
</template>
