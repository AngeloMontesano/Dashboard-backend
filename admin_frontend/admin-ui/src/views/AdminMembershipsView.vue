<template>
  <div class="grid2">
    <!-- Tenant Auswahl + Liste -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Tenant-User</div>
          <div class="cardHint">User + Membership pro Tenant verwalten</div>
        </div>
        <div class="cardHeaderActions">
          <button class="btnPrimary" :disabled="busy.tenants" @click="loadTenants">
            {{ busy.tenants ? "lädt..." : "Tenants laden" }}
          </button>
        </div>
      </header>

      <div class="controls">
        <select class="input" v-model="selectedTenantId" @change="loadTenantUsers">
          <option value="">Tenant auswählen</option>
          <option v-for="t in tenants" :key="t.id" :value="t.id">
            {{ t.name }} ({{ t.slug }})
          </option>
        </select>
        <input class="input" v-model.trim="q" placeholder="Suche E-Mail (serverseitig q)" @keyup.enter="loadTenantUsers" />
        <button class="btnGhost" :disabled="busy.users || !selectedTenantId" @click="loadTenantUsers">
          {{ busy.users ? "lädt..." : "Neu laden" }}
        </button>
      </div>

      <div class="table">
        <div class="thead">
          <div>E-Mail</div>
          <div>Rolle</div>
          <div>Status</div>
          <div>Aktion</div>
        </div>
        <div v-for="u in tenantUsers" :key="u.membership_id" class="trow">
          <div class="mono">{{ u.email }}</div>
          <div>
            <select class="input" :value="u.role" :disabled="busy.updateId === u.membership_id" @change="changeRole(u, $event)">
              <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="row gap6 wrap">
            <span class="tag" :class="u.user_is_active ? 'ok' : 'bad'">
              User {{ u.user_is_active ? "aktiv" : "deaktiviert" }}
            </span>
            <span class="tag" :class="u.membership_is_active ? 'ok' : 'bad'">
              Membership {{ u.membership_is_active ? "aktiv" : "deaktiviert" }}
            </span>
          </div>
          <div class="row gap6 wrap">
            <button class="btnGhost small" :disabled="busy.updateId === u.membership_id" @click="toggleUser(u)">
              {{ busy.updateId === u.membership_id ? "..." : u.user_is_active ? "User deaktivieren" : "User aktivieren" }}
            </button>
            <button class="btnGhost small" :disabled="busy.updateId === u.membership_id" @click="toggleMembership(u)">
              {{ busy.updateId === u.membership_id ? "..." : u.membership_is_active ? "Membership deaktivieren" : "Membership aktivieren" }}
            </button>
            <button class="btnGhost small" :disabled="busy.updateId === u.membership_id" @click="resetPassword(u)">
              {{ busy.updateId === u.membership_id ? "..." : "Passwort setzen" }}
            </button>
            <button class="btnGhost small danger" :disabled="busy.updateId === u.membership_id" @click="deleteTenantUser(u)">
              {{ busy.updateId === u.membership_id ? "..." : "Löschen" }}
            </button>
          </div>
        </div>
        <div class="kv">
          <div class="k">User aktiv?</div>
          <div class="v">
            <label class="toggle">
              <input type="checkbox" v-model="form.user_is_active" />
              <span>{{ form.user_is_active ? "aktiv" : "deaktiviert" }}</span>
            </label>
          </div>
        </div>
        <div class="kv">
          <div class="k">Membership aktiv?</div>
          <div class="v">
            <label class="toggle">
              <input type="checkbox" v-model="form.membership_is_active" />
              <span>{{ form.membership_is_active ? "aktiv" : "deaktiviert" }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="row gap8">
        <button class="btnPrimary" :disabled="!selectedTenantId || busy.create" @click="createTenantUser">
          {{ busy.create ? "legt an..." : "Hinzufügen" }}
        </button>
        <div class="muted">Legt User an (falls neu) und verknüpft Membership.</div>
      </div>

      <div class="hintBox">
        Nutzt <span class="mono">/admin/tenants/{id}/users</span>. Rollen kommen aus <span class="mono">/admin/roles</span>.
      </div>
    </section>

    <!-- User an Tenant linken -->
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">User hinzufügen</div>
          <div class="cardHint">Neuen User erzeugen oder bestehenden verknüpfen</div>
        </div>
      </header>

      <div class="kvGrid">
        <div class="kv">
          <div class="k">Tenant</div>
          <div class="v mono">{{ currentTenantLabel }}</div>
        </div>
        <div class="kv">
          <div class="k">E-Mail</div>
          <div class="v">
            <input class="input" v-model.trim="form.email" placeholder="user@example.com" />
          </div>
        </div>
        <div class="kv">
          <div class="k">Rolle</div>
          <div class="v">
            <select class="input" v-model="form.role">
              <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
        </div>
        <div class="kv">
          <div class="k">Passwort (optional)</div>
          <div class="v">
            <input class="input" v-model="form.password" type="password" placeholder="setzt nur falls angegeben" />
          </div>
        </div>
        <div class="kv">
          <div class="k">User aktiv?</div>
          <div class="v">
            <label class="toggle">
              <input type="checkbox" v-model="form.user_is_active" />
              <span>{{ form.user_is_active ? "aktiv" : "deaktiviert" }}</span>
            </label>
          </div>
        </div>
        <div class="kv">
          <div class="k">Membership aktiv?</div>
          <div class="v">
            <label class="toggle">
              <input type="checkbox" v-model="form.membership_is_active" />
              <span>{{ form.membership_is_active ? "aktiv" : "deaktiviert" }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="row gap8">
        <button class="btnPrimary" :disabled="!selectedTenantId || busy.create" @click="createTenantUser">
          {{ busy.create ? "legt an..." : "Hinzufügen" }}
        </button>
        <div class="muted">Legt User an (falls neu) und verknüpft Membership.</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  adminCreateTenantUser,
  adminListTenantUsers,
  adminListTenants,
  adminRoles,
  adminDeleteTenantUser,
  adminUpdateTenantUser,
} from "../api/admin";
import type { TenantOut, TenantUserOut } from "../types";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();

const { toast } = useToast();

const tenants = ref<TenantOut[]>([]);
const roles = ref<string[]>([]);
const tenantUsers = ref<TenantUserOut[]>([]);

const selectedTenantId = ref<string>("");
const q = ref("");

const form = reactive({
  email: "",
  role: "",
  password: "",
  user_is_active: true,
  membership_is_active: true,
});

const busy = reactive({
  tenants: false,
  users: false,
  create: false,
  updateId: "",
});

const currentTenantLabel = computed(() => {
  const t = tenants.value.find((x) => x.id === selectedTenantId.value);
  if (!t) return "-";
  return `${t.name} (${t.slug})`;
});

async function loadTenants() {
  busy.tenants = true;
  try {
    tenants.value = await adminListTenants(props.adminKey, props.actor, { limit: 200, offset: 0 });
    if (!selectedTenantId.value && tenants.value.length > 0) {
      selectedTenantId.value = tenants.value[0].id;
    }
    toast(`Tenants geladen: ${tenants.value.length}`);
    await loadTenantUsers();
  } catch (e: any) {
    toast(`Fehler beim Laden: ${stringifyError(e)}`);
  } finally {
    busy.tenants = false;
  }
}

async function loadRoles() {
  try {
    roles.value = await adminRoles(props.adminKey, props.actor);
    if (!roles.value.includes(form.role)) {
      form.role = roles.value[0] || "";
    }
  } catch (e: any) {
    toast(`Rollen konnten nicht geladen werden: ${stringifyError(e)}`);
  }
}

async function loadTenantUsers() {
  if (!selectedTenantId.value) return;
  busy.users = true;
  try {
    tenantUsers.value = await adminListTenantUsers(props.adminKey, props.actor, selectedTenantId.value, {
      q: q.value || undefined,
      limit: 200,
      offset: 0,
    });
    toast(`Tenant-User geladen: ${tenantUsers.value.length}`);
  } catch (e: any) {
    toast(`Fehler beim Laden: ${stringifyError(e)}`);
  } finally {
    busy.users = false;
  }
}

async function createTenantUser() {
  if (!selectedTenantId.value) {
    toast("Bitte Tenant auswählen");
    return;
  }
  if (!form.email.trim()) {
    toast("E-Mail ist Pflicht");
    return;
  }
  if (!form.role) {
    toast("Rolle auswählen");
    return;
  }
  busy.create = true;
  try {
    const created = await adminCreateTenantUser(props.adminKey, props.actor, selectedTenantId.value, {
      email: form.email.trim(),
      role: form.role,
      password: form.password || null,
      user_is_active: form.user_is_active,
      membership_is_active: form.membership_is_active,
    });
    tenantUsers.value = [created, ...tenantUsers.value];
    toast("Tenant-User angelegt");
    form.email = "";
    form.password = "";
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

async function toggleUser(u: TenantUserOut) {
  await patchTenantUser(u, { user_is_active: !u.user_is_active });
}

async function toggleMembership(u: TenantUserOut) {
  await patchTenantUser(u, { membership_is_active: !u.membership_is_active });
}

async function changeRole(u: TenantUserOut, event: Event) {
  const target = event.target as HTMLSelectElement;
  const role = target.value;
  await patchTenantUser(u, { role });
}

async function resetPassword(u: TenantUserOut) {
  const pw = window.prompt("Neues Passwort für diesen User setzen (mind. 8 Zeichen). Leer zum Abbrechen.");
  if (!pw) return;
  await patchTenantUser(u, { password: pw });
}

async function patchTenantUser(u: TenantUserOut, payload: Record<string, unknown>) {
  busy.updateId = u.membership_id;
  try {
    const updated = await adminUpdateTenantUser(
      props.adminKey,
      props.actor,
      selectedTenantId.value,
      u.membership_id,
      payload
    );
    tenantUsers.value = tenantUsers.value.map((x) => (x.membership_id === updated.membership_id ? updated : x));
    toast("Aktualisiert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.updateId = "";
  }
}

async function deleteTenantUser(u: TenantUserOut) {
  if (!selectedTenantId.value) {
    toast("Bitte Tenant auswählen");
    return;
  }
  const confirmDelete = window.confirm(`Membership für ${u.email} löschen? User bleibt erhalten.`);
  if (!confirmDelete) return;
  busy.updateId = u.membership_id;
  try {
    await adminDeleteTenantUser(props.adminKey, props.actor, selectedTenantId.value, u.membership_id);
    tenantUsers.value = tenantUsers.value.filter((x) => x.membership_id !== u.membership_id);
    toast("Membership gelöscht");
  } catch (e: any) {
    toast(`Fehler beim Löschen: ${stringifyError(e)}`);
  } finally {
    busy.updateId = "";
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

onMounted(async () => {
  await loadRoles();
  await loadTenants();
});
</script>
