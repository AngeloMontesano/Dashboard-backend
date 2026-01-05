<template>
  <UiPage>
    <UiSection title="Operations" subtitle="Health, Audit, Snapshots, Logs">
      <template #actions>
        <button class="btnGhost" @click="refreshActiveTab" :disabled="busy.health || busy.admin || busy.list">
          {{ busy.health || busy.admin || busy.list ? "..." : "Aktualisieren" }}
        </button>
      </template>

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
        <div class="box stack-sm">
          <div class="sectionTitle">Übersicht</div>
          <div class="text-muted text-small">Base URL: <span class="mono">{{ baseURL }}</span></div>
          <div class="text-muted text-small">API: {{ apiStatus }} · DB: {{ dbStatus }}</div>

          <div class="pill-row mt-6">
            <span class="tag" :class="props.apiOk ? 'ok' : 'bad'">API {{ props.apiOk ? "ok" : "down" }}</span>
            <span class="tag" :class="props.dbOk ? 'ok' : 'bad'">DB {{ props.dbOk ? "ok" : "down" }}</span>
            <span class="tag" :class="adminPingOk ? 'ok' : 'bad'">Admin Ping {{ adminPingOk ? "ok" : "down" }}</span>
            <span class="tag" :class="diagOk ? 'ok' : 'bad'">Diagnostics {{ diagOk ? "ok" : "down" }}</span>
          </div>

          <div class="text-muted text-small mt-6">
            Wähle oben einen Tab für Details oder Checks. Health und Admin Checks lassen sich über „Aktualisieren“ erneut ausführen.
          </div>
        </div>

        <div class="box stack-sm mt-6">
          <div class="sectionTitle">Tenant Routing Debug</div>
          <div class="kv-grid">
            <div class="kv">
              <div class="kv__label">Host</div>
              <div class="kv__value mono">{{ currentHost }}</div>
            </div>
            <div class="kv">
              <div class="kv__label">X-Forwarded-Host</div>
              <div class="kv__value mono">{{ forwardedHost || "unbekannt" }}</div>
            </div>
            <div class="kv">
              <div class="kv__label">Tenant (UI)</div>
              <div class="kv__value">{{ tenantLabel }}</div>
            </div>
            <div class="kv">
              <div class="kv__label">API Base</div>
              <div class="kv__value mono">{{ baseURL }}</div>
            </div>
            <div class="kv">
              <div class="kv__label">Browser Origin</div>
              <div class="kv__value mono">{{ windowOrigin }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'health'">
        <div class="box stack-sm">
          <div class="text-muted text-small">Base URL: <span class="mono">{{ baseURL }}</span></div>
          <div class="text-muted text-small">API: {{ apiStatus }} · DB: {{ dbStatus }}</div>

          <div class="action-row mt-6">
            <button class="btnPrimary" :disabled="busy.health" @click="runHealthChecks">
              {{ busy.health ? "prüfe..." : "Health Checks" }}
            </button>
            <button class="btnGhost" :disabled="busy.admin" @click="runAdminChecks">
              {{ busy.admin ? "prüfe..." : "Admin Checks" }}
            </button>
          </div>

          <div class="pill-row mt-6">
            <span class="tag" :class="props.apiOk ? 'ok' : 'bad'">API {{ props.apiOk ? "ok" : "down" }}</span>
            <span class="tag" :class="props.dbOk ? 'ok' : 'bad'">DB {{ props.dbOk ? "ok" : "down" }}</span>
            <span class="tag" :class="adminPingOk ? 'ok' : 'bad'">Admin Ping {{ adminPingOk ? "ok" : "down" }}</span>
            <span class="tag" :class="diagOk ? 'ok' : 'bad'">Diagnostics {{ diagOk ? "ok" : "down" }}</span>
          </div>
        </div>

        <div class="box stack-sm mt-6">
          <div class="sectionTitle">Diagnostics Daten</div>
          <pre class="code-block mono">{{ diagData ? JSON.stringify(diagData, null, 2) : "noch nicht geladen" }}</pre>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'audit'">
        <div class="action-row">
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

        <div class="stack-sm text-muted text-small mt-4">
          <div>Einträge: {{ rows.length }}</div>
          <div>
            Offset: <span class="mono">{{ filters.offset }}</span>
            · Limit: <span class="mono">{{ filters.limit }}</span>
          </div>
        </div>

        <AuditTable
          :rows="rows"
          :busy="busy.list"
          @open="openDrawer"
        />

        <div class="action-row mt-6">
          <button class="btnGhost" @click="prevPage" :disabled="busy.list || filters.offset === 0">Prev</button>
          <button class="btnGhost" @click="nextPage" :disabled="busy.list || rows.length < filters.limit">Next</button>

          <div class="text-muted text-small push-right">
            Tipp: Doppelklick auf Payload kopiert JSON im Drawer.
          </div>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'snapshot'">
        <div class="box stack-sm">
          <div class="sectionTitle">Snapshot</div>
          <div class="action-row">
            <button class="btnPrimary" :disabled="busy.snapshot" @click="createSnapshot">
              {{ busy.snapshot ? "speichere..." : "Snapshot erstellen" }}
            </button>
            <div class="text-muted text-small push-right">max. 20 Snapshots, lokal gespeichert</div>
          </div>

          <div class="tableWrap mt-4" v-if="snapshots.length">
            <table class="table">
              <thead>
                <tr>
                  <th>Zeit</th>
                  <th>Tenant</th>
                  <th>Status</th>
                  <th class="right">Aktion</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in snapshots" :key="s.id">
                  <td class="mono">{{ s.ts }}</td>
                  <td>{{ s.tenant?.slug || "—" }}</td>
                  <td>
                    <span class="tag" :class="s.status.apiOk ? 'ok' : 'bad'">API {{ s.status.apiOk ? "ok" : "down" }}</span>
                    <span class="tag" :class="s.status.dbOk ? 'ok' : 'bad'">DB {{ s.status.dbOk ? "ok" : "down" }}</span>
                    <span class="tag" :class="s.status.diagOk ? 'ok' : 'bad'">Diag {{ s.status.diagOk ? "ok" : "down" }}</span>
                  </td>
                  <td class="right">
                    <button class="btnGhost" @click="downloadSnapshot(s)">JSON herunterladen</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="text-muted text-small" v-else>Noch keine Snapshots gespeichert.</div>
        </div>

        <div class="box stack-sm mt-6" v-if="latestSnapshotJson">
          <div class="sectionTitle">Letzter Snapshot</div>
          <pre class="code-block mono">{{ latestSnapshotJson }}</pre>
        </div>
      </div>

      <div class="panel" v-else>
        <div class="box stack-sm">
          <div class="sectionTitle">Logs (Demo)</div>
          <div class="action-row mt-4">
            <button class="btnPrimary" :disabled="busy.logs" @click="loadLogs">
              {{ busy.logs ? "lade..." : "Letzte Logs laden" }}
            </button>
            <div class="text-muted text-small push-right">TODO: Backend Endpoint anbinden</div>
          </div>
          <pre class="code-block mono">{{ logText }}</pre>
        </div>
      </div>
    </UiSection>

    <AuditDrawer
      :open="drawer.open"
      :row="drawer.row"
      @close="closeDrawer"
    />
  </UiPage>
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
import { AuditDisplayRow, formatLocal, summarizePayload, toDisplayRow } from "../components/audit/format";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";

type OperationsTab = "overview" | "health" | "audit" | "snapshot" | "logs";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  initialTab?: OperationsTab;
  tenant?: { id: string; slug: string; name: string } | null;
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
  logs: false,
});

const adminPingOk = ref(false);
const diagOk = ref(false);
const diagData = ref<Record<string, any> | null>(null);

const drawer = reactive({
  open: false,
  row: null as AuditDisplayRow | null,
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

const rows = ref<AuditDisplayRow[]>([]);
const auditLoadedOnce = ref(false);

const baseURL = getBaseURL();
const windowOrigin = window.location.origin;
const currentHost = window.location.host;
const forwardedHost = computed(() => extractForwardedHost(diagData.value));
const tenantLabel = computed(() => props.tenant?.slug || "kein Tenant ausgewählt");

const apiStatus = computed(() => (props.apiOk ? "ok" : "down"));
const dbStatus = computed(() => (props.dbOk ? "ok" : "down"));

type SnapshotEntry = {
  id: string;
  ts: string;
  baseURL: string;
  actor: string | null;
  tenant: { id: string; slug: string; name: string } | null;
  status: { apiOk: boolean; dbOk: boolean; diagOk: boolean; adminPingOk: boolean };
  diagnostics: Record<string, any> | null;
};

const SNAPSHOT_KEY = "adminOperationsSnapshots";
const snapshots = ref<SnapshotEntry[]>(loadSnapshots());
const latestSnapshotJson = computed(() => {
  if (!snapshots.value.length) return "";
  return JSON.stringify(snapshots.value[0], null, 2);
});

const logLines = ref<string[]>([]);
const logText = computed(() => (logLines.value.length ? logLines.value.join("\n") : "Noch keine Logs geladen."));

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

    rows.value = res.map(toDisplayRow);
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

function openDrawer(row: AuditDisplayRow) {
  drawer.open = true;
  drawer.row = row;
}

function closeDrawer() {
  drawer.open = false;
  drawer.row = null;
}

function createSnapshot() {
  busy.snapshot = true;
  const entry: SnapshotEntry = {
    id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
    ts: formatLocal(new Date().toISOString()),
    baseURL,
    actor: props.actor || null,
    tenant: props.tenant ?? null,
    status: {
      apiOk: props.apiOk,
      dbOk: props.dbOk,
      diagOk: diagOk.value,
      adminPingOk: adminPingOk.value,
    },
    diagnostics: diagData.value,
  };

  snapshots.value = [entry, ...snapshots.value].slice(0, 20);
  persistSnapshots();
  busy.snapshot = false;
  toast("Snapshot gespeichert");
}

function downloadSnapshot(entry: SnapshotEntry) {
  const blob = new Blob([JSON.stringify(entry, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `snapshot-${entry.ts.replace(/[^0-9A-Za-z]/g, "_")}.json`;
  a.click();
  URL.revokeObjectURL(url);
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

function loadLogs() {
  busy.logs = true;
  // TODO: Backend Endpoint anbinden, derzeit Demo-Daten
  logLines.value = [
    `${new Date().toISOString()} [info] health check ok`,
    `${new Date().toISOString()} [warn] tenant routing fallback ${tenantLabel.value}`,
    `${new Date().toISOString()} [info] diagnostics ${diagOk.value ? "ok" : "unbekannt"}`,
  ];
  busy.logs = false;
}

function loadSnapshots(): SnapshotEntry[] {
  try {
    const raw = localStorage.getItem(SNAPSHOT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistSnapshots() {
  localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(snapshots.value));
}

function extractForwardedHost(diag: Record<string, any> | null) {
  if (!diag) return "";
  const headers = diag.request_headers || diag.headers || {};
  return headers["x-forwarded-host"] || headers["X-Forwarded-Host"] || diag.x_forwarded_host || "";
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
