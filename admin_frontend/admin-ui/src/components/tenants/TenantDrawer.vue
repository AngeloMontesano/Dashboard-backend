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

      <div class="sectionTitle u-mt-6">Notiz</div>
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
