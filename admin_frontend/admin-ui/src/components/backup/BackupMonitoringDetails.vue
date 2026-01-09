<template>
  <details class="table-card" id="backup-monitoring-details" open>
    <summary class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Monitoring Details</div>
        <div class="text-muted text-small">
          Detailansicht für Exporte, Restore-Jobs und Validierungs-Checks.
        </div>
      </div>
      <a class="btnGhost small" href="#backup-monitoring">Zur Übersicht</a>
    </summary>

    <div class="detail-grid">
      <div class="detail-box">
        <div class="detail-box__label">Letzter Export</div>
        <div class="detail-box__value">{{ latestBackupLabel }}</div>
        <div class="text-muted text-small">{{ latestBackupMeta }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Restore</div>
        <div class="detail-box__value">{{ latestRestoreLabel }}</div>
        <div class="text-muted text-small">{{ latestRestoreMeta }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Validierung</div>
        <div class="detail-box__value">Counts + Checksums</div>
        <div class="text-muted text-small">Serverseitige Checks erforderlich</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Check</div>
        <div class="detail-box__value">{{ latestBackupLabel }}</div>
        <div class="text-muted text-small">{{ latestBackupMeta }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Retention</div>
        <div class="detail-box__value">{{ retentionLabel }}</div>
        <div class="text-muted text-small">Gespeicherte Backups</div>
      </div>
    </div>

    <div class="tableWrap">
      <table class="table">
        <thead>
          <tr>
            <th>Job</th>
            <th>Status</th>
            <th>Letzte Ausführung</th>
            <th class="right">Hinweis</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.name">
            <td>{{ job.name }}</td>
            <td>
              <span class="tag" :class="job.status === 'ok' ? 'ok' : 'bad'">{{ job.statusLabel }}</span>
            </td>
            <td class="mono">{{ job.lastRun }}</td>
            <td class="right text-muted text-small">{{ job.note }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </details>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { adminListBackups } from "../../api/admin";
import { useToast } from "../../composables/useToast";

type BackupEntry = {
  id: string;
  createdAt: string;
  restoredAt?: string | null;
  status: string;
  files: { name: string }[];
};

const props = defineProps<{
  adminKey: string;
  actor?: string;
}>();

const { toast } = useToast();
const backups = ref<BackupEntry[]>([]);

const latestBackup = computed(() => backups.value[0]);
const latestRestore = computed(() => backups.value.find((entry) => entry.restoredAt));
const retentionLabel = computed(() =>
  backups.value.length ? `${backups.value.length} Backups` : "—"
);

const latestBackupLabel = computed(() =>
  latestBackup.value ? `OK · ${latestBackup.value.files.length} Dateien` : "—"
);

const latestBackupMeta = computed(() =>
  latestBackup.value ? `Zeit: ${latestBackup.value.createdAt}` : "Keine Backups vorhanden"
);

const latestRestoreLabel = computed(() =>
  latestRestore.value ? "OK · Restore" : "—"
);

const latestRestoreMeta = computed(() =>
  latestRestore.value ? `Zeit: ${latestRestore.value?.restoredAt}` : "Noch kein Restore"
);

const jobs = computed(() => [
  {
    name: "Letztes Backup",
    status: latestBackup.value ? "ok" : "bad",
    statusLabel: latestBackup.value ? "OK" : "—",
    lastRun: latestBackup.value?.createdAt || "—",
    note: latestBackup.value ? "Backup vorhanden" : "Kein Backup gefunden",
  },
  {
    name: "Letzter Restore",
    status: latestRestore.value ? "ok" : "bad",
    statusLabel: latestRestore.value ? "OK" : "—",
    lastRun: latestRestore.value?.restoredAt || "—",
    note: latestRestore.value ? "Restore abgeschlossen" : "Noch kein Restore",
  },
  {
    name: "Retention",
    status: backups.value.length ? "ok" : "bad",
    statusLabel: backups.value.length ? "OK" : "—",
    lastRun: backups.value[0]?.createdAt || "—",
    note: backups.value.length ? `${backups.value.length} Backups gespeichert` : "Keine Backups",
  },
]);

async function loadBackups() {
  try {
    backups.value = await adminListBackups(props.adminKey, props.actor);
  } catch (error) {
    toast("Monitoring Details konnten nicht geladen werden", "warning");
    console.error(error);
  }
}

onMounted(loadBackups);
</script>
