# env_current.md

Aktueller Stand der gefundenen Environment Variables inkl. Werte/Defaults.
Hinweis: `old_lm` wird ignoriert. SMTP wird aktuell nicht aus ENV gelesen (DB-Settings/Seed), daher hier nur als "nicht aktiv" markiert.

## Backend / Compose / DB (aktiv genutzt)
- `API_PORT=8000`
- `ENVIRONMENT=prod`
- `APP_VERSION=0.1.0`
- `GIT_COMMIT=`

- `ADMIN_API_KEY=change-me`
- `JWT_SECRET=please-set-a-long-random-secret`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRES_MIN=15`
- `REFRESH_TOKEN_EXPIRES_DAYS=30`
- `REFRESH_TOKEN_GRACE_MIN=5`

- `POSTGRES_DB=lager`
- `POSTGRES_USER=lager`
- `POSTGRES_PASSWORD=lager`
- `DATABASE_URL=postgresql+asyncpg://lager:lager@db:5432/lager`

- `BASE_DOMAIN=test.myitnetwork.de`
- `BASE_ADMIN_DOMAIN=admin.test.myitnetwork.de`
- `BACKUP_STORAGE_PATH=storage/backups`
- `BACKUP_STORAGE_DRIVER=local`
- `BACKUP_RETENTION_MAX_DAYS=`
- `BACKUP_RETENTION_MAX_COUNT=`
- `BACKUP_SCHEDULE_ENABLED=false`
- `BACKUP_SCHEDULE_INTERVAL_MINUTES=1440`
- `BACKUP_SCHEDULE_MODE=app`
- `BACKUP_SCHEDULE_LOCK_KEY=932754`
- `BACKUP_JOB_MAX_RETRIES=2`
- `BACKUP_JOB_RETRY_DELAY_SECONDS=5`

- `POSTGRES_DB_TEST=lager_test`
- `DATABASE_URL_TEST=postgresql+asyncpg://lager:lager@db_test:5432/lager_test`

- `SEED_TENANT_SLUG=kunde1`
- `SEED_TENANT_NAME=Kunde 1`
- `SEED_ADMIN_EMAIL=admin@test.myitnetwork.de`
- `SEED_ADMIN_PASSWORD=admin`
- `SEED_ADMIN_ROLE=owner`

## Backend Defaults (Code, aktiv)
- `BUILD_TIMESTAMP=unknown`
- `BUILD_BRANCH=unknown`
- `IMAGE_TAG=unknown`

## Optional lokal (nur wenn Datei vorhanden)
- `ENV_FILE=`

## Frontend (Vite, Build-Time; aktiv genutzt)
- `VITE_BASE_DOMAIN=test.myitnetwork.de`
- `VITE_TENANT_SLUG=`
- `VITE_GRAFANA_URL=http://localhost:3000`
- `VITE_BUILD_INFO=`

## Nicht aktiv genutzt (keine Wirkung im aktuellen Code)
- `API_HOST=` (nur Beispiel in `.env.example`)
- `DB_HOST=` (nur Beispiel in `.env.example`)
- `API_PROTOCOL=` (nicht im Code referenziert)
- `SMTP_HOST=` (SMTP wird über DB-Settings/Seed gesteuert)
- `SMTP_PORT=`
- `SMTP_USER=`
- `SMTP_PASSWORD=`
- `SMTP_FROM=`
- `SENTRY_DSN=`
- `GRAFANA_ADMIN_USER=`
- `GRAFANA_ADMIN_PASSWORD=`
- `PROMETHEUS_PORT=`
- `LOKI_PORT=`
- `GRAFANA_PORT=`
- `CADVISOR_PORT=`
- `VITE_API_BASE=`
- `VITE_API_HOST=`
- `VITE_API_PORT=`
- `VITE_API_PROTOCOL=`
- `VITE_API_SUBDOMAIN=`
- `VITE_API_BASE_URL=`
- `VITE_API_PREFIX=`
