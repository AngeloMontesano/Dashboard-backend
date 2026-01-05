<script setup lang="ts">
</script>

<template>
  <UiPage>
    <UiSection title="Dashboard" subtitle="Wichtigste Kennzahlen für dein Lager auf einen Blick.">
      <template #actions>
        <button class="button button--primary" type="button">Aktualisieren</button>
      </template>

      <div class="card-grid">
        <UiStatCard label="Offene Bestellungen" value="12" hint="Heute eingegangen" />
        <UiStatCard label="Bestände stabil" value="98 %" hint="unter Mindestbestand" />
        <UiStatCard label="Bewegungen heute" value="134" hint="Ein- und Ausgänge" />
      </div>
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import UiPage from "@/components/ui/UiPage.vue";
import UiSection from "@/components/ui/UiSection.vue";
import UiStatCard from "@/components/ui/UiStatCard.vue";
</script>
