<script setup lang="ts">
import { RouterView } from 'vue-router';
import Sidebar from './components/layout/Sidebar.vue';
import Topbar from './components/layout/Topbar.vue';
import ToastHost from './components/common/ToastHost.vue';
</script>

<template>
  <div class="app-shell">
    <Sidebar />
    <div class="app-content">
      <Topbar />
      <main class="page-surface">
        <RouterView />
      </main>
    </div>
    <ToastHost />
  </div>
</template>
