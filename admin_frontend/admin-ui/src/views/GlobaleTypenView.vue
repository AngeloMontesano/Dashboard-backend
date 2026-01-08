<template>
  <UiPage>
    <UiSection title="Globale Typen" subtitle="Typ-Stammdaten (Admin-Key erforderlich)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadTypes">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Globale Typen sind zentrale Stammdaten und werden serverseitig gespeichert. Änderungen gelten tenant-übergreifend.
          </p>
        </div>
      </div>

      <div class="filter-card two-column">
        <div class="stack">
          <label class="field-label" for="global-type-search">Suche</label>
          <input
            id="global-type-search"
            class="input"
            v-model.trim="search"
            placeholder="Typname"
            aria-label="Globale Typen filtern"
          />
          <div class="hint">Filtert die aktuelle Liste.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredTypes.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Typen</div>
          <div class="text-muted text-small">Globale Liste aus dem Backend.</div>
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
                v-for="entry in filteredTypes"
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
                  <div class="row gap8">
                    <button class="btnGhost small" type="button" @click.stop="openEdit(entry)">Bearbeiten</button>
                    <button class="btnGhost small danger" type="button" @click.stop="remove(entry)">Löschen</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredTypes.length">
                <td colspan="4" class="mutedPad">Noch keine Typen vorhanden.</td>
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
              <div class="modal__title">{{ modal.mode === "create" ? "Typ anlegen" : "Typ bearbeiten" }}</div>
              <button class="btnGhost small" type="button" @click="closeModal">Schließen</button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <label class="field">
                  <span class="field-label">Name *</span>
                  <input class="input" v-model.trim="modal.name" placeholder="z. B. Produktgruppe A" />
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
              <div class="hint">Änderungen werden sofort gespeichert.</div>
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
import { computed, reactive, ref, onMounted } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalType,
} from "../composables/useGlobalMasterdata";
import {
  fetchGlobalTypes,
  createGlobalType,
  updateGlobalType,
  deleteGlobalType,
} from "../api/globals";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { types, upsertType, replaceTypes } = useGlobalMasterdata();

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

const filteredTypes = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = types.value || [];
  if (!term) return list;
  return list.filter((t) => t.name.toLowerCase().includes(term) || (t.description || "").toLowerCase().includes(term));
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

function openEdit(entry: GlobalType) {
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

async function save() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich", "warning");
    return;
  }
  const name = modal.name.trim();
  if (!name) {
    toast("Name ist Pflicht", "warning");
    return;
  }
  busy.save = true;
  const payload = {
    name,
    description: modal.description?.trim() || "",
    is_active: modal.is_active,
  };
  try {
    const result =
      modal.mode === "edit"
        ? await updateGlobalType(props.adminKey, modal.id, payload, props.actor)
        : await createGlobalType(props.adminKey, payload, props.actor);
    upsertType(result);
    selectedId.value = result.id;
    toast(modal.mode === "edit" ? "Typ aktualisiert" : "Typ angelegt", "success");
    closeModal();
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "danger");
  } finally {
    busy.save = false;
  }
}

async function loadTypes() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich", "warning");
    return;
  }
  busy.load = true;
  try {
    const rows = await fetchGlobalTypes(props.adminKey, props.actor);
    replaceTypes(rows);
    toast("Typen geladen", "success");
  } catch (e: any) {
    toast(`Typen konnten nicht geladen werden: ${e?.message || e}`, "danger");
  } finally {
    busy.load = false;
  }
}

async function remove(entry: GlobalType) {
  if (!props.adminKey) {
    toast("Admin Key erforderlich", "warning");
    return;
  }
  if (!confirm(`Typ "${entry.name}" löschen?`)) return;
  busy.save = true;
  try {
    await deleteGlobalType(props.adminKey, entry.id, props.actor);
    replaceTypes(types.value.filter((t) => t.id !== entry.id));
    toast("Typ gelöscht", "success");
    if (selectedId.value === entry.id) selectedId.value = "";
  } catch (e: any) {
    toast(`Löschen fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "danger");
  } finally {
    busy.save = false;
  }
}

onMounted(() => {
  loadTypes();
});
</script>
