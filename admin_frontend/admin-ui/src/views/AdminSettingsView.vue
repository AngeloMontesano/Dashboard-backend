<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">Security, Feature Flags</div>
        </div>
      </div>

      <div class="box">
        <div class="kvGrid">
          <div class="kv">
            <div class="k">API Base</div>
            <div class="v mono">{{ apiBase }}</div>
          </div>
          <div class="kv">
            <div class="k">Base Domain</div>
            <div class="v mono">{{ baseDomain }}</div>
          </div>
          <div class="kv">
            <div class="k">Admin Key Länge</div>
            <div class="v">{{ adminKey ? adminKey.length : 0 }} Zeichen</div>
          </div>
          <div class="kv">
            <div class="k">Actor</div>
            <div class="v mono">{{ actor || "admin" }}</div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="row gap8 wrap">
          <button class="btnGhost" @click="$emit('toggleDark')">
            {{ dark ? "Light Mode" : "Dark Mode" }}
          </button>
          <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
            Admin Context zurücksetzen
          </button>
        </div>

        <div class="divider"></div>

        <div class="sectionTitle">User Management (Quick)</div>
        <div class="kvGrid">
          <div class="kv">
            <div class="k">Neuer User</div>
            <div class="v">
              <div class="row gap8 wrap">
                <input class="input" v-model.trim="userForm.email" placeholder="user@example.com" />
                <input class="input" v-model="userForm.password" type="password" placeholder="Passwort (optional)" />
                <button class="btnPrimary small" :disabled="busy.createUser" @click="createUser">Anlegen</button>
              </div>
            </div>
          </div>
          <div class="kv">
            <div class="k">Passwort setzen</div>
            <div class="v">
              <div class="row gap8 wrap">
                <select class="input" v-model="selectedUserId">
                  <option value="">User wählen</option>
                  <option v-for="u in users" :key="u.id" :value="u.id">
                    {{ u.email }} ({{ u.is_active ? "aktiv" : "deaktiviert" }})
                  </option>
                </select>
                <input class="input" v-model="userForm.newPassword" type="password" placeholder="Neues Passwort" />
                <button class="btnGhost small" :disabled="busy.password" @click="setPassword">Speichern</button>
              </div>
            </div>
          </div>
          <div class="kv">
            <div class="k">Status</div>
            <div class="v">
              <div class="row gap8 wrap">
                <select class="input" v-model="selectedUserId">
                  <option value="">User wählen</option>
                  <option v-for="u in users" :key="u.id" :value="u.id">
                    {{ u.email }} ({{ u.is_active ? "aktiv" : "deaktiviert" }})
                  </option>
                </select>
                <button class="btnGhost small" :disabled="busy.toggle || !selectedUserId" @click="toggleActive(true)">Aktivieren</button>
                <button class="btnGhost small" :disabled="busy.toggle || !selectedUserId" @click="toggleActive(false)">Deaktivieren</button>
              </div>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="kvGrid">
          <div class="kv">
            <div class="k">Security Hinweise</div>
            <div class="v">
              <ul class="bullets">
                <li>Admin Key nie im LocalStorage persistieren.</li>
                <li>Nur HTTPS nutzen, wenn hinter Proxy.</li>
                <li>Actor optional für Audit setzen (X-Admin-Actor).</li>
              </ul>
            </div>
          </div>
          <div class="kv">
            <div class="k">Feature Flags (UI)</div>
            <div class="v">
              <ul class="bullets">
                <li>Dark Mode Toggle</li>
                <li>Admin Context Reset</li>
                <li>Health-Anzeigen in Sidebar</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminSettingsView
  - Phase 1: Platzhalter
  - Phase 2: UI Settings, Feature Flags
*/
import { onMounted, reactive, ref } from "vue";
import { adminCreateUser, adminListUsers, adminUpdateUser } from "../api/admin";
import type { UserOut } from "../types";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  dark: boolean;
  apiBase: string;
  baseDomain: string;
}>();

const emit = defineEmits<{
  (e: "toggleDark"): void;
  (e: "resetContext"): void;
}>();

const { toast } = useToast();
const users = ref<UserOut[]>([]);
const selectedUserId = ref("");

const userForm = reactive({
  email: "",
  password: "",
  newPassword: "",
});

const busy = reactive({
  list: false,
  createUser: false,
  password: false,
  toggle: false,
});

async function loadUsers() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return;
  }
  busy.list = true;
  try {
    users.value = await adminListUsers(props.adminKey, props.actor);
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.list = false;
  }
}

async function createUser() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return;
  }
  if (!userForm.email.trim()) {
    toast("E-Mail ist Pflicht");
    return;
  }
  busy.createUser = true;
  try {
    const created = await adminCreateUser(props.adminKey, props.actor, {
      email: userForm.email.trim(),
      password: userForm.password || null,
    });
    users.value = [created, ...users.value];
    selectedUserId.value = created.id;
    toast("User angelegt");
    userForm.email = "";
    userForm.password = "";
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.createUser = false;
  }
}

async function setPassword() {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return;
  }
  if (!selectedUserId.value || !userForm.newPassword) {
    toast("User und Passwort sind Pflicht");
    return;
  }
  busy.password = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, selectedUserId.value, {
      password: userForm.newPassword,
    });
    users.value = users.value.map((u) => (u.id === updated.id ? updated : u));
    toast("Passwort gesetzt");
    userForm.newPassword = "";
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.password = false;
  }
}

async function toggleActive(state: boolean) {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return;
  }
  if (!selectedUserId.value) {
    toast("Bitte User wählen");
    return;
  }
  busy.toggle = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, selectedUserId.value, { is_active: state });
    users.value = users.value.map((u) => (u.id === updated.id ? updated : u));
    toast(state ? "User aktiviert" : "User deaktiviert");
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.toggle = false;
  }
}

function asError(e: any): string {
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
  loadUsers();
});
</script>
