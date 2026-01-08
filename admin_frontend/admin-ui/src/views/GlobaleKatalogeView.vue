<template>
  <UiPage>
    <UiSection title="Globale Kataloge" subtitle="Übersicht der globalen Stammdaten im Admin-Portal">
      <div class="table-card">
        <div class="stack">
          <p class="section-subtitle">
            Nutze die einzelnen Bereiche, um globale Artikel, Kategorien, Einheiten und Branchen zu pflegen. Diese
            Stammdaten sind tenant-übergreifend.
          </p>
          <ul class="bullets">
            <li>Globale Artikel: zentrale Artikelbasis ohne Tenant-Kontext.</li>
            <li>Globale Kategorien: strukturieren globale Artikel und sind systemweit sichtbar.</li>
            <li>Globale Einheiten: standardisierte Einheiten für Artikel (z. B. kg, l, pcs).</li>
            <li>Globale Branchen: Branchenpflege und Mapping zu globalen Artikeln.</li>
          </ul>
        </div>
      </div>
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
</script>
