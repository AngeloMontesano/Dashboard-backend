// src/composables/useToast.ts
import { reactive, readonly } from "vue";

/*
  Zentraler Toast
  - Einmal rendern (App.vue)
  - Überall nutzbar (Views, Components)
  - Mehrere Toasts möglich (Queue)
  - Optik angeglichen an Kundenportal
*/

export type ToastVariant = "info" | "success" | "warning" | "danger";

type ToastMessage = {
  id: number;
  title: string;
  description?: string;
  variant: ToastVariant;
  duration?: number;
};

const state = reactive({
  toasts: [] as ToastMessage[],
});

const timers = new Map<number, number>();
let counter = 0;

function dismiss(id: number) {
  const index = state.toasts.findIndex((t) => t.id === id);
  if (index !== -1) {
    state.toasts.splice(index, 1);
  }
  const timer = timers.get(id);
  if (timer) {
    window.clearTimeout(timer);
    timers.delete(id);
  }
}

function push(toast: Omit<ToastMessage, "id">) {
  const id = ++counter;
  const entry: ToastMessage = {
    id,
    duration: 3800,
    ...toast,
  };
  state.toasts.push(entry);

  const timer = window.setTimeout(() => dismiss(id), entry.duration);
  timers.set(id, timer);
  return id;
}

export function useToast() {
  function toast(title: string, variant: ToastVariant = "info") {
    return push({ title, variant });
  }

  return { toast, push, dismiss, toasts: readonly(state.toasts) };
}
