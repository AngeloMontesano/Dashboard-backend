# Frontend Rules

## Architektur-Grundsätze
- Zwei getrennte Frontends bleiben bestehen: `admin_frontend/admin-ui` und `customer_frontend/customer-ui`. Keine Zusammenlegung oder Shared-Package-Refactor in diesem Schritt.
- API-Aufrufe laufen ausschließlich über relative Pfade und den gemeinsamen Proxy-Pfad `/api`.
- Jede App besitzt genau eine Axios-Quelle in `src/api/client.ts`; Wrapper nutzen nur diese Instanz.

## Nicht verhandelbare Regeln
- Basis-URL ist immer `/api`, keine festen Hosts im Frontend-Code.
- `axios.create` ist nur in `src/api/client.ts` je Frontend erlaubt.
- Wrapper-Dateien (z. B. `auth.ts`, `inventory.ts`, `reporting.ts`, `admin.ts`, `platform.ts`) verwenden ausschließlich `api.get/post/patch/delete`.
- OpenAPI-Typen werden generiert und in den zentralen API-Wrappern genutzt.
- Admin- und Tenant-Kontexte bleiben strikt getrennt: Admin-User verwalten Tenants, Tenant-User existieren nur im Customer-Kontext.

## Ordnerstruktur je Frontend
- Admin: `admin_frontend/admin-ui/src/api`, `.../views`, `.../components`, `.../styles`.
- Customer: `customer_frontend/customer-ui/src/api`, `.../views`, `.../components`, `.../styles`.
- Generierte OpenAPI-Typen liegen je Frontend unter `src/api/gen/openapi.ts`.

## API-Regeln
- Alle Requests nutzen `/api` als Basis, keine Runtime-Host-Berechnung.
- Header für Tenant-Routing kommen aus `getTenantHeaders()` (Customer) bzw. `adminHeaders()` (Admin).
- Keine absoluten Backend-Hosts im Frontend; Hosts dürfen nur in Doku oder Build-Skripten vorkommen.
- Shared-Helper liefern nur relative Pfade/Headers; keine neuen Axios-Instanzen außerhalb der Clients.

## Client-Regeln
- Genau eine Axios-Instanz pro App: `customer/src/api/client.ts` und `admin_frontend/admin-ui/src/api/client.ts`.
- Token-/Kontext-Handling erfolgt über Helper (`authHeaders`, `adminHeaders`, `setAuthToken`), nicht über neue Instanzen.
- Timeouts werden zentral im Client oder Request-Config gesetzt, nicht pro ad-hoc Instanz.

## Error-Handling-Standard
- Fehlertexte werden über Hilfsfunktionen (`stringifyError` o. ä.) vereinheitlicht.
- Netzwerk-/Timeout-Fehler dürfen den Basis-Pfad `/api` im Text referenzieren, aber keine Hosts.

## Naming-Konventionen
- Admin: `adminKey`, `actor` als Header `X-Admin-Key` bzw. `X-Admin-Actor`.
- Customer: `tenantId`, `tenantSlug`, Header `X-Tenant-Slug`, `X-Forwarded-Host`.
- Auth: `accessToken`/`refreshToken`, keine abgekürzten Namen.

## Kontexttrennung
- Admin-User verwalten Tenants und Systemeinstellungen.
- Tenant-User existieren nur im Customer-Frontend; keine globalen User im Customer-Kontext.
