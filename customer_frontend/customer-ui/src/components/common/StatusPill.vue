<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  label: string;
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'info';
}>();

const toneClass = computed(() => props.tone ?? 'neutral');
</script>

<template>
  <span class="status-pill" :class="`status-pill--${toneClass}`">{{ label }}</span>
</template>
