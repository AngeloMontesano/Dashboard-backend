# Tenant-Status API (EPIC A – A-01)

## Zweck
Früher Tenant-Check vor App-Bootstrap, damit unbekannte/inaktive Tenants eine gestaltete Seite statt JSON erhalten.

## Endpoint
- `GET /public/tenant-status`
- Basis-Pfad: `/api` (über Proxy), keine absoluten Hosts.

## Request
- Query: `slug` (optional) – Tenant-Slug, falls nicht über Host ableitbar.
- Header:
  - `X-Tenant-Slug` (optional, priorisiert gegenüber Query/Host)
  - `X-Forwarded-Host` (vom Proxy, Basis für Host-Ableitung)
- Timeouts: 8s (Frontend), kein Auth-Refresh (`skipAuthRefresh` Flag im Client gesetzt).

## Responses (200)
```json
{ "status": "ok", "slug": "acme", "host": "acme.example.com", "tenant_id": "uuid", "is_active": true }
{ "status": "not_found", "slug": "unknown", "host": "unknown.example.com", "reason": "tenant_not_found" }
{ "status": "inactive", "slug": "acme", "host": "acme.example.com", "reason": "tenant_inactive" }
{ "status": "unavailable", "slug": "acme", "host": "acme.example.com", "reason": "OperationalError" }
{ "status": "not_found", "slug": null, "host": "example.com", "reason": "missing_slug" }
```

## Fehler-/Reason-Codes
- `tenant_not_found`, `tenant_inactive`, `missing_slug`
- DB-/Infra-Fehler werden als Klassenname in `reason` gespiegelt (z. B. `OperationalError`) und mit `status=unavailable` zurückgegeben.

## Annahmen / Regeln
- Endpoint ist öffentlich, keine Auth-Header, keine Session-Cookies nötig.
- Host-Ableitung nutzt `X-Forwarded-Host` und Basis-Domain (`settings.BASE_DOMAIN`); Fallback: `localhost`.
- Rückgaben bleiben schlank (keine Stacktraces, keine Validation Errors).
- OpenAPI-Schema: `PublicTenantStatus` in `docs/openapi/openapi.json`; Typen werden über `npm run gen:types(:local)` generiert (`src/api/gen/openapi.ts`).

## Akzeptanznotizen
- Kein JSON-Fehler im Browser sichtbar; Frontend routet bei `status != ok` auf `TenantStatusView`.
- 404-Routen landen ebenfalls auf `TenantStatusView` (UI-only 404).
- Reason-Codes genügen für QA (A-10/A-11) und Proxy-Szenarien (mit/ohne `X-Forwarded-Host`/Slug).
