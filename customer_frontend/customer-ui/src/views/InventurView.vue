<script setup lang="ts">
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
</script>

<template>
  <UiPage>
    <UiSection title="Inventur" subtitle="Plane Inventuren, verfolge Fortschritt und halte Abweichungen fest.">
      <template #actions>
        <button class="button button--primary" type="button">Inventur starten</button>
      </template>

      <div class="cards-grid mt-md">
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
    </UiSection>
  </UiPage>
</template>
