<script setup lang="ts">
import { computed } from "vue";
import { useToast, type ToastVariant } from "../../composables/useToast";

const { toasts, dismiss } = useToast();

const variantLabel: Record<ToastVariant, string> = {
  info: "Info",
  success: "Erfolg",
  warning: "Hinweis",
  danger: "Fehler",
};

const toneClass = computed(() => (variant: ToastVariant) => variant);
</script>

<template>
  <div class="toastHost" aria-live="polite">
    <div v-for="toast in toasts" :key="toast.id" class="toastCard" role="status">
      <div class="toastHeader">
        <span class="toastPill" :class="toneClass(toast.variant)">{{ variantLabel[toast.variant] }}</span>
        <button class="btnGhost small" type="button" aria-label="Toast schließen" @click="dismiss(toast.id)">✕</button>
      </div>
      <p class="toastTitle">{{ toast.title }}</p>
      <p v-if="toast.description" class="toastDescription">{{ toast.description }}</p>
    </div>
  </div>
</template>
