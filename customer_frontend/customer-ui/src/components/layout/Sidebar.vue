<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

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
  { label: 'Inventur', name: 'inventur', path: '/inventur', icon: '📋' },
  { label: 'Berichte & Analysen', name: 'berichte-analysen', path: '/berichte-analysen', icon: '📈' },
  { label: 'Bestellungen', name: 'bestellungen', path: '/bestellungen', icon: '🧾' },
  { label: 'Einstellungen', name: 'einstellungen', path: '/einstellungen', icon: '⚙️' }
];

const route = useRoute();

const activeName = computed(() => route.name);

</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">
      <div class="sidebar__logo">CL</div>
      <div class="sidebar__title">
        <p class="sidebar__heading">Customer Lagerportal</p>
        <p class="sidebar__subheading">Schneller Überblick</p>
      </div>
    </div>
    <nav class="sidebar__nav">
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="sidebar__link"
        :class="{ 'sidebar__link--active': activeName === item.name }"
      >
        <span class="sidebar__icon" aria-hidden="true">{{ item.icon }}</span>
        <span class="sidebar__label">{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>
