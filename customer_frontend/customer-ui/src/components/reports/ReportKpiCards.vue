<script setup lang="ts">
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
    <article class="card kpi-card">
      <header class="cardHeader">
        <div class="cardTitle">Gesamtverbrauch</div>
      </header>
      <div class="kpi-value">
        <span v-if="loading" class="spinner" aria-label="Laden"></span>
        <span v-else>{{ formatValue(kpis?.totalConsumption || 0) }}</span>
      </div>
      <p class="kpi-subtitle">Summe aller OUT Bewegungen</p>
    </article>

    <article class="card kpi-card">
      <header class="cardHeader">
        <div class="cardTitle">Ø Verbrauch pro Monat</div>
      </header>
      <div class="kpi-value">
        <span v-if="loading" class="spinner" aria-label="Laden"></span>
        <span v-else>{{ formatAverage(kpis?.averagePerMonth || 0) }}</span>
      </div>
      <p class="kpi-subtitle">Über {{ kpis?.months.length || 0 }} Monate</p>
    </article>

    <article class="card kpi-card">
      <header class="cardHeader">
        <div class="cardTitle">Top Artikel</div>
      </header>
      <div class="kpi-value">
        <span v-if="loading" class="spinner" aria-label="Laden"></span>
        <span v-else>{{ kpis?.topItem?.name || '—' }}</span>
      </div>
      <p class="kpi-subtitle">
        {{ kpis?.topItem ? `${formatValue(kpis.topItem.quantity)} Einheiten` : 'Noch keine Daten' }}
      </p>
    </article>
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
  min-height: 48px;
}

.kpi-subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
}

.spinner {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
