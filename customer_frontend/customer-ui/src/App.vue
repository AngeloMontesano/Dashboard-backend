<template>
  <div :class="['app', themeClass]">
    <div v-if="authed" class="shell">
      <Sidebar />
      <main class="main">
        <Topbar />
        <section class="workspace">
          <RouterView />
        </section>
      </main>
    </div>
    <div v-else class="auth-shell">
      <RouterView />
    </div>
    <ToastHost />
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

const themeClass = computed(() => (resolvedTheme.value === 'dark' ? 'theme-dark' : ''));
const authed = computed(() => isAuthenticated());
</script>
