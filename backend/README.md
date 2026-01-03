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
