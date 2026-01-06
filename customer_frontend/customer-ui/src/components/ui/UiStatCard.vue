<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, type RouteLocationRaw } from 'vue-router';

const props = defineProps<{
  label: string;
  value: string | number;
  hint?: string;
  to?: RouteLocationRaw;
  asButton?: boolean;
}>();

const interactive = computed(() => Boolean(props.to || props.asButton));
const componentTag = computed(() => {
  if (props.to) return RouterLink;
  if (props.asButton) return 'button';
  return 'article';
});

const componentProps = computed(() => {
  if (props.to) return { to: props.to };
  if (props.asButton) return { type: 'button' };
  return {};
});
</script>

<template>
  <component
    :is="componentTag"
    class="card"
    :class="{ 'card--clickable': interactive }"
    v-bind="componentProps"
    :aria-label="label"
  >
    <p class="card__title">{{ label }}</p>
    <p class="card__value">{{ value }}</p>
    <p v-if="hint" class="card__hint">{{ hint }}</p>
  </component>
</template>
