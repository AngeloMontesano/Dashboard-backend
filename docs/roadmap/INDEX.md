# Roadmap Index

## Standards (nicht verhandelbar)
- [Frontend Rules](../standards/FRONTEND_RULES.md): Eine Axios-Quelle pro App, Basis-URL immer `/api`, keine Host-Ermittlung im Frontend, Tenant-Header nur über die vorgesehenen Helper.
- [API Clients](../standards/API_CLIENTS.md): Admin-Client mit Pflichtheader `X-Admin-Key`, Customer-Client mit Tenant-Headern aus `getTenantHeaders()`, Timeouts zentral (15s/20s), keine zusätzlichen `axios.create` Instanzen.
- [OpenAPI Types](../standards/OPENAPI_TYPES.md): Typen werden aus `https://api.test.myitnetwork.de/openapi.json` generiert (Single Source of Truth), Wrapper nutzen ausschließlich diese Typen, `openapi.ts` ist unverändert generiert.
- [Component/Design/CSS Standards](../standards/DESIGN_SYSTEM.md), [COMPONENT_CONVENTIONS](../standards/COMPONENT_CONVENTIONS.md), [CSS_AND_UI_CONVENTIONS](../standards/CSS_AND_UI_CONVENTIONS.md): Styles über Tokens/Utilities, keine Inline-Styles, UI-Bausteine unter `src/components/ui/`, PrimeVue bleibt nur im Customer-Frontend-historie ersetzt.
- [Error Handling](../standards/ERROR_HANDLING.md): Fehlerklassifizierung (`auth`, `client`, `server`, `network`, `unknown`), keine rohen HTTP-Fehler im UI, Retry-/Login-/Edit-Aktionen pro Kategorie.
- [Darkmode/Theme Tokens](../standards/DARKMODE.md) & [THEME_TOKENS](../standards/THEME_TOKENS.md): Light/Dark per `useTheme`, Persistenz in `localStorage`, Tokens definieren alle Farben/Abstände; `data-theme` am Root setzen.

## Epic-Template (verbindlich)
1. Ziel
2. Problem heute
3. Scope
4. Nicht-Ziele
5. User Journeys
6. UI/UX Regeln
7. API/Backend Annahmen (nur wenn nötig)
8. Daten (konzeptionell)
9. Tasks (umsetzbar, klein)
10. Akzeptanzkriterien
11. Risiken/Offene Punkte

## Epics
- [EPIC_A_TENANT_RESOLUTION](EPIC_A_TENANT_RESOLUTION.md)
- [EPIC_B_GLOBAL_CATALOG_AND_INDUSTRY](EPIC_B_GLOBAL_CATALOG_AND_INDUSTRY.md)
- [EPIC_C_CUSTOMER_REPORTING_UX](EPIC_C_CUSTOMER_REPORTING_UX.md)
- [EPIC_D_CUSTOMER_DASHBOARD_NAVIGATION](EPIC_D_CUSTOMER_DASHBOARD_NAVIGATION.md)
- [EPIC_E_CUSTOMER_ORDERS_IMPROVEMENTS](EPIC_E_CUSTOMER_ORDERS_IMPROVEMENTS.md)
- [EPIC_F_OFFLINE_QUEUE_ERROR_HANDLING](EPIC_F_OFFLINE_QUEUE_ERROR_HANDLING.md)
- [EPIC_G_DOCUMENTATION_AND_HELP](EPIC_G_DOCUMENTATION_AND_HELP.md)
- [EPIC_H_MONITORING_LIGHTWEIGHT](EPIC_H_MONITORING_LIGHTWEIGHT.md)
- [EPIC_I_CONTACT_DATA_AND_SUPPORT](EPIC_I_CONTACT_DATA_AND_SUPPORT.md)

## Spezifikationen & Referenzen
- Tenant-Status (A-01): [docs/openapi/TENANT_STATUS.md](../openapi/TENANT_STATUS.md) inkl. Proxy-Header-Matrix (A-11 Vorbereitung); Schema `PublicTenantStatus` in [docs/openapi/openapi.json](../openapi/openapi.json)
- Globale Kataloge (B-02): [docs/openapi/GLOBAL_CATALOG.md](../openapi/GLOBAL_CATALOG.md) mit Paging-Defaults (`limit=50`, max 200), Fehlercodes (`industry_in_use/category_in_use/item_in_use/forbidden_system_record`), Status-Codes, Headerpflicht (`X-Admin-Key`), Response-Envelope ohne `data`-Wrapper und QA/Review-Checkliste; Schemas in [docs/openapi/openapi.json](../openapi/openapi.json) nachziehen
- OpenAPI Quelle (lokal): [docs/openapi/openapi.json](../openapi/openapi.json)

## Backlog & Logs
- [TODO.md](../../TODO.md): Priorisierter Now/Next/Later-Backlog mit Epic/Task-IDs.
- [Epic_TODO.md](../../Epic_TODO.md): Aufgaben je Epic (A–I) als Referenzliste.
- [WORKLOG.md](../../WORKLOG.md): Chronologische Arbeitsnotizen und Scans.
- [Epic_WORKLOG.md](../../Epic_WORKLOG.md): Änderungen/Prüfungen auf Epic-Ebene.

## Qualitätscheck
- Alle Epic-Dateien existieren und sind hier verlinkt.
- Jede Epic folgt dem Template (Ziel → Risiken) und enthält 8–20 Tasks mit ID, Bereich, Abhängigkeiten und Done-Kriterium.
- TODO.md und Epic_TODO.md referenzieren die Task-IDs konsistent (Now/Next/Later).
- WORKLOG.md/Epic_WORKLOG.md dokumentieren Datum, Änderungen und offene Punkte.
- Standards aus `docs/standards/` sind oben verlinkt und gelten für alle geplanten Arbeiten.
