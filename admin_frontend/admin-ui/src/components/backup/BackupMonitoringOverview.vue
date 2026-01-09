<template>
  <div class="table-card" id="backup-monitoring">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Monitoring (Quick Overview)</div>
        <div class="text-muted text-small">
          Kurzstatus der Backup-Pipeline mit Absprung zu Details.
        </div>
      </div>
      <div class="row gap8">
        <a class="btnGhost small" href="#backup-monitoring-details">Zu Details</a>
        <a class="btnGhost small" href="#backup-archive">Zu Archiv</a>
      </div>
    </div>

    <div class="card-grid">
      <div class="detail-box">
        <div class="detail-box__label">Letzter Export</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="latestExport ? 'ok' : 'bad'">
            <span class="dot"></span>
            {{ latestExport ? "OK" : "—" }}
          </span>
        </div>
        <div class="text-muted text-small">{{ latestExport || "Keine Backups vorhanden" }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Restore</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="latestRestore ? 'ok' : 'bad'">
            <span class="dot"></span>
            {{ latestRestore ? "OK" : "—" }}
          </span>
        </div>
        <div class="text-muted text-small">{{ latestRestore || "Noch kein Restore" }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Check</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="latestExport ? 'ok' : 'bad'">
            <span class="dot"></span>
            {{ latestExport ? "OK" : "—" }}
          </span>
        </div>
        <div class="text-muted text-small">Letztes Backup</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Offene Fehler</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="errorCount ? 'bad' : 'ok'">
            <span class="dot"></span>
            {{ errorCount }}
          </span>
        </div>
        <div class="text-muted text-small">Status der Backups</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Retention</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="backups.length ? 'ok' : 'bad'">
            <span class="dot"></span>
            {{ backups.length ? `${backups.length} Backups` : "—" }}
          </span>
        </div>
        <div class="text-muted text-small">Gespeicherte Snapshots</div>
      </div>
    </div>

    <div class="hint">Tipp: Status basiert auf den gespeicherten Backup-Einträgen.</div>
  </div>
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
};

const props = defineProps<{
  adminKey: string;
  actor?: string;
}>();

const { toast } = useToast();
const backups = ref<BackupEntry[]>([]);

const latestExport = computed(() => backups.value[0]?.createdAt || "");
const latestRestore = computed(() => backups.value.find((entry) => entry.restoredAt)?.restoredAt || "");
const errorCount = computed(() => backups.value.filter((entry) => entry.status !== "ok").length);

async function loadBackups() {
  try {
    backups.value = await adminListBackups(props.adminKey, props.actor);
  } catch (error) {
    toast("Monitoring konnte nicht geladen werden", "warning");
    console.error(error);
  }
}

onMounted(loadBackups);
</script>
