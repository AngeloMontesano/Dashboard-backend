<script setup lang="ts">
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
</script>

<template>
  <UiPage>
    <UiSection title="Bestellungen" subtitle="Überwache Eingänge und Ausgänge, priorisiere kritische Lieferungen.">
      <UiToolbar>
        <template #start>
          <p class="eyebrow">Einkauf & Ausgang</p>
        </template>
        <template #end>
          <div class="action-row">
            <button class="button button--ghost" type="button">Export</button>
            <button class="button button--primary" type="button">Neue Bestellung</button>
          </div>
        </template>
      </UiToolbar>

      <div class="cards-grid mt-md">
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
    </UiSection>
  </UiPage>
</template>
