<template>
  <div class="grid1">
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Operations</div>
          <div class="cardHint">Health, Audit, Snapshots, Logs</div>
        </div>

        <div class="cardHeaderActions">
          <button class="btnGhost" @click="refreshActiveTab" :disabled="busy.health || busy.admin || busy.list">
            {{ busy.health || busy.admin || busy.list ? "..." : "Aktualisieren" }}
          </button>
        </div>
      </header>

      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.id"
          class="tab"
          :class="{ active: tab === t.id }"
          @click="setTab(t.id)"
        >
          {{ t.label }}
        </button>
      </div>

      <div class="panel" v-if="tab === 'overview'">
        <div class="box">
          <div class="sectionTitle">Übersicht</div>
          <div class="meta">
            <div class="muted">Base URL: <span class="mono">{{ baseURL }}</span></div>
            <div class="muted">API: {{ apiStatus }} · DB: {{ dbStatus }}</div>
          </div>

          <div class="pillRow" style="margin-top: 12px;">
            <span class="tag" :class="props.apiOk ? 'ok' : 'bad'">API {{ props.apiOk ? "ok" : "down" }}</span>
            <span class="tag" :class="props.dbOk ? 'ok' : 'bad'">DB {{ props.dbOk ? "ok" : "down" }}</span>
            <span class="tag" :class="adminPingOk ? 'ok' : 'bad'">Admin Ping {{ adminPingOk ? "ok" : "down" }}</span>
            <span class="tag" :class="diagOk ? 'ok' : 'bad'">Diagnostics {{ diagOk ? "ok" : "down" }}</span>
          </div>

          <div class="muted" style="margin-top: 12px;">
            Wähle oben einen Tab für Details oder Checks. Health und Admin Checks lassen sich über „Aktualisieren“ erneut ausführen.
          </div>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'health'">
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

      <div class="panel" v-else-if="tab === 'audit'">
        <div class="rowActions" style="margin-bottom: 12px;">
          <button class="btnGhost" @click="resetFilters" :disabled="busy.list">Reset</button>
          <button class="btnPrimary" @click="loadAudit" :disabled="busy.list">
            {{ busy.list ? "lade..." : "Suchen" }}
          </button>
        </div>

        <AuditFiltersBar
          v-model:actor="filters.actor"
          v-model:action="filters.action"
          v-model:entityType="filters.entity_type"
          v-model:entityId="filters.entity_id"
          v-model:createdFrom="filters.created_from"
          v-model:createdTo="filters.created_to"
          v-model:limit="filters.limit"
          :busy="busy.list"
          @enter="loadAudit"
        />

        <div class="meta">
          <div class="muted">Einträge: {{ rows.length }}</div>
          <div class="muted">
            Offset: <span class="mono">{{ filters.offset }}</span>
            Limit: <span class="mono">{{ filters.limit }}</span>
          </div>
        </div>

        <AuditTable
          :rows="rows"
          :busy="busy.list"
          @open="openDrawer"
        />

        <div class="rowActions" style="margin-top: 12px;">
          <button class="btnGhost" @click="prevPage" :disabled="busy.list || filters.offset === 0">Prev</button>
          <button class="btnGhost" @click="nextPage" :disabled="busy.list || rows.length < filters.limit">Next</button>

          <div class="muted" style="margin-left: auto;">
            Tipp: Doppelklick auf Payload kopiert JSON im Drawer.
          </div>
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

    <AuditDrawer
      :open="drawer.open"
      :row="drawer.row"
      @close="closeDrawer"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { platformHealth, platformHealthDb } from "../api/platform";
import { getBaseURL } from "../api/base";
import { adminPing, adminDiagnostics, adminGetAudit } from "../api/admin";
import AuditFiltersBar from "../components/audit/AuditFiltersBar.vue";
import AuditTable from "../components/audit/AuditTable.vue";
import AuditDrawer from "../components/audit/AuditDrawer.vue";
import type { AuditOut } from "../types";
import { useToast } from "../composables/useToast";

type OperationsTab = "overview" | "health" | "audit" | "snapshot" | "logs";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  initialTab?: OperationsTab;
}>();

const emit = defineEmits<{
  (e: "tabChange", tab: OperationsTab): void;
}>();

const { toast } = useToast();

const tabs: { id: OperationsTab; label: string }[] = [
  { id: "overview", label: "Übersicht" },
  { id: "health", label: "Health" },
  { id: "audit", label: "Audit Log" },
  { id: "snapshot", label: "Snapshots" },
  { id: "logs", label: "Logs" },
];
const tab = ref<OperationsTab>("overview");

const busy = reactive({
  health: false,
  admin: false,
  snapshot: false,
  list: false,
});

const adminPingOk = ref(false);
const diagOk = ref(false);
const diagData = ref<Record<string, unknown> | null>(null);

const drawer = reactive({
  open: false,
  row: null as AuditOut | null,
});

const filters = reactive({
  actor: "" as string,
  action: "" as string,
  entity_type: "" as string,
  entity_id: "" as string,
  created_from: "" as string,
  created_to: "" as string,
  limit: 100,
  offset: 0,
});

const rows = ref<AuditOut[]>([]);
const auditLoadedOnce = ref(false);

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

async function loadAudit() {
  if (!props.adminKey) {
    toast("Admin Key fehlt");
    return;
  }

  busy.list = true;
  try {
    const res = await adminGetAudit(props.adminKey, props.actor, {
      actor: filters.actor || undefined,
      action: filters.action || undefined,
      entity_type: filters.entity_type || undefined,
      entity_id: filters.entity_id || undefined,
      created_from: filters.created_from || undefined,
      created_to: filters.created_to || undefined,
      limit: filters.limit,
      offset: filters.offset,
    });

    rows.value = res;
    auditLoadedOnce.value = true;
    toast(`Audit geladen: ${res.length}`);
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.list = false;
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

function nextPage() {
  filters.offset = filters.offset + filters.limit;
  loadAudit();
}

function prevPage() {
  filters.offset = Math.max(0, filters.offset - filters.limit);
  loadAudit();
}

function resetFilters() {
  filters.actor = "";
  filters.action = "";
  filters.entity_type = "";
  filters.entity_id = "";
  filters.created_from = "";
  filters.created_to = "";
  filters.limit = 100;
  filters.offset = 0;
  toast("Filter zurückgesetzt");
}

function openDrawer(row: AuditOut) {
  drawer.open = true;
  drawer.row = row;
}

function closeDrawer() {
  drawer.open = false;
  drawer.row = null;
}

function refreshActiveTab() {
  if (tab.value === "health") {
    runHealthChecks();
    runAdminChecks();
    return;
  }

  if (tab.value === "audit") {
    loadAudit();
  }
}

function setTab(next: OperationsTab) {
  tab.value = next;
  emit("tabChange", next);

  if (next === "audit" && !auditLoadedOnce.value) {
    loadAudit();
  }
}

function applyInitialTab(next?: OperationsTab | null) {
  if (!next || next === tab.value) return;
  tab.value = next;
  if (next === "audit" && !auditLoadedOnce.value) {
    loadAudit();
  }
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      runAdminChecks();
    }
  },
  { immediate: true }
);

watch(
  () => props.initialTab,
  (next) => applyInitialTab(next),
  { immediate: true }
);
</script>
