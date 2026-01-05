<template>
  <div class="section stack">
    <p class="section-title">{{ title }}</p>
    <p v-if="description" class="section-subtitle">{{ description }}</p>
    <div v-if="$slots.actions" class="section-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>
