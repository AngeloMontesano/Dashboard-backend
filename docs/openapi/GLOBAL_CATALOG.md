# Globale Kataloge & Branchen – Entwurf (EPIC B)

## Datenmodell
- `industries`
  - `id` UUID PK
  - `name` text unique (lowercase index)
  - `is_active` bool default true
  - `created_at/updated_at` timestamptz
  - Index: unique (lower(name)), partial index `is_active=true` optional
- `global_categories`
  - `id` UUID PK
  - `name` text unique (lowercase), `is_active` bool default true, `is_system` bool default false
  - Index: unique (lower(name))
- `global_types`
  - `id` UUID PK
  - `name` text unique (lowercase), `is_active` bool default true
  - Index: unique (lower(name))
- `global_items`
  - `id` UUID PK
  - `sku` text unique (lowercase), `name` text, `description` text
  - FK `type_id` → `global_types.id` (RESTRICT), FK `category_id` → `global_categories.id` (RESTRICT)
  - FK `industry_id` → `industries.id` (RESTRICT, nullable)
  - `is_active` bool default true, `is_system` bool default false
  - Indizes: unique (lower(sku)), index (industry_id), index (type_id, category_id)
- `industry_global_items` (Mapping)
  - PK (industry_id, item_id)
  - FK `industry_id` → `industries.id` (CASCADE)
  - FK `item_id` → `global_items.id` (CASCADE)
- Tenant-Erweiterung
  - `tenants.industry_id` FK → `industries.id` (RESTRICT, nullable)
  - Optional: `tenant_addresses.industry_id` FK → `industries.id` (RESTRICT)

## Admin API (CRUD)
Alle Pfade unter `/admin/global`, Header: `X-Admin-Key`, optional `X-Admin-Actor`. Responses im Standard-Fehlerformat (`error.code`, `message`).

### Industries
- `GET /admin/global/industries`
  - Query: `q` (search), `is_active` (bool), `limit`, `offset`
  - Response: Liste `{id, name, is_active}` + Paging-Metadaten `{total, limit, offset}`
  - Status: 200
- `POST /admin/global/industries`
  - Body: `{name, is_active?}`
  - Response: `{id, name, is_active}`
  - Status: 201
- `PATCH /admin/global/industries/{id}`
  - Body: `{name?, is_active?}`
  - Response: `{id, name, is_active}`
  - Status: 200, 404 wenn `id` fehlt
- `DELETE /admin/global/industries/{id}?confirm=true`
  - Status: 204, 404 wenn nicht gefunden, 409 wenn gemappt auf Tenants/Items (`industry_in_use`)

### Categories
- `GET /admin/global/categories` / `POST` / `PATCH` / `DELETE`
  - Felder: `{id?, name, is_active, is_system?}`
  - Validation: `is_system` nicht löschbar; `name` case-insensitive unique.
  - Status: GET 200, POST 201, PATCH 200 (404 wenn fehlt), DELETE 204 (409 `category_in_use`, 403 `forbidden_system_record`)

### Types
- `GET /admin/global/types` / `POST` / `PATCH` / `DELETE`
  - Felder: `{id?, name, is_active}`
  - Validation: `name` case-insensitive unique.
  - Status: GET 200, POST 201, PATCH 200 (404 wenn fehlt), DELETE 204 (404 wenn fehlt)

### Items
- `GET /admin/global/items`
  - Query: `q`, `industry_id`, `category_id`, `type_id`, `is_active`, `limit`, `offset`
  - Response: Liste `{id, sku, name, type_id, category_id, industry_id, is_active}` + `{total, limit, offset}`
  - Status: 200
- `POST /admin/global/items`
  - Body: `{sku, name, description?, type_id, category_id, industry_id?, is_active?}`
  - Validation: SKU case-insensitive unique; FK müssen existieren/aktiv sein; `industry_id` optional.
  - Status: 201, 404 wenn FK fehlen
- `PATCH /admin/global/items/{id}`
  - Body: Felder optional; gleiche Validierung, 404 wenn Item fehlt.
  - Status: 200, 404 wenn Item fehlt
- `DELETE /admin/global/items/{id}?confirm=true`
  - Status: 204, 404 wenn fehlt, 409 wenn im Mapping genutzt (`item_in_use`)

### Industry↔Item Mapping
- `GET /admin/global/industry-items/{industry_id}`
  - Response: Liste `item_id`
- `PUT /admin/global/industry-items/{industry_id}`
  - Body: `{item_ids: string[]}` (setzt Mapping vollständig)
  - Validation: Items müssen existieren/aktiv sein, 404 wenn Industry fehlt.
  - Status: 200, 404 wenn Industry fehlt

## OpenAPI-Schema (Vorschlag)
- Schemas: `GlobalIndustry`, `GlobalCategory`, `GlobalType`, `GlobalItem`, `GlobalItemList`, `GlobalIndustryItemMapping`, `PagedMeta {total, limit, offset}`.
- Fehler-Codes: `industry_not_found`, `category_not_found`, `type_not_found`, `global_item_not_found`, `mapping_in_use`, `industry_in_use`, `category_in_use`, `item_in_use`, `duplicate_name`, `duplicate_sku`, `forbidden_system_record`.
- Aufnahme in `docs/openapi/openapi.json` in Folgeschritt (nach Freigabe).

## Defaults & Limits
- Paging-Defaults: `limit=50`, `offset=0`; max `limit=200`.
- Sortierung: Alphabetisch nach `name` (Industries/Categories/Types) bzw. `sku` dann `name` (Items).
- Fehlerformat: `{error: {code, message}}` gemäß Fehler-Standard; 409 bei Referenz-Konflikten, 403 bei System-Schutz, 404 bei unbekannter ID/FK.

## Beispiele (cURL)
- Liste Branchen: `curl -H "X-Admin-Key: <key>" "http://localhost:8000/api/admin/global/industries?limit=20"`
- Branche anlegen: `curl -X POST -H "X-Admin-Key: <key>" -H "Content-Type: application/json" -d '{"name":"Logistik"}' "http://localhost:8000/api/admin/global/industries"`
- Globales Item anlegen: `curl -X POST -H "X-Admin-Key: <key>" -H "Content-Type: application/json" -d '{"sku":"ART-001","name":"Palette","type_id":"...","category_id":"...","industry_id":"..."}' "http://localhost:8000/api/admin/global/items"`
- Mapping setzen: `curl -X PUT -H "X-Admin-Key: <key>" -H "Content-Type: application/json" -d '{"item_ids":["..."]}' "http://localhost:8000/api/admin/global/industry-items/<industry_id>"`

## QA/Review-Checkliste
- Header: Jeder Call verlangt `X-Admin-Key`; fehlender Header liefert Standard-Auth-Fehler.
- Unique: Namen (Industrie/Kategorie/Typ) und SKU case-insensitive; Duplikate liefern `duplicate_name`/`duplicate_sku` mit 409.
- System-Datensätze: `is_system=true` nicht löschbar; DELETE gibt `forbidden_system_record` 403.
- Referenzen: DELETE liefert 409 (`industry_in_use`/`category_in_use`/`item_in_use`) wenn FK/Mappings existieren.
- Paging: Listen geben `{total, limit, offset}` zurück; Filter auf `is_active` funktioniert.
- Mapping: `PUT industry-items` ersetzt die Zuordnung vollständig und ignoriert inaktive/fehlende Items mit Fehlermeldung.

## Akzeptanznotizen
- Alle Endpunkte respektieren Admin-Header und nutzen das bestehende Fehlerformat.
- Unique-Checks sind case-insensitive.
- Deaktivierte Datensätze tauchen nur bei expliziter `is_active=false`-Filterung oder bei Detail-GET auf.
- Mapping-Update erfolgt als vollständiges Set (`PUT` ersetzt vorhandene Zuordnung).
