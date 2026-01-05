<template>
  <article class="card">
    <p class="card__title">{{ label }}</p>
    <p class="card__value">{{ value }}</p>
    <p v-if="hint" class="card__hint">{{ hint }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  hint?: string;
}>();
</script>
