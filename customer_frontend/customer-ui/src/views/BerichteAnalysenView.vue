<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';
import type { ChartData } from 'chart.js';
import { getReportData, exportCsv, exportExcel, exportPdf } from '@/api/reports';
import { fetchCategories, fetchItems, type Item } from '@/api/inventory';
import ReportFilters from '@/components/reports/ReportFilters.vue';
import ReportKpiCards from '@/components/reports/ReportKpiCards.vue';
import ReportCharts from '@/components/reports/ReportCharts.vue';
import ReportExportButtons from '@/components/reports/ReportExportButtons.vue';
import { useAuth } from '@/composables/useAuth';
import type { CategoryOption, ItemOption, ReportFilterState, ReportParams, ReportResponse } from '@/types/reports';

const { state: authState } = useAuth();
const toast = useToast();

const defaultRange = getDefaultRange();
const filters = reactive<ReportFilterState>({
  dateRange: [...defaultRange] as [Date, Date],
  appliedRange: [...defaultRange] as [Date, Date],
  mode: 'top5',
  categoryId: null,
  selectedItems: [],
  aggregateAll: true,
  topLimit: 5
});

const categories = ref<CategoryOption[]>([]);
const itemSuggestions = ref<ItemOption[]>([]);
const reportData = ref<ReportResponse | null>(null);
const loading = ref(false);
const applying = ref(false);
const error = ref<string | null>(null);
const exporting = ref<'csv' | 'excel' | 'pdf' | null>(null);
const consumptionChart = ref<ChartData<'bar'> | null>(null);
const trendChart = ref<ChartData<'line'> | null>(null);
let debounceTimer: number | undefined;

const allItemOptions = computed<ItemOption[]>(() => {
  const map = new Map<string, ItemOption>();
  for (const item of itemSuggestions.value) {
    map.set(item.value, item);
  }
  for (const item of filters.selectedItems) {
    map.set(item.value, item);
  }
  return Array.from(map.values());
});

function getDefaultRange(): [Date, Date] {
  const end = new Date();
  const start = new Date(end.getFullYear(), end.getMonth() - 5, 1);
  return [start, end];
}

function formatDateParam(date: Date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function buildParams(): ReportParams | null {
  const [start, end] = filters.appliedRange;
  if (!start || !end) return null;
  return {
    start: formatDateParam(start),
    end: formatDateParam(end),
    mode: filters.mode,
    category_id: filters.categoryId || undefined,
    item_ids: filters.mode === 'selected' ? filters.selectedItems.map((i) => i.value) : undefined,
    aggregate: filters.mode === 'all' ? filters.aggregateAll : undefined,
    limit: filters.mode === 'top5' ? filters.topLimit : undefined
  };
}

function triggerDebouncedLoad() {
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(() => {
    void loadReports();
  }, 300);
}

async function loadCategories() {
  if (!authState.accessToken) return;
  try {
    const res = await fetchCategories(authState.accessToken);
    categories.value = res
      .filter((c) => c.is_active)
      .map((c) => ({ label: c.name, value: c.id } satisfies CategoryOption));
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Kategorien fehlgeschlagen',
      detail: err?.message || 'Kategorien konnten nicht geladen werden',
      life: 5000
    });
  }
}

async function searchItems(query: string) {
  if (!authState.accessToken) return;
  try {
    const res = await fetchItems({
      token: authState.accessToken,
      q: query,
      category_id: filters.categoryId || undefined,
      active: true,
      page: 1,
      page_size: 20
    });
    itemSuggestions.value = res.items.map(toItemOption);
  } catch (err: any) {
    toast.add({
      severity: 'warn',
      summary: 'Suche fehlgeschlagen',
      detail: err?.message || 'Artikel konnten nicht gesucht werden',
      life: 4000
    });
  }
}

function toItemOption(item: Item): ItemOption {
  return {
    value: item.id,
    label: `${item.name} (${item.sku})`,
    categoryId: item.category_id || null
  };
}

async function selectCategoryItems() {
  if (!authState.accessToken || !filters.categoryId) return;
  try {
    const res = await fetchItems({
      token: authState.accessToken,
      category_id: filters.categoryId,
      active: true,
      page: 1,
      page_size: 100
    });
    const options = res.items.map(toItemOption);
    const merged = [...filters.selectedItems];
    options.forEach((opt) => {
      if (!merged.find((m) => m.value === opt.value)) merged.push(opt);
    });
    filters.selectedItems = merged;
    triggerDebouncedLoad();
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Kategorie-Übernahme fehlgeschlagen',
      detail: err?.message || 'Artikel der Kategorie konnten nicht geladen werden',
      life: 5000
    });
  }
}

function addSelectedItem(item: ItemOption) {
  if (filters.selectedItems.find((i) => i.value === item.value)) return;
  filters.selectedItems = [...filters.selectedItems, item];
  triggerDebouncedLoad();
}

function applyDateRange() {
  if (!filters.dateRange[0] || !filters.dateRange[1]) {
    toast.add({ severity: 'warn', summary: 'Zeitraum fehlt', detail: 'Bitte Zeitraum auswählen.', life: 3500 });
    return;
  }
  filters.appliedRange = [...filters.dateRange];
  applying.value = true;
  loadReports().finally(() => {
    applying.value = false;
  });
}

function extractMonths(series: ReportResponse): string[] {
  const months = new Set<string>();
  series.series.forEach((s) => s.data.forEach((p) => months.add(p.period)));
  series.kpis.months.forEach((m) => months.add(m));
  return Array.from(months).sort();
}

function buildCharts(data: ReportResponse) {
  const palette = ['#3b82f6', '#22c55e', '#a855f7', '#f59e0b', '#ef4444', '#14b8a6', '#6366f1', '#0ea5e9'];
  const labels = data.kpis.months && data.kpis.months.length ? data.kpis.months : extractMonths(data);

  const datasets = data.series.map((serie, index) => {
    const values = labels.map((month) => serie.data.find((p) => p.period === month)?.value || 0);
    const color = palette[index % palette.length];
    return {
      label: serie.label,
      data: values,
      backgroundColor: color,
      borderColor: color,
      borderWidth: 2,
      tension: 0.25,
      fill: false
    };
  });

  consumptionChart.value = {
    labels,
    datasets: datasets.map((d) => ({ ...d, type: 'bar' }))
  } as ChartData<'bar'>;

  trendChart.value = {
    labels,
    datasets: datasets.map((d) => ({ ...d, type: 'line' }))
  } as ChartData<'line'>;
}

async function loadReports() {
  if (!authState.accessToken) return;
  const params = buildParams();
  if (!params) return;
  loading.value = true;
  error.value = null;
  try {
    const res = await getReportData(authState.accessToken, params);
    const months = res.kpis.months && res.kpis.months.length ? res.kpis.months : extractMonths(res);
    reportData.value = { ...res, kpis: { ...res.kpis, months } };
    buildCharts(reportData.value);
  } catch (err: any) {
    const detail = err?.response?.data?.error?.message || err?.message || 'Konnte Bericht nicht laden';
    error.value = detail;
    toast.add({ severity: 'error', summary: 'Fehler beim Laden', detail, life: 6000 });
  } finally {
    loading.value = false;
  }
}

async function handleExport(format: 'csv' | 'excel' | 'pdf') {
  if (!authState.accessToken) return;
  const params = buildParams();
  if (!params) return;
  exporting.value = format;
  try {
    const action = format === 'csv' ? exportCsv : format === 'excel' ? exportExcel : exportPdf;
    const blob = await action(authState.accessToken, params);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    const extension = format === 'excel' ? 'xlsx' : format;
    link.href = url;
    link.download = `berichte-${params.start}-${params.end}.${extension}`;
    link.click();
    window.URL.revokeObjectURL(url);
    toast.add({ severity: 'success', summary: 'Export gestartet', detail: `${format.toUpperCase()} bereitgestellt.` });
  } catch (err: any) {
    const detail = err?.response?.data?.error?.message || err?.message || 'Export fehlgeschlagen';
    toast.add({ severity: 'error', summary: 'Export fehlgeschlagen', detail, life: 6000 });
  } finally {
    exporting.value = null;
  }
}

watch(
  () => filters.categoryId,
  () => {
    triggerDebouncedLoad();
  }
);

watch(
  () => filters.selectedItems.map((i) => i.value),
  () => {
    if (filters.mode === 'selected') triggerDebouncedLoad();
  }
);

watch(
  () => filters.mode,
  (mode) => {
    if (mode !== 'selected') filters.selectedItems = [];
    if (mode === 'all') filters.aggregateAll = true;
    triggerDebouncedLoad();
  }
);

watch(
  () => filters.topLimit,
  () => {
    if (filters.mode === 'top5') triggerDebouncedLoad();
  }
);

watch(
  () => filters.aggregateAll,
  () => {
    if (filters.mode === 'all') triggerDebouncedLoad();
  }
);

onMounted(async () => {
  await loadCategories();
  await loadReports();
});
</script>

<template>
  <section class="page-section">
    <Toast />
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Transparenz</p>
        <h2 class="section-title">Berichte &amp; Analysen</h2>
        <p class="section-subtitle">Kennzahlen, Trends und Exportmöglichkeiten für dein Lager.</p>
      </div>
      <ReportExportButtons
        :disabled="!reportData || loading"
        :loadingFormat="exporting"
        @export:csv="() => handleExport('csv')"
        @export:excel="() => handleExport('excel')"
        @export:pdf="() => handleExport('pdf')"
      />
    </header>

    <ReportFilters
      :dateRange="filters.dateRange"
      :mode="filters.mode"
      :categoryId="filters.categoryId"
      :categoryOptions="categories"
      :selectedItems="filters.selectedItems"
      :itemSuggestions="allItemOptions"
      :aggregateAll="filters.aggregateAll"
      :topLimit="filters.topLimit"
      :loading="loading"
      :applying="applying"
      @update:dateRange="(value) => (filters.dateRange = value)"
      @update:mode="(value) => (filters.mode = value)"
      @update:category="(value) => (filters.categoryId = value)"
      @update:selectedItems="(value) => (filters.selectedItems = value)"
      @update:aggregate="(value) => (filters.aggregateAll = value)"
      @update:topLimit="(value) => (filters.topLimit = value || 5)"
      @apply-range="applyDateRange"
      @select-category-items="selectCategoryItems"
      @search-items="searchItems"
      @add-item="addSelectedItem"
    />

    <div class="section-stack">
      <ReportKpiCards :kpis="reportData?.kpis || null" :loading="loading" />
      <ReportCharts
        :consumptionData="consumptionChart"
        :trendData="trendChart"
        :loading="loading"
        :error="error"
      />
    </div>
  </section>
</template>

<style scoped>
.section-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}
</style>
