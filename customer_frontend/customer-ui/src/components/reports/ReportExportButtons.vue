<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    loadingFormat?: 'csv' | 'excel' | 'pdf' | null;
  }>(),
  {
    disabled: false,
    loadingFormat: null
  }
);

const emit = defineEmits<{
  (e: 'export:csv'): void;
  (e: 'export:excel'): void;
  (e: 'export:pdf'): void;
}>();
</script>

<template>
  <div class="export-actions">
    <button
      class="btnGhost small"
      type="button"
      :disabled="disabled || loadingFormat === 'csv'"
      @click="emit('export:csv')"
    >
      {{ loadingFormat === 'csv' ? 'Lädt...' : 'CSV' }}
    </button>
    <button
      class="btnGhost small"
      type="button"
      :disabled="disabled || loadingFormat === 'excel'"
      @click="emit('export:excel')"
    >
      {{ loadingFormat === 'excel' ? 'Lädt...' : 'Excel' }}
    </button>
    <button
      class="btnPrimary small"
      type="button"
      :disabled="disabled || loadingFormat === 'pdf'"
      @click="emit('export:pdf')"
    >
      {{ loadingFormat === 'pdf' ? 'Lädt...' : 'PDF' }}
    </button>
  </div>
</template>

<style scoped>
.export-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}
</style>
