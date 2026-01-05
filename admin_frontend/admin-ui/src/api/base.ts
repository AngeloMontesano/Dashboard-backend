// Wrapper auf den gemeinsamen API-Client im Monorepo.
import { getBaseURL as sharedGetBaseURL } from '@shared/api-client';

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'test.myitnetwork.de';

export function getBaseURL() {
  return sharedGetBaseURL();
}

export function getBaseDomain() {
  return baseDomain;
}
