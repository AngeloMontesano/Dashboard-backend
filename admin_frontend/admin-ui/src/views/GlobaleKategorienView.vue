<template>
  <UiPage>
    <UiSection title="Globale Kategorien" subtitle="Globale Stammdaten ohne Tenant-Kontext verwalten">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadCategories">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="filter-card">
        <div class="stack">
          <label class="field-label" for="global-category-search">Suche</label>
          <input
            id="global-category-search"
            class="input"
            v-model.trim="search"
            placeholder="Name enthält..."
            aria-label="Globale Kategorien suchen"
          />
          <div class="hint">Filtert lokal. Kein Backend-Request.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredCategories.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Kategorien</div>
          <div class="text-muted text-small">Schreibvorgänge erfolgen direkt gegen die Admin-API.</div>
        </div>
        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th class="narrowCol">System</th>
                <th class="narrowCol"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cat in filteredCategories"
                :key="cat.id"
                :class="{ rowActive: selectedId === cat.id }"
                @click="select(cat.id)"
              >
                <td>{{ cat.name }}</td>
                <td>
                  <span class="tag" :class="cat.is_active ? 'ok' : 'bad'">
                    {{ cat.is_active ? "aktiv" : "deaktiviert" }}
                  </span>
                </td>
                <td class="mono">{{ cat.is_system ? "ja" : "nein" }}</td>
                <td class="text-right">
                  <button class="btnGhost small" type="button" @click.stop="openEdit(cat)">Bearbeiten</button>
                </td>
              </tr>
              <tr v-if="!filteredCategories.length">
                <td colspan="4" class="mutedPad">Noch keine Kategorien im UI hinterlegt.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="modal.open">
        <div class="modal-backdrop" @click="closeModal"></div>
        <div class="modal-panel" @click.stop>
          <div class="modal">
            <div class="modal__header">
              <div class="modal__title">{{ modal.mode === "create" ? "Kategorie anlegen" : "Kategorie bearbeiten" }}</div>
              <button class="btnGhost small" type="button" @click="closeModal">Schließen</button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <label class="field">
                  <span class="field-label">Name *</span>
                  <input class="input" v-model.trim="modal.name" placeholder="z. B. Getränke" />
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_system" />
                  <span>System-Kategorie</span>
                </label>
              </div>
              <div class="hint">Änderungen werden sofort in der Datenbank gespeichert.</div>
            </div>
            <div class="modal__footer">
              <button class="btnGhost" type="button" @click="closeModal">Abbrechen</button>
              <button class="btnPrimary" type="button" :disabled="busy.save" @click="save">
                {{ busy.save ? "speichert..." : "Speichern" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalCategory,
} from "../composables/useGlobalMasterdata";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import {
  adminCreateGlobalCategory,
  adminListGlobalCategories,
  adminUpdateGlobalCategory,
} from "../api/admin";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { categories, upsertCategory, replaceCategories } = useGlobalMasterdata();

const search = ref("");
const selectedId = ref("");
const busy = reactive({
  load: false,
  save: false,
});

const modal = reactive({
  open: false,
  mode: "create" as "create" | "edit",
  id: "",
  name: "",
  is_active: true,
  is_system: false,
});

const filteredCategories = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = categories.value || [];
  if (!term) return list;
  return list.filter((c) => c.name.toLowerCase().includes(term));
});

function resetFilters() {
  search.value = "";
}

function select(id: string) {
  selectedId.value = id;
}

function openCreateModal() {
  modal.open = true;
  modal.mode = "create";
  modal.id = "";
  modal.name = "";
  modal.is_active = true;
  modal.is_system = false;
}

function openEdit(cat: GlobalCategory) {
  modal.open = true;
  modal.mode = "edit";
  modal.id = cat.id;
  modal.name = cat.name;
  modal.is_active = cat.is_active;
  modal.is_system = cat.is_system;
}

function closeModal() {
  modal.open = false;
}

async function loadCategories() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  busy.load = true;
  try {
    const res = await adminListGlobalCategories(props.adminKey, props.actor);
    replaceCategories(res as GlobalCategory[]);
    toast(`Kategorien geladen: ${res.length}`);
  } catch (e: any) {
    toast(e?.message || "Laden fehlgeschlagen", "error");
  } finally {
    busy.load = false;
  }
}

async function save() {
  const name = modal.name.trim();
  if (!name) {
    toast("Name ist Pflicht", "warning");
    return;
  }
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  busy.save = true;
  try {
    const payload = { name, is_active: modal.is_active };
    let saved: GlobalCategory;
    if (modal.mode === "edit" && modal.id) {
      saved = await adminUpdateGlobalCategory(props.adminKey, props.actor, modal.id, payload);
    } else {
      saved = await adminCreateGlobalCategory(props.adminKey, props.actor, payload);
    }
    upsertCategory(saved);
    selectedId.value = saved.id;
    toast(modal.mode === "edit" ? "Kategorie aktualisiert" : "Kategorie angelegt", "success");
  } catch (e: any) {
    toast(e?.message || "Speichern fehlgeschlagen", "error");
  } finally {
    busy.save = false;
    closeModal();
  }
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadCategories();
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.adminKey) {
    loadCategories();
  }
});
</script>
