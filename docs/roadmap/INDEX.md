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
