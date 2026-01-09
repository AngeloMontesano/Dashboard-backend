<template>
  <div class="table-card">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Operative Checks (Kurz)</div>
        <div class="text-muted text-small">Zusammenfassung für tägliche Praxis & Audit.</div>
      </div>
    </div>
    <div class="detail-grid">
      <div class="detail-box">
        <div class="detail-box__label">Pflichtfelder</div>
        <div class="detail-box__value">tenant_id + FK-Check</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Validierung</div>
        <div class="detail-box__value">Counts + Checksums</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Restore</div>
        <div class="detail-box__value">Dry-Run + Audit</div>
      </div>
      <div class="detail-box">
        <div class="detail-box__label">Speicher</div>
        <div class="detail-box__value">Versioniert + Retention</div>
      </div>
    </div>
  </div>
</template>
