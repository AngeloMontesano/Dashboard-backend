<script setup lang="ts">
import StatusPill from './StatusPill.vue';
import { useToast, type ToastVariant } from '@/composables/useToast';

const { toasts, dismiss } = useToast();

const toneMap: Record<ToastVariant, ToastVariant> = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  danger: 'danger'
};
</script>

<template>
  <div class="toast-host" aria-live="polite">
    <div v-for="toast in toasts" :key="toast.id" class="toast" role="status">
      <div class="toast__header">
        <StatusPill :label="toast.variant" :tone="toneMap[toast.variant]" />
        <button class="button button--ghost" type="button" aria-label="Toast schließen" @click="dismiss(toast.id)">
          ✕
        </button>
      </div>
      <p class="toast__title">{{ toast.title }}</p>
      <p v-if="toast.description" class="toast__description">{{ toast.description }}</p>
    </div>
  </div>
</template>
