import type { ErrorCategory } from './errorClassify';

export const TELEMETRY_EVENT_NAMES = {
  authRefresh: 'customer-auth-refresh',
  movementQueue: 'movement-queue-event'
} as const;

export type TelemetryEventName = (typeof TELEMETRY_EVENT_NAMES)[keyof typeof TELEMETRY_EVENT_NAMES];

export type AuthRefreshEvent = {
  status: 'success' | 'failed';
  reason?: string;
  at: string;
};

export type AuthRefreshEventInput = Omit<AuthRefreshEvent, 'at'> & { at?: string };

export type MovementQueueTelemetryEvent =
  | { type: 'enqueue' | 'retry' | 'delete' | 'replace'; id: string; at: string }
  | { type: 'send_success'; id: string; retries: number; at: string }
  | { type: 'send_failed'; id: string; retries: number; category?: ErrorCategory; message?: string; at: string };

type WithOptionalTimestamp<T> = T extends { at: string } ? Omit<T, 'at'> & { at?: string } : T;

export type MovementQueueEventInput = WithOptionalTimestamp<MovementQueueTelemetryEvent>;

const AUTH_REFRESH_LOG_KEY = 'customer_auth_refresh_log';
const QUEUE_EVENT_KEY = 'movement_queue_events';

const safeParse = <T>(raw: string | null, fallback: T): T => {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
};

const emitTelemetry = (name: TelemetryEventName, detail: unknown) => {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent(name, { detail }));
};

const appendLogEntry = <T>(key: string, limit: number, entry: T) => {
  if (typeof sessionStorage === 'undefined') return;
  try {
    const existing = safeParse<T[]>(sessionStorage.getItem(key), []);
    const next = [...existing, entry].slice(-limit);
    sessionStorage.setItem(key, JSON.stringify(next));
  } catch {
    // ignore logging failures
  }
};

const enrichWithTimestamp = <T extends { at?: string }>(entry: T) => ({
  ...entry,
  at: entry.at || new Date().toISOString()
});

export function readAuthRefreshLog(): AuthRefreshEvent[] {
  if (typeof sessionStorage === 'undefined') return [];
  return safeParse<AuthRefreshEvent[]>(sessionStorage.getItem(AUTH_REFRESH_LOG_KEY), []);
}

export function appendAuthRefreshEvent(event: AuthRefreshEventInput): AuthRefreshEvent {
  const enriched = enrichWithTimestamp(event);
  appendLogEntry(AUTH_REFRESH_LOG_KEY, 10, enriched);
  emitTelemetry(TELEMETRY_EVENT_NAMES.authRefresh, enriched);
  return enriched as AuthRefreshEvent;
}

export function readQueueEventLog(): MovementQueueTelemetryEvent[] {
  if (typeof sessionStorage === 'undefined') return [];
  return safeParse<MovementQueueTelemetryEvent[]>(sessionStorage.getItem(QUEUE_EVENT_KEY), []);
}

export function appendQueueEvent(event: MovementQueueEventInput): MovementQueueTelemetryEvent {
  const enriched = enrichWithTimestamp(event);
  appendLogEntry(QUEUE_EVENT_KEY, 25, enriched);
  emitTelemetry(TELEMETRY_EVENT_NAMES.movementQueue, enriched);
  return enriched as MovementQueueTelemetryEvent;
}

export function subscribeTelemetry<T>(type: TelemetryEventName, handler: (payload: T) => void) {
  if (typeof window === 'undefined') return () => {};
  const listener = (event: Event) => {
    const customEvent = event as CustomEvent;
    handler(customEvent.detail as T);
  };
  window.addEventListener(type, listener as EventListener);
  return () => window.removeEventListener(type, listener as EventListener);
}

export function readTelemetrySnapshot() {
  return {
    authRefresh: readAuthRefreshLog(),
    movementQueue: readQueueEventLog()
  };
}

export function downloadTelemetrySnapshot(filename = 'customer-telemetry.json') {
  if (typeof document === 'undefined') return null;
  const snapshot = readTelemetrySnapshot();
  const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  return snapshot;
}
