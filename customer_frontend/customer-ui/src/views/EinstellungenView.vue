<script setup lang="ts">
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
</script>

<template>
  <UiPage>
    <UiSection title="Einstellungen" subtitle="Nutzer, Rollen, Benachrichtigungen und API-Schlüssel verwaltest du hier.">
      <div class="cards-grid mt-md">
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
    </UiSection>
  </UiPage>
</template>
