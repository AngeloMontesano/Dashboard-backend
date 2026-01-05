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

async function loadDashboard() {
  if (!authState.accessToken) return;
  state.loading = true;
  state.error = null;
  try {
    const [openOrders, reorder, items, movementsToday] = await Promise.all([
      listOrders(authState.accessToken, 'OPEN'),
      fetchReorderRecommendations(authState.accessToken),
      fetchAllItems(),
      loadMovementsToday()
    ]);

    const belowMin = countBelowMin(items);
    state.metrics = {
      openOrders: openOrders.length,
      recommended: reorder.items?.length ?? 0,
      stablePercent: calculateStablePercent(items.length, belowMin),
      movementsToday,
      totalItems: items.length,
      belowMin
    };
  } catch (err: any) {
    state.error = err?.message || 'Dashboard-Daten konnten nicht geladen werden.';
  } finally {
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
        />
        <UiStatCard
          label="Bestellwürdig"
          :value="state.metrics.recommended.toLocaleString('de-DE')"
          hint="Artikel unter Sollbestand"
        />
      </div>
    </UiSection>
  </UiPage>
</template>
