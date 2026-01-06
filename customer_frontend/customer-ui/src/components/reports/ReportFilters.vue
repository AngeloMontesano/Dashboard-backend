<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { CategoryOption, ItemOption, ReportMode } from '@/types/reports';

const props = withDefaults(
  defineProps<{
    dateRange: [Date | null, Date | null];
    mode: ReportMode;
    categoryId: string | null;
    categoryOptions: CategoryOption[];
    selectedItems: ItemOption[];
    itemSuggestions: ItemOption[];
    aggregateAll: boolean;
    topLimit: number;
    loading?: boolean;
    applying?: boolean;
    searching?: boolean;
  }>(),
  {
    loading: false,
    applying: false,
    searching: false
  }
);

const emit = defineEmits<{
  (e: 'update:dateRange', value: [Date | null, Date | null]): void;
  (e: 'update:mode', value: ReportMode): void;
  (e: 'update:category', value: string | null): void;
  (e: 'update:selectedItems', value: ItemOption[]): void;
  (e: 'update:aggregate', value: boolean): void;
  (e: 'update:topLimit', value: number): void;
  (e: 'apply-range'): void;
  (e: 'search-items', query: string): void;
  (e: 'add-item', item: ItemOption): void;
  (e: 'select-category-items'): void;
}>();

const modeOptions = [
  { label: 'Top 5 Artikel', value: 'top5', description: 'Automatisch relevanteste Artikel anzeigen' },
  { label: 'Alle Artikel (aggregiert)', value: 'all', description: 'Gesamtverbrauch pro Monat' },
  { label: 'Gezielte Auswahl', value: 'selected', description: 'Artikel oder Kategorien manuell wählen' }
];

const showAllLines = computed({
  get: () => !props.aggregateAll,
  set: (value: boolean) => emit('update:aggregate', !value ? true : false)
});

const dateRangeModel = computed({
  get: () => props.dateRange,
  set: (val: [Date | null, Date | null]) => emit('update:dateRange', val)
});

const selectedMode = computed({
  get: () => props.mode,
  set: (val: ReportMode) => emit('update:mode', val)
});

const selectedCategory = computed({
  get: () => props.categoryId,
  set: (val: string | null) => emit('update:category', val)
});

const topLimitModel = computed({
  get: () => props.topLimit,
  set: (val: number) => emit('update:topLimit', val)
});

const searchQuery = ref('');
const highlightedOption = ref<string>('');

watch(
  () => props.itemSuggestions,
  (list) => {
    if (!list.length) {
      highlightedOption.value = '';
      return;
    }
    if (!list.find((opt) => opt.value === highlightedOption.value)) {
      highlightedOption.value = list[0].value;
    }
  }
);

function formatInputDate(date: Date | null) {
  if (!date) return '';
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function parseInputDate(value: string) {
  if (!value) return null;
  const parts = value.split('-').map((p) => Number(p));
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  const [year, month, day] = parts;
  return new Date(year, month - 1, day);
}

function onDateChange(position: 'start' | 'end', event: Event) {
  const value = parseInputDate((event.target as HTMLInputElement).value);
  const next: [Date | null, Date | null] = [...dateRangeModel.value];
  if (position === 'start') next[0] = value;
  if (position === 'end') next[1] = value;
  emit('update:dateRange', next);
}

function onModeChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value as ReportMode;
  selectedMode.value = value;
}

function onCategoryChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value;
  selectedCategory.value = value || null;
}

function onTopLimitChange(event: Event) {
  const value = Number((event.target as HTMLInputElement).value);
  const safeValue = Number.isFinite(value) ? value : props.topLimit;
  topLimitModel.value = safeValue;
}

function onToggleAllLines(event: Event) {
  showAllLines.value = (event.target as HTMLInputElement).checked;
}

function onSearchInput(event: Event) {
  searchQuery.value = (event.target as HTMLInputElement).value;
  emit('search-items', searchQuery.value);
}

function onSuggestionChange(event: Event) {
  highlightedOption.value = (event.target as HTMLSelectElement).value;
}

function addHighlighted() {
  const candidateId = highlightedOption.value || props.itemSuggestions[0]?.value;
  if (!candidateId) return;
  const option = props.itemSuggestions.find((item) => item.value === candidateId);
  if (option) {
    emit('add-item', option);
  }
}

function clearSelected() {
  emit('update:selectedItems', []);
}

function removeItem(id: string) {
  const remaining = props.selectedItems.filter((item) => item.value !== id);
  emit('update:selectedItems', remaining);
}
</script>

<template>
  <section class="section report-card">
    <header class="section-header">
      <div>
        <h3 class="section-title">Filter</h3>
        <p class="section-subtitle">Zeitraum, Modus und Auswahl steuern die Auswertung.</p>
      </div>
      <div class="section-actions">
        <button class="btnPrimary small" type="button" :disabled="applying || loading" @click="emit('apply-range')">
          {{ applying ? '...' : 'Zeitraum anwenden' }}
        </button>
      </div>
    </header>

    <div class="filters-grid">
      <div class="field">
        <label class="field-label">Zeitraum</label>
        <div class="inline-range">
          <input
            class="input compat"
            type="date"
            :value="formatInputDate(dateRangeModel[0])"
            @input="(event) => onDateChange('start', event)"
          />
          <span class="range-sep">bis</span>
          <input
            class="input compat"
            type="date"
            :value="formatInputDate(dateRangeModel[1])"
            @input="(event) => onDateChange('end', event)"
          />
        </div>
        <small class="hint">Standard: letzte 30 Tage</small>
      </div>

      <div class="field">
        <label class="field-label">Modus</label>
        <select class="input compat" :value="selectedMode" @change="onModeChange">
          <option v-for="option in modeOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <small class="hint">{{ modeOptions.find((o) => o.value === mode)?.description }}</small>
      </div>

      <div class="field">
        <label class="field-label">Kategorie</label>
        <select class="input compat" :value="selectedCategory || ''" @change="onCategoryChange">
          <option value="">Alle Kategorien</option>
          <option v-for="option in categoryOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <div class="category-actions">
          <button class="btnGhost small" type="button" :disabled="applying || loading" @click="emit('apply-range')">
            {{ applying ? '...' : 'Aktualisieren' }}
          </button>
          <button
            v-if="mode === 'selected'"
            class="btnPrimary small"
            type="button"
            :disabled="!categoryId || loading"
            @click="emit('select-category-items')"
          >
            Kategorie übernehmen
          </button>
        </div>
      </div>
    </div>

    <div class="advanced-grid">
      <div class="field" v-if="mode !== 'top5'">
        <label class="field-label">Artikel auswählen</label>
        <input
          class="input compat"
          type="search"
          placeholder="SKU, Barcode oder Name"
          :value="searchQuery"
          @input="onSearchInput"
        />
        <small class="hint">Tippen zum Suchen. Vorschläge auswählen und hinzufügen.</small>
        <small v-if="searching" class="hint">Suche läuft...</small>

        <select
          class="input compat"
          size="6"
          :value="highlightedOption"
          @change="onSuggestionChange"
          @dblclick="addHighlighted"
        >
          <option v-for="item in itemSuggestions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <div class="category-actions">
          <button class="btnGhost small" type="button" :disabled="!itemSuggestions.length" @click="addHighlighted">
            Hinzufügen
          </button>
          <button class="btnGhost small" type="button" :disabled="!selectedItems.length" @click="clearSelected">
            Auswahl leeren
          </button>
        </div>

        <div class="chips" v-if="selectedItems.length">
          <div v-for="item in selectedItems" :key="item.value" class="chip">
            <span>{{ item.label }}</span>
            <button class="btnGhost small" type="button" @click="removeItem(item.value)">✕</button>
          </div>
        </div>
      </div>

      <div class="field" v-if="mode === 'top5'">
        <label class="field-label">Limit Top Artikel</label>
        <input
          class="input compat"
          type="number"
          min="1"
          max="10"
          :value="topLimitModel"
          @input="onTopLimitChange"
        />
        <small class="hint">Standard: 5</small>
      </div>

      <div class="field" v-if="mode === 'all'">
        <div class="switch-row">
          <span class="field-label">Alle als Linien anzeigen</span>
          <label class="toggle switch-toggle">
            <input type="checkbox" :checked="showAllLines" @change="onToggleAllLines" />
            <span>{{ showAllLines ? 'Ja' : 'Nein' }}</span>
          </label>
        </div>
        <small class="hint">Standard: Gesamtlinie. Aktivieren für Linien pro Artikel.</small>
      </div>
    </div>
  </section>
</template>

<style scoped>
.report-card {
  width: 100%;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-weight: 700;
  color: var(--text-strong);
}

.hint {
  color: var(--text-muted);
}

.category-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-2);
}

.inline-range {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.5rem;
  align-items: center;
}

.range-sep {
  color: var(--text-muted);
}

.switch-toggle input {
  margin-right: 6px;
}
</style>
