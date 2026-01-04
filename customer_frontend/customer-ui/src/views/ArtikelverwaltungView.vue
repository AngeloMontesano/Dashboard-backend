<script setup lang="ts">
import { onMounted, reactive, ref, computed, watch } from 'vue';
import {
  fetchCategories,
  fetchItems,
  createItem,
  checkSkuExists,
  exportItems,
  importItems,
  createCategory,
  updateCategory,
  type Category,
  type Item
} from '@/api/inventory';
import { useAuth } from '@/composables/useAuth';

const { state: authState, isAuthenticated } = useAuth();
const isLoading = ref(false);
const isImporting = ref(false);
const isCreating = ref(false);
const message = ref<string | null>(null);
const error = ref<string | null>(null);
const skuHint = ref<string | null>(null);
const categoryError = ref<string | null>(null);
const categoryMessage = ref<string | null>(null);
const editingCategoryId = ref<string | null>(null);
const categoryNameInput = ref('');

const categories = ref<Category[]>([]);
const items = ref<Item[]>([]);
const total = ref(0);

const filters = reactive({
  q: '',
  category_id: '' as string | null,
  active: true,
  page: 1,
  page_size: 25
});

const newItem = reactive({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  quantity: 0,
  unit: 'pcs',
  is_active: true,
  category_id: '' as string | null,
  min_stock: 0,
  max_stock: 0,
  target_stock: 0,
  recommended_stock: 0,
  order_mode: 0
});

const isLoggedIn = computed(() => isAuthenticated());

async function loadCategories() {
  if (!authState.accessToken) return;
  const data = await fetchCategories(authState.accessToken);
    categories.value = data.filter((c) => c.is_active);
  }

  async function loadItems() {
  if (!authState.accessToken) return;
  isLoading.value = true;
  error.value = null;
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
  } catch (err: any) {
    error.value = err?.message || 'Konnte Artikel nicht laden';
  } finally {
    isLoading.value = false;
  }
}

async function handleSkuBlur() {
  skuHint.value = null;
  if (!newItem.sku || !authState.accessToken) return;
  try {
    const res = await checkSkuExists(authState.accessToken, newItem.sku);
    if (res.exists) {
      skuHint.value = `SKU bereits vergeben (${res.normalized_sku})`;
    } else if (res.normalized_sku !== newItem.sku) {
      skuHint.value = `SKU wird gespeichert als ${res.normalized_sku}`;
    }
  } catch {
    // ignore hint errors
  }
}

async function handleCreate() {
  if (!authState.accessToken) return;
  error.value = null;
  message.value = null;
  isCreating.value = true;
  try {
    await createItem(authState.accessToken, {
      ...newItem,
      category_id: newItem.category_id || null
    });
    message.value = 'Artikel angelegt';
    resetForm();
    await loadItems();
  } catch (err: any) {
    error.value = err?.response?.data?.error?.message || err?.message || 'Anlage fehlgeschlagen';
  } finally {
    isCreating.value = false;
  }
}

function resetForm() {
  newItem.sku = '';
  newItem.barcode = '';
  newItem.name = '';
  newItem.description = '';
  newItem.quantity = 0;
  newItem.unit = 'pcs';
  newItem.is_active = true;
  newItem.category_id = '';
  newItem.min_stock = 0;
  newItem.max_stock = 0;
  newItem.target_stock = 0;
  newItem.recommended_stock = 0;
  newItem.order_mode = 0;
  skuHint.value = null;
}

async function handleExport() {
  if (!authState.accessToken) return;
  error.value = null;
  message.value = null;
  try {
    const csv = await exportItems(authState.accessToken);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const now = new Date().toISOString().split('T')[0];
    link.setAttribute('download', `artikel-${now}.csv`);
    link.click();
    window.URL.revokeObjectURL(url);
    message.value = 'Export erfolgreich';
  } catch (err: any) {
    error.value = err?.message || 'Export fehlgeschlagen';
  }
}

async function handleImport(event: Event) {
  if (!authState.accessToken) return;
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  isImporting.value = true;
  error.value = null;
  message.value = null;
  try {
    const res = await importItems(authState.accessToken, file);
    const hint = [`Importiert: ${res.imported}`, `Aktualisiert: ${res.updated}`];
    if (res.errors.length) {
      hint.push(`Fehler: ${res.errors.length}`);
      error.value = res.errors.slice(0, 3).map((e) => `Zeile ${e.row}: ${e.error}`).join('; ');
    } else {
      message.value = hint.join(' | ');
    }
    await loadItems();
  } catch (err: any) {
    error.value = err?.response?.data?.error?.message || err?.message || 'Import fehlgeschlagen';
  } finally {
    isImporting.value = false;
    target.value = '';
  }
}

onMounted(async () => {
  if (!isLoggedIn.value) return;
  await loadCategories();
  await loadItems();
});

watch(
  () => authState.accessToken,
  async (token) => {
    if (token) {
      await loadCategories();
      await loadItems();
    } else {
      items.value = [];
      categories.value = [];
    }
  }
);

async function handleDeactivate(item: Item, active: boolean) {
  if (!authState.accessToken) return;
  error.value = null;
  message.value = null;
  try {
    await updateItem(authState.accessToken, item.id, { is_active: active });
    message.value = active ? 'Artikel aktiviert' : 'Artikel deaktiviert';
    await loadItems();
  } catch (err: any) {
    error.value = err?.response?.data?.error?.message || err?.message || 'Aktion fehlgeschlagen';
  }
}

function selectForEdit(item: Item) {
  newItem.sku = item.sku;
  newItem.barcode = item.barcode;
  newItem.name = item.name;
  newItem.description = item.description;
  newItem.quantity = item.quantity;
  newItem.unit = item.unit;
  newItem.is_active = item.is_active;
  newItem.category_id = item.category_id || '';
  newItem.min_stock = item.min_stock;
  newItem.max_stock = item.max_stock;
  newItem.target_stock = item.target_stock;
  newItem.recommended_stock = item.recommended_stock;
  newItem.order_mode = item.order_mode;
}

async function handleUpdate(item: Item) {
  if (!authState.accessToken) return;
  error.value = null;
  message.value = null;
  try {
    await updateItem(authState.accessToken, item.id, {
      ...newItem,
      category_id: newItem.category_id || null
    });
    message.value = 'Artikel aktualisiert';
    resetForm();
    await loadItems();
  } catch (err: any) {
    error.value = err?.response?.data?.error?.message || err?.message || 'Aktualisierung fehlgeschlagen';
  }
}

async function handleCreateCategory() {
  if (!authState.accessToken) return;
  categoryError.value = null;
  categoryMessage.value = null;
  try {
    await createCategory(authState.accessToken, { name: categoryNameInput.value });
    categoryMessage.value = 'Kategorie angelegt';
    categoryNameInput.value = '';
    await loadCategories();
  } catch (err: any) {
    categoryError.value = err?.response?.data?.error?.message || err?.message || 'Kategorie konnte nicht angelegt werden';
  }
}

async function handleUpdateCategory(cat: Category) {
  if (!authState.accessToken) return;
  categoryError.value = null;
  categoryMessage.value = null;
  try {
    await updateCategory(authState.accessToken, cat.id, { name: categoryNameInput.value || cat.name });
    categoryMessage.value = 'Kategorie aktualisiert';
    categoryNameInput.value = '';
    editingCategoryId.value = null;
    await loadCategories();
  } catch (err: any) {
    categoryError.value = err?.response?.data?.error?.message || err?.message || 'Kategorie konnte nicht aktualisiert werden';
  }
}

async function handleToggleCategory(cat: Category, active: boolean) {
  if (!authState.accessToken) return;
  categoryError.value = null;
  categoryMessage.value = null;
  try {
    await updateCategory(authState.accessToken, cat.id, { is_active: active });
    categoryMessage.value = active ? 'Kategorie aktiviert' : 'Kategorie deaktiviert';
    await loadCategories();
  } catch (err: any) {
    categoryError.value = err?.response?.data?.error?.message || err?.message || 'Status konnte nicht geändert werden';
  }
}

function startEditCategory(cat: Category) {
  if (cat.is_system) return;
  editingCategoryId.value = cat.id;
  categoryNameInput.value = cat.name;
}
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Stammdaten</p>
        <h2 class="section-title">Artikelverwaltung</h2>
        <p class="section-subtitle">Artikel, Barcodes und Mindestbestände pro Tenant verwalten.</p>
      </div>
      <div class="actions">
        <label class="button button--ghost" style="cursor: pointer">
          <input type="file" accept=".csv" style="display: none" @change="handleImport" />
          Import CSV
        </label>
        <button class="button button--ghost" type="button" @click="handleExport" :disabled="!isLoggedIn">Export CSV</button>
      </div>
    </header>

    <div v-if="message" class="alert alert--success">{{ message }}</div>
    <div v-if="error" class="alert alert--error">{{ error }}</div>

    <div class="filters">
      <input v-model="filters.q" type="search" placeholder="Suche SKU, Barcode, Name" />
      <select v-model="filters.category_id">
        <option value="">Alle Kategorien</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
      <select v-model="filters.active">
        <option :value="true">Nur aktive</option>
        <option :value="false">Nur inaktive</option>
        <option :value="null">Alle</option>
      </select>
      <button class="button button--ghost" type="button" @click="loadItems" :disabled="isLoading">Aktualisieren</button>
      <label>
        <span class="sr-only">Seitengröße</span>
        <select v-model.number="filters.page_size">
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </label>
    </div>

    <div class="cards-grid" style="margin-bottom: 16px">
      <article class="card">
        <h3 class="card__title">Artikel gesamt</h3>
        <p class="card__value">{{ total }}</p>
        <p class="card__hint">aktuell gefiltert</p>
      </article>
    </div>

    <div class="table-wrapper" v-if="items.length">
      <table class="table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Barcode</th>
            <th>Name</th>
            <th>Bestand</th>
            <th>Mindestbestand</th>
            <th>Bestellung</th>
            <th>Kategorie</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.sku }}</td>
            <td>{{ item.barcode }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.quantity }}</td>
            <td>{{ item.min_stock }}</td>
            <td>{{ item.order_mode }}</td>
            <td>{{ item.category_name || '—' }}</td>
            <td>
              <span :class="['badge', item.is_active ? 'badge--success' : 'badge--muted']">
                {{ item.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td class="table-actions">
              <button class="button button--ghost" type="button" @click="selectForEdit(item)">Bearbeiten</button>
              <button
                class="button button--ghost"
                type="button"
                @click="handleDeactivate(item, !item.is_active)"
              >
                {{ item.is_active ? 'Deaktivieren' : 'Aktivieren' }}
              </button>
              <button class="button button--ghost" type="button" @click="handleUpdate(item)">Speichern</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        <button class="button button--ghost" type="button" :disabled="filters.page <= 1" @click="filters.page = filters.page - 1; loadItems();">
          Zurück
        </button>
        <span>Seite {{ filters.page }}</span>
        <button
          class="button button--ghost"
          type="button"
          :disabled="filters.page * filters.page_size >= total"
          @click="filters.page = filters.page + 1; loadItems();"
        >
          Weiter
        </button>
      </div>
    </div>
    <div v-else class="placeholder">
      <p v-if="isLoading">Lade Artikel...</p>
      <p v-else>Keine Artikel gefunden.</p>
    </div>

    <section class="card" style="margin-top: 24px">
      <h3 class="card__title">Neuer Artikel</h3>
      <form class="form-grid" @submit.prevent="handleCreate">
        <label>
          <span>SKU *</span>
          <input v-model="newItem.sku" required @blur="handleSkuBlur" />
          <small v-if="skuHint">{{ skuHint }}</small>
        </label>
        <label>
          <span>Barcode *</span>
          <input v-model="newItem.barcode" required />
        </label>
        <label>
          <span>Name *</span>
          <input v-model="newItem.name" required />
        </label>
        <label>
          <span>Kategorie</span>
          <select v-model="newItem.category_id">
            <option value="">Keine</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </label>
        <label>
          <span>Beschreibung</span>
          <textarea v-model="newItem.description" rows="2" />
        </label>
        <label>
          <span>Bestand</span>
          <input type="number" v-model.number="newItem.quantity" min="0" />
        </label>
        <label>
          <span>Einheit</span>
          <input v-model="newItem.unit" />
        </label>
        <label>
          <span>Min-Bestand</span>
          <input type="number" v-model.number="newItem.min_stock" min="0" />
        </label>
        <label>
          <span>Max-Bestand</span>
          <input type="number" v-model.number="newItem.max_stock" min="0" />
        </label>
        <label>
          <span>Soll-Bestand</span>
          <input type="number" v-model.number="newItem.target_stock" min="0" />
        </label>
        <label>
          <span>Empfohlen</span>
          <input type="number" v-model.number="newItem.recommended_stock" min="0" />
        </label>
        <label>
          <span>Bestell-Modus</span>
          <select v-model.number="newItem.order_mode">
            <option :value="0">0 - Kein Alarm</option>
            <option :value="1">1 - Alarm bei Unterschreitung</option>
            <option :value="2">2 - In Bestellliste aufnehmen</option>
            <option :value="3">3 - Automatisch nachbestellen</option>
          </select>
        </label>
        <label class="checkbox">
          <input type="checkbox" v-model="newItem.is_active" />
          <span>Aktiv</span>
        </label>
        <div class="form-actions">
          <button class="button button--primary" type="submit" :disabled="isCreating">Speichern</button>
          <button class="button button--ghost" type="button" @click="resetForm">Zurücksetzen</button>
        </div>
      </form>
    </section>

    <section class="card" style="margin-top: 24px">
      <h3 class="card__title">Kategorien verwalten</h3>
      <div v-if="categoryMessage" class="alert alert--success">{{ categoryMessage }}</div>
      <div v-if="categoryError" class="alert alert--error">{{ categoryError }}</div>
      <form class="form-inline" @submit.prevent="editingCategoryId ? null : handleCreateCategory">
        <input
          v-model="categoryNameInput"
          placeholder="Kategoriename"
          :disabled="Boolean(editingCategoryId)"
          required
        />
        <button class="button button--primary" type="submit" :disabled="Boolean(editingCategoryId)">Neue Kategorie</button>
      </form>
      <table class="table" style="margin-top: 12px">
        <thead>
          <tr>
            <th>Name</th>
            <th>System</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>
              <span v-if="editingCategoryId !== cat.id">{{ cat.name }}</span>
              <input
                v-else
                v-model="categoryNameInput"
                :disabled="cat.is_system"
              />
            </td>
            <td>{{ cat.is_system ? 'Ja' : 'Nein' }}</td>
            <td>
              <span :class="['badge', cat.is_active ? 'badge--success' : 'badge--muted']">
                {{ cat.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td class="table-actions">
              <button
                class="button button--ghost"
                type="button"
                :disabled="cat.is_system"
                @click="startEditCategory(cat)"
              >
                Bearbeiten
              </button>
              <button
                v-if="editingCategoryId === cat.id"
                class="button button--primary"
                type="button"
                @click="handleUpdateCategory(cat)"
              >
                Speichern
              </button>
              <button
                class="button button--ghost"
                type="button"
                :disabled="cat.is_system"
                @click="handleToggleCategory(cat, !cat.is_active)"
              >
                {{ cat.is_active ? 'Deaktivieren' : 'Aktivieren' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>
