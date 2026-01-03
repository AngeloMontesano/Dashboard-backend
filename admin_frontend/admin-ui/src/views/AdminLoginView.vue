<template>
  <div class="loginShell">
    <div class="card loginCard">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Admin Login</div>
          <div class="cardHint">Admin Key erforderlich für /admin Endpunkte</div>
        </div>
      </div>

      <div class="loginModes">
        <label class="mode">
          <input type="radio" value="key" v-model="mode" />
          <span>Login mit Admin Key</span>
        </label>
        <label class="mode">
          <input type="radio" value="user" v-model="mode" />
          <span>Login mit Benutzer</span>
        </label>
      </div>

      <div v-if="mode === 'key'" class="kvGrid">
        <div class="kv">
          <div class="k">Actor</div>
          <div class="v">
            <input class="input" v-model.trim="form.actor" placeholder="admin" />
          </div>
        </div>
        <div class="kv">
          <div class="k">Admin Key</div>
          <div class="v">
            <input class="input" v-model.trim="form.adminKey" type="password" placeholder="X-Admin-Key" />
          </div>
        </div>
      </div>

      <div v-else class="kvGrid">
        <div class="kv">
          <div class="k">E-Mail</div>
          <div class="v">
            <input class="input" v-model.trim="form.email" placeholder="admin@test.myitnetwork.de" />
          </div>
        </div>
        <div class="kv">
          <div class="k">Passwort</div>
          <div class="v">
            <input class="input" v-model.trim="form.password" type="password" placeholder="Passwort" />
          </div>
        </div>
      </div>

      <div class="row gap8">
        <button class="btnPrimary" :disabled="busy" @click="login">
          {{ busy ? "prüfe..." : "Login" }}
        </button>
        <div class="muted">
          <span v-if="mode === 'key'">Nutzung: /admin/ping mit Key und optional Actor.</span>
          <span v-else>Login mit Admin-Portal User (liefert Admin Key automatisch).</span>
        </div>
      </div>

      <div v-if="status.message" class="status" :class="status.type">
        {{ status.message }}
      </div>

      <div v-if="status.message" class="status" :class="status.type">
        {{ status.message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { adminPing, adminLoginWithCredentials } from "../api/admin";
import { getBaseURL } from "../api/base";
import { useToast } from "../composables/useToast";

const emit = defineEmits<{
  (e: "loggedIn", payload: { adminKey: string; actor: string }): void;
}>();

const form = reactive({
  actor: "admin",
  adminKey: "",
  email: "",
  password: "",
});

const busy = ref(false);
const mode = ref<"key" | "user">("key");
const { toast } = useToast();
const status = reactive({
  message: "",
  type: "",
});

async function login() {
  if (mode.value === "key" && !form.adminKey.trim()) {
    toast("Bitte Admin Key eingeben");
    status.message = "Bitte Admin Key eingeben";
    status.type = "error";
    return;
  }
  if (mode.value === "user" && (!form.email.trim() || !form.password.trim())) {
    toast("Bitte E-Mail und Passwort eingeben");
    status.message = "Bitte E-Mail und Passwort eingeben";
    status.type = "error";
    return;
  }
  busy.value = true;
  status.message = "Prüfe Zugang...";
  status.type = "info";
  console.info("[admin-login] Start", {
    apiBase: getBaseURL(),
    host: window.location.host,
    mode: mode.value,
    actor: mode.value === "key" ? form.actor || "admin" : form.email || "user",
  });
  try {
    if (mode.value === "key") {
      await adminPing(form.adminKey, form.actor || undefined);
      console.info("[admin-login] Erfolg", { actor: form.actor || "admin" });
      emit("loggedIn", { adminKey: form.adminKey.trim(), actor: form.actor.trim() || "admin" });
    } else {
      const res = await adminLoginWithCredentials(form.email.trim(), form.password.trim());
      const actor = res.actor || form.email.trim();
      console.info("[admin-login] Erfolg (user)", { actor });
      emit("loggedIn", { adminKey: res.admin_key, actor });
    }
    toast("Login erfolgreich");
    status.message = "Login erfolgreich. Admin Portal wird geladen...";
    status.type = "ok";
  } catch (e: any) {
    toast(asError(e));
    status.message = asError(e);
    status.type = "error";
    console.error("[admin-login] Fehler", e);
  } finally {
    busy.value = false;
  }
}

function asError(e: any): string {
  if (!e) return "unknown";
  if (typeof e === "string") return e;
  if (e?.response?.status === 401) return "401 Unauthorized – bitte Admin Key prüfen";
  if (e?.response?.data?.detail) return JSON.stringify(e.response.data.detail);
  if (e?.message === "Network Error") return `Network Error (API ${getBaseURL()})`;
  if (e?.message) return e.message;
  try {
    return JSON.stringify(e);
  } catch {
    return String(e);
  }
}
</script>

<style scoped>
.loginShell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-muted);
}
.loginCard {
  width: 420px;
}
.loginModes{
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}
.mode{
  display: inline-flex;
  gap: 6px;
  align-items: center;
  font-size: 13px;
}
.status{
  margin-top: 10px;
  font-size: 13px;
}
.status.info{ color: var(--muted); }
.status.ok{ color: var(--ok); }
.status.error{ color: var(--bad); }
</style>
