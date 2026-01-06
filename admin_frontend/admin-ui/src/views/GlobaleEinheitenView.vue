<template>
  <UiPage>
    <UiSection title="Globale Einheiten" subtitle="Einheiten für Artikel (Admin-API)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadUnits">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

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
          <div class="text-muted text-small">Ergebnisse stammen direkt aus der Admin-API.</div>
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
                :class="{ rowActive: selectedId === entry.code }"
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
                  <span class="field-label">Code *</span>
                  <input class="input" v-model.trim="modal.code" placeholder="z. B. pcs, kg, l" :disabled="modal.mode === 'edit'" />
                </label>
                <label class="field">
                  <span class="field-label">Bezeichnung *</span>
                  <input class="input" v-model.trim="modal.label" placeholder="z. B. Stück" />
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
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
  type GlobalUnit,
} from "../composables/useGlobalMasterdata";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import { adminListUnits, adminUpsertUnit } from "../api/admin";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { units, upsertUnit, replaceUnits } = useGlobalMasterdata();

const search = ref("");
const selectedId = ref("");
const busy = reactive({
  load: false,
  save: false,
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

function select(id: string) {
  selectedId.value = id;
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

async function save() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  const code = modal.code.trim();
  const label = modal.label.trim();
  if (!code || !label) {
    toast("Code und Bezeichnung sind Pflicht", "warning");
    return;
  }
  busy.save = true;
  try {
    const payload: GlobalUnit = {
      code,
      label,
      is_active: modal.is_active,
    };
    const saved = await adminUpsertUnit(props.adminKey, props.actor, payload);
    upsertUnit(saved);
    selectedId.value = saved.code;
    toast(modal.mode === "edit" ? "Einheit aktualisiert" : "Einheit angelegt", "success");
  } catch (e: any) {
    toast(e?.message || "Speichern fehlgeschlagen", "error");
  } finally {
    busy.save = false;
    closeModal();
  }
}

async function loadUnits() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  busy.load = true;
  try {
    const res = await adminListUnits(props.adminKey, props.actor);
    replaceUnits(res as GlobalUnit[]);
    toast(`Einheiten geladen: ${res.length}`);
  } catch (e: any) {
    toast(e?.message || "Laden fehlgeschlagen", "error");
  } finally {
    busy.load = false;
  }
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadUnits();
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.adminKey) loadUnits();
});
</script>
