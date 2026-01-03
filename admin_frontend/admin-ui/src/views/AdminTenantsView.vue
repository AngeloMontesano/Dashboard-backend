<template>
  <!--
    AdminTenantsView
    - Orchestrator für Tenant Verwaltung
    - Rendert: Liste links, Workspace rechts
    - Öffnet Drawer + Modal, macht API Calls
  -->
  <div class="grid2">
    <!-- LEFT: Tenant Liste -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Kunden</div>
          <div class="cardHint">Tenants auswählen und verwalten</div>
        </div>

        <div class="cardHeaderActions">
          <button class="btnGhost" @click="openCreateModal">Tenant anlegen</button>
          <button class="btnPrimary" :disabled="busy.list" @click="loadTenants">
            {{ busy.list ? "lade..." : "Neu laden" }}
          </button>
        </div>
      </header>

      <!-- Controls -->
      <div class="controls">
        <input class="input" v-model.trim="q" placeholder="Suche: Name, Slug" @keyup.enter="loadTenants" />
        <select class="input" v-model="statusFilter">
          <option value="all">Alle</option>
          <option value="active">Aktiv</option>
          <option value="disabled">Deaktiviert</option>
        </select>
      </div>

      <div class="meta">
        <div class="muted">Treffer: {{ filteredTenants.length }}</div>
        <div class="muted">
          Ausgewählt:
          <span class="mono">{{ selectedTenant ? selectedTenant.slug : "-" }}</span>
        </div>
      </div>

      <!-- Table Component -->
      <TenantTable
        :tenants="filteredTenants"
        :selectedId="selectedTenant?.id || ''"
        :busyToggleId="busy.toggleId"
        :busyList="busy.list"
        @select="selectTenant"
        @details="openDrawer"
        @toggle="toggleTenant"
      />

      <div class="hintBox">
        Tipp: Suche via <span class="mono">GET /admin/tenants?q=...</span>. Enter startet den Call.
      </div>
    </section>

    <!-- RIGHT: Workspace -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Workspace</div>
          <div class="cardHint">Ausgewählter Tenant</div>
        </div>

        <div class="cardHeaderActions">
          <button class="btnGhost" :disabled="!selectedTenant" @click="openDrawer(selectedTenant!)">
            Details
          </button>
        </div>
      </header>

      <div class="box">
        <div v-if="!selectedTenant" class="muted">Kein Tenant ausgewählt.</div>

        <div v-else class="kvGrid">
          <div class="kv">
            <div class="k">Name</div>
            <div class="v">{{ selectedTenant.name }}</div>
          </div>

          <div class="kv">
            <div class="k">Slug</div>
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
        </div>
      </div>

      <div class="hintBox" style="margin-top: 10px;">
        Nächster Schritt: Workspace Tabs (Benutzer, Memberships, Support) tenant scoped laden.
      </div>
    </section>

    <!-- Drawer -->
    <TenantDrawer
      :open="drawer.open"
      :tenant="drawer.tenant"
      :busyToggle="busy.toggleId"
      v-model:note="drawer.note"
      @close="closeDrawer"
      @toggle="toggleTenant"
    />

    <!-- Create Modal -->
    <TenantCreateModal
      :open="modal.open"
      :busy="busy.create"
      v-model:name="modal.name"
      v-model:slug="modal.slug"
      @close="closeCreateModal"
      @create="createTenant"
    />
  </div>
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

import { computed, onMounted, reactive, ref } from "vue";
import type { TenantOut } from "../types";
import { adminListTenants, adminCreateTenant, adminUpdateTenant } from "../api/admin";
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

/* Derived: Filter nach Status (Suche ist serverseitig via q) */
const filteredTenants = computed(() => {
  let list = tenants.value.slice();

  if (statusFilter.value === "active") list = list.filter((t) => t.is_active);
  if (statusFilter.value === "disabled") list = list.filter((t) => !t.is_active);

  return list;
});

/* API: Load Tenants */
async function loadTenants() {
  busy.list = true;
  try {
    const res = await adminListTenants(props.adminKey, props.actor, {
      q: q.value || undefined,
      limit: 200,
      offset: 0,
    });

    tenants.value = res;

    /* Selection stabil halten */
    if (selectedTenant.value) {
      selectedTenant.value = res.find((t) => t.id === selectedTenant.value!.id) ?? null;
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
  const name = modal.name.trim();
  const slug = modal.slug.trim();

  if (!name || !slug) {
    toast("Name und Slug sind Pflicht");
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

/* Helpers */
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

onMounted(() => {
  loadTenants();
});
</script>
