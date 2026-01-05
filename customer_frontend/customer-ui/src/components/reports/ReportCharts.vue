<script setup lang="ts">
import { computed } from 'vue';
import Card from 'primevue/card';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';
import 'chart.js/auto';
import type { ChartData, ChartOptions } from 'chart.js';

const props = withDefaults(
  defineProps<{
    consumptionData: ChartData<'bar'> | null;
    trendData: ChartData<'line'> | null;
    loading?: boolean;
    error?: string | null;
  }>(),
  {
    loading: false,
    error: null
  }
);

const barOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  plugins: {
    legend: {
      position: 'top'
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    x: {
      stacked: (props.consumptionData?.datasets?.length || 0) > 1
    },
    y: {
      beginAtZero: true
    }
  }
}));

const lineOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  plugins: {
    legend: {
      position: 'top'
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}));
</script>

<template>
  <div class="charts-grid">
    <Card class="chart-card">
      <template #title>Verbrauchsanalyse</template>
      <template #subtitle>Balken pro Monat je nach Modus aggregiert oder pro Artikel.</template>
      <template #content>
        <div v-if="loading" class="chart-placeholder">
          <ProgressSpinner />
        </div>
        <div v-else-if="error" class="chart-placeholder error">{{ error }}</div>
        <div v-else-if="consumptionData && consumptionData.labels?.length" class="chart-wrapper">
          <Chart type="bar" :data="consumptionData" :options="barOptions" />
        </div>
        <div v-else class="chart-placeholder">Keine Daten für den Zeitraum.</div>
      </template>
    </Card>

    <Card class="chart-card">
      <template #title>Trendanalyse</template>
      <template #subtitle>Linienchart nach Auswahlmodus (Top5, Alle oder Selektiert).</template>
      <template #content>
        <div v-if="loading" class="chart-placeholder">
          <ProgressSpinner />
        </div>
        <div v-else-if="error" class="chart-placeholder error">{{ error }}</div>
        <div v-else-if="trendData && trendData.labels?.length" class="chart-wrapper">
          <Chart type="line" :data="trendData" :options="lineOptions" />
        </div>
        <div v-else class="chart-placeholder">Keine Zeitreihen verfügbar.</div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.chart-card {
  height: 100%;
}

.chart-wrapper {
  width: 100%;
}

.chart-placeholder {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary-color, #6b7280);
}

.chart-placeholder.error {
  color: var(--color-danger, #dc2626);
}
</style>
