<script setup lang="ts">
import { onMounted, reactive, ref, computed, watch } from 'vue';
import {
  fetchCategories,
  fetchItems,
  createItem,
  checkSkuExists,
  exportItems,
  importItems,
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
    link.setAttribute('download', 'artikel.csv');
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
          </tr>
        </tbody>
      </table>
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
  </section>
</template>
