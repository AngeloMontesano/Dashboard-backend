<script setup lang="ts">
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import type { ReportKpis } from '@/types/reports';

const props = withDefaults(
  defineProps<{
    kpis: ReportKpis | null;
    loading?: boolean;
  }>(),
  {
    loading: false
  }
);

const numberFormatter = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });
const decimalFormatter = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1 });

function formatValue(value: number) {
  return numberFormatter.format(value || 0);
}

function formatAverage(value: number) {
  return decimalFormatter.format(value || 0);
}
</script>

<template>
  <div class="kpi-grid">
    <Card class="kpi-card">
      <template #title>Gesamtverbrauch</template>
      <template #content>
        <div class="kpi-value">
          <ProgressSpinner v-if="loading" style="width: 24px; height: 24px" strokeWidth="6" />
          <span v-else>{{ formatValue(kpis?.totalConsumption || 0) }}</span>
        </div>
        <p class="kpi-subtitle">Summe aller OUT Bewegungen</p>
      </template>
    </Card>

    <Card class="kpi-card">
      <template #title>Ø Verbrauch pro Monat</template>
      <template #content>
        <div class="kpi-value">
          <ProgressSpinner v-if="loading" style="width: 24px; height: 24px" strokeWidth="6" />
          <span v-else>{{ formatAverage(kpis?.averagePerMonth || 0) }}</span>
        </div>
        <p class="kpi-subtitle">Über {{ kpis?.months.length || 0 }} Monate</p>
      </template>
    </Card>

    <Card class="kpi-card">
      <template #title>Top Artikel</template>
      <template #content>
        <div class="kpi-value">
          <ProgressSpinner v-if="loading" style="width: 24px; height: 24px" strokeWidth="6" />
          <span v-else>{{ kpis?.topItem?.name || '—' }}</span>
        </div>
        <p class="kpi-subtitle">
          {{ kpis?.topItem ? `${formatValue(kpis.topItem.quantity)} Einheiten` : 'Noch keine Daten' }}
        </p>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.kpi-card {
  height: 100%;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.kpi-subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-secondary-color, #6b7280);
}
</style>
