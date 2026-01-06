# FRONTEND AUDIT – Admin & Customer Frontends

## Zusammenfassung der bindenden Standards
- Proxy-Pfad `/api` ist verpflichtend; keine festen Hosts oder weiteren Axios-Instanzen außerhalb von `src/api/client.ts` je App (siehe `docs/standards/FRONTEND_RULES.md`, `API_CLIENTS.md`).  
- OpenAPI-Typen werden aus `docs/openapi/openapi.json` generiert und in den API-Wrappern genutzt (`docs/standards/OPENAPI_TYPES.md`).  
- Design-System und Theme-Tokens pro App: Light/Dark (optional Ocean), alle Farben/Abstände/Radien über Tokens und Utilities; keine Inline-Styles, keine view-spezifischen Overrides (`docs/standards/DESIGN_SYSTEM.md`, `THEME_TOKENS.md`, `CSS_AND_UI_CONVENTIONS.md`).  
- UI-Bausteine unter `src/components/ui` und Utilities (`src/styles/utilities.css`) sind die einzige Quelle für Layout/Spacing; Views enthalten nur Struktur/Datenlogik (`docs/standards/COMPONENT_CONVENTIONS.md`).  
- Darkmode folgt System-Default, Persistenz via `localStorage`, Steuerung über `useTheme`, `data-theme` am `<html>`-Element (`docs/standards/DARKMODE.md`).  
- Admin und Customer bleiben getrennte Apps; keine Shared-Package-Refactors, kein PrimeVue im Admin, PrimeVue nur zentral im Customer (`docs/standards/DESIGN_SYSTEM.md`).

---

## Admin-Frontend (`admin_frontend/admin-ui`)

### Architektur (Ist)
- **Einstieg**: `src/main.ts` lädt Tokens/Base/Layout/Utilities und initialisiert Theme, mountet `App.vue`.  
- **Routing**: Kein Vue-Router; `App.vue` verwaltet Sections (`kunden`, `memberships`, `operations`, `users`, `settings`) per `pushState`/`popstate`.  
- **State**: Lokaler Reactivity-State in `App.vue`; Auth (adminKey/actor) wird nicht persistiert.  
- **API-Layer**: `src/api/client.ts` (Axios `/api`, 15s), Wrapper in `src/api/admin.ts` und `platform.ts`, Header-Helper `adminHeaders`.  
- **UI/Styles**: Globale Styles `styles/{tokens,base,layout,utilities}.css`; eigene UI-Komponenten unter `src/components/ui/*`, zentrale Toast-Implementierung (`components/common/ToastHost.vue`, `composables/useToast`).  
- **Theme**: `useTheme` steuert `data-theme` + Klassen `theme-dark`/`theme-classic`; Sidebar-Select + Settings-View.  
- **Dummy/Placeholder**: Operations-Logs-Tab rendert Demo-Daten, Kommentar „TODO: Backend Endpoint anbinden“.

### Befunde (Schlüsselstellen)
| Bereich | Datei | Problem | Impact (Enduser/Admin) | Empfehlung | Aufwand |
| --- | --- | --- | --- | --- | --- |
| Navigation/Deep-Linking | `src/App.vue` | Kein Router; manuelles `pushState` mit begrenztem Popstate-Sync, Tabs/Queries nur für Operations. | Admins verlieren Kontext beim Reload, URLs sind fragil. | Vue-Router einführen oder Routing-Hilfsschicht kapseln (Section -> Route-Mapping). | M |
| Auth-Context | `src/App.vue` | adminKey/actor nur im Memory, kein Persist/Timeout-Handling. | Reload → Logout, parallele Tabs nicht möglich. | Secure Persistenz (session/localStorage) plus Logout/Expiry-Handling; Maskierung im UI. | S |
| Theme-Applikation | `src/App.vue`, `composables/useTheme.ts` | Klassen-Mapping (`theme-dark`/`theme-classic`) + `data-theme`; Dark/Light-Auswahl nur per Select, kein Schnellzugriff im Topbar. | Inkonsistentes Theming bei neuen Komponenten, eingeschränkte Auffindbarkeit. | Theme-Anzeige/Toggler in Topbar mit Status, Utilities auf `data-theme` vereinheitlichen. | S |
| Tenants Suche/Listen | `src/views/AdminTenantsView.vue` | Limit 500, keine Pagination/Empty-State-CTA in Liste, CSV-Export filtert nur clientseitig. | Langsame Listen bei vielen Tenants; Auswahl wird unübersichtlich. | Pagination + Server-Filter (q/status), Export auf Server-Seite verlagern. | M |
| Tenant Settings Form | `src/views/AdminTenantsView.vue` | Keine Pflichtfeldvalidierung, keine Dirty-Checks, Save-Button auch ohne Änderungen aktiv. | Fehlerspeicherungen, versehentliche Leerwerte. | Validierung + Disable/Dirty-State, Erfolg/Fehler inline anzeigen. | S |
| Tenant Host Anzeige | `src/views/AdminTenantsView.vue` | Host wird aus `VITE_BASE_DOMAIN` gebaut, nicht aus API-Daten. | Falsche Host-Anzeige in Multi-Env-Setups. | Host aus API/Settings ableiten oder optionales Feld klar als Anzeige markieren. | S |
| Memberships Skalierung | `src/views/AdminMembershipsView.vue` | Kein Paging, Rolle/Status-Filter nur clientseitig; Busy/Empty-State pro Tenant rudimentär. | Große Tenants → Performance/UX-Einbruch. | Server-Paging + Loading/Empty-State in Tabelle ergänzen. | M |
| Operations Logs | `src/views/AdminOperationsView.vue` | Logs-Tab liefert nur Demo-Text, kommentiert als TODO (keine API). | Erwartete Funktion fehlt, Admins sehen Platzhalter. | Backend-Endpunkt anbinden oder Tab ausblenden bis verfügbar. | S |
| Snapshot/Health | `src/views/AdminOperationsView.vue` | Snapshots nur lokal (localStorage), kein Tenant-Scope im Health-Check-Feedback. | Begrenzter Nutzen für Incident-Handling, keine Team-Teilung. | Snapshot-Export/Import oder serverseitige Speicherung; Tenant/HOST in Status klar markieren. | M |
| Dialoge/Confirm | `src/views/AdminTenantsView.vue`, `AdminMembershipsView.vue` | Kritische Aktionen nutzen `window.confirm/prompt`; keine modalen Warntexte/Tokens. | Niedrige A11y, keine konsistente Danger-UX. | Einheitliche Confirm-Dialog-Komponente (Tokens, Fokus) für Delete/Deactivate. | S |

### UX-Top-10 (Admin)
1. Navigation ohne echten Router (Section-Wechsel per `pushState`), Query-Sync nur für Operations.  
2. Auth-Kontext wird nicht persistiert; Reload löscht Login.  
3. Tenants-Liste ohne Pagination/Server-Filter, nur Limit 500.  
4. Tenant-Settings-Form speichert ohne Pflichtfeldvalidierung/Dirty-Guard.  
5. Delete/Deactivate nur per `confirm/prompt`, keine sichere Danger-UI.  
6. Memberships-Ansicht ohne Paging; Busy-States nicht auf Row-Level.  
7. Operations-Logs-Tab zeigt Demo-Content („TODO Backend anbinden“).  
8. Snapshots nur lokal, keine Kennzeichnung des Tenant-Kontexts in der Snapshot-Liste.  
9. Theme-Toggle versteckt in Sidebar, nicht im primären Arbeitsbereich.  
10. Breadcrumb/Context verliert Tenant-Hinweis nach Reload, obwohl `localStorage` Slug/Id speichert.

### Quick Wins (Admin)
1. Persistenz für adminKey/actor (sessionStorage) mit Maskierung im UI.  
2. Vue-Router-Light einführen oder Section/Tab-State in URL normalisieren.  
3. Tenants- und Memberships-Filter um Server-Paging erweitern, Empty-State CTA beibehalten.  
4. Tenant-Settings-Buttons deaktivieren, wenn nichts geändert; Pflichtfelder validieren.  
5. Einheitliche Confirm-Dialog-Komponente für Delete/Deactivate.  
6. Logs-Tab ausblenden bis echter Endpoint verfügbar.  
7. Snapshot-Liste um Tenant/Host-Kennung ergänzen und Export ermöglichen.  
8. Theme-Toggle zusätzlich in der Topbar anzeigen.  
9. Health/Diagnostics-Status direkt in Operations-Tab reloadbar machen (Auto-Refresh).  
10. CSV-Export auf Server-Seite verlagern oder mit API-Daten synchron halten.

---

## Customer-Frontend (`customer_frontend/customer-ui`)

### Architektur (Ist)
- **Einstieg**: `src/main.ts` mit PrimeVue (Lara), ToastService, Router, Theme-Init; globale Styles `styles/{tokens,utilities,layout}.css`.  
- **Routing**: Vue-Router (`src/router/index.ts`), Auth-Guard via `useAuth()` (sessionStorage).  
- **State**: Auth-Composable (`useAuth`) mit Tokens/Role in `sessionStorage`; movement-Queue via IndexedDB (`useMovementQueue`), Theme-Composable (`useTheme`).  
- **API-Layer**: `src/api/client.ts` (Axios `/api`, Tenant-Header-Defaults), Wrapper `auth.ts`, `inventory.ts`, `reporting.ts`, `reports.ts` (OpenAPI-Typen).  
- **UI/Styles**: UI-Komponenten unter `src/components/ui`; Layout-Komponenten `Sidebar`, `Topbar`; PrimeVue-Komponenten v. a. in Reporting. Toast-Host custom plus PrimeVue Toast.  
- **Theme**: `useTheme` mit `data-theme` + Klasse `theme-dark`; Toggle in Topbar.  
- **Dummy/Placeholder**: Topbar „Hilfe“-Button ohne Handler; keine Mobile-Breakpoints für Sidebar/Layout.

### Befunde (Schlüsselstellen)
| Bereich | Datei | Problem | Impact (Enduser/Admin) | Empfehlung | Aufwand |
| --- | --- | --- | --- | --- | --- |
| Responsive/Layout | `src/styles/layout.css` | Kein Breakpoint für Sidebar/Grid; feste 2-Spalten-Shell. | Mobile Nutzer sehen abgeschnittene Inhalte. | Breakpoints für <1100px: Sidebar stapeln/ausblendbar, Toolbars umbrechen. | M |
| Topbar Actions | `src/components/layout/Topbar.vue` | „Hilfe“-Button ohne Aktion, Theme-Select ohne Label für Screenreader. | Toter CTA, eingeschränkte A11y. | Entfernen oder Link/Modal hinterlegen; `aria-label` hinzufügen. | S |
| Auth UX | `src/composables/useAuth.ts`, `views/LoginView.vue` | Tokens nur in SessionStorage, kein Refresh/Expiry-Handling, Fehlermeldungen teilweise generisch. | Re-Login nach Tab-Schließung, schwache Fehlerrückmeldung. | Refresh-/Expiry-Handling ergänzen, detaillierte Error-UI beibehalten. | M |
| Dashboard Laden | `src/views/DashboardView.vue` | Mehrfaches Laden aller Items sequentiell (max 25 Seiten) ohne Caching/Abort. | Langsame Loads bei großen Tenants. | Server-seitige Aggregation (KPIs) oder Paginierung/Caching. | M |
| Lagerbewegungen | `src/views/LagerbewegungenView.vue` | Keine leere/Loading-Stati für Queue-Tabelle; CTA „Queue leeren“ ohne Confirm. | Unklare Rückmeldung, versehentliches Löschen möglich. | Empty/Loading-State + Confirm-Dialog für Clear; Statusfilter ergänzen. | S |
| Bestellungen | `src/views/BestellungenView.vue` | PDF/E-Mail/Status-Buttons ohne Disable bei laufenden Requests pro Row; keine Totals/Empty-States pro Tabelle. | Doppel-Klicks möglich, unklare Ergebnisse. | Row-spezifische Busy-States/disable, leere Tabellen mit CTA. | S |
| Berichte & Analysen | `src/views/BerichteAnalysenView.vue` | PDF-Export druckt DOM via `window.open`, kein Dark-Mode/Tokens, Popup-Blocker möglich. | Export scheitert still, CI/A11y-Probleme. | Server/Backend-PDF oder Client-PDF mit Token-Styling und Fehlerhinweis. | M |
| Einstellungen | `src/views/EinstellungenView.vue` | Keine Pflichtfeldvalidierung, Save/Import/Export gleichzeitig aktiv; Test-E-Mail nutzt globale Fehlerfläche. | Fehlerspeicherungen, unklare Operationen. | Disable-Handling per Busy-Flag pro Aktion, Validierung und Inline-Feedback. | S |
| Reporting Filters | `src/components/reports/ReportFilters.vue` | Kein aria-Label/Keyboard-Hint für MultiSelect/DateRange; Loading nicht an Buttons gekoppelt. | Eingeschränkte A11y, Double-Submits. | aria-Label/role ergänzen, Apply-Button während Loading sperren. | S |
| Routing Guard | `src/router/index.ts` | Auth-Guard prüft nur SessionStorage-Tokens, kein Token-Refresh/Role-Check. | Ungültige Session führt zu 401 nach Route-Wechsel, kein Auto-Logout. | Token-Refresh/401-Interceptor mit Logout-Redirect. | M |

### UX-Top-10 (Customer)
1. Kein Mobile-Breakpoint für Sidebar/Layout; Inhalte laufen auf kleinen Screens über.  
2. „Hilfe“-Button ohne Funktion im Topbar.  
3. Session-basierte Auth ohne Refresh/Expiry-Handling.  
4. Dashboard lädt alle Items paginiert ohne Caching, potenziell sehr langsam.  
5. Lagerbewegungen: Kein Confirm für „Queue leeren“, keine leeren/Loading-Stati.  
6. Bestellungen: Aktionen pro Order ohne Row-Busy/Disable, keine leeren Zustände je Abschnitt.  
7. Reporting-PDF nutzt `window.open`/DOM-Kopie, blockiert durch Popups und ignoriert Theme.  
8. Einstellungen: Save/Import/Export/Test parallel aktivierbar, keine Pflichtfeldprüfung.  
9. Reporting-Filter: fehlende aria-Labels/Keyboard-Hinweise, Apply/Export ohne Busy-Block.  
10. Auth-Guard verlässt sich auf SessionStorage, 401 führen zu späten Fehlern statt Re-Login.

### Quick Wins (Customer)
1. Add Breakpoints: Sidebar collapsible/stacked <1100px, Toolbars wrap.  
2. Entferne oder hinterlege echten Link für „Hilfe“, ergänze aria-Label.  
3. Busy/Disable pro Order-Action (PDF/E-Mail/Status) und pro Settings-Button.  
4. Confirm-Dialog für „Queue leeren“ + Empty/Loading-State in Lagerbewegungen.  
5. Cache/Paginierung der Item-Ladungen im Dashboard oder serverseitige KPI-API nutzen.  
6. Reporting-PDF auf Server-Export oder tokenisiertes Client-PDF umstellen.  
7. Pflichtfeld-/Format-Validierung in Einstellungen; Success/Error inline.  
8. PrimeVue Toast/Overlay an Tokens koppeln und einheitlich initialisieren.  
9. Auth-Interceptor mit Refresh/Auto-Logout bei 401.  
10. A11y in Report-Filtern (aria-Labels, Tastatur-Support) und Theme-konforme Charts.
