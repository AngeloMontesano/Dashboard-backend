<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">Security, Feature Flags</div>
        </div>
      </div>

      <div class="box">
        <div class="muted">
          Platzhalter. Als nächstes: Security Hinweise, Key Handling, Feature Flags UI.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminSettingsView
  - Phase 1: Platzhalter
  - Phase 2: UI Settings, Feature Flags
*/
defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  dark: boolean;
}>();

defineEmits<{
  (e: "toggleDark"): void;
}>();
</script>
