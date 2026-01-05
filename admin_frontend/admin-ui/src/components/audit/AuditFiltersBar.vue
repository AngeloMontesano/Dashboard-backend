<template>
  <div class="box">
    <div class="form-grid">
      <div class="field">
        <div class="label">Actor (optional)</div>
        <input class="input" :value="actor" @input="$emit('update:actor', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>

      <div class="field">
        <div class="label">Aktion (create/update/delete)</div>
        <input class="input" :value="action" @input="$emit('update:action', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>

      <div class="field">
        <div class="label">Entity Typ (z.B. user/tenant)</div>
        <input class="input" :value="entityType" @input="$emit('update:entityType', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>

      <div class="field">
        <div class="label">Entity ID</div>
        <input class="input" :value="entityId" @input="$emit('update:entityId', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>
    </div>

    <div class="form-grid mt-4">
      <div class="field">
        <div class="label">Von (ISO)</div>
        <input class="input" placeholder="2026-01-02T10:00:00Z" :value="createdFrom" @input="$emit('update:createdFrom', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>

      <div class="field">
        <div class="label">Bis (ISO)</div>
        <input class="input" placeholder="2026-01-02T12:00:00Z" :value="createdTo" @input="$emit('update:createdTo', ($event.target as HTMLInputElement).value)" @keyup.enter="$emit('enter')" />
      </div>

      <div class="field">
        <div class="label">Limit</div>
        <select class="input" :value="String(limit)" @change="$emit('update:limit', Number(($event.target as HTMLSelectElement).value))">
          <option value="50">50</option>
          <option value="100">100</option>
          <option value="200">200</option>
          <option value="500">500</option>
        </select>
      </div>

      <div class="field">
        <div class="label">Status</div>
        <div class="muted">{{ busy ? "Lade..." : "Bereit" }}</div>
      </div>
    </div>

    <div class="text-muted text-small mt-4">
      Filter gehen direkt an <span class="mono">GET /admin/audit</span>.
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  actor: string;
  action: string;
  entityType: string;
  entityId: string;
  createdFrom: string;
  createdTo: string;
  limit: number;
  busy: boolean;
}>();

defineEmits<{
  (e: "update:actor", v: string): void;
  (e: "update:action", v: string): void;
  (e: "update:entityType", v: string): void;
  (e: "update:entityId", v: string): void;
  (e: "update:createdFrom", v: string): void;
  (e: "update:createdTo", v: string): void;
  (e: "update:limit", v: number): void;
  (e: "enter"): void;
}>();
</script>
