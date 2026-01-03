<template>
  <div class="grid1">
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Diagnostics</div>
          <div class="cardHint">Health Checks, Admin Checks, Snapshot</div>
        </div>
      </header>

      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.id"
          class="tab"
          :class="{ active: tab === t.id }"
          @click="tab = t.id"
        >
          {{ t.label }}
        </button>
      </div>

      <div class="panel" v-if="tab === 'health'">
        <div class="box">
          <div class="meta">
            <div class="muted">Base URL: <span class="mono">{{ baseURL }}</span></div>
            <div class="muted">API: {{ apiStatus }} · DB: {{ dbStatus }}</div>
          </div>

          <div class="rowActions" style="margin-top: 12px;">
            <button class="btnPrimary" :disabled="busy.health" @click="runHealthChecks">
              {{ busy.health ? "prüfe..." : "Health Checks" }}
            </button>
            <button class="btnGhost" :disabled="busy.admin" @click="runAdminChecks">
              {{ busy.admin ? "prüfe..." : "Admin Checks" }}
            </button>
          </div>

          <div class="pillRow" style="margin-top: 12px;">
            <span class="tag" :class="props.apiOk ? 'ok' : 'bad'">API {{ props.apiOk ? "ok" : "down" }}</span>
            <span class="tag" :class="props.dbOk ? 'ok' : 'bad'">DB {{ props.dbOk ? "ok" : "down" }}</span>
            <span class="tag" :class="adminPingOk ? 'ok' : 'bad'">Admin Ping {{ adminPingOk ? "ok" : "down" }}</span>
            <span class="tag" :class="diagOk ? 'ok' : 'bad'">Diagnostics {{ diagOk ? "ok" : "down" }}</span>
          </div>
        </div>

        <div class="box" style="margin-top: 12px;">
          <div class="sectionTitle">Diagnostics Daten</div>
          <pre class="code" style="margin-top: 8px;">{{ diagData ? JSON.stringify(diagData, null, 2) : "noch nicht geladen" }}</pre>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'snapshot'">
        <div class="box">
          <div class="sectionTitle">Snapshot</div>
          <div class="rowActions" style="margin-top: 10px;">
            <button class="btnPrimary" :disabled="busy.snapshot" @click="copySnapshot">
              {{ busy.snapshot ? "kopiere..." : "Snapshot kopieren" }}
            </button>
          </div>
          <pre class="code" style="margin-top: 10px;">{{ prettySnapshot }}</pre>
        </div>
      </div>

      <div class="panel" v-else>
        <div class="box">
          <div class="sectionTitle">Logs (Demo)</div>
          <div class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Zeit</th>
                  <th>Level</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in demoLogs" :key="l.id">
                  <td class="mono">{{ l.ts }}</td>
                  <td><span class="tag neutral">{{ l.level }}</span></td>
                  <td>{{ l.msg }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { platformHealth, platformHealthDb } from "../api/platform";
import { getBaseURL } from "../api/base";
import { adminPing, adminDiagnostics } from "../api/admin";
import { useToast } from "../composables/useToast";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();

/* Nur toast() nutzen, UI wird zentral in App.vue gerendert */
const { toast } = useToast();

type TabId = "health" | "snapshot" | "logs";
const tabs: { id: TabId; label: string }[] = [
  { id: "health", label: "Health" },
  { id: "snapshot", label: "Snapshot" },
  { id: "logs", label: "Logs" },
];
const tab = ref<TabId>("health");

const busy = reactive({
  health: false,
  admin: false,
  snapshot: false,
});

const adminPingOk = ref(false);
const diagOk = ref(false);
const diagData = ref<Record<string, unknown> | null>(null);

const demoLogs = [
  { id: "l1", ts: "11:01:02", level: "info", msg: "health check ok" },
  { id: "l2", ts: "11:02:18", level: "warn", msg: "tenant kunde3 disabled" },
  { id: "l3", ts: "11:04:41", level: "error", msg: "db timeout (demo)" },
];

async function runHealthChecks() {
  busy.health = true;

  try {
    await platformHealth();
    toast("API ok");
  } catch {
    toast("API down");
  }

  try {
    await platformHealthDb();
    toast("DB ok");
  } catch {
    toast("DB down");
  } finally {
    busy.health = false;
  }
}

async function runAdminChecks() {
  if (!props.adminKey) {
    toast("Admin Key fehlt");
    return;
  }

  busy.admin = true;

  try {
    await adminPing(props.adminKey, props.actor);
    adminPingOk.value = true;
  } catch {
    adminPingOk.value = false;
  }

  try {
    diagData.value = await adminDiagnostics(props.adminKey, props.actor);
    diagOk.value = true;
  } catch {
    diagData.value = null;
    diagOk.value = false;
  } finally {
    busy.admin = false;
  }
}

const baseURL = getBaseURL();

const apiStatus = computed(() => (props.apiOk ? "ok" : "down"));
const dbStatus = computed(() => (props.dbOk ? "ok" : "down"));

const snapshot = computed(() => ({
  ts: new Date().toISOString(),
  baseURL,
  apiOk: props.apiOk,
  dbOk: props.dbOk,
  actor: props.actor || null,
  adminKeySet: Boolean(props.adminKey),
  adminPingOk: adminPingOk.value,
  diagnosticsOk: diagOk.value,
  diagnostics: diagData.value,
  ui: { tab: tab.value },
}));

const prettySnapshot = computed(() => JSON.stringify(snapshot.value, null, 2));

async function copySnapshot() {
  busy.snapshot = true;
  try {
    await navigator.clipboard.writeText(prettySnapshot.value);
    toast("Kopiert");
  } catch {
    toast("Kopieren nicht möglich");
  } finally {
    busy.snapshot = false;
  }
}
</script>
