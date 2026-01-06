<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Chart, registerables, type ChartData, type ChartOptions } from 'chart.js';

Chart.register(...registerables);

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

const barCanvas = ref<HTMLCanvasElement | null>(null);
const lineCanvas = ref<HTMLCanvasElement | null>(null);
const barChart = ref<Chart<'bar'> | null>(null);
const lineChart = ref<Chart<'line'> | null>(null);

const barOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    tooltip: { mode: 'index', intersect: false }
  },
  scales: {
    x: { stacked: (props.consumptionData?.datasets?.length || 0) > 1 },
    y: { beginAtZero: true }
  }
}));

const lineOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    tooltip: { mode: 'index', intersect: false }
  },
  scales: { y: { beginAtZero: true } }
}));

function destroyBar() {
  if (barChart.value) {
    barChart.value.destroy();
    barChart.value = null;
  }
}

function destroyLine() {
  if (lineChart.value) {
    lineChart.value.destroy();
    lineChart.value = null;
  }
}

function renderCharts() {
  if (barCanvas.value && props.consumptionData && props.consumptionData.labels?.length) {
    destroyBar();
    barChart.value = new Chart(barCanvas.value, {
      type: 'bar',
      data: props.consumptionData,
      options: barOptions.value
    });
  } else {
    destroyBar();
  }

  if (lineCanvas.value && props.trendData && props.trendData.labels?.length) {
    destroyLine();
    lineChart.value = new Chart(lineCanvas.value, {
      type: 'line',
      data: props.trendData,
      options: lineOptions.value
    });
  } else {
    destroyLine();
  }
}

watch(
  () => [props.consumptionData, props.trendData, barOptions.value, lineOptions.value, props.loading, props.error],
  () => {
    if (props.loading || props.error) {
      destroyBar();
      destroyLine();
      return;
    }
    void nextTick(renderCharts);
  }
);

onMounted(() => {
  renderCharts();
});

onBeforeUnmount(() => {
  destroyBar();
  destroyLine();
});
</script>

<template>
  <div class="charts-grid">
    <article class="card chart-card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Verbrauchsanalyse</div>
          <div class="cardHint">Balken pro Monat je nach Modus aggregiert oder pro Artikel.</div>
        </div>
      </header>
      <div class="chart-body">
        <div v-if="loading" class="chart-placeholder">
          <span class="spinner" aria-label="Laden"></span>
        </div>
        <div v-else-if="error" class="chart-placeholder error">{{ error }}</div>
        <div v-else-if="consumptionData && consumptionData.labels?.length" class="chart-wrapper">
          <canvas ref="barCanvas" />
        </div>
        <div v-else class="chart-placeholder">Keine Daten für den Zeitraum.</div>
      </div>
    </article>

    <article class="card chart-card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Trendanalyse</div>
          <div class="cardHint">Linienchart nach Auswahlmodus (Top5, Alle oder Selektiert).</div>
        </div>
      </header>
      <div class="chart-body">
        <div v-if="loading" class="chart-placeholder">
          <span class="spinner" aria-label="Laden"></span>
        </div>
        <div v-else-if="error" class="chart-placeholder error">{{ error }}</div>
        <div v-else-if="trendData && trendData.labels?.length" class="chart-wrapper">
          <canvas ref="lineCanvas" />
        </div>
        <div v-else class="chart-placeholder">Keine Zeitreihen verfügbar.</div>
      </div>
    </article>
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

.chart-body {
  min-height: 260px;
}

.chart-wrapper {
  width: 100%;
}

.chart-placeholder {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.chart-placeholder.error {
  color: var(--danger);
}

.spinner {
  width: 32px;
  height: 32px;
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
