<script setup lang="ts">
</script>

<template>
  <section class="page-section">
    <header class="page-section__header">
      <div>
        <p class="eyebrow">Konfiguration</p>
        <h2 class="section-title">Einstellungen</h2>
        <p class="section-subtitle">
          Nutzer, Rollen, Benachrichtigungen und API-Schlüssel verwaltest du hier.
        </p>
      </div>
    </header>
    <div class="cards-grid" style="margin-bottom: 16px">
      <article class="card">
        <h3 class="card__title">Nutzer</h3>
        <p class="card__value">24</p>
        <p class="card__hint">davon 3 Admins</p>
      </article>
      <article class="card">
        <h3 class="card__title">Benachrichtigungen</h3>
        <p class="card__value">7 aktiv</p>
        <p class="card__hint">E-Mail & Slack</p>
      </article>
      <article class="card">
        <h3 class="card__title">API-Schlüssel</h3>
        <p class="card__value">2 gültig</p>
        <p class="card__hint">Zuletzt rotiert vor 12 Tagen</p>
      </article>
    </div>
    <div class="placeholder">
      <p>Konfigurationsoptionen werden bald hinzugefügt.</p>
    </div>
  </section>
</template>
