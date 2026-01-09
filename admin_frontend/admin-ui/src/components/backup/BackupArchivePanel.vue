<template>
  <div class="table-card" id="backup-archive">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Backups & Archive</div>
        <div class="text-muted text-small">
          Wähle einen Stand für Restore. Dateien werden angezeigt und als ZIP heruntergeladen.
        </div>
      </div>
      <div class="row gap8 wrap">
        <a class="btnGhost small" href="#backup-archive-list">Zur Liste</a>
        <button
          class="btnPrimary small"
          type="button"
          :disabled="busy.create || !canCreateTenantBackup"
          @click="createTenantBackup"
        >
          {{ busy.create ? "erstelle..." : "Backup Tenant" }}
        </button>
        <button class="btnGhost small" type="button" :disabled="busy.create" @click="createAllBackups">
          {{ busy.create ? "erstelle..." : "Backup alle Tenants" }}
        </button>
        <button class="btnGhost small" type="button" :disabled="busy.list" @click="loadBackups">
          {{ busy.list ? "lade..." : "Aktualisieren" }}
        </button>
      </div>
    </div>

    <div class="tableWrap" v-if="backups.length" id="backup-archive-list">
      <table class="table">
        <thead>
          <tr>
            <th>Auswahl</th>
            <th>Backup</th>
            <th>Erstellt</th>
            <th>Status</th>
            <th class="right">Aktion</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in backups"
            :key="entry.id"
            :class="{ rowActive: selectedId === entry.id }"
            @click="selectBackup(entry.id)"
          >
            <td>
              <input type="radio" name="backup" :checked="selectedId === entry.id" />
            </td>
            <td>{{ entry.name }}</td>
            <td class="mono">{{ entry.createdAt }}</td>
            <td>
              <span class="tag" :class="entry.status === 'ok' ? 'ok' : 'bad'">{{ entry.statusLabel }}</span>
            </td>
            <td class="right">
              <button class="btnGhost small" type="button" @click.stop="downloadZip(entry)">ZIP laden</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="text-muted text-small" v-else>Keine Backups vorhanden.</div>

    <div class="hint">
      API Pfad: <span class="mono">{{ backupBasePath }}</span>
      <span v-if="!canCreateTenantBackup">· Tenant für Backup auswählen</span>
    </div>

    <div class="detail-card" v-if="selectedBackup">
      <div class="detail-card__header">
        <div class="stack-sm">
          <div class="detail-card__title">Dateien im Backup</div>
          <div class="text-muted text-small">{{ selectedBackup.name }} · {{ selectedBackup.createdAt }}</div>
        </div>
        <div class="row gap8">
          <button class="btnPrimary small" type="button" @click="restoreSelected">Restore starten</button>
          <button class="btnGhost small" type="button" @click="downloadZip(selectedBackup)">ZIP laden</button>
        </div>
      </div>

      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>Datei</th>
              <th>Größe</th>
              <th class="right">Download</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in selectedBackup.files" :key="file.name">
              <td class="mono">{{ file.name }}</td>
              <td>{{ file.sizeLabel }}</td>
              <td class="right">
                <button class="btnGhost small" type="button" @click="downloadFile(selectedBackup, file)">
                  Datei laden
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="hint" v-if="restoreStatus">{{ restoreStatus }}</div>
    </div>

    <div class="table-card" v-if="history.length">
      <div class="table-card__header">
        <div class="stack-sm">
          <div class="tableTitle">Historie</div>
          <div class="text-muted text-small">Erstellte Backups und Restore-Aktionen.</div>
        </div>
      </div>
      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>Aktion</th>
              <th>Backup</th>
              <th>Zeit</th>
              <th>Status</th>
              <th class="right">Hinweis</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in history" :key="entry.id">
              <td>{{ entry.action === "create" ? "Backup erstellt" : "Restore" }}</td>
              <td>{{ entry.backupName }}</td>
              <td class="mono">{{ entry.timestamp }}</td>
              <td>
                <span class="tag" :class="entry.status === 'ok' ? 'ok' : 'bad'">{{ entry.statusLabel }}</span>
              </td>
              <td class="right text-muted text-small">{{ entry.message }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "../../composables/useToast";
import {
  adminCreateAllBackups,
  adminCreateTenantBackup,
  adminDownloadBackup,
  adminDownloadBackupFile,
  adminListBackups,
  adminRestoreBackup,
} from "../../api/admin";
import { getBackupBasePath } from "../../api/base";

type BackupEntry = {
  id: string;
  scope: string;
  tenant_id: string | null;
  tenant_slug: string | null;
  created_at: string;
  status: string;
  restored_at?: string | null;
  files: { name: string; size_label: string; size_bytes: number }[];
};

type BackupHistoryRow = {
  id: string;
  action: "create" | "restore";
  backupId: string;
  backupName: string;
  timestamp: string;
  status: "ok" | "error";
  statusLabel: string;
  message: string;
};

const props = defineProps<{
  adminKey: string;
  actor?: string;
  tenantId?: string;
  tenantSlug?: string;
}>();

const { toast } = useToast();
const backupBasePath = getBackupBasePath();
const backups = ref<BackupEntry[]>([]);
const history = ref<BackupHistoryRow[]>([]);
const selectedId = ref("");
const restoreStatus = ref("");
const busy = ref({ list: false, create: false, restore: false, download: false });

const selectedBackup = computed(() => backups.value.find((entry) => entry.id === selectedId.value) || null);
const canCreateTenantBackup = computed(() => Boolean(props.tenantId));

function selectBackup(id: string) {
  selectedId.value = id;
  restoreStatus.value = "";
}

function normalizeHistory(items: BackupEntry[]) {
  const rows: BackupHistoryRow[] = [];
  items.forEach((backup) => {
    rows.push({
      id: `${backup.id}-create`,
      action: "create",
      backupId: backup.id,
      backupName: backup.tenant_slug ? `${backup.tenant_slug}` : backup.id,
      timestamp: backup.created_at,
      status: "ok",
      statusLabel: "OK",
      message: backup.scope === "all" ? "Backup für alle Tenants" : "Tenant-Backup erstellt",
    });
    if (backup.restored_at) {
      rows.push({
        id: `${backup.id}-restore`,
        action: "restore",
        backupId: backup.id,
        backupName: backup.tenant_slug ? `${backup.tenant_slug}` : backup.id,
        timestamp: backup.restored_at,
        status: "ok",
        statusLabel: "OK",
        message: "Restore abgeschlossen",
      });
    }
  });
  history.value = rows.sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));
}

async function loadBackups() {
  busy.value.list = true;
  try {
    backups.value = await adminListBackups(props.adminKey, props.actor);
    if (backups.value.length && !selectedId.value) {
      selectedId.value = backups.value[0]?.id || "";
    }
    normalizeHistory(backups.value);
  } catch (error) {
    toast("Backups konnten nicht geladen werden", "warning");
    console.error(error);
  } finally {
    busy.value.list = false;
  }
}

async function createTenantBackup() {
  if (!props.tenantId) {
    toast("Bitte Tenant auswählen", "warning");
    return;
  }
  busy.value.create = true;
  try {
    const backup = await adminCreateTenantBackup(props.adminKey, props.actor, props.tenantId);
    backups.value = [backup, ...backups.value];
    selectedId.value = backup.id;
    normalizeHistory(backups.value);
    toast(`Backup erstellt: ${props.tenantSlug || backup.id}`, "success");
  } catch (error) {
    toast("Backup fehlgeschlagen", "danger");
    console.error(error);
  } finally {
    busy.value.create = false;
  }
}

async function createAllBackups() {
  busy.value.create = true;
  try {
    const backup = await adminCreateAllBackups(props.adminKey, props.actor);
    backups.value = [backup, ...backups.value];
    selectedId.value = backup.id;
    normalizeHistory(backups.value);
    toast("Backup für alle Tenants erstellt", "success");
  } catch (error) {
    toast("Backup fehlgeschlagen", "danger");
    console.error(error);
  } finally {
    busy.value.create = false;
  }
}

async function restoreSelected() {
  if (!selectedBackup.value) return;
  const confirmed = window.confirm(`Restore für ${selectedBackup.value.id} starten?`);
  if (!confirmed) return;
  busy.value.restore = true;
  restoreStatus.value = `Restore für ${selectedBackup.value.id} läuft...`;
  try {
    const backup = await adminRestoreBackup(props.adminKey, props.actor, selectedBackup.value.id);
    backups.value = backups.value.map((entry) => (entry.id === backup.id ? backup : entry));
    normalizeHistory(backups.value);
    restoreStatus.value = `Restore abgeschlossen: ${backup.id}`;
    toast(`Restore abgeschlossen: ${backup.id}`, "success");
  } catch (error) {
    toast("Restore fehlgeschlagen", "danger");
    console.error(error);
  } finally {
    busy.value.restore = false;
  }
}

async function downloadZip(backup: BackupEntry) {
  busy.value.download = true;
  try {
    const blob = await adminDownloadBackup(props.adminKey, props.actor, backup.id);
    saveBlob(blob, `${backup.id}.zip`);
  } catch (error) {
    toast("Download fehlgeschlagen", "danger");
    console.error(error);
  } finally {
    busy.value.download = false;
  }
}

async function downloadFile(backup: BackupEntry, file: BackupEntry["files"][number]) {
  busy.value.download = true;
  try {
    const blob = await adminDownloadBackupFile(props.adminKey, props.actor, backup.id, file.name);
    saveBlob(blob, file.name);
  } catch (error) {
    toast("Datei-Download fehlgeschlagen", "danger");
    console.error(error);
  } finally {
    busy.value.download = false;
  }
}

function saveBlob(blob: Blob, filename: string) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

onMounted(loadBackups);
</script>
