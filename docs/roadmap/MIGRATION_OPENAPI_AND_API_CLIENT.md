# Migration OpenAPI und API Client – Aufgabenübersicht

- Aufgabe: OpenAPI-Typgenerierung einführen (Scripts + lokale Spec).  
  - App: admin & customer  
  - Dateien: `admin_frontend/admin-ui/package.json`, `customer_frontend/customer-ui/package.json`, `docs/openapi/openapi.json`, `src/api/gen/openapi.ts` je App.  
  - Ziel: Typen reproduzierbar generieren (remote/local) und als Basis für Wrapper nutzen.

- Aufgabe: Axios-Clients zentralisieren und Basis-URL auf `/api` fixieren.  
  - App: admin & customer  
  - Dateien: `admin_frontend/admin-ui/src/api/client.ts`, `admin_frontend/admin-ui/src/api/base.ts`, `customer_frontend/customer-ui/src/api/client.ts`, `customer_frontend/customer-ui/src/api/base.ts`.  
  - Ziel: Genau eine Axios-Instanz je Frontend, keine Host-Ermittlung zur Laufzeit.

- Aufgabe: API-Wrapper auf zentrale Clients und OpenAPI-Typen umstellen.  
  - App: customer  
  - Dateien: `customer_frontend/customer-ui/src/api/auth.ts`, `customer_frontend/customer-ui/src/api/inventory.ts`, `customer_frontend/customer-ui/src/api/reporting.ts`, `customer_frontend/customer-ui/src/api/reports.ts`.  
  - Ziel: Wrapper nutzen `api.*`, `/api`-Pfad und generierte Typen für Kategorien, Items, Bewegungen.

- Aufgabe: Admin-Wrapper auf zentrale Clients und OpenAPI-Typen umstellen.  
  - App: admin  
  - Dateien: `admin_frontend/admin-ui/src/api/admin.ts`, `admin_frontend/admin-ui/src/api/platform.ts`, `admin_frontend/admin-ui/src/types.ts`.  
  - Ziel: Requests mit `adminHeaders`, `/api`-Pfad und generierten Typen für Tenants, Users, Memberships, Tenant Users.

- Aufgabe: Standards und Roadmap dokumentieren.  
  - App: repo-weit  
  - Dateien: `docs/standards/FRONTEND_RULES.md`, `docs/standards/OPENAPI_TYPES.md`, `docs/standards/API_CLIENTS.md`, `docs/standards/CSS_AND_UI_CONVENTIONS.md`, `docs/roadmap/POST_MIGRATION_TASKS.md`.  
  - Ziel: Dauerhafte Regeln für API-Nutzung, Typen-Generierung, UI-Konsistenz und offene Follow-ups festhalten.
