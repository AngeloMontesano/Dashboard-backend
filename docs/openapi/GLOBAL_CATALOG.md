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

- `GET /admin/global/industries`
  - Query: `q` (search), `is_active` (bool), `limit`, `offset`
  - Response: Liste `{id, name, is_active}`
- `POST /admin/global/industries`
  - Body: `{name, is_active?}`
  - Response: `{id, name, is_active}`
- `PATCH /admin/global/industries/{id}`
  - Body: `{name?, is_active?}`
  - Response: `{id, name, is_active}`
- `DELETE /admin/global/industries/{id}?confirm=true`
  - 409 wenn gemappt auf Tenants/Items

- `GET /admin/global/categories` / `POST` / `PATCH` / `DELETE`
  - Felder: `{name, is_active, is_system?}`
  - Validation: `is_system` nicht löschbar

- `GET /admin/global/types` / `POST` / `PATCH` / `DELETE`
  - Felder: `{name, is_active}`

- `GET /admin/global/items`
  - Query: `q`, `industry_id`, `category_id`, `type_id`, `is_active`, `limit`, `offset`
  - Response: Liste `{id, sku, name, type_id, category_id, industry_id, is_active}`
- `POST /admin/global/items`
  - Body: `{sku, name, description?, type_id, category_id, industry_id?, is_active?}`
  - Validation: SKU unique (lowercase), FK existieren, `industry_id` optional
- `PATCH /admin/global/items/{id}`
  - Body: Felder optional; gleiche Validierung
- `DELETE /admin/global/items/{id}?confirm=true`
  - 409 wenn im Mapping genutzt

- `GET /admin/global/industry-items/{industry_id}`
  - Response: Liste `item_id`
- `PUT /admin/global/industry-items/{industry_id}`
  - Body: `{item_ids: string[]}` (setzt Mapping vollständig)
  - Validation: Items müssen existieren/aktiv sein

## OpenAPI-Schema (Vorschlag)
- Schemas: `GlobalIndustry`, `GlobalCategory`, `GlobalType`, `GlobalItem`, `GlobalItemList`, `GlobalIndustryItemMapping`.
- Fehler-Codes: `industry_not_found`, `category_not_found`, `type_not_found`, `global_item_not_found`, `mapping_in_use`, `duplicate_name`, `duplicate_sku`.
- Aufnahme in `https://api.test.myitnetwork.de/openapi.json` in Folgeschritt (nach Freigabe).

## Akzeptanznotizen
- Alle Endpunkte respektieren Admin-Header und nutzen das bestehende Fehlerformat.
- Unique-Checks sind case-insensitive.
- Deaktivierte Datensätze tauchen nur bei expliziter `is_active=false`-Filterung oder bei Detail-GET auf.
- Mapping-Update erfolgt als vollständiges Set (`PUT` ersetzt vorhandene Zuordnung).
