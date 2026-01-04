<template>
  <div class="login-shell">
    <div class="login-card">
      <h1>Tenant Login</h1>
      <p class="muted">Mit deiner E-Mail und Passwort anmelden.</p>
      <div class="field">
        <label for="email">E-Mail</label>
        <input id="email" v-model.trim="email" type="email" placeholder="user@example.com" />
      </div>
      <div class="field">
        <label for="password">Passwort</label>
        <input id="password" v-model="password" type="password" placeholder="••••••••" />
      </div>
      <button class="button button--primary" :disabled="busy" @click="submit">
        {{ busy ? 'Login...' : 'Anmelden' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useToast } from '@/composables/useToast';

const email = ref('');
const password = ref('');
const error = ref('');
const busy = ref(false);
const router = useRouter();
const route = useRoute();
const { login } = useAuth();
const { push } = useToast();

async function submit() {
  error.value = '';
  if (!email.value || !password.value) {
    error.value = 'E-Mail und Passwort sind Pflicht.';
    return;
  }
  busy.value = true;
  try {
    await login(email.value, password.value);
    push({ title: 'Login', description: 'Login erfolgreich', variant: 'success' });
    const redirect = (route.query.redirect as string) || '/';
    router.push(redirect);
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Login fehlgeschlagen';
  } finally {
    busy.value = false;
  }
}
</script>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--color-surface-muted);
}
.login-card {
  width: 360px;
  padding: 24px;
  border-radius: 14px;
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--color-border);
  display: grid;
  gap: 14px;
}
.field {
  display: grid;
  gap: 6px;
}
label {
  font-weight: 600;
}
input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-muted);
}
.muted {
  color: var(--color-text-muted);
  margin: 0;
}
.error {
  color: var(--color-danger);
  margin: 0;
}
.button {
  width: 100%;
}
</style>
