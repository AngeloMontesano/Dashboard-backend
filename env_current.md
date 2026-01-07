# env_current.md

Aktueller Stand der gefundenen Environment Variables inkl. Werte/Defaults.

## Backend / Compose / DB (.env.example Werte)
- `API_PORT=8000`
- `ENVIRONMENT=prod`
- `APP_VERSION=0.1.0`
- `GIT_COMMIT=`
- `API_HOST=`

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
- `DB_HOST=`

- `BASE_DOMAIN=test.myitnetwork.de`
- `BASE_ADMIN_DOMAIN=admin.test.myitnetwork.de`

- `POSTGRES_DB_TEST=lager_test`
- `DATABASE_URL_TEST=postgresql+asyncpg://lager:lager@db_test:5432/lager_test`

- `SEED_TENANT_SLUG=kunde1`
- `SEED_TENANT_NAME=Kunde 1`
- `SEED_ADMIN_EMAIL=admin@test.myitnetwork.de`
- `SEED_ADMIN_PASSWORD=admin`
- `SEED_ADMIN_ROLE=owner`

## Backend Defaults (Code)
- `BUILD_TIMESTAMP=unknown`
- `BUILD_BRANCH=unknown`
- `IMAGE_TAG=unknown`

## Optional lokal
- `ENV_FILE=`

## Frontend (Vite, Build-Time; Defaults in Code)
- `VITE_BASE_DOMAIN=test.myitnetwork.de`
- `VITE_TENANT_SLUG=`
- `VITE_GRAFANA_URL=http://localhost:3000`
- `VITE_BUILD_INFO=`
