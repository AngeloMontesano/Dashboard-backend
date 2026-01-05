<script setup lang="ts">
import Button from 'primevue/button';

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
    <Button
      label="CSV"
      icon="pi pi-file"
      severity="secondary"
      outlined
      :loading="loadingFormat === 'csv'"
      :disabled="disabled"
      @click="emit('export:csv')"
    />
    <Button
      label="Excel"
      icon="pi pi-file-excel"
      severity="success"
      outlined
      :loading="loadingFormat === 'excel'"
      :disabled="disabled"
      @click="emit('export:excel')"
    />
    <Button
      label="PDF"
      icon="pi pi-file-pdf"
      severity="danger"
      outlined
      :loading="loadingFormat === 'pdf'"
      :disabled="disabled"
      @click="emit('export:pdf')"
    />
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
