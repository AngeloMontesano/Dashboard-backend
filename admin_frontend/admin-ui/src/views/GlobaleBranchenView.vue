<template>
  <UiPage>
    <UiSection title="Globale Branchen" subtitle="Branchen und Artikel-Zuordnung (Admin-Key erforderlich)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadAll">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Branchen werden global verwaltet. Zuordnungen zu Artikeln werden direkt gespeichert. Semikolon-CSV/XLSX Import/Export stehen für Artikel zur Verfügung (Branchen nur via API).
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
          <div class="hint">Filtert die geladene Liste.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredIndustries.length }}</span>
          <button class="btnGhost small" type="button" :disabled="!search" @click="resetFilters">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Branchen</div>
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
                  <div class="row gap8">
                    <button class="btnGhost small" type="button" @click.stop="openEdit(entry)">Bearbeiten</button>
                    <button class="btnGhost small danger" type="button" @click.stop="remove(entry)">Löschen</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredIndustries.length">
                <td colspan="4" class="mutedPad">Noch keine Branchen vorhanden.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Branche ↔ Artikel</div>
          <div class="text-muted text-small">
            Serverseitige Suche/Pagination für verfügbare Artikel. Änderungen werden als Pending gesammelt und erst beim Speichern ersetzt.
          </div>
        </div>
        <div class="box stack">
          <div class="grid-2">
            <label class="field">
              <span class="field-label">Branche wählen</span>
              <select class="input" v-model="selectedIndustryId" @change="onIndustryChange">
                <option value="">Bitte wählen</option>
                <option v-for="entry in industries" :key="entry.id" :value="entry.id">
                  {{ entry.name }}
                </option>
              </select>
            </label>
            <div class="stack-sm info-line">
              <div class="text-muted text-small">
                Zugeordnet: {{ initialAssignedIds.length }} · Pending +{{ pendingAdditions.length }} / -{{ pendingRemovals.length }} · Finale Liste: {{ finalItemIds.length }}
              </div>
              <div v-if="!selectedIndustryId" class="muted text-small">Bitte eine Branche wählen, um Zuordnungen zu laden.</div>
              <div v-else class="muted text-small">
                Speichern ersetzt die Zuordnung (`item_ids`). CSV/XLSX-Import für Mappings fehlt im Backend.
              </div>
            </div>
          </div>

          <div class="filter-card two-column">
            <div class="stack">
              <label class="field-label" for="industry-item-search">Suche</label>
              <input
                id="industry-item-search"
                class="input"
                v-model.trim="availableQuery.search"
                placeholder="Name, SKU oder Barcode"
                aria-label="Artikel suchen"
              />
              <div class="hint">Serverseitige Suche mit Debounce (q-Parameter).</div>
            </div>
            <div class="stack">
              <div class="row gap8 wrap">
                <label class="field grow">
                  <span class="field-label">Kategorie</span>
                  <select class="input" v-model="availableQuery.categoryId">
                    <option value="">Alle</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </label>
                <label class="field">
                  <span class="field-label">Status</span>
                  <select class="input" v-model="availableQuery.active">
                    <option value="">Alle</option>
                    <option value="true">Nur aktive</option>
                    <option value="false">Inaktive</option>
                  </select>
                </label>
              </div>
              <div class="row gap8 wrap">
                <span class="text-muted text-small">Treffer: {{ availableTotal }} (Seite {{ availablePage }} / {{ availableTotalPages }})</span>
                <button class="btnGhost small" type="button" :disabled="busy.loadAvailable" @click="reloadAvailable">
                  {{ busy.loadAvailable ? "lädt..." : "Artikel neu laden" }}
                </button>
              </div>
            </div>
          </div>

          <div class="mapping-grid">
            <div class="mapping-pane">
              <div class="pane-header">
                <div class="pane-title">Verfügbare Artikel</div>
                <div class="row gap8 wrap align-center">
                  <span class="text-muted text-small">Serverseitig, Mehrfachauswahl möglich.</span>
                  <span class="text-small">Ausgewählt: {{ availableSelectionCount }}</span>
                  <button class="btnGhost tiny" type="button" :disabled="!availableItems.length" @click="selectAllAvailablePage">
                    Seite auswählen
                  </button>
                  <button class="btnGhost tiny" type="button" :disabled="!availableSelectionCount" @click="clearAvailableSelection">
                    Auswahl leeren
                  </button>
                </div>
              </div>
              <div class="pane-body" :class="{ loading: busy.loadAvailable }">
                <div v-if="busy.loadAvailable" class="muted text-small">Lädt Artikel...</div>
                <div v-else-if="!availableItems.length" class="muted text-small">Keine Artikel gefunden.</div>
                <div v-else class="item-list">
                  <label v-for="item in availableItems" :key="item.id" class="item-row">
                    <input
                      type="checkbox"
                      :value="item.id"
                      v-model="selectedAvailableIds"
                      :disabled="!selectedIndustryId || finalItemIdSet.has(item.id)"
                    />
                    <div class="item-meta">
                      <div class="item-title">{{ item.name }}</div>
                      <div class="text-muted text-small mono">{{ item.sku }} · {{ item.barcode || "—" }}</div>
                    </div>
                    <div class="row gap6">
                      <span v-if="finalItemIdSet.has(item.id)" class="tag">
                        Bereits zugeordnet
                      </span>
                      <span class="tag" :class="item.is_active ? 'ok' : 'bad'">
                        {{ item.is_active ? "aktiv" : "inaktiv" }}
                      </span>
                    </div>
                  </label>
                </div>
              </div>
              <div class="pane-footer row gap8 wrap">
                <button class="btnGhost small" type="button" :disabled="availablePage <= 1 || busy.loadAvailable" @click="prevAvailablePage">
                  ◀ Seite zurück
                </button>
                <button
                  class="btnGhost small"
                  type="button"
                  :disabled="availablePage >= availableTotalPages || busy.loadAvailable"
                  @click="nextAvailablePage"
                >
                  ▶ Seite weiter
                </button>
              </div>
            </div>

            <div class="mapping-actions">
              <button class="btnPrimary" type="button" :disabled="!canAddSelection" @click="addSelection">Hinzufügen →</button>
              <button class="btnGhost" type="button" :disabled="!canRemoveSelection" @click="removeSelection">← Entfernen</button>
            </div>

            <div class="mapping-pane">
              <div class="pane-header">
                <div class="pane-title">Zugeordnete Artikel</div>
                <div class="row gap8 wrap align-center">
                  <span class="text-muted text-small">Pending-Status wird angezeigt. Clientseitige Pagination.</span>
                  <span class="text-small">Ausgewählt: {{ assignedSelectionCount }}</span>
                  <button class="btnGhost tiny" type="button" :disabled="!paginatedAssignedRows.length" @click="selectAllAssignedPage">
                    Seite auswählen
                  </button>
                  <button class="btnGhost tiny" type="button" :disabled="!assignedSelectionCount" @click="clearAssignedSelection">
                    Auswahl leeren
                  </button>
                </div>
              </div>
              <div class="pane-body" :class="{ loading: busy.loadMapping }">
                <div v-if="busy.loadMapping" class="muted text-small">Zuordnung wird geladen...</div>
                <div v-else-if="!assignedRows.length" class="muted text-small">
                  Noch keine Zuordnung für diese Branche.
                </div>
                <div v-else class="item-list">
                  <label v-for="row in paginatedAssignedRows" :key="row.item.id" class="item-row">
                    <input type="checkbox" :value="row.item.id" v-model="selectedAssignedIds" :disabled="!selectedIndustryId" />
                    <div class="item-meta">
                      <div class="item-title">{{ row.item.name }}</div>
                      <div class="text-muted text-small mono">{{ row.item.sku }} · {{ row.item.barcode || "—" }}</div>
                    </div>
                    <span class="tag" :class="row.status === 'remove' ? 'bad' : row.status === 'add' ? 'ok' : ''">
                      {{ row.status === "add" ? "Neu (pending)" : row.status === "remove" ? "Wird entfernt" : "Gespeichert" }}
                    </span>
                  </label>
                </div>
              </div>
              <div class="pane-footer row gap8 wrap">
                <button class="btnGhost small" type="button" :disabled="assignedPage <= 1" @click="prevAssignedPage">◀</button>
                <div class="text-muted text-small">Seite {{ assignedPage }} / {{ assignedTotalPages }}</div>
                <button class="btnGhost small" type="button" :disabled="assignedPage >= assignedTotalPages" @click="nextAssignedPage">▶</button>
              </div>
            </div>
          </div>

          <div class="row gap8 wrap">
            <button class="btnGhost small" type="button" :disabled="!hasPendingChanges" @click="resetPending">Änderungen verwerfen</button>
            <button
              class="btnPrimary small"
              type="button"
              :disabled="!selectedIndustryId || busy.saveMapping || !hasPendingChanges"
              @click="saveMapping"
            >
              {{ busy.saveMapping ? "speichert..." : "Speichern" }}
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
import { computed, reactive, ref, watch, onMounted } from "vue";
import { useToast } from "../composables/useToast";
import {
  useGlobalMasterdata,
  type GlobalIndustry,
  type GlobalItem,
} from "../composables/useGlobalMasterdata";
import {
  fetchGlobalIndustries,
  createGlobalIndustry,
  updateGlobalIndustry,
  deleteGlobalIndustry,
  fetchIndustryItems,
  setIndustryItems,
  fetchGlobalItems,
  fetchGlobalCategories,
} from "../api/globals";
import { debounce } from "../utils/debounce";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const {
  industries,
  categories,
  upsertIndustry,
  setIndustryArticles,
  replaceIndustries,
  replaceCategories,
} = useGlobalMasterdata();

const search = ref("");
const selectedIndustryId = ref("");

const availableItems = ref<GlobalItem[]>([]);
const availableTotal = ref(0);
const availablePage = ref(1);
const availablePageSize = 50;
const availableQuery = reactive({
  search: "",
  categoryId: "",
  active: "true" as "" | "true" | "false",
});

const assignedItems = ref<GlobalItem[]>([]);
const initialAssignedIds = ref<string[]>([]);
const pendingAdditions = ref<string[]>([]);
const pendingRemovals = ref<string[]>([]);
const knownItems = reactive<Record<string, GlobalItem>>({});

const selectedAvailableIds = ref<string[]>([]);
const selectedAssignedIds = ref<string[]>([]);
const assignedPage = ref(1);
const assignedPageSize = 20;

const busy = reactive({
  load: false,
  save: false,
  loadAvailable: false,
  loadMapping: false,
  saveMapping: false,
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

const availableTotalPages = computed(() =>
  availableTotal.value ? Math.max(1, Math.ceil(availableTotal.value / availablePageSize)) : 1
);
const assignedTotalPages = computed(() =>
  assignedRows.value.length ? Math.max(1, Math.ceil(assignedRows.value.length / assignedPageSize)) : 1
);

const hasPendingChanges = computed(
  () => pendingAdditions.value.length > 0 || pendingRemovals.value.length > 0
);

const finalItemIds = computed(() => {
  const base = new Set(initialAssignedIds.value);
  pendingAdditions.value.forEach((id) => base.add(id));
  pendingRemovals.value.forEach((id) => base.delete(id));
  return Array.from(base);
});

const finalItemIdSet = computed(() => new Set(finalItemIds.value));

const availableSelectionCount = computed(() => selectedAvailableIds.value.length);
const assignedSelectionCount = computed(() => selectedAssignedIds.value.length);

const assignedRows = computed(() => {
  const removalSet = new Set(pendingRemovals.value);
  const additionSet = new Set(pendingAdditions.value);
  const rows = assignedItems.value.map((item) => ({
    item,
    status: removalSet.has(item.id) ? ("remove" as const) : ("kept" as const),
  }));

  additionSet.forEach((id) => {
    const existing = knownItems[id];
    if (existing) {
      rows.push({ item: existing, status: "add" as const });
    }
  });

  return rows;
});

const paginatedAssignedRows = computed(() => {
  const start = (assignedPage.value - 1) * assignedPageSize;
  return assignedRows.value.slice(start, start + assignedPageSize);
});

watch(
  () => selectedIndustryId.value,
  () => {
    selectedAvailableIds.value = [];
    selectedAssignedIds.value = [];
    if (!selectedIndustryId.value) {
      assignedItems.value = [];
      initialAssignedIds.value = [];
      pendingAdditions.value = [];
      pendingRemovals.value = [];
      return;
    }
  }
);

watch(
  () => availableQuery.search,
  debounce(() => {
    availablePage.value = 1;
    loadAvailableItems();
  }, 350)
);

watch(
  () => [availableQuery.categoryId, availableQuery.active],
  () => {
    availablePage.value = 1;
    loadAvailableItems();
  }
);

watch(
  () => availablePage.value,
  () => {
    loadAvailableItems();
  }
);

watch(
  () => assignedTotalPages.value,
  (pages) => {
    if (assignedPage.value > pages) {
      assignedPage.value = pages;
    }
  }
);

function resetFilters() {
  search.value = "";
}

function selectIndustry(id: string) {
  selectedIndustryId.value = id;
}

function onIndustryChange() {
  assignedPage.value = 1;
  loadIndustryMapping();
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

function cacheItems(list: GlobalItem[]) {
  list.forEach((item) => {
    knownItems[item.id] = item;
  });
}

async function loadAvailableItems() {
  if (!props.adminKey) return;
  busy.loadAvailable = true;
  try {
    const params: Record<string, any> = {
      q: availableQuery.search || undefined,
      category_id: availableQuery.categoryId || undefined,
      active:
        availableQuery.active === "" ? undefined : availableQuery.active === "true" ? true : false,
      page: availablePage.value,
      page_size: availablePageSize,
    };
    const res = await fetchGlobalItems(props.adminKey, props.actor, params);
    availableItems.value = res.items as GlobalItem[];
    availableTotal.value = res.total;
    cacheItems(res.items as GlobalItem[]);
    const availableIds = new Set(availableItems.value.map((i) => i.id));
    selectedAvailableIds.value = selectedAvailableIds.value.filter(
      (id) => availableIds.has(id) && !finalItemIdSet.value.has(id)
    );
  } catch (e: any) {
    toast(`Artikel konnten nicht geladen werden: ${e?.message || e}`, "error");
  } finally {
    busy.loadAvailable = false;
  }
}

async function loadAll() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich");
    return;
  }
  busy.load = true;
  try {
    const [industryList, catList] = await Promise.all([
      fetchGlobalIndustries(props.adminKey, props.actor),
      fetchGlobalCategories(props.adminKey, props.actor),
    ]);
    replaceIndustries(industryList);
    replaceCategories(catList);
    await loadAvailableItems();
  } catch (e: any) {
    toast(`Laden fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.load = false;
  }
}

async function loadIndustryMapping() {
  if (!selectedIndustryId.value) return;
  busy.loadMapping = true;
  selectedAvailableIds.value = [];
  selectedAssignedIds.value = [];
  try {
    const res = await fetchIndustryItems(props.adminKey, selectedIndustryId.value, props.actor);
    assignedItems.value = res as GlobalItem[];
    initialAssignedIds.value = res.map((i) => i.id);
    pendingAdditions.value = [];
    pendingRemovals.value = [];
    assignedPage.value = 1;
    cacheItems(res as GlobalItem[]);
    setIndustryArticles(selectedIndustryId.value, res.map((i) => i.id));
  } catch (e: any) {
    toast(`Zuordnung konnte nicht geladen werden: ${e?.message || e}`, "error");
  } finally {
    busy.loadMapping = false;
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
    let saved: GlobalIndustry;
    if (modal.mode === "edit" && modal.id) {
      saved = await updateGlobalIndustry(
        props.adminKey,
        modal.id,
        { name, description: modal.description?.trim() || "", is_active: modal.is_active },
        props.actor
      );
    } else {
      saved = await createGlobalIndustry(
        props.adminKey,
        { name, description: modal.description?.trim() || "", is_active: modal.is_active },
        props.actor
      );
    }
    upsertIndustry(saved);
    selectedIndustryId.value = saved.id;
    toast(modal.mode === "edit" ? "Branche aktualisiert" : "Branche angelegt", "success");
    closeModal();
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.save = false;
  }
}

async function remove(entry: GlobalIndustry) {
  if (!window.confirm(`Branche ${entry.name} löschen?`)) return;
  try {
    await deleteGlobalIndustry(props.adminKey, entry.id, props.actor);
    replaceIndustries(industries.value.filter((i) => i.id !== entry.id));
    if (selectedIndustryId.value === entry.id) {
      selectedIndustryId.value = "";
      initialAssignedIds.value = [];
      pendingAdditions.value = [];
      pendingRemovals.value = [];
      assignedItems.value = [];
    }
    toast("Branche gelöscht", "success");
  } catch (e: any) {
    toast(`Löschen fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "error");
  }
}

async function removeFromModal() {
  const current = industries.value.find((i) => i.id === modal.id);
  if (!current) return;
  await remove(current);
  closeModal();
}

function addSelection() {
  if (!selectedIndustryId.value || !selectedAvailableIds.value.length) return;
  const pendingAddSet = new Set(pendingAdditions.value);
  const pendingRemoveSet = new Set(pendingRemovals.value);
  const initialSet = new Set(initialAssignedIds.value);

  selectedAvailableIds.value.forEach((id) => {
    pendingRemoveSet.delete(id);
    if (!initialSet.has(id)) {
      pendingAddSet.add(id);
    }
  });

  pendingAdditions.value = Array.from(pendingAddSet);
  pendingRemovals.value = Array.from(pendingRemoveSet);
  selectedAvailableIds.value = [];
}

function removeSelection() {
  if (!selectedIndustryId.value || !selectedAssignedIds.value.length) return;
  const pendingAddSet = new Set(pendingAdditions.value);
  const pendingRemoveSet = new Set(pendingRemovals.value);
  const initialSet = new Set(initialAssignedIds.value);

  selectedAssignedIds.value.forEach((id) => {
    if (pendingAddSet.has(id)) {
      pendingAddSet.delete(id);
      return;
    }
    if (initialSet.has(id)) {
      pendingRemoveSet.add(id);
    }
  });

  pendingAdditions.value = Array.from(pendingAddSet);
  pendingRemovals.value = Array.from(pendingRemoveSet);
  selectedAssignedIds.value = [];
}

function resetPending() {
  pendingAdditions.value = [];
  pendingRemovals.value = [];
  selectedAvailableIds.value = [];
  selectedAssignedIds.value = [];
}

function prevAvailablePage() {
  if (availablePage.value > 1) availablePage.value -= 1;
}

function nextAvailablePage() {
  if (availablePage.value < availableTotalPages.value) availablePage.value += 1;
}

function prevAssignedPage() {
  if (assignedPage.value > 1) assignedPage.value -= 1;
}

function nextAssignedPage() {
  if (assignedPage.value < assignedTotalPages.value) assignedPage.value += 1;
}

async function saveMapping() {
  if (!selectedIndustryId.value) {
    toast("Bitte Branche wählen", "warning");
    return;
  }
  busy.saveMapping = true;
  try {
    const payload = { item_ids: finalItemIds.value };
    await setIndustryItems(props.adminKey, selectedIndustryId.value, payload, props.actor);
    setIndustryArticles(selectedIndustryId.value, payload.item_ids);
    initialAssignedIds.value = [...payload.item_ids];
    pendingAdditions.value = [];
    pendingRemovals.value = [];
    assignedItems.value = assignedRows.value
      .filter((row) => row.status !== "remove")
      .map((row) => row.item);
    selectedAssignedIds.value = [];
    toast("Zuordnung gespeichert", "success");
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.saveMapping = false;
  }
}

const canAddSelection = computed(
  () => !!selectedIndustryId.value && selectedAvailableIds.value.length > 0
);
const canRemoveSelection = computed(
  () => !!selectedIndustryId.value && selectedAssignedIds.value.length > 0
);

function reloadAvailable() {
  availablePage.value = 1;
  loadAvailableItems();
}

function selectAllAvailablePage() {
  if (!availableItems.value.length) return;
  const selectable = availableItems.value
    .filter((item) => !finalItemIdSet.value.has(item.id))
    .map((item) => item.id);
  selectedAvailableIds.value = selectable;
}

function clearAvailableSelection() {
  selectedAvailableIds.value = [];
}

function selectAllAssignedPage() {
  if (!paginatedAssignedRows.value.length) return;
  selectedAssignedIds.value = paginatedAssignedRows.value.map((row) => row.item.id);
}

function clearAssignedSelection() {
  selectedAssignedIds.value = [];
}

onMounted(() => {
  if (props.adminKey) {
    loadAll();
  }
});
</script>

<style scoped>
.modal__footer--with-delete {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 12px;
}

.modal__footer--with-delete .btnGhost.danger {
  margin-right: auto;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 12px;
  align-items: end;
}

.info-line {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
}

.mapping-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
}

.mapping-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
  align-items: center;
}

.mapping-pane {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-1);
  display: flex;
  flex-direction: column;
  min-height: 320px;
}

.pane-header {
  padding: 12px;
  border-bottom: 1px solid var(--border);
}

.pane-title {
  font-weight: 700;
}

.pane-body {
  padding: 8px 12px;
  flex: 1;
  overflow: auto;
}

.pane-footer {
  padding: 8px 12px 12px;
  border-top: 1px solid var(--border);
}

.item-list {
  display: grid;
  gap: 8px;
}

.item-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-1);
}

.item-meta {
  min-width: 0;
}

.item-title {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pane-body.loading {
  opacity: 0.7;
}

@media (max-width: 960px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }

  .mapping-grid {
    grid-template-columns: 1fr;
  }

  .mapping-actions {
    flex-direction: row;
  }
}
</style>
