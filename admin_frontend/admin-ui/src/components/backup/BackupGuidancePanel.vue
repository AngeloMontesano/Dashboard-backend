<template>
  <div class="grid-auto">
    <details class="detail-card" open>
      <summary class="detail-card__header">
        <div class="stack-sm">
          <div class="detail-card__title">1) Schema-Introspektion & tenant_id-Pflicht</div>
          <div class="text-muted text-small">
            Automatisiert alle tenant-gebundenen Tabellen erkennen, um das „Vergessen“ zu verhindern.
          </div>
        </div>
        <span class="tag ok">Empfohlen</span>
      </summary>
      <div class="stack-sm">
        <ul class="text-muted text-small">
          <li>DB-Metadaten auslesen (Tabellen, Spalten, Foreign Keys).</li>
          <li>Alle Tabellen mit <span class="mono">tenant_id</span> automatisch exportieren.</li>
          <li>FK-Graph auflösen und Export-Reihenfolge deterministisch halten.</li>
          <li>CI-Regel: neue Tabellen ohne <span class="mono">tenant_id</span> blockieren.</li>
        </ul>
        <div class="hint">Best Practice: tenant_id als Pflichtfeld + Index, FK-Verweise nur innerhalb desselben Tenants.</div>
      </div>
    </details>

    <details class="detail-card">
      <summary class="detail-card__header">
        <div class="stack-sm">
          <div class="detail-card__title">2) Background Mass Export (generiert aus Schema)</div>
          <div class="text-muted text-small">
            Periodischer Export mit Validierung, um Fehler im Export-Script zu vermeiden.
          </div>
        </div>
        <span class="tag">Job</span>
      </summary>
      <div class="stack-sm">
        <ul class="text-muted text-small">
          <li>Export-Job erstellt pro Tenant JSON/CSV/SQL-Dumps.</li>
          <li>Tabellenliste wird dynamisch aus Schema-Introspektion erstellt.</li>
          <li>Export-Report: Datensatzanzahl je Tabelle + Checksums.</li>
          <li>Fehler, wenn Tabelle mit <span class="mono">tenant_id</span> nicht im Export vorkommt.</li>
        </ul>
        <div class="hint">Optional: Export in Storage + Versionierung (z. B. S3) mit Retention-Policy.</div>
      </div>
    </details>

    <details class="detail-card">
      <summary class="detail-card__header">
        <div class="stack-sm">
          <div class="detail-card__title">3) Restore & Validierung</div>
          <div class="text-muted text-small">
            Restore nur nach Validierung, inklusive Konsistenzchecks und Dry-Run.
          </div>
        </div>
        <span class="tag">Restore</span>
      </summary>
      <div class="stack-sm">
        <ul class="text-muted text-small">
          <li>Dry-Run Restore in Staging (Smoke Tests + FK-Integrität).</li>
          <li>Validierung der Counts pro Tabelle gegen Export-Report.</li>
          <li>Idempotenter Restore (z. B. upsert) mit Audit-Log.</li>
          <li>Rollback-Strategie definieren (Snapshot vor Restore).</li>
        </ul>
        <div class="hint">Best Practice: Restore nur mit explizitem Tenant-Filter und sperren der Writes während des Imports.</div>
      </div>
    </details>
  </div>
</template>
