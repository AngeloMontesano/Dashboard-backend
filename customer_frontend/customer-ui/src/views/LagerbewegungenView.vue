<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useMovementQueue, type MovementRecord } from '@/composables/useMovementQueue';
import { useOnlineStatus } from '@/composables/useOnlineStatus';
import { useToast } from '@/composables/useToast';
import { useAuth } from '@/composables/useAuth';
import { fetchSettings } from '@/api/inventory';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import { RouterLink } from 'vue-router';

const barcode = ref('');
const qty = ref<number>(1);
const note = ref('');
const barcodeInput = ref<HTMLInputElement | null>(null);
const clearing = ref(false);
const submitting = ref<{ IN: boolean; OUT: boolean }>({ IN: false, OUT: false });
const settings = ref<Awaited<ReturnType<typeof fetchSettings>> | null>(null);

const { isOnline } = useOnlineStatus();
const { state: authState } = useAuth();
const hasWriteAccess = computed(() => ['owner', 'admin'].includes(authState.role));
const {
  movements,
  enqueueMovement,
  syncNow,
  clearSent,
  hasPending,
  syncing,
  lastSyncError,
  deriveIssueState,
  attentionCount
} = useMovementQueue();
const { push: pushToast } = useToast();

const recentMovements = computed(() => movements.value.slice(0, 30));
const issueCount = computed(() => attentionCount.value);
const barcodeScannerReduceEnabled = computed(() => settings.value?.barcode_scanner_reduce_enabled ?? false);

const focusBarcodeInput = async () => {
  await nextTick();
  barcodeInput.value?.focus();
};

const loadSettings = async () => {
  if (!authState.accessToken) return;
  try {
    settings.value = await fetchSettings(authState.accessToken);
  } catch (err: any) {
    pushToast({
      title: 'Einstellungen',
      description: 'Systemverhalten konnte nicht geladen werden.',
      variant: 'warning'
    });
  }
};

const statusTone = (item: MovementRecord) => {
  const state = deriveIssueState(item);
  switch (state) {
    case 'auth':
      return 'warning';
    case 'blocked':
      return 'danger';
    case 'retrying':
      return 'info';
    case 'waiting':
      return 'warning';
    default:
      return item.status === 'sent' ? 'success' : 'neutral';
  }
};

const statusLabel = (item: MovementRecord) => {
  const state = deriveIssueState(item);
  switch (state) {
    case 'auth':
      return 'Anmeldung nötig';
    case 'blocked':
      return 'Blockiert';
    case 'retrying':
      return 'Retry geplant';
    case 'waiting':
      return 'Wartet';
    default:
      if (item.status === 'sent') return 'Gesendet';
      if (item.status === 'sending') return 'Senden...';
      return 'Wartet';
  }
};

const resetForm = async () => {
  barcode.value = '';
  qty.value = 1;
  note.value = '';
  await focusBarcodeInput();
};

const submitMovement = async (type: 'IN' | 'OUT') => {
  if (!hasWriteAccess.value) {
    pushToast({
      title: 'Keine Berechtigung',
      description: 'Nur Owner/Admin dürfen Lagerbewegungen buchen.',
      variant: 'warning'
    });
    return;
  }
  if (!barcode.value.trim()) {
    pushToast({
      title: 'Barcode fehlt',
      description: 'Bitte scanne oder tippe einen Barcode ein.',
      variant: 'warning'
    });
    barcodeInput.value?.focus();
    return;
  }

  const normalizedQty = Math.max(1, Number(qty.value) || 1);
  submitting.value[type] = true;

  try {
    await enqueueMovement({
      type,
      barcode: barcode.value,
      qty: normalizedQty,
      note: note.value
    });
    await resetForm();
  } finally {
    submitting.value[type] = false;
  }
};

const handleBarcodeEnter = (event: KeyboardEvent) => {
  if (!barcodeScannerReduceEnabled.value) return;
  event.preventDefault();
  void submitMovement('OUT');
};

const handleClearSent = async () => {
  if (clearing.value) return;
  clearing.value = true;
  try {
    await clearSent();
  } finally {
    clearing.value = false;
  }
};

onMounted(() => {
  void focusBarcodeInput();
});

watch(
  () => authState.accessToken,
  (value) => {
    if (value) {
      void loadSettings();
    }
  },
  { immediate: true }
);

watch(hasWriteAccess, (value) => {
  if (value) {
    void focusBarcodeInput();
  }
});
</script>

<template>
  <UiPage>
    <UiSection title="Lagerbewegungen" subtitle="Buche Bestandsänderungen auch offline. Die Queue synchronisiert automatisch.">
      <UiToolbar>
        <template #start>
          <StatusPill :label="isOnline ? 'Online' : 'Offline'" :tone="isOnline ? 'success' : 'warning'" />
        </template>
        <template #end>
          <div class="action-row">
            <button class="btnGhost small" type="button" @click="syncNow" :disabled="syncing" :aria-busy="syncing">
              <span class="btn-label">
                <span v-if="syncing" class="btn-spinner" aria-hidden="true"></span>
                Sync jetzt
              </span>
            </button>
            <button
              class="btnGhost small"
              type="button"
              @click="handleClearSent"
              :disabled="clearing"
              :aria-busy="clearing"
            >
              <span class="btn-label">
                <span v-if="clearing" class="btn-spinner" aria-hidden="true"></span>
                Queue leeren
              </span>
            </button>
            <RouterLink class="btnGhost small badge-button" :to="{ name: 'sync-probleme' }">
              Fehler ansehen
              <span class="badge-counter" v-if="issueCount">{{ issueCount }}</span>
            </RouterLink>
          </div>
        </template>
      </UiToolbar>

      <div class="form-grid">
        <div class="field">
          <label for="barcode">Barcode</label>
          <input
            id="barcode"
            ref="barcodeInput"
            v-model="barcode"
            class="input"
            type="text"
            autocomplete="off"
            placeholder="Barcode scannen oder eingeben"
            :disabled="!hasWriteAccess"
            autofocus
            @keydown.enter="handleBarcodeEnter"
          />
        </div>
        <div class="field">
          <label for="qty">Menge</label>
          <input
            id="qty"
            v-model.number="qty"
            class="input"
            type="number"
            min="1"
            step="1"
            placeholder="Anzahl"
            :disabled="!hasWriteAccess"
          />
        </div>
        <div class="field">
          <label for="note">Notiz (optional)</label>
          <input
            id="note"
            v-model="note"
            class="input"
            type="text"
            placeholder="Chargeninfo oder Kommentar"
            :disabled="!hasWriteAccess"
          />
        </div>
      </div>

      <div class="action-row">
        <button
          class="btnGhost small"
          type="button"
          @click="submitMovement('OUT')"
          :disabled="!hasWriteAccess || submitting.OUT"
          :aria-busy="submitting.OUT"
        >
          <span class="btn-label">
            <span v-if="submitting.OUT" class="btn-spinner" aria-hidden="true"></span>
            Bestand reduzieren
          </span>
        </button>
        <button
          class="btnPrimary small"
          type="button"
          @click="submitMovement('IN')"
          :disabled="!hasWriteAccess || submitting.IN"
          :aria-busy="submitting.IN"
        >
          <span class="btn-label">
            <span v-if="submitting.IN" class="btn-spinner" aria-hidden="true"></span>
            Bestand erhöhen
          </span>
        </button>
      </div>

      <div class="callout">
        <span>
          Wartende Einträge: {{ hasPending ? 'Ja' : 'Nein' }} • Probleme: {{ issueCount }}
          <span v-if="lastSyncError">• Letzte Meldung: {{ lastSyncError }}</span>
        </span>
        <RouterLink class="link" :to="{ name: 'sync-probleme' }">Fehlerzentrum öffnen</RouterLink>
      </div>

      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>Zeitpunkt</th>
              <th>Typ</th>
              <th>Barcode</th>
              <th>Menge</th>
              <th>Notiz</th>
              <th>Status</th>
              <th>Versuche</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in recentMovements" :key="item.id">
              <td>{{ new Date(item.created_at).toLocaleString() }}</td>
              <td>{{ item.type === 'IN' ? 'Bestand erhöhen' : 'Bestand reduzieren' }}</td>
              <td>{{ item.barcode }}</td>
              <td>{{ item.qty }}</td>
              <td>{{ item.note || '—' }}</td>
              <td>
                <StatusPill :label="statusLabel(item)" :tone="statusTone(item)" />
              </td>
              <td>
                <span v-if="item.status === 'failed' && item.last_error" class="text-danger">
                  {{ item.retries }} ({{ item.last_error }})
                </span>
                <span v-else>{{ item.retries }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UiSection>
  </UiPage>
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

.callout {
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.75rem;
  margin: 0.5rem 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.callout .link {
  font-weight: 600;
}
</style>
