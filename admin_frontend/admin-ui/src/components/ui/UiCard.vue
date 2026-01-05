<template>
  <article class="section stack">
    <header v-if="title || $slots.actions || $slots.header" class="section-header">
      <div class="stack">
        <h3 v-if="title" class="section-title">{{ title }}</h3>
        <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
        <slot name="header" />
      </div>
      <div v-if="$slots.actions" class="section-actions">
        <slot name="actions" />
      </div>
    </header>
    <slot />
  </article>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>
