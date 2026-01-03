<template>
  <!--
    TenantTable
    - Reine Darstellung
    - Keine API Calls
    - Emits: select, details, toggle
  -->
  <div class="tableWrap">
    <table class="table">
      <thead>
        <tr>
          <th>Slug</th>
          <th>Name</th>
          <th>Status</th>
          <th class="right">Aktionen</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="t in tenants"
          :key="t.id"
          :class="{ rowActive: selectedId === t.id }"
          @click="$emit('select', t)"
        >
          <td class="mono">{{ t.slug }}</td>
          <td>{{ t.name }}</td>
          <td>
            <span class="tag" :class="t.is_active ? 'ok' : 'bad'">
              {{ t.is_active ? "aktiv" : "deaktiviert" }}
            </span>
          </td>

          <td class="right">
            <button class="link" @click.stop="$emit('details', t)">Details</button>
            <button
              class="link"
              :disabled="busyToggleId === t.id"
              @click.stop="$emit('toggle', t)"
            >
              {{ busyToggleId === t.id ? "..." : (t.is_active ? "deaktivieren" : "aktivieren") }}
            </button>
          </td>
        </tr>

        <tr v-if="tenants.length === 0">
          <td colspan="4" class="mutedPad">
            {{ busyList ? "Lade Tenants..." : "Keine Tenants gefunden." }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { TenantOut } from "../../types";

defineProps<{
  tenants: TenantOut[];
  selectedId: string;
  busyToggleId: string;
  busyList: boolean;
}>();

defineEmits<{
  (e: "select", t: TenantOut): void;
  (e: "details", t: TenantOut): void;
  (e: "toggle", t: TenantOut): void;
}>();
</script>
