import axios from 'axios';

export type ErrorCategory = 'auth' | 'client' | 'server' | 'network' | 'unknown';
export type ErrorActionHint = 'login' | 'retry' | 'edit' | 'delete';

export type ClassifiedError = {
  category: ErrorCategory;
  status?: number;
  userMessage: string;
  detailMessage?: string;
  actionHints: ErrorActionHint[];
};

function buildDetailMessage(error: unknown): string | undefined {
  if (!error) return undefined;
  if (typeof error === 'string') return error;
  if (error instanceof Error) return error.message;
  const responseData = (error as any)?.response?.data;
  if (responseData?.detail) return String(responseData.detail);
  if (responseData?.error?.message) return String(responseData.error.message);
  if (typeof responseData === 'string') return responseData;
  return undefined;
}

export function classifyError(error: unknown): ClassifiedError {
  const axiosError = axios.isAxiosError(error) ? error : null;
  const status = axiosError?.response?.status;

  if (status === 401) {
    return {
      category: 'auth',
      status,
      userMessage: 'Sitzung abgelaufen. Bitte neu anmelden.',
      detailMessage: buildDetailMessage(error),
      actionHints: ['login', 'retry']
    };
  }

  if (status && [400, 404, 405, 409, 422].includes(status)) {
    const messages: Record<number, string> = {
      400: 'Eingabe unvollständig oder ungültig.',
      404: 'Eintrag nicht gefunden.',
      405: 'Aktion aktuell nicht erlaubt.',
      409: 'Konflikt: Vorgang kollidiert mit anderem Schritt.',
      422: 'Pflichtfeld fehlt oder nicht zulässig.'
    };
    return {
      category: 'client',
      status,
      userMessage: messages[status] ?? 'Eingabe nicht akzeptiert.',
      detailMessage: buildDetailMessage(error),
      actionHints: ['edit', 'delete']
    };
  }

  if (status && status >= 500) {
    return {
      category: 'server',
      status,
      userMessage: 'Server nicht erreichbar oder Fehler im System.',
      detailMessage: buildDetailMessage(error),
      actionHints: ['retry']
    };
  }

  if (axiosError && (!axiosError.response || axiosError.code === 'ECONNABORTED')) {
    return {
      category: 'network',
      status,
      userMessage: 'Keine Verbindung. Wir versuchen es erneut.',
      detailMessage: buildDetailMessage(error),
      actionHints: ['retry']
    };
  }

  return {
    category: 'unknown',
    status,
    userMessage: 'Unbekannter Fehler. Bitte erneut versuchen.',
    detailMessage: buildDetailMessage(error),
    actionHints: ['retry']
  };
}
