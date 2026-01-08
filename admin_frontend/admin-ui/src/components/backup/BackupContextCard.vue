<template>
  <div class="table-card">
    <div class="table-card__header">
      <div class="stack-sm">
        <div class="tableTitle">Scope & Kontext</div>
        <div class="text-muted text-small">
          Backup/Restore wird pro Tenant durchgeführt. Endpunkte und Payloads richten sich nach der OpenAPI-Quelle.
        </div>
      </div>
      <a
        class="btnGhost small"
        href="https://api.test.myitnetwork.de/openapi.json"
        target="_blank"
        rel="noreferrer"
      >
        OpenAPI ansehen
      </a>
    </div>
    <div class="chip-list">
      <div class="chip">
        <div class="chip__label">Tenant</div>
        <div class="chip__value">{{ tenantName }}</div>
      </div>
      <div class="chip">
        <div class="chip__label">Slug</div>
        <div class="chip__value">{{ tenantSlug }}</div>
      </div>
      <div class="chip">
        <div class="chip__label">Tenant ID</div>
        <div class="chip__value">{{ tenantId }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  tenant: {
    id: string;
    name: string;
    slug: string;
  };
}>();

const tenantName = computed(() => props.tenant.name || "Kein Tenant gewählt");
const tenantSlug = computed(() => props.tenant.slug || "—");
const tenantId = computed(() => props.tenant.id || "—");
</script>
