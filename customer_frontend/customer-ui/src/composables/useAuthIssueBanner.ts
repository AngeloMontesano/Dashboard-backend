import { ref } from 'vue';
import { classifyError, type ClassifiedError } from '@/utils/errorClassify';

export function useAuthIssueBanner(defaultMessage = 'Sitzung abgelaufen. Bitte neu anmelden.') {
  const authIssue = ref(false);
  const authMessage = ref(defaultMessage);

  const markAuthIssue = (message?: string) => {
    authIssue.value = true;
    authMessage.value = message || defaultMessage;
  };

  const clearAuthIssue = () => {
    authIssue.value = false;
    authMessage.value = defaultMessage;
  };

  const handleAuthError = (error: unknown): ClassifiedError => {
    const classified = classifyError(error);
    if (classified.category === 'auth') {
      markAuthIssue(classified.userMessage);
    }
    return classified;
  };

  return {
    authIssue,
    authMessage,
    handleAuthError,
    markAuthIssue,
    clearAuthIssue
  };
}
