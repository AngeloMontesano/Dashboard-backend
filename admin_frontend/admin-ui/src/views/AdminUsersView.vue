<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Benutzer</div>
          <div class="cardHint">Globale User Verwaltung</div>
        </div>
      </div>

      <div class="box">
        <div class="muted">
          Platzhalter. Als nächstes: User Liste, Aktivierung, Passwort setzen.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminUsersView
  - Phase 1: Platzhalter
  - Phase 2: API /admin/users nutzen
*/
defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();
</script>
