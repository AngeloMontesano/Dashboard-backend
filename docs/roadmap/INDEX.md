# Roadmap Index

## Standards (nicht verhandelbar)
- [Frontend Rules](../standards/FRONTEND_RULES.md): Genau eine Axios-Quelle pro App, Basis-URL strikt `/api`, keine Host-Ermittlung im Code, Tenant- bzw. Admin-Header nur über die bereitgestellten Helper.
- [API Clients](../standards/API_CLIENTS.md): Admin-Client mit Pflichtheader `X-Admin-Key` (optional `X-Admin-Actor`), Customer-Client mit Tenant-Headern aus `getTenantHeaders()`, Timeouts zentral (15s/20s), keine zusätzlichen `axios.create` Instanzen.
- [OpenAPI Types](../standards/OPENAPI_TYPES.md): Typen kommen aus `docs/openapi/openapi.json`, Wrapper nutzen ausschließlich die generierte `openapi.ts`, keine manuellen Änderungen daran.
- [UI/Design/CSS](../standards/DESIGN_SYSTEM.md) · [COMPONENT_CONVENTIONS](../standards/COMPONENT_CONVENTIONS.md) · [CSS_AND_UI_CONVENTIONS](../standards/CSS_AND_UI_CONVENTIONS.md): Styling über Tokens/Utilities, keine Inline-Styles oder neuen Farbwerte in Views, UI-Bausteine unter `src/components/ui/`, PrimeVue nur im Customer-Frontend.
- [Error Handling](../standards/ERROR_HANDLING.md): Fehlerklassifizierung (`auth`, `client`, `server`, `network`, `unknown`), keine rohen HTTP-Fehler im UI, stattdessen Liste/Badges mit passenden Aktionen (Retry/Login/Edit).
- [Darkmode/Theme Tokens](../standards/DARKMODE.md) & [THEME_TOKENS](../standards/THEME_TOKENS.md): Theme-State via `useTheme`, Persistenz in `localStorage`, `data-theme` am Root; alle Farben/Abstände/Radii über Tokens.
- OpenAPI Quelle (Single Point of Truth): `https://api.test.myitnetwork.de/openapi.json` – lokale `docs/openapi/openapi.json` spiegelt diesen Stand, Generierung erfolgt darüber.
- Typgenerierung: `npm run gen:types` (remote Quelle) oder `npm run gen:types:local` (lokale Datei); Ausgabedatei pro Frontend: `src/api/gen/openapi.ts` (nicht manuell editieren).

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
