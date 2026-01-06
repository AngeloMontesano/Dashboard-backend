<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps<{
  message?: string;
  redirect?: string;
  retryLabel?: string;
}>();

const emit = defineEmits<{
  (e: 'retry'): void;
}>();

const route = useRoute();
const router = useRouter();

const redirectTarget = computed(() => props.redirect || route.fullPath || '/');

const goToLogin = () => {
  router.push({ name: 'login', query: { redirect: redirectTarget.value } });
};
</script>

<template>
  <div class="auth-banner" role="status">
    <div>
      <p class="auth-title">Anmeldung erforderlich</p>
      <p class="auth-message">{{ message || 'Sitzung abgelaufen. Bitte neu anmelden.' }}</p>
    </div>
    <div class="actions">
      <button class="btnPrimary small" type="button" @click="goToLogin">Neu anmelden</button>
      <button v-if="retryLabel" class="btnGhost small" type="button" @click="emit('retry')">
        {{ retryLabel }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.auth-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface-muted);
}

.auth-title {
  margin: 0;
  font-weight: 700;
  color: var(--text-default);
}

.auth-message {
  margin: 0;
  color: var(--text-muted);
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 720px) {
  .auth-banner {
    flex-direction: column;
    align-items: flex-start;
  }
  .actions {
    width: 100%;
  }
  .actions button {
    width: 100%;
  }
}
</style>
