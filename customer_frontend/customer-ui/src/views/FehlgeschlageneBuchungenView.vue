<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import StatusPill from '@/components/common/StatusPill.vue';
import UiEmptyState from '@/components/ui/UiEmptyState.vue';
import UiPage from '@/components/ui/UiPage.vue';
import UiSection from '@/components/ui/UiSection.vue';
import { useMovementQueue, type MovementInput, type MovementRecord } from '@/composables/useMovementQueue';
import { useOnlineStatus } from '@/composables/useOnlineStatus';

const router = useRouter();
const {
  movements,
  blockedEntries,
  syncNow,
  retryEntry,
  deleteEntry,
  replaceEntry,
  deriveIssueState,
  hasPending
} = useMovementQueue();
const { isOnline } = useOnlineStatus();

const issueEntries = computed(() => movements.value.filter((m) => m.status === 'failed' || m.status === 'queued'));
const editing = ref<MovementRecord | null>(null);
const editForm = reactive<MovementInput>({
  type: 'OUT',
  barcode: '',
  qty: 1,
  note: ''
});
const formErrors = reactive<{ barcode: string; qty: string }>({ barcode: '', qty: '' });
const hasEditErrors = computed(() => Boolean(formErrors.barcode || formErrors.qty));

const statusTone = (entry: MovementRecord) => {
  switch (deriveIssueState(entry)) {
    case 'auth':
      return 'warning';
    case 'blocked':
      return 'danger';
    case 'retrying':
      return 'info';
    case 'waiting':
      return 'warning';
    default:
      return 'neutral';
  }
};

const statusLabel = (entry: MovementRecord) => {
  switch (deriveIssueState(entry)) {
    case 'auth':
      return 'Anmeldung nötig';
    case 'blocked':
      return 'Blockiert';
    case 'retrying':
      return 'Retry geplant';
    case 'waiting':
      return 'Wartet';
    default:
      return 'Offen';
  }
};

const shortMessage = (entry: MovementRecord) => entry.last_error || 'Wartet auf Sync.';

const typeLabel = (entry: MovementRecord) => (entry.type === 'IN' ? 'Bestand erhöhen' : 'Bestand reduzieren');

const startEdit = (entry: MovementRecord) => {
  editing.value = entry;
  editForm.type = entry.type;
  editForm.barcode = entry.barcode;
  editForm.qty = entry.qty;
  editForm.note = entry.note || '';
  formErrors.barcode = '';
  formErrors.qty = '';
};

const resetEdit = () => {
  editing.value = null;
  editForm.type = 'OUT';
  editForm.barcode = '';
  editForm.qty = 1;
  editForm.note = '';
  formErrors.barcode = '';
  formErrors.qty = '';
};

watch(
  () => editForm.barcode,
  (value) => {
    if (formErrors.barcode && value.trim()) {
      formErrors.barcode = '';
    }
  }
);

watch(
  () => editForm.qty,
  (value) => {
    if (formErrors.qty && value && value >= 1) {
      formErrors.qty = '';
    }
  }
);

const handleRetry = async (entry: MovementRecord) => {
  await retryEntry(entry.id);
};

const handleDelete = async (entry: MovementRecord) => {
  await deleteEntry(entry.id);
  if (editing.value?.id === entry.id) {
    resetEdit();
  }
};

const validateEditForm = () => {
  formErrors.barcode = editForm.barcode.trim() ? '' : 'Barcode darf nicht leer sein.';
  formErrors.qty = editForm.qty && editForm.qty >= 1 ? '' : 'Menge muss mindestens 1 sein.';
  return !formErrors.barcode && !formErrors.qty;
};

const handleEditSave = async () => {
  if (!editing.value) return;
  if (!validateEditForm()) return;
  await replaceEntry(editing.value.id, {
    type: editForm.type,
    barcode: editForm.barcode.trim(),
    qty: Math.max(1, Number(editForm.qty) || 1),
    note: editForm.note?.trim() || undefined
  });
  resetEdit();
  await syncNow();
};

const goToLogin = () => {
  router.push({ name: 'login', query: { redirect: '/sync-probleme' } });
};

const emptyStateText = computed(() =>
  isOnline.value
    ? 'Keine fehlgeschlagenen Buchungen. Alles synchron.'
    : 'Offline. Wartende Buchungen werden hier angezeigt.'
);
</script>

<template>
  <UiPage>
    <UiSection
      title="Fehlgeschlagene Buchungen"
      subtitle="Zentrale Übersicht für blockierte oder wartende Queue-Einträge – ohne Toast-Spam."
    >
      <template #actions>
        <div class="action-row">
          <span class="badge neutral">Blockiert: {{ blockedEntries.length }}</span>
          <span class="badge neutral">Wartend: {{ hasPending ? 'Ja' : 'Nein' }}</span>
          <span class="badge" :class="isOnline ? 'success' : 'warning'">
            {{ isOnline ? 'Online' : 'Offline' }}
          </span>
          <button class="btnGhost small" type="button" @click="syncNow" :disabled="!isOnline">
            Sync jetzt
          </button>
        </div>
      </template>

      <div class="issues-grid">
        <div class="issues-list">
          <article v-for="entry in issueEntries" :key="entry.id" class="card issue-card">
            <header class="issue-header">
              <div>
                <p class="issue-meta">{{ new Date(entry.created_at).toLocaleString() }}</p>
                <h3 class="issue-title">{{ typeLabel(entry) }}</h3>
                <p class="issue-meta">Barcode {{ entry.barcode }} • Menge {{ entry.qty }}</p>
              </div>
              <StatusPill :label="statusLabel(entry)" :tone="statusTone(entry)" />
            </header>
            <p class="issue-message">{{ shortMessage(entry) }}</p>

            <div class="issue-actions">
              <button
                v-if="deriveIssueState(entry) === 'auth'"
                type="button"
                class="btnPrimary small"
                @click="goToLogin"
              >
                Neu anmelden
              </button>
              <button
                v-if="deriveIssueState(entry) === 'auth'"
                type="button"
                class="btnGhost small"
                @click="syncNow"
                :disabled="!isOnline"
              >
                Nach Login synchronisieren
              </button>

              <button
                v-if="deriveIssueState(entry) === 'blocked'"
                type="button"
                class="btnPrimary small"
                @click="startEdit(entry)"
              >
                Bearbeiten
              </button>
              <button
                v-if="deriveIssueState(entry) === 'blocked'"
                type="button"
                class="btnGhost small"
                @click="handleDelete(entry)"
              >
                Löschen
              </button>

              <button
                v-if="['retrying', 'waiting'].includes(deriveIssueState(entry))"
                type="button"
                class="btnPrimary small"
                @click="handleRetry(entry)"
                :disabled="entry.status === 'sending'"
              >
                Jetzt erneut versuchen
              </button>
              <button
                v-if="['retrying', 'waiting'].includes(deriveIssueState(entry))"
                type="button"
                class="btnGhost small"
                @click="handleDelete(entry)"
              >
                Entfernen
              </button>
            </div>

            <details class="issue-details">
              <summary>Technische Details</summary>
              <dl>
                <div class="row">
                  <dt>Status</dt>
                  <dd>{{ statusLabel(entry) }}</dd>
                </div>
                <div class="row">
                  <dt>HTTP Status</dt>
                  <dd>{{ entry.status_code ?? '–' }}</dd>
                </div>
                <div class="row">
                  <dt>Letzte Meldung</dt>
                  <dd>{{ entry.last_error || 'Keine Meldung' }}</dd>
                </div>
                <div class="row" v-if="entry.error_detail">
                  <dt>Detail</dt>
                  <dd>{{ entry.error_detail }}</dd>
                </div>
                <div class="row">
                  <dt>Versuche</dt>
                  <dd>
                    {{ entry.retries }}
                    <span v-if="deriveIssueState(entry) === 'retrying'">• Retry geplant</span>
                  </dd>
                </div>
                <div class="row" v-if="entry.note">
                  <dt>Notiz</dt>
                  <dd>{{ entry.note }}</dd>
                </div>
              </dl>
            </details>
          </article>

          <UiEmptyState v-if="!issueEntries.length" :title="'Keine Fehler vorhanden'" :description="emptyStateText" />
        </div>

        <aside class="card edit-card">
          <header class="cardHeader">
            <div>
              <div class="cardTitle">{{ editing ? 'Buchung anpassen' : 'Aktionen' }}</div>
              <div class="cardHint">
                {{ editing ? 'Werte prüfen und neu einreihen.' : 'Wähle einen Eintrag für Details.' }}
              </div>
            </div>
          </header>

          <div v-if="editing" class="edit-form stack">
            <label class="field">
              <span>Typ</span>
              <select class="input" v-model="editForm.type">
                <option value="OUT">Bestand reduzieren</option>
                <option value="IN">Bestand erhöhen</option>
              </select>
            </label>

            <label class="field">
              <span>Barcode</span>
              <input class="input" v-model="editForm.barcode" type="text" autocomplete="off" />
              <p v-if="formErrors.barcode" class="field-error">{{ formErrors.barcode }}</p>
            </label>

            <label class="field">
              <span>Menge</span>
              <input class="input" v-model.number="editForm.qty" type="number" min="1" step="1" />
              <p v-if="formErrors.qty" class="field-error">{{ formErrors.qty }}</p>
            </label>

            <label class="field">
              <span>Notiz</span>
              <input class="input" v-model="editForm.note" type="text" />
            </label>

            <div class="action-row">
              <button class="btnPrimary small" type="button" @click="handleEditSave" :disabled="hasEditErrors">
                Speichern &amp; neu senden
              </button>
              <button class="btnGhost small" type="button" @click="resetEdit">Abbrechen</button>
            </div>
          </div>

          <div v-else class="stack helper-text">
            <p>• 4xx Fehler werden blockiert. Über “Bearbeiten” kannst du Barcode, Menge oder Notiz korrigieren.</p>
            <p>• 5xx/Netz werden automatisch erneut versucht. Du kannst jederzeit “Jetzt erneut versuchen” drücken.</p>
            <p>• Bei 401 hilft “Neu anmelden” und danach “Sync jetzt”.</p>
          </div>
        </aside>
      </div>
    </UiSection>
  </UiPage>
</template>

<style scoped>
.issues-grid {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 1rem;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.issue-card {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.issue-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.issue-title {
  margin: 0;
  font-size: 1rem;
}

.issue-meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.issue-message {
  margin: 0;
  color: var(--text-default);
}

.issue-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.issue-details {
  background: var(--surface-muted);
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
}

.issue-details summary {
  cursor: pointer;
  color: var(--text-muted);
}

.issue-details dl {
  margin: 0.5rem 0 0;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 0.5rem 0.75rem;
}

.issue-details dt {
  color: var(--text-muted);
  font-weight: 600;
}

.issue-details dd {
  margin: 0;
}

.edit-card {
  padding: 1rem;
  position: sticky;
  top: 1rem;
  align-self: start;
}

.edit-form {
  margin-top: 0.5rem;
}

.helper-text p {
  margin: 0;
  color: var(--text-muted);
}

.field-error {
  margin: 0.25rem 0 0;
  color: var(--danger, #b42318);
  font-size: 0.85rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  font-size: 0.875rem;
}

.badge.success {
  background: #e0f7ef;
  color: #146c43;
  border-color: #a4e4cb;
}

.badge.warning {
  background: #fff7e6;
  color: #a86c00;
  border-color: #ffd48a;
}

.badge.neutral {
  background: var(--surface-muted);
  color: var(--text-default);
}

@media (max-width: 1024px) {
  .issues-grid {
    grid-template-columns: 1fr;
  }

  .edit-card {
    position: static;
  }
}
</style>
