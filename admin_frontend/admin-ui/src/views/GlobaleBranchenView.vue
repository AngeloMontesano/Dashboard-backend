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
          <div class="tableTitle">Zugeordnete Artikel</div>
          <div class="text-muted text-small">
            Auswahl wird direkt im Backend gespeichert. Admin-Artikel sind schreibgeschützt für Kunden.
          </div>
        </div>
        <div class="box stack">
          <label class="field">
            <span class="field-label">Branche wählen</span>
            <select class="input" v-model="selectedIndustryId" @change="loadIndustryMapping">
              <option value="">Bitte wählen</option>
              <option v-for="entry in industries" :key="entry.id" :value="entry.id">
                {{ entry.name }}
              </option>
            </select>
          </label>
          <div v-if="!items.length" class="muted text-small">
            Keine Artikel geladen. Bitte zuerst Artikel laden oder Import durchführen.
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
          <div class="row gap8">
            <button class="btnGhost small" type="button" @click="resetMappingSelection">Auswahl zurücksetzen</button>
            <button class="btnPrimary small" type="button" :disabled="!selectedIndustryId || busy.saveMapping" @click="saveMapping">
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
} from "../api/globals";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { industries, items, industryArticles, upsertIndustry, setIndustryArticles, replaceIndustries, replaceItems } =
  useGlobalMasterdata();

const search = ref("");
const selectedIndustryId = ref("");
const selectedArticleIds = ref<string[]>([]);
const busy = reactive({
  load: false,
  save: false,
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

async function loadAll() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich");
    return;
  }
  busy.load = true;
  try {
    const [industryList, itemPage] = await Promise.all([
      fetchGlobalIndustries(props.adminKey, props.actor),
      fetchGlobalItems(props.adminKey, props.actor, { page: 1, page_size: 200, active: true }),
    ]);
    replaceIndustries(industryList);
    const allItems: GlobalItem[] = [...(itemPage.items as GlobalItem[])];
    const totalPages = Math.ceil((itemPage.total || 0) / (itemPage.page_size || 200));
    for (let p = 2; p <= totalPages; p += 1) {
      const next = await fetchGlobalItems(props.adminKey, props.actor, { page: p, page_size: 200, active: true });
      allItems.push(...(next.items as GlobalItem[]));
    }
    replaceItems(allItems);
  } catch (e: any) {
    toast(`Laden fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.load = false;
  }
}

async function loadIndustryMapping() {
  if (!selectedIndustryId.value) return;
  try {
    const res = await fetchIndustryItems(props.adminKey, selectedIndustryId.value, props.actor);
    setIndustryArticles(selectedIndustryId.value, res.map((i) => i.id));
    selectedArticleIds.value = res.map((i) => i.id);
  } catch (e: any) {
    toast(`Zuordnung konnte nicht geladen werden: ${e?.message || e}`, "error");
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
      selectedArticleIds.value = [];
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

async function saveMapping() {
  if (!selectedIndustryId.value) {
    toast("Bitte Branche wählen", "warning");
    return;
  }
  busy.saveMapping = true;
  try {
    await setIndustryItems(
      props.adminKey,
      selectedIndustryId.value,
      { item_ids: selectedArticleIds.value },
      props.actor
    );
    setIndustryArticles(selectedIndustryId.value, selectedArticleIds.value);
    toast("Zuordnung gespeichert", "success");
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.saveMapping = false;
  }
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
</style>
