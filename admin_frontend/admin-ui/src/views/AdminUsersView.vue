<template>
  <section class="usersView">
    <header class="viewHeader">
      <div class="headTitles">
        <div class="headTitle">Benutzer</div>
        <div class="headSubtitle">Admin-Portal Benutzer verwalten</div>
      </div>
      <div class="headActions">
        <button class="btnGhost small" :disabled="busy.list" @click="loadUsers">
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateModal">Neuen Benutzer anlegen</button>
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
        <button class="btnGhost small" :disabled="!filteredUsers.length" @click="exportCsv">
          Benutzer exportieren CSV
        </button>
      </div>
    </div>

    <div class="searchCard">
      <div class="searchLeft">
        <label class="fieldLabel" for="user-search">Suche E-Mail</label>
        <input
          id="user-search"
          class="input"
          v-model.trim="search"
          placeholder="user@example.com"
          aria-label="Benutzer nach E-Mail filtern"
        />
        <div class="hint">Tippen zum Filtern. Groß und Kleinschreibung egal.</div>
      </div>
      <div class="searchRight">
        <span class="muted smallText">Treffer: {{ filteredUsers.length }}</span>
        <button class="btnGhost small" @click="resetFilters" :disabled="!search">Filter zurücksetzen</button>
      </div>
    </div>

    <div class="tableCard">
      <div class="tableHeader">
        <div class="tableTitle">Benutzerliste</div>
        <div class="muted smallText">Zeile anklicken, um auszuwählen.</div>
      </div>
      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>E-Mail</th>
              <th>Status</th>
              <th>Passwort-Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="u in filteredUsers"
              :key="u.id"
              :class="{ rowActive: selectedUser?.id === u.id }"
              @click="select(u)"
            >
              <td class="mono">{{ u.email }}</td>
              <td>
                <span class="tag" :class="u.is_active ? 'ok' : 'bad'">{{ u.is_active ? 'aktiv' : 'deaktiviert' }}</span>
              </td>
              <td>
                <span class="tag" :class="u.has_password ? 'ok' : 'warn'">
                  {{ u.has_password ? "gesetzt" : "nicht gesetzt" }}
                </span>
              </td>
            </tr>
            <tr v-if="!busy.list && filteredUsers.length === 0">
              <td colspan="3" class="mutedPad">Keine Benutzer gefunden.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>
    </div>

    <div v-if="selectedUser" class="detailCard">
      <div class="detailGrid">
        <div class="detailBox">
          <div class="boxLabel">E-Mail</div>
          <div class="boxValue mono">{{ selectedUser.email }}</div>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Status</div>
          <div class="boxValue">
            <span class="tag" :class="selectedUser.is_active ? 'ok' : 'bad'">
              {{ selectedUser.is_active ? "aktiv" : "deaktiviert" }}
            </span>
          </div>
        </div>
        <div class="detailBox">
          <div class="boxLabel">Passwort</div>
          <div class="boxValue">
            <span class="tag" :class="selectedUser.has_password ? 'ok' : 'warn'">
              {{ selectedUser.has_password ? "gesetzt" : "nicht gesetzt" }}
            </span>
          </div>
        </div>
      </div>

      <div class="detailActions">
        <div class="row gap8 wrap">
          <button
            class="btnGhost small"
            :disabled="busy.toggleId === selectedUser.id"
            @click="toggleActive(selectedUser)"
          >
            {{ busy.toggleId === selectedUser.id ? "..." : selectedUser.is_active ? "Deaktivieren" : "Aktivieren" }}
          </button>
          <button class="btnGhost small" @click="openPasswordModal(selectedUser)">Passwort setzen</button>
        </div>
      </div>
    </div>

    <UserCreateModal
      :open="modalCreate.open"
      :busy="busy.create"
      v-model:email="modalCreate.email"
      v-model:password="modalCreate.password"
      @close="closeCreateModal"
      @create="createUser"
    />

    <PasswordModal
      :open="modalPassword.open"
      :busy="busy.password"
      :email="selectedUser?.email || ''"
      v-model:password="modalPassword.password"
      @close="closePasswordModal"
      @save="savePassword"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { adminCreateUser, adminListUsers, adminUpdateUser } from "../api/admin";
import type { UserOut } from "../types";
import { useToast } from "../composables/useToast";

import UserCreateModal from "../components/users/UserCreateModal.vue";
import PasswordModal from "../components/users/UserPasswordModal.vue";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();

const { toast } = useToast();

const users = ref<UserOut[]>([]);
const selectedUser = ref<UserOut | null>(null);
const search = ref("");

const modalCreate = reactive({
  open: false,
  email: "",
  password: "",
});

const modalPassword = reactive({
  open: false,
  password: "",
});

const busy = reactive({
  list: false,
  create: false,
  toggleId: "",
  password: false,
  error: "",
});

const totalUsers = computed(() => users.value.length);
const activeUsers = computed(() => users.value.filter((u) => u.is_active).length);
const inactiveUsers = computed(() => users.value.filter((u) => !u.is_active).length);

const filteredUsers = computed(() => {
  const term = search.value.trim().toLowerCase();
  if (!term) return users.value;
  return users.value.filter((u) => u.email.toLowerCase().includes(term));
});

async function loadUsers() {
  if (!ensureAdminKey()) return;
  busy.list = true;
  busy.error = "";
  try {
    const res = await adminListUsers(props.adminKey, props.actor);
    users.value = res;
    if (selectedUser.value) {
      selectedUser.value = res.find((u) => u.id === selectedUser.value?.id) ?? null;
    }
    toast(`Benutzer geladen: ${res.length}`);
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler beim Laden: ${busy.error}`);
  } finally {
    busy.list = false;
  }
}

async function createUser() {
  if (!ensureAdminKey()) return;
  const email = modalCreate.email.trim().toLowerCase();
  const password = modalCreate.password.trim();

  if (!email) {
    toast("E-Mail ist Pflicht");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateUser(props.adminKey, props.actor, { email, password: password || null });
    users.value = [created, ...users.value];
    selectedUser.value = created;
    toast("Benutzer angelegt");
    closeCreateModal();
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

async function toggleActive(u: UserOut) {
  if (!ensureAdminKey()) return;
  const actionLabel = u.is_active ? "deaktivieren" : "aktivieren";
  const ok = window.confirm(`Benutzer ${u.email} wirklich ${actionLabel}?`);
  if (!ok) return;

  busy.toggleId = u.id;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, u.id, { is_active: !u.is_active });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    if (selectedUser.value?.id === updated.id) selectedUser.value = updated;
    toast(updated.is_active ? "Benutzer aktiviert" : "Benutzer deaktiviert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.toggleId = "";
  }
}

function openPasswordModal(u: UserOut) {
  selectedUser.value = u;
  modalPassword.password = "";
  modalPassword.open = true;
}

function closePasswordModal() {
  modalPassword.open = false;
  modalPassword.password = "";
}

async function savePassword() {
  if (!ensureAdminKey() || !selectedUser.value) return;
  const pw = modalPassword.password.trim();
  if (!pw || pw.length < 8) {
    toast("Passwort muss mindestens 8 Zeichen haben");
    return;
  }

  busy.password = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, selectedUser.value.id, { password: pw });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    selectedUser.value = updated;
    toast("Passwort gesetzt");
    closePasswordModal();
  } catch (e: any) {
    toast(`Fehler beim Setzen: ${stringifyError(e)}`);
  } finally {
    busy.password = false;
  }
}

function select(u: UserOut) {
  selectedUser.value = u;
}

function resetFilters() {
  search.value = "";
}

function openCreateModal() {
  modalCreate.open = true;
  modalCreate.email = "";
  modalCreate.password = "";
}

function closeCreateModal() {
  modalCreate.open = false;
  modalCreate.email = "";
  modalCreate.password = "";
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

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

function exportCsv() {
  if (!filteredUsers.value.length) {
    toast("Keine Benutzer zum Export");
    return;
  }

  const header = ["email", "status", "passwort_status"];
  const rows = filteredUsers.value.map((u) => [
    u.email,
    u.is_active ? "aktiv" : "deaktiviert",
    u.has_password ? "gesetzt" : "nicht gesetzt",
  ]);
  const csv = [
    header.join(";"),
    ...rows.map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(";")),
  ].join("\n");
  const stamp = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const filename = `admin_users_export_${stamp.getFullYear()}${pad(stamp.getMonth() + 1)}${pad(stamp.getDate())}_${pad(
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
      loadUsers();
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.usersView {
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
  grid-template-columns: 1fr 200px;
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
  justify-items: end;
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

.detailGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
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

.detailActions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.errorText {
  color: var(--danger, #c53030);
  margin-top: 8px;
  font-size: 13px;
}

@media (max-width: 860px) {
  .searchCard {
    grid-template-columns: 1fr;
  }
}
</style>
