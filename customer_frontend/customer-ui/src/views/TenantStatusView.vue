<template>
  <div class="app auth-shell">
    <main class="auth-main">
      <section class="auth-card">
        <div class="auth-card-header">
          <h1 v-if="isRouteNotFound">Seite nicht gefunden</h1>
          <h1 v-else-if="statusValue.status === 'ok'">Tenant aktiv</h1>
          <h1 v-else-if="statusValue.status === 'not_found'">Tenant nicht gefunden</h1>
          <h1 v-else-if="statusValue.status === 'inactive'">Tenant inaktiv</h1>
          <h1 v-else>Service nicht verfügbar</h1>
          <p class="muted">
            Host: <span class="mono">{{ statusValue.host || '-' }}</span>
            <span class="divider">/</span>
            Slug: <span class="mono">{{ statusValue.slug || '-' }}</span>
          </p>
        </div>

        <div class="auth-card-body">
          <template v-if="isRouteNotFound">
            <p>Die angeforderte Seite wurde nicht gefunden. Bitte Navigation prüfen oder zur Startseite wechseln.</p>
            <div class="actions">
              <button class="btnPrimary" @click="goHome">Zur Startseite</button>
            </div>
          </template>

          <template v-else-if="statusValue.status === 'ok'">
            <p>Der Tenant ist aktiv. Bitte erneut versuchen.</p>
            <button class="btnPrimary" @click="reload">Weiter zur App</button>
          </template>

          <template v-else-if="statusValue.status === 'not_found'">
            <p>Die Subdomain oder der Tenant ist unbekannt. Prüfe die URL oder kontaktiere den Support.</p>
            <div class="actions">
              <button class="btnPrimary" @click="reload">Erneut versuchen</button>
              <button class="btnGhost" @click="goHome">Zur Startseite</button>
            </div>
          </template>

          <template v-else-if="statusValue.status === 'inactive'">
            <p>Der Tenant ist inaktiv. Bitte den Administrator oder Support kontaktieren.</p>
            <div class="actions">
              <button class="btnPrimary" @click="reload">Erneut versuchen</button>
              <button class="btnGhost" @click="goHome">Zur Startseite</button>
            </div>
          </template>

          <template v-else>
            <p>Der Dienst ist derzeit nicht erreichbar. Bitte später erneut versuchen.</p>
            <div class="actions">
              <button class="btnPrimary" @click="reload">Erneut versuchen</button>
              <button class="btnGhost" @click="goHome">Zur Startseite</button>
            </div>
            <p class="muted small">Grund: {{ statusValue.reason || 'unbekannt' }}</p>
          </template>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useTenantStatus } from '@/composables/useTenantStatus';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const statusValue = computed(() => useTenantStatus().value ?? { status: 'unavailable' });
const isRouteNotFound = computed(() => route.name === 'not-found' && statusValue.value.status === 'ok');

function reload() {
  window.location.reload();
}

function goHome() {
  router.push({ name: 'login' });
}
</script>

<style scoped>
.auth-main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
.auth-card {
  max-width: 520px;
  width: 100%;
  background: var(--surface-1);
  padding: var(--space-24);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}
.auth-card-header h1 {
  margin-bottom: var(--space-8);
}
.actions {
  display: flex;
  gap: var(--space-8);
  margin-top: var(--space-12);
}
.small {
  font-size: 0.85rem;
}
</style>
