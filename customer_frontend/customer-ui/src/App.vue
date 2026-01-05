<template>
  <div :class="['app-root', themeClass]">
    <div v-if="authed" class="app-shell">
      <Sidebar />
      <div class="app-content">
        <Topbar />
        <main class="page-surface">
          <RouterView />
        </main>
      </div>
      <ToastHost />
    </div>
    <div v-else class="app-shell--login">
      <RouterView />
      <ToastHost />
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { computed } from 'vue';
import Sidebar from './components/layout/Sidebar.vue';
import Topbar from './components/layout/Topbar.vue';
import ToastHost from './components/common/ToastHost.vue';
import { useAuth } from './composables/useAuth';
import { useTheme } from './composables/useTheme';

const { isAuthenticated } = useAuth();
const { resolvedTheme } = useTheme();

const themeClass = computed(() => (resolvedTheme.value === 'dark' ? 'theme-dark' : 'theme-classic'));
const authed = computed(() => isAuthenticated());
</script>
