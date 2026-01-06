<template>
  <UiPage>
    <UiSection title="Globale Kategorien" subtitle="Stammdaten für globale Artikel (Admin-Key erforderlich)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadCategories">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Kategorien ohne Tenant-Kontext. Semikolon-CSV und XLSX Import/Export verfügbar. System-Kategorien sind im Customer-Frontend schreibgeschützt.
          </p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Import / Export</div>
          <div class="text-muted text-small">Semikolon als CSV-Trenner. XLSX wird unterstützt.</div>
        </div>
        <div class="box stack">
          <div class="row gap8 wrap">
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportCategories('csv')">
              {{ busy.export ? "exportiert..." : "Export CSV" }}
            </button>
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportCategories('xlsx')">
              {{ busy.export ? "exportiert..." : "Export XLSX" }}
            </button>
            <label class="btnGhost small file-btn">
              Datei wählen (csv/xlsx)
              <input type="file" accept=".csv,.xlsx,.xls" @change="onFileSelected" />
            </label>
            <button class="btnPrimary small" type="button" :disabled="busy.import || !importFile" @click="importCategories">
              {{ busy.import ? "importiert..." : "Import starten" }}
            </button>
          </div>
          <ul class="bullets">
            <li>CSV Header: <code>name;is_active;is_system</code></li>
            <li>Bestehende Namen werden aktualisiert.</li>
          </ul>
        </div>
      </div>

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
          <div class="hint">Serverseitige Stammdaten. System-Kategorien sind schreibgeschützt im Kunden-Frontend.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredCategories.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Kategorien</div>
          <div class="text-muted text-small">Globale Liste aus dem Backend.</div>
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
                  <div class="row gap8">
                    <button class="btnGhost small" type="button" @click.stop="openEdit(cat)">Bearbeiten</button>
                    <button class="btnGhost small danger" type="button" @click.stop="remove(cat)">Löschen</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredCategories.length">
                <td colspan="4" class="mutedPad">Noch keine Kategorien vorhanden.</td>
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
              <div class="hint">System-Kategorien sind auch im Customer-Frontend schreibgeschützt.</div>
            </div>
            <div class="modal__footer modal__footer--with-delete">
              <button
                v-if="modal.mode === 'edit'"
                class="btnGhost small danger"
                type="button"
                :disabled="busy.save"
                @click="removeConfirm"
              >
                Löschen
              </button>
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
import { computed, reactive, ref, onMounted } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalCategory,
} from "../composables/useGlobalMasterdata";
import {
  fetchGlobalCategories,
  createGlobalCategory,
  updateGlobalCategory,
  deleteGlobalCategory,
  importGlobalCategories,
  exportGlobalCategories,
} from "../api/globals";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { categories, upsertCategory, replaceCategories } = useGlobalMasterdata();

const search = ref("");
const selectedId = ref("");
const importFile = ref<File | null>(null);
const busy = reactive({
  load: false,
  save: false,
  import: false,
  export: false,
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
    toast("Admin Key erforderlich");
    return;
  }
  busy.load = true;
  try {
    const res = await fetchGlobalCategories(props.adminKey, props.actor);
    replaceCategories(res);
    toast(`Kategorien geladen (${res.length})`);
  } catch (e: any) {
    toast(`Laden fehlgeschlagen: ${e?.message || e}`, "error");
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
  busy.save = true;
  try {
    let saved: GlobalCategory;
    if (modal.mode === "edit" && modal.id) {
      saved = await updateGlobalCategory(
        props.adminKey,
        modal.id,
        { name, is_active: modal.is_active, is_system: modal.is_system },
        props.actor
      );
    } else {
      saved = await createGlobalCategory(
        props.adminKey,
        { name, is_active: modal.is_active, is_system: modal.is_system },
        props.actor
      );
    }
    upsertCategory(saved);
    selectedId.value = saved.id;
    toast(modal.mode === "edit" ? "Kategorie aktualisiert" : "Kategorie angelegt", "success");
    closeModal();
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.save = false;
  }
}

async function removeConfirm() {
  if (!modal.id) return;
  const cat = categories.value.find((c) => c.id === modal.id);
  if (!cat) return;
  if (!window.confirm(`Kategorie ${cat.name} löschen?`)) return;
  try {
    await deleteGlobalCategory(props.adminKey, cat.id, props.actor);
    replaceCategories(categories.value.filter((c) => c.id !== cat.id));
    closeModal();
    toast("Kategorie gelöscht", "success");
  } catch (e: any) {
    toast(`Löschen fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "error");
  }
}

function onFileSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  importFile.value = files && files.length ? files[0] : null;
}

async function importCategories() {
  if (!importFile.value) {
    toast("Bitte Datei wählen", "warning");
    return;
  }
  busy.import = true;
  try {
    const res = await importGlobalCategories(props.adminKey, importFile.value, props.actor);
    toast(`Importiert: ${res.imported}, aktualisiert: ${res.updated}`, res.errors?.length ? "warning" : "success");
    await loadCategories();
  } catch (e: any) {
    toast(`Import fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.import = false;
  }
}

async function exportCategories(format: "csv" | "xlsx") {
  busy.export = true;
  try {
    const blob = await exportGlobalCategories(props.adminKey, format, props.actor);
    const filename = `globale_kategorien.${format === "csv" ? "csv" : "xlsx"}`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    toast(`Export ${format.toUpperCase()} erstellt`);
  } catch (e: any) {
    toast(`Export fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.export = false;
  }
}

onMounted(() => {
  if (props.adminKey) {
    loadCategories();
  }
});
</script>

<style scoped>
.table-card .table {
  margin-top: 4px;
}

.modal__footer--with-delete {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.modal__footer--with-delete .btnGhost.danger {
  margin-right: auto;
}
</style>
