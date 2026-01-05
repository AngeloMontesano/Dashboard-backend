<template>
  <UiPage>
    <UiSection title="Benutzer" subtitle="Admin-Portal Benutzer verwalten">
      <template #actions>
        <button class="btnGhost small" :disabled="busy.list" @click="loadUsers">
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" @click="openCreateCard">Neuen Benutzer anlegen</button>
      </template>

      <UiToolbar>
        <template #start>
          <div class="chip-list">
            <UiStatCard label="Benutzer gesamt" :value="totalUsers" />
            <UiStatCard label="aktiv" :value="activeUsers" tone="success" />
            <UiStatCard label="deaktiviert" :value="inactiveUsers" tone="danger" />
          </div>
        </template>
        <template #end>
          <button class="btnGhost small" :disabled="!filteredUsers.length" @click="exportCsv">
            Benutzer exportieren CSV
          </button>
        </template>
      </UiToolbar>

      <div class="filter-card">
        <div class="stack">
          <label class="field-label" for="user-search">Suche E-Mail</label>
          <input
            id="user-search"
            class="input"
            v-model.trim="search"
            placeholder="user@example.com"
            aria-label="Benutzer nach E-Mail filtern"
          />
          <div class="hint">Tippen zum Filtern. Groß und Kleinschreibung egal.</div>
        </div>
        <div class="stack">
          <span class="text-muted text-small">Treffer: {{ filteredUsers.length }}</span>
          <button class="btnGhost small" @click="resetFilters" :disabled="!search">Filter zurücksetzen</button>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Benutzerliste</div>
          <div class="text-muted text-small">Zeile anklicken, um auszuwählen.</div>
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

      <div v-if="selectedUser" class="detail-card">
        <div class="detail-grid">
          <div class="detail-box">
            <div class="detail-box__label">E-Mail</div>
            <div class="detail-box__value mono">{{ selectedUser.email }}</div>
          </div>
          <div class="detail-box">
            <div class="detail-box__label">Status</div>
            <div class="detail-box__value">
              <span class="tag" :class="selectedUser.is_active ? 'ok' : 'bad'">
                {{ selectedUser.is_active ? "aktiv" : "deaktiviert" }}
              </span>
            </div>
          </div>
          <div class="detail-box">
            <div class="detail-box__label">Passwort</div>
            <div class="detail-box__value">
              <span class="tag" :class="selectedUser.has_password ? 'ok' : 'warn'">
                {{ selectedUser.has_password ? "gesetzt" : "nicht gesetzt" }}
              </span>
            </div>
          </div>
        </div>

        <div class="action-row">
          <button class="btnGhost small" :disabled="busy.toggleId === selectedUser.id" @click="toggleActive(selectedUser)">
            {{ busy.toggleId === selectedUser.id ? "..." : selectedUser.is_active ? "Deaktivieren" : "Aktivieren" }}
          </button>
          <button class="btnGhost small" @click="openPasswordModal(selectedUser)">Passwort setzen</button>
        </div>
      </div>

      <div v-if="createForm.open" ref="createCardRef">
        <UserCreateCard
          :open="createForm.open"
          :busy="busy.create"
          v-model:email="createForm.email"
          v-model:password="createForm.password"
          @close="closeCreateCard"
          @create="createUser"
        />
      </div>

      <PasswordModal
        :open="modalPassword.open"
        :busy="busy.password"
        :email="selectedUser?.email || ''"
        v-model:password="modalPassword.password"
        @close="closePasswordModal"
        @save="savePassword"
      />
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue";
import { adminCreateUser, adminListUsers, adminUpdateUser } from "../api/admin";
import type { UserOut } from "../types";
import { useToast } from "../composables/useToast";

import UserCreateCard from "../components/users/UserCreateCard.vue";
import PasswordModal from "../components/users/UserPasswordModal.vue";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import UiToolbar from "../components/ui/UiToolbar.vue";
import UiStatCard from "../components/ui/UiStatCard.vue";

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

const createForm = reactive({
  open: false,
  email: "",
  password: "",
});

const createCardRef = ref<HTMLElement | null>(null);

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
    toast(`Benutzer geladen: ${res.length}`, "success");
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler beim Laden: ${busy.error}`, "danger");
  } finally {
    busy.list = false;
  }
}

async function createUser() {
  if (!ensureAdminKey()) return;
  const email = createForm.email.trim().toLowerCase();
  const password = createForm.password.trim();

  if (!email) {
    toast("E-Mail ist Pflicht", "warning");
    return;
  }
  if (!password || password.length < 8) {
    toast("Passwort muss mindestens 8 Zeichen haben", "warning");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateUser(props.adminKey, props.actor, { email, password });
    users.value = [created, ...users.value];
    selectedUser.value = created;
    toast("Benutzer angelegt", "success");
    closeCreateCard();
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`, "danger");
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
    toast(updated.is_active ? "Benutzer aktiviert" : "Benutzer deaktiviert", "success");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`, "danger");
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
    toast("Passwort muss mindestens 8 Zeichen haben", "warning");
    return;
  }

  busy.password = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, selectedUser.value.id, { password: pw });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    selectedUser.value = updated;
    toast("Passwort gesetzt", "success");
    closePasswordModal();
  } catch (e: any) {
    toast(`Fehler beim Setzen: ${stringifyError(e)}`, "danger");
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

async function openCreateCard() {
  createForm.open = true;
  createForm.email = "";
  createForm.password = "";
  await nextTick();
  createCardRef.value?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeCreateCard() {
  createForm.open = false;
  createForm.email = "";
  createForm.password = "";
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
    toast("Bitte Admin Key setzen", "warning");
    return false;
  }
  return true;
}

function exportCsv() {
  if (!filteredUsers.value.length) {
    toast("Keine Benutzer zum Export", "warning");
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
  toast("Export erstellt", "success");
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
