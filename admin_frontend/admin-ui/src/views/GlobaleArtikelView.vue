<template>
  <UiPage>
    <UiSection title="Globale Artikel" subtitle="Artikel-Stammdaten ohne Tenant-Kontext (Admin-Key erforderlich)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadAll">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Admin-Artikel sind im Customer-Frontend schreibgeschützt (Name/SKU/Barcode/Kategorie/Einheit). Import/Export unterstützt Semikolon-CSV und XLSX.
          </p>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Import / Export</div>
          <div class="text-muted text-small">CSV-Trenner: Semikolon. Kategorien/Einheiten/Typen müssen existieren.</div>
        </div>
        <div class="box stack">
          <div class="row gap8 wrap">
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportItems('csv')">
              {{ busy.export ? "exportiert..." : "Export CSV" }}
            </button>
            <button class="btnGhost small" type="button" :disabled="busy.export" @click="exportItems('xlsx')">
              {{ busy.export ? "exportiert..." : "Export XLSX" }}
            </button>
            <label class="btnGhost small file-btn">
              Datei wählen (csv/xlsx)
              <input type="file" accept=".xlsx,.xls,.csv" @change="onFileSelected" />
            </label>
            <button class="btnPrimary small" type="button" :disabled="busy.import || !importFile" @click="importItems">
              {{ busy.import ? "importiert..." : "Import starten" }}
            </button>
          </div>
          <ul class="bullets">
            <li>Pflichtfelder: <code>sku</code>, <code>barcode</code>, <code>name</code>. Kategorienamen müssen vorhanden sein.</li>
            <li>Optional: <code>type</code> (Typname, falls gepflegt).</li>
            <li>CSV Header: {{ csvColumns.join(";") }}</li>
          </ul>
        </div>
      </div>

      <div class="filter-card three-column">
        <div class="stack">
          <label class="field-label" for="global-item-search">Suche</label>
          <input
            id="global-item-search"
            class="input"
            v-model.trim="search"
            placeholder="Name, SKU oder Barcode"
            aria-label="Globale Artikel filtern"
            @keyup.enter="loadItems"
          />
          <div class="hint">Filter wird serverseitig angewendet.</div>
        </div>
        <div class="stack">
          <label class="field-label" for="global-item-category">Kategorie</label>
          <select id="global-item-category" class="input" v-model="categoryFilter" @change="loadItems">
            <option value="">Alle</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <span class="text-muted text-small">Treffer: {{ items.length }} / {{ totalItems }}</span>
        </div>
        <div class="stack">
          <label class="field-label" for="global-item-type">Typ</label>
          <select id="global-item-type" class="input" v-model="typeFilter" @change="loadItems">
            <option value="">Alle</option>
            <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Artikel</div>
          <div class="text-muted text-small">Globale Liste aus dem Backend.</div>
        </div>
        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Artikel</th>
                <th>Kategorie</th>
                <th>Einheit</th>
                <th>Typ</th>
                <th>Status</th>
                <th class="narrowCol"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in items"
                :key="item.id"
                :class="{ rowActive: selectedId === item.id }"
                @click="select(item.id)"
              >
                <td class="mono">{{ item.sku }}</td>
                <td>
                  <div class="stack-sm">
                    <div>{{ item.name }}</div>
                    <div class="text-muted text-small">{{ item.barcode }}</div>
                  </div>
                </td>
                <td>{{ item.category_name || getCategoryName(item.category_id) || "—" }}</td>
                <td class="mono">{{ item.unit }}</td>
                <td>{{ item.type_id ? getTypeName(item.type_id) : "—" }}</td>
                <td>
                  <span class="tag" :class="item.is_active ? 'ok' : 'bad'">
                    {{ item.is_active ? "aktiv" : "deaktiviert" }}
                  </span>
                </td>
                <td class="text-right">
                  <div class="row gap8">
                    <button class="btnGhost small" type="button" @click.stop="openEdit(item)">Bearbeiten</button>
                    <button class="btnGhost small danger" type="button" @click.stop="remove(item)">Löschen</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!items.length">
                <td colspan="7" class="mutedPad">Keine Artikel gefunden.</td>
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
              <div class="modal__title">{{ modal.mode === "create" ? "Artikel anlegen" : "Artikel bearbeiten" }}</div>
              <button class="btnGhost small" type="button" @click="closeModal">Schließen</button>
            </div>
            <div class="modal__body">
              <div class="form-grid">
                <label class="field span-2">
                  <span class="field-label">Name *</span>
                  <input class="input" v-model.trim="modal.name" placeholder="z. B. Mineralwasser 1L" />
                </label>
                <label class="field">
                  <span class="field-label">SKU *</span>
                  <input class="input" v-model.trim="modal.sku" placeholder="ART-1001" />
                </label>
                <label class="field">
                  <span class="field-label">Barcode</span>
                  <input class="input" v-model.trim="modal.barcode" placeholder="Optional" />
                </label>
                <label class="field">
                  <span class="field-label">Einheit *</span>
                  <select class="input" v-model="modal.unit">
                    <option v-for="u in unitOptions" :key="u.code" :value="u.code">{{ u.label }}</option>
                  </select>
                </label>
                <label class="field">
                  <span class="field-label">Kategorie</span>
                  <select class="input" v-model="modal.category_id">
                    <option value="">Keine</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </label>
                <label class="field">
                  <span class="field-label">Typ</span>
                  <select class="input" v-model="modal.type_id">
                    <option value="">Kein Typ</option>
                    <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                </label>
                <label class="field span-2">
                  <span class="field-label">Beschreibung</span>
                  <textarea class="input" rows="2" v-model="modal.description" placeholder="Optional"></textarea>
                </label>
                <label class="field">
                  <span class="field-label">Menge</span>
                  <input class="input" type="number" min="0" v-model.number="modal.quantity" />
                </label>
                <label class="field">
                  <span class="field-label">Mindestbestand</span>
                  <input class="input" type="number" min="0" v-model.number="modal.min_stock" />
                </label>
                <label class="field">
                  <span class="field-label">Zielbestand</span>
                  <input class="input" type="number" min="0" v-model.number="modal.target_stock" />
                </label>
                <label class="field">
                  <span class="field-label">Maximalbestand</span>
                  <input class="input" type="number" min="0" v-model.number="modal.max_stock" />
                </label>
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
                </label>
              </div>
              <div class="hint">Admin-Artikel sind im Customer-Frontend read-only.</div>
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
  getCategoryName,
  getTypeName,
  useGlobalMasterdata,
  type GlobalItem,
  type GlobalCategory,
  type GlobalType,
  type GlobalUnit,
} from "../composables/useGlobalMasterdata";
import {
  fetchGlobalItems,
  createGlobalItem,
  updateGlobalItem,
  deleteGlobalItem,
  importGlobalItems,
  exportGlobalItems,
  fetchGlobalCategories,
  fetchGlobalUnits,
  fetchGlobalTypes,
} from "../api/globals";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { items, categories, types, units: globalUnits, replaceItems, replaceCategories, replaceTypes, replaceUnits, upsertItem } =
  useGlobalMasterdata();

const search = ref("");
const categoryFilter = ref("");
const typeFilter = ref("");
const selectedId = ref("");
const totalItems = ref(0);
const page = ref(1);
const pageSize = 50;
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
  sku: "",
  barcode: "",
  description: "",
  unit: "pcs",
  category_id: "",
  type_id: "",
  quantity: 0,
  min_stock: 0,
  target_stock: 0,
  max_stock: 0,
  is_active: true,
});

const csvColumns = [
  "sku",
  "barcode",
  "name",
  "description",
  "qty",
  "unit",
  "is_active",
  "category",
  "min_stock",
  "max_stock",
  "target_stock",
  "recommended_stock",
  "order_mode",
  "type",
];

const unitOptions = computed<GlobalUnit[]>(() => {
  if (globalUnits.value.length) return globalUnits.value;
  return [
    { code: "pcs", label: "Stück", is_active: true },
    { code: "kg", label: "Kilogramm", is_active: true },
    { code: "l", label: "Liter", is_active: true },
  ];
});

async function loadCategoriesUnits() {
  if (!props.adminKey) return;
  try {
    const [cats, units, globalTypes] = await Promise.all([
      fetchGlobalCategories(props.adminKey, props.actor),
      fetchGlobalUnits(props.adminKey, props.actor),
      fetchGlobalTypes(props.adminKey, props.actor),
    ]);
    replaceCategories(cats);
    replaceUnits(units);
    replaceTypes(globalTypes);
  } catch (e: any) {
    toast(`Kategorien/Einheiten/Typen konnten nicht geladen werden: ${e?.message || e}`, "error");
  }
}

async function loadItems() {
  if (!props.adminKey) {
    toast("Admin Key erforderlich");
    return;
  }
  busy.load = true;
  try {
    const params: Record<string, any> = {
      q: search.value || undefined,
      category_id: categoryFilter.value || undefined,
      type_id: typeFilter.value || undefined,
      page: page.value,
      page_size: pageSize,
    };
    const res = await fetchGlobalItems(props.adminKey, props.actor, params);
    replaceItems(res.items);
    totalItems.value = res.total;
  } catch (e: any) {
    toast(`Laden fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.load = false;
  }
}

async function loadAll() {
  await Promise.all([loadCategoriesUnits(), loadItems()]);
}

function openCreateModal() {
  modal.open = true;
  modal.mode = "create";
  modal.id = "";
  modal.name = "";
  modal.sku = "";
  modal.barcode = "";
  modal.description = "";
  modal.unit = unitOptions.value[0]?.code || "pcs";
  modal.category_id = "";
  modal.type_id = "";
  modal.quantity = 0;
  modal.min_stock = 0;
  modal.target_stock = 0;
  modal.max_stock = 0;
  modal.is_active = true;
}

function openEdit(item: GlobalItem) {
  modal.open = true;
  modal.mode = "edit";
  modal.id = item.id;
  modal.name = item.name;
  modal.sku = item.sku;
  modal.barcode = item.barcode;
  modal.description = item.description || "";
  modal.unit = item.unit || "pcs";
  modal.category_id = item.category_id || "";
  modal.type_id = item.type_id || "";
  modal.quantity = item.quantity || 0;
  modal.min_stock = item.min_stock || 0;
  modal.target_stock = item.target_stock || 0;
  modal.max_stock = item.max_stock || 0;
  modal.is_active = item.is_active;
}

function closeModal() {
  modal.open = false;
}

function select(id: string) {
  selectedId.value = id;
}

async function save() {
  const name = modal.name.trim();
  const sku = modal.sku.trim();
  if (!name || !sku) {
    toast("Name und SKU sind Pflicht", "warning");
    return;
  }
  busy.save = true;
  try {
    const payload = {
      name,
      sku,
      barcode: modal.barcode?.trim() || "",
      description: modal.description?.trim() || "",
      quantity: Number.isFinite(modal.quantity) ? Number(modal.quantity) : 0,
      unit: modal.unit || "pcs",
      is_active: modal.is_active,
      category_id: modal.category_id || null,
      type_id: modal.type_id || null,
      min_stock: Number.isFinite(modal.min_stock) ? Number(modal.min_stock) : 0,
      max_stock: Number.isFinite(modal.max_stock) ? Number(modal.max_stock) : 0,
      target_stock: Number.isFinite(modal.target_stock) ? Number(modal.target_stock) : 0,
      recommended_stock: Number.isFinite(modal.target_stock) ? Number(modal.target_stock) : 0,
      order_mode: 0,
    };

    let saved: GlobalItem;
    if (modal.mode === "edit" && modal.id) {
      saved = await updateGlobalItem(props.adminKey, modal.id, payload, props.actor);
    } else {
      saved = await createGlobalItem(props.adminKey, payload, props.actor);
    }
    upsertItem(saved);
    selectedId.value = saved.id;
    toast(modal.mode === "edit" ? "Artikel aktualisiert" : "Artikel angelegt", "success");
    closeModal();
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "error");
  } finally {
    busy.save = false;
  }
}

async function remove(item: GlobalItem) {
  if (!window.confirm(`Artikel ${item.name} löschen?`)) return;
  try {
    await deleteGlobalItem(props.adminKey, item.id, props.actor);
    replaceItems(items.value.filter((i) => i.id !== item.id));
    toast("Artikel gelöscht", "success");
  } catch (e: any) {
    toast(`Löschen fehlgeschlagen: ${e?.response?.data?.detail?.error?.message || e?.message || e}`, "error");
  }
}

async function removeFromModal() {
  const current = items.value.find((i) => i.id === modal.id);
  if (!current) return;
  await remove(current);
  closeModal();
}

function onFileSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  importFile.value = files && files.length ? files[0] : null;
}

async function importItems() {
  if (!importFile.value) {
    toast("Bitte Datei wählen", "warning");
    return;
  }
  busy.import = true;
  try {
    const res = await importGlobalItems(props.adminKey, importFile.value, props.actor);
    if (res.errors?.length) {
      console.warn("Import-Fehler (erste 5):", res.errors.slice(0, 5));
      const firstError = res.errors[0];
      toast(
        `Importiert: ${res.imported}, aktualisiert: ${res.updated}, Fehler z.B. Zeile ${firstError.row}: ${firstError.error}`,
        "warning"
      );
    } else {
      toast(`Importiert: ${res.imported}, aktualisiert: ${res.updated}`, "success");
    }
    await loadItems();
  } catch (e: any) {
    toast(`Import fehlgeschlagen: ${e?.message || e}`, "error");
  } finally {
    busy.import = false;
  }
}

async function exportItems(format: "csv" | "xlsx") {
  busy.export = true;
  try {
    const blob = await exportGlobalItems(props.adminKey, format, props.actor);
    const filename = `globale_artikel.${format === "csv" ? "csv" : "xlsx"}`;
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
    loadAll();
  }
});
</script>
