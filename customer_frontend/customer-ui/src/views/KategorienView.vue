<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { createCategory, fetchCategories, updateCategory, type Category } from '@/api/inventory';
import { useAuth } from '@/composables/useAuth';

const { state: authState, isAuthenticated } = useAuth();
const hasWriteAccess = computed(() => ['owner', 'admin'].includes(authState.role));

const categories = ref<Category[]>([]);
const isLoading = ref(false);
const feedback = reactive({ error: '', message: '' });

const form = reactive({
  name: '',
  is_active: true
});

async function loadCategories() {
  if (!authState.accessToken) return;
  isLoading.value = true;
  feedback.error = '';
  try {
    categories.value = await fetchCategories(authState.accessToken);
  } catch (err: any) {
    feedback.error = err?.message || 'Konnte Kategorien nicht laden.';
  } finally {
    isLoading.value = false;
  }
}

async function handleCreate() {
  if (!authState.accessToken || !hasWriteAccess.value || !form.name.trim()) {
    return;
  }
  feedback.error = '';
  feedback.message = '';
  try {
    await createCategory(authState.accessToken, { name: form.name.trim(), is_active: form.is_active });
    feedback.message = 'Kategorie angelegt.';
    form.name = '';
    form.is_active = true;
    await loadCategories();
  } catch (err: any) {
    feedback.error = err?.response?.data?.error?.message || err?.message || 'Kategorie konnte nicht angelegt werden.';
  }
}

async function toggleCategory(cat: Category, active: boolean) {
  if (!authState.accessToken || !hasWriteAccess.value) return;
  feedback.error = '';
  feedback.message = '';
  try {
    await updateCategory(authState.accessToken, cat.id, { is_active: active });
    feedback.message = active ? 'Kategorie aktiviert.' : 'Kategorie deaktiviert.';
    await loadCategories();
  } catch (err: any) {
    feedback.error = err?.response?.data?.error?.message || err?.message || 'Status konnte nicht geändert werden.';
  }
}

async function renameCategory(cat: Category, name: string) {
  if (!authState.accessToken || !hasWriteAccess.value || !name.trim()) return;
  feedback.error = '';
  feedback.message = '';
  try {
    await updateCategory(authState.accessToken, cat.id, { name: name.trim() });
    feedback.message = 'Kategorie aktualisiert.';
    await loadCategories();
  } catch (err: any) {
    feedback.error = err?.response?.data?.error?.message || err?.message || 'Kategorie konnte nicht aktualisiert werden.';
  }
}

onMounted(async () => {
  if (!isAuthenticated()) return;
  await loadCategories();
});
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Stammdaten</p>
        <h2 class="section-title">Kategorien</h2>
        <p class="section-subtitle">Kategorien verwalten und aktivieren/deaktivieren.</p>
      </div>
    </header>

    <div v-if="feedback.message" class="alert alert--success">{{ feedback.message }}</div>
    <div v-if="feedback.error" class="alert alert--error">{{ feedback.error }}</div>

    <form class="form-inline" @submit.prevent="handleCreate">
      <input v-model="form.name" placeholder="Kategoriename" required :disabled="!hasWriteAccess" />
      <label class="checkbox">
        <input type="checkbox" v-model="form.is_active" :disabled="!hasWriteAccess" />
        <span>Aktiv</span>
      </label>
      <button class="button button--primary" type="submit" :disabled="!hasWriteAccess">Neue Kategorie</button>
    </form>

    <div class="table-wrapper" style="margin-top: 12px" v-if="categories.length">
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>System</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>
              <input
                :value="cat.name"
                :disabled="cat.is_system || !hasWriteAccess"
                @change="renameCategory(cat, ($event.target as HTMLInputElement).value)"
              />
            </td>
            <td>
              <span :class="['badge', cat.is_active ? 'badge--success' : 'badge--muted']">
                {{ cat.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
            </td>
            <td>{{ cat.is_system ? 'Ja' : 'Nein' }}</td>
            <td class="table-actions">
              <button
                class="button button--ghost"
                type="button"
                :disabled="cat.is_system || !hasWriteAccess"
                @click="toggleCategory(cat, !cat.is_active)"
              >
                {{ cat.is_active ? 'Deaktivieren' : 'Aktivieren' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="placeholder">
      <p v-if="isLoading">Lade Kategorien...</p>
      <p v-else>Keine Kategorien vorhanden.</p>
    </div>
  </section>
</template>

<style scoped>
.form-inline {
  display: flex;
  gap: 8px;
  align-items: center;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
