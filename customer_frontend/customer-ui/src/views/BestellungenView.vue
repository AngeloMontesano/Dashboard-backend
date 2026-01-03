<script setup lang="ts">
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Einkauf & Ausgang</p>
        <h2 class="section-title">Bestellungen</h2>
        <p class="section-subtitle">
          Überwache Eingänge und Ausgänge, priorisiere kritische Lieferungen.
        </p>
      </div>
      <div class="actions">
        <button class="button button--ghost" type="button">Export</button>
        <button class="button button--primary" type="button">Neue Bestellung</button>
      </div>
    </header>
    <div class="cards-grid" style="margin-bottom: 16px">
      <article class="card">
        <h3 class="card__title">Offene Eingänge</h3>
        <p class="card__value">21</p>
        <p class="card__hint">davon 4 überfällig</p>
      </article>
      <article class="card">
        <h3 class="card__title">Ausgehende Aufträge</h3>
        <p class="card__value">18</p>
        <p class="card__hint">für heute geplant</p>
      </article>
      <article class="card">
        <h3 class="card__title">Freigaben offen</h3>
        <p class="card__value">5</p>
        <p class="card__hint">warten auf Prüfung</p>
      </article>
    </div>
    <div class="placeholder">
      <p>Auftragslisten, Liefertermine und Freigaben folgen hier.</p>
    </div>
  </section>
</template>
