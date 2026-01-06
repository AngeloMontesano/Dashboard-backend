<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <div class="empty-state stack">
    <p class="empty-state__title">{{ title }}</p>
    <p v-if="description" class="empty-state__description">{{ description }}</p>
    <div v-if="$slots.actions" class="empty-state__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--surface-2) 70%, var(--surface-1) 30%);
  padding: var(--space-12);
  color: var(--text-strong);
}

.empty-state__title {
  margin: 0;
  font-weight: 820;
  font-size: 16px;
}

.empty-state__description {
  margin: 0;
  color: var(--text-muted);
}

.empty-state__actions {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}
</style>
