<script setup lang="ts">
import { reactive, onMounted } from 'vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import { useAuth } from '@/composables/useAuth';
import AuthReauthBanner from '@/components/auth/AuthReauthBanner.vue';
import { useAuthIssueBanner } from '@/composables/useAuthIssueBanner';
import {
  fetchSettings,
  updateSettings,
  exportSettings,
  importSettings,
  sendTestEmail
} from '@/api/inventory';

const { state: authState } = useAuth();
const { authIssue, authMessage, handleAuthError } = useAuthIssueBanner();

type Settings = Awaited<ReturnType<typeof fetchSettings>>;

const state = reactive<{
  settings: Settings | null;
  loading: boolean;
  error: string | null;
  success: string | null;
  testEmail: string;
  importing: boolean;
  testing: boolean;
  addressStreet: string;
  addressNumber: string;
}>({
  settings: null,
  loading: false,
  error: null,
  success: null,
  testEmail: '',
  importing: false,
  testing: false,
  addressStreet: '',
  addressNumber: ''
});

function showError(err: unknown, fallback: string) {
  const classified = handleAuthError(err);
  const detail = classified.detailMessage || classified.userMessage || fallback;
  state.error = classified.category === 'auth' ? classified.userMessage : `${fallback}: ${detail}`;
  return classified.category === 'auth';
}

async function loadSettings() {
  if (!authState.accessToken) return;
  state.loading = true;
  state.error = null;
  try {
    state.settings = await fetchSettings(authState.accessToken);
    const split = splitAddress(state.settings?.address || '');
    state.addressStreet = split.street;
    state.addressNumber = split.number;
  } catch (err: any) {
    showError(err, 'Einstellungen konnten nicht geladen werden');
  } finally {
    state.loading = false;
  }
}

async function saveSettings() {
  if (!authState.accessToken || !state.settings) return;
  state.loading = true;
  state.error = null;
  state.success = null;
  try {
    state.settings.address = composeAddress(state.addressStreet, state.addressNumber);
    state.settings = await updateSettings(authState.accessToken, state.settings);
    state.success = 'Einstellungen gespeichert';
  } catch (err: any) {
    showError(err, 'Speichern fehlgeschlagen');
  } finally {
    state.loading = false;
  }
}

async function handleExport() {
  if (!authState.accessToken) return;
  try {
    const blob = await exportSettings(authState.accessToken);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'settings_export.xlsx';
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    showError(err, 'Export fehlgeschlagen');
  }
}

async function handleImport(event: Event) {
  if (!authState.accessToken) return;
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  state.importing = true;
  state.error = null;
  state.success = null;
  try {
    await importSettings(authState.accessToken, file);
    state.success = 'Import abgeschlossen';
    await loadSettings();
  } catch (err: any) {
    showError(err, 'Import fehlgeschlagen');
  } finally {
    state.importing = false;
    target.value = '';
  }
}

async function handleTestEmail() {
  if (!authState.accessToken) return;
  state.testing = true;
  state.error = null;
  state.success = null;
  try {
    const res = await sendTestEmail(authState.accessToken, state.testEmail || state.settings?.contact_email || '');
    if (!res.ok) {
      state.error = res.error || 'Test-E-Mail fehlgeschlagen';
    } else {
      state.success = 'Test-E-Mail gesendet';
    }
  } catch (err: any) {
    showError(err, 'Test-E-Mail fehlgeschlagen');
  } finally {
    state.testing = false;
  }
}

function splitAddress(address: string) {
  const match = address?.match(/^(.*?)(\s+\d+\w*)$/);
  return {
    street: match ? match[1].trim() : (address || '').trim(),
    number: match ? match[2].trim() : ''
  };
}

function composeAddress(street: string, number: string) {
  return [street?.trim(), number?.trim()].filter(Boolean).join(' ');
}

onMounted(loadSettings);
</script>

<template>
  <UiPage>
    <UiSection title="Einstellungen" subtitle="Firmendaten, Auto-Bestellung und Exporte verwalten.">
      <UiToolbar>
        <template #start>
          <p class="eyebrow">Firmendaten & Benachrichtigungen</p>
        </template>
        <template #end>
          <div class="action-row">
            <button class="btnGhost small" type="button" @click="loadSettings" :disabled="state.loading">Neu laden</button>
            <button class="btnGhost small" type="button" @click="handleExport">Export</button>
            <label class="btnGhost small">
              Import
              <input type="file" class="sr-only" accept=".xlsx" @change="handleImport" :disabled="state.importing" />
            </label>
            <button class="btnPrimary small" type="button" @click="saveSettings" :disabled="state.loading">
              Speichern
            </button>
          </div>
        </template>
      </UiToolbar>

      <AuthReauthBanner
        v-if="authIssue"
        class="mt-sm"
        :message="authMessage"
        retry-label="Neu laden"
        @retry="() => loadSettings()"
      />

      <div v-if="state.error" class="banner banner--error mt-sm">
        {{ state.error }}
      </div>
      <div v-if="state.success" class="banner banner--success mt-sm">
        {{ state.success }}
      </div>

      <div class="form-grid mt-md" v-if="state.settings">
        <label class="form-field">
          <span class="form-label">Firma</span>
          <input v-model="state.settings.company_name" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Ansprechpartner</span>
          <input v-model="state.settings.contact_name" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Kontakt E-Mail</span>
          <input v-model="state.settings.contact_email" type="email" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Bestell-E-Mail</span>
          <input v-model="state.settings.order_email" type="email" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Telefon</span>
          <input v-model="state.settings.phone" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Straße</span>
          <input v-model="state.addressStreet" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Hausnummer</span>
          <input v-model="state.addressNumber" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">PLZ</span>
          <input v-model="state.settings.address_postal_code" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Ort</span>
          <input v-model="state.settings.address_city" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Export-Format</span>
          <input v-model="state.settings.export_format" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field checkbox-field">
          <input
            v-model="state.settings.auto_order_enabled"
            type="checkbox"
            :disabled="state.loading"
            aria-label="Auto-Bestellung aktivieren"
          />
          <span class="form-label">Auto-Bestellung aktiv</span>
        </label>
        <label class="form-field">
          <span class="form-label">Auto-Bestellung Minimum</span>
          <input v-model.number="state.settings.auto_order_min" type="number" class="input" min="0" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Filialnummer</span>
          <input v-model="state.settings.branch_number" type="text" class="input" :disabled="state.loading" />
        </label>
        <label class="form-field">
          <span class="form-label">Steuernummer</span>
          <input v-model="state.settings.tax_number" type="text" class="input" :disabled="state.loading" />
        </label>
      </div>

      <div class="mt-lg">
        <h3 class="eyebrow">Test-E-Mail</h3>
        <div class="form-grid">
          <label class="form-field">
            <span class="form-label">Empfänger</span>
            <input v-model="state.testEmail" type="email" class="input" placeholder="adresse@example.com" :disabled="state.testing" />
          </label>
          <button class="btnGhost small align-self-end" type="button" @click="handleTestEmail" :disabled="state.testing">
            {{ state.testing ? 'Senden...' : 'Test-E-Mail senden' }}
          </button>
        </div>
      </div>
    </UiSection>
  </UiPage>
</template>
