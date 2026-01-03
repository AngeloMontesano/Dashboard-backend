<template>
  <!--
    TenantCreateModal
    - Reine Darstellung
    - v-model:name / v-model:slug
    - create/close events
  -->
  <div v-if="open">
    <div class="backdrop" @click="$emit('close')"></div>

    <div class="modal" @click.stop>
      <div class="modalHeader">
        <div class="modalTitle">Tenant anlegen</div>
        <button class="btnGhost" @click="$emit('close')">Schließen</button>
      </div>

      <div class="modalBody">
        <div class="formGrid">
          <div class="field">
            <div class="label">Name</div>
            <input
              class="input"
              :value="name"
              @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
              placeholder="Bäckerei Muster"
            />
          </div>

          <div class="field">
            <div class="label">Slug</div>
            <input
              class="input"
              :value="slug"
              @input="$emit('update:slug', ($event.target as HTMLInputElement).value)"
              placeholder="baeckerei-muster"
            />
          </div>
        </div>

        <div class="hintBox" style="margin-top: 10px;">
          Erstellt via <span class="mono">POST /admin/tenants</span>. Slug muss eindeutig sein.
        </div>
      </div>

      <div class="modalFooter">
        <button class="btnGhost" @click="$emit('close')">Abbrechen</button>
        <button class="btnPrimary" :disabled="busy" @click="$emit('create')">
          {{ busy ? "..." : "Anlegen" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  open: boolean;
  busy: boolean;
  name: string;
  slug: string;
}>();

defineEmits<{
  (e: "close"): void;
  (e: "create"): void;
  (e: "update:name", v: string): void;
  (e: "update:slug", v: string): void;
}>();
</script>
