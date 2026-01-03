<template>
  <div class="loginShell">
    <div class="card loginCard">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Admin Login</div>
          <div class="cardHint">Admin Key erforderlich für /admin Endpunkte</div>
        </div>
      </div>

      <div class="kvGrid">
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

      <div class="row gap8">
        <button class="btnPrimary" :disabled="busy" @click="login">
          {{ busy ? "prüfe..." : "Login" }}
        </button>
        <div class="muted">Nutzung: /admin/ping mit Key und optional Actor.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { adminPing } from "../api/admin";
import { useToast } from "../composables/useToast";

const emit = defineEmits<{
  (e: "loggedIn", payload: { adminKey: string; actor: string }): void;
}>();

const form = reactive({
  actor: "admin",
  adminKey: "",
});

const busy = ref(false);
const { toast } = useToast();

async function login() {
  if (!form.adminKey.trim()) {
    toast("Bitte Admin Key eingeben");
    return;
  }
  busy.value = true;
  try {
    await adminPing(form.adminKey, form.actor || undefined);
    emit("loggedIn", { adminKey: form.adminKey.trim(), actor: form.actor.trim() || "admin" });
    toast("Login erfolgreich");
  } catch (e: any) {
    toast(asError(e));
  } finally {
    busy.value = false;
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
</style>
