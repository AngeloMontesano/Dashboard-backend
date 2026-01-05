<template>
  <div class="table-card">
    <div class="stack align-start">
      <p class="section-title no-margin">{{ title }}</p>
      <p class="section-subtitle" v-if="description">{{ description }}</p>
      <div v-if="$slots.actions" class="section-actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>
