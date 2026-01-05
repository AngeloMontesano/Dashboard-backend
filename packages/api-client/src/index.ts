// Gemeinsamer API-Client für alle Frontends
// Stellt zentrale BaseURL-Ermittlung, Tenant-Header und Axios-Instanziierung bereit.

import axios, { type AxiosInstance } from 'axios';

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'test.myitnetwork.de';
const apiSubdomain = import.meta.env.VITE_API_SUBDOMAIN || 'api';
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || 'https';
const apiHost = import.meta.env.VITE_API_HOST || '';
const apiPort = import.meta.env.VITE_API_PORT || '';
const tenantSlugEnv = import.meta.env.VITE_TENANT_SLUG || '';
const explicitApiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE;
const allowRuntimeHost = (import.meta.env.VITE_ALLOW_RUNTIME_HOST || 'true').toLowerCase() === 'true';
const apiPrefix = normalizePrefix(import.meta.env.VITE_API_PREFIX ?? '/api');

const runtimeHost = typeof window !== 'undefined' ? window.location.hostname : '';
const runtimeProtocol = typeof window !== 'undefined' ? window.location.protocol.replace(':', '') : '';
const runtimePort = typeof window !== 'undefined' ? window.location.port : '';

function normalizePrefix(prefix: string | undefined | null): string {
  if (!prefix) return '';
  const trimmed = prefix.trim();
  if (!trimmed || trimmed === '/') return '';
  const withLeading = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  return withLeading.replace(/\/+$/, '');
}

function applyPrefix(url: string): string {
  const sanitized = url.replace(/\/+$/, '');
  if (!apiPrefix) return sanitized;
  return `${sanitized}${apiPrefix}`;
}

function replaceHost(url: string, host: string): string | null {
  try {
    const parsed = new URL(url);
    parsed.host = host;
    return parsed.toString().replace(/\/$/, '');
  } catch {
    return null;
  }
}

export function getTenantHost(): string | null {
  if (baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
    return runtimeHost + (runtimePort ? `:${runtimePort}` : '');
  }
  if (tenantSlugEnv && baseDomain) {
    const portPart = apiPort ? `:${apiPort}` : '';
    return `${tenantSlugEnv}.${baseDomain}${portPart}`;
  }
  return null;
}

export function getTenantSlug(): string {
  const tenantHost = getTenantHost();
  const slugFromHost = tenantHost ? tenantHost.split(':')[0]?.split('.')[0] : '';
  return slugFromHost || tenantSlugEnv || '';
}

export function getTenantHeaders(): Record<string, string> {
  const tenantHost = getTenantHost();
  const slug = getTenantSlug();

  const headers: Record<string, string> = {};
  if (tenantHost) headers['X-Forwarded-Host'] = tenantHost;
  if (slug) headers['X-Tenant-Slug'] = slug;
  return headers;
}

export function getBaseURL(): string {
  // Expliziter Base gewinnt, darf aber bei Multi-Tenant durch runtime host ersetzt werden
  if (explicitApiBase) {
    if (allowRuntimeHost && baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
      const adjusted = replaceHost(explicitApiBase, runtimeHost + (runtimePort ? `:${runtimePort}` : ''));
      if (adjusted) return applyPrefix(adjusted);
    }
    return applyPrefix(explicitApiBase);
  }

  if (apiHost) {
    const portPart = apiPort ? `:${apiPort}` : '';
    return applyPrefix(`${apiProtocol}://${apiHost}${portPart}`);
  }

  if (baseDomain && runtimeHost && runtimeHost.endsWith(`.${baseDomain}`)) {
    const portPart = runtimePort ? `:${runtimePort}` : '';
    const protocol = runtimeProtocol || apiProtocol;
    return applyPrefix(`${protocol}://${runtimeHost}${portPart}`);
  }

  if (tenantSlugEnv && baseDomain) {
    return applyPrefix(`${apiProtocol}://${tenantSlugEnv}.${baseDomain}`);
  }

  return applyPrefix(`${apiProtocol}://${apiSubdomain}.${baseDomain}`);
}

export type ApiClientOptions = {
  token?: string;
  timeout?: number;
  extraHeaders?: Record<string, string>;
};

export function createApiClient(options: ApiClientOptions = {}): AxiosInstance {
  const { token, timeout = 20000, extraHeaders = {} } = options;
  const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  return axios.create({
    baseURL: getBaseURL(),
    timeout,
    headers: {
      'Content-Type': 'application/json',
      ...getTenantHeaders(),
      ...authHeaders,
      ...extraHeaders
    }
  });
}

// Hilfreiches Logging für Laufzeitdiagnosen (nur Info-Level)
if (typeof console !== 'undefined') {
  console.info('[shared-api] resolved base URL', getBaseURL(), {
    explicitApiBase,
    apiHost,
    apiPort,
    apiProtocol,
    apiSubdomain,
    baseDomain,
    tenantSlugEnv,
    runtimeHost,
    runtimeProtocol,
    runtimePort,
    allowRuntimeHost,
    apiPrefix
  });
}
