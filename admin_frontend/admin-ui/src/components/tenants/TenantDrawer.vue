<template>
  <!--
    TenantDrawer
    - Reine Darstellung + User Actions
    - Toggle wird nach außen emitted
    - Note wird via v-model:note gebunden
  -->
  <div v-if="open" class="drawerCard" @click.stop>
    <div class="drawerHeader">
      <div>
        <div class="drawerTitle">{{ tenant?.name || "-" }}</div>
        <div class="drawerSub mono">
          {{ tenant ? `${tenant.slug}.${baseDomain}` : "-" }} · {{ tenant?.id || "-" }}
        </div>
      </div>
      <button class="btnGhost" @click="$emit('close')">Schließen</button>
    </div>

    <div class="drawerBody">
      <div class="sectionTitle">Aktionen</div>

      <div class="rowActions">
        <button
          class="btnPrimary"
          :disabled="!tenant || busyToggle === tenant.id"
          @click="tenant && $emit('toggle', tenant)"
        >
          {{ tenant?.is_active ? "Deaktivieren" : "Aktivieren" }}
        </button>

        <button class="btnGhost danger" :disabled="!tenant || busyDelete === tenant?.id" @click="tenant && $emit('delete', tenant)">
          {{ busyDelete === tenant?.id ? "löscht..." : "Löschen" }}
        </button>
        <button class="btnGhost" disabled>Support Session</button>
        <button class="btnGhost" disabled>Passwort Reset</button>
      </div>

      <div class="sectionTitle" style="margin-top: 12px;">Notiz</div>
      <textarea
        class="input area"
        :value="note"
        @input="$emit('update:note', ($event.target as HTMLTextAreaElement).value)"
        placeholder="Interne Notiz"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TenantOut } from "../../types";

defineProps<{
  open: boolean;
  tenant: TenantOut | null;
  busyToggle: string;
  busyDelete: string;
  note: string;
  baseDomain: string;
}>();

defineEmits<{
  (e: "close"): void;
  (e: "toggle", t: TenantOut): void;
  (e: "delete", t: TenantOut): void;
  (e: "update:note", v: string): void;
}>();
</script>

<style scoped>
.drawerCard {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 14px;
  margin-top: 12px;
}

.drawerHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.drawerTitle {
  font-weight: 800;
}

.drawerSub {
  color: var(--muted);
  font-size: 12px;
  margin-top: 2px;
}

.drawerBody {
  display: grid;
  gap: 10px;
}

.rowActions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sectionTitle {
  font-weight: 700;
  font-size: 13px;
}

.input.area {
  min-height: 90px;
}
</style>
