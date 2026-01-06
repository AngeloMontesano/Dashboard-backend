<template>
  <div class="panel">
    <div class="sectionTitle">User Management (Quick)</div>
    <div class="kvGrid">
      <div class="kv">
        <div class="k">Neuer User</div>
        <div class="v">
          <div class="row gap8 wrap">
            <input class="input" v-model.trim="form.email" placeholder="user@example.com" />
            <input class="input" v-model="form.password" type="password" placeholder="Passwort (optional)" />
            <button class="btnPrimary small" :disabled="busy.create" @click="createUser">Anlegen</button>
          </div>
        </div>
      </div>
      <div class="kv">
        <div class="k">Passwort setzen</div>
        <div class="v">
          <div class="row gap8 wrap">
            <select class="input" v-model="localSelectedId">
              <option value="">User wählen</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.email }} ({{ u.is_active ? "aktiv" : "deaktiviert" }})
              </option>
            </select>
            <input class="input" v-model="form.newPassword" type="password" placeholder="Neues Passwort" />
            <button class="btnGhost small" :disabled="busy.password" @click="setPassword">Speichern</button>
          </div>
        </div>
      </div>
      <div class="kv">
        <div class="k">Status</div>
        <div class="v">
          <div class="row gap8 wrap">
            <select class="input" v-model="localSelectedId">
              <option value="">User wählen</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.email }} ({{ u.is_active ? "aktiv" : "deaktiviert" }})
              </option>
            </select>
            <button class="btnGhost small" :disabled="busy.toggle || !localSelectedId" @click="toggleActive(true)">Aktivieren</button>
            <button class="btnGhost small" :disabled="busy.toggle || !localSelectedId" @click="toggleActive(false)">Deaktivieren</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { adminCreateUser, adminUpdateUser } from "../../api/admin";
import type { UserOut } from "../../types";
import { useToast } from "../../composables/useToast";

const props = defineProps<{
  adminKey: string;
  actor: string;
  users: UserOut[];
  selectedUserId?: string;
}>();

const emit = defineEmits<{
  (e: "usersUpdated", users: UserOut[]): void;
  (e: "selectUser", userId: string): void;
}>();

const { toast } = useToast();

const form = reactive({
  email: "",
  password: "",
  newPassword: "",
});

const busy = reactive({
  create: false,
  password: false,
  toggle: false,
});

const localSelectedId = ref(props.selectedUserId || "");

watch(
  () => props.selectedUserId,
  (val) => {
    if (val !== undefined) {
      localSelectedId.value = val || "";
    }
  }
);

watch(
  () => props.users,
  (list) => {
    if (localSelectedId.value && !list.find((u) => u.id === localSelectedId.value)) {
      localSelectedId.value = "";
    }
  }
);

watch(localSelectedId, (val) => {
  emit("selectUser", val);
});

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

async function createUser() {
  if (!ensureAdminKey()) return;
  if (!form.email.trim()) {
    toast("E-Mail ist Pflicht");
    return;
  }
  busy.create = true;
  try {
    const created = await adminCreateUser(props.adminKey, props.actor, {
      email: form.email.trim(),
      password: form.password || null,
    });
    const next = [created, ...props.users];
    emit("usersUpdated", next);
    emit("selectUser", created.id);
    toast("User angelegt");
    form.email = "";
    form.password = "";
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.create = false;
  }
}

async function setPassword() {
  if (!ensureAdminKey()) return;
  if (!localSelectedId.value || !form.newPassword) {
    toast("User und Passwort sind Pflicht");
    return;
  }
  busy.password = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, localSelectedId.value, {
      password: form.newPassword,
    });
    updateUsers(updated);
    toast("Passwort gesetzt");
    form.newPassword = "";
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.password = false;
  }
}

async function toggleActive(state: boolean) {
  if (!ensureAdminKey()) return;
  if (!localSelectedId.value) {
    toast("Bitte User wählen");
    return;
  }
  busy.toggle = true;
  try {
    const updated = await adminUpdateUser(props.adminKey, props.actor, localSelectedId.value, { is_active: state });
    updateUsers(updated);
    toast(state ? "User aktiviert" : "User deaktiviert");
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.toggle = false;
  }
}

function updateUsers(updated: UserOut) {
  const next = props.users.map((u) => (u.id === updated.id ? updated : u));
  emit("usersUpdated", next);
  emit("selectUser", updated.id);
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
</script>
