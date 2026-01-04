<template>
  <section class="tenantsView">
    <header class="viewHeader">
      <div class="headTitles">
        <div class="headTitle">Kunden</div>
        <div class="headSubtitle">Kunden suchen und auswählen</div>
      </div>
      <div class="headActions">
        <button class="btnGhost small" @click="openCreateModal">Neuen Kunden anlegen</button>
        <button class="btnGhost small" :disabled="busy.list" @click="loadTenants">
          <span v-if="busy.list" class="dotSpinner" aria-hidden="true"></span>
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
      </div>
    </header>

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
        <button class="btnGhost small" :disabled="!filteredTenants.length" @click="exportCsv">
          Kunden exportieren CSV
        </button>
        <button class="btnGhost small" :disabled="busy.list" @click="loadTenants">Neu laden</button>
      </div>
    </div>

    <div class="searchCard">
      <div class="searchLeft">
        <label class="fieldLabel" for="kunden-search">Suche</label>
        <input
          id="kunden-search"
          class="input"
          v-model.trim="q"
          placeholder="Name oder URL-Kürzel eingeben"
          aria-label="Kunden suchen"
        />
        <div class="hint">Tippen zum Filtern. Groß und Kleinschreibung egal. Prefix zuerst, sonst enthält.</div>
      </div>
      <div class="searchRight">
        <label class="fieldLabel" for="kunden-status">Status</label>
        <select id="kunden-status" class="input" v-model="statusFilter" aria-label="Status filtern">
          <option value="all">Alle</option>
          <option value="active">Aktiv</option>
          <option value="disabled">Deaktiviert</option>
        </select>
        <span class="muted smallText">Treffer: {{ filteredTenants.length }}</span>
      </div>
    </div>

    <div class="tableCard">
      <div class="tableHeader">
        <div class="tableTitle">Kundenliste</div>
        <div class="muted smallText">Zeile anklicken, um auszuwählen.</div>
      </div>
      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th class="narrowCol"></th>
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

    <div v-if="selectedTenant" class="detailCard">
      <div class="detailHeader">
        <div class="detailTitles">
          <div class="detailLine">
            <div class="lineMain">
              <span class="detailTitle">{{ selectedTenant.name }}</span>
              <span class="dotSep">·</span>
              <span class="mono">{{ selectedTenant.id }}</span>
            </div>
            <button
              class="link tiny"
              type="button"
              title="In Zwischenablage kopieren"
              @click="copyValue(selectedTenant.id, 'Tenant ID')"
            >
              kopieren
            </button>
          </div>
          <div class="detailLine hostRow">
            <span class="mono hostValue">{{ tenantHost }}</span>
            <button
              class="link tiny"
              type="button"
              title="In Zwischenablage kopieren"
              @click="copyValue(tenantHost, 'Tenant Host')"
            >
              kopieren
            </button>
          </div>
        </div>
      </div>

      <div class="detailGrid">
        <div class="detailBox tight">
          <div class="boxLabel">Name</div>
          <div class="boxValue">{{ selectedTenant.name }}</div>
        </div>
        <div class="detailBox tight">
          <div class="boxLabel">URL-Kürzel</div>
          <div class="boxValue mono">{{ selectedTenant.slug }}</div>
        </div>
        <div class="detailBox medium">
          <div class="boxLabel">Tenant ID</div>
          <div class="boxValue mono">{{ selectedTenant.id }}</div>
        </div>
        <div class="detailBox hostBox">
          <div class="boxLabel">Tenant Host</div>
          <div class="boxValue mono hostValue">{{ tenantHost }}</div>
        </div>
      </div>

      <div class="detailActions">
        <div class="row gap8 wrap">
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
        </div>
        <button class="btnPrimary small" @click="openMemberships(selectedTenant.id)">Tenant User verwalten</button>
      </div>
    </div>

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
const tenantHost = computed(() => (selectedTenant.value ? `${selectedTenant.value.slug}.${baseDomain}` : ""));

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

  const actionLabel = t.is_active ? "deaktivieren" : "aktivieren";
  const ok = window.confirm(`Kunde ${t.slug} wirklich ${actionLabel}?`);
  if (!ok) return;

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
  const confirmed = window.confirm(`Kunde ${t.slug} wirklich löschen? Diese Aktion ist irreversibel.`);
  if (!confirmed) return;
  const check = window.prompt(
    `Bitte Tenant ID zur Bestätigung eingeben:\n${t.id}\nLöschen kann nicht rückgängig gemacht werden.`
  );
  if (!check || check.trim() !== t.id) {
    toast("Löschen abgebrochen: Tenant ID stimmt nicht.");
    return;
  }

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

async function copyValue(value: string, label: string) {
  try {
    await navigator.clipboard.writeText(value);
    toast(`${label} kopiert`);
  } catch {
    toast(`${label} konnte nicht kopiert werden`);
  }
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
.tenantsView {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.viewHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0 12px;
  border-bottom: 1px solid var(--border);
  min-height: 56px;
}

.headTitles {
  display: grid;
  gap: 4px;
}

.headTitle {
  font-size: 18px;
  font-weight: 800;
}

.headSubtitle {
  color: var(--muted);
  font-size: 13px;
}

.headActions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
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
  grid-template-columns: 1fr 220px;
  gap: 12px;
}

.fieldLabel {
  font-weight: 700;
  font-size: 13px;
}

.hint {
  font-size: 12px;
  color: var(--muted);
  margin-top: 6px;
}

.searchLeft {
  display: grid;
  gap: 6px;
}

.searchRight {
  display: grid;
  gap: 8px;
  align-content: start;
}

.smallText {
  font-size: 12px;
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

.narrowCol {
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

.table tbody tr {
  cursor: pointer;
}

.table tbody tr.rowActive {
  background: var(--surface-2, #f8fafc);
}

.detailCard {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  color: var(--text, #0f172a);
  display: grid;
  gap: 10px;
  margin-top: 4px;
}

.detailHeader {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.detailTitles {
  display: grid;
  gap: 6px;
}

.detailTitleRow {
  display: flex;
  gap: 8px;
  align-items: center;
}

.detailTitles {
  display: grid;
  gap: 6px;
}

.detailTitleRow {
  display: flex;
  gap: 8px;
  align-items: center;
}

.detailTitles {
  display: grid;
  gap: 8px;
  width: 100%;
}

.detailLine {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.lineMain {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.detailTitle {
  font-size: 16px;
  font-weight: 800;
}

.hostRow {
  color: var(--text, #0f172a);
}

.hostValue {
  white-space: nowrap;
  overflow-x: auto;
}

.dotSep {
  opacity: 0.6;
}

.detailGrid {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr 3fr;
  gap: 10px;
  align-items: stretch;
}

.detailBox {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  background: var(--surface-2, #f8fafc);
}

.boxLabel {
  font-size: 12px;
  color: var(--muted);
}

.boxValue {
  font-weight: 700;
  margin-top: 4px;
}

.detailBox.tight {
  min-width: 120px;
}

.detailBox.medium {
  min-width: 200px;
}

.detailBox.hostBox {
  min-width: 320px;
}

.detailActions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tiny {
  font-size: 11px;
  padding: 0;
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

@media (max-width: 1024px) {
  .detailGrid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

@media (max-width: 860px) {
  .searchCard {
    grid-template-columns: 1fr;
  }

  .hostValue {
    white-space: nowrap;
    overflow-x: auto;
  }
}
</style>
