<script setup lang="ts">
import { onMounted, reactive, computed } from 'vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import UiEmptyState from '@/components/ui/UiEmptyState.vue';
import { useAuth } from '@/composables/useAuth';
import { fetchItems, exportInventory, bulkUpdateInventory } from '@/api/inventory';
import AuthReauthBanner from '@/components/auth/AuthReauthBanner.vue';
import { useAuthIssueBanner } from '@/composables/useAuthIssueBanner';

const { state: authState } = useAuth();
const { authIssue, authMessage, handleAuthError } = useAuthIssueBanner();

type Item = Awaited<ReturnType<typeof fetchItems>>['items'][number];

const state = reactive<{
  items: Item[];
  loading: boolean;
  saving: boolean;
  exporting: boolean;
  error: string | null;
  success: string | null;
  draft: Record<string, number>;
}>({
  items: [],
  loading: false,
  saving: false,
  exporting: false,
  error: null,
  success: null,
  draft: {}
});

const totalItems = computed(() => state.items.length);
const belowMin = computed(() => state.items.filter((i) => i.quantity < i.min_stock).length);
const atTarget = computed(() => state.items.filter((i) => i.quantity >= i.target_stock).length);

function showError(err: unknown, fallback: string) {
  const classified = handleAuthError(err);
  const detail = classified.detailMessage || classified.userMessage || fallback;
  state.error = classified.category === 'auth' ? classified.userMessage : `${fallback}: ${detail}`;
}

async function loadItems() {
  if (!authState.accessToken) return;
  state.loading = true;
  state.error = null;
  try {
    const res = await fetchItems({ token: authState.accessToken, page: 1, page_size: 500, active: true });
    state.items = res.items;
    state.draft = res.items.reduce((acc, item) => {
      acc[item.id] = item.quantity;
      return acc;
    }, {} as Record<string, number>);
  } catch (err: any) {
    showError(err, 'Inventur-Daten konnten nicht geladen werden');
  } finally {
    state.loading = false;
  }
}

async function handleExport() {
  if (!authState.accessToken) return;
  state.exporting = true;
  state.error = null;
  try {
    const blob = await exportInventory(authState.accessToken);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'inventur.xlsx';
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    showError(err, 'Export fehlgeschlagen');
  } finally {
    state.exporting = false;
  }
}

async function handleSave() {
  if (!authState.accessToken) return;
  const updates = Object.entries(state.draft).map(([itemId, quantity]) => ({
    item_id: itemId,
    quantity: Number.isFinite(quantity) ? Number(quantity) : 0
  }));
  state.saving = true;
  state.error = null;
  state.success = null;
  try {
    await bulkUpdateInventory(authState.accessToken, { updates });
    state.success = 'Inventur gespeichert';
    await loadItems();
  } catch (err: any) {
    showError(err, 'Speichern fehlgeschlagen');
  } finally {
    state.saving = false;
  }
}

onMounted(loadItems);
</script>

<template>
  <UiPage>
    <UiSection title="Inventur" subtitle="Bestände prüfen, exportieren und aktualisieren.">
      <UiToolbar>
        <template #start>
          <p class="eyebrow">Bestände</p>
        </template>
        <template #end>
          <div class="action-row">
            <button class="btnGhost small" type="button" @click="loadItems" :disabled="state.loading">Neu laden</button>
            <button class="btnGhost small" type="button" @click="handleExport" :disabled="state.exporting">Export</button>
            <button class="btnPrimary small" type="button" @click="handleSave" :disabled="state.saving">Speichern</button>
          </div>
        </template>
      </UiToolbar>

      <AuthReauthBanner
        v-if="authIssue"
        class="mt-sm"
        :message="authMessage"
        retry-label="Neu laden"
        @retry="() => loadItems()"
      />

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
      </div>
      <div v-if="state.success" class="banner banner--success mt-sm">
        {{ state.success }}
      </div>

      <div class="cards-grid mt-md">
        <article class="card">
          <h3 class="card__title">Artikel gesamt</h3>
          <p class="card__value">{{ totalItems }}</p>
          <p class="card__hint">aktive Artikel</p>
        </article>
        <article class="card">
          <h3 class="card__title">Unter Mindestbestand</h3>
          <p class="card__value">{{ belowMin }}</p>
          <p class="card__hint">benötigen Auffüllung</p>
        </article>
        <article class="card">
          <h3 class="card__title">Soll erreicht</h3>
          <p class="card__value">{{ atTarget }}</p>
          <p class="card__hint">Artikel auf Zielbestand</p>
        </article>
      </div>

      <div class="mt-lg">
        <div class="tableWrap" v-if="state.items.length">
          <table class="table">
            <thead>
              <tr>
                <th>Artikel</th>
                <th>Barcode</th>
                <th>Kategorie</th>
                <th>Soll</th>
                <th>Min</th>
                <th>Bestand</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in state.items" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.barcode }}</td>
                <td>{{ item.category_name || '—' }}</td>
                <td>{{ item.target_stock }}</td>
                <td>{{ item.min_stock }}</td>
                <td>
                  <input v-model.number="state.draft[item.id]" type="number" min="0" class="input input--sm" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <UiEmptyState
          v-else
          class="mt-sm"
          title="Keine Artikel gefunden"
          description="Neu laden oder Filter anpassen, um Bestände zu erfassen."
        >
          <template #actions>
            <button class="btnGhost small" type="button" @click="loadItems" :disabled="state.loading">
              Neu laden
            </button>
          </template>
        </UiEmptyState>
      </div>
    </UiSection>
  </UiPage>
</template>
