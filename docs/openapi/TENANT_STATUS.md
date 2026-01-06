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
- HTTP-Status: immer 200, Fehlerzustände liegen im Feld `status` (kein 4xx/5xx-Leak nach außen).

## Responses (200)
```json
{ "status": "ok", "slug": "acme", "host": "acme.example.com", "tenant_id": "uuid", "is_active": true }
{ "status": "not_found", "slug": "unknown", "host": "unknown.example.com", "reason": "tenant_not_found" }
{ "status": "inactive", "slug": "acme", "host": "acme.example.com", "reason": "tenant_inactive" }
{ "status": "unavailable", "slug": "acme", "host": "acme.example.com", "reason": "OperationalError" }
{ "status": "not_found", "slug": null, "host": "example.com", "reason": "missing_slug" }
```

## Beispiele
- Host-Ableitung:  
  ```bash
  curl -H "Host: foo.example.com" -H "X-Forwarded-Host: foo.example.com" https://app.example.com/api/public/tenant-status
  ```
- Slug-Override per Header:  
  ```bash
  curl -H "X-Tenant-Slug: bar" https://app.example.com/api/public/tenant-status
  ```
- Expliziter Slug per Query (ohne Host):  
  ```bash
  curl "http://localhost:8000/api/public/tenant-status?slug=demo"
  ```

## Fehler-/Reason-Codes
- `tenant_not_found`, `tenant_inactive`, `missing_slug`
- DB-/Infra-Fehler werden als Klassenname in `reason` gespiegelt (z. B. `OperationalError`) und mit `status=unavailable` zurückgegeben.

## Annahmen / Regeln
- Endpoint ist öffentlich, keine Auth-Header, keine Session-Cookies nötig.
- Host-Ableitung nutzt `X-Forwarded-Host` und Basis-Domain (`settings.BASE_DOMAIN`); Fallback: `localhost`.
- Rückgaben bleiben schlank (keine Stacktraces, keine Validation Errors).
- OpenAPI-Schema: `PublicTenantStatus` in `docs/openapi/openapi.json`; Typen werden über `npm run gen:types(:local)` generiert (`src/api/gen/openapi.ts`).

## QA-Hinweise (A-10/A-11)
- Mit/ohne `X-Forwarded-Host`, mit/ohne `X-Tenant-Slug`, falscher Slug, fehlender Slug: Response bleibt in Schema (kein 500/Traceback).
- Datenbank down simulieren (`SQLAlchemyError`) → `status=unavailable`, `reason` enthält Klassennamen.
- 404-Routen im Frontend leiten auf TenantStatusView; Backend liefert hier immer 200 mit Status-Payload.

## Review-Checkliste (A-01)
- Header-Priorität dokumentiert (X-Tenant-Slug > Query `slug` > Host-Ableitung).
- HTTP-Status bleibt 200 in allen Pfaden; Fehler sind nur im Feld `status`/`reason`.
- Beispiele decken Proxy-Header, Slug-Override und Localhost-Query ab.
- Reason-Codes sind konsistent mit QA-Szenarien (A-10/A-11) und OpenAPI-Schema.

## Implementierungs-Mapping (Backend Stand)
- Pfad: `backend/app/modules/public/routes.py::tenant_status` (Router `prefix="/public"` wird in `main.py` eingebunden).
- Slug-Auflösung: `X-Tenant-Slug` → Query `slug` → Host-Ableitung via `_get_effective_host` + `_extract_slug_from_hosts` (Base-Domain aus `settings.BASE_DOMAIN`, Fallback `localhost`).
- DB-Verfügbarkeit: Health-Probe `SELECT 1`, `SQLAlchemyError` → `status=unavailable`, `reason` = Klassenname.
- Status-Mapping: fehlender Slug → `not_found/missing_slug`; unbekannter Slug → `not_found/tenant_not_found`; inaktiv → `inactive/tenant_inactive`; ok → `ok` + `tenant_id` + `is_active`.
- HTTP-Code bleibt 200 für alle Pfade; Rückgabeobjekte sind kompakt (keine Tracebacks).

## Proxy-Header-Matrix (A-11 Vorbereitung)
| Szenario | X-Forwarded-Host | X-Tenant-Slug | Query `slug` | Erwarteter Status/Reason |
| --- | --- | --- | --- | --- |
| 1) Host korrekt, kein Slug | `foo.example.com` | – | – | `ok`/`not_found` je nach Tenant; keine 404/500 |
| 2) Host korrekt, Slug Header falsch | `foo.example.com` | `bar` | – | Slug = `bar` (Header gewinnt), Status gemäß `bar` |
| 3) Host korrekt, Slug Query falsch | `foo.example.com` | – | `bar` | Slug = `bar` (Query gewinnt vs Host), Status gemäß `bar` |
| 4) Host leer, Slug Header gesetzt | – | `bar` | – | Slug = `bar`, Status gemäß `bar` |
| 5) Host leer, Slug Query gesetzt | – | – | `bar` | Slug = `bar`, Status gemäß `bar` |
| 6) Host ohne Subdomain, kein Slug | `example.com` | – | – | `status=not_found`, `reason=missing_slug` |
| 7) DB down | beliebig | beliebig | beliebig | `status=unavailable`, `reason=OperationalError` |

## Akzeptanznotizen
- Kein JSON-Fehler im Browser sichtbar; Frontend routet bei `status != ok` auf `TenantStatusView`.
- 404-Routen landen ebenfalls auf `TenantStatusView` (UI-only 404).
- Reason-Codes genügen für QA (A-10/A-11) und Proxy-Szenarien (mit/ohne `X-Forwarded-Host`/Slug).
