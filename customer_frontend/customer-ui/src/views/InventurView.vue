<script setup lang="ts">
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Bestandsprüfung</p>
        <h2 class="section-title">Inventur</h2>
        <p class="section-subtitle">
          Plane Inventuren, verfolge Fortschritt und halte Abweichungen fest.
        </p>
      </div>
      <button class="button button--primary" type="button">Inventur starten</button>
    </header>
    <div class="cards-grid" style="margin-bottom: 16px">
      <article class="card">
        <h3 class="card__title">Geplante Inventuren</h3>
        <p class="card__value">3</p>
        <p class="card__hint">Nächster Termin: 12. Feb</p>
      </article>
      <article class="card">
        <h3 class="card__title">Abweichungen offen</h3>
        <p class="card__value">8</p>
        <p class="card__hint">müssen geprüft werden</p>
      </article>
      <article class="card">
        <h3 class="card__title">Erledigt dieses Jahr</h3>
        <p class="card__value">5</p>
        <p class="card__hint">vollständig dokumentiert</p>
      </article>
    </div>
    <div class="placeholder">
      <p>Übersicht und Checklisten für kommende Inventuren werden hier dargestellt.</p>
    </div>
  </section>
</template>
