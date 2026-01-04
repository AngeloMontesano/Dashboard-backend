<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { useAuth } from '@/composables/useAuth';

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();

const title = computed(() => {
  switch (route.name) {
    case 'artikelverwaltung':
      return 'Artikelverwaltung';
    case 'lagerbewegungen':
      return 'Lagerbewegungen';
    case 'inventur':
      return 'Inventur';
    case 'berichte-analysen':
      return 'Berichte & Analysen';
    case 'bestellungen':
      return 'Bestellungen';
    case 'einstellungen':
      return 'Einstellungen';
    case 'dashboard':
    default:
      return 'Dashboard';
  }
});

function handleLogout() {
  logout();
  router.push({ name: 'login' });
}
</script>

<template>
  <header class="topbar">
    <div>
      <p class="topbar__eyebrow">Kundenportal</p>
      <h1 class="topbar__title">{{ title }}</h1>
    </div>
    <div class="topbar__actions">
      <button type="button" class="button button--ghost">Hilfe</button>
      <button type="button" class="button button--primary" @click="handleLogout">Abmelden</button>
    </div>
  </header>
</template>
