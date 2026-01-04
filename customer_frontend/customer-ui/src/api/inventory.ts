import axios from 'axios';
import { getBaseURL, getTenantForwardHeader } from './base';

export type MovementPayload = {
  client_tx_id: string;
  type: 'IN' | 'OUT';
  barcode: string;
  qty: number;
  note?: string;
  created_at: string;
};

const client = axios.create({
  baseURL: getBaseURL(),
  timeout: 8000,
  headers: {
    ...getTenantForwardHeader()
  }
});

const mockPost = async (payload: MovementPayload) => {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return {
    ok: true,
    data: {
      ...payload,
      mocked: true
    }
  };
};

export async function postInventoryMovement(payload: MovementPayload) {
  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    throw new Error('Offline - kann Bewegung nicht senden');
  }

  try {
    const response = await client.post('/inventory/movements', payload);
    return response.data;
  } catch (error) {
    // Fallback Mock, damit Frontend weiter funktioniert bis API verfügbar ist.
    return mockPost(payload);
  }
}
