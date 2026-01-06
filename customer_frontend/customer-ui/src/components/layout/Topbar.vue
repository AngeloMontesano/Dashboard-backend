<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useTheme } from '@/composables/useTheme';

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();
const { theme, setTheme } = useTheme();

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
function onThemeChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value as 'light' | 'dark' | 'system';
  setTheme(value);
}
</script>

<template>
  <header class="topbar">
    <div>
      <div class="pageTitle">{{ title }}</div>
      <div class="crumbs">Kundenportal</div>
    </div>
    <div class="section-actions">
      <div class="toggle">
        <span>Theme</span>
        <select class="input" :value="theme" @change="onThemeChange">
          <option value="system">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
      <button type="button" class="btnGhost small">Hilfe</button>
      <button type="button" class="btnPrimary small" @click="handleLogout">Abmelden</button>
    </div>
  </header>
</template>
