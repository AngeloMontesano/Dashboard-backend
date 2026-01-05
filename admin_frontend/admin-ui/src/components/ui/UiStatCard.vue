<template>
  <div class="chip">
    <div class="chip__label">{{ label }}</div>
    <div class="chip__value" :class="toneClass">{{ value }}</div>
    <p v-if="hint" class="hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string;
  value: string | number;
  hint?: string;
  tone?: "default" | "success" | "danger";
}>();

const toneClass = props.tone === "success" ? "tone-success" : props.tone === "danger" ? "tone-danger" : "";
</script>
