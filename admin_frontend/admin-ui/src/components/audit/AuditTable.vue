<template>
  <div class="tableWrap">
    <table class="table">
      <thead>
        <tr>
          <th>Zeit</th>
          <th>Actor</th>
          <th>Aktion</th>
          <th>Entity</th>
          <th>Änderung</th>
          <th class="right">Aktion</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="r in rows" :key="r.id" @dblclick="open(r)">
          <td class="mono">{{ r.createdAtLocal }}</td>
          <td class="mono">{{ r.actor }}</td>
          <td><span class="tag neutral">{{ r.actionLabel }}</span></td>
          <td class="mono">{{ r.entityLabel }} · {{ r.entity_id }}</td>
          <td>{{ r.summary }}</td>
          <td class="right">
            <button class="link" @click.stop="open(r)">Details</button>
          </td>
        </tr>

        <tr v-if="rows.length === 0">
          <td colspan="6" class="mutedPad">
            {{ busy ? "Lade Audit..." : "Keine Einträge." }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { AuditDisplayRow } from "./format";

const props = defineProps<{
  rows: AuditDisplayRow[];
  busy: boolean;
}>();

const emit = defineEmits<{
  (e: "open", row: AuditDisplayRow): void;
}>();

function open(row: AuditDisplayRow) {
  emit("open", row);
}
</script>
