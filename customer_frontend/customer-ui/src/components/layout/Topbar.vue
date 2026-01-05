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
      <p class="topbar__eyebrow">Kundenportal</p>
      <h1 class="topbar__title">{{ title }}</h1>
    </div>
    <div class="topbar__actions">
      <label class="button button--ghost inline-field">
        <span>Theme</span>
        <select class="input" :value="theme" @change="onThemeChange">
          <option value="system">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
      <button type="button" class="button button--ghost">Hilfe</button>
      <button type="button" class="button button--primary" @click="handleLogout">Abmelden</button>
    </div>
  </header>
</template>
