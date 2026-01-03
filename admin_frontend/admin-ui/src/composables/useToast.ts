// src/composables/useToast.ts
import { reactive } from "vue";

/*
  Zentraler Toast
  - Einmal rendern (App.vue)
  - Überall nutzbar (Views, Components)
*/

const toastState = reactive({
  open: false,
  text: "",
});

let timer: number | null = null;

export function useToast() {
  function toast(text: string) {
    toastState.text = text;
    toastState.open = true;

    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => (toastState.open = false), 2200);
  }

  return { toast, toastState };
}
