<template>
  <div class="table-card" id="backup-monitoring-details">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Monitoring Details</div>
        <div class="text-muted text-small">
          Detailansicht für Exporte, Restore-Jobs und Validierungs-Checks.
        </div>
      </div>
      <a class="btnGhost small" href="#backup-monitoring">Zur Übersicht</a>
    </div>

    <div class="detail-grid">
      <div class="detail-box">
        <div class="detail-box__label">Letzter Export</div>
        <div class="detail-box__value">OK · 12 Tabellen</div>
        <div class="text-muted text-small">Zeit: 10:32 · Dauer: 2m 14s</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Restore</div>
        <div class="detail-box__value">OK · Dry-Run</div>
        <div class="text-muted text-small">Zeit: 09:10 · Dauer: 1m 02s</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Validierung</div>
        <div class="detail-box__value">Counts + Checksums</div>
        <div class="text-muted text-small">Keine Abweichungen</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Retention</div>
        <div class="detail-box__value">30 Tage · 20 Versionen</div>
        <div class="text-muted text-small">Letzter Cleanup: heute</div>
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
  </div>
</template>

<script setup lang="ts">
const jobs = [
  { name: "Schema-Introspektion", status: "ok", statusLabel: "OK", lastRun: "10:31", note: "Tabellenliste aktuell" },
  { name: "Mass Export", status: "ok", statusLabel: "OK", lastRun: "10:32", note: "Export-Report erstellt" },
  { name: "Restore Dry-Run", status: "ok", statusLabel: "OK", lastRun: "09:10", note: "FK-Checks bestanden" },
  { name: "Retention Cleanup", status: "ok", statusLabel: "OK", lastRun: "08:00", note: "Alte Backups entfernt" },
] as const;
</script>
