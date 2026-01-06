# Roadmap Index

## Standards (nicht verhandelbar)
- API/Routing: [Frontend Rules](../standards/FRONTEND_RULES.md) & [API Clients](../standards/API_CLIENTS.md) – exakt eine Axios-Instanz je App, Basis-URL immer `/api`, keine Host-Ermittlung im Frontend, Header nur über `getTenantHeaders()`/`adminHeaders()`, Admin-Requests mit `X-Admin-Key` (+ optional `X-Admin-Actor`), Timeouts 15s (Admin) / 20s (Customer).
- Typen: [OpenAPI Types](../standards/OPENAPI_TYPES.md) – Source of Truth ist `https://api.test.myitnetwork.de/openapi.json` (lokal gespiegelt unter `docs/openapi/openapi.json`), Generierung nur über `gen:types`, keine manuellen Änderungen an `openapi.ts`.
- UI/Design: [DESIGN_SYSTEM](../standards/DESIGN_SYSTEM.md), [COMPONENT_CONVENTIONS](../standards/COMPONENT_CONVENTIONS.md), [CSS_AND_UI_CONVENTIONS](../standards/CSS_AND_UI_CONVENTIONS.md) – Styles ausschließlich über Tokens/Utilities, keine Inline-Styles, Views nutzen UI-Bausteine unter `src/components/ui/`, PrimeVue bleibt nur im Customer-Frontend soweit vorhanden.
- Fehler/Darkmode: [ERROR_HANDLING](../standards/ERROR_HANDLING.md) – Fehlerklassifizierung (`auth`, `client`, `server`, `network`, `unknown`), keine rohen HTTP-Meldungen im UI; [DARKMODE](../standards/DARKMODE.md) & [THEME_TOKENS](../standards/THEME_TOKENS.md) – `useTheme` pro App, Persistenz in `localStorage`, `data-theme` am Root, alle Farben/Abstände aus Tokens.

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
