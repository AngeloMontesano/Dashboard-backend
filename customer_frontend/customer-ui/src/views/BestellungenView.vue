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
  fetchReorderRecommendations
} from '@/api/inventory';

const { state: authState } = useAuth();

type Order = Awaited<ReturnType<typeof listOrders>>[number];
type ReorderItem = Awaited<ReturnType<typeof fetchReorderRecommendations>>['items'][number];

const state = reactive<{
  orders: Order[];
  loading: boolean;
  error: string | null;
  emailing: Record<string, boolean>;
  recommended: ReorderItem[];
  downloading: Record<string, boolean>;
}>({
  orders: [],
  loading: false,
  error: null,
  emailing: {},
  recommended: [],
  downloading: {}
});

const openOrders = computed(() => state.orders.filter((o) => o.status === 'OPEN'));
const completedOrders = computed(() => state.orders.filter((o) => o.status === 'COMPLETED'));

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
  } catch {
    state.recommended = [];
  }
}

async function markComplete(orderId: string) {
  if (!authState.accessToken) return;
  state.loading = true;
  try {
    const updated = await completeOrder(authState.accessToken, orderId);
    state.orders = state.orders.map((o) => (o.id === updated.id ? updated : o));
  } catch (err: any) {
    state.error = err?.message || 'Erledigen fehlgeschlagen';
  } finally {
    state.loading = false;
  }
}

async function markCanceled(orderId: string) {
  if (!authState.accessToken) return;
  state.loading = true;
  try {
    const updated = await cancelOrder(authState.accessToken, orderId);
    state.orders = state.orders.map((o) => (o.id === updated.id ? updated : o));
  } catch (err: any) {
    state.error = err?.message || 'Stornieren fehlgeschlagen';
  } finally {
    state.loading = false;
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
    const blob = await downloadOrderPdf(authState.accessToken, orderId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `order-${orderId}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    state.error = err?.message || 'PDF konnte nicht geladen werden';
  } finally {
    state.downloading[orderId] = false;
  }
}

onMounted(async () => {
  await loadOrders();
  await loadRecommendations();
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
            <button class="button button--ghost" type="button" @click="loadOrders" :disabled="state.loading">
              Neu laden
            </button>
          </div>
        </template>
      </UiToolbar>

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
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
        <h3 class="eyebrow">Offene Bestellungen</h3>
        <div class="table-wrapper" v-if="openOrders.length">
          <table class="table">
            <thead>
              <tr>
                <th>Nummer</th>
                <th>Positionen</th>
                <th>Status</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in openOrders" :key="order.id">
                <td>{{ order.number }}</td>
                <td>{{ order.items.length }}</td>
                <td>{{ order.status }}</td>
                <td class="table-actions">
                  <button class="button button--ghost" type="button" @click="downloadPdf(order.id)" :disabled="state.downloading[order.id]">
                    PDF
                  </button>
                  <button class="button button--ghost" type="button" @click="sendEmail(order.id)" :disabled="state.emailing[order.id]">
                    E-Mail
                  </button>
                  <button class="button button--primary" type="button" @click="markComplete(order.id)" :disabled="state.loading">
                    Erledigt
                  </button>
                  <button class="button button--ghost" type="button" @click="markCanceled(order.id)" :disabled="state.loading">
                    Stornieren
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="placeholder mt-sm">Keine offenen Bestellungen vorhanden.</p>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Bestellwürdig</h3>
        <div class="table-wrapper" v-if="state.recommended.length">
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
