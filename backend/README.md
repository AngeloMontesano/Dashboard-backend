# Dashboard Backend (FastAPI, Async SQLAlchemy, PostgreSQL)

Produktionsorientiertes Setup für die Multi-Tenant Lagerverwaltung.

## Stack
- Python 3.11, FastAPI
- Async SQLAlchemy 2.x + asyncpg, Alembic
- Pydantic v2 + pydantic-settings
- Dockerfile + docker compose (kein Dev/Test-Profil)

## Konfiguration (.env)
Aus dem Repo-Root eine `.env` anlegen (Compose erwartet sie dort), z. B.:

```bash
cp .env.example .env
```

Wichtige Keys:
- `DATABASE_URL` (postgresql+asyncpg)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `ADMIN_API_KEY` (für Admin-Endpoints via `X-Admin-Key`)
- `JWT_SECRET`, `JWT_ALGORITHM`
- `BASE_DOMAIN` (z. B. `test.myitnetwork.de`)
- `BASE_ADMIN_DOMAIN` (Standard: `admin.test.myitnetwork.de`)
- `ACCESS_TOKEN_EXPIRES_MIN`, `REFRESH_TOKEN_EXPIRES_DAYS`
- `ENVIRONMENT=prod`

## Start (Prod)
```bash
docker compose up -d --build
```
- Alembic-Migrationen und Seed laufen automatisch im Entrypoint.
- `uvicorn` läuft ohne Reload.

## Tenant-Resolution
- Erwartet genau eine Subdomain vor `BASE_DOMAIN`, z. B. `kunde1.test.myitnetwork.de`.
- Fallback-Domain `localhost` erlaubt ebenfalls eine Subdomain, z. B. `kunde1.localhost`.
- Host wird aus `X-Forwarded-Host` oder `Host` gelesen.

## Wichtige Endpoints
- Health: `GET /health`, `GET /health/db`
- Inventory Ping (mit Host/Subdomain): `GET /inventory/ping`
- Admin (Header `X-Admin-Key`): `GET /admin/ping`, `POST /admin/tenants`, ...
- Auth (tenant-context über Host):
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `POST /auth/logout`

## Seeding
- Läuft automatisch, wenn die DB leer ist.
- Werte können via `SEED_*` Variablen in `.env` überschrieben werden.

## Multi-Tenant Inventar/Artikel (Planung & Regeln)
Dieser Abschnitt dokumentiert die vereinbarten Regeln für die Artikelverwaltung, damit Implementierungen konsistent bleiben.

- **Tenant-Isolation**: Alle Queries/Mutationen müssen mit `WHERE tenant_id = ctx.tenant.id` arbeiten. Der Tenant wird über Host/Subdomain (`X-Forwarded-Host`/`Host`) ermittelt.
- **SKU-Eindeutigkeit**: `sku` muss pro Tenant eindeutig sein (Unique-Constraint einplanen). Frontend soll vor dem Speichern bereits gegen eine „SKU existiert“-Prüfung testen.
- **Kundeneigene SKUs**: Eingaben ohne Präfix werden beim Speichern zu `z_<eingabe>` normalisiert, damit ERP-Importe eigene Artikel nicht überschreiben.
- **Kategorien**: Artikel referenzieren Kategorien per ID. Kategorien können global (systemweit) oder tenant-spezifisch sein; das Dropdown soll beide anbieten, eigene Kategorien dürfen angelegt werden.
- **Felder (Soll-Stand)**:
  - `sku`, `barcode`, `name` (Pflicht)
  - `description` (optional)
  - `quantity` (aktueller Bestand)
  - `min_stock`, `max_stock`, `target_stock` (Soll), `recommended_stock`
  - `order_mode` (Bestellung) mit 4 Modi:
    - `0`: kein Alarm bei Unterschreitung
    - `1`: Alarm bei Unterschreitung des Mindestbestands
    - `2`: Artikel in Bestellliste mit empfohlener Menge aufnehmen
    - `3`: automatisch sofort nachbestellen
  - `unit` (z. B. `pcs`), `is_active` (bool), `category_id` (optional)
- **CSV-Import/Export (geplant)**:
  - Spalten: `sku`, `barcode`, `name`, `description`, `qty`, `unit`, `is_active`, `category`, `min_stock`, `max_stock`, `target_stock`, `recommended_stock`, `order_mode`
  - Pflicht: `sku`, `barcode`, `name`; Defaults: `qty=0`, `unit="pcs"`, `is_active=true`.
  - Upsert pro Tenant anhand `sku` (mit Präfix-Regel); Fehler pro Zeile zurückmelden; Export liefert die gleichen Spalten.

Diese Regeln dienen als Referenz, bis die vollständigen Endpunkte/Modelle implementiert sind.
