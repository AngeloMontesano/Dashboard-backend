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

## Multi-Tenant Inventar/Artikel (Stand)
- **Tenant-Isolation**: Alle Inventar-Endpoints filtern strikt per `tenant_id` aus dem Host/Subdomain-Kontext (`X-Forwarded-Host`/`Host`). Ohne gültigen Tenant gibt es 404.
- **Rollen**: Lesen für alle aktiven Memberships; Schreiben (Artikel/Kategorien anlegen, ändern, importieren) nur für `owner` und `admin`.
- **SKU-Eindeutigkeit**: Unique pro Tenant (DB-Constraint). Eingaben werden zu `z_<eingabe>` normalisiert, falls nicht bereits mit `z_` beginnen.
- **Kategorien**: Separate Tabelle, global (systemweit) oder tenant-spezifisch; Artikel referenzieren Kategorien per ID. Systemkategorien sind schreibgeschützt, eigene Kategorien können angelegt/umbenannt/deaktiviert werden.
- **Artikel-Felder**:
  - Pflicht: `sku`, `barcode`, `name`
  - Bestandsfelder: `quantity`, `min_stock`, `max_stock`, `target_stock`, `recommended_stock`
  - Bestellung/Alarm: `order_mode` (0=kein Alarm, 1=Alarm, 2=Bestellliste mit Empfehlung, 3=automatisch bestellen)
  - Weitere: `description`, `unit` (Default `pcs`), `is_active`, `category_id` (optional)
- **Lagerbewegungen**:
  - Endpoint: `POST /inventory/movements` (owner/admin), Payload mit `client_tx_id`, `type` (`IN`/`OUT`), `barcode`, `qty`, optional `note`, `created_at`.
  - Idempotenz: `client_tx_id` ist pro Tenant eindeutig, wiederholte Requests mit gleicher ID werden nicht doppelt gebucht.
  - Bestandsschutz: OUT-Buchungen schlagen fehl, wenn der Bestand negativ würde.
- **CSV-Import/Export**:
  - Spalten: `sku`, `barcode`, `name`, `description`, `qty`, `unit`, `is_active`, `category`, `min_stock`, `max_stock`, `target_stock`, `recommended_stock`, `order_mode`
  - Upsert pro Tenant anhand `sku` (mit Präfix-Regel). Fehler werden zeilenweise zurückgegeben, Export liefert das gleiche Schema.
