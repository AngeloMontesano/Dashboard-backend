<script setup lang="ts">
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
  <div class="toastHost" aria-live="polite">
    <div v-for="toast in toasts" :key="toast.id" class="toastCard" role="status">
      <div class="toastHeader">
        <span class="toastPill" :class="toneMap[toast.variant]">{{ toast.variant }}</span>
        <button class="btnGhost small" type="button" aria-label="Toast schließen" @click="dismiss(toast.id)">
          ✕
        </button>
      </div>
      <p class="toastTitle">{{ toast.title }}</p>
      <p v-if="toast.description" class="toastDescription">{{ toast.description }}</p>
    </div>
  </div>
</template>
