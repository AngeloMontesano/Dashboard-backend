import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { openDB, type IDBPDatabase } from 'idb';
import { postInventoryMovement, type MovementPayload } from '@/api/inventory';
import { useAuth } from './useAuth';
import { useToast } from './useToast';

export type MovementStatus = 'queued' | 'sending' | 'sent' | 'failed';

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

export function useMovementQueue() {
  const records = ref<MovementRecord[]>([]);
  const syncing = ref(false);
  const lastSyncError = ref<string | null>(null);
  const syncInterval = ref<number | null>(null);
  const { push: pushToast } = useToast();
  const { state: authState } = useAuth();

  const loadRecords = async () => {
    const db = await openDatabase();
    const all = await db.getAll(STORE_NAME);
    records.value = all.sort((a, b) => a.created_at.localeCompare(b.created_at));
  };

  const persistRecord = async (record: MovementRecord) => {
    const db = await openDatabase();
    await db.put(STORE_NAME, record);
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

  const updateRecord = async (updated: MovementRecord) => {
    await persistRecord(updated);
    const index = records.value.findIndex((r) => r.id === updated.id);
    if (index >= 0) {
      records.value.splice(index, 1, updated);
    } else {
      records.value.push(updated);
    }
  };

  const pendingEntries = computed(() =>
    records.value.filter((r) => r.status === 'queued' || r.status === 'failed')
  );

  const hasPending = computed(() => pendingEntries.value.length > 0);

  const movementList = computed(() =>
    [...records.value].sort((a, b) => b.created_at.localeCompare(a.created_at))
  );

  const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const sendEntry = async (entry: MovementRecord) => {
    if (!authState.accessToken) {
      const retries = Math.min(MAX_RETRIES, entry.retries + 1);
      const failed: MovementRecord = {
        ...entry,
        status: 'failed',
        retries,
        last_error: 'Keine aktive Anmeldung'
      };
      await updateRecord(failed);
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
        last_error: undefined
      };
      await updateRecord(sent);
      return true;
    } catch (error) {
      const retries = Math.min(MAX_RETRIES, entry.retries + 1);
      const failed: MovementRecord = {
        ...entry,
        status: 'failed',
        retries,
        last_error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      };
      await updateRecord(failed);
      return false;
    }
  };

  const processQueue = async () => {
    if (syncing.value || (typeof navigator !== 'undefined' && !navigator.onLine)) return;
    if (pendingEntries.value.length === 0) return;

    syncing.value = true;
    lastSyncError.value = null;

    const sorted = [...pendingEntries.value].sort((a, b) =>
      a.created_at.localeCompare(b.created_at)
    );

    for (const entry of sorted) {
      const delay = Math.min(30000, 1000 * 2 ** entry.retries);
      if (entry.retries > 0) {
        await wait(delay);
      }

      const success = await sendEntry(entry);
      if (!success) {
        lastSyncError.value = entry.last_error ?? 'Fehler beim Senden';
      }
    }

    syncing.value = false;
  };

  const enqueueMovement = async (input: MovementInput) => {
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
      pushToast({
        title: 'Bewegung versendet',
        description: 'Die Buchung wurde direkt übertragen.',
        variant: 'success'
      });
    } else {
      pushToast({
        title: 'Offline gespeichert',
        description: 'Die Buchung wurde in die Warteschlange gelegt.',
        variant: 'info'
      });
    }
  };

  const syncNow = async () => {
    await processQueue();
    if (!hasPending.value && (typeof navigator === 'undefined' || navigator.onLine)) {
      pushToast({
        title: 'Queue synchronisiert',
        description: 'Alle Bewegungen wurden verarbeitet.',
        variant: 'success'
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
    processQueue();
  };

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

  onMounted(async () => {
    await loadRecords();
    startInterval();
    window.addEventListener('online', handleOnline);
  });

  onUnmounted(() => {
    stopInterval();
    window.removeEventListener('online', handleOnline);
  });

  return {
    movements: movementList,
    hasPending,
    syncing,
    lastSyncError,
    enqueueMovement,
    syncNow,
    clearSent,
    reload: loadRecords
  };
}
