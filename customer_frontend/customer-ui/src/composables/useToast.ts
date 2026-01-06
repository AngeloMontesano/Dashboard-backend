import { reactive, readonly } from 'vue';

export type ToastVariant = 'info' | 'success' | 'warning' | 'danger';

export type ToastMessage = {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
  duration?: number;
  onceKey?: string;
};

type ToastState = {
  toasts: ToastMessage[];
};

const state: ToastState = reactive({
  toasts: []
});

const generateId = () =>
  typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

const seenOnce = new Set<string>();

export function useToast() {
  const push = (toast: Omit<ToastMessage, 'id'>) => {
    if (toast.onceKey && seenOnce.has(toast.onceKey)) return toast.onceKey;
    const id = generateId();
    const entry: ToastMessage = { id, duration: 4000, ...toast };
    state.toasts.push(entry);
    if (entry.onceKey) {
      seenOnce.add(entry.onceKey);
    }

    if (entry.duration && entry.duration > 0) {
      setTimeout(() => dismiss(id), entry.duration);
    }

    return id;
  };

  const dismiss = (id: string) => {
    const index = state.toasts.findIndex((t) => t.id === id);
    if (index >= 0) {
      state.toasts.splice(index, 1);
    }
  };

  return {
    toasts: readonly(state.toasts),
    push,
    dismiss
  };
}
