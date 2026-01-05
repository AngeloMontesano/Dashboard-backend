<template>
  <div class="toolbar">
    <div v-if="$slots.start" class="toolbar-group">
      <slot name="start" />
    </div>
    <div v-if="$slots.end" class="toolbar-group">
      <slot name="end" />
    </div>
  </div>
</template>
