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
        <div class="detail-box__value">{{ lastExport.title }}</div>
        <div class="text-muted text-small">{{ lastExport.detail }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Letzter Restore</div>
        <div class="detail-box__value">{{ lastRestore.title }}</div>
        <div class="text-muted text-small">{{ lastRestore.detail }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Validierung</div>
        <div class="detail-box__value">{{ validation.title }}</div>
        <div class="text-muted text-small">{{ validation.detail }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Jobs</div>
        <div class="detail-box__value">{{ jobsSummary.title }}</div>
        <div class="text-muted text-small">{{ jobsSummary.detail }}</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Retention</div>
        <div class="detail-box__value">{{ retention.title }}</div>
        <div class="text-muted text-small">{{ retention.detail }}</div>
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
          <tr v-for="job in jobs" :key="job.id">
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
type DetailRow = { title: string; detail: string };
type JobRow = { id: string; name: string; status: "ok" | "error"; statusLabel: string; lastRun: string; note: string };

defineProps<{
  lastExport: DetailRow;
  lastRestore: DetailRow;
  validation: DetailRow;
  jobsSummary: DetailRow;
  retention: DetailRow;
  jobs: JobRow[];
}>();
</script>
