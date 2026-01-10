<template>
  <div class="table-card">
      <div class="table-card__header">
        <div class="stack-sm">
          <div class="tableTitle">Backups & Archive</div>
          <div class="text-muted text-small">
            Wähle einen Stand für Restore. Dateien werden angezeigt und als ZIP heruntergeladen.
          </div>
        </div>
        <div class="row gap8">
          <button class="btnGhost small" type="button" :disabled="busy" @click="createTenantBackup">
            Tenant-Backup starten
          </button>
          <button class="btnGhost small" type="button" :disabled="busy" @click="createAllBackups">
            Alle Tenants (Job)
          </button>
        </div>
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
import { computed } from "vue";

type BackupFile = {
  name: string;
  sizeLabel: string;
};

export type BackupEntry = {
  id: string;
  name: string;
  createdAt: string;
  status: "ok" | "error";
  statusLabel: string;
  files: BackupFile[];
};

const props = defineProps<{
  backups: BackupEntry[];
  selectedId: string;
  restoreStatus: string;
  busy: boolean;
}>();

const emit = defineEmits<{
  (e: "select", id: string): void;
  (e: "downloadZip", backup: BackupEntry): void;
  (e: "downloadFile", payload: { backup: BackupEntry; file: BackupFile }): void;
  (e: "restore", backup: BackupEntry): void;
  (e: "createTenantBackup"): void;
  (e: "createAllBackups"): void;
}>();

const selectedBackup = computed(() => props.backups.find((entry) => entry.id === props.selectedId) || null);

function selectBackup(id: string) {
  emit("select", id);
}

function downloadFile(backup: BackupEntry, file: BackupFile) {
  emit("downloadFile", { backup, file });
}

function downloadZip(backup: BackupEntry) {
  emit("downloadZip", backup);
}

function restoreSelected() {
  if (!selectedBackup.value) return;
  emit("restore", selectedBackup.value);
}

function createTenantBackup() {
  emit("createTenantBackup");
}

function createAllBackups() {
  emit("createAllBackups");
}
</script>
