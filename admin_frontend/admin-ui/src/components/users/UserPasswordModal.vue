<template>
  <div v-if="open">
    <div class="backdrop" @click="$emit('close')"></div>
    <div class="modal" @click.stop>
      <div class="modalHeader">
        <div class="modalTitle">Passwort setzen</div>
        <button class="btnGhost" @click="$emit('close')">Schließen</button>
      </div>

      <div class="modalBody">
        <div class="field">
          <div class="label">Benutzer</div>
          <div class="mono">{{ email || "–" }}</div>
        </div>
        <div class="field">
          <div class="label">Neues Passwort</div>
          <input
            class="input"
            type="password"
            :value="password"
            @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
            placeholder="mind. 8 Zeichen"
          />
          <div class="muted smallText">Wird sofort gesetzt, Passwort wird nicht angezeigt.</div>
        </div>
      </div>

      <div class="modalFooter">
        <button class="btnGhost" @click="$emit('close')">Abbrechen</button>
        <button class="btnPrimary" :disabled="busy" @click="$emit('save')">
          {{ busy ? "..." : "Speichern" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  open: boolean;
  busy: boolean;
  email: string;
  password: string;
}>();

defineEmits<{
  (e: "close"): void;
  (e: "save"): void;
  (e: "update:password", v: string): void;
}>();
</script>
