import { computed, effectScope, ref, watch } from 'vue';
import { openDB, type IDBPDatabase } from 'idb';
import { postInventoryMovement, type MovementPayload } from '@/api/inventory';
import { api } from '@/api/client';
import { useAuth } from './useAuth';
import { useToast } from './useToast';
import { classifyError, type ErrorActionHint, type ErrorCategory } from '@/utils/errorClassify';

export type MovementStatus = 'queued' | 'sending' | 'sent' | 'failed';
export type UiIssueState = 'waiting' | 'blocked' | 'auth' | 'retrying' | 'none';

export type MovementRecord = {
  id: string;
  created_at: string;
  type: 'IN' | 'OUT';
  barcode: string;
  qty: number;
  note?: string;
  status: MovementStatus;
  retries: number;
  last_error?: string;
  status_code?: number;
  error_category?: ErrorCategory;
  error_detail?: string;
  action_hints?: ErrorActionHint[];
  stop_retry?: boolean;
};

export type MovementInput = {
  type: 'IN' | 'OUT';
  barcode: string;
  qty: number;
  note?: string;
};

const DB_NAME = 'customer_app';
const STORE_NAME = 'movement_queue';
const MAX_RETRIES = 10;

let dbPromise: Promise<IDBPDatabase> | null = null;
let initPromise: Promise<void> | null = null;
let watchersStarted = false;
let onlineHandlerAttached = false;

const generateId = () =>
  typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

const openDatabase = async () => {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        }
      }
    });
  }
  return dbPromise;
};

const records = ref<MovementRecord[]>([]);
const syncing = ref(false);
const lastSyncError = ref<string | null>(null);
const syncInterval = ref<number | null>(null);
const { push: pushToast } = useToast();
const { state: authState, logout } = useAuth();
const hasWriteAccess = computed(() => ['owner', 'admin'].includes(authState.role));

const pendingEntries = computed(() =>
  records.value.filter((r) => (r.status === 'queued' || r.status === 'failed') && !r.stop_retry && r.retries < MAX_RETRIES)
);

const failedEntries = computed(() => records.value.filter((r) => r.status === 'failed'));
const blockedEntries = computed(() => failedEntries.value.filter((r) => r.stop_retry));
const attentionCount = computed(() => pendingEntries.value.length + blockedEntries.value.length);

const hasPending = computed(() => pendingEntries.value.length > 0);

const movementList = computed(() => [...records.value].sort((a, b) => b.created_at.localeCompare(a.created_at)));

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const loadRecords = async () => {
  const db = await openDatabase();
  const all = await db.getAll(STORE_NAME);
  records.value = all.sort((a, b) => a.created_at.localeCompare(b.created_at));
};

const persistRecord = async (record: MovementRecord) => {
  const db = await openDatabase();
  await db.put(STORE_NAME, record);
};

const updateRecord = async (updated: MovementRecord) => {
  await persistRecord(updated);
  const index = records.value.findIndex((r) => r.id === updated.id);
  if (index >= 0) {
    records.value.splice(index, 1, updated);
  } else {
    records.value.push(updated);
  }
};

const removeSent = async () => {
  const db = await openDatabase();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  for (const entry of records.value.filter((r) => r.status === 'sent')) {
    await store.delete(entry.id);
  }
  await tx.done;
  await loadRecords();
};

const deriveIssueState = (entry: MovementRecord): UiIssueState => {
  if (entry.status === 'failed') {
    if (entry.error_category === 'auth') return 'auth';
    if (entry.stop_retry) return 'blocked';
    return 'retrying';
  }
  if (entry.status === 'queued') return 'waiting';
  return 'none';
};

const sendEntry = async (entry: MovementRecord) => {
  if (!authState.accessToken || !hasWriteAccess.value) {
    const retries = Math.min(MAX_RETRIES, entry.retries + 1);
    const failed: MovementRecord = {
      ...entry,
      status: 'failed',
      retries,
      last_error: !authState.accessToken ? 'Keine aktive Anmeldung' : 'Keine Berechtigung',
      error_category: !authState.accessToken ? 'auth' : 'client',
      action_hints: !authState.accessToken ? ['login', 'retry'] : ['edit', 'delete'],
      stop_retry: true
    };
    await updateRecord(failed);
    lastSyncError.value = failed.last_error || null;
    return false;
  }

  const payload: MovementPayload = {
    client_tx_id: entry.id,
    type: entry.type,
    barcode: entry.barcode,
    qty: entry.qty,
    note: entry.note,
    created_at: entry.created_at
  };

  const sending: MovementRecord = { ...entry, status: 'sending' };
  await updateRecord(sending);

  try {
    await postInventoryMovement(authState.accessToken, payload);
    const sent: MovementRecord = {
      ...sending,
      status: 'sent',
      retries: entry.retries,
      last_error: undefined,
      error_category: undefined,
      error_detail: undefined,
      status_code: undefined,
      action_hints: undefined,
      stop_retry: false
    };
    await updateRecord(sent);
    return true;
  } catch (error: any) {
    const classified = classifyError(error);
    const retries = Math.min(MAX_RETRIES, entry.retries + 1);
    const failed: MovementRecord = {
      ...entry,
      status: 'failed',
      retries,
      last_error: classified.userMessage,
      status_code: classified.status,
      error_category: classified.category,
      error_detail: classified.detailMessage,
      action_hints: classified.actionHints,
      stop_retry: classified.category === 'client' || classified.category === 'auth'
    };
    await updateRecord(failed);
    lastSyncError.value = classified.userMessage;
    if (classified.category === 'auth') {
      logout();
      delete api.defaults.headers.common.Authorization;
    }
    return !(classified.category === 'client' || classified.category === 'auth');
  }
};

const processQueue = async () => {
  if (syncing.value || (typeof navigator !== 'undefined' && !navigator.onLine)) return;
  if (pendingEntries.value.length === 0) return;

  syncing.value = true;
  lastSyncError.value = null;

  const sorted = [...pendingEntries.value].sort((a, b) => a.created_at.localeCompare(b.created_at));

  for (const entry of sorted) {
    const delay = Math.min(30000, 1000 * 2 ** entry.retries);
    if (entry.retries > 0) {
      await wait(delay);
    }

    const success = await sendEntry(entry);
    if (!success) {
      const updated = records.value.find((r) => r.id === entry.id);
      lastSyncError.value = updated?.last_error ?? entry.last_error ?? 'Fehler beim Senden';
    }
  }

  syncing.value = false;
};

const enqueueMovement = async (input: MovementInput, options?: { silent?: boolean }) => {
  await ensureInitialized();
  const now = new Date().toISOString();
  const record: MovementRecord = {
    id: generateId(),
    created_at: now,
    type: input.type,
    barcode: input.barcode.trim(),
    qty: input.qty,
    note: input.note?.trim() || undefined,
    status: 'queued',
    retries: 0
  };

  await persistRecord(record);
  await loadRecords();

  if (typeof navigator !== 'undefined' && navigator.onLine) {
    await processQueue();
    if (!options?.silent) {
      pushToast({
        title: 'Bewegung versendet',
        description: 'Die Buchung wurde direkt übertragen.',
        variant: 'success',
        onceKey: 'movement-sent'
      });
    }
  } else if (!options?.silent) {
    pushToast({
      title: 'Offline gespeichert',
      description: 'Die Buchung wurde in die Warteschlange gelegt.',
      variant: 'info'
    });
  }
};

const retryEntry = async (id: string) => {
  await ensureInitialized();
  const entry = records.value.find((r) => r.id === id);
  if (!entry) return;
  const retrying: MovementRecord = {
    ...entry,
    status: 'queued',
    stop_retry: false,
    last_error: undefined,
    error_category: undefined,
    error_detail: undefined
  };
  await updateRecord(retrying);
  await processQueue();
};

const deleteEntry = async (id: string) => {
  await ensureInitialized();
  const db = await openDatabase();
  await db.delete(STORE_NAME, id);
  records.value = records.value.filter((r) => r.id !== id);
};

const replaceEntry = async (id: string, input: MovementInput) => {
  await ensureInitialized();
  await deleteEntry(id);
  await enqueueMovement(input, { silent: true });
};

const syncNow = async () => {
  await ensureInitialized();
  await processQueue();
  if (!hasPending.value && (typeof navigator === 'undefined' || navigator.onLine)) {
    pushToast({
      title: 'Queue synchronisiert',
      description: 'Alle Bewegungen wurden verarbeitet.',
      variant: 'success',
      onceKey: 'queue-sync-success'
    });
  }
};

const clearSent = async () => {
  await removeSent();
  pushToast({
    title: 'Liste bereinigt',
    description: 'Erfolgreich gesendete Einträge wurden entfernt.',
    variant: 'info'
  });
};

const startInterval = () => {
  if (syncInterval.value || pendingEntries.value.length === 0) return;
  syncInterval.value = window.setInterval(processQueue, 10000);
};

const stopInterval = () => {
  if (syncInterval.value) {
    clearInterval(syncInterval.value);
    syncInterval.value = null;
  }
};

const handleOnline = () => {
  void processQueue();
};

const startWatchers = () => {
  if (watchersStarted) return;
  watchersStarted = true;
  const scope = effectScope(true);
  scope.run(() => {
    watch(
      hasPending,
      (pending) => {
        if (pending) {
          startInterval();
        } else {
          stopInterval();
        }
      },
      { immediate: true }
    );
  });
};

const ensureInitialized = async () => {
  if (!initPromise) {
    initPromise = (async () => {
      await loadRecords();
      startInterval();
      if (typeof window !== 'undefined' && !onlineHandlerAttached) {
        window.addEventListener('online', handleOnline);
        onlineHandlerAttached = true;
      }
      startWatchers();
    })();
  }
  return initPromise;
};

void ensureInitialized();

export function useMovementQueue() {
  return {
    movements: movementList,
    hasPending,
    syncing,
    lastSyncError,
    enqueueMovement,
    syncNow,
    clearSent,
    reload: loadRecords,
    retryEntry,
    deleteEntry,
    replaceEntry,
    failedEntries,
    blockedEntries,
    attentionCount,
    deriveIssueState
  };
}
