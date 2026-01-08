<template>
  <div class="table-card" id="backup-monitoring">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Monitoring (Quick Overview)</div>
        <div class="text-muted text-small">
          Kurzstatus der Backup-Pipeline mit Absprung zu Details.
        </div>
      </div>
      <a class="btnGhost small" href="#backup-monitoring-details">Zu Details</a>
    </div>

    <div class="card-grid">
      <div class="detail-box" v-for="item in overview" :key="item.label">
        <div class="detail-box__label">{{ item.label }}</div>
        <div class="detail-box__value">
          <span class="statusPill" :class="item.status">
            <span class="dot"></span>
            {{ item.value }}
          </span>
        </div>
      </div>
    </div>

    <div class="hint">Tipp: Status basiert auf Snapshot/Export-Logs und dient als Frühwarnung.</div>
  </div>
</template>

<script setup lang="ts">
const overview = [
  { label: "Letzter Export", value: "OK", status: "ok" },
  { label: "Letzter Restore", value: "OK", status: "ok" },
  { label: "Offene Fehler", value: "0", status: "ok" },
  { label: "Retention", value: "Aktiv", status: "ok" },
] as const;
</script>
