<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import type { ChartData } from 'chart.js';
import { getReportData, exportCsv, exportExcel, exportPdf } from '@/api/reporting';
import { fetchCategories, fetchItems, type Item, type Category } from '@/api/inventory';
import ReportFilters from '@/components/reports/ReportFilters.vue';
import ReportKpiCards from '@/components/reports/ReportKpiCards.vue';
import ReportCharts from '@/components/reports/ReportCharts.vue';
import ReportExportButtons from '@/components/reports/ReportExportButtons.vue';
import { useAuth } from '@/composables/useAuth';
import { useToast } from '@/composables/useToast';
import AuthReauthBanner from '@/components/auth/AuthReauthBanner.vue';
import { useAuthIssueBanner } from '@/composables/useAuthIssueBanner';
import type { CategoryOption, ItemOption, ReportFilterState, ReportParams, ReportResponse, ReportSeries } from '@/types/reports';

const { state: authState } = useAuth();
const { push: pushToast } = useToast();
const { authIssue, authMessage, handleAuthError } = useAuthIssueBanner();

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
const tableItems = ref<{ name: string; total: number; itemId?: string }[]>([]);
let loadDebounceTimer: number | undefined;
let searchDebounceTimer: number | undefined;
let searchAbortController: AbortController | null = null;
let lastSearchQuery = '';
const searching = ref(false);

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
  const start = new Date();
  start.setDate(end.getDate() - 29);
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
    from: formatDateParam(start),
    to: formatDateParam(end),
    mode: filters.mode,
    category_id: filters.categoryId || undefined,
    item_ids: filters.mode === 'selected' ? filters.selectedItems.map((i) => i.value) : undefined,
    aggregate: filters.mode === 'all' ? filters.aggregateAll : undefined,
    limit: filters.mode === 'top5' ? filters.topLimit : undefined
  };
}

function triggerDebouncedLoad() {
  window.clearTimeout(loadDebounceTimer);
  loadDebounceTimer = window.setTimeout(() => {
    void loadReports();
  }, 300);
}

async function loadCategories() {
  if (!authState.accessToken) return;
  try {
    const res = await fetchCategories(authState.accessToken);
    categories.value = res
      .filter((c: Category) => c.is_active)
      .map((c: Category) => ({ label: c.name, value: c.id } satisfies CategoryOption));
  } catch (err: any) {
    const classified = handleAuthError(err);
    if (classified.category === 'auth') return;
    pushToast({
      variant: 'danger',
      title: 'Kategorien fehlgeschlagen',
      description: classified.detailMessage || classified.userMessage
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
    options.forEach((opt: ItemOption) => {
      if (!merged.find((m) => m.value === opt.value)) merged.push(opt);
    });
    filters.selectedItems = merged;
    triggerDebouncedLoad();
  } catch (err: any) {
    const classified = handleAuthError(err);
    if (classified.category === 'auth') return;
    pushToast({
      variant: 'danger',
      title: 'Kategorie-Übernahme fehlgeschlagen',
      description: classified.detailMessage || classified.userMessage
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
    pushToast({ variant: 'warning', title: 'Zeitraum fehlt', description: 'Bitte Zeitraum auswählen.' });
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

  tableItems.value = buildTableData(data.series);
}

function buildTableData(series: ReportSeries[]) {
  const totals: Record<string, { total: number; name: string }> = {};
  series.forEach((s) => {
    const total = s.data.reduce((acc, curr) => acc + (curr.value || 0), 0);
    totals[s.label] = { total, name: s.label };
  });
  return Object.values(totals).sort((a, b) => b.total - a.total);
}

async function loadReports() {
  if (!authState.accessToken) return;
  const params = buildParams();
  if (!params) {
    error.value = 'Bitte Zeitraum auswählen.';
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    const res = await getReportData(authState.accessToken, params);
    const months = res.kpis.months && res.kpis.months.length ? res.kpis.months : extractMonths(res);
    reportData.value = { ...res, kpis: { ...res.kpis, months } };
    buildCharts(reportData.value);
  } catch (err: any) {
    const classified = handleAuthError(err);
    error.value = classified.userMessage || 'Berichte konnten nicht geladen werden.';
    if (classified.category !== 'auth') {
      pushToast({ variant: 'danger', title: 'Fehler beim Laden', description: classified.detailMessage || classified.userMessage });
    }
  } finally {
    loading.value = false;
  }
}

function clearSearchDebounce() {
  window.clearTimeout(searchDebounceTimer);
  searchDebounceTimer = undefined;
}

function clearSearchController() {
  if (searchAbortController) {
    searchAbortController.abort();
    searchAbortController = null;
  }
}

async function runItemSearch(query: string) {
  if (!authState.accessToken) return;
  searching.value = true;
  clearSearchController();
  const controller = new AbortController();
  searchAbortController = controller;
  lastSearchQuery = query;

  try {
    const res = await fetchItems({
      token: authState.accessToken,
      q: query,
      category_id: filters.categoryId || undefined,
      active: true,
      page: 1,
      page_size: 20,
      signal: controller.signal
    });
    itemSuggestions.value = res.items.map(toItemOption);
  } catch (err: any) {
    if (controller.signal.aborted) return;
    const classified = handleAuthError(err);
    if (classified.category === 'auth') return;
    pushToast({
      variant: 'warning',
      title: 'Suche fehlgeschlagen',
      description: classified.detailMessage || classified.userMessage
    });
  } finally {
    searching.value = false;
    if (searchAbortController === controller) {
      searchAbortController = null;
    }
  }
}

async function loadCategorySuggestions() {
  if (!authState.accessToken || !filters.categoryId) return;
  searching.value = true;
  clearSearchController();
  const controller = new AbortController();
  searchAbortController = controller;
  try {
    const res = await fetchItems({
      token: authState.accessToken,
      category_id: filters.categoryId,
      active: true,
      page: 1,
      page_size: 20,
      signal: controller.signal
    });
    itemSuggestions.value = res.items.map(toItemOption);
  } catch (err: any) {
    if (controller.signal.aborted) return;
    const classified = handleAuthError(err);
    if (classified.category === 'auth') return;
    pushToast({
      variant: 'warning',
      title: 'Suche fehlgeschlagen',
      description: classified.detailMessage || classified.userMessage
    });
  } finally {
    searching.value = false;
    if (searchAbortController === controller) {
      searchAbortController = null;
    }
  }
}

function searchItems(query: string) {
  const trimmed = (query || '').trim();
  clearSearchDebounce();

  if (!trimmed) {
    clearSearchController();
    lastSearchQuery = '';
    if (filters.categoryId) {
      searchDebounceTimer = window.setTimeout(() => {
        void loadCategorySuggestions();
      }, 280);
    } else {
      itemSuggestions.value = filters.selectedItems.slice();
      searching.value = false;
    }
    return;
  }

  searchDebounceTimer = window.setTimeout(() => {
    void runItemSearch(trimmed);
  }, 320);
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
    link.download = `berichte-${params.from}-${params.to}.${extension}`;
    link.click();
    window.URL.revokeObjectURL(url);
    pushToast({
      variant: 'success',
      title: 'Export gestartet',
      description: `${format.toUpperCase()} bereitgestellt.`
    });
  } catch (err: any) {
    const classified = handleAuthError(err);
    if (classified.category !== 'auth') {
      pushToast({ variant: 'danger', title: 'Export fehlgeschlagen', description: classified.detailMessage || classified.userMessage });
    }
  } finally {
    exporting.value = null;
  }
}

watch(
  () => filters.categoryId,
  () => {
    triggerDebouncedLoad();
    if (lastSearchQuery) {
      searchItems(lastSearchQuery);
    } else {
      if (filters.categoryId) {
        void loadCategorySuggestions();
      } else {
        itemSuggestions.value = filters.selectedItems.slice();
      }
    }
  }
);

watch(
  () => filters.dateRange,
  (range) => {
    if (range[0] && range[1]) {
      filters.appliedRange = [...range] as [Date, Date];
      triggerDebouncedLoad();
    }
  },
  { deep: true }
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
    if (mode === 'selected' && !lastSearchQuery && filters.categoryId) {
      void loadCategorySuggestions();
    }
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

onBeforeUnmount(() => {
  window.clearTimeout(loadDebounceTimer);
  clearSearchDebounce();
  clearSearchController();
});
</script>

<template>
  <section class="section page-section">
    <header class="section-header">
      <div>
        <p class="section-subtitle">Transparenz</p>
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
      :searching="searching"
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
      <AuthReauthBanner
        v-if="authIssue"
        :message="authMessage"
        retry-label="Erneut laden"
        @retry="() => loadReports()"
      />
      <ReportKpiCards :kpis="reportData?.kpis || null" :loading="loading" />
      <ReportCharts
        :consumptionData="consumptionChart"
        :trendData="trendChart"
        :loading="loading"
        :error="error"
      />

      <article class="card table-card">
        <header class="cardHeader">
          <div>
            <div class="cardTitle">Top Artikel</div>
            <div class="cardHint">Sortiert nach Gesamtverbrauch im Zeitraum</div>
          </div>
        </header>
        <div v-if="loading" class="table-loading">
          <span class="spinner" aria-label="Laden"></span>
        </div>
        <div v-else-if="error" class="table-loading error">{{ error }}</div>
        <div v-else>
          <div v-if="tableItems.length" class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Artikel</th>
                  <th class="right">Gesamtverbrauch</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableItems" :key="row.name">
                  <td class="item-name">{{ row.name }}</td>
                  <td class="right">
                    <span class="tag neutral">{{ row.total.toLocaleString('de-DE') }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="table-loading">Keine Artikel im Zeitraum</div>
        </div>
      </article>
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

.table-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 160px;
  color: var(--text-muted);
}

.table-loading.error {
  color: var(--danger);
}

.item-name {
  font-weight: 600;
}

.spinner {
  width: 28px;
  height: 28px;
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
