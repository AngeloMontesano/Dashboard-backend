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
  lastSyncError
} = useMovementQueue();
const { push: pushToast } = useToast();

const recentMovements = computed(() => movements.value.slice(0, 30));

const statusTone = (status: MovementRecord['status']) => {
  switch (status) {
    case 'sent':
      return 'success';
    case 'sending':
      return 'info';
    case 'failed':
      return 'danger';
    case 'queued':
    default:
      return 'warning';
  }
};

const statusLabel = (status: MovementRecord['status']) => {
  switch (status) {
    case 'sent':
      return 'Gesendet';
    case 'sending':
      return 'Senden...';
    case 'failed':
      return 'Fehlgeschlagen';
    case 'queued':
    default:
      return 'Wartend';
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

      <p v-if="hasPending" class="section-subtitle text-small">
        Wartende Einträge: {{ hasPending ? 'Ja' : 'Nein' }} | Status: {{ syncing ? 'Sync läuft' : 'Bereit' }}
      </p>
      <p v-if="lastSyncError" class="section-subtitle text-small text-danger">
        Letzter Fehler: {{ lastSyncError }}
      </p>

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
                <StatusPill :label="statusLabel(item.status)" :tone="statusTone(item.status)" />
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
