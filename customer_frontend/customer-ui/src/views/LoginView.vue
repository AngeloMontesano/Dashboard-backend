<template>
  <UiPage>
    <div class="auth-shell">
      <div class="section auth-card stack">
        <h1 class="section-title">Tenant Login</h1>
        <p class="text-muted">Mit deiner E-Mail und Passwort anmelden.</p>
        <div class="field">
          <label for="email">E-Mail</label>
          <input id="email" v-model.trim="email" class="input" type="email" placeholder="user@example.com" />
        </div>
        <div class="field">
          <label for="password">Passwort</label>
          <input id="password" v-model="password" class="input" type="password" placeholder="••••••••" />
        </div>
        <button class="btnPrimary small" :disabled="busy" @click="submit">
          {{ busy ? 'Login...' : 'Anmelden' }}
        </button>
        <p v-if="error" class="text-danger text-small">{{ error }}</p>
      </div>
    </div>
  </UiPage>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useToast } from '@/composables/useToast';
import UiPage from '@/components/ui/UiPage.vue';

const email = ref('');
const password = ref('');
const error = ref('');
const busy = ref(false);
const router = useRouter();
const route = useRoute();
const { login } = useAuth();
const { push } = useToast();

function formatLoginError(e: any): string {
  const responseData = e?.response?.data;
  const status = e?.response?.status;
  const errorPayload = responseData?.error;

  if (errorPayload) {
    const code = errorPayload.code ? ` (${errorPayload.code})` : '';
    const baseMessage = errorPayload.message || 'Login fehlgeschlagen';
    const firstDetail = Array.isArray(errorPayload.details) ? errorPayload.details[0] : null;
    const detailMessage = firstDetail?.msg;
    const detailLoc = Array.isArray(firstDetail?.loc) ? firstDetail.loc.join('.') : '';
    const detail = detailMessage ? `${detailLoc ? `${detailLoc}: ` : ''}${detailMessage}` : '';
    return detail ? `${baseMessage}${code} – ${detail}` : `${baseMessage}${code}`;
  }

  if (status === 422) {
    return 'Ungültige Eingabe (422)';
  }

  return e?.message || 'Login fehlgeschlagen';
}

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
    console.error('Login failed', e?.response?.data || e);
    error.value = formatLoginError(e);
  } finally {
    busy.value = false;
  }
}
</script>
