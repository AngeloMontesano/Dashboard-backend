<template>
  <section class="card minimalHeader">
    <header class="cardHeader tight">
      <div>
        <div class="cardTitle">Kunden</div>
        <div class="cardHint">Kunden suchen und auswählen</div>
      </div>
      <div class="cardHeaderActions">
        <button class="btnGhost" @click="openCreateModal">Neuen Kunden anlegen</button>
        <button class="btnPrimary" :disabled="busy.list" @click="loadTenants">
          <span v-if="busy.list" class="dotSpinner" aria-hidden="true"></span>
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
      </div>
    </header>

    <!-- Toolbar mit KPIs + Export -->
    <div class="toolbar">
      <div class="chips">
        <div class="chip">
          <div class="chipLabel">Kunden gesamt</div>
          <div class="chipValue">{{ totalTenants }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">aktiv</div>
          <div class="chipValue success">{{ activeTenants }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">deaktiviert</div>
          <div class="chipValue danger">{{ inactiveTenants }}</div>
        </div>
      </div>
      <div class="toolbarActions">
        <button class="btnGhost" :disabled="!filteredTenants.length" @click="exportCsv">Kunden exportieren CSV</button>
        <button class="btnGhost" :disabled="busy.list" @click="loadTenants">Neu laden</button>
      </div>
    </div>

    <!-- Suche -->
    <div class="searchCard">
      <label class="fieldLabel" for="kunden-search">Suche</label>
      <input
        id="kunden-search"
        class="input"
        v-model.trim="q"
        placeholder="Name oder URL-Kürzel eingeben"
        aria-label="Kunden suchen"
      />
      <div class="hint">Tippen zum Filtern. Groß und Kleinschreibung egal. Prefix-Treffer zuerst.</div>
      <div class="filterRow">
        <select class="input" v-model="statusFilter" aria-label="Status filtern">
          <option value="all">Alle</option>
          <option value="active">Aktiv</option>
          <option value="disabled">Deaktiviert</option>
        </select>
        <span class="muted smallText">Treffer: {{ filteredTenants.length }}</span>
      </div>
    </div>

    <!-- Tabelle -->
    <div class="tableCard">
      <div class="tableHeader">
        <div class="tableTitle">Kundenliste</div>
        <div class="muted smallText">Zeile anklicken, um auszuwählen.</div>
      </div>
      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th></th>
              <th>Slug</th>
              <th>Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="t in filteredTenants"
              :key="t.id"
              :class="{ rowActive: selectedTenant?.id === t.id }"
              @click="selectTenant(t)"
            >
              <td class="selectDot">
                <span class="dot" :class="selectedTenant?.id === t.id ? 'dotActive' : ''"></span>
              </td>
              <td class="mono">{{ t.slug }}</td>
              <td>{{ t.name }}</td>
              <td>
                <span class="tag" :class="t.is_active ? 'ok' : 'bad'">
                  {{ t.is_active ? "aktiv" : "deaktiviert" }}
                </span>
              </td>
            </tr>
            <tr v-if="!busy.list && filteredTenants.length === 0">
              <td colspan="4" class="mutedPad">Keine Kunden gefunden.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>
      <div v-if="!busy.list && filteredTenants.length === 0" class="row gap8 wrap">
        <button class="btnPrimary small" @click="openCreateModal">Ersten Kunden anlegen</button>
        <button class="btnGhost small" @click="resetFilters">Filter zurücksetzen</button>
      </div>
    </div>

    <!-- Details -->
    <div v-if="selectedTenant" class="detailCard">
      <div class="detailHeader">
        <div>
          <div class="detailTitle">{{ selectedTenant.name }}</div>
          <div class="detailSub mono">{{ selectedTenant.slug }} · {{ selectedTenant.id }}</div>
        </div>
        <div class="detailStatus">
          <span class="tag" :class="selectedTenant.is_active ? 'ok' : 'bad'">
            {{ selectedTenant.is_active ? "aktiv" : "deaktiviert" }}
          </span>
        </div>
      </div>

      <div class="kvGrid">
        <div class="kv">
          <div class="k">Name</div>
          <div class="v">{{ selectedTenant.name }}</div>
        </div>
        <div class="kv">
          <div class="k">URL-Kürzel</div>
          <div class="v mono">{{ selectedTenant.slug }}</div>
        </div>
        <div class="kv">
          <div class="k">Tenant ID</div>
          <div class="v mono">{{ selectedTenant.id }}</div>
        </div>
        <div class="kv">
          <div class="k">Tenant Host</div>
          <div class="v mono">{{ `${selectedTenant.slug}.${baseDomain}` }}</div>
        </div>
      </div>

      <div class="row gap8 wrap" style="margin-top: 12px;">
        <button
          class="btnGhost small"
          :disabled="busy.toggleId === selectedTenant.id"
          @click="toggleTenant(selectedTenant)"
        >
          {{ busy.toggleId === selectedTenant.id ? "..." : selectedTenant.is_active ? "Deaktivieren" : "Aktivieren" }}
        </button>
        <button
          class="btnGhost small danger"
          :disabled="busy.deleteId === selectedTenant.id"
          @click="deleteTenant(selectedTenant)"
        >
          {{ busy.deleteId === selectedTenant.id ? "löscht..." : "Kunde löschen" }}
        </button>
        <button class="btnPrimary small" @click="openMemberships(selectedTenant.id)">Tenant User verwalten</button>
      </div>
    </div>

    <!-- Create Modal -->
    <TenantCreateModal
      :open="modal.open"
      :busy="busy.create"
      :baseDomain="baseDomain"
      v-model:name="modal.name"
      v-model:slug="modal.slug"
      @close="closeCreateModal"
      @create="createTenant"
    />
  </section>
</template>

<script setup lang="ts">
/*
  Kunden-Ansicht
  - Live-Suche (Prefix-first), case insensitive
  - Tabelle nur zur Auswahl
  - Detailbereich mit Aktionen
  - CSV-Export aus gefilterter Liste
*/
import { computed, reactive, ref, watch } from "vue";
import type { TenantOut } from "../types";
import { adminListTenants, adminCreateTenant, adminUpdateTenant, adminDeleteTenant } from "../api/admin";
import { useToast } from "../composables/useToast";

import TenantCreateModal from "../components/tenants/TenantCreateModal.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
  apiOk: boolean;
  dbOk: boolean;
  selectedTenantId?: string;
}>();

const emit = defineEmits<{
  (e: "openMemberships", tenantId: string): void;
  (e: "tenantSelected", payload: { id: string; name: string; slug: string } | null): void;
}>();

const { toast } = useToast();

/* State */
const tenants = ref<TenantOut[]>([]);
const selectedTenant = ref<TenantOut | null>(null);

const q = ref("");
const statusFilter = ref<"all" | "active" | "disabled">("all");

const totalTenants = computed(() => tenants.value.length);
const activeTenants = computed(() => tenants.value.filter((t) => t.is_active).length);
const inactiveTenants = computed(() => tenants.value.filter((t) => !t.is_active).length);

const busy = reactive({
  list: false,
  create: false,
  toggleId: "" as string,
  deleteId: "" as string,
  error: "",
});

/* Modal State */
const modal = reactive({
  open: false,
  name: "",
  slug: "",
});

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";

/* Filter */
const filteredTenants = computed(() => {
  let list = tenants.value.slice();
  if (statusFilter.value === "active") list = list.filter((t) => t.is_active);
  if (statusFilter.value === "disabled") list = list.filter((t) => !t.is_active);

  const term = q.value.trim().toLowerCase();
  if (!term) return list;

  const prefix = list.filter(
    (t) => t.slug.toLowerCase().startsWith(term) || t.name.toLowerCase().startsWith(term)
  );
  if (prefix.length) return prefix;
  return list.filter((t) => t.slug.toLowerCase().includes(term) || t.name.toLowerCase().includes(term));
});

/* API: Load Tenants */
async function loadTenants() {
  if (!ensureAdminKey()) return;
  busy.list = true;
  busy.error = "";
  try {
    const res = await adminListTenants(props.adminKey, props.actor, {
      limit: 500,
      offset: 0,
    });
    tenants.value = res;
    // Default: keine Auswahl
    if (selectedTenant.value) {
      selectedTenant.value = res.find((t) => t.id === selectedTenant.value.id) ?? null;
    }
    emitSelectedTenant();
    toast(`Kunden geladen: ${res.length}`);
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler beim Laden: ${busy.error}`);
  } finally {
    busy.list = false;
  }
}

/* API: Create Tenant */
async function createTenant() {
  if (!ensureAdminKey()) return;
  const name = modal.name.trim();
  const slug = modal.slug.trim().toLowerCase();

  if (!name || !slug) {
    toast("Name und URL-Kürzel sind Pflicht");
    return;
  }

  if (!/^[a-z0-9-]+$/.test(slug)) {
    toast("URL-Kürzel: nur Kleinbuchstaben, Zahlen und Bindestriche erlaubt");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateTenant(props.adminKey, props.actor, { name, slug });
    tenants.value = [created, ...tenants.value];
    selectedTenant.value = created;
    closeCreateModal();
    toast("Kunde angelegt");
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

/* API: Toggle Tenant Active */
async function toggleTenant(t: TenantOut) {
  if (!ensureAdminKey()) return;
  if (!t) return;

  busy.toggleId = t.id;
  try {
    const updated = await adminUpdateTenant(props.adminKey, props.actor, t.id, {
      is_active: !t.is_active,
    });
    tenants.value = tenants.value.map((x) => (x.id === updated.id ? updated : x));
    if (selectedTenant.value?.id === updated.id) selectedTenant.value = updated;
    toast(updated.is_active ? "Kunde aktiviert" : "Kunde deaktiviert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.toggleId = "";
  }
}

async function deleteTenant(t: TenantOut) {
  if (!ensureAdminKey()) return;
  if (!t) return;
  const confirmDelete = window.confirm(`Kunde ${t.slug} wirklich löschen? Diese Aktion ist irreversibel.`);
  if (!confirmDelete) return;

  busy.deleteId = t.id;
  try {
    await adminDeleteTenant(props.adminKey, props.actor, t.id);
    tenants.value = tenants.value.filter((x) => x.id !== t.id);
    if (selectedTenant.value?.id === t.id) selectedTenant.value = null;
    toast("Kunde gelöscht");
  } catch (e: any) {
    toast(`Fehler beim Löschen: ${stringifyError(e)}`);
  } finally {
    busy.deleteId = "";
  }
}

/* UI actions */
function selectTenant(t: TenantOut) {
  selectedTenant.value = t;
  emitSelectedTenant();
}

function openCreateModal() {
  modal.open = true;
  modal.name = "";
  modal.slug = "";
}

function closeCreateModal() {
  modal.open = false;
}

function openMemberships(tenantId: string) {
  emit("openMemberships", tenantId);
}

function resetFilters() {
  q.value = "";
  statusFilter.value = "all";
}

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

function emitSelectedTenant() {
  if (selectedTenant.value) {
    emit("tenantSelected", {
      id: selectedTenant.value.id,
      name: selectedTenant.value.name,
      slug: selectedTenant.value.slug,
    });
  } else {
    emit("tenantSelected", null);
  }
}

function stringifyError(e: any): string {
  if (!e) return "unknown";
  if (typeof e === "string") return e;
  if (e?.response?.data?.detail) return JSON.stringify(e.response.data.detail);
  if (e?.message) return e.message;
  try {
    return JSON.stringify(e);
  } catch {
    return String(e);
  }
}

function exportCsv() {
  if (!filteredTenants.value.length) {
    toast("Keine Kunden zum Export");
    return;
  }
  const header = ["slug", "name", "status", "tenant_id", "host"];
  const rows = filteredTenants.value.map((t) => [
    t.slug,
    t.name,
    t.is_active ? "aktiv" : "deaktiviert",
    t.id,
    `${t.slug}.${baseDomain}`,
  ]);
  const csv = [
    header.join(";"),
    ...rows.map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(";")),
  ].join("\n");
  const stamp = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const filename = `kunden_export_${stamp.getFullYear()}${pad(stamp.getMonth() + 1)}${pad(stamp.getDate())}_${pad(
    stamp.getHours()
  )}${pad(stamp.getMinutes())}.csv`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  toast("Export erstellt");
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadTenants();
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.minimalHeader {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface-2, #f8fafc);
  min-width: 120px;
}

.chipLabel {
  font-size: 12px;
  color: var(--muted);
}

.chipValue {
  font-weight: 700;
  font-size: 16px;
}

.chipValue.success {
  color: var(--success, #22c55e);
}

.chipValue.danger {
  color: var(--danger, #c53030);
}

.toolbarActions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.searchCard {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  display: grid;
  gap: 8px;
}

.fieldLabel {
  font-weight: 700;
  font-size: 13px;
}

.hint {
  font-size: 12px;
  color: var(--muted);
}

.filterRow {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
  flex-wrap: wrap;
}

.tableCard {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  display: grid;
  gap: 8px;
}

.tableHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tableTitle {
  font-weight: 800;
}

.tableWrap {
  overflow: auto;
}

.selectDot {
  width: 32px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--border);
  display: inline-block;
}

.dotActive {
  border-color: var(--primary);
  background: var(--primary);
}

.detailCard {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

.detailHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detailTitle {
  font-size: 16px;
  font-weight: 800;
}

.detailSub {
  color: var(--muted);
  font-size: 12px;
}

.detailStatus {
  display: flex;
}

.smallText {
  font-size: 12px;
}

.emptyState {
  margin-top: 8px;
  padding: 12px;
  border: 1px dashed var(--border, #dcdcdc);
  border-radius: 10px;
  background: var(--surface-2, #f9fafb);
}

.emptyTitle {
  font-weight: 600;
}

.emptyBody {
  color: var(--muted);
  margin: 4px 0 8px 0;
}

.errorText {
  color: var(--danger, #c53030);
  margin-top: 8px;
  font-size: 13px;
}

.dotSpinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--muted);
  border-top-color: transparent;
  display: inline-block;
  margin-right: 6px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
