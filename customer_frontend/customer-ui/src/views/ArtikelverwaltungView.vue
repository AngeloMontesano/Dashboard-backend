<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  checkSkuExists,
  createItem,
  fetchCategories,
  fetchItems,
  fetchUnits,
  importItems,
  updateItem,
  type Category,
  type Item,
  type ItemUnit
} from '@/api/inventory';
import { useAuth } from '@/composables/useAuth';
import BaseInput from '@/components/common/BaseInput.vue';
import BaseSelect from '@/components/common/BaseSelect.vue';
import BaseField from '@/components/common/BaseField.vue';

const router = useRouter();
const { state: authState, isAuthenticated, logout } = useAuth();

const hasWriteAccess = computed(() => Boolean(authState.accessToken) && authState.role !== 'readonly');
const canOpenModals = computed(() => Boolean(authState.accessToken));
const isLoggedIn = computed(() => isAuthenticated());

const categories = ref<Category[]>([]);
const units = ref<ItemUnit[]>([]);
const items = ref<Item[]>([]);
const total = ref(0);

const filters = reactive({
  q: '',
  category_id: '' as string | null,
  active: null as boolean | null,
  page: 1,
  page_size: 25
});

const searchTerm = ref('');
const quickScanValue = ref('');
const quickScanInput = ref<HTMLInputElement | null>(null);

const isLoading = ref(false);
const isSaving = ref(false);
const isExporting = ref(false);
const banner = reactive({ message: '', error: '', scan: '' });

const selectedArticleId = ref<string | null>(null);
const selectedArticle = computed(() => items.value.find((item) => item.id === selectedArticleId.value) || null);

const editForm = reactive({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  category_id: '' as string | null,
  quantity: 0,
  unit: '',
  min_stock: 0,
  max_stock: 0,
  target_stock: 0,
  recommended_stock: 0,
  order_mode: 0,
  is_active: true
});

const showCreate = ref(false);
const createCardRef = ref<HTMLElement | null>(null);
const createBarcodeInput = ref<InstanceType<typeof BaseInput> | null>(null);
const createUnitInput = ref<InstanceType<typeof BaseInput> | null>(null);
const createForm = reactive({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  category_id: '' as string | null,
  quantity: 0,
  unit: '',
  min_stock: 0,
  max_stock: 0,
  target_stock: 0,
  recommended_stock: 0,
  order_mode: 0,
  is_active: true
});
const createSkuHint = ref<string | null>(null);
const createFeedback = reactive({ error: '', hint: '' });
const showMoreCreateFields = ref(false);

const importModalOpen = ref(false);
const importStep = ref<1 | 2 | 3>(1);
const importFile = ref<File | null>(null);
const importHeaders = ref<string[]>([]);
const importPreview = ref<string[][]>([]);
const importMapping = reactive<Record<string, string>>({
  sku: '',
  barcode: '',
  name: '',
  unit: '',
  description: '',
  quantity: '',
  category_id: '',
  min_stock: '',
  max_stock: '',
  target_stock: '',
  recommended_stock: '',
  order_mode: ''
});
const importLoading = ref(false);
const importError = ref('');
const importResult = reactive({
  created: 0,
  updated: 0,
  errors: [] as Array<{ row: string; error: string }>
});

const requiredMappingFields = ['sku', 'barcode', 'name', 'unit'];
const isMappingValid = computed(() => requiredMappingFields.every((key) => importMapping[key]));
const isEditValid = computed(
  () => !!editForm.sku.trim() && !!editForm.barcode.trim() && !!editForm.name.trim() && !!editForm.unit.trim()
);
const isCreateValid = computed(
  () => !!createForm.sku.trim() && !!createForm.barcode.trim() && !!createForm.name.trim() && !!createForm.unit.trim()
);
const showCreateCard = computed(() => showCreate.value);
const categoryOptions = computed(() =>
  categories.value.map((cat) => ({ label: cat.name, value: cat.id }))
);
const unitOptions = computed(() => units.value.map((u) => ({ label: u.label, value: u.code })));

function resetCreateForm() {
  createForm.sku = '';
  createForm.barcode = '';
  createForm.name = '';
  createForm.description = '';
  createForm.category_id = '';
  createForm.quantity = 0;
  createForm.unit = '';
  createForm.min_stock = 0;
  createForm.max_stock = 0;
  createForm.target_stock = 0;
  createForm.recommended_stock = 0;
  createForm.order_mode = 0;
  createForm.is_active = true;
  createSkuHint.value = null;
  createFeedback.error = '';
  createFeedback.hint = '';
  showMoreCreateFields.value = false;
}

function resetEditForm() {
  if (!selectedArticle.value) return;
  hydrateFormFromItem(selectedArticle.value, editForm);
}

function hydrateFormFromItem(item: Item, target: typeof editForm | typeof createForm) {
  target.sku = item.sku;
  target.barcode = item.barcode;
  target.name = item.name;
  target.description = item.description;
  target.category_id = item.category_id || '';
  target.quantity = item.quantity;
  target.unit = item.unit;
  target.min_stock = item.min_stock;
  target.max_stock = item.max_stock;
  target.target_stock = item.target_stock;
  target.recommended_stock = item.recommended_stock;
  target.order_mode = item.order_mode;
  target.is_active = item.is_active;
}

function handleAuthError(err: any) {
  const status = err?.response?.status;
  if (status === 401) {
    banner.error = 'Sitzung abgelaufen. Bitte erneut anmelden.';
    logout();
    router.push({ name: 'login', query: { redirect: '/artikelverwaltung' } });
    return true;
  }
  return false;
}

async function loadCategories() {
  if (!authState.accessToken) return;
  const data = await fetchCategories(authState.accessToken);
  categories.value = data.filter((c: Category) => c.is_active);
}

async function loadUnits() {
  if (!authState.accessToken) return;
  try {
    const data = await fetchUnits(authState.accessToken);
    units.value = data.filter((u) => u.is_active);
  } catch {
    units.value = [
      { code: 'pcs', label: 'Stück', is_active: true },
      { code: 'kg', label: 'Kilogramm', is_active: true },
      { code: 'g', label: 'Gramm', is_active: true },
      { code: 'l', label: 'Liter', is_active: true },
      { code: 'ml', label: 'Milliliter', is_active: true }
    ];
  }
}

async function loadItems() {
  if (!authState.accessToken) return;
  isLoading.value = true;
  banner.error = '';
  try {
    const data = await fetchItems({
      token: authState.accessToken,
      q: filters.q || undefined,
      category_id: filters.category_id || undefined,
      active: filters.active,
      page: filters.page,
      page_size: filters.page_size
    });
    items.value = data.items;
    total.value = data.total;
    if (selectedArticleId.value && !items.value.some((item) => item.id === selectedArticleId.value)) {
      selectedArticleId.value = null;
    }
    if (selectedArticle.value) {
      hydrateFormFromItem(selectedArticle.value, editForm);
    }
  } catch (err: any) {
    if (handleAuthError(err)) return;
    banner.error = err?.message || 'Konnte Artikel nicht laden.';
  } finally {
    isLoading.value = false;
  }
}

async function handleQuickScan() {
  if (!authState.accessToken || !quickScanValue.value.trim()) return;
  banner.scan = '';
  const barcode = quickScanValue.value.trim();
  quickScanValue.value = '';
  await nextTick();
  quickScanInput.value?.focus();
  try {
    const result = await fetchItems({
      token: authState.accessToken,
      q: barcode,
      active: null,
      page: 1,
      page_size: 200
    });
    if (result.total === 0) {
      banner.scan = 'Kein Artikel zum Barcode gefunden';
      return;
    }
    filters.q = barcode;
    filters.page = 1;
    await loadItems();
    if (result.total === 1 && result.items[0]) {
      selectedArticleId.value = result.items[0].id;
      hydrateFormFromItem(result.items[0], editForm);
    } else {
      banner.scan = `${result.total} Treffer zum Barcode – Filter gesetzt.`;
    }
  } catch (err: any) {
    if (handleAuthError(err)) return;
    banner.scan = 'Schnellscan fehlgeschlagen.';
  }
}

async function handleSaveSelected() {
  if (!authState.accessToken || !selectedArticle.value || !hasWriteAccess.value) {
    banner.error = 'Keine Berechtigung für Änderungen.';
    return;
  }
  if (!isEditValid.value) return;
  banner.error = '';
  banner.message = '';
  isSaving.value = true;
  try {
    await updateItem(authState.accessToken, selectedArticle.value.id, {
      ...editForm,
      category_id: editForm.category_id || null
    });
    banner.message = 'Artikel gespeichert.';
    await loadItems();
  } catch (err: any) {
    if (handleAuthError(err)) return;
    banner.error = err?.response?.data?.error?.message || err?.message || 'Speichern fehlgeschlagen.';
  } finally {
    isSaving.value = false;
  }
}

async function handleCreate() {
  if (!authState.accessToken || !hasWriteAccess.value) {
    createFeedback.error = 'Keine Berechtigung für Änderungen.';
    return;
  }
  if (!isCreateValid.value) return;
  createFeedback.error = '';
  createFeedback.hint = '';
  isSaving.value = true;
  try {
    const created = await createItem(authState.accessToken, {
      ...createForm,
      category_id: createForm.category_id || null
    });
    banner.message = 'Artikel angelegt.';
    showCreate.value = false;
    resetCreateForm();
    await loadItems();
    selectedArticleId.value = created.id;
    hydrateFormFromItem(created, editForm);
  } catch (err: any) {
    if (handleAuthError(err)) return;
    createFeedback.error = err?.response?.data?.error?.message || err?.message || 'Anlage fehlgeschlagen.';
  } finally {
    isSaving.value = false;
  }
}

async function handleCreateSkuBlur() {
  createSkuHint.value = null;
  if (!createForm.sku || !authState.accessToken) return;
  try {
    const res = await checkSkuExists(authState.accessToken, createForm.sku);
    if (res.exists) {
      createSkuHint.value = `SKU bereits vergeben (${res.normalized_sku})`;
    } else if (res.normalized_sku !== createForm.sku) {
      createSkuHint.value = `SKU wird gespeichert als ${res.normalized_sku}`;
    }
  } catch {
    createSkuHint.value = null;
  }
}

async function fetchAllItemsForExport() {
  if (!authState.accessToken) return [];
  const pageSize = 200;
  let page = 1;
  const all: Item[] = [];
  let totalItems = 0;
  do {
    const response = await fetchItems({
      token: authState.accessToken,
      page,
      page_size: pageSize,
      active: null,
      q: undefined,
      category_id: undefined
    });
    all.push(...response.items);
    totalItems = response.total;
    page += 1;
  } while (all.length < totalItems);
  return all;
}

function toCsvValue(value: unknown) {
  if (value === null || value === undefined) return '';
  const str = String(value);
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

async function handleExportAll() {
  if (!hasWriteAccess.value) {
    banner.error = 'Keine Berechtigung für Export.';
    return;
  }
  isExporting.value = true;
  banner.error = '';
  banner.message = '';
  try {
    const allItems = await fetchAllItemsForExport();
    const headers = [
      'SKU',
      'Name',
      'Barcode',
      'Kategorie',
      'Bestand',
      'Einheit',
      'Min-Bestand',
      'Max-Bestand',
      'Soll-Bestand',
      'Empfohlen',
      'Status'
    ];
    const rows = allItems.map((item) => [
      toCsvValue(item.sku),
      toCsvValue(item.name),
      toCsvValue(item.barcode),
      toCsvValue(item.category_name || ''),
      toCsvValue(item.quantity),
      toCsvValue(item.unit),
      toCsvValue(item.min_stock),
      toCsvValue(item.max_stock),
      toCsvValue(item.target_stock),
      toCsvValue(item.recommended_stock),
      toCsvValue(item.is_active ? 'Aktiv' : 'Inaktiv')
    ]);
    const csvContent = [headers.map(toCsvValue).join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const now = new Date();
    const pad = (v: number) => v.toString().padStart(2, '0');
    const filename = `artikel_export_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(
      now.getHours()
    )}${pad(now.getMinutes())}.csv`;
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    link.click();
    window.URL.revokeObjectURL(url);
    banner.message = '';
  } catch (err: any) {
    if (handleAuthError(err)) return;
    banner.error = err?.message || 'Export fehlgeschlagen.';
  } finally {
    isExporting.value = false;
  }
}

function openCreateCard() {
  resetCreateForm();
  createFeedback.error = '';
  selectedArticleId.value = null;
  showCreate.value = true;
  nextTick(() => {
    createCardRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    focusInputElement(createBarcodeInput.value);
  });
}

function openImportModal() {
  importModalOpen.value = true;
  importStep.value = 1;
  importFile.value = null;
  importHeaders.value = [];
  importPreview.value = [];
  importError.value = '';
  importResult.created = 0;
  importResult.updated = 0;
  importResult.errors = [];
  Object.keys(importMapping).forEach((key) => (importMapping[key] = ''));
  banner.error = '';
}

function closeImportModal() {
  importModalOpen.value = false;
}

function suggestMapping(headers: string[]) {
  const normalized = headers.map((h) => h.toLowerCase());
  const findHeader = (candidates: string[]) => {
    const idx = normalized.findIndex((h) => candidates.some((c) => h === c || h.includes(c)));
    return idx >= 0 ? headers[idx] : '';
  };
  importMapping.sku = findHeader(['sku', 'artikelnummer']);
  importMapping.barcode = findHeader(['barcode', 'ean']);
  importMapping.name = findHeader(['name', 'titel', 'artikel']);
  importMapping.unit = findHeader(['einheit', 'unit']);
  importMapping.description = findHeader(['beschreibung', 'desc']);
  importMapping.quantity = findHeader(['menge', 'bestand', 'quantity']);
  importMapping.category_id = findHeader(['kategorie', 'category']);
  importMapping.min_stock = findHeader(['min', 'mind', 'min_stock']);
  importMapping.max_stock = findHeader(['max', 'max_stock']);
  importMapping.target_stock = findHeader(['soll', 'target']);
  importMapping.recommended_stock = findHeader(['empfohlen', 'recommended']);
  importMapping.order_mode = findHeader(['order', 'modus', 'order_mode']);
}

async function handleImportFile(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  importFile.value = file;
  const text = await file.slice(0, 6000).text();
  const lines = text.split(/\r?\n/).filter(Boolean);
  if (!lines.length) return;
  const headerLine = lines[0];
  const headers = headerLine.split(',').map((h) => h.trim());
  importHeaders.value = headers;
  importPreview.value = lines.slice(1, 4).map((line) => line.split(','));
  suggestMapping(headers);
  importStep.value = 2;
}

async function startImport() {
  if (!authState.accessToken || !importFile.value || !isMappingValid.value) return;
  importLoading.value = true;
  importError.value = '';
  importResult.created = 0;
  importResult.updated = 0;
  importResult.errors = [];
  try {
    const res = await importItems(authState.accessToken, importFile.value, importMapping);
    importResult.created = res.imported;
    importResult.updated = res.updated;
    importResult.errors = res.errors;
    await loadItems();
  } catch (err: any) {
    if (handleAuthError(err)) return;
    importError.value = err?.response?.data?.error?.message || err?.message || 'Import fehlgeschlagen.';
  } finally {
    importLoading.value = false;
  }
}

const handleRowClick = (item: Item) => {
  showCreate.value = false;
  selectedArticleId.value = item.id;
  hydrateFormFromItem(item, editForm);
  banner.message = '';
  banner.error = '';
};

const handleNavigateCategories = () => {
  router.push('/kategorien');
};

function focusCreateBarcode() {
  if (showCreateCard.value) {
    nextTick(() => focusInputElement(createBarcodeInput.value));
  } else {
    quickScanInput.value?.focus();
  }
}

function focusInputElement(comp: any) {
  if (comp?.focus) {
    comp.focus();
    return;
  }
  const el: HTMLInputElement | HTMLTextAreaElement | null | undefined =
    comp?.$el?.querySelector?.('input,textarea');
  el?.focus();
}

function closeCreateCard() {
  showCreate.value = false;
  resetCreateForm();
  nextTick(() => quickScanInput.value?.focus());
}

onMounted(async () => {
  if (!isLoggedIn.value) return;
  await loadUnits();
  await loadCategories();
  await loadItems();
  await nextTick();
  quickScanInput.value?.focus();
});

watch(
  () => authState.accessToken,
  async (token) => {
    if (token) {
      await loadUnits();
      await loadCategories();
      await loadItems();
    } else {
      categories.value = [];
      items.value = [];
      units.value = [];
    }
  }
);

let searchTimer: number | undefined;
watch(
  searchTerm,
  (value) => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(async () => {
      filters.q = value.trim();
      filters.page = 1;
      await loadItems();
    }, 200);
  },
  { flush: 'post' }
);

watch(
  () => [filters.category_id, filters.active, filters.page_size],
  async () => {
    filters.page = 1;
    await loadItems();
  }
);

watch(
  () => filters.page,
  async () => {
    await loadItems();
  }
);
</script>

<template>
  <section class="page-section artikelverwaltung">
    <header class="page-head">
      <div>
        <p class="eyebrow">Stammdaten</p>
        <h2 class="section-title">Artikelverwaltung</h2>
        <p class="section-subtitle">Artikel, Barcodes und Mindestbestände verwalten.</p>
      </div>
      <div class="page-head__actions">
        <button class="button button--ghost" type="button" @click="handleNavigateCategories">
          Kategorien verwalten
        </button>
        <button class="button button--ghost" type="button" @click="openImportModal" :disabled="!canOpenModals">
          Import CSV
        </button>
        <button class="button button--ghost" type="button" @click="handleExportAll" :disabled="isExporting">
          {{ isExporting ? 'Exportiert...' : 'Export CSV' }}
        </button>
        <button
          class="button button--primary"
          type="button"
          @click="openCreateCard"
          :disabled="!canOpenModals"
        >
          Neuer Artikel
        </button>
      </div>
    </header>

    <div v-if="banner.message" class="alert alert--success">{{ banner.message }}</div>
    <div v-if="banner.error" class="alert alert--error">{{ banner.error }}</div>
    <div v-if="banner.scan" class="alert alert--muted">{{ banner.scan }}</div>

    <div class="toolbar">
      <label class="toolbar__field">
        <span class="toolbar__label">Schnellscan</span>
        <input
          ref="quickScanInput"
          v-model="quickScanValue"
          type="text"
          placeholder="Barcode scannen und Enter"
          @keydown.enter.prevent="handleQuickScan"
        />
      </label>
      <label class="toolbar__field">
        <span class="toolbar__label sr-only">Suche</span>
        <input v-model="searchTerm" type="search" placeholder="Suche SKU, Barcode, Name" />
      </label>
<!--      <button class="button button--ghost toolbar__focus" type="button" @click="focusCreateBarcode">
        Fokus auf Barcode
      </button>
    -->    
      <label class="toolbar__field select-field">
        <span class="toolbar__label">Kategorie</span>
        <select v-model="filters.category_id">
          <option value="">Alle Kategorien</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </label>
      <label class="toolbar__field select-field">
        <span class="toolbar__label">Status</span>
        <select v-model="filters.active">
          <option :value="null">Alle</option>
          <option :value="true">Nur aktive</option>
          <option :value="false">Nur inaktive</option>
        </select>
      </label>
      <label class="toolbar__field select-field">
        <span class="toolbar__label">Seitengröße</span>
        <select v-model.number="filters.page_size">
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </label>
    </div>

    <div class="card table-card">
      <div class="table-header">
        <div>
          <h3 class="card__title">Artikel</h3>
          <p class="card__hint">SKU, Name, Barcode, Bestände</p>
        </div>
        <div class="table-meta">{{ total }} Artikel</div>
      </div>
      <div class="table-wrapper" v-if="items.length">
        <table class="table table--clickable">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th>Barcode</th>
              <th>Kategorie</th>
              <th>Bestand</th>
              <th>Min-Bestand</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="item.id"
              :class="{ 'table-row--active': selectedArticleId === item.id }"
              @click="handleRowClick(item)"
            >
              <td>{{ item.sku }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.barcode }}</td>
              <td>{{ item.category_name || '—' }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ item.min_stock }}</td>
              <td>
                <span :class="['badge', item.is_active ? 'badge--success' : 'badge--muted']">
                  {{ item.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="placeholder">
        <p v-if="isLoading">Lade Artikel...</p>
        <p v-else>Keine Artikel gefunden. Nutze "Neuen Artikel anlegen" oder importiere per CSV.</p>
      </div>
      <div class="pagination">
        <button class="button button--ghost" type="button" :disabled="filters.page <= 1" @click="filters.page -= 1">
          Zurück
        </button>
        <span>Seite {{ filters.page }}</span>
        <button
          class="button button--ghost"
          type="button"
          :disabled="filters.page * filters.page_size >= total"
          @click="filters.page += 1"
        >
          Weiter
        </button>
      </div>
    </div>

    <section v-if="selectedArticle" class="card detail-card">
      <header class="detail-card__header">
        <div>
          <p class="eyebrow">Details</p>
          <h3 class="card__title">Ausgewählter Artikel: {{ selectedArticle.name }} ({{ selectedArticle.sku }})</h3>
        </div>
        <div class="detail-card__actions">
          <button class="button button--ghost" type="button" @click="resetEditForm">Zurücksetzen</button>
          <button
            class="button button--primary"
            type="button"
            :disabled="!isEditValid || !hasWriteAccess || isSaving"
            @click="handleSaveSelected"
          >
            {{ isSaving ? 'Speichert...' : 'Speichern' }}
          </button>
        </div>
      </header>
      <div class="form-grid two-col">
        <div class="form-section">
          <h4>Stammdaten</h4>
          <label>
            <span>SKU *</span>
            <input v-model="editForm.sku" :disabled="!hasWriteAccess" />
            <small v-if="!editForm.sku">SKU ist erforderlich.</small>
          </label>
          <label>
            <span>Name *</span>
            <input v-model="editForm.name" :disabled="!hasWriteAccess" />
            <small v-if="!editForm.name">Name ist erforderlich.</small>
          </label>
          <label>
            <span>Barcode *</span>
            <input v-model="editForm.barcode" :disabled="!hasWriteAccess" />
            <small v-if="!editForm.barcode">Barcode ist erforderlich.</small>
          </label>
          <label>
            <span>Kategorie</span>
            <select v-model="editForm.category_id" :disabled="!hasWriteAccess">
              <option value="">Keine</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </label>
          <label>
            <span>Beschreibung</span>
            <textarea v-model="editForm.description" rows="3" :disabled="!hasWriteAccess" />
          </label>
        </div>

        <div class="form-section">
          <h4>Bestand & Grenzwerte</h4>
          <label>
            <span>Bestand</span>
            <input type="number" min="0" v-model.number="editForm.quantity" :disabled="!hasWriteAccess" />
          </label>
          <label>
            <span>Einheit *</span>
            <select v-model="editForm.unit" :disabled="!hasWriteAccess">
              <option value="">Bitte wählen</option>
              <option v-for="u in unitOptions" :key="u.value" :value="u.value">{{ u.label }}</option>
            </select>
            <small v-if="!editForm.unit">Einheit ist erforderlich.</small>
          </label>
          <label>
            <span>Min-Bestand</span>
            <input type="number" min="0" v-model.number="editForm.min_stock" :disabled="!hasWriteAccess" />
          </label>
          <label>
            <span>Max-Bestand</span>
            <input type="number" min="0" v-model.number="editForm.max_stock" :disabled="!hasWriteAccess" />
          </label>
          <label>
            <span>Soll-Bestand</span>
            <input type="number" min="0" v-model.number="editForm.target_stock" :disabled="!hasWriteAccess" />
          </label>
<!--          <label>
            <span>Empfohlen</span>
-->    
            <input type="number" min="0" v-model.number="editForm.recommended_stock" :disabled="!hasWriteAccess" />
          </label>
          <label>
            <span>Bestell-Modus</span>
            <select v-model.number="editForm.order_mode" :disabled="!hasWriteAccess">
              <option :value="0">0 - Kein Alarm</option>
              <option :value="1">1 - Alarm bei Unterschreitung</option>
              <option :value="2">2 - In Bestellliste aufnehmen</option>
              <option :value="3">3 - Automatisch nachbestellen</option>
            </select>
          </label>
          <label class="checkbox">
            <input type="checkbox" v-model="editForm.is_active" :disabled="!hasWriteAccess" />
            <span>Aktiv</span>
          </label>
        </div>
      </div>
    </section>

    <section v-if="showCreateCard" ref="createCardRef" class="card create-card">
      <header class="detail-card__header">
        <div>
          <p class="eyebrow">Neu</p>
          <h3 class="card__title">Neuen Artikel anlegen</h3>
          <p class="card__hint">Pflichtfelder: Artikelnummer, Name, Barcode, Einheit.</p>
        </div>
        <div class="detail-card__actions">
          <button class="button button--ghost" type="button" @click="resetCreateForm">Zurücksetzen</button>
          <button class="button button--ghost" type="button" @click="closeCreateCard">Abbrechen</button>
          <button class="button button--primary" type="button" :disabled="!isCreateValid || isSaving" @click="handleCreate">
            {{ isSaving ? 'Speichert...' : 'Speichern' }}
          </button>
        </div>
      </header>

      <div v-if="createFeedback.error" class="alert alert--error">{{ createFeedback.error }}</div>

      <div class="create-grid">
        <BaseField
          label="Artikelnummer"
          :required="true"
          :hint="createSkuHint || 'Interne Artikelnummer, z.B. A-10023'"
          :error="!createForm.sku ? 'Artikelnummer ist erforderlich.' : ''"
        >
          <BaseInput v-model="createForm.sku" @blur="handleCreateSkuBlur" />
        </BaseField>

        <BaseField label="Name" :required="true" :error="!createForm.name ? 'Name ist erforderlich.' : ''">
          <BaseInput v-model="createForm.name" />
        </BaseField>

        <BaseField label="Barcode" :required="true" :error="!createForm.barcode ? 'Barcode ist erforderlich.' : ''" hint="Scanner benutzen oder eintippen.">
          <BaseInput ref="createBarcodeInput" v-model="createForm.barcode" @keydown.enter.prevent="focusInputElement(createUnitInput)" />
        </BaseField>

        <BaseField label="Einheit" :required="true" :error="!createForm.unit ? 'Einheit ist erforderlich.' : ''">
          <BaseSelect
            ref="createUnitInput"
            v-model="createForm.unit"
            :options="unitOptions"
            placeholder="Bitte wählen"
          />
        </BaseField>

        <BaseField label="Kategorie">
          <BaseSelect v-model="createForm.category_id" :options="categoryOptions" placeholder="Keine" />
        </BaseField>

        <BaseField label="Artikel ist aktiv" hint="Inaktive Artikel werden nicht in Auswahl und Buchungen angeboten.">
          <label class="checkbox">
            <input type="checkbox" v-model="createForm.is_active" />
            <span>Aktiv</span>
          </label>
        </BaseField>

        <BaseField class="full-span" label="Artikelbeschreibung">
          <textarea class="input" rows="2" v-model="createForm.description" />
        </BaseField>
      </div>

      <details
        class="more-fields"
        :open="showMoreCreateFields"
        @toggle="showMoreCreateFields = ($event.target as HTMLDetailsElement).open"
      >
        <summary>Weitere Felder</summary>
        <div class="create-grid mt-md">
          <BaseField label="Bestand">
            <BaseInput type="number" :min="0" v-model="createForm.quantity" />
          </BaseField>
          <BaseField label="Min-Bestand">
            <BaseInput type="number" :min="0" v-model="createForm.min_stock" />
          </BaseField>
          <BaseField label="Max-Bestand">
            <BaseInput type="number" :min="0" v-model="createForm.max_stock" />
          </BaseField>
          <BaseField label="Soll-Bestand">
            <BaseInput type="number" :min="0" v-model="createForm.target_stock" />
          </BaseField>
          <BaseField label="Empfohlen">
            <BaseInput type="number" :min="0" v-model="createForm.recommended_stock" />
          </BaseField>
          <BaseField label="Bestell-Modus">
            <BaseSelect
              v-model="createForm.order_mode"
              :options="[
                { label: '0 - Kein Alarm', value: 0 },
                { label: '1 - Alarm bei Unterschreitung', value: 1 },
                { label: '2 - In Bestellliste aufnehmen', value: 2 },
                { label: '3 - Automatisch nachbestellen', value: 3 }
              ]"
              placeholder="Wählen"
            />
          </BaseField>
        </div>
      </details>
    </section>

    <div v-else-if="!selectedArticle" class="placeholder mt-md">
      <p>Wähle einen Artikel aus der Tabelle oder klicke auf "Neuer Artikel".</p>
    </div>
  </section>

  <div v-if="importModalOpen" class="modal-backdrop">
    <div class="modal modal--large">
      <header class="modal__header">
        <div>
          <p class="eyebrow">Import</p>
          <h3>CSV Import</h3>
        </div>
        <button class="button button--ghost" type="button" @click="closeImportModal">Schließen</button>
      </header>

      <div v-if="importError" class="alert alert--error">{{ importError }}</div>

      <div class="wizard-steps">
        <span :class="{ active: importStep === 1 }">1. Datei</span>
        <span :class="{ active: importStep === 2 }">2. Mapping</span>
        <span :class="{ active: importStep === 3 }">3. Import</span>
      </div>

      <div v-if="importStep === 1" class="wizard-step">
        <p>Wähle eine CSV-Datei (UTF-8, Komma getrennt).</p>
        <input type="file" accept=".csv" @change="handleImportFile" />
        <div class="form-actions">
          <button class="button button--primary" type="button" :disabled="!importFile" @click="importStep = 2">
            Weiter
          </button>
        </div>
      </div>

      <div v-if="importStep === 2" class="wizard-step">
        <p>Ordne die Pflichtfelder den CSV-Spalten zu.</p>
        <div class="mapping-grid">
          <label v-for="field in requiredMappingFields" :key="field">
            <span>{{ field.toUpperCase() }} *</span>
            <select v-model="importMapping[field]">
              <option value="">Quelle Spalte auswählen</option>
              <option v-for="header in importHeaders" :key="header" :value="header">{{ header }}</option>
            </select>
          </label>
        </div>
        <div v-if="importPreview.length" class="import-preview">
          <p>Vorschau (erste Zeilen):</p>
          <table class="table">
            <thead>
              <tr>
                <th v-for="header in importHeaders" :key="header">{{ header }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in importPreview" :key="index">
                <td v-for="(cell, idx) in row" :key="idx">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="form-actions">
          <button class="button button--ghost" type="button" @click="importStep = 1">Zurück</button>
          <button class="button button--primary" type="button" :disabled="!isMappingValid" @click="importStep = 3">
            Weiter
          </button>
        </div>
      </div>

      <div v-if="importStep === 3" class="wizard-step">
        <p>Import starten. Pflichtfelder müssen zugeordnet sein.</p>
        <div class="form-actions">
          <button class="button button--ghost" type="button" @click="importStep = 2">Zurück</button>
          <button class="button button--primary" type="button" :disabled="importLoading" @click="startImport">
            {{ importLoading ? 'Import läuft...' : 'Import starten' }}
          </button>
          <button class="button button--ghost" type="button" @click="closeImportModal">Schließen</button>
        </div>
        <div v-if="!importLoading && (importResult.created || importResult.updated || importResult.errors.length)" class="import-result">
          <p>Erstellt: {{ importResult.created }}</p>
          <p>Aktualisiert: {{ importResult.updated }}</p>
          <p>Fehler: {{ importResult.errors.length }}</p>
          <table v-if="importResult.errors.length" class="table">
            <thead>
              <tr>
                <th>Zeile</th>
                <th>Meldung</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="err in importResult.errors" :key="err.row">
                <td>{{ err.row }}</td>
                <td>{{ err.error }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.artikelverwaltung {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-head__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  align-items: end;
}

.toolbar__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toolbar__label {
  color: var(--color-text-muted);
  font-size: 13px;
}
.toolbar__focus {
  height: 100%;
  align-self: flex-end;
}

.table-card {
  padding: 16px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.table-meta {
  color: var(--color-text-muted);
}

.table--clickable tbody tr {
  cursor: pointer;
}

.table-row--active {
  background: rgba(47, 123, 255, 0.08);
}

.pagination {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
  padding-top: 12px;
}

.create-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
}

.create-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.create-grid .full-span {
  grid-column: 1 / -1;
}

@media (min-width: 768px) {
  .create-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1200px) {
  .create-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.detail-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.detail-card__actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.form-grid {
  display: grid;
  gap: 12px;
}

.form-grid.two-col {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.form-section {
  display: grid;
  gap: 10px;
}

.form-section h4 {
  margin: 0 0 4px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.full-width {
  grid-column: 1 / -1;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
  padding: 16px;
  z-index: 10;
}

.modal {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 20px;
  width: min(960px, 100%);
  box-shadow: var(--shadow-soft);
}

.modal--large {
  width: min(1120px, 100%);
}

.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.wizard-steps {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.wizard-steps span {
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}

.wizard-steps span.active {
  background: rgba(47, 123, 255, 0.12);
  color: var(--color-primary-strong);
}

.mapping-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.import-preview {
  margin-top: 12px;
}

.import-result {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.alert--muted {
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}

.more-fields summary {
  cursor: pointer;
  font-weight: 600;
}
</style>
