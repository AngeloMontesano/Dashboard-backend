<script setup lang="ts">
import { computed, nextTick, ref } from 'vue';
import StatusPill from '@/components/common/StatusPill.vue';
import { useMovementQueue, type MovementRecord } from '@/composables/useMovementQueue';
import { useOnlineStatus } from '@/composables/useOnlineStatus';
import { useToast } from '@/composables/useToast';
import { useAuth } from '@/composables/useAuth';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import UiToolbar from '@/components/ui/UiToolbar.vue';
import { RouterLink } from 'vue-router';

const barcode = ref('');
const qty = ref<number>(1);
const note = ref('');
const barcodeInput = ref<HTMLInputElement | null>(null);

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
  await nextTick();
  barcodeInput.value?.focus();
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

  await enqueueMovement({
    type,
    barcode: barcode.value,
    qty: normalizedQty,
    note: note.value
  });

  await resetForm();
};
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
            <button class="btnGhost small" type="button" @click="syncNow" :disabled="syncing">
              Sync jetzt
            </button>
            <button class="btnGhost small" type="button" @click="clearSent">
              Queue leeren
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
        <button class="btnGhost small" type="button" @click="submitMovement('OUT')" :disabled="!hasWriteAccess">
          Bestand reduzieren
        </button>
        <button class="btnPrimary small" type="button" @click="submitMovement('IN')" :disabled="!hasWriteAccess">
          Bestand erhöhen
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
