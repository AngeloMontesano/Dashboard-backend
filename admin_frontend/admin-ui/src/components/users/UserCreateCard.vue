<template>
  <section v-if="open" class="createCard">
    <div class="cardHeader">
      <div>
        <div class="cardTitle">Benutzer anlegen</div>
        <div class="muted smallText">Pflichtfelder. Passwort muss mindestens 8 Zeichen haben.</div>
      </div>
      <button class="btnGhost small" type="button" @click="$emit('close')">Schließen</button>
    </div>

    <div class="formGrid">
      <label class="field">
        <span class="label">E-Mail</span>
        <input
          class="input"
          :value="email"
          required
          autocomplete="email"
          @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
          placeholder="user@example.com"
        />
        <span class="muted smallText">E-Mail wird in Kleinbuchstaben gespeichert.</span>
      </label>
      <label class="field">
        <span class="label">Passwort</span>
        <input
          class="input"
          type="password"
          required
          minlength="8"
          autocomplete="new-password"
          :value="password"
          @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
          placeholder="mindestens 8 Zeichen"
        />
      </label>
    </div>

    <div class="actions">
      <button class="btnGhost" type="button" @click="$emit('close')">Abbrechen</button>
      <button class="btnPrimary" type="button" :disabled="busy" @click="$emit('create')">
        {{ busy ? "..." : "Benutzer anlegen" }}
      </button>
    </div>
  </section>
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

<style scoped>
.createCard {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  background: var(--panel);
  box-shadow: var(--shadow);
  display: grid;
  gap: 14px;
}

.formGrid {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
}

.label {
  font-size: 12px;
  font-weight: 800;
  color: var(--muted);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
