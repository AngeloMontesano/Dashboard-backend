<template>
  <UiPage>
    <div class="auth-shell">
      <div class="section auth-card stack">
        <div class="stack-sm">
          <div class="section-title">Admin Login</div>
          <div class="text-muted text-small">Admin Key erforderlich für /admin Endpunkte</div>
        </div>

        <div class="stack-sm">
          <div class="field-label">Login-Modus</div>
          <div class="action-row">
            <label class="field--inline">
              <input type="radio" value="key" v-model="mode" />
              <span>Login mit Admin Key</span>
            </label>
            <label class="field--inline">
              <input type="radio" value="user" v-model="mode" />
              <span>Login mit Benutzer</span>
            </label>
          </div>
        </div>

        <div v-if="mode === 'key'" class="kv-grid">
          <div class="kv">
            <div class="kv__label">Actor</div>
            <div class="kv__value">
              <input class="input" v-model.trim="form.actor" placeholder="admin" />
            </div>
          </div>
          <div class="kv">
            <div class="kv__label">Admin Key</div>
            <div class="kv__value">
              <input class="input" v-model.trim="form.adminKey" type="password" placeholder="X-Admin-Key" />
            </div>
          </div>
        </div>

        <div v-else class="kv-grid">
          <div class="kv">
            <div class="kv__label">E-Mail</div>
            <div class="kv__value">
              <input class="input" v-model.trim="form.email" placeholder="admin@test.myitnetwork.de" />
            </div>
          </div>
          <div class="kv">
            <div class="kv__label">Passwort</div>
            <div class="kv__value">
              <input class="input" v-model.trim="form.password" type="password" placeholder="Passwort" />
            </div>
          </div>
        </div>

        <div class="action-row">
          <button class="btnPrimary" :disabled="busy" @click="login">
            {{ busy ? "prüfe..." : "Login" }}
          </button>
          <div class="text-muted text-small">
            <span v-if="mode === 'key'">Nutzung: /admin/ping mit Key und optional Actor.</span>
            <span v-else>Login mit Admin-Portal User (liefert Admin Key automatisch).</span>
          </div>
        </div>

        <div v-if="status.message" class="text-small" :class="statusClass">
          {{ status.message }}
        </div>
      </div>
    </div>
  </UiPage>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { adminPing, adminLoginWithCredentials } from "../api/admin";
import { getBaseURL } from "../api/base";
import { useToast } from "../composables/useToast";
import UiPage from "../components/ui/UiPage.vue";

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

const statusClass = computed(() => {
  if (status.type === "ok") return "text-success";
  if (status.type === "error") return "text-danger";
  return "text-info";
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
