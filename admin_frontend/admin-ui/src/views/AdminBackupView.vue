<template>
  <UiPage>
    <UiSection title="Backup" subtitle="Tenant-spezifische Exporte & Restore (Schema-Introspektion + tenant_id-Pflicht)">
      <BackupContextCard :tenant="tenant" />

      <BackupMonitoringOverview :overview="overviewItems" />

      <BackupGuidancePanel />

      <BackupMonitoringDetails
        :lastExport="lastExport"
        :lastRestore="lastRestore"
        :validation="validationSummary"
        :jobsSummary="jobsSummary"
        :retention="retentionSummary"
        :jobs="jobsTable"
      />

      <BackupChecksCard />

      <div class="table-card">
        <div class="table-card__header">
          <div class="stack-sm">
            <div class="tableTitle">Historie / Audit</div>
            <div class="text-muted text-small">Alle Backup-Aktionen mit Filter nach Aktion und Zeitraum.</div>
          </div>
          <div class="row gap8">
            <button class="btnGhost small" type="button" :disabled="busy.history" @click="resetHistoryFilters">
              Reset
            </button>
            <button class="btnPrimary small" type="button" :disabled="busy.history" @click="applyHistoryFilters">
              {{ busy.history ? "lade..." : "Filtern" }}
            </button>
          </div>
        </div>

        <div class="row gap8 mt-6">
          <label class="text-small">
            Aktion
            <select class="input" v-model="historyFilters.action">
              <option value="">Alle</option>
              <option value="backup.create">Backup erstellt</option>
              <option value="backup.restore">Backup Restore</option>
            </select>
          </label>
          <label class="text-small">
            Von
            <input class="input" type="date" v-model="historyFilters.createdFrom" />
          </label>
          <label class="text-small">
            Bis
            <input class="input" type="date" v-model="historyFilters.createdTo" />
          </label>
        </div>

        <div class="tableWrap mt-6" v-if="historyRows.length">
          <table class="table">
            <thead>
              <tr>
                <th>Zeit</th>
                <th>Aktion</th>
                <th>Backup-ID</th>
                <th>Actor</th>
                <th class="right">Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in historyRows" :key="entry.id">
                <td class="mono">{{ entry.createdAt }}</td>
                <td>{{ entry.actionLabel }}</td>
                <td class="mono">{{ entry.entityId }}</td>
                <td class="mono">{{ entry.actor }}</td>
                <td class="right text-muted text-small">{{ entry.details }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="text-muted text-small" v-else>Keine Audit-Einträge gefunden.</div>
      </div>

      <BackupArchivePanel
        :backups="backups"
        :selectedId="selectedId"
        :restoreStatus="restoreStatus"
        :busy="busy.action"
        @select="selectBackup"
        @downloadZip="downloadZip"
        @downloadFile="downloadFile"
        @restore="restoreBackup"
        @createTenantBackup="createTenantBackup"
        @createAllBackups="createAllBackups"
      />
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import BackupContextCard from "../components/backup/BackupContextCard.vue";
import BackupMonitoringOverview from "../components/backup/BackupMonitoringOverview.vue";
import BackupMonitoringDetails from "../components/backup/BackupMonitoringDetails.vue";
import BackupGuidancePanel from "../components/backup/BackupGuidancePanel.vue";
import BackupChecksCard from "../components/backup/BackupChecksCard.vue";
import BackupArchivePanel from "../components/backup/BackupArchivePanel.vue";
import {
  adminBackupHistory,
  adminCreateAllBackups,
  adminCreateTenantBackup,
  adminDownloadBackup,
  adminDownloadBackupFile,
  adminListBackupJobs,
  adminListBackups,
  adminRestoreBackup,
  BackupJobEntry,
} from "../api/admin";
import { formatLocal } from "../components/audit/format";
import { useToast } from "../composables/useToast";
import type { AuditOut } from "../types";

type BackupFile = {
  name: string;
  sizeBytes: number;
  sizeLabel: string;
};

type BackupEntry = {
  id: string;
  scope: string;
  tenantId: string | null;
  tenantSlug: string | null;
  createdAtRaw: string;
  createdAt: string;
  restoredAt?: string | null;
  status: "ok" | "error";
  statusLabel: string;
  name: string;
  files: BackupFile[];
};

const props = defineProps<{
  tenant: {
    id: string;
    name: string;
    slug: string;
  };
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();

const backups = ref<BackupEntry[]>([]);
const jobs = ref<BackupJobEntry[]>([]);
const history = ref<AuditOut[]>([]);
const historyLatest = ref<AuditOut[]>([]);
const selectedId = ref("");
const restoreStatus = ref("");
const busy = reactive({
  loading: false,
  action: false,
  history: false,
});
const historyFilters = reactive({
  action: "" as string,
  createdFrom: "" as string,
  createdTo: "" as string,
});
const hadActiveJobs = ref(false);
let pollTimer: number | null = null;

const selectedBackup = computed(() => backups.value.find((entry) => entry.id === selectedId.value) || null);

function mapBackupEntry(entry: {
  id: string;
  scope: string;
  tenant_id: string | null;
  tenant_slug: string | null;
  created_at: string;
  status: string;
  restored_at?: string | null;
  files: { name: string; size_bytes: number; size_label: string }[];
}): BackupEntry {
  const createdAtLocal = formatLocal(entry.created_at);
  const labelScope = entry.scope === "all" ? "Alle Tenants" : entry.tenant_slug || entry.tenant_id || "Tenant";
  return {
    id: entry.id,
    scope: entry.scope,
    tenantId: entry.tenant_id,
    tenantSlug: entry.tenant_slug,
    createdAtRaw: entry.created_at,
    createdAt: createdAtLocal,
    restoredAt: entry.restored_at ?? null,
    status: entry.status === "ok" ? "ok" : "error",
    statusLabel: entry.status === "ok" ? "OK" : "Fehler",
    name: `${labelScope} · ${createdAtLocal}`,
    files: entry.files.map((file) => ({
      name: file.name,
      sizeBytes: file.size_bytes,
      sizeLabel: file.size_label,
    })),
  };
}

async function loadBackups() {
  const backupItems = await adminListBackups(
    props.adminKey,
    props.actor || undefined,
    props.tenant?.id ? { tenant_id: props.tenant.id } : undefined
  );
  backups.value = backupItems
    .map(mapBackupEntry)
    .sort((a, b) => new Date(b.createdAtRaw).getTime() - new Date(a.createdAtRaw).getTime());
  if (!selectedId.value && backups.value.length) {
    selectedId.value = backups.value[0].id;
  }
}

async function loadJobs() {
  const jobItems = await adminListBackupJobs(props.adminKey, props.actor || undefined);
  jobs.value = jobItems;
  const hasActiveJobs = jobItems.some((job) => ["queued", "running"].includes(job.status));
  if (hadActiveJobs.value && !hasActiveJobs) {
    await loadBackups();
    await loadHistoryLatest();
  }
  hadActiveJobs.value = hasActiveJobs;
  updatePolling(hasActiveJobs);
}

function buildHistoryParams() {
  const created_from = historyFilters.createdFrom ? toIsoStart(historyFilters.createdFrom) : undefined;
  const created_to = historyFilters.createdTo ? toIsoEnd(historyFilters.createdTo) : undefined;
  return {
    action: historyFilters.action || undefined,
    created_from,
    created_to,
    limit: 100,
    offset: 0,
  };
}

async function loadHistory() {
  busy.history = true;
  try {
    const historyItems = await adminBackupHistory(props.adminKey, props.actor || undefined, buildHistoryParams());
    history.value = [...historyItems].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch (error) {
    console.error("[backup] history load failed", error);
    toast("Audit-Historie konnte nicht geladen werden.", "error");
  } finally {
    busy.history = false;
  }
}

async function loadHistoryLatest() {
  const historyItems = await adminBackupHistory(props.adminKey, props.actor || undefined, { limit: 100, offset: 0 });
  historyLatest.value = [...historyItems].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

async function loadData() {
  if (!props.adminKey) return;
  busy.loading = true;
  try {
    await Promise.all([loadBackups(), loadJobs(), loadHistory(), loadHistoryLatest()]);
  } catch (error) {
    console.error("[backup] load failed", error);
    toast("Backup-Daten konnten nicht geladen werden.", "error");
  } finally {
    busy.loading = false;
  }
}

function applyHistoryFilters() {
  loadHistory();
}

function resetHistoryFilters() {
  historyFilters.action = "";
  historyFilters.createdFrom = "";
  historyFilters.createdTo = "";
  applyHistoryFilters();
}

function selectBackup(id: string) {
  selectedId.value = id;
  restoreStatus.value = "";
}

async function createTenantBackup() {
  if (!props.adminKey) return;
  if (!props.tenant?.id) {
    toast("Kein Tenant gewählt.", "warning");
    return;
  }
  busy.action = true;
  try {
    const created = await adminCreateTenantBackup(props.adminKey, props.actor || undefined, props.tenant.id);
    const mapped = mapBackupEntry(created);
    backups.value = [mapped, ...backups.value];
    selectedId.value = mapped.id;
    toast("Tenant-Backup erstellt.", "success");
  } catch (error) {
    console.error("[backup] create tenant backup failed", error);
    toast("Tenant-Backup konnte nicht erstellt werden.", "error");
  } finally {
    busy.action = false;
  }
}

async function createAllBackups() {
  if (!props.adminKey) return;
  busy.action = true;
  try {
    const job = await adminCreateAllBackups(props.adminKey, props.actor || undefined);
    jobs.value = [job, ...jobs.value];
    toast("Batch-Backup Job gestartet.", "success");
    updatePolling(true);
  } catch (error) {
    console.error("[backup] create all backups failed", error);
    toast("Batch-Backup konnte nicht gestartet werden.", "error");
  } finally {
    busy.action = false;
  }
}

async function restoreBackup(backup: BackupEntry) {
  if (!props.adminKey) return;
  const confirmed = window.confirm(`Restore für ${backup.name} starten?`);
  if (!confirmed) return;
  busy.action = true;
  restoreStatus.value = `Restore für ${backup.name} läuft...`;
  try {
    await adminRestoreBackup(props.adminKey, props.actor || undefined, backup.id);
    toast(`Restore gestartet: ${backup.name}`, "info");
    await loadData();
    restoreStatus.value = `Restore abgeschlossen: ${backup.name}`;
  } catch (error) {
    console.error("[backup] restore failed", error);
    restoreStatus.value = "";
    toast("Restore fehlgeschlagen.", "error");
  } finally {
    busy.action = false;
  }
}

async function downloadZip(backup: BackupEntry) {
  if (!props.adminKey) return;
  try {
    const blob = await adminDownloadBackup(props.adminKey, props.actor || undefined, backup.id);
    saveBlob(blob, `${backup.id}.zip`);
  } catch (error) {
    console.error("[backup] download zip failed", error);
    toast("ZIP-Download fehlgeschlagen.", "error");
  }
}

async function downloadFile(payload: { backup: BackupEntry; file: BackupFile }) {
  if (!props.adminKey) return;
  try {
    const blob = await adminDownloadBackupFile(
      props.adminKey,
      props.actor || undefined,
      payload.backup.id,
      payload.file.name
    );
    saveBlob(blob, payload.file.name);
  } catch (error) {
    console.error("[backup] download file failed", error);
    toast("Datei-Download fehlgeschlagen.", "error");
  }
}

function saveBlob(blob: Blob, filename: string) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

const lastBackup = computed(() => backups.value[0] || null);
const lastRestoreEntry = computed(
  () => historyLatest.value.find((entry) => entry.action === "backup.restore") || null
);

const overviewItems = computed(() => {
  const errorCount =
    backups.value.filter((entry) => entry.status !== "ok").length +
    jobs.value.filter((job) => job.status === "failed").length;
  return [
    {
      label: "Letzter Export",
      value: lastBackup.value ? lastBackup.value.createdAt : "Keine Daten",
      status: lastBackup.value ? "ok" : "warn",
    },
    {
      label: "Letzter Restore",
      value: lastRestoreEntry.value ? formatLocal(lastRestoreEntry.value.created_at) : "Keine Daten",
      status: lastRestoreEntry.value ? "ok" : "warn",
    },
    {
      label: "Jobs",
      value: jobs.value.length ? `${jobs.value.length} Job(s)` : "Keine Jobs",
      status: jobs.value.length ? "ok" : "warn",
    },
    {
      label: "Offene Fehler",
      value: String(errorCount),
      status: errorCount === 0 ? "ok" : "bad",
    },
    {
      label: "Retention",
      value: backups.value.length ? "Serverseitig" : "Unbekannt",
      status: backups.value.length ? "ok" : "warn",
    },
  ];
});

const lastExport = computed(() => ({
  title: lastBackup.value ? `${lastBackup.value.statusLabel}` : "Keine Daten",
  detail: lastBackup.value ? `Zeit: ${lastBackup.value.createdAt}` : "Noch kein Backup vorhanden.",
}));

const lastRestore = computed(() => ({
  title: lastRestoreEntry.value ? "OK" : "Keine Daten",
  detail: lastRestoreEntry.value
    ? `Zeit: ${formatLocal(lastRestoreEntry.value.created_at)}`
    : "Noch kein Restore protokolliert.",
}));

const validationSummary = computed(() => ({
  title: "Automatisch beim Restore",
  detail: "Checksums, Counts und FK-Checks werden serverseitig geprüft.",
}));

const jobsSummary = computed(() => ({
  title: jobs.value.length ? `${jobs.value.length} Job(s)` : "Keine Jobs",
  detail: jobs.value.length ? "Batch-Jobs werden serverseitig verarbeitet." : "Kein aktiver Batch-Job.",
}));

const retentionSummary = computed(() => ({
  title: "Serverseitig",
  detail: backups.value.length ? "Retention-Konfiguration erfolgt im Backend." : "Keine Backups vorhanden.",
}));

const jobsTable = computed(() =>
  jobs.value.map((job) => ({
    id: job.id,
    name: job.trigger === "scheduler" ? "Geplanter Batch-Job" : "Batch-Job",
    status: job.status === "failed" ? "error" : "ok",
    statusLabel: job.status === "completed" ? "OK" : job.status,
    lastRun: formatLocal(job.finished_at || job.started_at || job.created_at),
    note: job.error ? `Fehler: ${job.error}` : `${job.processed}/${job.total} Tenants verarbeitet`,
  }))
);

const historyRows = computed(() =>
  history.value.map((entry) => ({
    id: entry.id,
    createdAt: formatLocal(entry.created_at),
    actionLabel: backupActionLabel(entry.action),
    entityId: entry.entity_id,
    actor: entry.actor,
    details: formatBackupDetails(entry.payload),
  }))
);

function backupActionLabel(action: string) {
  if (action === "backup.create") return "Backup erstellt";
  if (action === "backup.restore") return "Backup Restore";
  return action;
}

function formatBackupDetails(payload: AuditOut["payload"]) {
  if (!payload || typeof payload !== "object") return "—";
  const parts: string[] = [];
  const typed = payload as Record<string, unknown>;
  if (typed.scope) parts.push(`scope=${typed.scope}`);
  if (typed.tenant_slug) parts.push(`tenant=${typed.tenant_slug}`);
  if (typed.tenant_id && !typed.tenant_slug) parts.push(`tenant_id=${typed.tenant_id}`);
  if (typed.table_counts && typeof typed.table_counts === "object") {
    parts.push(`tabellen=${Object.keys(typed.table_counts as Record<string, unknown>).length}`);
  }
  return parts.length ? parts.join(" · ") : "—";
}

function toIsoStart(dateString: string) {
  return new Date(`${dateString}T00:00:00.000Z`).toISOString();
}

function toIsoEnd(dateString: string) {
  return new Date(`${dateString}T23:59:59.999Z`).toISOString();
}

function updatePolling(shouldRun: boolean) {
  if (shouldRun && pollTimer === null) {
    pollTimer = window.setInterval(() => {
      loadJobs().catch((error) => console.error("[backup] job polling failed", error));
    }, 10000);
  } else if (!shouldRun && pollTimer !== null) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

onMounted(loadData);

watch(
  () => [props.adminKey, props.tenant?.id],
  () => {
    loadData();
  }
);

onBeforeUnmount(() => {
  updatePolling(false);
});
</script>
