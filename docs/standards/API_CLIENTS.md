# API Clients

## Customer (`customer_frontend/customer-ui/src/api/client.ts`)
- Eine Axios-Instanz mit `baseURL: "/api"` (keine Host-/Env-Ermittlung) und Timeout 20s.
- Default-Header: `Content-Type: application/json` plus Tenant-Header aus `getTenantHeaders()`.
- Helper:
  - `authHeaders(token?)` liefert `{ Authorization: Bearer <token> }` oder `undefined`.
  - `setAuthToken(token?)` setzt/entfernt den Default-Auth-Header.
- Alle Wrapper (`auth.ts`, `inventory.ts`, `reporting.ts`, `reports.ts`) nutzen nur diese Instanz.

## Admin (`admin_frontend/admin-ui/src/api/client.ts`)
- Eine Axios-Instanz mit `baseURL: "/api"` (keine Host-/Env-Ermittlung) und Timeout 15s.
- Default-Header: `Content-Type: application/json`.
- Helper: `adminHeaders(adminKey, actor?)` setzt `X-Admin-Key` und optional `X-Admin-Actor`.
- Wrapper (`admin.ts`, `platform.ts`) nutzen ausschließlich diese Instanz.

## Header-Regeln
- Admin: Pflichtheader `X-Admin-Key`, optional `X-Admin-Actor`.
- Customer: Tenant-Kontext über `X-Tenant-Slug` und `X-Forwarded-Host` aus `getTenantHeaders()`.
- Keine festen Host-URLs in Headern; nur relative Pfade über `/api`.

## Token-Handling
- Auth-Tokens werden per Header gesetzt, nicht über neue Axios-Instanzen.
- Für Uploads (FormData) wird der Auth-Header mitgegeben; Content-Type wird bei Bedarf pro Request überschrieben.

## Timeout-Regeln
- Zeitlimits sind zentral im Client definiert; spezielle Requests dürfen ein engeres Timeout per Request-Config setzen.
- Shared Helper in `packages/api-client` stellt nur `getBaseURL()` (immer `/api`) und Tenant-Header bereit; neue Axios-Instanzen außerhalb der Clients sind nicht erlaubt.

## Neues Wrapper-Template
```ts
import { api, authHeaders } from "./client";
import type { components, paths } from "./gen/openapi";

type ResponseType = paths["/example"]["get"]["responses"]["200"]["content"]["application/json"];

export async function getExample(token: string, params?: Record<string, unknown>) {
  const res = await api.get<ResponseType>("/example", { params, headers: authHeaders(token) });
  return res.data;
}
```
