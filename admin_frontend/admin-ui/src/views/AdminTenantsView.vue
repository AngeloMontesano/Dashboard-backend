<template>
  <!--
    AdminTenantsView
    - Kompaktere Ansicht: Suche + Anlage links, Details rechts
    - Workspace zeigt nur relevante Infos + Aktionen zum ausgewählten Tenant
  -->
  <section class="sectionShell">
    <div class="sectionHeader">
      <div class="sectionTitleWrap">
        <div class="sectionLabel">Bereich Kunden</div>
        <div class="sectionTitle">Kunden</div>
        <div class="sectionSubtitle">Tenants suchen, auswählen, Details & Aktionen</div>
        <div class="sectionMeta">
          Aktueller Tenant: <span class="mono">{{ selectedTenant?.slug || "–" }}</span>
        </div>
      </div>
      <div class="sectionStats">
        <div class="stat">
          <div class="statNumber">{{ totalTenants }}</div>
          <div class="statLabel">Tenants gesamt</div>
        </div>
        <div class="stat">
          <div class="statNumber success">{{ activeTenants }}</div>
          <div class="statLabel">aktiv</div>
        </div>
        <div class="stat">
          <div class="statNumber danger">{{ inactiveTenants }}</div>
          <div class="statLabel">deaktiviert</div>
        </div>
      </div>
    </div>

    <section class="card">
      <header class="cardHeader tight">
        <div>
          <div class="cardTitle">Kunden suchen</div>
          <div class="cardHint">Mit Enter bestätigen; Treffer sofort auswählbar</div>
        </div>
        <div class="cardHeaderActions">
          <button class="btnGhost" @click="openCreateModal">Neuen Kunden anlegen</button>
          <button class="btnPrimary" :disabled="busy.list" @click="loadTenants">
            <span v-if="busy.list" class="dotSpinner" aria-hidden="true"></span>
            {{ busy.list ? "lädt..." : "Neu laden" }}
          </button>
        </div>
      </header>

      <div class="grid2" style="align-items: stretch; gap: 16px;">
        <!-- Liste + Suche -->
        <div class="box">
          <div class="controlBar">
            <div class="controlLeft">
              <input
                class="input"
                v-model.trim="q"
                placeholder="Name oder URL-Kürzel suchen"
                @keyup.enter="loadTenants"
                aria-label="Tenant suchen"
              />
              <select class="input" v-model="statusFilter" aria-label="Status filtern">
                <option value="all">Alle</option>
                <option value="active">Aktiv</option>
                <option value="disabled">Deaktiviert</option>
              </select>
            </div>
            <div class="controlRight">
              <span class="muted smallText">Treffer: {{ filteredTenants.length }}</span>
              <span class="muted smallText">Auswahl: {{ selectedTenant ? selectedTenant.slug : "-" }}</span>
            </div>
          </div>

          <TenantTable
            :tenants="filteredTenants"
            :selectedId="selectedTenant?.id || ''"
            :busyToggleId="busy.toggleId"
            :busyList="busy.list"
            @select="selectTenant"
            @details="openDrawer"
            @toggle="toggleTenant"
            @delete="deleteTenant"
          />

          <div v-if="!busy.list && filteredTenants.length === 0" class="emptyState">
            <div class="emptyTitle">Keine Tenants gefunden</div>
            <div class="emptyBody">Lege den ersten Tenant an oder passe Suche/Filter an.</div>
            <div class="row gap8 wrap">
              <button class="btnPrimary small" @click="openCreateModal">Ersten Tenant anlegen</button>
              <button class="btnGhost small" @click="resetFilters">Filter zurücksetzen</button>
            </div>
          </div>

          <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>

          <div class="hintBox">
            Tipp: Suche via <span class="mono">GET /admin/tenants?q=...</span>. Enter startet den Call.
          </div>
        </div>

        <!-- Details + Aktionen -->
        <div class="box">
          <header class="row" style="justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
              <div class="cardTitle" style="margin: 0;">Ausgewählter Kunde</div>
              <div class="cardHint" style="margin: 0;">Kundendetails & Aktionen</div>
            </div>
            <button class="btnGhost small" :disabled="!selectedTenant" @click="selectedTenant && openDrawer(selectedTenant)">
              Details
            </button>
          </header>

          <div v-if="!selectedTenant" class="muted">
            Kein Tenant ausgewählt. Wähle links einen Kunden aus oder lege einen neuen an.
          </div>

          <div v-else class="kvGrid">
            <div class="kv">
              <div class="k">Name</div>
              <div class="v">{{ selectedTenant.name }}</div>
            </div>

            <div class="kv">
              <div class="k">URL-Kürzel</div>
              <div class="v mono">{{ selectedTenant.slug }}</div>
            </div>

            <div class="kv">
              <div class="k">Status</div>
              <div class="v">
                <span class="tag" :class="selectedTenant.is_active ? 'ok' : 'bad'">
                  {{ selectedTenant.is_active ? "aktiv" : "deaktiviert" }}
                </span>
              </div>
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
              :disabled="!selectedTenant || busy.toggleId === selectedTenant?.id"
              @click="selectedTenant && toggleTenant(selectedTenant)"
            >
              {{ busy.toggleId === selectedTenant?.id ? "..." : selectedTenant?.is_active ? "Deaktivieren" : "Aktivieren" }}
            </button>
            <button
              class="btnGhost small danger"
              :disabled="!selectedTenant || busy.deleteId === selectedTenant?.id"
              @click="selectedTenant && deleteTenant(selectedTenant)"
            >
              {{ busy.deleteId === selectedTenant?.id ? "löscht..." : "Tenant löschen" }}
            </button>
            <button
              class="btnPrimary small"
              :disabled="!selectedTenant"
              @click="selectedTenant && openMemberships(selectedTenant.id)"
            >
              Tenant-User verwalten
            </button>
          </div>

          <div class="hintBox" style="margin-top: 10px;">
            Tenant-User Verwaltung öffnet den Tab <span class="mono">Tenant-User</span> und übernimmt den ausgewählten Kunden.
            <div v-if="!hasTenants" class="muted" style="margin-top: 4px;">
              Noch keine Kunden vorhanden – lege zuerst einen Tenant an.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Drawer -->
    <TenantDrawer
      :open="drawer.open"
      :tenant="drawer.tenant"
      :busyToggle="busy.toggleId"
      :baseDomain="baseDomain"
      v-model:note="drawer.note"
      @close="closeDrawer"
      @toggle="toggleTenant"
      @delete="deleteTenant"
    />

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
  AdminTenantsView
  - Enthält nur State + API Calls + Orchestration
  - UI Bausteine sind ausgelagert:
      - TenantTable
      - TenantDrawer
      - TenantCreateModal
  - Toast zentral in App.vue, hier nur toast() verwenden
*/

import { computed, reactive, ref, watch } from "vue";
import type { TenantOut } from "../types";
import { adminListTenants, adminCreateTenant, adminUpdateTenant, adminDeleteTenant } from "../api/admin";
import { useToast } from "../composables/useToast";

/* Components */
import TenantTable from "../components/tenants/TenantTable.vue";
import TenantDrawer from "../components/tenants/TenantDrawer.vue";
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

/* Drawer State */
const drawer = reactive({
  open: false,
  tenant: null as TenantOut | null,
  note: "",
});

/* Modal State */
const modal = reactive({
  open: false,
  name: "",
  slug: "",
});

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";

const hasTenants = computed(() => tenants.value.length > 0);

/* Derived: Filter nach Status (Suche ist serverseitig via q) */
const filteredTenants = computed(() => {
  let list = tenants.value.slice();

  if (statusFilter.value === "active") list = list.filter((t) => t.is_active);
  if (statusFilter.value === "disabled") list = list.filter((t) => !t.is_active);

  return list;
});

/* API: Load Tenants */
async function loadTenants() {
  if (!ensureAdminKey()) return;
  busy.list = true;
  busy.error = "";
  try {
    const res = await adminListTenants(props.adminKey, props.actor, {
      q: q.value || undefined,
      limit: 200,
        offset: 0,
      });
      tenants.value = res;

      /* Selection stabil halten oder erste wählen */
      const preferredId =
        props.selectedTenantId ||
        localStorage.getItem("adminSelectedTenantId") ||
        sessionStorage.getItem("adminSelectedTenantId") ||
        "";

      if (selectedTenant.value) {
        selectedTenant.value = res.find((t) => t.id === selectedTenant.value!.id) ?? null;
      }
      if (!selectedTenant.value && preferredId) {
        selectedTenant.value = res.find((t) => t.id === preferredId) ?? null;
      }
      if (!selectedTenant.value && res.length > 0) {
        selectedTenant.value = res[0];
      }

      emitSelectedTenant();

    toast(`Tenants geladen: ${res.length}`);
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

    /* Optimistisch in Liste vorne einfügen */
    tenants.value = [created, ...tenants.value];

    /* UX: neuen Tenant direkt selektieren */
    selectedTenant.value = created;

    closeCreateModal();
    toast("Tenant angelegt");
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
    if (drawer.tenant?.id === updated.id) drawer.tenant = updated;

    toast(updated.is_active ? "Tenant aktiviert" : "Tenant deaktiviert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.toggleId = "";
  }
}

/* UI actions */
function selectTenant(t: TenantOut) {
  selectedTenant.value = t;
  emitSelectedTenant();
}

function openDrawer(t: TenantOut) {
  drawer.open = true;
  drawer.tenant = t;
  drawer.note = "";
}

function closeDrawer() {
  drawer.open = false;
  drawer.tenant = null;
  drawer.note = "";
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
  localStorage.setItem("adminSelectedTenantId", tenantId);
  emit("openMemberships", tenantId);
}

function resetFilters() {
  q.value = "";
  statusFilter.value = "all";
  loadTenants();
}

watch(
  () => selectedTenant.value?.id,
  (id) => {
    if (id) {
      localStorage.setItem("adminSelectedTenantId", id);
    } else {
      localStorage.removeItem("adminSelectedTenantId");
    }
  }
);
watch(
  () => props.selectedTenantId,
  (id) => {
    if (!id) {
      selectedTenant.value = null;
      emitSelectedTenant();
      return;
    }
    if (!tenants.value.length) return;
    if (selectedTenant.value?.id === id) return;
    const match = tenants.value.find((t) => t.id === id);
    if (match) {
      selectedTenant.value = match;
      emitSelectedTenant();
    }
  }
);

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

async function deleteTenant(t: TenantOut) {
  if (!ensureAdminKey()) return;
  if (!t) return;
  const confirmDelete = window.confirm(`Tenant ${t.slug} wirklich löschen? Diese Aktion ist irreversibel.`);
  if (!confirmDelete) return;

  busy.deleteId = t.id;
  try {
    await adminDeleteTenant(props.adminKey, props.actor, t.id);
    tenants.value = tenants.value.filter((x) => x.id !== t.id);
    if (selectedTenant.value?.id === t.id) selectedTenant.value = null;
    if (drawer.tenant?.id === t.id) closeDrawer();
    toast("Tenant gelöscht");
  } catch (e: any) {
    toast(`Fehler beim Löschen: ${stringifyError(e)}`);
  } finally {
    busy.deleteId = "";
  }
}

/* Helpers */
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
.sectionShell {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sectionHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid var(--border, #dcdcdc);
  border-radius: 12px;
  background: var(--surface, #fff);
}

.sectionTitleWrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sectionLabel {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--muted);
}

.sectionTitle {
  font-size: 18px;
  font-weight: 700;
}

.sectionSubtitle {
  color: var(--muted);
  font-size: 14px;
}

.sectionMeta {
  font-size: 13px;
  color: var(--muted);
}

.sectionStats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stat {
  min-width: 110px;
  padding: 8px 10px;
  border: 1px solid var(--border, #dcdcdc);
  border-radius: 10px;
  background: var(--surface-2, #f8fafc);
  text-align: center;
}

.statNumber {
  font-weight: 700;
  font-size: 18px;
}

.statNumber.success {
  color: var(--success, #22c55e);
}

.statNumber.danger {
  color: var(--danger, #c53030);
}

.statLabel {
  font-size: 12px;
  color: var(--muted);
}

.controlBar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.controlLeft {
  display: flex;
  gap: 8px;
  flex: 1;
}

.controlLeft .input {
  flex: 1;
}

.controlRight {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
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
