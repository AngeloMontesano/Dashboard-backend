<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Memberships</div>
          <div class="cardHint">User <-> Tenant Rollen</div>
        </div>
      </div>

      <div class="box">
        <div class="muted">
          Platzhalter. Als nächstes: Suche nach Tenant oder User und dann Memberships anzeigen.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminMembershipsView
  - Phase 1: Platzhalter
  - Phase 2: /admin/memberships/tenant/* und /admin/memberships/user/* nutzen
*/
defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
}>();
</script>
