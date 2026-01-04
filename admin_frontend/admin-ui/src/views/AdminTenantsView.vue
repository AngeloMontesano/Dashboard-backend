<template>
  <!--
    AdminTenantsView
    - Kompaktere Ansicht: Suche + Anlage links, Details rechts
    - Workspace zeigt nur relevante Infos + Aktionen zum ausgewählten Tenant
  -->
  <section class="card">
    <header class="cardHeader">
      <div>
        <div class="cardTitle">Kunden</div>
        <div class="cardHint">Tenants suchen, anlegen, Details & Tenant-User verwalten</div>
      </div>
      <div class="cardHeaderActions">
        <button class="btnGhost" @click="openCreateModal">Tenant anlegen</button>
        <button class="btnPrimary" :disabled="busy.list" @click="loadTenants">
          {{ busy.list ? "lade..." : "Neu laden" }}
        </button>
      </div>
    </header>

    <div class="grid2" style="align-items: start; gap: 16px;">
      <!-- Liste + Suche -->
      <div class="box">
        <div v-if="adminKeyMissing" class="hintBox" style="margin-bottom: 8px;">
          Admin Key fehlt. Bitte links in der Sidebar setzen, damit Kunden geladen werden können.
        </div>
        <div class="row gap8 wrap" style="margin-bottom: 10px;">
          <input class="input" v-model.trim="q" placeholder="Suche: Name, Slug" @keyup.enter="loadTenants" />
          <select class="input" v-model="statusFilter">
            <option value="all">Alle</option>
            <option value="active">Aktiv</option>
            <option value="disabled">Deaktiviert</option>
          </select>
        </div>
        <div class="meta" style="margin-bottom: 8px;">
          <div class="muted">Treffer: {{ filteredTenants.length }}</div>
          <div class="muted">
            Ausgewählt: <span class="mono">{{ selectedTenant ? selectedTenant.slug : "-" }}</span>
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

        <div class="hintBox">
          Tipp: Suche via <span class="mono">GET /admin/tenants?q=...</span>. Enter startet den Call.
        </div>
      </div>

      <!-- Details + Aktionen -->
      <div class="box">
        <header class="row" style="justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div>
            <div class="cardTitle" style="margin: 0;">Tenant Details</div>
            <div class="cardHint" style="margin: 0;">Status, Host, User-Verwaltung</div>
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
  selectedTenantId: string;
}>();

const emit = defineEmits<{
  (e: "openMemberships", tenantId: string): void;
  (e: "selectTenant", tenantId: string): void;
}>();

const { toast } = useToast();

/* State */
const tenants = ref<TenantOut[]>([]);
const selectedTenant = ref<TenantOut | null>(null);

const q = ref("");
const statusFilter = ref<"all" | "active" | "disabled">("all");

const busy = reactive({
  list: false,
  create: false,
  toggleId: "" as string,
  deleteId: "" as string,
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
const adminKeyMissing = computed(() => !props.adminKey);

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
  try {
    const res = await adminListTenants(props.adminKey, props.actor, {
      q: q.value || undefined,
      limit: 200,
        offset: 0,
      });
      tenants.value = res;

      /* Selection stabil halten oder erste wählen */
      if (props.selectedTenantId) {
        const pre = res.find((t) => t.id === props.selectedTenantId);
        if (pre) selectedTenant.value = pre;
      }
      if (selectedTenant.value) {
        selectedTenant.value = res.find((t) => t.id === selectedTenant.value!.id) ?? null;
      }
      if (!selectedTenant.value && res.length > 0) {
        selectedTenant.value = res[0];
      }

    toast(`Tenants geladen: ${res.length}`);
  } catch (e: any) {
    toast(`Fehler beim Laden: ${stringifyError(e)}`);
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
  emit("selectTenant", t.id);
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
  sessionStorage.setItem("adminSelectedTenantId", tenantId);
  emit("openMemberships", tenantId);
}

watch(
  () => selectedTenant.value?.id,
  (id) => {
    if (id) {
      sessionStorage.setItem("adminSelectedTenantId", id);
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
