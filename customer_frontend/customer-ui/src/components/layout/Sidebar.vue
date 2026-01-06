<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useMovementQueue } from '@/composables/useMovementQueue';

type NavItem = {
  label: string;
  name: string;
  path: string;
  icon: string;
};

const navItems: NavItem[] = [
  { label: 'Dashboard', name: 'dashboard', path: '/', icon: '📊' },
  { label: 'Artikelverwaltung', name: 'artikelverwaltung', path: '/artikelverwaltung', icon: '📦' },
  { label: 'Kategorien', name: 'kategorien', path: '/kategorien', icon: '🏷️' },
  { label: 'Lagerbewegungen', name: 'lagerbewegungen', path: '/lagerbewegungen', icon: '🔄' },
  { label: 'Sync & Fehler', name: 'sync-probleme', path: '/sync-probleme', icon: '🚧' },
  { label: 'Inventur', name: 'inventur', path: '/inventur', icon: '📋' },
  { label: 'Berichte & Analysen', name: 'berichte-analysen', path: '/berichte-analysen', icon: '📈' },
  { label: 'Bestellungen', name: 'bestellungen', path: '/bestellungen', icon: '🧾' },
  { label: 'Einstellungen', name: 'einstellungen', path: '/einstellungen', icon: '⚙️' }
];

const route = useRoute();
const { attentionCount } = useMovementQueue();

const activeName = computed(() => route.name);
const issueCount = computed(() => attentionCount.value);

</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">LV</div>
      <div class="brandText">
        <div class="brandTitle">Lagerverwaltung</div>
        <div class="brandSub">Customer Portal</div>
      </div>
    </div>
    <nav class="nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="navItem"
        :class="{ active: activeName === item.name }"
        :aria-current="activeName === item.name ? 'page' : undefined"
      >
        <span class="navIcon" aria-hidden="true">{{ item.icon }}</span>
        <span class="navLabel">{{ item.label }}</span>
        <span class="navBadge" v-if="item.name === 'sync-probleme' && issueCount">{{ issueCount }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.navBadge {
  margin-left: auto;
  background: var(--danger-soft, #ffe5e5);
  color: var(--danger, #b42318);
  border-radius: 999px;
  padding: 0.15rem 0.55rem;
  font-weight: 700;
  font-size: 0.85rem;
}
</style>
