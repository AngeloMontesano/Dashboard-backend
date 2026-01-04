<template>
  <section class="tenantUsersView">
    <header class="viewHeader">
      <div class="headTitles">
        <div class="headTitle">Tenant Benutzer</div>
        <div class="headSubtitle">User je Kunde verwalten</div>
      </div>
      <div class="headActions">
        <button class="btnGhost small" :disabled="busy.tenants" @click="loadTenants">
          {{ busy.tenants ? "lädt..." : "Tenants laden" }}
        </button>
        <button class="btnGhost small" :disabled="busy.list || !selectedTenant" @click="loadTenantUsers">
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
      </div>
    </header>

    <div class="toolbar">
      <div class="chips">
        <div class="chip">
          <div class="chipLabel">Benutzer gesamt</div>
          <div class="chipValue">{{ totalUsers }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">aktiv</div>
          <div class="chipValue success">{{ activeUsers }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">deaktiviert</div>
          <div class="chipValue danger">{{ inactiveUsers }}</div>
        </div>
      </div>
      <div class="toolbarActions">
        <button class="btnGhost small" :disabled="!selectedTenant" @click="toggleCreate">
          {{ createForm.open ? "Schließen" : "Benutzer hinzufügen" }}
        </button>
      </div>
    </div>

    <div class="searchCard">
      <div class="searchLeft column">
        <label class="fieldLabel" for="tenant-search">Kunden Suche</label>
        <input
          id="tenant-search"
          class="input"
          v-model.trim="filters.tenantSearch"
          placeholder="Tenant Name oder Slug"
          aria-label="Tenant suchen"
        />
        <div class="hint">Tippen zum Filtern, case-insensitive.</div>
        <div class="tenantList">
          <button
            v-for="t in filteredTenants"
            :key="t.id"
            class="tenantOption"
            :class="{ active: selectedTenant?.id === t.id }"
            @click="selectTenant(t)"
          >
            <span class="tenantName">{{ t.name }}</span>
            <span class="muted mono">{{ t.slug }}</span>
          </button>
          <div v-if="!filteredTenants.length" class="muted smallText">Keine Treffer.</div>
        </div>
      </div>

      <div class="searchRight column" v-if="selectedTenant">
        <label class="fieldLabel" for="user-search">User Suche</label>
        <input
          id="user-search"
          class="input"
          v-model.trim="filters.userSearch"
          placeholder="E-Mail oder Name"
          aria-label="Tenant Benutzer suchen"
        />
        <div class="hint">Live (q-Param, debounce 300ms). Groß/Kleinschreibung egal.</div>

        <div class="fieldRow">
          <div class="field">
            <div class="label">Status</div>
            <select class="input" v-model="filters.status">
              <option value="all">Alle</option>
              <option value="active">aktiv</option>
              <option value="inactive">deaktiviert</option>
            </select>
          </div>
          <div class="field">
            <div class="label">Rolle</div>
            <select class="input" v-model="filters.role">
              <option value="all">Alle</option>
              <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="searchRight column" v-else>
        <div class="muted">Bitte zuerst einen Tenant auswählen.</div>
      </div>
    </div>

    <div class="tableCard">
      <div class="tableHeader">
        <div class="tableTitle">Tenant Benutzer</div>
        <div class="muted smallText">Quelle: /admin/tenants/{id}/users</div>
      </div>

      <div v-if="!selectedTenant" class="mutedPad">Bitte Kunde auswählen.</div>
      <div v-else class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>E-Mail</th>
              <th>Rolle</th>
              <th>Status</th>
              <th>Zuletzt geändert</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="u in filteredUsers"
              :key="u.id"
              :class="{ rowActive: selectedUser?.id === u.id }"
              @click="selectUser(u)"
            >
              <td class="mono">{{ u.email }}</td>
              <td>{{ u.role }}</td>
              <td>
                <span class="tag" :class="u.is_active ? 'ok' : 'bad'">
                  {{ u.is_active ? "aktiv" : "deaktiviert" }}
                </span>
              </td>
              <td class="mono">{{ lastChanged(u) }}</td>
            </tr>
            <tr v-if="!busy.list && filteredUsers.length === 0">
              <td colspan="4" class="mutedPad">Keine Tenant Benutzer gefunden.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>
    </div>

    <div v-if="selectedUser" class="detailCard">
      <div class="detailHeader">
        <div>
          <div class="detailTitle">{{ selectedUser.email }}</div>
          <div class="muted mono">ID: {{ selectedUser.id }}</div>
        </div>
        <button class="btnGhost small" @click="copyEmail">E-Mail kopieren</button>
      </div>

      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">Status</div>
          <label class="toggle">
            <input type="checkbox" v-model="edit.is_active" :disabled="busy.save" />
            <span>{{ edit.is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Rolle</div>
          <select class="input" v-model="edit.role" :disabled="busy.save">
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>

      <div class="detailActions row gap8 wrap">
        <button class="btnPrimary small" :disabled="busy.save" @click="saveUser">
          {{ busy.save ? "speichere..." : "Speichern" }}
        </button>
        <button class="btnGhost small" :disabled="busy.password" @click="setPassword">
          {{ busy.password ? "setzt..." : "Passwort setzen" }}
        </button>
        <button class="btnGhost small" :disabled="busy.save" @click="toggleActive">
          {{ edit.is_active ? "Deaktivieren" : "Aktivieren" }}
        </button>
        <button class="btnGhost small danger" :disabled="busy.save" @click="deleteUser">
          Löschen
        </button>
      </div>
    </div>

    <div v-if="createForm.open" ref="createCardRef" class="detailCard">
      <div class="detailHeader">
        <div>
          <div class="detailTitle">Neuen Tenant Benutzer anlegen</div>
          <div class="muted">Passwort Pflicht, Rolle wählen.</div>
        </div>
        <button class="btnGhost small" @click="toggleCreate">Schließen</button>
      </div>

      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">Tenant</div>
          <div class="boxValue mono">{{ selectedTenant ? `${selectedTenant.name} (${selectedTenant.slug})` : "Bitte auswählen" }}</div>
        </div>
        <div class="detailBox">
          <div class="boxLabel">E-Mail</div>
          <input class="input" v-model.trim="createForm.email" placeholder="user@example.com" />
        </div>
        <div class="detailBox">
          <div class="boxLabel">Rolle</div>
          <select class="input" v-model="createForm.role">
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Passwort</div>
          <input class="input" type="password" v-model="createForm.password" placeholder="mind. 8 Zeichen" />
        </div>
        <div class="detailBox">
          <div class="boxLabel">Status</div>
          <label class="toggle">
            <input type="checkbox" v-model="createForm.is_active" />
            <span>{{ createForm.is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
      </div>

      <div class="detailActions row gap8 wrap">
        <button class="btnPrimary small" :disabled="!selectedTenant || busy.create" @click="createUser">
          {{ busy.create ? "legt an..." : "Benutzer hinzufügen" }}
        </button>
        <div class="muted smallText">Legt Tenant Benutzer an und lädt Liste neu.</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue";
import {
  adminCreateTenantUser,
  adminDeleteTenantUser,
  adminListTenantUsers,
  adminListTenants,
  adminRoles,
  adminSetTenantUserPassword,
  adminUpdateTenantUser,
} from "../api/admin";
import type { TenantOut, TenantUserOut } from "../types";
import { useToast } from "../composables/useToast";
import { debounce } from "../utils/debounce";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  selectedTenantId?: string;
}>();

const emit = defineEmits<{
  (e: "tenantSelected", payload: { id: string; name: string; slug: string } | null): void;
}>();

const { toast } = useToast();

const tenants = ref<TenantOut[]>([]);
const roles = ref<string[]>([]);
const memberships = ref<TenantUserOut[]>([]);

const selectedTenant = ref<TenantOut | null>(null);
const selectedMembership = ref<TenantUserOut | null>(null);

const selectedUser = ref<TenantUserOut | null>(null);

const filters = reactive({
  tenantSearch: "",
  userSearch: "",
  status: "all",
  role: "all",
});

const createForm = reactive({
  open: false,
  email: "",
  role: "",
  password: "",
  is_active: true,
});

const edit = reactive({
  role: "",
  is_active: false,
});

const edit = reactive({
  role: "",
  user_is_active: false,
  membership_is_active: false,
});

const busy = reactive({
  tenants: false,
  list: false,
  save: false,
  create: false,
  password: false,
  error: "",
});

const createCardRef = ref<HTMLElement | null>(null);

const totalUsers = computed(() => tenantUsers.value.length);
const activeUsers = computed(() => tenantUsers.value.filter((u) => u.is_active).length);
const inactiveUsers = computed(() => tenantUsers.value.filter((u) => !u.is_active).length);

const filteredTenants = computed(() => {
  if (!filters.tenantSearch.trim()) return tenants.value;
  const q = filters.tenantSearch.trim().toLowerCase();
  return tenants.value.filter((t) => t.name.toLowerCase().includes(q) || t.slug.toLowerCase().includes(q));
});

const filteredUsers = computed(() => {
  let rows = [...tenantUsers.value];
  const q = filters.userSearch.trim().toLowerCase();
  if (q) rows = rows.filter((u) => u.email.toLowerCase().includes(q));
  if (filters.status === "active") rows = rows.filter((u) => u.is_active);
  if (filters.status === "inactive") rows = rows.filter((u) => !u.is_active);
  if (filters.role !== "all") rows = rows.filter((u) => u.role === filters.role);
  return rows;
});

const debouncedUserSearch = debounce(() => {
  if (selectedTenant.value) loadTenantUsers();
}, 300);

function lastChanged(u: TenantUserOut) {
  return u.updated_at ? new Date(u.updated_at).toLocaleString() : "—";
}

async function loadTenants() {
  if (!ensureAdminKey()) return;
  busy.tenants = true;
  try {
    tenants.value = await adminListTenants(props.adminKey, props.actor, { limit: 200, offset: 0 });
    toast(`Tenants geladen: ${tenants.value.length}`);
  } catch (e: any) {
    toast(`Fehler beim Laden: ${stringifyError(e)}`);
  } finally {
    busy.tenants = false;
  }
}

async function loadRoles() {
  if (!ensureAdminKey()) return;
  try {
    roles.value = await adminRoles(props.adminKey, props.actor);
    if (!roles.value.includes(createForm.role)) createForm.role = roles.value[0] || "";
  } catch (e: any) {
    toast(`Rollen konnten nicht geladen werden: ${stringifyError(e)}`);
  }
}

async function loadTenantUsers() {
  if (!ensureAdminKey() || !selectedTenant.value) return;
  busy.list = true;
  busy.error = "";
  try {
    tenantUsers.value = await adminListTenantUsers(props.adminKey, props.actor, selectedTenant.value.id, {
      q: filters.userSearch || undefined,
      limit: 200,
      offset: 0,
    });
    toast(`Tenant Benutzer geladen: ${tenantUsers.value.length}`);
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler: ${busy.error}`);
  } finally {
    busy.list = false;
  }
}

function selectTenant(t: TenantOut) {
  selectedTenant.value = t;
  selectedUser.value = null;
  emit("tenantSelected", { id: t.id, name: t.name, slug: t.slug });
  createForm.open = false;
  loadTenantUsers();
}

function selectUser(u: TenantUserOut) {
  selectedUser.value = u;
  edit.role = u.role;
  edit.is_active = u.is_active;
}

async function saveUser() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedUser.value) return;
  busy.save = true;
  try {
    const updated = await adminUpdateTenantUser(props.adminKey, props.actor, selectedTenant.value.id, selectedUser.value.id, {
      role: edit.role,
      is_active: edit.is_active,
    });
    tenantUsers.value = tenantUsers.value.map((u) => (u.id === updated.id ? updated : u));
    selectUser(updated);
    toast("Gespeichert");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.save = false;
  }
}

async function toggleActive() {
  edit.is_active = !edit.is_active;
  await saveUser();
}

async function setPassword() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedUser.value) return;
  const pw = window.prompt("Neues Passwort (mind. 8 Zeichen)", "");
  if (!pw) return;
  busy.password = true;
  try {
    const updated = await adminSetTenantUserPassword(
      props.adminKey,
      props.actor,
      selectedTenant.value.id,
      selectedUser.value.id,
      pw
    );
    tenantUsers.value = tenantUsers.value.map((u) => (u.id === updated.id ? updated : u));
    selectUser(updated);
    toast("Passwort gesetzt");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.password = false;
  }
}

async function deleteUser() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedUser.value) return;
  const ok = window.confirm(`Tenant Benutzer ${selectedUser.value.email} löschen?`);
  if (!ok) return;
  busy.save = true;
  try {
    await adminDeleteTenantUser(props.adminKey, props.actor, selectedTenant.value.id, selectedUser.value.id);
    tenantUsers.value = tenantUsers.value.filter((u) => u.id !== selectedUser.value?.id);
    selectedUser.value = null;
    toast("Gelöscht");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.save = false;
  }
}

async function createUser() {
  if (!ensureAdminKey() || !selectedTenant.value) {
    toast("Bitte Tenant auswählen.");
    return;
  }
  if (!createForm.email.trim()) {
    toast("E-Mail ist Pflicht");
    return;
  }
  if (!createForm.password || createForm.password.length < 8) {
    toast("Passwort mindestens 8 Zeichen");
    return;
  }
  if (!createForm.role) {
    toast("Rolle auswählen");
    return;
  }
  busy.create = true;
  try {
    const created = await adminCreateTenantUser(props.adminKey, props.actor, selectedTenant.value.id, {
      email: createForm.email.trim(),
      role: createForm.role,
      password: createForm.password,
      is_active: createForm.is_active,
    });
    await loadTenantUsers();
    const match = tenantUsers.value.find((u) => u.id === created.id) || created;
    selectUser(match);
    createForm.email = "";
    createForm.password = "";
    createForm.is_active = true;
    createForm.open = false;
    await nextTick();
    toast("Tenant Benutzer angelegt");
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

function toggleCreate() {
  if (!selectedTenant.value) {
    toast("Bitte Tenant auswählen.");
    return;
  }
  createForm.open = !createForm.open;
  if (createForm.open) {
    nextTick(() => {
      createCardRef.value?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

async function copyEmail() {
  if (!selectedUser.value) return;
  try {
    await navigator.clipboard.writeText(selectedUser.value.email);
    toast("E-Mail kopiert");
  } catch {
    toast("Kopieren nicht möglich");
  }
}

function stringifyError(e: any): string {
  if (!e) return "unknown";
  if (typeof e === "string") return e;
  if (e?.response?.status === 403) return "403 Forbidden";
  if (e?.response?.status === 404) return "404 Nicht gefunden";
  if (e?.response?.data?.detail) return JSON.stringify(e.response.data.detail);
  if (e?.message) return e.message;
  try {
    return JSON.stringify(e);
  } catch {
    return String(e);
  }
}

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

watch(
  () => props.adminKey,
  async (key, prev) => {
    if (key && key !== prev) {
      await loadRoles();
      await loadTenants();
    }
  },
  { immediate: true }
);

watch(
  () => filters.userSearch,
  () => debouncedUserSearch()
);

watch(
  () => props.selectedTenantId,
  (id) => {
    if (!id) {
      selectedTenant.value = null;
      selectedUser.value = null;
      return;
    }
    const match = tenants.value.find((t) => t.id === id);
    if (match) selectTenant(match);
  }
);
</script>

<style scoped>
.tenantUsersView {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.viewHeader {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.headTitles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.headTitle {
  font-size: 22px;
  font-weight: 700;
}

.headSubtitle {
  color: var(--muted);
}

.headActions {
  display: flex;
  gap: 8px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  min-width: 140px;
}

.chipLabel {
  color: var(--muted);
  font-size: 12px;
}

.chipValue {
  font-size: 18px;
  font-weight: 700;
}

.chipValue.success {
  color: var(--green);
}

.chipValue.danger {
  color: var(--red);
}

.toolbarActions {
  display: flex;
  gap: 8px;
}

.searchCard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tenantList {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow: auto;
  padding-right: 4px;
}

.tenantOption {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  cursor: pointer;
  text-align: left;
}

.tenantOption.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px var(--primary);
}

.tenantName {
  font-weight: 600;
}

.fieldRow {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 6px;
}

.tableCard {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
}

.tableHeader {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.tableTitle {
  font-weight: 700;
}

.detailCard {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detailHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detailTitle {
  font-size: 18px;
  font-weight: 700;
}

.detailGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.detailBox {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
}

.boxLabel {
  color: var(--muted);
  font-size: 12px;
}

.boxValue {
  font-weight: 600;
}

.detailActions {
  align-items: center;
}

.errorText {
  color: var(--red);
  margin-top: 8px;
}

@media (max-width: 960px) {
  .searchCard {
    grid-template-columns: 1fr;
  }
}
</style>
