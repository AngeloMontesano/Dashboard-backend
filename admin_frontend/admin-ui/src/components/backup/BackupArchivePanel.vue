<template>
  <div class="table-card" id="backup-archive">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Backups & Archive</div>
        <div class="text-muted text-small">
          Wähle einen Stand für Restore. Dateien werden angezeigt und als ZIP heruntergeladen.
        </div>
      </div>
      <div class="row gap8">
        <a class="btnGhost small" href="#backup-archive-list">Zur Liste</a>
        <button class="btnGhost small" type="button" @click="createDemoBackup">Demo-Backup erstellen</button>
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

    <div class="hint">API Pfad: <span class="mono">{{ backupBasePath }}</span></div>

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
import { computed, ref } from "vue";
import { zipSync, strToU8 } from "fflate";
import { useToast } from "../../composables/useToast";
import { getBackupBasePath } from "../../api/base";
import { addBackup, loadBackupState, markRestore, type BackupEntry } from "./backupStore";

const { toast } = useToast();
const backupBasePath = getBackupBasePath();
const state = ref(loadBackupState());
const backups = computed(() => state.value.backups);
const history = computed(() =>
  state.value.history.map((entry) => ({
    ...entry,
    statusLabel: entry.status === "ok" ? "OK" : "Error",
  }))
);
const selectedId = ref(backups.value[0]?.id || "");
const restoreStatus = ref("");

const selectedBackup = computed(() => backups.value.find((entry) => entry.id === selectedId.value) || null);

function selectBackup(id: string) {
  selectedId.value = id;
  restoreStatus.value = "";
}

function downloadFile(backup: BackupEntry, file: BackupEntry["files"][number]) {
  const blob = new Blob([file.content], { type: "application/json" });
  saveBlob(blob, `${backup.name}-${file.name}`);
}

function downloadZip(backup: BackupEntry) {
  const payload: Record<string, Uint8Array> = {};
  backup.files.forEach((file) => {
    payload[file.name] = strToU8(file.content);
  });
  const zipped = zipSync(payload, { level: 6 });
  const blob = new Blob([zipped], { type: "application/zip" });
  saveBlob(blob, `${backup.name}.zip`);
}

function restoreSelected() {
  if (!selectedBackup.value) return;
  const confirmed = window.confirm(`Restore für ${selectedBackup.value.name} starten?`);
  if (!confirmed) return;
  restoreStatus.value = `Restore für ${selectedBackup.value.name} läuft...`;
  toast(`Restore gestartet: ${selectedBackup.value.name}`, "info");
  window.setTimeout(() => {
    restoreStatus.value = `Restore abgeschlossen: ${selectedBackup.value?.name}`;
    toast(`Restore abgeschlossen: ${selectedBackup.value?.name}`, "success");
    state.value = markRestore(state.value, selectedBackup.value as BackupEntry);
  }, 1200);
}

function createDemoBackup() {
  state.value = addBackup(state.value);
  selectedId.value = state.value.backups[0]?.id || "";
  toast(`Backup erstellt: ${state.value.backups[0]?.name}`, "success");
}

function saveBlob(blob: Blob, filename: string) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

const hasBackups = computed(() => backups.value.length > 0);

if (hasBackups.value && !selectedId.value) {
  selectedId.value = backups.value[0]?.id || "";
}
</script>
