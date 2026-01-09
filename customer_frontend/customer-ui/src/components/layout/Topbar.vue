<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed, reactive, ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useTheme } from '@/composables/useTheme';
import { useMovementQueue } from '@/composables/useMovementQueue';
import { downloadTelemetrySnapshot } from '@/utils/telemetry';
import { fetchHelpInfo, type HelpInfoOut } from '@/api/inventory';

const route = useRoute();
const router = useRouter();
const { logout, state: authState } = useAuth();
const { theme, setTheme } = useTheme();
const { attentionCount } = useMovementQueue();
const isDev = import.meta.env.DEV;

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
const helpOpen = ref(false);
const helpState = reactive<{
  loading: boolean;
  error: string;
  info: HelpInfoOut | null;
}>({
  loading: false,
  error: '',
  info: null
});

function handleLogout() {
  logout();
  router.push({ name: 'login' });
}

function exportTelemetry() {
  downloadTelemetrySnapshot('customer-telemetry-log.json');
}

function onThemeChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value as 'light' | 'dark' | 'system';
  setTheme(value);
}

async function openHelp() {
  helpOpen.value = true;
  if (helpState.info || helpState.loading) return;
  if (!authState.accessToken) {
    helpState.error = 'Keine Anmeldung gefunden.';
    return;
  }
  helpState.loading = true;
  helpState.error = '';
  try {
    helpState.info = await fetchHelpInfo(authState.accessToken);
  } catch (error) {
    helpState.error = (error as Error).message || 'Daten konnten nicht geladen werden.';
  } finally {
    helpState.loading = false;
  }
}

function closeHelp() {
  helpOpen.value = false;
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
      <details v-if="isDev" class="dev-tools">
        <summary>Dev</summary>
        <div class="dev-actions">
          <button type="button" class="btnGhost small" @click="exportTelemetry">Telemetry export</button>
        </div>
      </details>
      <div class="toggle">
        <span>Theme</span>
        <select class="input" :value="theme" @change="onThemeChange">
          <option value="system">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
      <button type="button" class="btnGhost small" @click="openHelp">Hilfe</button>
      <button type="button" class="btnPrimary small" @click="handleLogout">Abmelden</button>
    </div>
  </header>

  <teleport to="body">
    <div v-if="helpOpen" class="help-overlay" @click="closeHelp">
      <div class="help-modal" @click.stop>
        <div class="help-header">
          <div>
            <div class="help-title">Support</div>
            <div class="help-subtitle">Hilfe & Kontakt</div>
          </div>
          <button class="btnGhost small" type="button" @click="closeHelp">Schließen</button>
        </div>

        <div v-if="helpState.loading" class="help-loading">Lädt...</div>
        <div v-else-if="helpState.error" class="help-error">{{ helpState.error }}</div>
        <div v-else-if="helpState.info" class="help-content">
          <details class="help-section" open>
            <summary>Supportzeiten</summary>
            <div class="help-section-body">
              <div v-if="!helpState.info.support.support_hours.length" class="muted">
                Keine Zeiten hinterlegt.
              </div>
              <div v-else class="help-hours">
                <div v-for="(row, index) in helpState.info.support.support_hours" :key="index" class="help-hours__row">
                  <span class="help-hours__day">{{ row.day }}</span>
                  <span class="help-hours__time">{{ row.time }}</span>
                </div>
              </div>
            </div>
          </details>

          <details class="help-section" open>
            <summary>Kontaktdaten</summary>
            <div class="help-section-body">
              <div class="help-contact">
                <div>
                  <span class="muted">Tel:</span> {{ helpState.info.support.support_phone || '—' }}
                </div>
                <div>
                  <span class="muted">E-Mail:</span> {{ helpState.info.support.support_email || '—' }}
                </div>
              </div>
              <div v-if="helpState.info.support.support_note" class="help-note">
                {{ helpState.info.support.support_note }}
              </div>
            </div>
          </details>

          <details class="help-section">
            <summary>Kontaktdaten Persönlicher Vertriebler</summary>
            <div class="help-section-body">
              <div class="help-contact">
                <div>
                  <span class="muted">Name:</span> {{ helpState.info.sales_contact.name || '—' }}
                </div>
                <div>
                  <span class="muted">Tel:</span> {{ helpState.info.sales_contact.phone || '—' }}
                </div>
                <div>
                  <span class="muted">E-Mail:</span> {{ helpState.info.sales_contact.email || '—' }}
                </div>
              </div>
            </div>
          </details>
        </div>
      </div>
    </div>
  </teleport>
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

.dev-tools {
  position: relative;
}

.dev-tools summary {
  cursor: pointer;
  user-select: none;
}

.dev-actions {
  position: absolute;
  right: 0;
  z-index: 2;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 12rem;
}

.help-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.42);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  z-index: 1000;
}

:global(.theme-dark) .help-overlay,
:global([data-theme="dark"]) .help-overlay {
  background: rgba(4, 6, 10, 0.75);
}

.help-modal {
  background: var(--surface);
  color: var(--text);
  border-radius: 16px;
  border: 1px solid var(--border);
  width: min(720px, 100%);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.help-title {
  font-size: 1.25rem;
  font-weight: 700;
}

.help-subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.help-loading,
.help-error {
  font-size: 0.95rem;
}

.help-error {
  color: var(--danger, #b42318);
}

.help-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.help-section {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  background: var(--surface-2);
}

.help-section summary {
  cursor: pointer;
  font-weight: 600;
}

.help-section-body {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.help-hours {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.help-hours__row {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) minmax(160px, 1fr);
  gap: 0.75rem;
}

.help-hours__day {
  font-weight: 600;
}

.help-contact {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.help-note {
  padding: 0.75rem;
  border-radius: 10px;
  background: var(--surface);
  border: 1px dashed var(--border);
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .help-modal {
    padding: 1rem;
  }

  .help-hours__row {
    grid-template-columns: 1fr;
  }
}
</style>
