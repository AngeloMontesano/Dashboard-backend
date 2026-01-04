<script setup lang="ts">
import { defineExpose, ref } from 'vue';

type Option = {
  label: string;
  value: string | number | null;
};

const props = defineProps<{
  modelValue: string | number | null;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{ 'update:modelValue': [string | number | null] }>();
const selectEl = ref<HTMLSelectElement | null>(null);

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  const selected = props.options.find((opt) => String(opt.value ?? '') === target.value);
  emit('update:modelValue', selected ? selected.value : null);
}

defineExpose({
  focus: () => selectEl.value?.focus()
});
</script>

<template>
  <select ref="selectEl" class="input" :disabled="disabled" :value="modelValue ?? ''" @change="onChange">
    <option value="">{{ placeholder || 'Bitte wählen' }}</option>
    <option v-for="option in options" :key="option.value ?? option.label" :value="option.value ?? ''">
      {{ option.label }}
    </option>
  </select>
</template>
