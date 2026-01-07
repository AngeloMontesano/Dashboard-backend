# env_needed.md

Ziel: Keine Pflicht-.env. Alle Services lesen Konfiguration ausschließlich aus Environment Variables (Portainer Stack-Env). Optional kann lokal eine `.env` Datei per `ENV_FILE` genutzt werden, sie ist jedoch nie erforderlich.

## Backend API (`backend`)
**Pflicht**
- `DATABASE_URL` – PostgreSQL DSN (z. B. `postgresql+asyncpg://user:pass@db:5432/dbname`).
- `ADMIN_API_KEY` – Shared Secret für `X-Admin-Key`.
- `JWT_SECRET` – Secret für JWT Signierung.
- `BASE_DOMAIN` – Basisdomain für Tenant-Subdomains.
- `BASE_ADMIN_DOMAIN` – Basisdomain für Admin-UI Subdomains.

**Optional (Defaults im Code)**
- `JWT_ALGORITHM` – Default `HS256`.
- `ACCESS_TOKEN_EXPIRES_MIN` – Default `15`.
- `REFRESH_TOKEN_EXPIRES_DAYS` – Default `30`.
- `REFRESH_TOKEN_GRACE_MIN` – Default `5`.
- `ENVIRONMENT` – `prod`/`dev`, Default `prod`.
- `APP_VERSION` – Default `0.1.0`.
- `GIT_COMMIT` – Default `unknown`.
- `BUILD_TIMESTAMP` – Default `unknown`.
- `BUILD_BRANCH` – Default `unknown`.
- `IMAGE_TAG` – Default `unknown`.

**Optional (lokal/Legacy)**
- `ENV_FILE` – Pfad zu einer optionalen `.env` Datei (wird nur geladen, wenn vorhanden).
- `API_PORT` – Port-Mapping in Compose (Default `8000`).

## Postgres (`backend/docker-compose.yml`)
- `POSTGRES_DB` – Datenbankname.
- `POSTGRES_USER` – DB-User.
- `POSTGRES_PASSWORD` – DB-Passwort.

## Seed Initial Data (`backend/app/scripts/seed_initial.py`)
- `SEED_TENANT_SLUG` – Default `kunde1`.
- `SEED_TENANT_NAME` – Default `Kunde 1`.
- `SEED_ADMIN_EMAIL` – Default `admin@test.myitnetwork.de`.
- `SEED_ADMIN_PASSWORD` – Default `admin` (nur Dev).
- `SEED_ADMIN_ROLE` – Default `owner`.

## Tests (optional/legacy)
- `POSTGRES_DB_TEST` – Test-DB Name (falls separat genutzt).
- `DATABASE_URL_TEST` – Test-DB DSN.

## Admin Frontend (`admin_frontend/admin-ui`)
Vite liest Variablen mit `VITE_` Prefix (Build-Time, optional wenn nicht verwendet):
- `VITE_BASE_DOMAIN` – Basisdomain zur Anzeige/Host-Bildung (Fallback `test.myitnetwork.de`).
- `VITE_GRAFANA_URL` – Observability-Link (Fallback `http://localhost:3000`).
- `VITE_BUILD_INFO` – Build-/Version-Info (Fallback `package.json` Version).

## Customer Frontend (`customer_frontend/customer-ui`)
Vite liest Variablen mit `VITE_` Prefix (Build-Time, optional wenn nicht verwendet):
- `VITE_BASE_DOMAIN` – Basisdomain für Host-Whitelist (Fallback `test.myitnetwork.de`).
- `VITE_TENANT_SLUG` – Optionaler Tenant-Slug (Fallback: aus Host ermittelt).

## Shared Package (`packages/api-client`)
- `VITE_TENANT_SLUG` – Optionaler Tenant-Slug (Fallback: aus Host ermittelt).
