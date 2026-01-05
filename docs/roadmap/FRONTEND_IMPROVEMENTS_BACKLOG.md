# FRONTEND IMPROVEMENTS BACKLOG

Legende: **Priorität** P0 (kritisch), P1 (hoch), P2 (mittel). **Aufwand** S/M/L. **Risiko** niedrig/mittel/hoch.

## API Layer
- **Admin Logs-Endpunkt anbinden oder Tab verstecken** (AdminOperationsView) — P1, Aufwand S, Risiko niedrig. Abhängigkeit: Backend-Logs-API.  
- **Server-Paging für Tenants/Memberships** (AdminTenantsView/AdminMembershipsView) — P1, Aufwand M, Risiko mittel. Abhängigkeit: Backend-Filter/Paging.  
- **Dashboard-KPI-API statt Mehrfach-Item-Requests** (Customer Dashboard) — P1, Aufwand M, Risiko mittel. Abhängigkeit: Backend Aggregations-Endpoint.  
- **Token-Refresh/401-Interceptor** (Customer `api/client.ts`) — P1, Aufwand M, Risiko mittel.

## Types/OpenAPI Nutzung
- **Validierungs-Types in Forms nutzen** (TenantSettings, Orders, Settings) — P2, Aufwand M, Risiko niedrig.  
- **Report-Export/Filter-Parameter aus OpenAPI ableiten** (Customer Reporting) — P2, Aufwand S, Risiko niedrig.

## Error Handling
- **Zentrale Fehler-Helfer (stringifyError) je App** — P1, Aufwand S, Risiko niedrig.  
- **Row-Level Busy/Error in Bestellungen & Memberships** — P1, Aufwand S, Risiko niedrig.  
- **Queue-Operationen mit Confirm/Undo** (Lagerbewegungen) — P2, Aufwand S, Risiko niedrig.

## Theme/Tokens
- **Breakpoints/Utilities für Mobile** (beide Apps) — P1, Aufwand M, Risiko mittel.  
- **PrimeVue-Overlays/Toasts an Tokens binden** (Customer) — P2, Aufwand S, Risiko niedrig.  
- **Theme-Toggle in Topbar spiegeln (Admin)** — P2, Aufwand S, Risiko niedrig.

## Components/Primitives
- **Confirm-Dialog-Komponente für Danger-Aktionen** (beide Apps) — P1, Aufwand S, Risiko niedrig.  
- **Paginator/Table-Wrapper mit Empty/Loading-State** — P1, Aufwand M, Risiko mittel.  
- **Reusable Form Validation (Dirty/Required)** — P1, Aufwand M, Risiko mittel.

## Performance
- **Lazy-Loading großer Tabellen** (Tenants, Orders) — P2, Aufwand M, Risiko mittel.  
- **Debounce/Abort für Suchanfragen** (Tenants/Memberships Filters, Reporting Item-Suche) — P2, Aufwand S, Risiko niedrig.

## Testing (Vorschläge)
- **E2E Smoke für Auth + Kernflüsse** (Login, Tenants CRUD, Orders CRUD) — P2, Aufwand M, Risiko mittel.  
- **Component-Tests für Queue/Reporting-Filter** — P2, Aufwand M, Risiko mittel.

## A11y/Mobile
- **ARIA/Keyboard-Support in Report-Filtern und Topbar-Selects** — P1, Aufwand S, Risiko niedrig.  
- **Responsive Sidebar/Toolbar Stacking** (Customer Shell, Admin Shell) — P1, Aufwand M, Risiko mittel.  
- **Focus-Management in Modals (Tenant Create, Confirms)** — P2, Aufwand S, Risiko niedrig.
