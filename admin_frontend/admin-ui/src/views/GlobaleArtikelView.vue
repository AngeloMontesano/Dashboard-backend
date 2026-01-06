<template>
  <UiPage>
    <UiSection title="Globale Artikel" subtitle="Artikel-Stammdaten (ohne Tenant-Kontext)">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.load" @click="loadItems">
          {{ busy.load ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neu anlegen</button>
      </template>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Import / Export</div>
          <div class="text-muted text-small">Admin-Endpoints für globale Artikel nutzen CSV-Format wie im Tenant.</div>
        </div>
        <div class="box stack">
          <div class="row gap8 wrap">
            <button class="btnGhost small" type="button" :disabled="busy.exporting" @click="exportItems">
              {{ busy.exporting ? "exportiert..." : "Export starten" }}
            </button>
            <label class="btnGhost small file-btn">
              Datei wählen (xlsx/csv)
              <input type="file" accept=".xlsx,.xls,.csv" @change="onFileSelected" />
            </label>
            <button class="btnPrimary small" type="button" :disabled="busy.importing" @click="importItems">
              {{ busy.importing ? "importiert..." : "Import starten" }}
            </button>
          </div>
          <ul class="bullets">
            <li>CSV/XLSX Strukturen wie im Customer-Frontend (alle Felder, inkl. Kategorie/Einheit).</li>
            <li>Admin-Artikel sind schreibgeschützt für Kunden-APIs.</li>
            <li>Kunden-Artikel erhalten automatisch ein <code>z_</code>-Prefix im Customer-Backend.</li>
          </ul>
        </div>
      </div>

      <div class="filter-card two-column">
        <div class="stack">
          <label class="field-label" for="global-item-search">Suche</label>
          <input
            id="global-item-search"
            class="input"
            v-model.trim="search"
            placeholder="Name, SKU oder Barcode"
            aria-label="Globale Artikel filtern"
          />
          <div class="hint">Filtert nur den lokalen Zustand.</div>
        </div>
        <div class="stack">
          <label class="field-label" for="global-item-category">Kategorie</label>
          <select id="global-item-category" class="input" v-model="categoryFilter">
            <option value="">Alle</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <span class="text-muted text-small">Treffer: {{ filteredItems.length }}</span>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Artikel</div>
          <div class="text-muted text-small">Daten werden live aus dem Backend geladen.</div>
        </div>
        <div class="tableWrap">
          <table class="table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Artikel</th>
                <th>Kategorie</th>
                <th>Status</th>
                <th class="narrowCol"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in filteredItems"
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
                <td>{{ getCategoryName(item.category_id) || "—" }}</td>
                <td>
                  <span class="tag" :class="item.is_active ? 'ok' : 'bad'">
                    {{ item.is_active ? "aktiv" : "deaktiviert" }}
                  </span>
                </td>
                <td class="text-right">
                  <button class="btnGhost small" type="button" @click.stop="openEdit(item)">Bearbeiten</button>
                </td>
              </tr>
              <tr v-if="!filteredItems.length">
                <td colspan="5" class="mutedPad">Noch keine Artikel im UI hinterlegt.</td>
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
                    <option v-for="u in units" :key="u.code" :value="u.code">{{ u.label }}</option>
                  </select>
                </label>
                <label class="field">
                  <span class="field-label">Kategorie</span>
                  <select class="input" v-model="modal.category_id">
                    <option value="">Keine</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
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
                <label class="field checkbox">
                  <input type="checkbox" v-model="modal.is_active" />
                  <span>Aktiv</span>
                </label>
              </div>
              <div class="hint">Speichern legt den Artikel global ohne Tenant-Kontext an.</div>
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
  getCategoryName,
  useGlobalMasterdata,
  type GlobalItem,
} from "../composables/useGlobalMasterdata";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import {
  adminCreateGlobalItem,
  adminExportGlobalItems,
  adminImportGlobalItems,
  adminListGlobalCategories,
  adminListGlobalItems,
  adminListUnits,
  adminUpdateGlobalItem,
} from "../api/admin";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();
const { items, categories, units: globalUnits, upsertItem, replaceItems, replaceCategories, replaceUnits } =
  useGlobalMasterdata();

const search = ref("");
const categoryFilter = ref("");
const selectedId = ref("");
const busy = reactive({
  load: false,
  save: false,
  importing: false,
  exporting: false,
});
const defaultUnits = [
  { code: "pcs", label: "Stück", is_active: true },
  { code: "kg", label: "Kilogramm", is_active: true },
  { code: "l", label: "Liter", is_active: true },
];
const units = computed(() => (globalUnits.value.length ? globalUnits.value : defaultUnits));

const modal = reactive({
  open: false,
  mode: "create" as "create" | "edit",
  id: "",
  name: "",
  sku: "",
  barcode: "",
  description: "",
  unit: units.value[0]?.code || "",
  category_id: "",
  quantity: 0,
  min_stock: 0,
  target_stock: 0,
  is_active: true,
});
const importFile = ref<File | null>(null);

const filteredItems = computed(() => {
  const term = search.value.trim().toLowerCase();
  const list = items.value || [];
  let filtered = list;
  if (categoryFilter.value) {
    filtered = filtered.filter((i) => i.category_id === categoryFilter.value);
  }
  if (!term) return filtered;
  return filtered.filter(
    (i) =>
      i.name.toLowerCase().includes(term) ||
      i.sku.toLowerCase().includes(term) ||
      (i.barcode || "").toLowerCase().includes(term)
  );
});

function select(id: string) {
  selectedId.value = id;
}

function openCreateModal() {
  modal.open = true;
  modal.mode = "create";
  modal.id = "";
  modal.name = "";
  modal.sku = "";
  modal.barcode = "";
  modal.description = "";
  modal.unit = units.value[0]?.code || "pcs";
  modal.category_id = "";
  modal.quantity = 0;
  modal.min_stock = 0;
  modal.target_stock = 0;
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
  modal.unit = item.unit;
  modal.category_id = item.category_id || "";
  modal.quantity = item.quantity || 0;
  modal.min_stock = item.min_stock || 0;
  modal.target_stock = item.target_stock || 0;
  modal.is_active = item.is_active;
}

function closeModal() {
  modal.open = false;
}

async function loadMasterdata() {
  if (!props.adminKey) return;
  busy.load = true;
  try {
    const [cats, itemRes, unitRes] = await Promise.all([
      adminListGlobalCategories(props.adminKey, props.actor),
      adminListGlobalItems(props.adminKey, props.actor, { page_size: 200 }),
      adminListUnits(props.adminKey, props.actor),
    ]);
    replaceCategories(cats);
    replaceItems(itemRes.items || []);
    replaceUnits(unitRes);
    toast("Globale Stammdaten geladen");
  } catch (e: any) {
    toast(e?.message || "Laden fehlgeschlagen", "error");
  } finally {
    busy.load = false;
  }
}

async function save() {
  const name = modal.name.trim();
  const sku = modal.sku.trim();
  if (!name || !sku) {
    toast("Name und SKU sind Pflicht", "warning");
    return;
  }
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
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
      min_stock: Number.isFinite(modal.min_stock) ? Number(modal.min_stock) : 0,
      max_stock: Number.isFinite(modal.target_stock) ? Number(modal.target_stock) : 0,
      target_stock: Number.isFinite(modal.target_stock) ? Number(modal.target_stock) : 0,
      recommended_stock: Number.isFinite(modal.target_stock) ? Number(modal.target_stock) : 0,
      order_mode: 0,
    };
    let saved: GlobalItem;
    if (modal.mode === "edit" && modal.id) {
      saved = await adminUpdateGlobalItem(props.adminKey, props.actor, modal.id, payload);
    } else {
      saved = await adminCreateGlobalItem(props.adminKey, props.actor, payload);
    }
    upsertItem(saved);
    selectedId.value = saved.id;
    toast(modal.mode === "edit" ? "Artikel aktualisiert" : "Artikel angelegt", "success");
  } catch (e: any) {
    toast(e?.message || "Speichern fehlgeschlagen", "error");
  } finally {
    busy.save = false;
    closeModal();
  }
}

async function loadItems() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  busy.load = true;
  try {
    const res = await adminListGlobalItems(props.adminKey, props.actor, { page_size: 200 });
    replaceItems(res.items || []);
    toast(`Artikel geladen: ${res.items?.length || 0}`);
  } catch (e: any) {
    toast(e?.message || "Laden fehlgeschlagen", "error");
  } finally {
    busy.load = false;
  }
}

async function exportItems() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  busy.exporting = true;
  try {
    const res = await adminExportGlobalItems(props.adminKey, props.actor);
    const blob = new Blob([res.csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "globale_artikel.csv";
    link.click();
    URL.revokeObjectURL(url);
    toast("Export erstellt", "success");
  } catch (e: any) {
    toast(e?.message || "Export fehlgeschlagen", "error");
  } finally {
    busy.exporting = false;
  }
}

async function importItems() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen", "warning");
    return;
  }
  if (!importFile.value) {
    toast("Bitte Datei wählen (XLSX/CSV)", "warning");
    return;
  }
  busy.importing = true;
  try {
    const res = await adminImportGlobalItems(props.adminKey, props.actor, importFile.value);
    toast(`Import: ${res.imported} neu, ${res.updated} aktualisiert`, "success");
    await loadItems();
  } catch (e: any) {
    toast(e?.message || "Import fehlgeschlagen", "error");
  } finally {
    busy.importing = false;
  }
}

function onFileSelected(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  importFile.value = files && files.length ? files[0] : null;
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadMasterdata();
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.adminKey) {
    loadMasterdata();
  }
});
</script>
