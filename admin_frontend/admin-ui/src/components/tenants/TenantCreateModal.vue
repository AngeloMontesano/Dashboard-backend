<template>
  <!--
    TenantCreateModal
    - Reine Darstellung
    - v-model:name / v-model:slug
    - create/close events
  -->
  <div v-if="open">
    <div class="modal-backdrop" @click="$emit('close')"></div>

    <div class="modal-panel" @click.stop>
      <div class="modal">
        <div class="modal__header">
          <div class="modal__title">Tenant anlegen</div>
          <button class="btnGhost" @click="$emit('close')">Schließen</button>
        </div>

        <div class="modal__body">
          <div class="form-grid">
            <div class="field">
              <div class="field-label">Name</div>
              <input
                class="input"
                :value="name"
                @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
                placeholder="Bäckerei Muster"
              />
            </div>

            <div class="field">
              <div class="field-label">URL-Kürzel (für Links)</div>
              <input
                class="input"
                :value="slug"
                @input="$emit('update:slug', ($event.target as HTMLInputElement).value)"
                placeholder="z. B. baeckerei-muster"
                aria-describedby="slug-help"
              />
              <div class="muted text-small" id="slug-help">
                Wird zur Subdomain: <span class="mono">{{ slugPreview }}</span>. Nur Kleinbuchstaben, Zahlen und
                Bindestriche, z. B. <span class="mono">firma-mueller</span>.
              </div>
            </div>
          </div>

          <div class="hint">
            Erstellt via <span class="mono">POST /admin/tenants</span>. Slug muss eindeutig sein.
          </div>
        </div>

        <div class="modal__footer">
          <button class="btnGhost" @click="$emit('close')">Abbrechen</button>
          <button class="btnPrimary" :disabled="busy" @click="$emit('create')">
            {{ busy ? "..." : "Anlegen" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  open: boolean;
  busy: boolean;
  name: string;
  slug: string;
  baseDomain: string;
}>();

defineEmits<{
  (e: "close"): void;
  (e: "create"): void;
  (e: "update:name", v: string): void;
  (e: "update:slug", v: string): void;
}>();

const slugPreview = computed(() => {
  const s = props.slug.trim().toLowerCase() || "<slug>";
  return `${s}.${props.baseDomain}`;
});
</script>
