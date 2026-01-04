<template>
  <div v-if="open">
    <div class="backdrop" @click="$emit('close')"></div>
    <div class="modal" @click.stop>
      <div class="modalHeader">
        <div class="modalTitle">Benutzer anlegen</div>
        <button class="btnGhost" @click="$emit('close')">Schließen</button>
      </div>

      <div class="modalBody">
        <div class="formGrid">
          <div class="field">
            <div class="label">E-Mail</div>
            <input
              class="input"
              :value="email"
              @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
              placeholder="user@example.com"
            />
            <div class="muted smallText">E-Mail wird in Kleinbuchstaben gespeichert.</div>
          </div>
          <div class="field">
            <div class="label">Passwort (optional)</div>
            <input
              class="input"
              type="password"
              :value="password"
              @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
              placeholder="mind. 8 Zeichen oder leer lassen"
            />
          </div>
        </div>
      </div>

      <div class="modalFooter">
        <button class="btnGhost" @click="$emit('close')">Abbrechen</button>
        <button class="btnPrimary" :disabled="busy" @click="$emit('create')">
          {{ busy ? "..." : "Benutzer anlegen" }}
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
  (e: "create"): void;
  (e: "update:email", v: string): void;
  (e: "update:password", v: string): void;
}>();
</script>
