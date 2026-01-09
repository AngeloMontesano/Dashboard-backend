<template>
  <div class="table-card">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Backups & Archive</div>
        <div class="text-muted text-small">
          Wähle einen Stand für Restore. Dateien werden angezeigt und als ZIP heruntergeladen.
        </div>
      </div>
      <button class="btnGhost small" type="button" @click="createDemoBackup">Demo-Backup erstellen</button>
    </div>

    <div class="tableWrap" v-if="backups.length">
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { zipSync, strToU8 } from "fflate";
import { useToast } from "../../composables/useToast";

type BackupFile = {
  name: string;
  sizeLabel: string;
  content: string;
};

type BackupEntry = {
  id: string;
  name: string;
  createdAt: string;
  status: "ok" | "error";
  statusLabel: string;
  files: BackupFile[];
};

const { toast } = useToast();
const backups = ref<BackupEntry[]>([buildDemoBackup(1), buildDemoBackup(2)]);
const selectedId = ref(backups.value[0]?.id || "");
const restoreStatus = ref("");

const selectedBackup = computed(() => backups.value.find((entry) => entry.id === selectedId.value) || null);

function selectBackup(id: string) {
  selectedId.value = id;
  restoreStatus.value = "";
}

function downloadFile(backup: BackupEntry, file: BackupFile) {
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
  }, 1200);
}

function createDemoBackup() {
  const nextIndex = backups.value.length + 1;
  const entry = buildDemoBackup(nextIndex);
  backups.value = [entry, ...backups.value];
  selectedId.value = entry.id;
  toast(`Backup erstellt: ${entry.name}`, "success");
}

function saveBlob(blob: Blob, filename: string) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

function buildDemoBackup(index: number): BackupEntry {
  const timestamp = new Date(Date.now() - index * 3600_000)
    .toISOString()
    .replace("T", " ")
    .replace(/:\d{2}\.\d{3}Z$/, "");
  const id = `backup-${index}`;
  return {
    id,
    name: `tenant-backup-${index}`,
    createdAt: timestamp,
    status: "ok",
    statusLabel: "OK",
    files: [
      {
        name: "meta.json",
        sizeLabel: "4 KB",
        content: JSON.stringify({ id, createdAt: timestamp, version: "1.0" }, null, 2),
      },
      {
        name: "tables.json",
        sizeLabel: "18 KB",
        content: JSON.stringify({ tables: ["tenants", "users", "orders"] }, null, 2),
      },
      {
        name: "data.json",
        sizeLabel: "120 KB",
        content: JSON.stringify({ rows: 1240, checksum: "sha256:demo" }, null, 2),
      },
    ],
  };
}
</script>
