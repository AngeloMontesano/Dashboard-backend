<template>
  <UiPage>
    <UiSection title="Globale Einheiten" subtitle="Einheiten für Artikel (Admin-weit, ohne Tenant-Kontext)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadUnits">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">Globale Einheiten werden direkt im Backend verwaltet. Semikolon-CSV und XLSX Import/Export stehen bereit.</p>
        </div>
      </div>

      <div class="filter-card two-column">
        <div class="stack">
          <label class="field-label" for="global-unit-search">Suche</label>
          <input
            id="global-unit-search"
            class="input"
            v-model.trim="search"
            placeholder="Einheit oder Beschreibung"
            aria-label="Globale Einheiten filtern"
          />
          <div class="hint">Filtert nur den lokalen Zustand.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredUnits.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Import / Export</div>
          <div class="text-muted text-small">Semikolon als CSV-Trenner. XLSX unterstützt.</div>
        </div>
        <div class="box stack">
          <div class="row gap8 wrap">
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportUnits('csv')">
              {{ busy.export ? "exportiert..." : "Export CSV" }}
            </button>
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportUnits('xlsx')">
              {{ busy.export ? "exportiert..." : "Export XLSX" }}
            </button>
            <label class="btnGhost small file-btn">
              Datei wählen (csv/xlsx)
              <input type="file" accept=".csv,.xlsx,.xls" @change="onFileSelected" />
            </label>
            <button class="btnPrimary small" type="button" :disabled="busy.import || !importFile" @click="importUnits">
              {{ busy.import ? "importiert..." : "Import starten" }}
            </button>
          </div>
          <ul class="bullets">
            <li>CSV Header: <code>code;label;is_active</code> (Semikolon).</li>
            <li>Bestehende Codes werden aktualisiert, neue Einheiten angelegt.</li>
          </ul>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Einheiten</div>
          <div class="text-muted text-small">Globale Liste aus dem Backend.</div>
        </div>
        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Bezeichnung</th>
                <th>Status</th>
                <th class="narrowCol"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in filteredUnits"
                :key="entry.code"
                :class="{ rowActive: selectedCode === entry.code }"
                @click="select(entry.code)"
              >
                <td class="mono">{{ entry.code }}</td>
                <td>{{ entry.label }}</td>
                <td>
                  <span class="tag" :class="entry.is_active ? 'ok' : 'bad'">
                    {{ entry.is_active ? "aktiv" : "deaktiviert" }}
                  </span>
                </td>
                <td class="text-right">
                  <div class="row gap8">
                    <button class="btnGhost small" type="button" @click.stop="openEdit(entry)">Bearbeiten</button>
                    <button class="btnGhost small danger" type="button" @click.stop="remove(entry)">Löschen</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredUnits.length">
                <td colspan="4" class="mutedPad">Noch keine Einheiten im UI hinterlegt.</td>
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
              <div class="modal__title">{{ modal.mode === "create" ? "Einheit anlegen" : "Einheit bearbeiten" }}</div>
              <button class="btnGhost small" type="button" @click="closeModal">Schließen</button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <label class="field">
                  <span class="field-label">Code *</span>
                  <input class="input" v-model.trim="modal.code" placeholder="pcs, kg, l" :disabled="modal.mode === 'edit'" />
                </label>
                <label class="field">
                  <span class="field-label">Bezeichnung *</span>
                  <input class="input" v-model.trim="modal.label" placeholder="z. B. Stück, Kilogramm" />
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
                </label>
              </div>
            </div>
            <div class="modal__footer modal__footer--with-delete">
              <button
                v-if="modal.mode === 'edit'"
                class="btnGhost small danger"
                type="button"
                :disabled="busy.save"
                @click="removeFromModal"
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
  type GlobalUnit,
} from "../composables/useGlobalMasterdata";
import {
  fetchGlobalUnits,
  upsertGlobalUnit,
  deleteGlobalUnit,
  importGlobalUnits,
  exportGlobalUnits,
} from "../api/globals";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { units, upsertUnit, replaceUnits } = useGlobalMasterdata();

const search = ref("");
const selectedCode = ref("");
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
  code: "",
  label: "",
  is_active: true,
});

const filteredUnits = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = units.value || [];
  if (!term) return list;
  return list.filter(
    (t) => t.code.toLowerCase().includes(term) || (t.label || "").toLowerCase().includes(term)
  );
});

function resetFilters() {
  search.value = "";
}

function select(code: string) {
  selectedCode.value = code;
}

function openCreateModal() {
  modal.open = true;
  modal.mode = "create";
  modal.code = "";
  modal.label = "";
  modal.is_active = true;
}

function openEdit(entry: GlobalUnit) {
  modal.open = true;
  modal.mode = "edit";
  modal.code = entry.code;
  modal.label = entry.label;
  modal.is_active = entry.is_active;
}

function closeModal() {
  modal.open = false;
}

async function loadUnits() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich");
    return;
  }
  busy.load = true;
  try {
    const res = await fetchGlobalUnits(props.adminKey, props.actor);
    replaceUnits(res);
    toast(`Einheiten geladen (${res.length})`);
  } catch (e: any) {
    toast(`Laden fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.load = false;
  }
}

async function save() {
  const code = modal.code.trim();
  const label = modal.label.trim();
  if (!code || !label) {
    toast("Code und Bezeichnung sind Pflicht", "warning");
    return;
  }
  busy.save = true;
  try {
    const payload: GlobalUnit = { code, label, is_active: modal.is_active };
    const saved = await upsertGlobalUnit(props.adminKey, payload, props.actor);
    upsertUnit(saved);
    selectedCode.value = saved.code;
    toast(modal.mode === "edit" ? "Einheit aktualisiert" : "Einheit angelegt", "success");
    closeModal();
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.save = false;
  }
}

async function remove(entry: GlobalUnit) {
  if (!window.confirm(`Einheit ${entry.code} löschen?`)) return;
  try {
    await deleteGlobalUnit(props.adminKey, entry.code, props.actor);
    replaceUnits(units.value.filter((u) => u.code !== entry.code));
    toast("Einheit gelöscht", "success");
  } catch (e: any) {
    toast(`Löschen fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "error");
  }
}

async function removeFromModal() {
  const current = units.value.find((u) => u.code === modal.code);
  if (!current) return;
  await remove(current);
  closeModal();
}

function onFileSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  importFile.value = files && files.length ? files[0] : null;
}

async function importUnits() {
  if (!importFile.value) {
    toast("Bitte Datei wählen", "warning");
    return;
  }
  busy.import = true;
  try {
    const res = await importGlobalUnits(props.adminKey, importFile.value, props.actor);
    toast(`Importiert: ${res.imported}, aktualisiert: ${res.updated}`, res.errors?.length ? "warning" : "success");
    await loadUnits();
  } catch (e: any) {
    toast(`Import fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.import = false;
  }
}

async function exportUnits(format: "csv" | "xlsx") {
  busy.export = true;
  try {
    const blob = await exportGlobalUnits(props.adminKey, format, props.actor);
    const filename = `globale_einheiten.${format === "csv" ? "csv" : "xlsx"}`;
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
    loadUnits();
  }
});
</script>
