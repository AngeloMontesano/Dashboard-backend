<script setup lang="ts">
</script>

<template>
  <div class="page stack">
    <section class="section stack">
      <header class="section-header">
        <div class="stack">
          <p class="eyebrow">Überblick</p>
          <h2 class="section-title">Dashboard</h2>
          <p class="section-subtitle">
            Wichtigste Kennzahlen für dein Lager auf einen Blick.
          </p>
        </div>
        <div class="section-actions">
          <button class="button button--primary" type="button">Aktualisieren</button>
        </div>
      </header>
      <div class="card-grid">
        <article class="card">
          <h3 class="card__title">Offene Bestellungen</h3>
          <p class="card__value">12</p>
          <p class="card__hint">Heute eingegangen</p>
        </article>
        <article class="card">
          <h3 class="card__title">Bestände stabil</h3>
          <p class="card__value">98 %</p>
          <p class="card__hint">unter Mindestbestand</p>
        </article>
        <article class="card">
          <h3 class="card__title">Bewegungen heute</h3>
          <p class="card__value">134</p>
          <p class="card__hint">Ein- und Ausgänge</p>
        </article>
      </div>
    </section>
  </div>
</template>
