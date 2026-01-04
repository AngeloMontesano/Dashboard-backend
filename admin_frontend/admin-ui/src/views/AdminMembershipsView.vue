<template>
  <section class="tenantUsersView">
    <header class="viewHeader">
      <div class="headTitles">
        <div class="headTitle">Tenant-User</div>
        <div class="headSubtitle">User mit Kunden verknüpfen und Rollen setzen</div>
      </div>
      <div class="headActions">
        <button class="btnGhost small" :disabled="busy.tenants" @click="loadTenants">
          {{ busy.tenants ? "lädt..." : "Tenants laden" }}
        </button>
        <button class="btnGhost small" :disabled="busy.list || !selectedTenant" @click="loadMemberships">
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
      </div>
    </header>

    <div class="toolbar">
      <div class="chips">
        <div class="chip">
          <div class="chipLabel">Verknüpfungen gesamt</div>
          <div class="chipValue">{{ totalMemberships }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">aktiv</div>
          <div class="chipValue success">{{ activeMemberships }}</div>
        </div>
        <div class="chip">
          <div class="chipLabel">deaktiviert</div>
          <div class="chipValue danger">{{ inactiveMemberships }}</div>
        </div>
      </div>
      <div class="toolbarActions">
        <button class="btnGhost small" :disabled="!selectedTenant" @click="toggleLinkForm">
          {{ linkForm.open ? "Schließen" : "Neu verknüpfen" }}
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
        <div class="hint">Tippen zum Filtern. Groß/Kleinschreibung egal.</div>
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
          placeholder="E-Mail suchen (live, q-Param)"
          aria-label="Tenant User suchen"
        />
        <div class="hint">Sucht serverseitig mit q. Groß/Kleinschreibung egal.</div>

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
        <div class="muted">Bitte Kunde auswählen.</div>
      </div>
    </div>

    <div class="tableCard">
      <div class="tableHeader">
        <div>
          <div class="tableTitle">Verknüpfungen</div>
          <div class="muted smallText" v-if="selectedTenant">Zeile anklicken, um Details anzuzeigen.</div>
          <div class="muted smallText" v-else>Bitte zuerst einen Tenant auswählen.</div>
        </div>
        <div class="muted smallText">Quelle: /admin/tenants/{id}/users</div>
      </div>

      <div v-if="!selectedTenant" class="mutedPad">Bitte Kunde auswählen.</div>
      <div v-else class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>E-Mail</th>
              <th>Rolle</th>
              <th>User Status</th>
              <th>Membership Status</th>
              <th>Zuletzt geändert</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="m in filteredMemberships"
              :key="m.membership_id"
              :class="{ rowActive: selectedMembership?.membership_id === m.membership_id }"
              @click="selectMembership(m)"
            >
              <td class="mono">{{ m.email }}</td>
              <td>{{ m.role }}</td>
              <td>
                <span class="tag" :class="m.user_is_active ? 'ok' : 'bad'">
                  {{ m.user_is_active ? "aktiv" : "deaktiviert" }}
                </span>
              </td>
              <td>
                <span class="tag" :class="m.membership_is_active ? 'ok' : 'bad'">
                  {{ m.membership_is_active ? "aktiv" : "deaktiviert" }}
                </span>
              </td>
              <td class="mono">{{ lastChanged(m) }}</td>
            </tr>
            <tr v-if="!busy.list && filteredMemberships.length === 0">
              <td colspan="5" class="mutedPad">Keine verknüpften Benutzer.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>
    </div>

    <div v-if="selectedMembership" class="detailCard">
      <div class="detailHeader">
        <div>
          <div class="detailTitle">{{ selectedMembership.email }}</div>
          <div class="muted">Membership {{ selectedMembership.membership_id }}</div>
        </div>
        <div class="muted">Tenant: {{ selectedTenant?.name }} ({{ selectedTenant?.slug }})</div>
      </div>

      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">Rolle</div>
          <select class="input" v-model="edit.role" :disabled="busy.save">
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div class="detailBox">
          <div class="boxLabel">User Status</div>
          <label class="toggle">
            <input type="checkbox" v-model="edit.user_is_active" :disabled="busy.save" />
            <span>{{ edit.user_is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Membership Status</div>
          <label class="toggle">
            <input type="checkbox" v-model="edit.membership_is_active" :disabled="busy.save" />
            <span>{{ edit.membership_is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
      </div>

      <div class="detailActions row gap8 wrap">
        <button class="btnPrimary small" :disabled="busy.save" @click="saveChanges">
          {{ busy.save ? "speichere..." : "Speichern" }}
        </button>
        <button class="btnGhost small" :disabled="busy.save" @click="setPassword">Passwort setzen</button>
        <button class="btnGhost small" :disabled="busy.save" @click="toggleUserStatus">
          {{ edit.user_is_active ? "User deaktivieren" : "User aktivieren" }}
        </button>
        <button class="btnGhost small" :disabled="busy.save" @click="toggleMembershipStatus">
          {{ edit.membership_is_active ? "Membership deaktivieren" : "Membership aktivieren" }}
        </button>
        <button class="btnGhost small danger" :disabled="busy.save" @click="deleteMembership">Verknüpfung löschen</button>
      </div>
    </div>

    <div v-if="linkForm.open" class="detailCard">
      <div class="detailHeader">
        <div>
          <div class="detailTitle">Neu verknüpfen</div>
          <div class="muted">User an Tenant koppeln</div>
        </div>
        <button class="btnGhost small" @click="toggleLinkForm">Schließen</button>
      </div>

      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">Tenant</div>
          <div class="boxValue mono">{{ selectedTenant ? `${selectedTenant.name} (${selectedTenant.slug})` : "Bitte auswählen" }}</div>
        </div>
        <div class="detailBox">
          <div class="boxLabel">E-Mail</div>
          <input class="input" v-model.trim="linkForm.email" placeholder="user@example.com" />
        </div>
        <div class="detailBox">
          <div class="boxLabel">Rolle</div>
          <select class="input" v-model="linkForm.role">
            <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>

      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">Passwort (optional)</div>
          <input class="input" type="password" v-model="linkForm.password" placeholder="setzt nur falls angegeben" />
        </div>
        <div class="detailBox">
          <div class="boxLabel">User aktiv</div>
          <label class="toggle">
            <input type="checkbox" v-model="linkForm.user_is_active" />
            <span>{{ linkForm.user_is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Membership aktiv</div>
          <label class="toggle">
            <input type="checkbox" v-model="linkForm.membership_is_active" />
            <span>{{ linkForm.membership_is_active ? "aktiv" : "deaktiviert" }}</span>
          </label>
        </div>
      </div>

      <div class="detailActions row gap8 wrap">
        <button class="btnPrimary small" :disabled="!selectedTenant || busy.create" @click="linkUser">
          {{ busy.create ? "verknüpfe..." : "Verknüpfen" }}
        </button>
        <div class="muted smallText">Legt User an (falls neu) und verknüpft Membership.</div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import {
  adminCreateTenantUser,
  adminDeleteTenantUser,
  adminListTenantUsers,
  adminListTenants,
  adminRoles,
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

const filters = reactive({
  tenantSearch: "",
  userSearch: "",
  status: "all",
  role: "all",
});

const linkForm = reactive({
  open: false,
  email: "",
  role: "",
  password: "",
  user_is_active: true,
  membership_is_active: true,
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
  error: "",
});

const totalMemberships = computed(() => memberships.value.length);
const activeMemberships = computed(() => memberships.value.filter((m) => m.membership_is_active).length);
const inactiveMemberships = computed(() => memberships.value.filter((m) => !m.membership_is_active).length);

const filteredTenants = computed(() => {
  if (!filters.tenantSearch.trim()) return tenants.value;
  const q = filters.tenantSearch.trim().toLowerCase();
  return tenants.value.filter((t) => t.name.toLowerCase().includes(q) || t.slug.toLowerCase().includes(q));
});

const filteredMemberships = computed(() => {
  let rows = [...memberships.value];
  const q = filters.userSearch.trim().toLowerCase();
  if (q) {
    rows = rows.filter((m) => m.email.toLowerCase().includes(q));
  }
  if (filters.status === "active") {
    rows = rows.filter((m) => m.membership_is_active && m.user_is_active);
  } else if (filters.status === "inactive") {
    rows = rows.filter((m) => !m.membership_is_active || !m.user_is_active);
  }
  if (filters.role !== "all") {
    rows = rows.filter((m) => m.role === filters.role);
  }
  return rows;
});

const debouncedTenantSearch = debounce(() => {
  /* trigger computed */
}, 250);

const debouncedUserSearch = debounce(() => {
  if (selectedTenant.value) {
    loadMemberships();
  }
}, 300);

function lastChanged(m: TenantUserOut) {
  const raw = (m as any).updated_at || (m as any).modified_at;
  return raw ? new Date(raw).toLocaleString() : "—";
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
    if (!roles.value.includes(linkForm.role)) {
      linkForm.role = roles.value[0] || "";
    }
  } catch (e: any) {
    toast(`Rollen konnten nicht geladen werden: ${stringifyError(e)}`);
  }
}

async function loadMemberships() {
  if (!ensureAdminKey() || !selectedTenant.value) return;
  busy.list = true;
  busy.error = "";
  try {
    memberships.value = await adminListTenantUsers(props.adminKey, props.actor, selectedTenant.value.id, {
      q: filters.userSearch || undefined,
      limit: 200,
      offset: 0,
    });
    toast(`Tenant-User geladen: ${memberships.value.length}`);
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler: ${busy.error}`);
  } finally {
    busy.list = false;
  }
}

function selectTenant(t: TenantOut) {
  selectedTenant.value = t;
  selectedMembership.value = null;
  emit("tenantSelected", { id: t.id, name: t.name, slug: t.slug });
  linkForm.open = false;
  loadMemberships();
}

function selectMembership(m: TenantUserOut) {
  selectedMembership.value = m;
  edit.role = m.role;
  edit.user_is_active = m.user_is_active;
  edit.membership_is_active = m.membership_is_active;
}

function toggleLinkForm() {
  if (!selectedTenant.value) {
    toast("Bitte zuerst einen Tenant auswählen.");
    return;
  }
  linkForm.open = !linkForm.open;
}

async function saveChanges() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedMembership.value) return;
  busy.save = true;
  try {
    const updated = await adminUpdateTenantUser(
      props.adminKey,
      props.actor,
      selectedTenant.value.id,
      selectedMembership.value.membership_id,
      {
        role: edit.role,
        user_is_active: edit.user_is_active,
        membership_is_active: edit.membership_is_active,
      }
    );
    memberships.value = memberships.value.map((x) => (x.membership_id === updated.membership_id ? updated : x));
    selectMembership(updated);
    toast("Gespeichert");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.save = false;
  }
}

async function setPassword() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedMembership.value) return;
  const pw = window.prompt("Neues Passwort setzen (mind. 8 Zeichen). Leer zum Abbrechen.");
  if (!pw) return;
  busy.save = true;
  try {
    const updated = await adminUpdateTenantUser(
      props.adminKey,
      props.actor,
      selectedTenant.value.id,
      selectedMembership.value.membership_id,
      { password: pw }
    );
    memberships.value = memberships.value.map((x) => (x.membership_id === updated.membership_id ? updated : x));
    toast("Passwort gesetzt");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.save = false;
  }
}

async function toggleUserStatus() {
  edit.user_is_active = !edit.user_is_active;
  await saveChanges();
}

async function toggleMembershipStatus() {
  edit.membership_is_active = !edit.membership_is_active;
  await saveChanges();
}

async function deleteMembership() {
  if (!ensureAdminKey() || !selectedTenant.value || !selectedMembership.value) return;
  const confirmDelete = window.confirm(`Membership für ${selectedMembership.value.email} löschen? User bleibt erhalten.`);
  if (!confirmDelete) return;
  busy.save = true;
  try {
    await adminDeleteTenantUser(
      props.adminKey,
      props.actor,
      selectedTenant.value.id,
      selectedMembership.value.membership_id
    );
    memberships.value = memberships.value.filter((x) => x.membership_id !== selectedMembership.value?.membership_id);
    selectedMembership.value = null;
    toast("Verknüpfung gelöscht");
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.save = false;
  }
}

async function linkUser() {
  if (!ensureAdminKey() || !selectedTenant.value) {
    toast("Bitte Tenant auswählen.");
    return;
  }
  if (!linkForm.email.trim()) {
    toast("E-Mail ist Pflicht");
    return;
  }
  if (!linkForm.role) {
    toast("Rolle auswählen");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateTenantUser(props.adminKey, props.actor, selectedTenant.value.id, {
      email: linkForm.email.trim(),
      role: linkForm.role,
      password: linkForm.password || null,
      user_is_active: linkForm.user_is_active,
      membership_is_active: linkForm.membership_is_active,
    });
    memberships.value = [created, ...memberships.value];
    selectMembership(created);
    toast("Verknüpft");
    linkForm.email = "";
    linkForm.password = "";
    linkForm.user_is_active = true;
    linkForm.membership_is_active = true;
    linkForm.open = false;
  } catch (e: any) {
    toast(`Fehler beim Verknüpfen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
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
  () => filters.tenantSearch,
  () => debouncedTenantSearch()
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
      selectedMembership.value = null;
      return;
    }
    const match = tenants.value.find((t) => t.id === id);
    if (match) {
      selectTenant(match);
    }
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
  max-height: 220px;
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
