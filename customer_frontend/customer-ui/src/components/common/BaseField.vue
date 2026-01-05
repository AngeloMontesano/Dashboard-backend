<script setup lang="ts">
defineProps<{
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
}>();
</script>

<template>
  <div class="field">
    <label>
      {{ label }}<span v-if="required" aria-hidden="true"> *</span>
    </label>
    <div class="field__control">
      <slot />
    </div>
    <small v-if="error" class="field__error">{{ error }}</small>
    <small v-else-if="hint" class="field__hint">{{ hint }}</small>
  </div>
</template>

<style scoped>
.field__control :deep(.input) {
  width: 100%;
}
.field__hint {
  color: var(--color-text-muted);
}
.field__error {
  color: var(--color-danger);
}
</style>
