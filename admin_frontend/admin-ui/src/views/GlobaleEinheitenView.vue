<template>
  <UiPage>
    <UiSection title="Globale Einheiten" subtitle="Einheiten für Artikel (UI-only, Backend-Endpunkte fehlen)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadUnits">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Keine OpenAPI-Pfade für globale Einheiten vorhanden. Aktionen werden nur im UI gespeichert und dienen als
            Vorbereitung, bis passende Backend-Endpunkte existieren. Einheiten sollten in Artikeln wiederverwendet
            werden, sobald das Backend sie bereitstellt.
          </p>
        </div>
      </div>

      <div class="filter-card">
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
          <div class="tableTitle">Einheiten</div>
          <div class="text-muted text-small">UI-only, nicht im Backend gespeichert.</div>
        </div>
        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Beschreibung</th>
                <th>Status</th>
                <th class="narrowCol"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in filteredUnits"
                :key="entry.id"
                :class="{ rowActive: selectedId === entry.id }"
                @click="select(entry.id)"
              >
                <td>{{ entry.name }}</td>
                <td class="text-muted text-small">{{ entry.description || "—" }}</td>
                <td>
                  <span class="tag" :class="entry.is_active ? 'ok' : 'bad'">
                    {{ entry.is_active ? "aktiv" : "deaktiviert" }}
                  </span>
                </td>
                <td class="text-right">
                  <button class="btnGhost small" type="button" @click.stop="openEdit(entry)">Bearbeiten</button>
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
                  <span class="field-label">Name *</span>
                  <input class="input" v-model.trim="modal.name" placeholder="z. B. Stück, kg, l" />
                </label>
                <label class="field">
                  <span class="field-label">Beschreibung</span>
                  <textarea class="input" rows="2" v-model="modal.description" placeholder="Optional"></textarea>
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
                </label>
              </div>
              <div class="hint">Aktion ist UI-only; Backend-Endpunkte fehlen noch.</div>
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
import { computed, reactive, ref } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalUnit,
  generateId,
} from "../composables/useGlobalMasterdata";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { units, upsertUnit } = useGlobalMasterdata();

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
  description: "",
  is_active: true,
});

const filteredUnits = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = units.value || [];
  if (!term) return list;
  return list.filter(
    (t) => t.name.toLowerCase().includes(term) || (t.description || "").toLowerCase().includes(term)
  );
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
  modal.description = "";
  modal.is_active = true;
}

function openEdit(entry: GlobalUnit) {
  modal.open = true;
  modal.mode = "edit";
  modal.id = entry.id;
  modal.name = entry.name;
  modal.description = entry.description || "";
  modal.is_active = entry.is_active;
}

function closeModal() {
  modal.open = false;
}

function save() {
  const name = modal.name.trim();
  if (!name) {
    toast("Name ist Pflicht", "warning");
    return;
  }
  busy.save = true;
  const payload: GlobalUnit = {
    id: modal.id || generateId(),
    name,
    description: modal.description?.trim() || "",
    is_active: modal.is_active,
  };
  upsertUnit(payload);
  selectedId.value = payload.id;
  toast(
    modal.mode === "edit" ? "Einheit aktualisiert (UI-only, Backend fehlt)" : "Einheit angelegt (UI-only, Backend fehlt)",
    "success"
  );
  busy.save = false;
  closeModal();
}

function loadUnits() {
  busy.load = true;
  toast("Backend-Unterstützung fehlt – kein Ladevorgang möglich", "warning");
  busy.load = false;
}
</script>
