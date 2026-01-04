<template>
  <div class="grid2">
    <!-- User Liste -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Benutzer</div>
          <div class="cardHint">Globale User-Verwaltung (E-Mail eindeutig)</div>
        </div>
        <div class="cardHeaderActions">
          <button class="btnPrimary" :disabled="busy.list" @click="loadUsers">
            {{ busy.list ? "lade..." : "Neu laden" }}
          </button>
        </div>
      </header>

      <div class="controls">
        <input class="input" v-model.trim="search" placeholder="Filter nach E-Mail (clientseitig)" />
        <div class="muted">Treffer: {{ filteredUsers.length }}</div>
      </div>

      <div class="table">
        <div class="thead">
          <div>E-Mail</div>
          <div>Status</div>
          <div>Passwort</div>
          <div>Aktionen</div>
        </div>
        <div
          v-for="u in filteredUsers"
          :key="u.id"
          class="trow"
          :class="{ selected: selectedId === u.id }"
          @click="select(u.id)"
        >
          <div class="mono">{{ u.email }}</div>
          <div>
            <span class="tag" :class="u.is_active ? 'ok' : 'bad'">{{ u.is_active ? "aktiv" : "deaktiviert" }}</span>
          </div>
          <div>
            <span class="tag" :class="u.has_password ? 'ok' : 'warn'">{{ u.has_password ? "gesetzt" : "fehlend" }}</span>
          </div>
          <div class="row gap8">
            <button class="btnGhost small" :disabled="busy.toggleId === u.id" @click.stop="toggleActive(u)">
              {{ busy.toggleId === u.id ? "..." : u.is_active ? "Deaktivieren" : "Aktivieren" }}
            </button>
            <button class="btnGhost small" :disabled="busy.passwordId === u.id" @click.stop="promptPassword(u)">
              {{ busy.passwordId === u.id ? "..." : "Passwort setzen" }}
            </button>
          </div>
        </div>
      </div>

      <div class="hintBox">
        Aktionen nutzen <span class="mono">/admin/users</span>. Passwort wird nie angezeigt, nur gesetzt.
      </div>
    </section>

    <!-- User anlegen / Details -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Benutzer anlegen</div>
          <div class="cardHint">E-Mail ist global eindeutig, Passwort optional</div>
        </div>
      </header>

      <div class="kvGrid">
        <div class="kv">
          <div class="k">E-Mail</div>
          <div class="v">
            <input class="input" v-model.trim="form.email" placeholder="user@example.com" />
          </div>
        </div>
        <div class="kv">
          <div class="k">Passwort (optional)</div>
          <div class="v">
            <input class="input" v-model="form.password" type="password" placeholder="mind. 8 Zeichen oder leer" />
          </div>
        </div>
      </div>

      <div class="row gap8">
        <button class="btnPrimary" :disabled="busy.create" @click="createUser">
          {{ busy.create ? "legt an..." : "Benutzer anlegen" }}
        </button>
        <div class="muted">E-Mail wird in Kleinbuchstaben gespeichert.</div>
      </div>
      <div class="divider"></div>

      <div v-if="selectedUser" class="box">
        <div class="cardTitle">Auswahl</div>
        <div class="kvGrid">
          <div class="kv">
            <div class="k">User ID</div>
            <div class="v mono">{{ selectedUser.id }}</div>
          </div>
          <div class="kv">
            <div class="k">Status</div>
            <div class="v">
              <span class="tag" :class="selectedUser.is_active ? 'ok' : 'bad'">
                {{ selectedUser.is_active ? "aktiv" : "deaktiviert" }}
              </span>
            </div>
          </div>
          <div class="kv">
            <div class="k">Passwort</div>
            <div class="v">
              <span class="tag" :class="selectedUser.has_password ? 'ok' : 'warn'">
                {{ selectedUser.has_password ? "gesetzt" : "fehlend" }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="muted box">Kein Benutzer ausgewählt.</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { adminCreateUser, adminListUsers, adminUpdateUser } from "../api/admin";
import type { UserOut } from "../types";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();

const { toast } = useToast();

const users = ref<UserOut[]>([]);
const search = ref("");
const selectedId = ref<string>("");

const form = reactive({
  email: "",
  password: "",
});

const busy = reactive({
  list: false,
  create: false,
  toggleId: "",
  passwordId: "",
});

const filteredUsers = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter((u) => u.email.toLowerCase().includes(q));
});

const selectedUser = computed(() => users.value.find((u) => u.id === selectedId.value));

async function loadUsers() {
  if (!ensureAdminKey()) return;
  busy.list = true;
  try {
    const res = await adminListUsers(props.adminKey, props.actor);
    users.value = res;
    toast(`Benutzer geladen: ${res.length}`);
  } catch (e: any) {
    toast(`Fehler beim Laden: ${stringifyError(e)}`);
  } finally {
    busy.list = false;
  }
}

async function createUser() {
  if (!ensureAdminKey()) return;
  const email = form.email.trim();
  const password = form.password.trim();

  if (!email) {
    toast("E-Mail ist Pflicht");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateUser(props.adminKey, props.actor, { email, password: password || null });
    users.value = [created, ...users.value];
    selectedId.value = created.id;
    toast("Benutzer angelegt");
    form.email = "";
    form.password = "";
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

async function toggleActive(u: UserOut) {
  if (!ensureAdminKey()) return;
  busy.toggleId = u.id;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, u.id, { is_active: !u.is_active });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    toast(updated.is_active ? "Benutzer aktiviert" : "Benutzer deaktiviert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.toggleId = "";
  }
}

async function promptPassword(u: UserOut) {
  if (!ensureAdminKey()) return;
  const pw = window.prompt("Neues Passwort setzen (mind. 8 Zeichen). Leer lassen zum Abbrechen.");
  if (!pw) return;
  busy.passwordId = u.id;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, u.id, { password: pw });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    toast("Passwort gesetzt");
  } catch (e: any) {
    toast(`Fehler beim Setzen: ${stringifyError(e)}`);
  } finally {
    busy.passwordId = "";
  }
}

function select(id: string) {
  selectedId.value = id;
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
