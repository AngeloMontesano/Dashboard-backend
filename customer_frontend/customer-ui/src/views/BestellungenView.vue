<script setup lang="ts">
import { onMounted, reactive, computed, ref } from 'vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import UiEmptyState from '@/components/ui/UiEmptyState.vue';
import BaseField from '@/components/common/BaseField.vue';
import BaseInput from '@/components/common/BaseInput.vue';
import BaseSelect from '@/components/common/BaseSelect.vue';
import { useAuth } from '@/composables/useAuth';
import AuthReauthBanner from '@/components/auth/AuthReauthBanner.vue';
import { useAuthIssueBanner } from '@/composables/useAuthIssueBanner';
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
const { authIssue, authMessage, handleAuthError } = useAuthIssueBanner();

type Order = Awaited<ReturnType<typeof listOrders>>[number];
type ReorderItem = Awaited<ReturnType<typeof fetchReorderRecommendations>>['items'][number];
type ItemOption = Awaited<ReturnType<typeof fetchItems>>['items'][number];
type OrderRow = { id: string; itemId: string | null; quantity: number; note: string };
type FilterStatus = 'ALL' | 'OPEN' | 'COMPLETED' | 'CANCELED';

const statusOptions: { label: string; value: FilterStatus }[] = [
  { label: 'Alle', value: 'ALL' },
  { label: 'Offen', value: 'OPEN' },
  { label: 'Erledigt', value: 'COMPLETED' },
  { label: 'Storniert', value: 'CANCELED' }
];

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
  filters: { status: FilterStatus; search: string };
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
const hasItemSelection = (row: OrderRow): row is OrderRow & { itemId: string } => Boolean(row.itemId);

const selectableItems = computed(() => {
  const map = new Map<string, { value: string; label: string }>();
  const pushItem = (item: { id: string; name: string; quantity?: number | null; sku?: string | null }) => {
    if (!item?.id) return;
    const id = String(item.id);
    if (map.has(id)) return;
    const parts = [item.name];
    if (typeof item.quantity === 'number') parts.push(`Bestand ${item.quantity}`);
    if (item.sku) parts.push(`SKU ${item.sku}`);
    map.set(id, { value: id, label: parts.join(' • ') });
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

const statusClass = (status: Order['status']) => {
  if (status === 'COMPLETED') return 'status-pill status-pill--success';
  if (status === 'CANCELED') return 'status-pill status-pill--danger';
  return 'status-pill status-pill--info';
};

function showError(err: unknown, fallback: string) {
  const classified = handleAuthError(err);
  const detail = classified.detailMessage || classified.userMessage || fallback;
  state.error = classified.category === 'auth' ? classified.userMessage : `${fallback}: ${detail}`;
  return classified;
}

async function loadOrders() {
  if (!authState.accessToken) return;
  if (state.loading) return;
  state.loading = true;
  state.error = null;
  try {
    state.orders = await listOrders(authState.accessToken);
  } catch (err: any) {
    showError(err, 'Bestellungen konnten nicht geladen werden');
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
  } catch (err: any) {
    const classified = handleAuthError(err);
    if (classified.category === 'auth') {
      state.error = classified.userMessage;
    } else if (state.items.length) {
      // Fallback auf lokale Items, falls Endpoint (z.B. wegen Migration) fehlt
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
  } catch (err: any) {
    const classified = handleAuthError(err);
    if (classified.category === 'auth') {
      state.error = classified.userMessage;
    } else {
      state.items = [];
    }
  }

  if (!state.createRows.length) {
    prefillRowsFromRecommended();
  }
}

function prefillRowsFromRecommended(force = false) {
  if (!state.recommended.length) return;
  if (state.createRows.length && !force) return;
  const existingIds = new Set(
    state.createRows
      .map((row) => row.itemId)
      .filter(Boolean) as string[]
  );
  const additions = state.recommended
    .filter((item) => !existingIds.has(String(item.id)))
    .map((item) => ({
      id: nextRowId(),
      itemId: String(item.id),
      quantity: Math.max(item.recommended_qty || item.quantity || 1, 1),
      note: ''
    }));
  if (additions.length) {
    state.createRows = [...state.createRows, ...additions];
  }
}

function addEmptyRow() {
  state.createRows = [...state.createRows, { id: nextRowId(), itemId: null, quantity: 1, note: '' }];
}

function removeRow(rowId: string) {
  state.createRows = state.createRows.filter((row) => row.id !== rowId);
  if (confirmRemoveRow.value === rowId) {
    confirmRemoveRow.value = null;
  }
}

async function markComplete(orderId: string) {
  if (!authState.accessToken) return;
  state.completing[orderId] = true;
  try {
    const updated = await completeOrder(authState.accessToken, orderId);
    state.orders = state.orders.map((o) => (o.id === updated.id ? updated : o));
  } catch (err: any) {
    showError(err, 'Erledigen fehlgeschlagen');
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
    showError(err, 'Stornieren fehlgeschlagen');
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
      showError(res.error, 'E-Mail-Versand fehlgeschlagen');
    }
  } catch (err: any) {
    showError(err, 'E-Mail-Versand fehlgeschlagen');
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
    showError(err, 'PDF konnte nicht geladen werden');
  } finally {
    state.downloading[orderId] = false;
  }
}

async function createNewOrder() {
  if (!authState.accessToken) return;
  if (!state.createRows.length && state.recommended.length) {
    prefillRowsFromRecommended(true);
  }
  const validRows = state.createRows.filter(hasItemSelection).filter((row) => row.quantity > 0);
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
    showError(err, 'Bestellung konnte nicht angelegt werden');
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
            <button
              class="btnGhost small"
              type="button"
              @click="loadOrders"
              :disabled="state.loading"
              :aria-busy="state.loading"
            >
              <span class="btn-label">
                <span v-if="state.loading" class="btn-spinner" aria-hidden="true"></span>
                Neu laden
              </span>
            </button>
            <button
              class="btnPrimary small"
              type="button"
              @click="createNewOrder"
              :disabled="state.creating"
              :aria-busy="state.creating"
            >
              <span class="btn-label">
                <span v-if="state.creating" class="btn-spinner" aria-hidden="true"></span>
                Bestellung anlegen
              </span>
            </button>
          </div>
        </template>
      </UiToolbar>

      <AuthReauthBanner
        v-if="authIssue"
        class="mt-sm"
        :message="authMessage"
        retry-label="Neu laden"
        @retry="() => loadOrders()"
      />

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
      </div>

      <div class="form-grid mt-md">
        <BaseField label="Status-Filter">
          <BaseSelect v-model="state.filters.status" :options="statusOptions" />
        </BaseField>
        <BaseField label="Suche">
          <BaseInput
            v-model="state.filters.search"
            type="text"
            placeholder="Nummer, Notiz oder Artikel"
            autocomplete="off"
          />
        </BaseField>
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
                  <BaseSelect v-model="row.itemId" :options="selectableItems" placeholder="Artikel auswählen" />
                </td>
                <td>
                  <BaseInput v-model.number="row.quantity" type="number" min="1" />
                </td>
                <td>
                  <BaseInput v-model="row.note" type="text" placeholder="Notiz (optional)" />
                </td>
                <td>
                  <div class="table-actions">
                    <button
                      class="btnGhost small danger"
                      type="button"
                      @click="confirmRemoveRow === row.id ? removeRow(row.id) : (confirmRemoveRow = row.id)"
                    >
                      {{ confirmRemoveRow === row.id ? 'Jetzt entfernen' : 'Entfernen' }}
                    </button>
                    <span v-if="confirmRemoveRow === row.id" class="inline-confirm">Nochmal klicken zum Bestätigen.</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine Positionen ausgewählt"
          description="Bestellwürdige Artikel werden automatisch vorgeschlagen."
        />

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
          <BaseField label="Notiz zur Bestellung">
            <BaseInput v-model="state.orderNote" type="text" placeholder="optional" />
          </BaseField>
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
                <td><span :class="statusClass(order.status)">{{ order.status }}</span></td>
                <td class="table-actions">
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="downloadPdf(order.id)"
                    :disabled="state.downloading[order.id]"
                    :aria-busy="state.downloading[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.downloading[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      PDF
                    </span>
                  </button>
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="sendEmail(order.id)"
                    :disabled="state.emailing[order.id]"
                    :aria-busy="state.emailing[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.emailing[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      E-Mail
                    </span>
                  </button>
                  <button
                    class="btnPrimary small"
                    type="button"
                    @click="markComplete(order.id)"
                    :disabled="state.completing[order.id] || state.canceling[order.id]"
                    :aria-busy="state.completing[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.completing[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      Erledigt
                    </span>
                  </button>
                  <button
                    class="btnGhost small danger"
                    type="button"
                    @click="markCanceled(order.id)"
                    :disabled="state.canceling[order.id] || state.completing[order.id]"
                    :aria-busy="state.canceling[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.canceling[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      Stornieren
                    </span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine offenen Bestellungen"
          description="Filter berücksichtigen oder neue Bestellung anlegen."
        >
          <template #actions>
            <button class="btnPrimary small" type="button" @click="createNewOrder" :disabled="state.creating">
              Bestellung anlegen
            </button>
            <button class="btnGhost small" type="button" @click="loadOrders" :disabled="state.loading">
              Neu laden
            </button>
          </template>
        </UiEmptyState>
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
                <td><span :class="statusClass(order.status)">{{ order.status }}</span></td>
                <td class="table-actions">
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="downloadPdf(order.id)"
                    :disabled="state.downloading[order.id]"
                    :aria-busy="state.downloading[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.downloading[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      PDF
                    </span>
                  </button>
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="sendEmail(order.id)"
                    :disabled="state.emailing[order.id]"
                    :aria-busy="state.emailing[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.emailing[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      E-Mail
                    </span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine erledigten Bestellungen"
          description="Filter prüfen oder abgeschlossene Bestellungen später erneut laden."
        >
          <template #actions>
            <button class="btnGhost small" type="button" @click="loadOrders" :disabled="state.loading">
              Neu laden
            </button>
          </template>
        </UiEmptyState>
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
                <td><span :class="statusClass(order.status)">{{ order.status }}</span></td>
                <td class="table-actions">
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="downloadPdf(order.id)"
                    :disabled="state.downloading[order.id]"
                    :aria-busy="state.downloading[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.downloading[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      PDF
                    </span>
                  </button>
                  <button
                    class="btnGhost small"
                    type="button"
                    @click="sendEmail(order.id)"
                    :disabled="state.emailing[order.id]"
                    :aria-busy="state.emailing[order.id]"
                  >
                    <span class="btn-label">
                      <span v-if="state.emailing[order.id]" class="btn-spinner" aria-hidden="true"></span>
                      E-Mail
                    </span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine stornierten Bestellungen"
          description="Filter berücksichtigen oder offene Bestellungen zur Kontrolle laden."
        >
          <template #actions>
            <button class="btnGhost small" type="button" @click="loadOrders" :disabled="state.loading">
              Neu laden
            </button>
          </template>
        </UiEmptyState>
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
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine bestellwürdigen Artikel"
          description="Alle Artikel liegen aktuell auf oder über dem Sollbestand."
        >
          <template #actions>
            <button class="btnGhost small" type="button" @click="loadRecommendations">
              Empfohlene Artikel neu laden
            </button>
          </template>
        </UiEmptyState>
      </div>
    </UiSection>
  </UiPage>
</template>
