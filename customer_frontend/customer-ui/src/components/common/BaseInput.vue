<script setup lang="ts">
import { defineExpose, ref } from 'vue';

const props = withDefaults(
  defineProps<{
    modelValue: string | number;
    type?: string;
    placeholder?: string;
    disabled?: boolean;
    autocomplete?: string;
    min?: number;
    max?: number;
    step?: number | string;
  }>(),
  {
    type: 'text',
    placeholder: '',
    disabled: false,
    autocomplete: 'off',
    min: undefined,
    max: undefined,
    step: undefined
  }
);

const emit = defineEmits<{ 'update:modelValue': [string | number] }>();

const inputEl = ref<HTMLInputElement | null>(null);

function onInput(event: Event) {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', props.type === 'number' ? Number(target.value) : target.value);
}

defineExpose({
  focus: () => inputEl.value?.focus()
});
</script>

<template>
  <input
    ref="inputEl"
    class="input"
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :autocomplete="autocomplete"
    :min="min"
    :max="max"
    :step="step"
    @input="onInput"
  />
</template>
