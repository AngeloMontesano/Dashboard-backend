<script setup lang="ts">
import { onMounted, reactive } from 'vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiStatCard from '@/components/ui/UiStatCard.vue';
import { useAuth } from '@/composables/useAuth';
import {
  fetchItems,
  fetchMovements,
  fetchReorderRecommendations,
  listOrders,
  type Item,
  type MovementOut
} from '@/api/inventory';

const { state: authState } = useAuth();

type DashboardMetrics = {
  openOrders: number;
  recommended: number;
  stablePercent: number;
  movementsToday: number;
  totalItems: number;
  belowMin: number;
};

const state = reactive<{
  metrics: DashboardMetrics;
  loading: boolean;
  error: string | null;
}>({
  metrics: {
    openOrders: 0,
    recommended: 0,
    stablePercent: 0,
    movementsToday: 0,
    totalItems: 0,
    belowMin: 0
  },
  loading: false,
  error: null
});

async function fetchAllItems() {
  if (!authState.accessToken) return [];
  const pageSize = 200;
  let page = 1;
  let total = 0;
  const items: Awaited<ReturnType<typeof fetchItems>>['items'] = [];
  do {
    const res = await fetchItems({
      token: authState.accessToken,
      page,
      page_size: pageSize,
      active: null
    });
    items.push(...res.items);
    total = res.total;
    page += 1;
  } while (items.length < total && page <= 25); // safety cap to avoid runaway calls
  return items;
}

function calculateStablePercent(total: number, belowMin: number) {
  if (total === 0) return 100;
  const healthy = total - belowMin;
  const percent = Math.max(0, Math.min(100, Math.round((healthy / total) * 100)));
  return percent;
}

function countBelowMin(items: Awaited<ReturnType<typeof fetchItems>>['items']) {
  return items.filter((item) => item.quantity < item.min_stock).length;
}

async function loadMovementsToday(): Promise<number> {
  if (!authState.accessToken) return 0;
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const movements: MovementOut[] = await fetchMovements({
    token: authState.accessToken,
    start: start.toISOString(),
    limit: 500
  });
  return movements.length;
}

function deriveRecommendations(items: Item[]): number {
  return items.filter(
    (item) =>
      item.is_active &&
      item.order_mode !== 0 &&
      item.target_stock > 0 &&
      item.quantity < item.target_stock
  ).length;
}

async function loadDashboard() {
  if (!authState.accessToken) return;
  state.loading = true;
  const errors: string[] = [];
  try {
    let openOrders = [];
    let reorderCount = 0;
    let items: Item[] = [];
    let movementsToday = 0;

    try {
      openOrders = await listOrders(authState.accessToken, 'OPEN');
    } catch (err: any) {
      errors.push(`Bestellungen: ${err?.message || 'nicht erreichbar'}`);
    }

    try {
      const res = await fetchReorderRecommendations(authState.accessToken);
      reorderCount = res.items?.length ?? 0;
    } catch (err: any) {
      errors.push(`Bestellwürdig: ${err?.message || 'nicht erreichbar'}`);
    }

    try {
      items = await fetchAllItems();
    } catch (err: any) {
      errors.push(`Artikel: ${err?.message || 'nicht ladbar'}`);
    }

    try {
      movementsToday = await loadMovementsToday();
    } catch (err: any) {
      errors.push(`Bewegungen: ${err?.message || 'nicht ladbar'}`);
    }

    if (reorderCount === 0 && items.length) {
      reorderCount = deriveRecommendations(items);
    }

    const belowMin = countBelowMin(items);
    state.metrics = {
      openOrders: openOrders.length,
      recommended: reorderCount,
      stablePercent: calculateStablePercent(items.length, belowMin),
      movementsToday,
      totalItems: items.length,
      belowMin
    };
  } catch (err: any) {
    errors.push(err?.message || 'Unbekannter Fehler');
  } finally {
    state.error = errors.length ? errors.join(' | ') : null;
    state.loading = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <UiPage>
    <UiSection title="Dashboard" subtitle="Wichtigste Kennzahlen für dein Lager auf einen Blick.">
      <template #actions>
        <button class="button button--primary" type="button" @click="loadDashboard" :disabled="state.loading">
          {{ state.loading ? 'Aktualisiere...' : 'Aktualisieren' }}
        </button>
      </template>

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
      </div>

      <div class="card-grid">
        <UiStatCard
          label="Offene Bestellungen"
          :value="state.metrics.openOrders.toLocaleString('de-DE')"
          :hint="state.loading ? 'Lade...' : 'Aktuell offene Bestellungen'"
          to="/bestellungen"
        />
        <UiStatCard
          label="Bestände stabil"
          :value="`${state.metrics.stablePercent} %`"
          :hint="`Unter Min: ${state.metrics.belowMin} / ${state.metrics.totalItems}`"
        />
        <UiStatCard
          label="Bewegungen heute"
          :value="state.metrics.movementsToday.toLocaleString('de-DE')"
          :hint="state.loading ? 'Lade...' : 'Ein- und Ausgänge seit 00:00'"
          to="/lagerbewegungen"
        />
        <UiStatCard
          label="Bestellwürdig"
          :value="state.metrics.recommended.toLocaleString('de-DE')"
          hint="Artikel unter Sollbestand"
          :to="{ path: '/bestellungen', query: { tab: 'bestellwuerdig' } }"
        />
      </div>
    </UiSection>
  </UiPage>
</template>
