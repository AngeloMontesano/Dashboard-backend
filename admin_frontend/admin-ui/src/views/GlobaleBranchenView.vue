<template>
  <UiPage>
    <UiSection title="Globale Branchen" subtitle="Branchen und Artikel-Zuordnung (UI-only, Backend fehlt)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadIndustries">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Keine OpenAPI-Pfade für Branchen oder Branchen→Artikel-Mapping vorhanden. Aktionen werden nur im UI
            gespeichert, ein Backend-Speicher fehlt. Fehlende Endpunkte sind dokumentiert.
          </p>
        </div>
      </div>

      <div class="filter-card">
        <div class="stack">
          <label class="field-label" for="global-industry-search">Suche</label>
          <input
            id="global-industry-search"
            class="input"
            v-model.trim="search"
            placeholder="Branchenname"
            aria-label="Globale Branchen filtern"
          />
          <div class="hint">Filtert nur den lokalen Zustand.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredIndustries.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Branchen</div>
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
                v-for="entry in filteredIndustries"
                :key="entry.id"
                :class="{ rowActive: selectedIndustryId === entry.id }"
                @click="selectIndustry(entry.id)"
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
              <tr v-if="!filteredIndustries.length">
                <td colspan="4" class="mutedPad">Noch keine Branchen im UI hinterlegt.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Zugeordnete Artikel</div>
          <div class="text-muted text-small">
            UI-only Mapping. Speichern ohne Backend, damit Anforderungen sichtbar sind.
          </div>
        </div>
        <div class="box stack">
          <label class="field">
            <span class="field-label">Branche wählen</span>
            <select class="input" v-model="selectedIndustryId">
              <option value="">Bitte wählen</option>
              <option v-for="entry in industries" :key="entry.id" :value="entry.id">
                {{ entry.name }}
              </option>
            </select>
          </label>
          <div v-if="!items.length" class="muted text-small">
            Keine Artikel im UI vorhanden. Bitte erst unter „Globale Artikel“ erfassen.
          </div>
          <div v-else class="stack">
            <div class="field-label">Artikel auswählen</div>
            <div class="stack-sm">
              <label v-for="item in items" :key="item.id" class="field checkbox">
                <input
                  type="checkbox"
                  :value="item.id"
                  :checked="selectedArticleIds.includes(item.id)"
                  @change="toggleArticle(item.id, $event)"
                />
                <span>{{ item.name }} <span class="text-muted mono">({{ item.sku }})</span></span>
              </label>
            </div>
          </div>
          <div class="hint">Speichern aktualisiert nur die lokale UI-Zuordnung. Backend-Unterstützung fehlt.</div>
          <div class="row gap8">
            <button class="btnGhost small" type="button" @click="resetMappingSelection">Auswahl zurücksetzen</button>
            <button class="btnPrimary small" type="button" :disabled="!selectedIndustryId" @click="saveMapping">
              Speichern
            </button>
          </div>
        </div>
      </div>

      <div v-if="modal.open">
        <div class="modal-backdrop" @click="closeModal"></div>
        <div class="modal-panel" @click.stop>
          <div class="modal">
            <div class="modal__header">
              <div class="modal__title">{{ modal.mode === "create" ? "Branche anlegen" : "Branche bearbeiten" }}</div>
              <button class="btnGhost small" type="button" @click="closeModal">Schließen</button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <label class="field">
                  <span class="field-label">Name *</span>
                  <input class="input" v-model.trim="modal.name" placeholder="z. B. Gastronomie" />
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
import { computed, reactive, ref, watch } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalIndustry,
  generateId,
} from "../composables/useGlobalMasterdata";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { industries, items, industryArticles, upsertIndustry, setIndustryArticles } = useGlobalMasterdata();

const search = ref("");
const selectedIndustryId = ref("");
const selectedArticleIds = ref<string[]>([]);
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

const filteredIndustries = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = industries.value || [];
  if (!term) return list;
  return list.filter(
    (t) => t.name.toLowerCase().includes(term) || (t.description || "").toLowerCase().includes(term)
  );
});

watch(
  () => selectedIndustryId.value,
  (id) => {
    const map = industryArticles.value || {};
    selectedArticleIds.value = id ? [...(map[id] || [])] : [];
  }
);

function resetFilters() {
  search.value = "";
}

function selectIndustry(id: string) {
  selectedIndustryId.value = id;
}

function openCreateModal() {
  modal.open = true;
  modal.mode = "create";
  modal.id = "";
  modal.name = "";
  modal.description = "";
  modal.is_active = true;
}

function openEdit(entry: GlobalIndustry) {
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
  const payload: GlobalIndustry = {
    id: modal.id || generateId(),
    name,
    description: modal.description?.trim() || "",
    is_active: modal.is_active,
  };
  upsertIndustry(payload);
  selectedIndustryId.value = payload.id;
  toast(
    modal.mode === "edit" ? "Branche aktualisiert (UI-only, Backend fehlt)" : "Branche angelegt (UI-only, Backend fehlt)",
    "success"
  );
  busy.save = false;
  closeModal();
}

function toggleArticle(id: string, event: Event) {
  const checked = (event.target as HTMLInputElement).checked;
  if (checked) {
    selectedArticleIds.value = Array.from(new Set([...selectedArticleIds.value, id]));
  } else {
    selectedArticleIds.value = selectedArticleIds.value.filter((entry) => entry !== id);
  }
}

function resetMappingSelection() {
  selectedArticleIds.value = [];
}

function saveMapping() {
  if (!selectedIndustryId.value) {
    toast("Bitte Branche wählen", "warning");
    return;
  }
  busy.save = true;
  setIndustryArticles(selectedIndustryId.value, selectedArticleIds.value);
  toast("Zuordnung gespeichert (UI-only, Backend fehlt)", "success");
  busy.save = false;
}

function loadIndustries() {
  busy.load = true;
  toast("Backend-Unterstützung fehlt – kein Ladevorgang möglich", "warning");
  busy.load = false;
}
</script>
