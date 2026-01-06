<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useTheme } from '@/composables/useTheme';
import { useMovementQueue } from '@/composables/useMovementQueue';

const route = useRoute();
const router = useRouter();
const { logout } = useAuth();
const { theme, setTheme } = useTheme();
const { attentionCount } = useMovementQueue();

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
    case 'sync-probleme':
      return 'Sync & Fehler';
    case 'bestellungen':
      return 'Bestellungen';
    case 'einstellungen':
      return 'Einstellungen';
    case 'dashboard':
    default:
      return 'Dashboard';
  }
});

const issueCount = computed(() => attentionCount.value);

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
      <RouterLink class="btnGhost small badge-button" :to="{ name: 'sync-probleme' }">
        Fehler
        <span class="badge-counter" v-if="issueCount">{{ issueCount }}</span>
      </RouterLink>
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

<style scoped>
.badge-button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.badge-counter {
  min-width: 1.5rem;
  height: 1.5rem;
  padding: 0 0.35rem;
  border-radius: 999px;
  background: var(--danger-soft, #ffe5e5);
  color: var(--danger, #b42318);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
}
</style>
