<template>
  <div class="tableWrap">
    <table class="table">
      <thead>
        <tr>
          <th>Zeit</th>
          <th>Actor</th>
          <th>Action</th>
          <th>Entity</th>
          <th class="right">Aktion</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="r in rows" :key="r.id" @dblclick="open(r)">
          <td class="mono">{{ formatTs(r.created_at) }}</td>
          <td class="mono">{{ r.actor }}</td>
          <td><span class="tag neutral">{{ r.action }}</span></td>
          <td class="mono">{{ r.entity_type }} · {{ r.entity_id }}</td>
          <td class="right">
            <button class="link" @click.stop="open(r)">Details</button>
          </td>
        </tr>

        <tr v-if="rows.length === 0">
          <td colspan="5" class="mutedPad">
            {{ busy ? "Lade Audit..." : "Keine Einträge." }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { AuditOut } from "../../types";

const props = defineProps<{
  rows: AuditOut[];
  busy: boolean;
}>();

const emit = defineEmits<{
  (e: "open", row: AuditOut): void;
}>();

function open(row: AuditOut) {
  emit("open", row);
}

function formatTs(iso: string) {
  // simpel, stabil, ohne externe libs
  try {
    const d = new Date(iso);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
  } catch {
    return iso;
  }
}
</script>
