# Dashboard Backend (FastAPI, Async SQLAlchemy, PostgreSQL)

Produktionsorientiertes Setup für die Multi-Tenant Lagerverwaltung. Dieses Dokument beschreibt Architektur, wichtige Module, wie Requests den Tenant-Kontext erhalten und welche Logs/Telemetry verfügbar sind.

## Architektur-Überblick
- **Framework:** FastAPI auf Python 3.11
- **Persistence:** Async SQLAlchemy 2.x mit asyncpg, Alembic für Migrationen
- **Schema/Settings:** Pydantic v2 & pydantic-settings
- **Service-Layer:** Tenant-fähige Auth & Admin-Module, Inventory-Ping als Beispiel
- **Observability:** strukturierte Request-Logs, Prometheus-Metrics unter `/metrics`
- **Container:** Dockerfile + Compose (prod-orientiert, kein Dev-Reload)

## Request-Lifecycle & Middleware
`app/main.py` bootstrapped das FastAPI-App-Objekt, registriert Router und Middleware.
- **CORS:** Voll offen (alle Origins/Methoden/Headers). Anpassbar über `CORSMiddleware` falls restriktiver benötigt.【F:backend/app/main.py†L16-L70】
- **Request-ID:** Generiert `X-Request-Id` (Header oder UUID). In `request.state.request_id` verfügbar und in Responses gespiegelt.【F:backend/app/main.py†L45-L75】
- **Request-Logging & Metrics:** Misst Dauer, schreibt strukturierte Logs (`app.request`) inkl. Host, Actor, Request-ID und aktualisiert Prometheus Counter/Histogramm.【F:backend/app/main.py†L45-L79】
- **Exception-Handling:** Einheitliches Fehlerformat `{error: {code, message, details?}}` plus `X-Request-Id` Header. Validation-Fehler loggen mit Path und Details.【F:backend/app/core/errors.py†L15-L125】

## Tenant-Auflösung
Tenant-Kontext wird zentral in `app/core/tenant.py` / `get_tenant_context` gelöst:
- Host wird bevorzugt aus `X-Forwarded-Host`, sonst `Host` gelesen, Port und Kommas entfernt.【F:backend/app/core/tenant.py†L22-L45】
- Erwartet genau eine Subdomain vor `BASE_DOMAIN` (z. B. `kunde1.test.myitnetwork.de`). Fallback: `*.localhost` ist erlaubt.【F:backend/app/core/tenant.py†L52-L86】
- `X-Tenant-Slug` Header überschreibt den Slug (nützlich bei zentralem API-Host).【F:backend/app/core/tenant.py†L60-L80】
- Fehlschläge liefern `404 tenant_not_found` mit Host/Slug-Infos und werden im Logger `app.request` als Warning ausgegeben.【F:backend/app/core/tenant.py†L80-L117】
- Erfolgreich aufgelöste Tenants stehen als `TenantContext` (Tenant-Objekt + Slug) bereit.【F:backend/app/core/tenant.py†L9-L20】【F:backend/app/core/deps_tenant.py†L8-L17】

## Module & Routen
- **Auth (`/auth`):** Tenant-aware Login/Refresh/Logout. Loggt Login-Versuche inkl. Request-ID; Fehler (z. B. Invalid Credentials, fehlende Membership) werden mit Code/Status geloggt und als Standard-Error zurückgegeben.【F:backend/app/modules/auth/routes.py†L18-L96】
- **Admin (`/admin`):** Geschützt per `X-Admin-Key`. Endpunkte für Tenants, Users, Memberships, Rollen, Audit, Diagnostics.【F:backend/app/modules/admin/routes.py†L1-L38】
- **Inventory (`/inventory/ping`):** Beispielroute, die Tenant-Kontext benötigt.【F:backend/app/modules/inventory/routes.py†L1-L47】
- **Platform:** Health (`/health`, `/health/db`), Meta (`/meta`), Metrics (`/metrics`). Metrics geben Prometheus-Registry aus.【F:backend/app/main.py†L82-L143】

## Authentifizierung & Sessions
- **Login Flow:** `POST /auth/login` erwartet `email`, `password`. Nach erfolgreicher Tenant-Resolution werden Credentials geprüft, Membership validiert und JWT + Refresh Token erstellt.【F:backend/app/modules/auth/service.py†L36-L95】
- **Passwort-Policy:** Aktuell min. 4 Zeichen (dev-seed-kompatibel), max. 200. Stärkevalidierung kann bei Bedarf ergänzt werden.【F:backend/app/modules/auth/schemas.py†L7-L21】
- **Tokens:** Access Tokens werden mit `create_access_token` (JWT) erstellt, Refresh Tokens als random Strings gespeichert (Hash in DB). Rotation bei Refresh, Revocation bei Logout.【F:backend/app/modules/auth/service.py†L58-L119】
- **Membership-Enforcement:** Nur aktive Memberships des Tenants dürfen Tokens erhalten; sonst 403 `no_membership`.【F:backend/app/modules/auth/service.py†L48-L94】

## Datenmodell (relevant für Auth)
- `Tenant`: slug, name, aktiv-Flag.
- `User`: global eindeutige Email, `password_hash`, aktiv-Flag.
- `Membership`: verbindet User <-> Tenant mit Rolle und Aktiv-Flag.
- `RefreshSession`: Refresh Token Hash, Tenant/User, Ablauf/Revocation, `last_used_at`.

## Logging & Observability
- **Logger-Namen:** `app.request` (Request/Metrics), `app.auth` (Auth-Flows), `app` (Exception-Handler). Konsumierbar in Docker-Logs.
- **Validation Logs:** 422-Validation-Errors loggen Path + Fehlerdetails + Request-ID für schnellere Ursachefindung.【F:backend/app/core/errors.py†L75-L93】
- **Prometheus:** Counter `http_requests_total` & Histogram `http_request_duration_seconds` für jede Route/Status.【F:backend/app/observability/metrics.py†L1-L200】
- **Request-ID Propagation:** Responses setzen `X-Request-Id`, Fehler-Responses ebenso – nützlich für Korrelation mit Frontend/Browser-Konsole.【F:backend/app/core/errors.py†L15-L43】【F:backend/app/main.py†L45-L75】

## Konfiguration (.env)
Beispiel erzeugen:
```bash
cp .env.example .env
```
Wichtige Keys (Repo-Root `.env`, von Compose geladen):
- Datenbank: `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Auth: `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRES_MIN`, `REFRESH_TOKEN_EXPIRES_DAYS`, `REFRESH_TOKEN_GRACE_MIN`
- Domains: `BASE_DOMAIN` (z. B. `test.myitnetwork.de`), `BASE_ADMIN_DOMAIN`
- Admin-Key: `ADMIN_API_KEY` (Header `X-Admin-Key`)
- Umgebung: `ENVIRONMENT` (`prod`/`dev` beeinflusst Fehlerdetails)

## Deployment / Start
```bash
docker compose up -d --build
```
- Alembic-Migrationen + Seed laufen im Entrypoint (nur wenn DB leer).
- `uvicorn` läuft ohne Reload (prod-orientiert). Für Dev kann `--reload` im Entrypoint ergänzt werden.

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
