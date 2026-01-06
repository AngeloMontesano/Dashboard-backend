<script setup lang="ts">
import { computed, ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import MultiSelect from 'primevue/multiselect';
import AutoComplete from 'primevue/autocomplete';
import InputSwitch from 'primevue/inputswitch';
import InputNumber from 'primevue/inputnumber';
import Tag from 'primevue/tag';
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
  }>(),
  {
    loading: false,
    applying: false
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

const autocompleteValue = ref<string>('');

const selectedItemsModel = computed({
  get: () => props.selectedItems,
  set: (val: ItemOption[]) => emit('update:selectedItems', val)
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

const handleItemSelect = (event: { value: ItemOption }) => {
  if (!event?.value) return;
  emit('add-item', event.value);
  autocompleteValue.value = '';
};

</script>

<template>
  <Card class="report-card">
    <template #title>Filter</template>
    <template #subtitle>Zeitraum, Modus und Artikel-Auswahl steuern die Auswertung.</template>

    <div class="filters-grid">
      <div class="field">
        <label class="field-label">Zeitraum</label>
        <Calendar
          v-model="dateRangeModel"
          selectionMode="range"
          :manualInput="false"
          view="date"
          dateFormat="dd.mm.yy"
          showIcon
          showButtonBar
          placeholder="Zeitraum wählen"
          class="w-full"
          @update:modelValue="(value) => emit('update:dateRange', value as [Date | null, Date | null])"
        />
        <small class="hint">Standard: letzte 30 Tage</small>
      </div>

      <div class="field">
        <label class="field-label">Modus</label>
        <Dropdown v-model="selectedMode" :options="modeOptions" optionLabel="label" optionValue="value" class="w-full" />
        <small class="hint">{{ modeOptions.find((o) => o.value === mode)?.description }}</small>
      </div>

      <div class="field">
        <label class="field-label">Kategorie</label>
        <Dropdown
          v-model="selectedCategory"
          :options="categoryOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Alle Kategorien"
          showClear
          class="w-full"
        />
        <div class="category-actions">
          <Button
            label="Zeitraum anwenden"
            icon="pi pi-refresh"
            :loading="applying"
            @click="emit('apply-range')"
          />
          <Button
            v-if="mode === 'selected'"
            label="Kategorie übernehmen"
            icon="pi pi-check-circle"
            severity="secondary"
            outlined
            :disabled="!categoryId || loading"
            @click="emit('select-category-items')"
          />
        </div>
      </div>
    </div>

    <div class="advanced-grid">
      <div class="field" v-if="mode !== 'top5'">
        <label class="field-label">Artikel auswählen</label>
        <MultiSelect
          v-model="selectedItemsModel"
          :options="itemSuggestions"
          optionLabel="label"
          filter
          placeholder="Artikel wählen"
          class="w-full"
        />
        <div class="chips" v-if="selectedItems.length">
          <Tag
            v-for="item in selectedItems"
            :key="item.value"
            :value="item.label"
            class="chip"
          />
        </div>
      </div>

      <div class="field" v-if="mode === 'selected'">
        <label class="field-label">Artikel hinzufügen</label>
        <AutoComplete
          v-model="autocompleteValue"
          :suggestions="itemSuggestions"
          optionLabel="label"
          optionValue="value"
          :minLength="2"
          placeholder="SKU, Barcode oder Name"
          forceSelection
          class="w-full"
          @complete="(e) => emit('search-items', e.query)"
          @item-select="handleItemSelect"
        />
        <small class="hint">Tippen zum Suchen, Enter zum Übernehmen</small>
      </div>

      <div class="field" v-if="mode === 'top5'">
        <label class="field-label">Limit Top Artikel</label>
        <InputNumber v-model="topLimitModel" inputId="top-limit" :min="1" :max="10" showButtons class="w-full" />
        <small class="hint">Standard: 5</small>
      </div>

      <div class="field" v-if="mode === 'all'">
        <div class="switch-row">
          <span class="field-label">Alle als Linien anzeigen</span>
          <InputSwitch v-model="showAllLines" />
        </div>
        <small class="hint">Standard: Gesamtlinie. Aktivieren für Linien pro Artikel.</small>
      </div>
    </div>
  </Card>
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
  font-weight: 600;
  color: var(--text-color, #2a2a2a);
}

.hint {
  color: var(--text-secondary-color, #6b7280);
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
  background: var(--surface-100, #f3f4f6);
}

.w-full {
  width: 100%;
}
</style>
